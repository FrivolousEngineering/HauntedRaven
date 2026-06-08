from serial import SerialException

import maestro
import time

from serial.tools import list_ports


class Raven:
    # For this to work you *must* set the maestro in "dual" mode via the official applications (via settings)
    # By default it's in uart mode which will not work
    def __init__(self): 
        print("Attempting to create serial")

        self.controller = None
        self.findController()

    def findController(self):
        for port in ["/dev/ttyACM0", "/dev/ttyACM1"]:
            try:
                controller = maestro.Controller(ttyStr=port)
                controller.getPosition(0)  # verify Maestro responds
                self.controller = controller
                print(f"Connected to Maestro command port: {port}")
                return
            except Exception as e:
                print(f"{port} did not work: {e}")

        raise RuntimeError("Could not find Maestro command port")

    def nodYes(self) -> bool:
        self._checkController()
        if self.controller:
            self.controller.runScriptSub(0)
            time.sleep(1)
            self.controller.runScriptSub(5)
            return True
        return False

    def nodNo(self) -> bool:
        self._checkController()
        if self.controller:
            self.controller.runScriptSub(0)
            time.sleep(1)
            self.controller.runScriptSub(1)
            return True
        return False

    def _checkController(self):
        try:
            self.controller.getPosition(0)
        except (SerialException, AttributeError):
            print("failed to write to controller")
            # We failed to write, so it must've gotten disconnected or we were never connected in the first place.
            self.controller = None
            self.findController()


if __name__ == "__main__":

    raven = Raven()
    raven.controller.getPosition(0)
    raven.controller.runScriptSub(0)
    raven.controller.runScriptSub(1)
    raven.controller.runScriptSub(5)

    print('brr?')
    time.sleep(0.5)
    raven.controller.runScriptSub(5)
    time.sleep(1)

