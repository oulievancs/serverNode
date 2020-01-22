#Authors:   Oulis Evangelos, Oulis Nikolaos, Drosos Katsibras
#===================================================================
# using flask restful
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps
import json
from flask_cors import CORS
import mysql.connector
from base64 import b64encode
from os import urandom

# ==================================================================
# ==================================================================

# creating the flask app
app = Flask(__name__)
CORS(app)

# Session list
sessions = []

# Chart values
chart = []

# creating an API object
api = Api(app)


# Initialize the database Connection (Classified)
class mySqlConnect:
	def __init__(self):
		self.con = con = mysql.connector.connect(
			host = "127.0.0.1",#"q2gen47hi68k1yrb.chr7pe7iynqr.eu-west-1.rds.amazonaws.com",
			user = "root",#"zsgmj50h7zgz9ioq",
			password = "rootP",#"omk5l1hrwsgvlcez",
			database = "PARKING"#"g0s9cnmdkziq6fsp"
		)
		
		self.cur = self.con.cursor();
	
	def __del__(self):
		self.cur.close()
		self.con.close()
	
	@property
	def cursor(self):
		return self.cur
	
	@property
	def connection(self):
		return self.con

# ==================================
# Define our functions.
# Define a function that gets the parking status
#   for all parking codes.
def getParkings():
	parks = []
	
	sql = mySqlConnect()
	myCursor = sql.cur
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
	mysql = mySqlConnect()
	myCursor = mysql.cur
	
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
def isAuthenticated(data):
	try:
		if data['cookie'] in sessions:
			return True
		else:
			return False
	except KeyError as e:
		return False

# For the chart Data.
def updateChart():
	parks = getParkings()
	all_parks = len(parks)
	
	full = 0
	
	for p in parks:
		if p['status'] == False:
			full+=1
	
	j = 1
	if len(chart) < 16 :
		chart.append(full)
		print (chart)
	elif len(chart) == 16:
		for i in chart:
			chart[j] = i
			j+=1
			
			if j == 16:
				break
		chart[0] = full
	return True


# ==================================================================
# making a class for a particular resource 
# the get, post methods correspond to get and post requests 
# they are automatically mapped by flask_restful. 
# other methods include put, delete, etc.

# Resource that returns th whole parking status in a JSON
class Parking(Resource):
	def get(self):
		parks = None
		try:
			parks = getParkings()
		except (mysql.connector.errors.DatabaseError, mysql.connector.errors.InterfaceError) as e:
				print ("An error")
		
		return parks, 200

# Update parking status resource from authenticated only Node
class ParkingStatus(Resource):
	def get(self):
		return """<html>
			<head><title>ERROR</title></head>
			<body><h1>Not get at '/parkingStatus'.</h1></body>
			</html>"""
	def post(self):
		# Gets the data into as a JSON Object from HTTP request.
		data = json.loads(request.data)
		if isAuthenticated(data):
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
				mysql = mySqlConnect()
				myCursor = mysql.cur
				con = mysql.con
				
				if not thereIs:
					# Make a new insert entry for a new Parking Code.
					values = (int(data['no']), int(data['status']))
					myCursor.execute("INSERT INTO PARKING (PARKING_CODE, PARKING_STATUS) VALUES (%s, %s)", values)
					con.commit()
					parks = getParkings()
					
					updateChart()
				elif toUpdate:
					# Make an Update status for Parking Code that availability changed.
					values = (int(data['status']), int(data['no']))
					myCursor.execute("UPDATE PARKING SET PARKING_STATUS=%s WHERE PARKING_CODE=%s", values)
					con.commit()
					parks = getParkings()
					
					updateChart()
			except (mysql.connector.errors.DatabaseError, mysql.connector.errors.InterfaceError) as e:
				print ("An error")
			
			return currentParking, 201
		else:
			return "Error! You aren't authenticated. [POST] /authenticate first.", 403

# Authentication resource.
class Authenticate(Resource):
	def post(self):
		try:
			#Get the credencial from body of request.
			data = json.loads(request.data)
			
			if data['username'] != None and data['password'] != None and data['device'] != None:
				isValid = isMember(data['username'], data['password'])
				
				if isValid:
					session_key = str(b64encode(urandom(32)).decode('utf-8'))
					
					# Send the cookie value back to clinet.
					session = {"cookie": session_key}
					sessions.append(session_key)
					return session, 200
				else:
					return "Not Authenticative device", 403
			else:
				return "Error authentication", 403
		except (mysql.connector.errors.DatabaseError, mysql.connector.errors.InterfaceError) as e:
				print ("An error")

# Chart
class Chart(Resource):
	def get(self):
		result = dict()
		
		j = 1
		for i in chart:
			result[j] = i
			j += 1
		
		print (result)
		return result, 200

# ==================================================================
# matches the defined resources to their corresponding urls to REST APIs 
api.add_resource(Parking, '/')
api.add_resource(ParkingStatus, '/parkingStatus')
api.add_resource(Authenticate, '/authenticate')
api.add_resource(Chart, '/chart')

# ==================================================================
# ===========================MAIN CLASS=============================
# driver function "Main Class"
if __name__ == '__main__':
    app.run(
            debug=True,
            host=app.config.get("HOST", "localhost"),
            port=app.config.get("PORT", "8080")
    )

# END
