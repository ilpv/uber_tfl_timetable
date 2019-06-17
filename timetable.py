from flask import Flask
from flask import render_template, request, jsonify, send_from_directory
import database_shard
import os

app = Flask(__name__)
database_shard.init()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coordinates', methods=['POST'])
#return stops near coordinates 
def coordinates():
    jsn = request.get_json()
    lat = jsn["location"]["lat"]
    lon = jsn["location"]["lng"]
    stops = database_shard.getNearestStops(lat,lon)
    res = {}
    res["Error"] = 0
    res["stopPoints"] = stops 
    return jsonify(res)

@app.route('/timetable', methods=['POST'])
#return timetable for stopid 
def timetable():
    jsn = request.get_json()
    lat = jsn["location"]["lat"]
    lon = jsn["location"]["lng"]
    stopid = jsn["location"]["id"]
    times = database_shard.getTimeTable(lat,lon,stopid)
    return jsonify(times)
