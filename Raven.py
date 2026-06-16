import subprocess
import time
import atexit
from serial import SerialException
import maestro


class Raven:
    # For this to work you *must* set the maestro in "dual" mode via the official applications (via settings)
    # By default it's in uart mode which will not work
    def __init__(self):

        # Tie all animations to the sounds
        self._animations = {
            "All_will_be_made_clear_echo": 1,
            "All_will_be_made_clear_normal": 2,
            "Death_is_too_good_for_you": 3,
            "Fuck_Off_Full": 4,
            "Fuck_Off_Short": 5,
            "Gimme_gimme_snack": 6,
            "Gimme_Give_it_to_me": 7,
            "I_Know_It_All_echo": 8,
            "I_Know_It_All": 9,
            "I_See_You_short": 10,
            "Mine_short": 11,
            "Nevermore_1": 12,
            "Nevermore_2": 13,
            "Nevermore_3": 14,
            "No_absolutely_not": 15,
            "Snack_short": 16,
            "Theres_no_hiding_long": 17,
            "Truth_wont_drown_echo": 18,
            "Truth_wont_drown_short": 19,
            "You_cant_hide_short": 20,
        }

        self.controller = None
        self.audio_process = None
        self.findController()
        atexit.register(self.cleanup)

    def getAnimations(self):
        return self._animations

    def cleanup(self):
        if self.audio_process and self.audio_process.poll() is None:
            self.audio_process.terminate()
            try:
                self.audio_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.audio_process.kill()

    def findController(self):
        for port in ["/dev/ttyACM0", "/dev/ttyACM1"]:
            try:
                controller = maestro.Controller(ttyStr=port)
                controller.getPosition(0) # verify that the Maestro responds (aka; is correctly connected)
                self.controller = controller
                print(f"Connected to Maestro command port: {port}")
                return
            except Exception as e:
                print(f"{port} did not work: {e}")

        raise RuntimeError("Could not find Maestro command port")

    def stopAudio(self):
        if self.audio_process and self.audio_process.poll() is None:
            self.audio_process.terminate()
            try:
                self.audio_process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self.audio_process.kill()

        self.audio_process = None

    def playAudio(self, filename: str):
        self.stopAudio()

        self.audio_process = subprocess.Popen(
            ["mpg123", "-q", filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return self.audio_process

    def perform(self, script_id: int, audio_file: str | None = None):
        self._checkController()

        if audio_file:
            self.playAudio(audio_file)

        self.controller.runScriptSub(0)
        time.sleep(1)
        self.controller.runScriptSub(script_id)

    def doCommand(self, command_name: str) -> bool:
        if command_name not in self._animations:
            return False
        self.perform(self._animations[command_name], f"Sounds/{command_name}.mp3")
        return True

    def nodYes(self) -> bool:
        self.perform(5, "Sounds/yes.mp3")
        return True

    def nodNo(self) -> bool:
        self.perform(1, "Sounds/no.mp3")
        return True

    def _checkController(self):
        try:
            self.controller.getPosition(0)
        except (SerialException, AttributeError):
            print("failed to write to controller")
            self.controller = None
            self.findController()

if __name__ == "__main__":

    raven = Raven()
    print("brr?")
    raven.perform(5, "test.mp3")