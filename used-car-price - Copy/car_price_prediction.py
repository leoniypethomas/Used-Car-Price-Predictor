import pandas as pd
import numpy as np
import pickle
import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

def train_model():
    """
    Loads data, trains an XGBoost regression model, evaluates it, and saves it.
    """

    # --- 1. Load Dataset ---
    try:
        df = pd.read_csv("enhanced_car_dataset.csv")
        print("✅ Successfully loaded 'enhanced_car_dataset.csv'")
    except FileNotFoundError:
        print("❌ ERROR: 'enhanced_car_dataset.csv' not found. Please generate it first.")
        return
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    # --- 2. Feature Engineering ---
    print("\n🔧 Feature engineering in progress...")
    
    # --- UPDATED: We DROP 'Brand' because 'Car_Name' is more specific ---
    if 'Brand' in df.columns:
        df.drop('Brand', axis=1, inplace=True)
    
    # We will drop 'Year' as 'Car_Age' is the engineered feature
    if 'Year' in df.columns:
        df.drop('Year', axis=1, inplace=True)

    # --- 3. Encoding categorical variables ---
    print("🔤 Encoding categorical features...")
    
    # --- UPDATED: 'Car_Name' is now a feature, 'Brand' is removed ---
    categorical_cols = [
        'Car_Name', 'City', 'Condition', 'Fuel_Type', 
        'Seller_Type', 'Transmission'
    ]
    
    numerical_cols = [col for col in df.columns if col not in categorical_cols + ['Selling_Price(Lakhs)']]
    
    mappings = {} # Dictionary to store our encoders
    
    for col in categorical_cols:
        if col in df.columns:
            encoder = LabelEncoder()
            df[col] = encoder.fit_transform(df[col])
            mappings[col] = encoder # Save the fitted encoder
            print(f"   - Encoded '{col}'")
        else:
            print(f"   - WARNING: Column '{col}' not found in dataset.")
            
    # --- 4. Define Features (X) and Target (y) ---
    print("\n🎯 Defining features (X) and target (y)...")
    feature_cols = numerical_cols + categorical_cols
    
    missing_in_df = [col for col in feature_cols if col not in df.columns]
    if missing_in_df:
        print(f"❌ ERROR: The following expected columns are missing: {missing_in_df}")
        return
        
    X = df[feature_cols]
    y = df['Selling_Price(Lakhs)']
    
    model_columns = X.columns.tolist()
    print(f"   - Model will be trained on {len(model_columns)} features.")

    # --- 5. Train-Test Split ---
    print("🔪 Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- 6. Model Training ---
    print("🚀 Training XGBoost Regressor model...")
    model = XGBRegressor(
        n_estimators=1000, 
        learning_rate=0.05, 
        max_depth=5, 
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=50
    )
    
    model.fit(X_train, y_train, 
              eval_set=[(X_test, y_test)], 
              verbose=False)
    print("   - Model training complete.")

    # --- 7. Model Evaluation ---
    print("\n📊 Evaluating model performance...")
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print(f"🔹 R² Score: {r2:.4f}")

    # --- 8. Save Model + Metadata ---
    model_data = {
        'model': model,
        'mappings': mappings, # The saved encoders
        'columns': model_columns # The exact feature order
    }

    with open('car_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)

    print("\n💾 Model and encoders saved to 'car_model.pkl'")
    print("---------------------------------------------")

if __name__ == "__main__":
    train_model()