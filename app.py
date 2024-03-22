from flask import Flask, render_template, jsonify, request, render_template_string
import random
from mqtt_functions import *
from flask_sqlalchemy import SQLAlchemy
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from threading import Thread
import time
from sqlalchemy import func, and_, cast, Numeric




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensordata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TemperatureData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class HumidityData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MovementData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([("ecar/robot/value/temp", 0), ("ecar/robot/value/hum", 0), ("ecar/robot/value/mouv", 0)])

def on_message(client, userdata, msg):
    print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")
    with app.app_context():
        if msg.topic == "ecar/robot/value/temp":
            data = TemperatureData(value=msg.payload.decode())
            db.session.add(data)
        elif msg.topic == "ecar/robot/value/hum":
            data = HumidityData(value=msg.payload.decode())
            db.session.add(data)
        elif msg.topic == "ecar/robot/value/mouv":
            data = MovementData(value=msg.payload.decode())
            db.session.add(data)
        db.session.commit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect("test.mosquitto.org", 1883, 60)
except Exception as e:
    print(f"Could not connect to the broker: {e}")
    exit(1)

client.loop_start()

# website part
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/car_control', methods=['GET', 'POST'])
def page1():
    message = ""
    if request.method == 'POST':
        if 'button_forward' in request.form:
            message = move_forward()
        elif 'button_backward' in request.form:
            message = move_backward()
        elif 'button_left' in request.form:
            message = move_left()
        elif 'button_right' in request.form:
            message = move_right()
        elif 'button_stop' in request.form:
            message = move_stop()
    return render_template('carcont.html', message=message)


@app.route('/sensor_info', methods=['GET'])
def page2():
   # Existing queries for the latest readings
    temp = TemperatureData.query.order_by(TemperatureData.id.desc()).first()
    hum = HumidityData.query.order_by(HumidityData.id.desc()).first()
    move = MovementData.query.order_by(MovementData.id.desc()).first()
    
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculating averages for the last hour
    avg_temp_last_hour = db.session.query(func.avg(TemperatureData.value))\
        .filter(TemperatureData.timestamp >= one_hour_ago).scalar()
    avg_hum_last_hour = db.session.query(func.avg(HumidityData.value))\
        .filter(HumidityData.timestamp >= one_hour_ago).scalar()

    # Calculating min and max for the day
    min_max_temp_today = db.session.query(
        func.min(TemperatureData.value),
        func.max(TemperatureData.value)
    ).filter(TemperatureData.timestamp >= today_start).first()

    min_max_hum_today = db.session.query(
        func.min(HumidityData.value),
        func.max(HumidityData.value)
    ).filter(HumidityData.timestamp >= today_start).first()

    if move:
        move_time = move.timestamp.strftime('%H:%M')
    else:
        move_time = 'N/A'

    return render_template('info.html', temp=temp, hum=hum, move_time=move_time, 
                           avg_temp_last_hour=avg_temp_last_hour, avg_hum_last_hour=avg_hum_last_hour,
                           min_temp_today=min_max_temp_today[0], max_temp_today=min_max_temp_today[1],
                           min_hum_today=min_max_hum_today[0], max_hum_today=min_max_hum_today[1])


@app.route('/generate-number', methods=['POST'])
def generate_number():
    number = random.randint(1, 100)  # Generates a random number between 1 and 100
    return jsonify(number=number)


if __name__ == '__main__':

    app.run(debug=True)
    
