@echo off
title NuPredict App Launcher
echo ===================================================
echo   🥑 NuPredict - Starting Streamlit Web App 🥑
echo ===================================================
echo.
cd /d "%~dp0"

echo [1/3] Checking dependencies...
pip install -r requirements.txt
echo.

echo [2/3] Checking ML model...
if not exist "models\calorie_model.pkl" (
    echo Model not found. Training model now...
    python models\train_model.py
) else (
    echo ML Model verified!
)
echo.

echo [3/3] Launching Streamlit Web App...
streamlit run src\app.py
pause
