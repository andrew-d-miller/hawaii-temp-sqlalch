import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Setup Database
engine = create_engine("sqlite://Resources/hawaii.sqlite")

# Refelct existing database into new one
Base = automap_base()

# Reflect tables
Base.prepare(engine, reflect=True)

# Save to table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from python to database
session = Session(engine)

# Flask setup and routes
app = Flask(__name__)

@app.route("/")
def index():
    return (
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2017-08-23<br/>"
    )
# query precipitation data for the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= "2016-08-23").all()

    session.close()

    # Create a dictionary and append to a list of year_prcp
    year_prcp = []
    for precip in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = Measurement.date
        prcp_dict["tobs"] = Measurement.tobs
        year_prcp.append(prcp_dict)

    return jsonify(year_prcp)


# Query all stations
@app.route("/api/v1.0/station")
def station():
    station_results = session.query(Station.station, Station.name).all()

    session.close()

    all_stations = list(np.ravel(station_results))

    all_stations_dict = []
    for stations in station_results:
        station_dict = {}
        station_dict["station"] = Station.station
        station_dict["name"] = Station.name
        all_stations_dict.append(station_dict)

    return jsonify(all_stations_dict)



# Query dates and tobs of the most active station for the last year 
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-23').\
        order_by(Measurement.date.desc()).all()

    session.close()

    active_station_temp = list(np.ravel(tobs_results))

    return jsonify(active_station_temp)

## `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
## Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range

@app.route("/api/v1.0/<date>")
def last_year(date):
    last_year_results = session.query((Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs).\
        filter(Measurement.date) >= date).all()

    session.close()

    temp_dates = list(np.ravel(last_year_results))
    # return jsonify(temp_dates)

    last_year_dict = []
    for yr in last_year_results:
        year_dict = {}
        year_dict["Date"] = yr.Date
        year_dict["Average"] = yr.func.avg(Measurement.tobs)
        year_dict["Minimum"] = yr.func.min(Measurement.tobs)
        year_dict["Maximum"] = yr.func.max(Measurement.tobs)
        last_year_dict.append(year_dict)

    return jsonify(last_year_dict)



if __name__ == '__main__':
    app.run(debug=True)