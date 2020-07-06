# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 18:06:12 2019

@author: danielm
"""

import os
import time
from datetime import datetime
from uuid import uuid4

import psycopg2
from psycopg2 import sql
from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "super secret key"


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/bomen_mvt/<z>/<x>/<y>")
def get_boom_tiles(z, x, y):
    query = """
    SELECT ST_AsMVT(q, 'bomen', 4096, 'mvt_geom')
         FROM (
                 SELECT
                    tree_id, hoogte, elementid, elementtype, aantalbomen, avg_height,
                    ST_AsMVTGeom(
                            geom,
                            TileBBox(%(z)s, %(x)s, %(y)s),
                            4096,
                            256,
                            false
                    ) mvt_geom
                 FROM lasreg_api.bomen  
                 WHERE geom && TileBBox(%(z)s, %(x)s, %(y)s)
                 AND ST_Intersects(geom, TileBBox(%(z)s, %(x)s, %(y)s))
         ) q;
    """
    CACHE_PATH = './LasReg_mvt_cache_bomen'
    cachefile = "{}/{}/{}/{}".format(CACHE_PATH, z, x, y)
    if os.path.exists(cachefile) and time.time() - os.path.getmtime(cachefile) < 300:
        with open(cachefile, "rb") as f:
            response = app.make_response(f.read())
    else:
        connection = psycopg2.connect(user = "danielm", password = "", host = "mimas.geodan.nl", port = "5432", database = "research")
        cursor = connection.cursor()
        cursor.execute(query, {'z': z, 'x': x, 'y': y})
        result = cursor.fetchone()[0]
        connection.close()
        if not os.path.exists("{}/{}/{}".format(CACHE_PATH, z, x)):
            os.makedirs("{}/{}/{}".format(CACHE_PATH, z, x))
        with open(cachefile, "wb") as f:
            f.write(bytes(result))
        response = app.make_response(bytes(result))
    response.headers['Content-Type'] = 'application/x-protobuf'
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.route("/landschapselementen_mvt/<z>/<x>/<y>")
def get_LSE_tiles(z, x, y):
    query = """
    SELECT ST_AsMVT(q, 'landschapselementen', 4096, 'mvt_geom')
         FROM (
                 SELECT
                    "identificatie.lokaalID" as elementid, typeLandschapselement as elementtype, 
                    aantalBomen, hoogte, onderhoudsStatus, inOnderzoek, bronhouder,
                    ST_AsMVTGeom(
                            geometrie2d,
                            TileBBox(%(z)s, %(x)s, %(y)s),
                            4096,
                            256,
                            false
                    ) mvt_geom
                 FROM lasreg_api.landschapselementen  
                 WHERE geometrie2d && TileBBox(%(z)s, %(x)s, %(y)s)
                 AND ST_Intersects(geometrie2d, TileBBox(%(z)s, %(x)s, %(y)s))
         ) q;
    """
    CACHE_PATH = './LasReg_mvt_cache_elementen'
    cachefile = "{}/{}/{}/{}".format(CACHE_PATH, z, x, y)
    if os.path.exists(cachefile) and time.time() - os.path.getmtime(cachefile) < 300:
        with open(cachefile, "rb") as f:
            response = app.make_response(f.read())
    else:
        connection = psycopg2.connect(user = "danielm", password = "", host = "mimas.geodan.nl", port = "5432", database = "research")
        cursor = connection.cursor()
        cursor.execute(query, {'z': z, 'x': x, 'y': y})
        result = cursor.fetchone()[0]
        connection.close()
        if not os.path.exists("{}/{}/{}".format(CACHE_PATH, z, x)):
            os.makedirs("{}/{}/{}".format(CACHE_PATH, z, x))
        with open(cachefile, "wb") as f:
            f.write(bytes(result))
        response = app.make_response(bytes(result))
    response.headers['Content-Type'] = 'application/x-protobuf'
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.route("/geschiedenis/<id>")
def get_geschiedenis(id):
    query = """
SELECT json_agg(ev) FROM (
SELECT *, to_char(datetime, 'DD-MM-YYYY HH24:MI') as tijd
FROM lasreg_api.events
WHERE landschapselementid = %s
ORDER BY datetime
	) as ev;
    """
    connection = psycopg2.connect(user = "danielm", password = "", host = "mimas.geodan.nl", port = "5432", database = "research") 
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()[0]
    connection.close()
    return jsonify(result)


@app.route("/opmerking/<id>/<opm_type>/<author>/<text>")
def add_opmerking(id, opm_type, author, text):
    connection = psycopg2.connect(user = "danielm", password = "", host = "mimas.geodan.nl", port = "5432", database = "research")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO lasreg_api.events VALUES (%s, %s, %s, %s, false, %s, %s);", 
                    (str(uuid4()), id, opm_type, author, datetime.now(), text))
    connection.commit()
    connection.close()
    return get_geschiedenis(id)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=1500)



