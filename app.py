from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail,Message
from flask_caching import Cache
from flask_cors import CORS
from celery_app import make_celery, celery_app
from celery.result import AsyncResult
from dotenv import load_dotenv
import os
from sqlalchemy import text
from datetime import timedelta, datetime, date
from celery import Celery
from celery.schedules import crontab

# Load .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'instance', 'trekking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key-123')

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "localhost"
app.config["CACHE_REDIS_PORT"] = 6379
app.config["CACHE_REDIS_DB"] = 0
app.config["CACHE_DEFAULT_TIMEOUT"] = 60

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] =  587
app.config['MAIL_USE_TLS'] =True
app.config['MAIL_USERNAME'] = "prajjwaldsmnru1@gmail.com"
app.config['MAIL_PASSWORD'] = "muqb hlgo aypo nanf"
app.config['MAIL_DEFAULT_SENDER'] ="prajjwaldsmnru1@gmail.com"

# Initialize extensions
CORS(app, resources={r"/*": {"origins": "*"}})
cache = Cache(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)
celery = make_celery(app)

def clear_cache():
    cache.clear()

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
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    staff = db.relationship('User', backref='treks_assigned')


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="booked") 
    user = db.relationship('User', backref='bookings')
    trek = db.relationship('Trek', backref='bookings')

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
    return jsonify({"token": access_user,"message": "Login successful",'role': user.role
                    ,'status': user.status,"name":user.name}), 200
#admin
@app.route('/adminDashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60) # cashe 1
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
    print("this is the end ")

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
    existing_trk = Trek.query.filter_by(name = data['name'] , location = data['location']).first()
    if existing_trk:
            return jsonify({"message": "Trek already exists"}), 400
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    if start_date <= date.today():
        return jsonify({"message": "Start date must be after today"}), 400
    if end_date <= start_date:
        return jsonify({"message": "End date must be after start date"}), 400
    duration = (end_date - start_date).days    
    trek=Trek(name=data['name'],location=data['location'],
              slots=data['slots'],status=data.get('status', 'open'),difficulty=data.get('difficulty', 'easy'),
              end_date=end_date,start_date=start_date,duration=duration   
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
    if user.role !="admin" :
        print("inside alltrek")
        return jsonify({"message": " You are not admin or staff"}), 403
    trek=Trek.query.all()
    trek_list=[]
    print("outside allTrek")
    for trek in trek:
        trek_list.append({"id":trek.id, "location":trek.location, 
                          "name":trek.name, "slots":trek.slots ,
                          "staff_id": trek.staff_id,"status": trek.status,"difficulty": trek.difficulty,
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
    existing_user = User.query.filter((User.email == data['email']) & (User.name == data['name'])).first()
    #existing_user = User.query.filter_by(email == data['email'], User.name == data['name']).first()
    if existing_user:
        return jsonify({"message": "Staff already exists"}), 400
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
    trek.status=data.get('status',trek.status)
    trek.difficulty=data.get('difficulty',trek.difficulty)
    trek.staff_id=data.get('staff_id',trek.staff_id)
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
    booking=Booking.query.filter_by(trek_id=trek_id)
    for booking in booking:
        db.session.delete(booking)

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
    print("updateUser called")
    admin_id = get_jwt_identity()
    user=User.query.get(admin_id)
    if user.role != 'admin':
        print("Failed to access admin dashboard")
        return jsonify({"message": " You are not admin"}), 403
    data=request.get_json(silent=True) or {}
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    print("Updating user:", user_id, "with data:", data)
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
@app.route('/allBookings',methods=['GET'])
@jwt_required()
def allBookings():
    bookings = Booking.query.all()
    booking_list = []
    for b in bookings:
        user = User.query.get(b.user_id)
        trek = Trek.query.get(b.trek_id)
        booking_list.append({
            "id": b.id,
            "user_name": user.name,
            "trek_name": trek.name,
            "status": b.status,
            "staff_name": trek.staff.name if trek.staff else None
        })
    return jsonify(booking_list), 200

#staff
@app.route('/staffDashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60) # cashe 2
def staffDashboard():
    staff_id = get_jwt_identity()
    staff = User.query.get(staff_id)
    print(staff.name)
    if staff.role != 'staff':
        return jsonify({"message": "You are not staff"}), 403

    treks = Trek.query.filter_by(staff_id=staff.id).all()
    trek_list = []
    for t in treks:
        trek_list.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "slots": t.slots,
            "status": t.status, 
            "registered_count": Booking.query.filter_by(trek_id=t.id).count()
        })
    return jsonify({"trek_list": trek_list , "staff_name": staff.name}), 200

@app.route('/staff/updateTrek/<int:trek_id>', methods=['PUT'])
@jwt_required()
def staffUpdateTrek(trek_id):
    staff_id = get_jwt_identity()
    trek = Trek.query.get(trek_id)
    print("staff_id:", staff_id, "trek.staff_id:", trek.staff_id)
    if trek.staff_id is None:
        print("trek.staff_id is not None")
        return jsonify({"message": "Not authorized"}), 403

    data = request.get_json()
    trek.slots = data.get("slots", trek.slots)
    trek.status = data.get("status", trek.status)
    db.session.commit()
    return jsonify({"message": "Trek updated"}), 200

@app.route('/participants/<int:trek_id>', methods=['GET'])
@jwt_required()
def staffParticipants(trek_id):
    staff_id = get_jwt_identity()
    trek = Trek.query.get(trek_id)
    print("staff_id:", type(staff_id), "trek.staff_id:", trek.staff_id)
    if not trek or int(trek.staff_id) != int(staff_id):
        print("Not authorized: trek.staff_id:", trek.staff_id, "staff_id:", staff_id)
        return jsonify({"message": "Not authorized"}), 403


    participants = []
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    

    for b in bookings:
        user = User.query.get(b.user_id)
        participants.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "status": b.status
        })
    
    return jsonify(participants), 200


#user
@app.route("/user/allTreks", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60) # cashe 3
def all_Trek():
    
    print("allTrek")
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    if user.role !="user" :
        print("inside alltrek")
        return jsonify({"message": " You are not admin or staff"}), 403
    print("outside allTrek")
    trek_list=[]
    trek=Trek.query.all()
    print("Fetched treks:", trek)
    query=request.args.get('q')
    difficulty=request.args.get('difficulty')
    print("query:", query, difficulty)
    # if query or difficulty:                    #fail when any of input is empty ans cass-sencitive
    #     print("Filtering treks based on query and difficulty")
    #     trek = Trek.query.filter(Trek.name.contains(query) | Trek.location.contains(query) |
    #                                Trek.difficulty.contains(difficulty)).all()
    #     print("Filtered treks:", trek)
    
    if query:
        trek = [t for t in trek if query.lower() in t.name.lower() or query.lower() in t.location.lower()]
    if difficulty:
        trek = [t for t in trek if difficulty.lower() in t.difficulty.lower()]
   
    for trek in trek:
        book=Booking.query.filter_by(user_id=user_id,status="booked",trek_id=trek.id).first()
        if book:
            print(book.trek_id)

        else:
            trek_list.append({"id":trek.id, "location":trek.location, 
                                      "name":trek.name, "slots":trek.slots ,
                                      "staff_id": trek.staff_id,"status": trek.status,"difficulty": trek.difficulty,
                    "staff_name": trek.staff.name if trek.staff else None })
    return jsonify(trek_list),200  

@app.route('/user/book/<int:trek_id>', methods=['POST'])
@jwt_required()
def book_trek(trek_id):
    userId = get_jwt_identity()
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    if trek.status != "open" or trek.slots <= 0:
        return jsonify({"message": "Booking not allowed"}), 403

    existing = Booking.query.filter_by(user_id=userId, trek_id=trek_id,status="booked").first()
    if existing:
        return jsonify({"message": "Already booked"}), 400

    new_booking = Booking(user_id=userId, trek_id=trek_id, status="booked")
    trek.slots -= 1
    db.session.add(new_booking)
    db.session.commit()
    print("Booking successful for user:", userId, "on trek:", trek_id)

    return jsonify({"message": "Booking successful"}), 200

@app.route('/user/bookings', methods=['GET'])
@jwt_required()
def user_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    booking_list = []
    print("Fetched bookings for user:", user_id, "Bookings:", bookings)
    for b in bookings:
        trek = Trek.query.get(b.trek_id)
        if b.status=="booked":
            booking_list.append({
                        "id": b.id,
                        "trek_name": trek.name ,
                        "location": trek.location ,
                        "status": b.status,"treakingStatus": trek.status
                    })
        
    return jsonify(booking_list), 200

@app.route('/user/history', methods=['GET'])
@jwt_required()
def user_history():
    user_id= get_jwt_identity()
    user=User.query.get(user_id)
    if user.role!="user":
        return jsonify({"message": "You are not a user"}), 403
    history=Booking.query.filter_by(user_id=user_id).all()
    history_list=[]
    for h in history:
        trek=Trek.query.get(h.trek_id)
        if h.status=="cancel" or trek.status=="completed":
            history_list.append({
                        "id":h.id,
                        "trek_name": trek.name,
                        "location": trek.location,
                        "status": h.status,"treakingStatus": trek.status
            
                    })
        
    print(trek.status)    
    return jsonify(history_list), 200

@app.route('/user/cancel/<int:book_id>', methods=['POST'])
@jwt_required()
def cancel(book_id):
    print("hi",book_id)
    user_id = get_jwt_identity()
    user=User.query.get(user_id)
    if user.role!="user":
        return jsonify({"message":"Invalid Individual"})
    booking = Booking.query.get(book_id)
    trekId=booking.trek_id
    booking.status="cancel"
    trek=Trek.query.get(trekId)
    trek.slots +=1
    db.session.commit()
    return jsonify({"message": "Booking successful"}), 200

@app.route('/user/profile',methods=['GET'])
@jwt_required()
def UserProfile():
    user_id = get_jwt_identity()
    user=User.query.get(user_id)
    if user.role !="user":
        return jsonify ({"message":"Invalid User"})
    return jsonify({"name": user.name, "email": user.email,"password":user.name}), 200

@app.route('/user/profile/edit', methods=['PUT'])
@jwt_required()
def edit_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != "user":
        return jsonify({"message": "Invalid User"}), 403

    data = request.get_json()
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.password = data.get("password", user.password)

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200


# ============ CELERY ENDPOINTS ============

# Endpoint 1: Trigger CSV export
@app.route('/api/tasks/export-history', methods=['POST'])
@jwt_required()
def trigger_csv_export():
    """User can download their trek history as CSV"""
    user_id = get_jwt_identity()
    
    # Check user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Import and queue the task
    from tasks import export_user_trekking_history
    task = export_user_trekking_history.delay(user_id)
    
    return jsonify({
        "message": "Export started",
        "task_id": task.id,
        "status": "processing"
    }), 202


# Endpoint 2: Check export status
@app.route('/api/tasks/export-status/<task_id>', methods=['GET'])
@jwt_required()
def check_export_status(task_id):
    """Check if export is done"""
    # Get task result
    task_result = AsyncResult(task_id, app=celery)
    
    # Return status
    if task_result.state == 'PENDING':
        return jsonify({
            "state": "PENDING",
            "status": "Processing..."
        }), 200
    elif task_result.state == 'SUCCESS':
        return jsonify({
            "state": "SUCCESS",
            "status": "Done!",
            "result": task_result.result
        }), 200
    elif task_result.state == 'FAILURE':
        return jsonify({
            "state": "FAILURE",
            "status": "Failed",
            "error": str(task_result.info)
        }), 200
    else:
        return jsonify({
            "state": task_result.state,
            "status": "Working..."
        }), 200


# Endpoint 3: List user's exports
@app.route('/api/exports', methods=['GET'])
@jwt_required()
def list_exports():
    """Get list of export files for current user"""
    user_id = get_jwt_identity()
    
    # Look for export files
    export_dir = os.path.join(app.root_path, 'exports')
    if not os.path.exists(export_dir):
        return jsonify({"exports": []}), 200
    
    # Find files for this user
    exports = []
    all_files = os.listdir(export_dir)
    
    for filename in all_files:
        if filename.startswith(f'user_{user_id}_'):
            filepath = os.path.join(export_dir, filename)
            file_size = os.path.getsize(filepath)
            exports.append({
                "filename": filename,
                "size": file_size
            })
    
    return jsonify({"exports": exports}), 200


# Endpoint 4: Download export file
@app.route('/api/exports/<filename>', methods=['GET'])
@jwt_required()
def download_export(filename):
    """Download the CSV file"""
    user_id = get_jwt_identity()
    
    # Security check: file must belong to this user
    if not filename.startswith(f'user_{user_id}_'):
        return jsonify({"message": "Not allowed"}), 403
    
    # Get file path
    export_dir = os.path.join(app.root_path, 'exports')
    filepath = os.path.join(export_dir, filename)
    
    # Check file exists
    if not os.path.exists(filepath):
        return jsonify({"message": "File not found"}), 404
    
    # Send file
    return send_file(filepath, as_attachment=True, download_name=filename)


# Endpoint 5: Admin - Manual reminder trigger
@app.route('/api/tasks/send-reminder', methods=['POST'])
@jwt_required()
def trigger_manual_reminder():
    """Admin can manually send reminders"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if admin
    if not user or user.role != 'admin':
        return jsonify({"message": "Only admin can do this"}), 403
    
    # Queue the task
    from tasks import send_daily_reminder
    task = send_daily_reminder.delay()
    
    return jsonify({
        "message": "Reminder task started",
        "task_id": task.id
    }), 202


# Endpoint 6: Admin - Manual report trigger
@app.route('/api/tasks/generate-report', methods=['POST'])
@jwt_required()
def trigger_manual_report():
    """Admin can manually generate report"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if admin
    if not user or user.role != 'admin':
        return jsonify({"message": "Only admin can do this"}), 403
    
    # Queue the task
    from tasks import generate_monthly_report
    task = generate_monthly_report.delay()
    
    return jsonify({
        "message": "Report task started",
        "task_id": task.id
    }), 202


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



