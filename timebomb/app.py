from flask import Flask
from flask_restplus import Api, Resource
import socketio

app = Flask(__name__)
api = Api(app=app)

ns_conf = api.namespace("conferences", description="Conference operations")


@ns_conf.route("/")
class ConferenceList(Resource):
    def get(self):
        """
        returns a list of conferences
        """

    def post(self):
        """
        Adds a new conference to the list
        """


@ns_conf.route("/<int:id>")
class Conference(Resource):
    def get(self, id):
        """
        Displays a conference's details
        """

    def put(self, id):
        """
        Edits a selected conference
        """


if __name__ == "__main__":
    app.run(debug=True)


sio = socketio.Server(async_mode="eventlet")
socket_io_app = socketio.WSGIApp(sio, api)
