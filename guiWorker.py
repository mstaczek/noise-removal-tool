from audacityController import AudacityController, AudacityCommands
import psutil
import time
import subprocess
import threading
import os
import subprocess

class guiWorker:
    logger=None
    audacityPath=None
    audacityCtrl=None
    init_failed=False
    fixedAudioPath=None

    def __init__(self, logger=print, audacityPath="") -> None:
        self.logger=logger
        self._prepare_audacity(audacityPath)

    def process_selected_file(self, noise_path, file_for_proccessing):
        self.logger("\n------------ Processing start ------------\n")
        if(not self.init_failed):
            
            self._audacity_process_selected_file(noise_path, file_for_proccessing)
            self._ffmpeg_process_selected_file(file_for_proccessing)

        else:
            self.logger("Failed connecting to Audacity.")
            kill_audacity()
        self.logger("\n------------ Finished processing ---------")

    def _ffmpeg_process_selected_file(self, original_video):
        fixedAudioPath ,outputPath = self._get_paths_for_ffmpeg(original_video)

        self.logger("\n--------- FFMPEG - Processing start ---------\n")
        self.logger("Lecture original file:\n" + original_video + "\n")
        self.logger("Fixed audio: \n" + fixedAudioPath + "\n")
        self.logger("Output: \n" + outputPath + "\n")

        args = ["ffmpeg","-i",original_video,"-i",fixedAudioPath,"-c:v","copy","-c:a","aac","-map","0:v:0","-map","1:a:0",outputPath,"-y"]
        command = " ".join(args)
        os.system("start /wait cmd /k " + command)
        # with subprocess.Popen(args,stdout=subprocess.PIPE) as proc:
        #     self.logger(proc.stdout.read())

        self.logger("\n------------ FFMPEG - Finished processing ---------")

    def _get_paths_for_ffmpeg(self, original_video):
        fixedAudioPath = self._get_fixed_audio_path(original_video)
        outputPath = os.path.splitext(original_video)[0]+"-fixed.mp4"
        return fixedAudioPath, outputPath

    def _get_fixed_audio_path(self, original_video):
        filenameWithoutExtension = os.path.splitext(os.path.basename(original_video))[0]
        fixedAudioPath = os.path.join(os.path.dirname(original_video), "macro-output",filenameWithoutExtension+ ".wav")
        return fixedAudioPath

    def _prepare_audacity(self,audacityPath):
        if(audacityPath==""):
            self.logger("No Audacity path specified.")
            return
        self.audacityPath=audacityPath
        kill_audacity()
        self._open_audacity()
        self._get_audacity_ctrl()

    def _get_audacity_ctrl(self):
        for _ in range(5):
            time.sleep(1)
            self.audacityCtrl = AudacityController(logger=self.logger)
            if not self.audacityCtrl.failed:
                time.sleep(3)
                return
        self.init_failed=True

    def _open_audacity(self):
        def audacityProcess():
            subprocess.Popen([self.audacityPath])
        t1 = threading.Thread(daemon=True,target=audacityProcess,args=[])
        t1.start()
        t1.join()

    def _audacity_process_selected_file(self, path_noise, path_input):
        self.logger("\n--------- Audacity - Processing start ---------\n")
        self.logger("Noise file: \n" + path_noise + "\n")
        self.logger("Lecture file:\n" + path_input + "\n")

        AudaCMD = AudacityCommands(self.audacityCtrl)
        AudaCMD.get_noise_profile(path_noise)
        AudaCMD.open_new_window()
        AudaCMD.import_test_file(path_input)
        AudaCMD.apply_effects()
        if os.path.exists(self._get_fixed_audio_path(path_input)):
            os.remove(self._get_fixed_audio_path(path_input))
        AudaCMD.export_to_wav()
        time.sleep(0.5)
        kill_audacity()
        self.logger("\n--------- Audacity - Finished processing ------")

def kill_audacity(msg="", logger=print):
    if(msg!=""):
        logger(msg)
    PROCNAME = "audacity.exe"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

    