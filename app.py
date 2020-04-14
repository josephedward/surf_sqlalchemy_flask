import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

m_table_ref = Base.classes.measurement
s_table_ref = Base.classes.station

app = Flask(__name__)


@app.route("/")
def home():
    print("List all available api routes")
    return (f"Available Routes:<br/><br/>"
        # f"Precipitation Data for Aug 2016 - Aug 2017: <br/>"
        f'All Precipitation Data: <br/><br/>'
        f"/precipitation_2016_2017<br/><br/>"
        f"List of Stations: <br/><br/>"
        f"/station_list<br/><br/>"
        f"List of Temperatures at Waihee for Aug 2016 - Aug 2017: <br/><br/>"
        f"/temperatures_waihee<br/><br/>"
        f"Min, Max, and Avg Temperatures from date yyyy-mm-dd:<br/><br/>"
        f"/temp_dates/'your_date'<br/><br/>"
        f"Min, Max, and Avg Temperatures from start to end date: yyyy-mm-dd/yyyy-mm-dd<br/><br/>"
        f"/temp_dates/'start_date'/'end_date'<br/><br/>"
    )

@app.route("/precipitation_2016_2017")
def precipitation():
    session = Session(engine)
    last_yr_prcp_df = pd.DataFrame(session.query(m_table_ref.date, m_table_ref.prcp).\
    # filter(m_table_ref.date <= '2017-08-23').\
    #     filter(m_table_ref.date > '2016-08-23').\
        order_by(m_table_ref.date).all())
    return last_yr_prcp_df.to_json()
    
@app.route("/station_list")
def stations():
    session = Session(engine)
    station_list_df = pd.DataFrame(session.query(s_table_ref.station,s_table_ref.name ).\
    group_by(s_table_ref.station).\
    order_by(s_table_ref.station).all())
    station_list = list(station_list_df['name'])
    return jsonify(station_list)

@app.route("/temperatures_waihee")
def temperatures():    
    session = Session(engine)
    waihee_temp_df = pd.DataFrame(session.query(m_table_ref.date, m_table_ref.tobs).\
    filter(m_table_ref.station == 'USC00519281').\
    filter(m_table_ref.date >= '2017-01-01').\
    filter(m_table_ref.date <= '2017-12-31').\
    group_by(m_table_ref.date).all())
    return waihee_temp_df.to_json()

@app.route("/temp_dates/<your_date>")
def start_date(your_date):
    session = Session(engine)
    temp_df = pd.DataFrame(session.query(m_table_ref.date, m_table_ref.tobs).\
    filter(m_table_ref.date >= your_date).all())
    temp_funcs_df=pd.DataFrame({'Min: ':temp_df['tobs'].min(), 'Max: ':temp_df['tobs'].max(), 'Avg: ':temp_df['tobs'].mean()}, index=["Temp: "])
    return temp_funcs_df.to_json()


@app.route("/temp_dates/<start_date>/<end_date>")
def start_end_date(start_date, end_date):
    session = Session(engine)
    temp_df = pd.DataFrame(session.query(m_table_ref.date, m_table_ref.tobs).\
    filter(m_table_ref.date >= start_date).\
    filter(m_table_ref.date <= end_date).all())
    temp_funcs_df=pd.DataFrame({'Min: ':temp_df['tobs'].min(), 'Max: ':temp_df['tobs'].max(), 'Avg: ':temp_df['tobs'].mean()}, index=["Temp: "])
    return temp_funcs_df.to_json()


if __name__ == '__main__':
    app.run(debug=True)