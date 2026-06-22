import os
import pickle
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Import helpers
from utils import (
    load_profile,
    save_profile,
    check_and_update_streak,
    log_meal_and_update_streak,
    delete_meal_entry,
    inject_custom_css,
    create_calorie_gauge,
    create_macro_pie_chart,
    create_calorie_history_chart
)

# Set page configurations
st.set_page_config(
    page_title="NuPredict - Food Calorie & Nutrient Tracker",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom styles
inject_custom_css()

# Paths
DATASET_PATH = os.path.join("data", "food_dataset.csv")
MODEL_PATH = os.path.join("models", "calorie_model.pkl")

# Load dataset and ML model helper functions
@st.cache_data
def load_dataset():
    if os.path.exists(DATASET_PATH):
        return pd.read_csv(DATASET_PATH)
    return pd.DataFrame(columns=["Food_Item", "Category", "Carbohydrates_g", "Protein_g", "Fat_g", "Fiber_g", "Calories"])

def load_ml_model():
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"Error loading model: {e}")
    return None

# Load application data
df_foods = load_dataset()
model_data = load_ml_model()

# Initialize session state for user profile
if "profile" not in st.session_state:
    profile = load_profile()
    st.session_state.profile = check_and_update_streak(profile)

# Sync local settings
limit = st.session_state.profile.get("daily_calorie_limit", 2000)

# Title Area
st.markdown("<h1 class='glow-text' style='text-align: center; margin-bottom: 5px;'>🥑 NuPredict</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8a99ad; margin-bottom: 25px;'>Precision Food Calorie Estimation & Smart Habit Tracking Dashboard</p>", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.markdown("<h3 class='glow-text-orange'>⚙️ Control Center</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Calorie Limit config
    new_limit = st.number_input("Daily Calorie Target (kcal):", min_value=1000, max_value=5000, value=int(limit), step=100)
    if new_limit != limit:
        st.session_state.profile["daily_calorie_limit"] = new_limit
        save_profile(st.session_state.profile)
        st.rerun()
        
    st.markdown("### Profile Summary")
    st.write(f"**Total Days Active:** {st.session_state.profile['total_days_logged']} days")
    
    # Reset Option
    st.markdown("---")
    if st.button("Reset Profile & Progress", type="primary", use_container_width=True):
        default_profile = {
            "streak": 0,
            "longest_streak": 0,
            "last_log_date": None,
            "total_days_logged": 0,
            "daily_calorie_limit": 2000,
            "history": {}
        }
        st.session_state.profile = default_profile
        save_profile(default_profile)
        st.success("Profile reset successfully!")
        st.rerun()

# Setup Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Streak & Dashboard", 
    "🔮 ML Calorie Predictor", 
    "🥗 Food Search & Log", 
    "📈 Model performance"
])

# ==========================================
# TAB 1: STREAK & DASHBOARD
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.container(border=True):
            st.markdown("<h3 class='glow-text-orange'>🔥 Your Habit Streak</h3>", unsafe_allow_html=True)
            
            streak = st.session_state.profile.get("streak", 0)
            longest_streak = st.session_state.profile.get("longest_streak", 0)
            
            # Display streak counter
            st.markdown(f"""
                <div style='text-align: center; margin: 20px 0;'>
                    <span class='streak-badge'>🔥 {streak} Day Streak</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Streak message
            if streak == 0:
                st.markdown("<p style='text-align: center; color: #8a99ad;'>You haven't logged today yet! Add a meal in the <b>Food Search & Log</b> tab to start your streak.</p>", unsafe_allow_html=True)
            elif streak == 1:
                st.markdown("<p style='text-align: center; color: #00ffc8;'>Great start! Log again tomorrow to keep your streak alive!</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='text-align: center; color: #00ffc8;'>Awesome! You've maintained your healthy streak for {streak} days. Keep it up!</p>", unsafe_allow_html=True)
                
            # Metric Grid
            st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-box'>
                        <div class='metric-value' style='color: #ff9500;'>{streak}</div>
                        <div class='metric-label'>Current Streak</div>
                    </div>
                    <div class='metric-box'>
                        <div class='metric-value' style='color: #00ffc8;'>{longest_streak}</div>
                        <div class='metric-label'>Best Streak</div>
                    </div>
                    <div class='metric-box'>
                        <div class='metric-value' style='color: #ffcc00;'>{st.session_state.profile.get("total_days_logged", 0)}</div>
                        <div class='metric-label'>Total Active Days</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
    with col2:
        with st.container(border=True):
            st.markdown("<h3 class='glow-text'>📊 Daily Nutrients (Today)</h3>", unsafe_allow_html=True)
            
            # Calculate today's totals
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            today_meals = st.session_state.profile["history"].get(today_str, [])
            
            total_calories = sum([m["calories"] for m in today_meals])
            total_carbs = sum([m["carbs"] for m in today_meals])
            total_protein = sum([m["protein"] for m in today_meals])
            total_fat = sum([m["fat"] for m in today_meals])
            
            sub_c1, sub_c2 = st.columns(2)
            with sub_c1:
                st.plotly_chart(create_calorie_gauge(total_calories, limit), use_container_width=True)
            with sub_c2:
                st.plotly_chart(create_macro_pie_chart(total_carbs, total_protein, total_fat), use_container_width=True)
                st.markdown("""
                    <div style='text-align: center; font-size: 12px; margin-top: -15px; color: #8a99ad;'>
                        <span style='color: #ff5e36; margin-right: 3px;'>■</span>Carbs
                        <span style='color: #00ffc8; margin-left: 10px; margin-right: 3px;'>■</span>Protein
                        <span style='color: #ffcc00; margin-left: 10px; margin-right: 3px;'>■</span>Fat
                    </div>
                """, unsafe_allow_html=True)
        
    # Calorie History chart row
    history_chart = create_calorie_history_chart(st.session_state.profile)
    if history_chart:
        with st.container(border=True):
            st.plotly_chart(history_chart, use_container_width=True)
    else:
        st.markdown("<p style='text-align: center; color: #8a99ad; margin-top: 20px;'>Log food items across multiple days to view your calorie history chart here.</p>", unsafe_allow_html=True)


# ==========================================
# TAB 2: ML CALORIE PREDICTOR
# ==========================================
with tab2:
    with st.container(border=True):
        st.markdown("<h3 class='glow-text'>🔮 Predict Calories from Nutrients</h3>", unsafe_allow_html=True)
        st.write("Search for a food from the database to pre-fill nutrients automatically, or adjust the sliders manually to see the ML model's prediction.")
        
        # Quick Autofill from Database
        if not df_foods.empty:
            st.markdown("##### 🔍 Quick Autofill from Database")
            autofill_query = st.text_input("Search a food item to pre-fill nutrients below:", key="ml_autofill_query", placeholder="e.g. Bread, Pizza, Egg").strip()
            
            if autofill_query:
                ml_matches = df_foods[df_foods["Food_Item"].str.contains(autofill_query, case=False, na=False)].head(5)
                if not ml_matches.empty:
                    # Map options
                    autofill_options = [f"{row['Food_Item']} (Carbs: {row['Carbohydrates_g']}g, Protein: {row['Protein_g']}g, Fat: {row['Fat_g']}g, Fiber: {row['Fiber_g']}g)" for idx, row in ml_matches.iterrows()]
                    selected_autofill_opt = st.selectbox("Select matching food item:", autofill_options, key="autofill_select_widget")
                    
                    selected_idx = autofill_options.index(selected_autofill_opt)
                    matched_item = ml_matches.iloc[selected_idx]
                    
                    if st.button("Apply Selected Food Nutrients", type="secondary", use_container_width=True):
                        st.session_state.p_carbs_val = float(matched_item["Carbohydrates_g"])
                        st.session_state.p_protein_val = float(matched_item["Protein_g"])
                        st.session_state.p_fat_val = float(matched_item["Fat_g"])
                        st.session_state.p_fiber_val = float(matched_item["Fiber_g"])
                        st.success(f"Applied nutrients for {matched_item['Food_Item']}!")
                        st.rerun()
                else:
                    st.warning("No matching food items found.")
            st.markdown("---")
            
        col_input, col_pred = st.columns([3, 2])
        
        with col_input:
            st.markdown("<br>", unsafe_allow_html=True)
            p_carbs = st.slider("Carbohydrates (grams per 100g):", 0.0, 100.0, value=st.session_state.get("p_carbs_val", 15.0), step=0.1)
            p_protein = st.slider("Protein (grams per 100g):", 0.0, 100.0, value=st.session_state.get("p_protein_val", 10.0), step=0.1)
            p_fat = st.slider("Fat (grams per 100g):", 0.0, 100.0, value=st.session_state.get("p_fat_val", 5.0), step=0.1)
            p_fiber = st.slider("Dietary Fiber (grams per 100g):", 0.0, 30.0, value=st.session_state.get("p_fiber_val", 1.0), step=0.1)
            
            # Sanity check sum
            total_g = p_carbs + p_protein + p_fat
            if total_g > 100:
                st.warning(f"⚠️ Total macronutrients sum up to {total_g:.1g}g. A food item cannot exceed 100g in total components per 100g.")
                
        with col_pred:
            # Standard formula (Atwater)
            atwater_cals = (p_carbs * 4) + (p_protein * 4) + (p_fat * 9)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            
            if model_data is not None:
                # Predict using ML model
                model = model_data["model"]
                features = model_data["features"]
                
                # Predict input DataFrame
                input_df = pd.DataFrame([[p_carbs, p_protein, p_fat, p_fiber]], columns=features)
                ml_pred = model.predict(input_df)[0]
                
                # Formatting the metrics
                st.markdown(f"""
                    <div style='background: rgba(0, 255, 200, 0.08); border: 2px solid #00ffc8; border-radius: 12px; padding: 25px; display: inline-block; min-width: 250px;'>
                        <div style='font-size: 14px; text-transform: uppercase; color: #8a99ad; letter-spacing: 1px;'>ML Calorie Prediction</div>
                        <div style='font-size: 48px; font-weight: 700; color: #ffffff; text-shadow: 0 0 10px rgba(0, 255, 200, 0.3);'>{ml_pred:.1f}</div>
                        <div style='font-size: 12px; color: #00ffc8;'>kcal per 100g</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Difference comparison
                diff = ml_pred - atwater_cals
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"**Standard Atwater Formula (4-4-9):** `{atwater_cals:.1f}` kcal/100g")
                
                if abs(diff) < 2.0:
                    st.markdown("🟢 *The ML prediction matches the theoretical Atwater formula closely.*")
                else:
                    direction = "higher" if diff > 0 else "lower"
                    st.markdown(f"ℹ️ *ML prediction is `{abs(diff):.1f}` kcal **{direction}** than the theoretical Atwater formula. The ML model has adjusted for non-linearities, water/ash content, and fiber density present in real foods.*")
            else:
                st.warning("⚠️ ML Model not found! Please run the training script (`models/train_model.py`) to activate the Machine Learning calorie predictor.")
                st.markdown(f"""
                    <div style='background: rgba(255, 149, 0, 0.08); border: 2px solid #ff9500; border-radius: 12px; padding: 25px; display: inline-block; min-width: 250px;'>
                        <div style='font-size: 14px; text-transform: uppercase; color: #8a99ad; letter-spacing: 1px;'>Atwater Formula (Fallback)</div>
                        <div style='font-size: 48px; font-weight: 700; color: #ffffff;'>{atwater_cals:.1f}</div>
                        <div style='font-size: 12px; color: #ff9500;'>kcal per 100g</div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 3: FOOD SEARCH & LOG
# ==========================================
with tab3:
    with st.container(border=True):
        st.markdown("<h3 class='glow-text'>🥗 Log Meals & Search Food Database</h3>", unsafe_allow_html=True)
        
        # Select Date
        log_date = st.date_input("Select Log Date:", datetime.date.today())
        log_date_str = log_date.strftime("%Y-%m-%d")
        
        st.markdown("#### Search Database")
        
        if df_foods.empty:
            st.info("No items in dataset yet. You can manually enter items to build your log, or wait for the scraper script to finish.")
        else:
            # Food items search bar
            search_query = st.text_input("🔍 Search Food Item (e.g. apple, pizza, bread):", "").strip()
            
            # Display search results
            if search_query:
                # Simple substring matching
                results = df_foods[df_foods["Food_Item"].str.contains(search_query, case=False, na=False)].head(10)
                
                if not results.empty:
                    st.write("Select food from search results:")
                    
                    # Show results in radio select
                    options = [f"{row['Food_Item']} ({row['Category']}) | Carbs: {row['Carbohydrates_g']}g, Protein: {row['Protein_g']}g, Fat: {row['Fat_g']}g | {row['Calories']} kcal/100g" for idx, row in results.iterrows()]
                    selected_opt = st.radio("Search Matches:", options, label_visibility="collapsed")
                    
                    selected_idx = options.index(selected_opt)
                    matched_row = results.iloc[selected_idx]
                    
                    # Portions inputs
                    sub_col1, sub_col2 = st.columns([2, 1])
                    with sub_col1:
                        portion_grams = st.number_input("Serving Weight (grams):", min_value=1.0, max_value=2000.0, value=100.0, step=10.0)
                    with sub_col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Log Selected Food", type="primary", use_container_width=True):
                            factor = portion_grams / 100.0
                            
                            # Use ML model to predict calories if available
                            if model_data is not None:
                                model = model_data["model"]
                                features = model_data["features"]
                                input_df = pd.DataFrame([[
                                    matched_row["Carbohydrates_g"], 
                                    matched_row["Protein_g"], 
                                    matched_row["Fat_g"], 
                                    matched_row["Fiber_g"]
                                ]], columns=features)
                                pred_cal_100g = model.predict(input_df)[0]
                                calculated_cals = round(pred_cal_100g * factor, 1)
                            else:
                                calculated_cals = round(matched_row["Calories"] * factor, 1)
                                
                            meal_entry = {
                                "food": matched_row["Food_Item"],
                                "carbs": round(matched_row["Carbohydrates_g"] * factor, 1),
                                "protein": round(matched_row["Protein_g"] * factor, 1),
                                "fat": round(matched_row["Fat_g"] * factor, 1),
                                "fiber": round(matched_row["Fiber_g"] * factor, 1),
                                "calories": calculated_cals,
                                "grams": portion_grams
                            }
                            st.session_state.profile = log_meal_and_update_streak(log_date_str, meal_entry, st.session_state.profile)
                            st.success(f"Logged {portion_grams}g of {matched_row['Food_Item']} (Predicted {calculated_cals} kcal)!")
                            st.rerun()
                else:
                    st.warning("No matches found. Try custom food entry below.")
                    
        st.markdown("---")
        st.markdown("#### ➕ Log Custom Food Entry")
        
        with st.form("custom_food_form"):
            col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
            with col_c1:
                custom_name = st.text_input("Food Name:", placeholder="e.g. Avocado Toast")
            with col_c2:
                custom_carbs = st.number_input("Carbs (g):", min_value=0.0, value=0.0, step=0.1)
            with col_c3:
                custom_protein = st.number_input("Protein (g):", min_value=0.0, value=0.0, step=0.1)
            with col_c4:
                custom_fat = st.number_input("Fat (g):", min_value=0.0, value=0.0, step=0.1)
            with col_c5:
                custom_fiber = st.number_input("Fiber (g):", min_value=0.0, value=0.0, step=0.1)
                
            submitted = st.form_submit_button("Log Custom Item", use_container_width=True)
            if submitted:
                if not custom_name:
                    st.error("Please enter a food name.")
                else:
                    # Predict calories for custom item using ML model if available
                    if model_data is not None:
                        # Predict using ML model
                        model = model_data["model"]
                        features = model_data["features"]
                        input_df = pd.DataFrame([[custom_carbs, custom_protein, custom_fat, custom_fiber]], columns=features)
                        calculated_cals = round(model.predict(input_df)[0], 1)
                    else:
                        calculated_cals = round((custom_carbs * 4) + (custom_protein * 4) + (custom_fat * 9), 1)
                    
                    meal_entry = {
                        "food": custom_name,
                        "carbs": custom_carbs,
                        "protein": custom_protein,
                        "fat": custom_fat,
                        "fiber": custom_fiber,
                        "calories": calculated_cals,
                        "grams": 100.0  # default custom item serving
                    }
                    
                    st.session_state.profile = log_meal_and_update_streak(log_date_str, meal_entry, st.session_state.profile)
                    st.success(f"Logged custom food '{custom_name}' with predicted {calculated_cals} kcal!")
                    st.rerun()
    
    # Logged meals list for date
    with st.container(border=True):
        st.markdown(f"<h3 class='glow-text-orange'>📝 Meal Log: {log_date.strftime('%B %d, %Y')}</h3>", unsafe_allow_html=True)
        
        logged_meals = st.session_state.profile["history"].get(log_date_str, [])
        
        if not logged_meals:
            st.write("No meals logged for this date.")
        else:
            # Table of meals
            meal_df_list = []
            for idx, m in enumerate(logged_meals):
                meal_df_list.append({
                    "Index": idx,
                    "Food Item": m["food"],
                    "Weight (g)": m["grams"],
                    "Carbs (g)": m["carbs"],
                    "Protein (g)": m["protein"],
                    "Fat (g)": m["fat"],
                    "Fiber (g)": m["fiber"],
                    "Calories (kcal)": m["calories"]
                })
                
            m_df = pd.DataFrame(meal_df_list)
            
            # Display table cleanly
            for idx, row in m_df.iterrows():
                sub_col_data, sub_col_del = st.columns([9, 1])
                with sub_col_data:
                    st.markdown(f"**{row['Food Item']}** ({row['Weight (g)']}g) | Carbs: {row['Carbs (g)']}g, Protein: {row['Protein (g)']}g, Fat: {row['Fat (g)']}g, Fiber: {row['Fiber (g)']}g | **{row['Calories (kcal)']} kcal**")
                with sub_col_del:
                    if st.button("❌", key=f"del_{log_date_str}_{idx}"):
                        st.session_state.profile = delete_meal_entry(log_date_str, row["Index"], st.session_state.profile)
                        st.rerun()
                        
            st.markdown("---")
            total_day_cal = sum([m["calories"] for m in logged_meals])
            st.write(f"**Total Day Calories:** `{total_day_cal:.1f}` kcal | Target limit: `{limit}` kcal")


# ==========================================
# TAB 4: MODEL PERFORMANCE & DATASET INSIGHTS
# ==========================================
with tab4:
    with st.container(border=True):
        st.markdown("<h3 class='glow-text-pink'>📈 Machine Learning Model Performance</h3>", unsafe_allow_html=True)
        
        if model_data is not None:
            metrics = model_data["metrics"]
            importances = model_data["importances"]
            
            st.write("Below are the real-time evaluation metrics of the calorie prediction Random Forest regressor, trained on our compiled food dataset. We also display the comparative performance against a baseline Linear Regression model.")
            
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                st.markdown("#### Random Forest Regressor (Selected Model)")
                st.markdown(f"""
                    <div style='background: rgba(0, 255, 200, 0.03); border: 1px solid rgba(0, 255, 200, 0.2); border-radius: 8px; padding: 15px; margin: 10px 0;'>
                        <div style='display: flex; justify-content: space-between;'><b>R² (Coefficient of Determination):</b> <code style='color:#00ffc8;'>{metrics['rf']['r2']:.4f}</code></div>
                        <div style='display: flex; justify-content: space-between;'><b>Mean Absolute Error (MAE):</b> <code>{metrics['rf']['mae']:.2f} kcal/100g</code></div>
                        <div style='display: flex; justify-content: space-between;'><b>Root Mean Squared Error (RMSE):</b> <code>{metrics['rf']['rmse']:.2f} kcal/100g</code></div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("*An R² score close to 1.0 indicates that our Random Forest model successfully explains nearly all variations in food calorie density based on the nutrient features.*")
                
            with col_m2:
                st.markdown("#### Linear Regression (Baseline)")
                st.markdown(f"""
                    <div style='background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 15px; margin: 10px 0;'>
                        <div style='display: flex; justify-content: space-between;'><b>R² (Coefficient of Determination):</b> <code>{metrics['lr']['r2']:.4f}</code></div>
                        <div style='display: flex; justify-content: space-between;'><b>Mean Absolute Error (MAE):</b> <code>{metrics['lr']['mae']:.2f} kcal/100g</code></div>
                        <div style='display: flex; justify-content: space-between;'><b>Root Mean Squared Error (RMSE):</b> <code>{metrics['lr']['rmse']:.2f} kcal/100g</code></div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("*The Linear Regression baseline shows a solid fit because the physics of energy intake is linear, but Random Forest handles non-linearities (like fiber deductions) better.*")
                
            # Feature importance chart
            st.markdown("---")
            st.markdown("#### 📊 Feature Importance")
            st.write("Feature importance values measure how heavily the Random Forest model relies on each nutrient to estimate calorie values.")
            
            imp_df = pd.DataFrame({
                "Nutrient": list(importances.keys()),
                "Importance Value": list(importances.values())
            }).sort_values("Importance Value", ascending=True)
            
            fig_imp = px.bar(
                imp_df, 
                x="Importance Value", 
                y="Nutrient", 
                orientation="h",
                color="Importance Value",
                color_continuous_scale="Viridis"
            )
            
            fig_imp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=20),
                height=200,
                coloraxis_showscale=False,
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8a99ad")),
                yaxis=dict(tickfont=dict(color="#8a99ad"))
            )
            st.plotly_chart(fig_imp, use_container_width=True)
            
        else:
            st.warning("⚠️ Model training data has not been generated yet. Please run the model trainer script (`models/train_model.py`) to generate details for this tab.")
            
        # Dataset Exploration section
        st.markdown("---")
        st.markdown("#### 📁 Dataset Inspection")
        if not df_foods.empty:
            st.write(f"The dataset contains `{len(df_foods)}` items. Below is a preview of the dataset:")
            
            # Display dataset table
            st.dataframe(df_foods.head(15), use_container_width=True)
            
            # Simple scatter plot of Carbs vs Calories
            st.markdown("##### Calorie Density vs Macronutrients")
            mac = st.selectbox("Select nutrient for scatter correlation plot:", ["Carbohydrates_g", "Protein_g", "Fat_g", "Fiber_g"])
            
            fig_scatter = px.scatter(
                df_foods, 
                x=mac, 
                y="Calories", 
                color="Category",
                hover_name="Food_Item",
                opacity=0.7,
                title=f"Correlation between {mac.split('_')[0]} (g) and Calorie Count"
            )
            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                height=350,
                legend=dict(font=dict(color="#ffffff")),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8a99ad"), title=mac),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#8a99ad"), title="Calories (kcal/100g)"),
                title=dict(font=dict(color="#ffffff"))
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Food dataset is currently empty. Run `data/fetch_data.py` to fetch food items.")
