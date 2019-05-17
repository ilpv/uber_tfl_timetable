from flask import Flask
from flask import render_template, request, jsonify
import tfl_api

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coordinates', methods=['POST'])
#return stops near coordinates 
def coordinates():
    jsn = request.get_json()
    lat = jsn["location"]["lat"]
    lon = jsn["location"]["lng"]
    stops = tfl_api.getNearestStops(lat,lon)
    return jsonify(stops)

@app.route('/timetable', methods=['POST'])
#return timetable for stopid 
def timetable():
    jsn = request.get_json()
    naptanId = jsn["stopid"]
    times = tfl_api.getTimeTable(naptanId)
    return jsonify(times)
