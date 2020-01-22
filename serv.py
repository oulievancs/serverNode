#Authors:   Oulis Evangelos, Oulis Nikolaos, Drosos Katsibras
#===================================================================
# using flask restful
from flask import Flask, request, jsonify, session
from flask_restful import Resource, Api
from json import dumps
import json
from flask_cors import CORS
import mysql.connector
import os

# ==================================================================
# ==================================================================

# creating the flask app
app = Flask(__name__)
CORS(app)

# create the secret key for session
app.secret_key = os.urandom(24)

# creating an API object
api = Api(app)

# Initialize the database Connection
mydb = mysql.connector.connect(
    host = "127.0.0.1",#"q2gen47hi68k1yrb.chr7pe7iynqr.eu-west-1.rds.amazonaws.com",
    user = "root",#"zsgmj50h7zgz9ioq",
    password = "rootP",#"omk5l1hrwsgvlcez",
    database = "PARKING"#"g0s9cnmdkziq6fsp"
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
			parks.append({"no": res[0], "status": True})
		else:
			parks.append({"no": res[0], "status": False})
	return parks

# Define a function that get if a user with exiting credencials
#	username and password is authenticated.
def isMember(username, password):
	myCursor.execute("SELECT * FROM USERS")
	myRes = myCursor.fetchall()
	
	isValid = False
	for res in myRes:
		if res[1] == username and res[2] == password:
			isValid = True
			break
	
	return isValid

# Function that return if the requested user is authenticated
# 	or not (True / False).
def isAuthenticated():
	if 'device_id' in session:
		return True
	else:
		return False


# ==================================================================
# making a class for a particular resource 
# the get, post methods correspond to get and post requests 
# they are automatically mapped by flask_restful. 
# other methods include put, delete, etc.
class Parking(Resource):
	def get(self):
		parks = None
		try:
			parks = getParkings()
		except mysql.connector.errors.DatabaseError as e:
				mydb.reconnect(attempts=1, delay=0)
		
		return parks, 200

class ParkingStatus(Resource):
	def get(self):
		return """<html>
			<head><title>ERROR</title></head>
			<body><h1>Not get at '/parkingStatus'.</h1></body>
			</html>"""
	def post(self):
		if isAuthenticated():
			# Gets the data into as a JSON Object from HTTP request.
			data = json.loads(request.data)
			
			try:
				# SQL get all Parking places status.
				parks = getParkings()
			except mysql.connector.errors.DatabaseError as e:
				mydb.reconnect(attempts=1, delay=0)
			
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
			
			try:
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
			except mysql.connector.errors.DatabaseError as e:
				mydb.reconnect(attempts=1, delay=0)
			
			return currentParking, 201
		else:
			return "Error! You aren't authenticated. [POST] /authenticate first.", 403

class Authenticate(Resource):
	def post(self):
		try:
			#Get the credencial from body of request.
			data = json.loads(request.data)
			
			if data['username'] != None and data['password'] != None and data['device'] != None:
				isValid = isMember(data['username'], data['password'])
				
				if isValid:
					session['device_id'] = data['device']
				else:
					return "Not Authenticatiove device", 403
			else:
				return "Error authentication", 403
		except mysql.connector.errors.DatabaseError as e:
				mydb.reconnect(attempts=1, delay=0)

# ==================================================================
# adding the defined resources along with their corresponding urls to REST APIs 
api.add_resource(Parking, '/')
api.add_resource(ParkingStatus, '/parkingStatus')
api.add_resource(Authenticate, '/authenticate')

# ==================================================================
# driver function
if __name__ == '__main__':
    app.run(
            debug=True,
            host=app.config.get("HOST", "localhost"),
            port=app.config.get("PORT", "8080")
    )

# END
