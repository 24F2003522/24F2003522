from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))  
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    contact = db.Column(db.String(15))
    status = db.Column(db.String(20), default="active") 


class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    duration = db.Column(db.Integer)
    slots = db.Column(db.Integer)
    status = db.Column(db.String(20), default="open") 
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    booking_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default="booked") 

class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    experience = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    status = db.Column(db.String(20), default="active")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)