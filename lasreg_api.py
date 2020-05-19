# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 18:06:12 2019

@author: danielm
"""

import os
import time

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


@app.route("/bomen")
def get_boom():
    query = """
select row_to_json(fc)
from (
    select
        'FeatureCollection' as "type",
        COALESCE(array_to_json(array_agg(f)), '[]'::json) as "features"
    from (
        select
            'Feature' as "type",
            ST_AsGeoJSON(ST_Transform(geom, 4326), 6) :: json as "geometry",
            (
                select json_strip_nulls(row_to_json(t))
                from (
                    select tree_id, height, elementid, elementtype, aantal_bomen, avg_height
                ) t
            ) as "properties"
        FROM achterhoek.bomen a
        WHERE ST_WITHIN(geom, ST_MakeEnvelope(241719, 437008, 243324, 437826, 28992))
    ) as f
) as fc;
    """
    connection = psycopg2.connect(user = "danielm",
                                  password = "",
                                  host = "localhost",
                                  port = "5432",
                                  database = "Lasreg")
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]
    connection.close()
    return jsonify(result)


@app.route("/bomen_mvt/<z>/<x>/<y>")
def get_boom_tiles(z, x, y):
    query = """
    SELECT ST_AsMVT(q, 'bomen', 4096, 'mvt_geom')
         FROM (
                 SELECT
                 tree_id, height, elementid, elementtype, aantal_bomen, avg_height,
                 ST_AsMVTGeom(
                         geom_3857,
                         TileBBox(%(z)s, %(x)s, %(y)s),
                         4096,
                         256,
                         false
                 ) mvt_geom
                 FROM achterhoek.bomen  
                 WHERE geom_3857 && TileBBox(%(z)s, %(x)s, %(y)s)
                 AND ST_Intersects(geom_3857, TileBBox(%(z)s, %(x)s, %(y)s))
         ) q;
    """
    CACHE_PATH = './LasReg_mvt_cache'
    cachefile = "{}/{}/{}/{}".format(CACHE_PATH, z, x, y)
    if os.path.exists(cachefile) and time.time() - os.path.getmtime(cachefile) < 300:
        with open(cachefile, "rb") as f:
            response = app.make_response(f.read())
    else:
        connection = psycopg2.connect(user = "danielm", password = "", host = "localhost", port = "5432", database = "Lasreg")
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


@app.route("/poelen")
def get_poel():
    query = """
select row_to_json(fc)
from (
    select
        'FeatureCollection' as "type",
        COALESCE(array_to_json(array_agg(f)), '[]'::json) as "features"
    from (
        select
            'Feature' as "type",
            ST_AsGeoJSON(ST_Transform(shape, 4326), 6) :: json as "geometry",
            (
                select json_strip_nulls(row_to_json(t))
                from (
                    select objectid as elementid, 'Poel' as elementtype, ST_AREA(shape) as area
                ) t
            ) as "properties"
        FROM achterhoek.anlb_hout_water_zone_2
        WHERE left(pakket_omschrijving, 4) = 'Poel'
    ) as f
) as fc;
    """
    connection = psycopg2.connect(user = "danielm",
                                  password = "",
                                  host = "localhost",
                                  port = "5432",
                                  database = "Lasreg")
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]
    connection.close()
    return jsonify(result)
    
@app.route("/heggen")
def get_heg():
    query = """
select row_to_json(fc)
from (
    select
        'FeatureCollection' as "type",
        COALESCE(array_to_json(array_agg(f)), '[]'::json) as "features"
    from (
        select
            'Feature' as "type",
            ST_AsGeoJSON(ST_Transform(shape, 4326), 6) :: json as "geometry",
            (
                select json_strip_nulls(row_to_json(t))
                from (
                    select objectid as elementid, 'Heg' as elementtype, 1.5 as height, shape_length as length, shape_area as area
                ) t
            ) as "properties"
        FROM achterhoek.anlb_hout_water_zone_2
        WHERE split_part(pakket_omschrijving, ':', 1) = 'Knip- en scheerheg'
        OR split_part(pakket_omschrijving, ';', 1) = 'Struweelhaag'
        OR pakket_omschrijving = 'Struweelrand'
    ) as f
) as fc;
    """
    connection = psycopg2.connect(user = "danielm",
                                  password = "",
                                  host = "localhost",
                                  port = "5432",
                                  database = "Lasreg")
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]
    connection.close()
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1500)



