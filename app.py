import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


# DATABASE SETUP
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# SAVE TABLE REFERENCES
Measurement = Base.classes.measurement
Station = Base.classes.station

# FLASK SETUP
app = Flask(__name__)


# FLASK ROUTES

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;` and `/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        f"dates must be written as YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Measurement table
    last_date_string = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()[0]

    last_date = dt.datetime.strptime(last_date_string,"%Y-%m-%d")
    
    one_year_back = last_date - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > one_year_back)

    session.close()

    # Convert results into dictionary
    prcp_dict = {}

    for (date, precipitation) in results:
        if date not in prcp_dict:
            prcp_dict[date] = [precipitation]
        else:
            prcp_dict[date].append(precipitation)

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the database
    results = session.query(Station.id, Station.station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    results_list = list(np.ravel(results))

    return jsonify(results_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the database
    last_date_string = session.query(Measurement.date).\
        filter(Measurement.station == Station.station).\
        filter(Station.id == 9).\
        order_by(Measurement.date.desc()).first()[0]

    last_date = dt.datetime.strptime(last_date_string,"%Y-%m-%d")

    one_year_back = last_date - dt.timedelta(days=365)


    temp_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == Station.station).\
        filter(Station.id == 9).\
        filter(Measurement.date > one_year_back)

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    tobs_dict = {}

    for (date, temp) in temp_results:
        if date not in tobs_dict:
            tobs_dict[date] = temp

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the database

    low_temp_result = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date > start).all()

    high_temp_result = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date > start).all()

    avg_temp_result = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date > start).all()

    low_temp = np.ravel(low_temp_result)
    high_temp = np.ravel(high_temp_result)
    avg_temp = np.ravel(avg_temp_result)

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    results_dict = {
        "TMIN": low_temp[0],
        "TMAX": high_temp[0],
        "TAVG": avg_temp[0]
    }

    return jsonify(results_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the database

    low_temp_result = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).all()

    high_temp_result = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).all()

    avg_temp_result = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).all()

    low_temp = np.ravel(low_temp_result)
    high_temp = np.ravel(high_temp_result)
    avg_temp = np.ravel(avg_temp_result)

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    results_dict = {
        "TMIN": low_temp[0],
        "TMAX": high_temp[0],
        "TAVG": avg_temp[0]
    }

    return jsonify(results_dict)

if __name__ == '__main__':
    app.run(debug=True)
