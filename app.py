import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# database setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)

# table references
Measurement = Base.classes.measurement
Station = Base.classes.station

# session
session = Session(engine)

# flask - weather app
#################################################
app = Flask(__name__)

# variables

latest_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
latest_day = list(np.ravel(latest_day))[0]
latest_day = dt.datetime.strptime(latest_day, '%Y-%m-%d')

year = int(dt.datetime.strftime(latest_day, '%Y'))
month = int(dt.datetime.strftime(latest_day, '%m'))
day = int(dt.datetime.strftime(latest_day, '%d'))

year_before = dt.date(year, month, day)-dt.timedelta(days=365)
year_before = dt.datetime.strftime(year_before, '%Y-%m-%d')
results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_before).order_by(Measurement.date.desc()).all()



# welcome page

@app.route('/')
def aloha():
    return (
        f'testing:<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/tobs<br/>'
      #  f'/api/v1.0/<start>''
      #  f'/api/v1.0/<end>'
    )

# stations
@app.route('/api/v1.0/stations')
def stations():
    all_stations = session.query(Station.name).all()
    all_stations = list(np.ravel(all_stations))
    return jsonify(all_stations)

# Precipitation
@app.route('/api/v1.0/precipitation')
def prcp():
    results = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
        filter(Measurement.date > year_before).\
        order_by(Measurement.date.desc()).all()
    
    prcp_data = []
    
    for row in results:
        prcp_dict = {row.date: row.prcp, "Station": row.station}
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

    """Return a list of prcp data including"""

    # Query for precip

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    
    

if __name__ == '__main__':
    app.run(debug=True)
