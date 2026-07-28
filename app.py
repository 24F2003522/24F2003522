import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'instance', 'trekking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'my_secret_key'# yo to give unique signature or key
db = SQLAlchemy(app)
JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20),default='user')  
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
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    booking_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default="booked") 

class StaffProfile(db.Model):
    name = db.Column(db.String(100))
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact = db.Column(db.String(15))
    experience = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    status = db.Column(db.String(20), default="active")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Bro!"}), 200
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {} # return an empty dict if no JSON is provided
    # request.json 

    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Name, email, and password are required"}), 400

    existing_user = User.query.filter((User.email == data['email']) & (User.name == data['name'])).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    new_user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'user')
    )
    db.session.add(new_user)
    db.session.commit()
    print("new user added")
    return jsonify({"message": "You have registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    access_user = create_access_token(identity=user.id) #This token belongs to the user with this id(uesr)
    return jsonify({"access_token": access_user,"message": "Login successful",'role': user.role}), 200




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("tables created.")
        ext_admin = User.query.filter_by(name="admin").first()
        if not ext_admin:
            print("indie if block")
            admin_new = User(name="admin", email="admin@gmail.com", password="admin", role="admin")
            db.session.add(admin_new)
            db.session.commit()
    app.run(debug=True)



