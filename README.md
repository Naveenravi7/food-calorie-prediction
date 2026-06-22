# NuPredict - Food Calorie & Nutrient Tracker Web App 🥑

NuPredict is a modern, high-fidelity **Streamlit** web application designed to predict calories from food items using **Machine Learning** (Random Forest Regressor) and track daily nutritional intake and habit streaks. It compiles a dataset of **550+ food products** by fetching data directly from the public **Open Food Facts API**, trains multiple regression models, and provides an interactive web dashboard.

---

## 🌟 Key Features

1. **🔮 Machine Learning Calorie Predictor**:
   - Predicts food calories (per 100g) dynamically based on user-inputted macronutrients: **Carbohydrates**, **Proteins**, **Fats**, and **Fiber**.
   - Powered by a trained **Random Forest Regressor** model ($R^2 \approx 0.89$, MAE $\approx 18.5$ kcal/100g).
   - Compares the model's predictions with the theoretical **Atwater General Factor System** ($4 \times \text{Carbs} + 4 \times \text{Protein} + 9 \times \text{Fat}$).

2. **🔥 Persistent Streak Habit Tracker**:
   - Tracks consecutive daily logins and meal logs to build healthy logging habits.
   - Streak data persists locally via `user_profile.json` so user progress is saved across app restarts.
   - Visualizes streaks, best historical streaks, and total active days with glowing aesthetic indicators.

3. **🥗 Food Search & Logging System**:
   - Dynamic search engine querying the scraped/cleaned food dataset of 550+ items.
   - Calculates custom portions (serving sizes in grams) and scales nutrients instantly.
   - Interactive gauge charts (for daily calorie limit) and doughnut charts (for carbohydrate/protein/fat ratio contributions) powered by **Plotly**.
   - Custom meal logging system allowing users to add unlisted items manually.

4. **📈 ML Dashboard & Dataset Insights**:
   - Shows live validation metrics: Coefficient of Determination ($R^2$), Mean Absolute Error (MAE), and Root Mean Squared Error (RMSE).
   - Compares Random Forest performance with a Baseline Linear Regression model.
   - Displays Random Forest feature importances showing which macronutrients contribute most to calorie density.
   - Interactive scatter plots for examining correlations between macronutrients and calorie count.

---

## 📁 Project Directory Structure

```
food-calorie-predictor/
├── data/
│   ├── fetch_data.py             # Script to scrape/fetch 1800+ foods from Open Food Facts
│   ├── preprocess.py             # Data preprocessing pipeline (outliers, imputation, scaling)
│   ├── food_dataset.csv          # Cleaned raw dataset
│   └── preprocessed/             # Folder containing standardized training/testing splits
├── models/
│   ├── train_model.py            # Model training & comparison script
│   └── calorie_model.pkl         # Serialized Random Forest model & evaluation metadata
├── src/
│   ├── app.py                    # Main Streamlit web application
│   └── utils.py                  # UI helper module (glassmorphic CSS, database, Plotly charts)
├── user_profile.json             # Persistent local database for streaks and daily logs
└── requirements.txt              # Project package requirements
```

---

## 🚀 Getting Started (Setup & Run)

Follow these simple steps to run the project locally on your machine:

### 1. Prerequisites
Make sure you have **Python 3.8+** installed.

### 2. Clone/Copy Code & Install Dependencies
Navigate to your project directory and install the necessary libraries:
```bash
pip install -r requirements.txt
```

### 3. Fetch/Scrape Food Data
Run the scraping script to fetch food products from Open Food Facts API and generate the dataset:
```bash
python data/fetch_data.py
```
*Note: A local offline fallback dataset is automatically merged to guarantee the baseline quality of common foods (e.g. apple, egg, rice).*

### 4. Train the ML Model
Train the Random Forest regressor and save the model file:
```bash
python models/train_model.py
```

### 5. Launch the Streamlit Web Application
Run the Streamlit development server:
```bash
streamlit run app.py
```

Streamlit will open a new tab in your web browser (usually at `http://localhost:8501`).

---

## 📊 Technical ML Details

- **Dataset Size:** 557 unique food items.
- **Target Variable:** `Calories` (kcal per 100g).
- **Predictors:** `Carbohydrates_g`, `Protein_g`, `Fat_g`, `Fiber_g`.
- **Model Architecture:** `RandomForestRegressor(n_estimators=150, max_depth=12)`.
- **Performance:**
  - **Random Forest R² Score:** `0.8933`
  - **Linear Regression Baseline R² Score:** `0.9071`
  - **Feature Importances:** `Fat` ($\approx 50.2\%$), `Carbohydrates` ($\approx 44.0\%$), `Protein` ($\approx 5.0\%$), `Fiber` ($\approx 0.8\%$).
