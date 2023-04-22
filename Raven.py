from serial import SerialException

import maestro


class Raven:
    def __init__(self):
        print("Attempting to create serial")

        self.controller = None
        self.findController()

    def findController(self):
        for i in range(0, 10):
            try:
                port = "/dev/ttyACM%s" % i
                self.controller = maestro.Controller(ttyStr= port)
                print("Connected with serial %s" % port)
                break
            except:
                pass

    def nodYes(self) -> bool:
        self._checkController()
        if self.controller:
            self.controller.runScriptSub(2)
            return True
        return False

    def nodNo(self) -> bool:
        self._checkController()
        if self.controller:
            self.controller.runScriptSub(1)
            return True
        return False

    def _checkController(self):
        try:
            self.controller.getPosition(0)
        except (SerialException, AttributeError):
            # We failed to write, so it must've gotten disconnected or we were never connected in the first place.
            self.controller = None
            self.findController()
