from flask import Flask, jsonify, request, session
from models import db, OfficeStatus, Office, User
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS
from urllib.parse import unquote  # Add this import

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Enable CORS
CORS(app, supports_credentials=True)
# Initialize the database
db.init_app(app)

# Create the database tables manually when the app starts
with app.app_context():
    db.create_all()


# Route to create a new office (room)
@app.route('/office/create', methods=['POST'])
def create_office():
    data = request.json
    name = data.get('name')

    # Check if the office already exists
    existing_office = Office.query.filter_by(name=name).first()
    if existing_office:
        return jsonify({'error': 'Office already exists'}), 400

    # Create a new office
    new_office = Office(name=name)
    db.session.add(new_office)
    db.session.commit()

    return jsonify({'message': 'Office created successfully'}), 201


# Route to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    office_name = data.get('office_name')

    # Check if the office exists
    office = Office.query.filter_by(name=office_name).first()
    if not office:
        return jsonify({'error': 'Office not found'}), 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=hashed_password,
        office_id=office.id  # Link user to the office by its primary key
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# Route to log in a user
# Route to log in a user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Fetch the user by email
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password matches
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Store the user's ID and office ID in the session
    session['user_id'] = user.id
    session['office_id'] = user.office_id  # Store the office ID in the session

    # Fetch the associated office to provide more info if needed
    office = Office.query.get(user.office_id)

    return jsonify({
        'message': 'Logged in successfully',
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'office_name': office.name if office else 'No office assigned'
        }
    }), 200



# Route to update office status (only for logged-in users)
@app.route('/status/update', methods=['POST'])
def update_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    print(data)
    office_id = session['office_id']  # Get the user's office from the session
    status_message = data.get('status_message')

    if not status_message:
        return jsonify({'error': 'Missing status_message'}), 400

    print(status_message)

    # Check if the office status already exists for the given office
    office_status = OfficeStatus.query.filter_by(office_id=office_id).first()

    if office_status:
        # If status exists, update it
        office_status.status_message = status_message
    else:
        # If no status exists, create a new one
        office_status = OfficeStatus(office_id=office_id, status_message=status_message)
        db.session.add(office_status)

    db.session.commit()  # Commit the changes to the database
    return jsonify({'message': 'Status updated successfully'}), 200



# Route to get office status
@app.route('/status/<office_name>', methods=['GET'])
def get_status(office_name):
    # Decode the office name from the URL
    office_name = unquote(office_name).strip()

    # Find the office by its name
    office = Office.query.filter_by(name=office_name).first()
    if not office:
        return jsonify({'error': 'Office not found'}), 404

    # Find the current status of the office
    office_status = OfficeStatus.query.filter_by(office_id=office.id).first()
    if not office_status:
        return jsonify({'error': 'Office status not found'}), 404

    return jsonify({'office_name': office.name, 'status_message': office_status.status_message}), 200


# Route to fetch available offices (offices that are not associated with any user)
@app.route('/offices', methods=['GET'])
def get_available_offices():
    # Fetch offices that do not have any users associated
    available_offices = Office.query.filter(~Office.users.any()).all()  # Use SQLAlchemy to fetch offices without users
    office_list = [{'id': office.id, 'name': office.name} for office in available_offices]
    return jsonify({'offices': office_list}), 200


# Route to get the logged-in user's info
@app.route('/user/info', methods=['GET'])
def get_user_info():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Fetch the user from the session
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Fetch the office the user belongs to
    office = Office.query.get(user.office_id)

    print(office)

    return jsonify({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'office_name': office.name if office else 'No office assigned'
    }), 200



# Route to log out the user
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
