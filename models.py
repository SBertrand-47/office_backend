from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Office model
class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), unique=True, nullable=False)  # Unique office name
    users = db.relationship('User', backref='office', lazy=True)  # Link to employees

# OfficeStatus model
class OfficeStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status_message = db.Column(db.String(200), nullable=False)  # Status message for the office
    office_id = db.Column(db.Integer, db.ForeignKey('office.id'), nullable=False)  # Link to the office
    office = db.relationship('Office', backref='status_messages')  # Relationship to Office

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Increase to 200 or higher
    role = db.Column(db.String(50), nullable=False, default="employee")
    office_id = db.Column(db.Integer, db.ForeignKey('office.id'), nullable=False)

