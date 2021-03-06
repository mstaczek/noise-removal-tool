from tkinter import Tk, StringVar, filedialog, Button, scrolledtext
from tkinter.constants import BOTH, W, N, E, S, END
from tkinter.ttk import Frame, Label
import threading
import logging
import guiWorker
from configparser import ConfigParser

class TextHandler(logging.Handler):
    """
    Class used for printing logs to console and/or logging field in GUI.
    """
    def __init__(self, text):
        logging.Handler.__init__(self)
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(END, msg + '\n')
            self.text.configure(state='disabled')
            self.text.yview(END)
        self.text.after(0, append)

class myGUI(Frame):
    """
    Class for managing Tkinter's based GUI.
    """
    config = None

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.config = ConfigParser()
        self.build_gui()


    def build_gui(self):
        def noiseChooseButtonListener():
            noiseFilename = filedialog.askopenfilename(title="Select noise file")
            if(noiseFilename != '' and noiseFilename != None):
                selectedNoise.set(noiseFilename)

        def lectureChooseButtonListener():
            lectureFilename = filedialog.askopenfilename(title="Select lecture file")
            if(lectureFilename != '' and lectureFilename != None):
                selectedLecture.set(lectureFilename)

        def audacityChooseButtonListener():
            audacityFilename = filedialog.askopenfilename(title="Select lecture file")
            if(audacityFilename != '' and audacityFilename != None):
                selectedAudacity.set(audacityFilename)

        def startProcessingListener():
            update_config()
            t1 = threading.Thread(daemon=True,target=self.worker,
                                  args=[selectedNoise.get(), selectedLecture.get(), logging.info, selectedAudacity.get()])
            t1.start()
        
        def stopProcessingListener():
            guiWorker.kill_audacity("--- Stopping Audacity ---", logging.info)

        def read_config():
            self.config.read('config.ini')
            if(len(self.config.sections()) > 0):
                selectedLecture.set(self.config.get('PATHS', 'LECTURE'))
                selectedNoise.set(self.config.get('PATHS', 'NOISE'))
                selectedAudacity.set(self.config.get('PATHS', 'AUDACITY'))
            else:
                self.config.add_section('PATHS')

        def update_config():
            self.config.set('PATHS', 'AUDACITY', selectedAudacity.get())
            self.config.set('PATHS', 'NOISE', selectedNoise.get())
            self.config.set('PATHS', 'LECTURE', selectedLecture.get())
            with open('config.ini', 'w') as f:
                self.config.write(f)

        # init window
        self.root.title('Sieci lecture processor')
        self.root.geometry("800x500+400+150")
        self.pack(fill=BOTH, expand=True)

        # resizable columns and rows
        self.columnconfigure(1, weight=1)
        self.rowconfigure(6, weight=1)

        # padding for columns and rows with buttons
        self.columnconfigure(0, pad=7)
        self.columnconfigure(2, pad=7)
        self.rowconfigure(0, pad=7)
        self.rowconfigure(1, pad=7)
        self.rowconfigure(2, pad=7)
        self.rowconfigure(3, pad=7)

        # set up grid
        # noise in
        noiseChooseButton = Button(
            self, text="Choose noise file", command=noiseChooseButtonListener)
        noiseChooseButton.grid(row=0, column=0, sticky=W+E, padx=5)

        selectedNoise = StringVar()
        selectedNoise.set("not selected")
        selectedNoiseLabel = Label(
            self, textvariable=selectedNoise, background='white', relief='sunken')
        selectedNoiseLabel.grid(row=0, column=1, sticky=W+E, padx=5)

        # lecture in
        lectureChooseButton = Button(
            self, text="Choose lecture file", command=lectureChooseButtonListener)
        lectureChooseButton.grid(row=1, column=0, sticky=W+E, padx=5)

        selectedLecture = StringVar()
        selectedLecture.set("not selected")
        selectedLectureLabel = Label(
            self, textvariable=selectedLecture, background='white', relief='sunken')
        selectedLectureLabel.grid(row=1, column=1, sticky=W+E, padx=5)

        # Audacity exe in
        audacityChooseButton = Button(
            self, text="Choose audacity file", command=audacityChooseButtonListener)
        audacityChooseButton.grid(row=2, column=0, sticky=W+E, padx=5)

        selectedAudacity = StringVar()
        selectedAudacity.set("not selected")
        selectedAudacityLabel = Label(
            self, textvariable=selectedAudacity, background='white', relief='sunken')
        selectedAudacityLabel.grid(row=2, column=1, sticky=W+E, padx=5)

        # start
        startProcessingButton = Button(
            self, text="Start processing", command=startProcessingListener, background="#9dff9c")
        startProcessingButton.grid(row=0, column=2, sticky=N+E+W+S, padx=5, pady=5)

        # stop
        startProcessingButton = Button(
            self, text="Stop processing", command=stopProcessingListener, background="#ff8787")
        startProcessingButton.grid(row=1, column=2, sticky=N+E+W+S, padx=5, pady=5)


        # info label
        infoLabel = Label(
            self, text="Requirements: Audacity and ffmpeg", background='#bdfdff')
        infoLabel.grid(row=4, column=0, padx=5, pady=5, columnspan=3)

        # info label 2
        infoLabel = Label(
            self, text="If prompted, save Audacity output with default settings!")
        infoLabel.grid(row=5, column=0, padx=5, pady=5, columnspan=3)

        # Logs area
        loggingArea = scrolledtext.ScrolledText(self, state='disabled')
        loggingArea.grid(row=6, column=0, columnspan=4,
                         padx=5, sticky=E+W+S+N)
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger()
        logger.addHandler(TextHandler(loggingArea))

        # fill input with saved config
        read_config()


    def worker(self, noiseFile, lectureFile, logger, audacityPath):
        worker = guiWorker.guiWorker(logger=logger, audacityPath=audacityPath)
        worker.process_selected_file(noiseFile, lectureFile)


if __name__ == '__main__':
    root = Tk()
    myGUI(root)
    root.mainloop()
