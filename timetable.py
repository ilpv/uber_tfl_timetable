from flask import Flask
from flask import render_template, render_template_string, request, jsonify
import tfl_api
import json
import logging

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coordinates', methods=['POST'])
def coordinates():
    cds = request.get_json()
    lat = cds["location"]["lat"]
    lon = cds["location"]["lng"]
#    logging.info("Lat=%f",lat)
#    logging.info("Lat=%f",lon)
#find nearest stops and show timestable
    stops = tfl_api.getNearestStops(lat,lon)
#    logging.info(stops)
    return jsonify(stops)
