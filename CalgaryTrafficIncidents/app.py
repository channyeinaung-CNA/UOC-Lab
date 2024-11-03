# YouTube Video Link: https://youtu.be/hHqLQ5mNDwE
import json
import os

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# setup application context
app.app_context().push()

# Load password from pass.txt
with open("pass.txt") as f:
    password = f.readline().strip()

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://postgres:{password}@localhost:5432/ENGO451"
)

# Initialize SQLAlchemy only once
db = SQLAlchemy(app)

# run flask on port 5050    : flask run --port 5050
# check if the connection is successful
try:
    db.engine.connect()
    print("Connection to the database is successful")
except Exception as e:
    print(f"Error: {e}")


# Create a route for the home page. "/" is the default route
@app.route("/")  # Home page
def index():
    return render_template("index.html")


# Create a route for the map data that will return the data in GeoJSON format
@app.route("/map_data")
def map_data():
    # Query for geometries and their attributes from different tables
    layers = {}
    tables = [
        "TrafficIncidents",
        "TrafficSignals",
        "TrafficCameras",
    ]

    queries = [
        f'SELECT ST_AsGeoJSON(geom3776) as geom3776, id, incident_i, descriptio, date_start, time_start FROM "Lab3"."TrafficIncidents"',
        f'SELECT ST_AsGeoJSON(geom3776) as geom3776, unitid, firstroad, secondroad, int_type FROM "Lab3"."TrafficSignals"',
        f'SELECT ST_AsGeoJSON(geom3776) as geom3776, camera_loc, camera_url FROM "Lab3"."TrafficCameras"',
    ]

    for table in tables:
        # Make a query to select the geometry and name from the tabl
        query = queries[tables.index(table)]
        # Make the query as text(sql) and execute it
        query = db.text(query)
        result = db.session.execute(query)
        # access cursor object and fetch all the rows
        result = result.fetchall()
        # print(result)
        layers[table] = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    # load the geometry from the database
                    "coordinates": json.loads(row[0])["coordinates"],
                },
                "properties": {
                    "id": row[1] if table == "TrafficIncidents" else None,
                    "location": row[2] if table == "TrafficIncidents" else None,
                    "description": row[3] if table == "TrafficIncidents" else None,
                    "date": row[4] if table == "TrafficIncidents" else None,
                    "time": row[5] if table == "TrafficIncidents" else None,
                    "unitid": row[1] if table == "TrafficSignals" else None,
                    "firstroad": row[2] if table == "TrafficSignals" else None,
                    "secondroad": row[3] if table == "TrafficSignals" else None,
                    "int_type": row[4] if table == "TrafficSignals" else None,
                    "camera_loc": row[1] if table == "TrafficCameras" else None,
                    "camera_url": row[2] if table == "TrafficCameras" else None,
                },
            }
            for row in result
        ]
    # turn it to a geojson format and have a geojson object for each layer
    geojson_dict = {}
    for key, value in layers.items():
        geojson = {"type": "FeatureCollection", "features": value}
        # add the geojson object to the dictionary with the table name as the key
        geojson_dict[key] = geojson

    return jsonify(geojson_dict)


if __name__ == "__main__":
    app.run(debug=True)
