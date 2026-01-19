import numpy as np
import pandas as pd
import pickle
import datetime as dt
from flask import Flask, request, render_template, redirect, url_for, session, g, flash, jsonify
from flask_mail import Mail, Message
import os
# --- NEW IMPORTS ---
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- Initialize App ---
app = Flask(__name__, template_folder='templates', static_folder='static')
# IMPORTANT: Set a real secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_strong_random_default_key_!@#$') 

# --- NEW: Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # This creates a users.db file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- FLASK-MAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_google_app_password')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'your_email@gmail.com')

mail = Mail(app)

# --- NEW: User Database Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# --- Model Loading & Constants ---
model = None
model_mappings = None
model_columns = None
brand_to_model_map = {}
CURRENT_YEAR = dt.datetime.now().year

try:
    # Load the trained model
    with open("car_model.pkl", 'rb') as f:
        loaded = pickle.load(f)
        if isinstance(loaded, dict) and 'model' in loaded:
            model = loaded['model']
            model_mappings = loaded.get('mappings', {})
            model_columns = loaded.get('columns', [])
            print("--- Model, Mappings, and Columns loaded successfully ---")
        else:
            print("--- WARNING: Old model format loaded. ---")
            
    # Load the dataset to build the brand-to-model map for the frontend
    df_data = pd.read_csv('enhanced_car_dataset.csv')
    brand_to_model_map = df_data.groupby('Brand')['Car_Name'].unique().apply(list).to_dict()
    print(brand_to_model_map)
    print("--- Brand-to-Model map created successfully ---")
    
except FileNotFoundError as e:
    print(f"--- FATAL ERROR: Missing file {e.filename}. Please run generate_data.py and car_price_prediction.py ---")
except Exception as e:
    print(f"--- FATAL ERROR: Could not load model or data. {e} ---")


# --- Reusable Prediction Helper Function (FIXED) ---
def _predict_price(form_data, prefix=''):
    try:
        # This function now expects a dictionary-like object (request.form or request.json)
        year = int(form_data.get(prefix + 'Year'))
        present_price = float(form_data.get(prefix + 'Present_Price(Lakhs)'))
        kms_driven = int(form_data.get(prefix + 'Kms_Driven'))
        owner = int(form_data.get(prefix + 'Owner'))
        
        # --- FIX: These variables are now used ---
        fuel_type = form_data.get(prefix + 'Fuel_Type')
        seller_type = form_data.get(prefix + 'Seller_Type')
        transmission = form_data.get(prefix + 'Transmission')
        car_name = form_data.get(prefix + 'Car_Name')
        city = form_data.get(prefix + 'City')
        condition = form_data.get(prefix + 'Condition')
        # --- End Fix ---

        mileage = float(form_data.get(prefix + 'Mileage(km/l)'))
        engine_power = int(form_data.get(prefix + 'Engine_Power(cc)'))
        maintenance = int(form_data.get(prefix + 'Maintenance_Cost(₹/yr)'))
        insurance = int(form_data.get(prefix + 'Insurance_Age(yrs)'))
        accidents = int(form_data.get(prefix + 'Accidents'))
        
        car_age = CURRENT_YEAR - year

        if model is None or not model_mappings or not model_columns:
            print("Model not loaded or incomplete.")
            return None, None

        # Create a dictionary to hold all feature values
        features = {}
        
        # --- Handle Numeric Features ---
        features['Present_Price(Lakhs)'] = present_price
        features['Kms_Driven'] = kms_driven
        features['Owner'] = owner
        features['Car_Age'] = car_age
        features['Mileage(km/l)'] = mileage
        features['Engine_Power(cc)'] = engine_power
        features['Maintenance_Cost(₹/yr)'] = maintenance
        features['Insurance_Age(yrs)'] = insurance
        features['Accidents'] = accidents

        # --- FIX: Handle All Encoded Features ---
        # This loop now correctly processes all string-based features
        for col_name in ['Car_Name', 'City', 'Condition', 'Fuel_Type', 'Seller_Type', 'Transmission']:
            encoder = model_mappings.get(col_name)
            form_value = form_data.get(prefix + col_name) # Get value from form
            if encoder:
                try:
                    # Use encoder.transform which expects a list
                    features[col_name] = encoder.transform([form_value])[0]
                except ValueError: 
                    # Handle unseen labels (e.g., a new city) by mapping to 0
                    print(f"Warning: Unknown category '{form_value}' for column '{col_name}'. Using 0.")
                    features[col_name] = 0 
            else:
                print(f"Warning: No encoder found for column '{col_name}'.")

        # Create the final feature list in the exact order the model was trained on
        final_features = [features.get(col, 0) for col in model_columns]
        data_array = [np.array(final_features)]

        prediction = model.predict(data_array)
        output = round(max(0, float(prediction[0])), 2) # Cast to float
        
        return output, present_price

    except Exception as e:
        print(f"Error in _predict_price (prefix={prefix}): {e}")
        return None, None

# --- Login & Session Management ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_email'] = user.email
            session['user_name'] = user.name
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            
    return render_template('login.html')

# --- Signup Route (FIXED) ---
@app.route('/signup', methods=['POST'])
def signup():
    if 'user_email' in session:
        return redirect(url_for('home'))

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already exists. Please login.', 'error')
        return redirect(url_for('login'))
        
    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    # --- FIX: Per your request, prompt user to sign in ---
    flash('Account created successfully. Please sign in.', 'success')
    return redirect(url_for('login'))

# --- Logout Route (FIXED) ---
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.before_request
def require_login():
    exempt_routes = ['login', 'signup', 'static']
    if request.endpoint not in exempt_routes and 'user_email' not in session:
        return redirect(url_for('login'))
    
    g.user = session.get('user_name')


# --- Main App Routes ---
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

# --- ** THE FIX for UndefinedError ** ---
@app.route('/predict_page')
def predict_page():
    # This route serves the HTML and MUST pass the variables
    # that index.html expects.
    
    # Define the form options that index.html needs
    form_options = {
        'Year': {'min': 2000, 'max': CURRENT_YEAR},
        'Kms_Driven': {'min': 0},
        'Present_Price(Lakhs)': {'min': 0.1, 'step': 0.01},
        'Owner': {'min': 0, 'max': 5},
        'Mileage(km/l)': {'min': 5, 'max': 40, 'step': 0.1},
        'Engine_Power(cc)': {'min': 600, 'max': 5000, 'step': 1},
        'Maintenance_Cost(₹/yr)': {'min': 0, 'step': 100},
        'Insurance_Age(yrs)': {'min': 0, 'max': 15},
        'Accidents': {'min': 0, 'max': 10}
    }
    
    return render_template('index.html', 
                           brand_map=brand_to_model_map, 
                           form_options=form_options, 
                           current_year=CURRENT_YEAR)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        form_data = request.json # Get data from fetch
        prediction, showroom_price = _predict_price(form_data) # Use helper
        
        if prediction is not None:
            return jsonify({
                'success': True,
                'predicted_price': prediction,
                'showroom_price': showroom_price,
                'details': form_data # Send details back
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid data received by server.'}), 400

    except Exception as e:
        print(f"API Prediction Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    price_a, price_b = None, None
    form_data = {}
    
    if request.method == 'POST':
        form_data = request.form
        # Note: The compare.html form needs to be updated to match the new feature names
        price_a, _ = _predict_price(form_data, 'a_')
        price_b, _ = _predict_price(form_data, 'b_')
        
        if price_a is None or price_b is None:
            flash('Error: Could not make comparison. Please check all inputs.', 'error')
        else:
            flash('Comparison successful!', 'success')
            
    return render_template('compare.html',
                           current_year=CURRENT_YEAR,
                           form_data=form_data,
                           price_a=price_a, 
                           price_b=price_b)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            subject = request.form['subject']
            message_body = request.form['message']
            
            admin_subject = f"New Contact Form: {subject} (from {name})"
            admin_body = f"Message from: {name} ({email})\n\n{message_body}"
            msg_admin = Message(admin_subject, sender=app.config['MAIL_USERNAME'], recipients=[ADMIN_EMAIL])
            msg_admin.body = admin_body
            mail.send(msg_admin)
            
            user_subject = "We've received your message!"
            user_body = f"Hello {name},\n\nThank you for contacting us. We will get back to you shortly."
            msg_user = Message(user_subject, sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg_user.body = user_body
            mail.send(msg_user)

            flash('Message sent successfully! Please check your email for a confirmation.', 'success')
        
        except Exception as e:
            print(f"ERROR SENDING EMAIL: {e}")
            flash('Error sending message. Please check server logs and configuration.', 'error')
        
        return redirect(url_for('contact'))

    return render_template('contact.html')


if __name__ == '__main__':
    # Create the database tables before running the app
    with app.app_context():
        db.create_all()
    print("Starting Flask app... Visit http://127.0.0.1:5000/login")
    app.run(debug=True)