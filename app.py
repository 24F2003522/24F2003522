from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'instance', 'trekking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this-in-production-123456'
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
    staff = db.relationship('User', backref='treks_assigned')


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
    data = request.get_json(silent=True) or {} # return an empty dict if no JSON is provided , silent=True give none for badrequest
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

    access_user = create_access_token(identity=str(user.id))
    print("user logged in")
    return jsonify({"token": access_user,"message": "Login successful",'role': user.role,'status': user.status}), 200

@app.route('/adminDashboard', methods=['GET'])
@jwt_required()
def adminDashboard():
    # .get() always searches by primary key
    user_id = get_jwt_identity()
    user=User.query.get(user_id)
    if user.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403
    print("Sending data")
    totalUsers = User.query.count()
    totalTreks = Trek.query.count()
    totalBookings = Booking.query.count()
    totalStaff = User.query.filter_by(role="staff").count()

    return jsonify({
        "users": totalUsers,"treks": totalTreks,"bookings": totalBookings,"staff": totalStaff
    })


@app.route('/creatTrek',methods=['POST'])
@jwt_required()
def creatTrek():
    user_id = get_jwt_identity()
    user=User.query.get(user_id)
    if user.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403
    data=request.get_json(silent=True) or {}
    trek=Trek(name=data['name'],location=data['location'],
              slots=data['slots'],
              )
    db.session.add(trek)
    db.session.commit()
    return jsonify({"message":"Trek created successfully"}),201

@app.route("/allTreks", methods=["GET"])
@jwt_required()
def allTrek():
    print("allTrek")
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    if user.role !="admin":
        return jsonify({"message": " You are not admin"}), 403
    trek=Trek.query.all()
    trek_list=[]
    for trek in trek:
        trek_list.append({"id":trek.id, "location":trek.location, 
                          "name":trek.name, "slots":trek.slots ,"staff_id": trek.staff_id,
            "staff_name": trek.staff.name if trek.staff else None })
    return jsonify(trek_list),200    

@app.route('/addStaff',methods=['POST'])
@jwt_required()
def addStaff():
    user_id = get_jwt_identity()
    user=User.query.get(user_id)
    if user.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403
    data=request.get_json(silent=True) or {}
    staff=User(name=data['name'],email=data['email'],password=data['password'],role='staff')
    db.session.add(staff)
    db.session.commit()
    return jsonify({"message":"Staff added successfully"}),201

@app.route('/deactivateUser/<int:user_id>',methods=['PUT'])
@jwt_required()
def deactivateUser(user_id):
    admin_id = get_jwt_identity()
    admin=User.query.get(admin_id)
    if admin.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403    

    user = User.query.get(user_id)
    user.status = "inactive"
    db.session.commit()
    return jsonify({"message": "User deactivated successfully"}), 200

@app.route('/updateTrek/<int:trek_id>',methods=['PUT'])
@jwt_required()
def updateTrek(trek_id):
    user_id = get_jwt_identity()
    user=User.query.get(user_id)
    if user.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message":"You are not admin"}),403
    data=request.get_json(silent=True) or {}
    trek=Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message":"Trek not found"}),404
    # if 'name' in data:
    #     trek.name=data['name']
    # if 'location' in data:
    #     trek.location=data['location']
    trek.name=data.get('name',trek.name) #If name does not exist in data obj., use trek.name (the current value in the database).
    trek.location=data.get('location',trek.location)
    trek.slots=data.get('slots',trek.slots)
    db.session.commit()
    return jsonify({"message":"Trek updated successfully"}),200

@app.route('/deleteTrek/<int:trek_id>',methods=['DELETE'])
@jwt_required()
def delete(trek_id):
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    if user.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message":"You are not admin"}),403
    trek=Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message":"Trek not found"}),404
    db.session.delete(trek)
    db.session.commit()
    return jsonify({"message":"Trek deleted successfully"}),200


@app.route("/allUsers", methods=["GET"])
@jwt_required()
def allUsers():
    print("allUsers")
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    if user.role !="admin":
        return jsonify({"message": " You are not admin"}), 403
    users=User.query.filter(User.role != "admin").all()
    users_list=[]
    for user in users:
        users_list.append({"id":user.id, "name":user.name, "email":user.email, "status":user.status})
    return jsonify(users_list),200  



@app.route('/updateUser/<int:user_id>',methods=['PUT'])
@jwt_required()
def updateUser(user_id):
    user_id = get_jwt_identity()
    user=User.query.get(user_id)
    if user.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403
    data=request.get_json(silent=True) or {}
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.status = data.get('status', user.status)
    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

@app.route('/deleteUser/<int:user_id>',methods=['DELETE'])
@jwt_required()
def deleteUser(user_id):
    admin_id = get_jwt_identity()
    admin=User.query.get(admin_id)
    if admin.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/search', methods=['GET'])
@jwt_required()
def search():
    admin_id = get_jwt_identity()
    admin=User.query.get(admin_id)
    if admin.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403

    query = request.args.get('q')
    if not query:
        return jsonify({"message": "Search query is required"}), 400

    treks = Trek.query.filter(Trek.name.contains(query) | Trek.location.contains(query)).all()
    users = User.query.filter(User.name.contains(query) | User.email.contains(query)).all()

    search_results = {
        "treks": [{"id": trek.id, "name": trek.name, "location": trek.location, "slots": trek.slots} for trek in treks],
        "users": [{"id": user.id, "name": user.name, "email": user.email, "status": user.status} for user in users],
        
    }

    return jsonify(search_results), 200
@app.route('/assignStaff/<int:trek_id>/<int:staff_id>', methods=['PUT'])
@jwt_required()
def assignStaff(trek_id, staff_id):
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    if admin.role != 'admin':
        return jsonify({"message": "You are not admin"}), 403

    trek = Trek.query.get(trek_id)
    staff = User.query.get(staff_id)
    if not trek or not staff or staff.role != "staff":
        return jsonify({"message": "Invalid trek or staff"}), 404

    trek.staff_id = staff.id
    db.session.commit()
    return jsonify({"message": f"Staff {staff.name} assigned to trek {trek.name}"}), 200


@app.route('/allStaff', methods=['GET'])
@jwt_required()
def allStaff():
    staff = User.query.filter_by(role="staff").all()
    staff_list = [{"id": s.id, "name": s.name, "email": s.email, "contact": s.contact} for s in staff]
    return jsonify(staff_list), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("tables created.")
        ext_admin = User.query.filter_by(email='admin@gmail.com').first()
        if not ext_admin:
            admin_user = User(name="admin", email="admin@gmail.com", password="admin", role="admin")
            db.session.add(admin_user)
            db.session.commit()
            
    app.run(debug=True)



