import os
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

def load_raw_data(filepath):
    """Loads the raw dataset from CSV."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw dataset not found at {filepath}. Please run fetch_data.py first.")
    df = pd.read_csv(filepath)
    print(f"[Step 1] Raw dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df

def handle_missing_values(df, numeric_features, target):
    """Imputes missing values in numerical columns using the median."""
    print("\n[Step 2] Handling missing values...")
    # Check initial null values
    print("Initial nulls:\n", df[numeric_features + [target]].isnull().sum())
    
    # Impute numeric features
    imputer = SimpleImputer(strategy='median')
    df[numeric_features] = imputer.fit_transform(df[numeric_features])
    
    # Drop rows where target is missing
    df = df.dropna(subset=[target])
    
    print("Cleaned nulls:\n", df[numeric_features + [target]].isnull().sum())
    print(f"Dataset size after null imputation: {df.shape[0]} rows.")
    return df

def remove_outliers_iqr(df, features):
    """Detects and removes outliers using the Interquartile Range (IQR) method."""
    print("\n[Step 3] Detecting and removing outliers (IQR method)...")
    initial_rows = df.shape[0]
    
    for col in features:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Filter dataframe
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
    removed_rows = initial_rows - df.shape[0]
    print(f"Removed {removed_rows} outliers. Remaining rows: {df.shape[0]}.")
    return df

def perform_feature_engineering(df):
    """Creates engineered features from raw macronutrients."""
    print("\n[Step 4] Performing Feature Engineering...")
    # 1. Total Macronutrient Sum (grams per 100g)
    df["Total_Macros_g"] = df["Carbohydrates_g"] + df["Protein_g"] + df["Fat_g"]
    
    # 2. Carbs-to-Protein Ratio (handling division by zero with small epsilon)
    df["Carbs_Protein_Ratio"] = df["Carbohydrates_g"] / (df["Protein_g"] + 1e-5)
    
    # 3. Calorie Density Classification
    # Low Calorie: < 100 kcal, Medium: 100 - 300 kcal, High: > 300 kcal per 100g
    df["Calorie_Density_Label"] = pd.cut(
        df["Calories"], 
        bins=[-np.inf, 100, 300, np.inf], 
        labels=["Low", "Medium", "High"]
    )
    
    print(f"Created engineered features. Current columns: {list(df.columns)}")
    return df

def preprocess_and_save():
    # Paths setup
    raw_data_path = os.path.join("data", "food_dataset.csv")
    output_dir = os.path.join("data", "preprocessed")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Raw Data
    df = load_raw_data(raw_data_path)
    
    # Columns setup
    numeric_features = ["Carbohydrates_g", "Protein_g", "Fat_g", "Fiber_g"]
    target = "Calories"
    
    # 2. Handle missing data
    df = handle_missing_values(df, numeric_features, target)
    
    # 3. Outlier removal
    df = remove_outliers_iqr(df, numeric_features)
    
    # 4. Feature Engineering
    df = perform_feature_engineering(df)
    
    # 5. Split Dataset
    print("\n[Step 5] Splitting dataset into train/test sets...")
    X = df[numeric_features + ["Total_Macros_g", "Carbs_Protein_Ratio"]]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train set: {X_train.shape[0]} samples. Test set: {X_test.shape[0]} samples.")
    
    # 6. Feature Scaling (Standardization)
    print("\n[Step 6] Standardizing continuous features (Zero Mean, Unit Variance)...")
    scaler = StandardScaler()
    
    # Scale X_train and X_test separately to prevent data leakage
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save processed splits to CSV
    print(f"\n[Step 7] Saving preprocessed training/testing datasets to {output_dir}...")
    pd.DataFrame(X_train_scaled, columns=X.columns).to_csv(os.path.join(output_dir, "X_train.csv"), index=False)
    pd.DataFrame(X_test_scaled, columns=X.columns).to_csv(os.path.join(output_dir, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(output_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(output_dir, "y_test.csv"), index=False)
    
    # Also save the scaled full preprocessed dataset for visualization if needed
    df.to_csv(os.path.join(output_dir, "fully_preprocessed_foods.csv"), index=False)
    
    print("\n=== Data Preprocessing Pipeline Completed Successfully! ===")

if __name__ == "__main__":
    preprocess_and_save()
