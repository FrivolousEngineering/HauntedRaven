import flask
from flask import request
from flask import render_template

from Raven import Raven


class Server(flask.Flask):
    STATIC_LOCATION = ""

    def __init__(self, import_name="Raven", port=80, **kwargs):
        super().__init__(import_name, **kwargs)
        self._port = port
        self._raven = Raven()

        self.add_url_rule(rule="/<path:path>", view_func=self.staticHost)
        self.add_url_rule("/", endpoint="adminPage", view_func=self.renderAdminPage)

        self.add_url_rule("/startAnimation", endpoint="startAnimation",
                          view_func=self.startAnimation, methods=["POST"])

    def staticHost(self, path):
        return flask.send_from_directory(self.STATIC_LOCATION, path)

    def run(self, *args, **kwargs):
        kwargs["host"] = "0.0.0.0"
        super().run(*args, **kwargs)

    def renderAdminPage(self):
        return render_template("adminPage.html")

    def startAnimation(self):
        animation_to_start = request.form["animation"]
        command_succeeded = False
        if animation_to_start == "yes":
            command_succeeded = self._raven.nodYes()
        elif animation_to_start == "no":
            command_succeeded = self._raven.nodNo()

        if command_succeeded:
            return flask.Response(flask.json.dumps({"message": "Animation Started"}), status=200,
                                  mimetype='application/json')

        return flask.Response(flask.json.dumps({"message": "Unable to start animation"}), status=200,
                              mimetype='application/json')



if __name__ == "__main__":
    print("Starting the server")
    server = Server()
    server.run()
