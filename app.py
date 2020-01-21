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
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False})
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

# welcome page

@app.route('/')
def aloha():
    return (
        f'Aloha! Welcome to the Hawaii Climate App.<br/>'
        f'---------------------------------------------'
        f'Get the full list of stations:</br>'
        f'/api/v1.0/stations<br/>'
        f'</br>'
        f'Get the rainfall data:</br>'
        f'/api/v1.0/precipitation</br>'
        f'</br>'
        f'Get the temperature data:</br>'
        f'/api/v1.0/tobs</br>'
        f'</br>'
        f'Search dates by inputting a start date & end date:</br>'
        f'--API Example 1: /api/v1.0/searchdates/YYY-MM-DD -- gives the high, low, avg for given date & days after</br>'
        f'--API Example 2: /api/v1.0/searchdates/YYY-MM-YY/YYYY-MM-DD -- gives the high, low, avg for dates in between first and second date inputs'
    )

# stations
@app.route('/api/v1.0/stations')
def stations():
    all_stations = session.query(Station.name).all()
    all_stations = list(np.ravel(all_stations))
    return jsonify(all_stations)

# precipitation
@app.route('/api/v1.0/precipitation')
def prcp():
    prcp_results = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
        filter(Measurement.date > year_before).\
        order_by(Measurement.date.desc()).all()
    
    prcp_data = []
    
    for r in prcp_results:
        prcp_dict = {r.date: r.prcp, 'Station': r.station}
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

# tobs
@app.route('/api/v1.0/tobs')
def tobs():
    tobs_results =  session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date > year_before).\
        order_by(Measurement.date.desc()).all()
    
    tobs_data = []
    
    for t_r in tobs_results:
        tobs_dict = {t_r.date: t_r.tobs, 'Station': t_r.station}
        tobs_data.append(tobs_dict)
    
    return jsonify(tobs_data)

# ---------search dates-start
@app.route('/api/v1.0/searchdates/<start_date>')
def start_search(start_date):
    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    start_results =  (session.query(*sel).\
        filter(func.strftime('%Y-%m-%d', Measurement.date) >= start_date).\
        group_by(Measurement.date).all())
    
    s_dates = []          

    for s_r in start_results:
        s_date_dict = {}
        s_date_dict['date'] = s_r[0]
        s_date_dict['low temp'] = s_r[1]
        s_date_dict['avg temp'] = s_r[2]
        s_date_dict['high temp'] = s_r[3]
        s_dates.append(s_date_dict)

    return jsonify(s_dates)

# ---------search dates-end
@app.route('/api/v1.0/datesearch/<start_date>/<end_date>')
def end_search(start_date, end_date):    
    sel2 = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_end_results =  (session.query(*sel2).\
        filter(func.strftime('%Y-%m-%d', Measurement.date) >= start_date).\
        filter(func.strftime('%Y-%m-%d', Measurement.date) <= end_date).\
        group_by(Measurement.date.desc()).all()
    
    s_e_r_dates = []
    for s_e_r in start_end_results:
        ser_date_dict = {}
        ser_date_dict['date'] = s_e_r[0]
        ser_date_dict['low temp'] = s_e_r[1]
        ser_date_dict['avg temp'] = s_e_r[2]
        ser_date_dict['high temp'] = s_e_r[3]
        s_e_r_dates.append(ser_date_dict)
    
    return jsonify(s_e_r_dates)

session.close()

if __name__ == '__main__':
    app.run(debug=True)