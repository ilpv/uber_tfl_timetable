from flask import Flask
from flask import render_template, request, jsonify, send_from_directory
from database_shard import init, getNearestStops, getTimeTable
import os
app = Flask(__name__)
db = init()

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
    stops = getNearestStops(lat,lon,db)
    res = {}
    res["Error"] = 0
    res["stopPoints"] = stops 
    return jsonify(res)

@app.route('/timetable', methods=['POST'])
#return timetable for stopid 
def timetable():
    jsn = request.get_json()
    naptanId = jsn["stopid"]
    times = getTimeTable(naptanId,db)
    return jsonify(times)
