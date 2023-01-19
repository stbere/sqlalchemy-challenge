import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create session engine
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Hawaii Climate Analysis API!</br>"
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/temp/start/<start></br>"
        f"/api/v1.0/temps/start/end</br>"
        f"<p>ATTN: The 'start' and 'end' should be replaced with a date format YYYY-MM-DD.</p>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Creating session from py to DB
    session = Session(engine)
    # Calculate date 1 year ago from most recent date in the DB
    lastyr = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Data query retrieval and precip scores
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= lastyr).all()

    session.close()

    # Precipitation scores and date held in dictionaries
    precipitation_dictionary = {date: pr for date, pr in precipitation}
    # Return dictionary jsonify
    return jsonify(precipitation_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    # All-station query
    station_results = session.query(Station.station).all()

    session.close()
    # listing station results
    stations = list(np.ravel(station_results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def mo_temp():
    # Calculate date 1 year ago from most recent date in the DB
    last_yr = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Tobs query for specific station/timeframe
    tobs_yr = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= last_yr).all()
        
    session.close()

    temps = list(np.ravel(tobs_yr))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/start/<start>")
@app.route("/api/v1.0/temps/<start>/<end>")
def stats(start=None, end=None):
    # min, max & average of tobs
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Starting date in YYY-MM-DD format
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        # Query gathering min, max, average of tobs with starting date and the above
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    # Start/end must be in YYYY-MM-DD format
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")
    # Query gathering min, max, average of tobs with starting date and the above
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()