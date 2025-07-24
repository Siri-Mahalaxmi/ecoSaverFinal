import os
import json
import logging
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from models import db, User, Emission

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Database configuration - SQLite for cross-platform compatibility
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///carbon_tracker.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
    # Only use these options for PostgreSQL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        "pool_recycle": 300,
    }

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Emission factors (kg CO2 per unit)
EMISSION_FACTORS = {
    'transportation': {
        'Car': {'Petrol': 0.24, 'Diesel': 0.27, 'CNG': 0.18, 'Electric': 0.05},
        'Bike': {'Petrol': 0.08, 'Electric': 0.02},
        'Bus': {'Diesel': 0.10, 'CNG': 0.08, 'Electric': 0.04},
        'Train': {'Electric': 0.04, 'Diesel': 0.06},
        'Plane': {'Jet Fuel': 0.25},
        'Walking': {'None': 0.0}
    },
    'appliances': {
        'AC': 1.5,  # kWh per hour
        'Fan': 0.05,
        'Fridge': 0.15,
        'Washing Machine': 0.5,
        'Heater': 2.0,
        'TV': 0.1
    },
    'electricity': 0.5,  # kg CO2 per kWh
    'diet': {
        'Chicken': 0.6,  # kg CO2 per 100g
        'Beef': 2.7,
        'Pork': 1.2,
        'Fish': 0.5,
        'Mutton': 2.4,
        'Vegetarian': 0.1
    },
    'gas': 2.98,  # kg CO2 per kg LPG
    'waste': {
        'recycled': 0.1,  # kg CO2 per kg waste
        'not_recycled': 0.5
    },
    'water': 0.0003  # kg CO2 per liter
}

def load_data():
    """Load emissions data from JSON file"""
    try:
        with open('data/emissions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    """Save emissions data to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/emissions.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_eco_facts():
    """Load eco facts from JSON file"""
    try:
        with open('data/eco_facts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default facts if file doesn't exist
        default_facts = [
            "A single tree can absorb 22 kg of CO₂ per year.",
            "Walking or cycling for short trips can reduce your carbon footprint by up to 50%.",
            "LED bulbs use 75% less energy than incandescent bulbs.",
            "Recycling one aluminum can saves enough energy to power a TV for 3 hours.",
            "Eating less meat one day per week can save 1,900 pounds of CO₂ per year.",
            "Taking shorter showers can save up to 150 gallons of water per month.",
            "Unplugging electronics when not in use can reduce energy consumption by 10%.",
            "Using public transport instead of driving can reduce CO₂ emissions by 45%."
        ]
        save_eco_facts(default_facts)
        return default_facts

def save_eco_facts(facts):
    """Save eco facts to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/eco_facts.json', 'w') as f:
        json.dump(facts, f, indent=2)

def calculate_transportation_emissions(transport_data):
    """Calculate CO2 emissions from transportation"""
    total_emissions = 0
    
    for transport in transport_data:
        vehicle = transport.get('vehicle')
        fuel = transport.get('fuel')
        distance = float(transport.get('distance', 0))
        
        if vehicle in EMISSION_FACTORS['transportation']:
            if fuel in EMISSION_FACTORS['transportation'][vehicle]:
                factor = EMISSION_FACTORS['transportation'][vehicle][fuel]
                total_emissions += distance * factor
    
    return total_emissions

def calculate_electricity_emissions(appliances_data):
    """Calculate CO2 emissions from electricity usage"""
    total_kwh = 0
    
    for appliance_data in appliances_data:
        appliance = appliance_data.get('appliance')
        hours = float(appliance_data.get('hours', 0))
        
        if appliance in EMISSION_FACTORS['appliances']:
            kwh_per_hour = EMISSION_FACTORS['appliances'][appliance]
            total_kwh += hours * kwh_per_hour
    
    return total_kwh * EMISSION_FACTORS['electricity']

def calculate_diet_emissions(diet_data):
    """Calculate CO2 emissions from diet"""
    diet_type = diet_data.get('type')
    frequency = float(diet_data.get('frequency', 0))
    
    if diet_type == 'Vegetarian':
        return frequency * EMISSION_FACTORS['diet']['Vegetarian'] * 7  # per week
    
    total_emissions = 0
    meat_types = diet_data.get('meat_types', [])
    
    for meat in meat_types:
        if meat in EMISSION_FACTORS['diet']:
            # Assume 100g serving per meal
            total_emissions += frequency * EMISSION_FACTORS['diet'][meat]
    
    return total_emissions

def generate_suggestions(breakdown):
    """Generate personalized suggestions based on emissions breakdown"""
    suggestions = []
    
    # Find the highest emission category
    max_category = max(breakdown.items(), key=lambda x: x[1])
    high_categories = [cat for cat, value in breakdown.items() if value > 1.0]  # Above 1kg CO2
    
    if 'transportation' in high_categories:
        suggestions.append("🚌 Consider using public transport, carpooling, or cycling for short trips to reduce transportation emissions.")
    
    if 'electricity' in high_categories:
        suggestions.append("💡 Switch to energy-efficient LED bulbs and unplug devices when not in use to lower electricity consumption.")
    
    if 'diet' in high_categories:
        suggestions.append("🥗 Try reducing meat consumption by having one meat-free day per week - it can significantly lower your carbon footprint.")
    
    if 'waste' in high_categories:
        suggestions.append("♻️ Increase your recycling efforts and consider composting organic waste to reduce waste emissions.")
    
    if 'gas' in high_categories:
        suggestions.append("🔥 Use efficient cooking methods and consider batch cooking to reduce LPG consumption.")
    
    if 'water' in high_categories:
        suggestions.append("💧 Take shorter showers and fix any leaks to reduce water usage and associated emissions.")
    
    # Ensure we always have at least 2 suggestions
    if len(suggestions) < 2:
        general_suggestions = [
            "🌱 Plant trees or support reforestation projects to offset your carbon footprint.",
            "🏠 Improve home insulation to reduce heating and cooling energy needs.",
            "🛒 Choose local and seasonal products to reduce transportation emissions."
        ]
        suggestions.extend(general_suggestions[:2-len(suggestions)])
    
    return suggestions[:3]  # Return max 3 suggestions

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            remember_me = bool(request.form.get('remember_me'))
            login_user(user, remember=remember_me)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('root'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists. Please use a different email.', 'error')
        else:
            # Create new user
            try:
                new_user = User()
                new_user.username = username
                new_user.email = email
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                
                # Log in the new user
                login_user(new_user)
                flash('Account created successfully! Welcome to EcoTracker!', 'success')
                return redirect(url_for('root'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while creating your account. Please try again.', 'error')
                logging.error(f"Error creating user: {str(e)}")
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('signin'))

@app.route('/')
def root():
    if current_user.is_authenticated:
        return render_template('index.html', today=date.today())
    else:
        return redirect(url_for('signin'))

@app.route('/dashboard')
@login_required
def index():
    return render_template('index.html', today=date.today())

@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        # Get current user
        user = current_user
        
        # Get form data
        selected_date = request.form.get('date', str(date.today()))
        
        # Transportation data
        transport_data = []
        transport_count = int(request.form.get('transport_count', 0))
        
        for i in range(transport_count):
            vehicle = request.form.get(f'transport_vehicle_{i}')
            fuel = request.form.get(f'transport_fuel_{i}')
            distance = request.form.get(f'transport_distance_{i}')
            
            if vehicle and fuel and distance:
                transport_data.append({
                    'vehicle': vehicle,
                    'fuel': fuel,
                    'distance': distance
                })
        
        # Electricity data
        appliances_data = []
        appliance_count = int(request.form.get('appliance_count', 0))
        
        for i in range(appliance_count):
            appliance = request.form.get(f'appliance_name_{i}')
            hours = request.form.get(f'appliance_hours_{i}')
            
            if appliance and hours:
                appliances_data.append({
                    'appliance': appliance,
                    'hours': hours
                })
        
        # Diet data
        diet_type = request.form.get('diet_type')
        diet_frequency = request.form.get('diet_frequency', 0)
        meat_types = request.form.getlist('meat_types')
        
        diet_data = {
            'type': diet_type,
            'frequency': diet_frequency,
            'meat_types': meat_types
        }
        
        # Other data
        gas_usage = float(request.form.get('gas_usage', 0))
        waste_amount = float(request.form.get('waste_amount', 0))
        recycles = request.form.get('recycles') == 'yes'
        water_usage = float(request.form.get('water_usage', 0))
        
        # Calculate emissions
        transportation_emissions = calculate_transportation_emissions(transport_data)
        electricity_emissions = calculate_electricity_emissions(appliances_data)
        diet_emissions = calculate_diet_emissions(diet_data)
        gas_emissions = gas_usage * EMISSION_FACTORS['gas']
        waste_emissions = waste_amount * (EMISSION_FACTORS['waste']['recycled'] if recycles else EMISSION_FACTORS['waste']['not_recycled'])
        water_emissions = water_usage * EMISSION_FACTORS['water']
        
        # Create breakdown
        breakdown = {
            'transportation': round(transportation_emissions, 2),
            'electricity': round(electricity_emissions, 2),
            'diet': round(diet_emissions, 2),
            'gas': round(gas_emissions, 2),
            'waste': round(waste_emissions, 2),
            'water': round(water_emissions, 2)
        }
        
        total_emissions = sum(breakdown.values())
        
        # Generate suggestions
        suggestions = generate_suggestions(breakdown)
        
        # Get random eco fact
        eco_facts = load_eco_facts()
        import random
        eco_fact = random.choice(eco_facts)
        
        # Save data to database
        from datetime import datetime
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        # Check if entry for this date already exists for this user
        existing_emission = Emission.query.filter_by(
            user_id=user.id, 
            date=selected_date_obj
        ).first()
        
        if existing_emission:
            # Update existing entry
            existing_emission.transport_total = round(transportation_emissions, 2)
            existing_emission.electricity_total = round(electricity_emissions, 2)
            existing_emission.diet_total = round(diet_emissions, 2)
            existing_emission.gas_total = round(gas_emissions, 2)
            existing_emission.waste_total = round(waste_emissions, 2)
            existing_emission.water_total = round(water_emissions, 2)
            existing_emission.total_emissions = round(total_emissions, 2)
            existing_emission.appliance_usage = appliances_data
            existing_emission.diet_type = diet_type
            existing_emission.gas_usage = gas_usage
            existing_emission.waste_amount = waste_amount
            existing_emission.waste_recycled = recycles
            existing_emission.water_usage = water_usage
        else:
            # Create new entry
            new_emission = Emission()
            new_emission.user_id = user.id
            new_emission.date = selected_date_obj
            new_emission.transport_total = round(transportation_emissions, 2)
            new_emission.electricity_total = round(electricity_emissions, 2)
            new_emission.diet_total = round(diet_emissions, 2)
            new_emission.gas_total = round(gas_emissions, 2)
            new_emission.waste_total = round(waste_emissions, 2)
            new_emission.water_total = round(water_emissions, 2)
            new_emission.total_emissions = round(total_emissions, 2)
            new_emission.appliance_usage = appliances_data
            new_emission.diet_type = diet_type
            new_emission.gas_usage = gas_usage
            new_emission.waste_amount = waste_amount
            new_emission.waste_recycled = recycles
            new_emission.water_usage = water_usage
            db.session.add(new_emission)
        
        db.session.commit()
        
        return render_template('result.html', 
                             breakdown=breakdown, 
                             total=round(total_emissions, 2),
                             suggestions=suggestions,
                             eco_fact=eco_fact)
        
    except Exception as e:
        logging.error(f"Error in calculate route: {str(e)}")
        flash(f"An error occurred while calculating emissions: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/history')
@login_required
def history():
    try:
        # Get user-specific emissions data from database
        user_emissions = Emission.query.filter_by(user_id=current_user.id)\
                                     .order_by(Emission.date.desc()).all()
        
        if not user_emissions:
            return render_template('history.html', 
                                 emissions_data=[], 
                                 chart_dates=[], 
                                 chart_totals=[],
                                 total_entries=0,
                                 average_daily=0,
                                 highest_day=0,
                                 lowest_day=0)
        
        # Convert to dictionary format for template compatibility
        emissions_data = [emission.to_dict() for emission in user_emissions]
        
        # Calculate statistics
        total_entries = len(emissions_data)
        total_sum = sum(entry['total'] for entry in emissions_data)
        average_daily = total_sum / total_entries if total_entries > 0 else 0
        highest_day = max(entry['total'] for entry in emissions_data)
        lowest_day = min(entry['total'] for entry in emissions_data)
        
        # Prepare data for charts (last 30 entries)
        chart_data = list(reversed(emissions_data[-30:]))
        dates = [entry['date'] for entry in chart_data]
        totals = [entry['total'] for entry in chart_data]
        
        return render_template('history.html', 
                             emissions_data=emissions_data,
                             chart_dates=dates,
                             chart_totals=totals,
                             total_entries=total_entries,
                             average_daily=round(average_daily, 2),
                             highest_day=round(highest_day, 2),
                             lowest_day=round(lowest_day, 2))
        
    except Exception as e:
        logging.error(f"Error in history route: {str(e)}")
        flash(f"An error occurred while loading history: {str(e)}", 'error')
        return render_template('history.html', 
                             emissions_data=[], 
                             chart_dates=[], 
                             chart_totals=[],
                             total_entries=0,
                             average_daily=0,
                             highest_day=0,
                             lowest_day=0)

@app.route('/api/fuel-types/<vehicle>')
def get_fuel_types(vehicle):
    """API endpoint to get fuel types for a vehicle"""
    try:
        fuel_types = list(EMISSION_FACTORS['transportation'].get(vehicle, {}).keys())
        return jsonify(fuel_types)
    except Exception as e:
        logging.error(f"Error getting fuel types: {str(e)}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
