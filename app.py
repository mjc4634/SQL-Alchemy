import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify


#####################
# Database Setup
#####################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# create reference to a table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create our session(link) from python to the DB
session = Session(engine)


####################
# Flask Setup
####################    

app = Flask(__name__)



# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f" /api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
    



@app.route("/api/v1.0/precipitation")
def precipitation():
    
    results = session.query(Measurement.date, Measurement.prcp).all()

    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    last_tob = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = str(last_tob[0]) 
    year = int(last_date.split("-")[0])
    month = int(last_date.split("-")[1])
    day = int(last_date.split("-")[2])
         
    last_year = dt.date(year, month, day) - dt.timedelta(days=365)
    temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > last_year).order_by(Measurement.date).all()
    


    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    temp_min = ("Min Temperature: ", temp_data[0][0])
    temp_avg = ("Avg Temperature: ", temp_data[0][1])
    temp_max = ("Max Temperature: ", temp_data[0][2])

    result = [temp_min, temp_avg, temp_max]
    
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def temp_trip(start, end):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temp_data = temp_data[0]
    temp_min = ("Min Temperature: ", temp_data[0])
    temp_avg = ("Avg Temperature: ", temp_data[1])
    temp_max = ("Max Temperature: ", temp_data[2])

    result = [temp_min, temp_avg, temp_max]
    
    return jsonify(result)
    
if __name__ == "__main__":
    app.run(debug=True)