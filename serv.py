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
# Define our functions.
# Define a function that gets the parking status
#   for all parking codes.
def getParkings():
    parks = []
    
    myCursor.execute("SELECT * FROM PARKING")
    myRes = myCursor.fetchall()
    
    for res in myRes:
        if res[1] == 1:
            parks.append = ({"no": res[0], "status": True})
        else:
            parks.append = ({"no": res[0], "status": False})
    return parks

# ==================================================================
# making a class for a particular resource 
# the get, post methods correspond to get and post requests 
# they are automatically mapped by flask_restful. 
# other methods include put, delete, etc.
class Parking(Resource):
    def get(self):
        parks = getParkings()
        return parks, 200

class ParkingStatus(Resource):
    def get(self):
        return """<html>
            <head><title>ERROR</title></head>
            <body><h1>Not get at '/parkingStatus'.</h1></body>
            </html>"""
    def post(self):
        # Gets the data into a JSON Object.
        data = json.loads(request.data)
        
        # SQL get all Parking places status.
        parks = getParkings()
        
        currentParking = {}
        for park in parks:
            if park['no'] == data['no']:
                currentParking = park
                break;
        
        thereIs = False
        toUpdate = False
        try:
            if currentParking['status'] != data['status']:
                toUpdate = True
            thereIs = True
        except IndexError:
            # handle Index Error
            thereIs = False
            toUpdate = False
        except KeyError:
            # handle the KeyError
            thereIs = False
            toUpdate = False
        
        if not thereIs:
            # Make a new insert entry for a new Parking Code.
            values = (int(data['no']), int(data['status']))
            myCursor.execute("INSERT INTO PARKING (PARKING_CODE, PARKING_STATUS) VALUES (%s, %s)", values)
            mydb.commit()
            parks = getParkings()
        elif toUpdate:
            # Make an Update status for Parking Code that availability changed.
            values = (int(data['status']), int(data['no']))
            myCursor.execute("UPDATE PARKING SET PARKING_STATUS=%s WHERE PARKING_CODE=%s", values)
            mydb.commit()
            parks = getParkings()
        
        return currentParking, 201


# ==================================================================
# adding the defined resources along with their corresponding urls to REST APIs 
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
