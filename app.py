import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Welcome
#################################################

@app.route("/")
def welcome():
    return (
        f"test:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
      #  f"/api/v1.0/<start>"
      #  f"/api/v1.0/<end>"
    )

# Precipitation
#################################################
@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of prcp data including"""

    # Query for precip

    latest_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_day = list(np.ravel(latest_day))[0]
    latest_day2 = dt.datetime.strptime(latest_day, '%Y-%m-%d')

    year = int(dt.datetime.strftime(latest_day2, '%Y'))
    month = int(dt.datetime.strftime(latest_day2, '%m'))
    day = int(dt.datetime.strftime(latest_day2, '%d'))
    
    year_before = dt.date(year, month, day)-dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_before).order_by(Measurement.date.desc()).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    prcp_data = []
    for row in results:
        prcp_dict = {row.date, row.prcp}
        prcp_data.append(prcp_dict)

    return jsonify(prcp_dict)

if __name__ == '__main__':
    app.run(debug=True)
