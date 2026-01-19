import pandas as pd
import numpy as np
import random

# -----------------------------
# CONFIGURATION
# -----------------------------
N_ROWS = 60000
CURRENT_YEAR = 2025
MIN_YEAR = 2010

# Minimum absolute selling price in Lakhs (user requirement)
MIN_SELLING_PRICE_LAKHS = 1.5

# -----------------------------
# CAR MODELS, PRICE & SPECS
# -----------------------------
CAR_SPECS = {
    # --- Maruti ---
    'Maruti Swift': {'price_range': (6.5, 8.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Maruti'},
    'Maruti Baleno': {'price_range': (7.0, 9.5), 'fuel': ['Petrol', 'CNG'], 'brand': 'Maruti'},
    'Maruti Wagon R': {'price_range': (5.5, 7.5), 'fuel': ['Petrol', 'CNG'], 'brand': 'Maruti'},
    'Maruti Dzire': {'price_range': (7.0, 9.0), 'fuel': ['Petrol', 'CNG'], 'brand': 'Maruti'},
    'Maruti Brezza': {'price_range': (9.0, 13.0), 'fuel': ['Petrol', 'CNG'], 'brand': 'Maruti'},
    'Maruti Ertiga': {'price_range': (9.0, 13.5), 'fuel': ['Petrol', 'CNG'], 'brand': 'Maruti'},

    # --- Hyundai ---
    'Hyundai i20': {'price_range': (6.8, 9.5), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Hyundai'},
    'Hyundai Creta': {'price_range': (11.0, 19.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Hyundai'},
    'Hyundai Venue': {'price_range': (8.0, 13.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Hyundai'},
    'Hyundai Verna': {'price_range': (11.0, 17.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Hyundai'},
    'Hyundai Grand i10': {'price_range': (6.0, 8.5), 'fuel': ['Petrol', 'CNG'], 'brand': 'Hyundai'},

    # --- Honda ---
    'Honda Amaze': {'price_range': (8.0, 11.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Honda'},
    'Honda City': {'price_range': (9.5, 14.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Honda'},
    'Honda Jazz': {'price_range': (8.0, 9.5), 'fuel': ['Petrol'], 'brand': 'Honda'},
    'Honda WR-V': {'price_range': (9.0, 11.5), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Honda'},

    # --- Tata ---
    'Tata Tiago': {'price_range': (6.0, 8.0), 'fuel': ['Petrol', 'CNG'], 'brand': 'Tata'},
    'Tata Tigor': {'price_range': (7.0, 9.0), 'fuel': ['Petrol', 'CNG'], 'brand': 'Tata'},
    'Tata Altroz': {'price_range': (7.0, 10.5), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Tata'},
    'Tata Nexon': {'price_range': (10.0, 14.5), 'fuel': ['Petrol', 'Diesel', 'CNG'], 'brand': 'Tata'},
    'Tata Harrier': {'price_range': (16.0, 25.0), 'fuel': ['Diesel'], 'brand': 'Tata'},
    'Tata Safari': {'price_range': (17.0, 28.0), 'fuel': ['Diesel'], 'brand': 'Tata'},

    # --- Mahindra ---
    'Mahindra Scorpio': {'price_range': (12.0, 18.0), 'fuel': ['Diesel'], 'brand': 'Mahindra'},
    'Mahindra XUV300': {'price_range': (9.0, 13.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Mahindra'},
    'Mahindra XUV700': {'price_range': (14.0, 26.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Mahindra'},
    'Mahindra Thar': {'price_range': (14.0, 18.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Mahindra'},
    'Mahindra Bolero': {'price_range': (9.5, 11.5), 'fuel': ['Diesel'], 'brand': 'Mahindra'},

    # --- Toyota ---
    'Toyota Innova': {'price_range': (18.0, 25.0), 'fuel': ['Diesel', 'Petrol'], 'brand': 'Toyota'},
    'Toyota Fortuner': {'price_range': (30.0, 45.0), 'fuel': ['Diesel', 'Petrol'], 'brand': 'Toyota'},
    'Toyota Glanza': {'price_range': (7.0, 10.0), 'fuel': ['Petrol', 'CNG'], 'brand': 'Toyota'},
    'Toyota Urban Cruiser Hyryder': {'price_range': (15.0, 22.0), 'fuel': ['Petrol', 'Hybrid'], 'brand': 'Toyota'},

    # --- Kia ---
    'Kia Seltos': {'price_range': (11.0, 18.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Kia'},
    'Kia Sonet': {'price_range': (8.0, 14.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Kia'},
    'Kia Carens': {'price_range': (12.0, 18.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Kia'},

    # --- Volkswagen & Skoda ---
    'Volkswagen Polo': {'price_range': (7.0, 10.0), 'fuel': ['Petrol'], 'brand': 'Volkswagen'},
    'Volkswagen Virtus': {'price_range': (11.0, 17.0), 'fuel': ['Petrol'], 'brand': 'Volkswagen'},
    'Skoda Kushaq': {'price_range': (11.0, 17.0), 'fuel': ['Petrol'], 'brand': 'Skoda'},
    'Skoda Slavia': {'price_range': (11.0, 17.0), 'fuel': ['Petrol'], 'brand': 'Skoda'},

    # --- Renault & Nissan ---
    'Renault Kwid': {'price_range': (5.0, 7.5), 'fuel': ['Petrol'], 'brand': 'Renault'},
    'Renault Triber': {'price_range': (6.5, 8.5), 'fuel': ['Petrol'], 'brand': 'Renault'},
    'Renault Duster': {'price_range': (10.0, 14.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Renault'},
    'Nissan Magnite': {'price_range': (6.5, 11.0), 'fuel': ['Petrol'], 'brand': 'Nissan'},
    'Nissan Kicks': {'price_range': (10.0, 15.0), 'fuel': ['Petrol'], 'brand': 'Nissan'},

    # --- MG & Jeep ---
    'MG Hector': {'price_range': (14.0, 20.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'MG'},
    'MG Astor': {'price_range': (11.0, 17.0), 'fuel': ['Petrol'], 'brand': 'MG'},
    'Jeep Compass': {'price_range': (18.0, 26.0), 'fuel': ['Petrol', 'Diesel'], 'brand': 'Jeep'},
    'Jeep Meridian': {'price_range': (29.0, 36.0), 'fuel': ['Diesel'], 'brand': 'Jeep'},
}


# -----------------------------
# ADDITIONAL FACTORS
# -----------------------------
CITIES = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']
CONDITIONS = ['Excellent', 'Good', 'Average', 'Poor']

BRAND_REPUTATION = {
    # Common Indian brands
    'Maruti': 1.00,
    'Hyundai': 1.02,
    'Honda': 1.05,
    'Ford': 0.95,
    'Tata': 1.00,
    'Toyota': 1.10,
    'Mahindra': 1.02,
    'Kia': 1.03,
    'Volkswagen': 1.04,
    'Renault': 0.97,
    'MG': 1.00,
    'Jeep': 1.06,
    'Skoda': 1.05,
    'Nissan': 0.96,
}


# -----------------------------
# DATA GENERATION
# -----------------------------
data = []

for _ in range(N_ROWS):
    car_name = random.choice(list(CAR_SPECS.keys()))
    specs = CAR_SPECS[car_name]
    brand = specs['brand']
    year = random.randint(MIN_YEAR, CURRENT_YEAR - 1)
    car_age = CURRENT_YEAR - year

    # Prices
    present_price = round(random.uniform(*specs['price_range']), 2)

    # Random attributes
    fuel_type = random.choice(specs['fuel'])
    seller_type = random.choices(['Dealer', 'Individual'], [0.7, 0.3])[0]
    transmission = random.choices(['Manual', 'Automatic'], [0.7, 0.3])[0]
    owner = random.choices([0, 1, 2], [0.6, 0.3, 0.1])[0]
    city = random.choice(CITIES)
    condition = random.choices(CONDITIONS, [0.3, 0.4, 0.2, 0.1])[0]

    # Mileage, Engine Power & Maintenance
    mileage = round(random.uniform(12, 25), 1)  # km/l
    engine_power = random.choice([1000, 1200, 1500, 1800, 2000, 2500])
    maintenance_cost = round(random.uniform(3000, 15000), 2)
    insurance_age = random.randint(0, 5)
    accidents = random.choices([0, 1, 2], [0.8, 0.15, 0.05])[0]

    # KMs Driven
    avg_kms_per_year = random.randint(10000, 15000)
    kms_driven = int(car_age * avg_kms_per_year + random.randint(-5000, 5000))
    kms_driven = max(5000, kms_driven)

    # -----------------------------
    # SELLING PRICE CALCULATION
    # -----------------------------
    selling_price = present_price

    # Age depreciation
    age_depreciation_rate = random.uniform(0.07, 0.10)
    selling_price *= (1 - age_depreciation_rate) ** car_age

    # Kms depreciation
    kms_depreciation = (kms_driven / 100000) * 0.4
    selling_price *= (1 - kms_depreciation)

    # Owner depreciation
    selling_price *= (1 - 0.08) ** owner

    # Condition factor
    if condition == 'Excellent':
        selling_price *= 1.05
    elif condition == 'Good':
        selling_price *= 1.00
    elif condition == 'Average':
        selling_price *= 0.9
    else:
        selling_price *= 0.75

    # Brand reputation
    selling_price *= BRAND_REPUTATION[brand]

    # Fuel & Transmission adjustment
    if fuel_type == 'Diesel':
        selling_price *= 1.05
    if transmission == 'Automatic':
        selling_price *= 1.03

    # Accident & maintenance penalties
    selling_price *= (1 - 0.05 * accidents)
    selling_price *= (1 - 0.00001 * maintenance_cost)

    # Random noise
    selling_price *= random.uniform(0.95, 1.05)

    # -----------------------------
    # ENFORCE MINIMUM SELLING PRICE
    # -----------------------------
    # Option A (absolute floor): ensure price >= MIN_SELLING_PRICE_LAKHS
    final_min_price = MIN_SELLING_PRICE_LAKHS

    # Option B (optional, uncomment to use): model-proportional floor
    # This ensures expensive models don't drop to an unrealistically tiny fraction.
    # e.g., keep at least 18% of present price or the absolute floor, whichever is larger.
    # model_floor = max(MIN_SELLING_PRICE_LAKHS, round(0.18 * present_price, 2))
    # final_min_price = model_floor

    selling_price = max(final_min_price, round(selling_price, 2))

    # -----------------------------
    # APPEND ROW
    # -----------------------------
    data.append({
        'Brand': brand,
        'Car_Name': car_name,
        'City': city,
        'Year': year,
        'Car_Age': car_age,
        'Condition': condition,
        'Present_Price(Lakhs)': present_price,
        'Selling_Price(Lakhs)': selling_price,
        'Kms_Driven': kms_driven,
        'Fuel_Type': fuel_type,
        'Seller_Type': seller_type,
        'Transmission': transmission,
        'Owner': owner,
        'Mileage(km/l)': mileage,
        'Engine_Power(cc)': engine_power,
        'Maintenance_Cost(₹/yr)': maintenance_cost,
        'Insurance_Age(yrs)': insurance_age,
        'Accidents': accidents
    })

# -----------------------------
# EXPORT TO CSV
# -----------------------------
df = pd.DataFrame(data)
df.to_csv('enhanced_car_dataset.csv', index=False)

print(f"✅ Successfully generated 'enhanced_car_dataset_with_floor.csv' with {len(df)} rows and {df.shape[1]} columns.")