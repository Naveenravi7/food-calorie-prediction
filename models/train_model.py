import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def main():
    print("--- Starting ML Model Training ---")
    
    # Path settings
    dataset_path = os.path.join("data", "food_dataset.csv")
    models_dir = "models"
    model_output_path = os.path.join(models_dir, "calorie_model.pkl")
    
    # Ensure directories exist
    os.makedirs(models_dir, exist_ok=True)
    
    # Load dataset
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}. Please run fetch_data.py first.")
        return
        
    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {len(df)} items.")
    
    # Define features and target
    features = ["Carbohydrates_g", "Protein_g", "Fat_g", "Fiber_g"]
    target = "Calories"
    
    # Drop rows with NaN in features or target
    df_clean = df.dropna(subset=features + [target])
    print(f"Dataset size after dropping NaNs: {len(df_clean)} items.")
    
    X = df_clean[features]
    y = df_clean[target]
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples.")
    
    # Train Random Forest Regressor
    rf_model = RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Train Linear Regression for comparison
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    
    # Evaluate Random Forest
    rf_preds = rf_model.predict(X_test)
    rf_r2 = r2_score(y_test, rf_preds)
    rf_mae = mean_absolute_error(y_test, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
    
    # Evaluate Linear Regression
    lr_preds = lr_model.predict(X_test)
    lr_r2 = r2_score(y_test, lr_preds)
    lr_mae = mean_absolute_error(y_test, lr_preds)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_preds))
    
    print("\n--- Model Evaluation Results ---")
    print("Random Forest Regressor:")
    print(f"  R^2 Score:                  {rf_r2:.4f}")
    print(f"  Mean Absolute Error (MAE):  {rf_mae:.2f} kcal/100g")
    print(f"  Root Mean Sq. Error (RMSE): {rf_rmse:.2f} kcal/100g")
    
    print("\nLinear Regression (Baseline):")
    print(f"  R^2 Score:                  {lr_r2:.4f}")
    print(f"  Mean Absolute Error (MAE):  {lr_mae:.2f} kcal/100g")
    print(f"  Root Mean Sq. Error (RMSE): {lr_rmse:.2f} kcal/100g")
    
    # Calculate Feature Importances
    importances = rf_model.feature_importances_
    feat_imp = dict(zip(features, importances))
    print("\nRandom Forest Feature Importances:")
    for feat, imp in feat_imp.items():
        print(f"  {feat}: {imp:.4f}")
        
    # Save the model and metrics dictionary together
    model_data = {
        "model": rf_model,
        "features": features,
        "metrics": {
            "rf": {"r2": rf_r2, "mae": rf_mae, "rmse": rf_rmse},
            "lr": {"r2": lr_r2, "mae": lr_mae, "rmse": lr_rmse}
        },
        "importances": feat_imp
    }
    
    with open(model_output_path, "wb") as f:
        pickle.dump(model_data, f)
        
    print(f"\nTrained model and metadata saved successfully to: {model_output_path}")

if __name__ == "__main__":
    main()
