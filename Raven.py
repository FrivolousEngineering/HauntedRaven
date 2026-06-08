import subprocess
import time
import atexit
from serial import SerialException
import maestro


class Raven:
    # For this to work you *must* set the maestro in "dual" mode via the official applications (via settings)
    # By default it's in uart mode which will not work
    def __init__(self):
        self.controller = None
        self.audio_process = None
        self.findController()
        atexit.register(self.cleanup)

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

    def nodYes(self) -> bool:
        self.perform(5, "sounds/yes.mp3")
        return True

    def nodNo(self) -> bool:
        self.perform(1, "sounds/no.mp3")
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