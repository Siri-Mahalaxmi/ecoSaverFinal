from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to emissions
    emissions = db.relationship('Emission', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Emission(db.Model):
    __tablename__ = 'emissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Transportation
    transport_total = db.Column(db.Float, default=0.0)
    transport_vehicle = db.Column(db.String(50))
    transport_fuel = db.Column(db.String(50))
    transport_distance = db.Column(db.Float, default=0.0)
    
    # Electricity
    electricity_total = db.Column(db.Float, default=0.0)
    appliance_usage = db.Column(db.JSON)  # Store appliance data as JSON
    
    # Diet
    diet_total = db.Column(db.Float, default=0.0)
    diet_type = db.Column(db.String(50))
    
    # Gas
    gas_total = db.Column(db.Float, default=0.0)
    gas_usage = db.Column(db.Float, default=0.0)
    
    # Waste
    waste_total = db.Column(db.Float, default=0.0)
    waste_amount = db.Column(db.Float, default=0.0)
    waste_recycled = db.Column(db.Boolean, default=False)
    
    # Water
    water_total = db.Column(db.Float, default=0.0)
    water_usage = db.Column(db.Float, default=0.0)
    
    # Totals
    total_emissions = db.Column(db.Float, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert emission record to dictionary for compatibility with existing code"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'user_id': self.user_id,
            'transportation': self.transport_total,
            'electricity': self.electricity_total,
            'diet': self.diet_total,
            'gas': self.gas_total,
            'waste': self.waste_total,
            'water': self.water_total,
            'total': self.total_emissions,
            'breakdown': {
                'Transportation': self.transport_total,
                'Electricity': self.electricity_total,
                'Diet': self.diet_total,
                'Gas': self.gas_total,
                'Waste': self.waste_total,
                'Water': self.water_total
            },
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Emission {self.date} - {self.total_emissions}kg CO2>'