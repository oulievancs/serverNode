#Authors:   Oulis Evangelos, Oulis Nikolaos, Drosos Katsibras
#===================================================================
# using flask restful
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps
import json
from flask_cors import CORS
import mysql.connector

# ==================================================================
# ==================================================================

# creating the flask app
app = Flask(__name__)
CORS(app)

# creating an API object
api = Api(app)

# Initialize the database Connection
mydb = mysql.connector.connect(
    host = "q2gen47hi68k1yrb.chr7pe7iynqr.eu-west-1.rds.amazonaws.com",
    user = "zsgmj50h7zgz9ioq",
    password = "omk5l1hrwsgvlcez",
    database = "g0s9cnmdkziq6fsp"
)

myCursor = mydb.cursor()

# ==================================

# ==================================================================
# making a class for a particular resource 
# the get, post methods correspond to get and post requests 
# they are automatically mapped by flask_restful. 
# other methods include put, delete, etc.
class Parking(Resource):
    def get(self):
        parks = dict()
        
        myCursor.execute("SELECT * FROM PARKING")
        myRes = myCursor.fetchall()
        
        for res in myRes:
            parks[res[0]] = res[1]
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
        
        parks = dict()
        
        myCursor.execute("SELECT * FROM PARKING")
        myRes = myCursor.fetchall()
        
        thereIs = False
        for res in myRes:
            parks[res[0]] = res[1]
            if res[0] == data['no']:
                thereIs = True
        if not thereIs:
            myCursor.execute("INSERT INTO PARKING (PARKING_CODE, PARKING_STATUS) VALUES (%s, %s)", (int (data['no']), int(data['status'])))
        
        parks[data['no']] = data['status']
        return parks[data['no']], 201


# ==================================================================
# adding the defined resources along with their corresponding urls 
api.add_resource(Parking, '/')
api.add_resource(ParkingStatus, '/parkingStatus')

# ==================================================================
# driver function
if __name__ == '__main__':
    app.run(
            debug=True,
            host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", "5000")
    )

# END
