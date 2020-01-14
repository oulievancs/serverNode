#Authors:   Oulis Evangelos, Oulis Nikolaos, Drosos Katsibras
#===================================================================
# using flask restful
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps
import json
from flask_cors import CORS

# ==================================================================
# ==================================================================

# creating the flask app
app = Flask(__name__)
CORS(app)

# creating an API object
api = Api(app)

# ==================================================================
# making a class for a particular resource 
# the get, post methods correspond to get and post requests 
# they are automatically mapped by flask_restful. 
# other methods include put, delete, etc.
class Parking(Resource):
    def get(self):
        return parks, 200

class ParkingStatus(Resource):
    def get(self):
        return """<html>
            <head><title>ERROR</title></head>
            <body><h1>Not get at '/parkingStatus'.</h1></body>
            </html>"""
    def post(self):
        print (request)
        data = json.loads(request.data)
        print (data)
        parks[data['no']] = data['status']
        return parks[data['no']], 201


# ==================================================================
# adding the defined resources along with their corresponding urls 
api.add_resource(Parking, '/')
api.add_resource(ParkingStatus, '/parkingStatus')

# ==================================================================
# driver function
if __name__ == '__main__':
    global parks = dict()
    app.run(
            debug=True,
            host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", "5000")
    )

# END
