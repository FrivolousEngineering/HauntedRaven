import flask
from flask import request
from flask import render_template

from Raven import Raven


class Server(flask.Flask):
    STATIC_LOCATION = ""

    def __init__(self, import_name="Raven", port=80, **kwargs):
        super().__init__(import_name, **kwargs)
        self._port = port
        self._radio_instance = Raven()

        self.add_url_rule(rule="/<path:path>", view_func=self.staticHost)
        self.add_url_rule("/", endpoint="adminPage", view_func=self.renderAdminPage)

    def staticHost(self, path):
        return flask.send_from_directory(self.STATIC_LOCATION, path)

    def run(self, *args, **kwargs):
        kwargs["host"] = "0.0.0.0"
        super().run(*args, **kwargs)

    def renderAdminPage(self):
        return render_template("adminPage.html")


if __name__ == "__main__":
    print("Starting the server")
    server = Server()
    server.run()
