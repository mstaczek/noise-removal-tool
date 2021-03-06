import os
import sys

class AudacityController:
    """
    This class tests if connection to Audacity was succesful.
    Then can be used to send commands to Audacity to apply selected effects and more.

    Source:
    https://github.com/audacity/audacity/blob/master/scripts/piped-work/pipe_test.py
    """

    TONAME=''
    FROMNAME=''
    EOL=''
    logger=print
    failed = 0

    def __init__(self, logger=print) -> None:
        self.logger=logger
        if sys.platform == 'win32':
            self.TONAME = '\\\\.\\pipe\\ToSrvPipe'
            self.FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
            self.EOL = '\r\n\0'
        else:
            logger("sys.platform != 'win32'")

        failed = 0
        logger("Write to  \"" + self.TONAME +"\"")
        if not os.path.exists(self.TONAME):
            logger(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
            failed = 1

        logger("Read from \"" + self.FROMNAME +"\"")
        if not os.path.exists(self.FROMNAME):
            logger(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
            failed = 1
        
        if failed == 1:
            self.failed = 1
            return

        logger("-- Both pipes exist.  Good.")

        self.TOFILE = open(self.TONAME, 'w')
        logger("-- File to write to has been opened")
        self.FROMFILE = open(self.FROMNAME, 'rt')
        logger("-- File to read from has now been opened too\r\n")


    def _send_command(self, command):
        self.logger("BatchCommand: "+command)
        self.TOFILE.write(command + self.EOL)
        self.TOFILE.flush()

    def _get_response(self):
        result = ''
        line = ''
        while True:
            result += line
            line = self.FROMFILE.readline()
            if line == '\n' and len(result) > 0:
                break
        return result[1:]

    def run(self, command):
        self._send_command(command)
        response = self._get_response()
        self.logger(response)
        return response  


class AudacityCommands:  
    """
    Class sending commands to Audacity via AudacityController described above
    and passed to this class in constructor.

    Modify this class according to your needs (check Audacity scripting
    documentation at https://manual.audacityteam.org/man/scripting_reference.html).

    Side note: 
    in Audacity v2.4.2 NoiseReduction is said to be not available however it
    turns out it is working as intended.
    """
    audacityCtrl = None

    def __init__(self, audacityCtrl) -> None:
        self.audacityCtrl = audacityCtrl

    def get_noise_profile(self, path_noise):
        self.audacityCtrl.run('Import2:Filename='+path_noise)
        self.audacityCtrl.run('NoiseReduction:Use_Preset="<Factory Defaults>"')

    def open_new_window(self):
        self.audacityCtrl.run('New')

    def import_test_file(self, path_input):
        self.audacityCtrl.run('Import2:Filename='+path_input)

    def apply_effects(self):
        self.audacityCtrl.run('SelectAll')
        self.audacityCtrl.run('Normalize:ApplyGain="1" PeakLevel="-2" RemoveDcOffset="1" StereoIndependent="0"')
        self.audacityCtrl.run('NoiseReduction:Use_Preset="<Factory Defaults>"')
        self.audacityCtrl.run('Compressor:Threshold="-13" NoiseFloor="-40" Ratio="6" AttackTime="0.28" ReleaseTime="1" Normalize="0" UsePeak="0"')

    def export_to_wav(self):
        self.audacityCtrl.run('ExportWav')