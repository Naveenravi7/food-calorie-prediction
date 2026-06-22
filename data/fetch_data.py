import os
import time
import requests
import pandas as pd
import numpy as np

# Open Food Facts API Categories to fetch
CATEGORIES = [
    # Original categories
    "pizza", "burger", "salad", "sandwich", "soup", "yogurt", "bread", 
    "cheese", "snack", "chocolate", "juice", "pasta", "cookie", "cake", 
    "cereal", "ice cream", "soda", "chicken", "beef", "milk",
    # Additional categories for 1500+ data items
    "rice", "fish", "meat", "egg", "butter", "oil", "sauce", "potato", 
    "onion", "tomato", "beans", "nut", "seed", "coffee", "tea", 
    "pastry", "pie", "donut", "fruit", "vegetable", "sausage", 
    "ham", "honey", "jam", "seafood", "pork", "turkey", "lamb", 
    "spices", "cracker", "chips", "wrap", "taco", "sushi"
]

FALLBACK_FOODS = [
    {"Food_Item": "Apple", "Category": "Fruit", "Carbohydrates_g": 13.8, "Protein_g": 0.3, "Fat_g": 0.2, "Fiber_g": 2.4, "Calories": 52.0},
    {"Food_Item": "Banana", "Category": "Fruit", "Carbohydrates_g": 22.8, "Protein_g": 1.1, "Fat_g": 0.3, "Fiber_g": 2.6, "Calories": 89.0},
    {"Food_Item": "Orange", "Category": "Fruit", "Carbohydrates_g": 11.8, "Protein_g": 0.9, "Fat_g": 0.1, "Fiber_g": 2.4, "Calories": 47.0},
    {"Food_Item": "Broccoli", "Category": "Vegetable", "Carbohydrates_g": 6.6, "Protein_g": 2.8, "Fat_g": 0.4, "Fiber_g": 2.6, "Calories": 34.0},
    {"Food_Item": "Spinach", "Category": "Vegetable", "Carbohydrates_g": 3.6, "Protein_g": 2.9, "Fat_g": 0.4, "Fiber_g": 2.2, "Calories": 23.0},
    {"Food_Item": "Chicken Breast", "Category": "Meat", "Carbohydrates_g": 0.0, "Protein_g": 31.0, "Fat_g": 3.6, "Fiber_g": 0.0, "Calories": 165.0},
    {"Food_Item": "Salmon", "Category": "Fish", "Carbohydrates_g": 0.0, "Protein_g": 20.0, "Fat_g": 13.0, "Fiber_g": 0.0, "Calories": 208.0},
    {"Food_Item": "Brown Rice", "Category": "Grain", "Carbohydrates_g": 23.0, "Protein_g": 2.6, "Fat_g": 0.9, "Fiber_g": 1.8, "Calories": 111.0},
    {"Food_Item": "White Bread", "Category": "Grain", "Carbohydrates_g": 49.0, "Protein_g": 9.0, "Fat_g": 3.2, "Fiber_g": 2.7, "Calories": 265.0},
    {"Food_Item": "Whole Milk", "Category": "Dairy", "Carbohydrates_g": 4.8, "Protein_g": 3.2, "Fat_g": 3.3, "Fiber_g": 0.0, "Calories": 61.0},
    {"Food_Item": "Egg (Large)", "Category": "Dairy", "Carbohydrates_g": 0.6, "Protein_g": 12.6, "Fat_g": 9.5, "Fiber_g": 0.0, "Calories": 143.0},
    {"Food_Item": "Cheddar Cheese", "Category": "Dairy", "Carbohydrates_g": 1.3, "Protein_g": 25.0, "Fat_g": 33.0, "Fiber_g": 0.0, "Calories": 403.0},
    {"Food_Item": "Potato Chips", "Category": "Snack", "Carbohydrates_g": 53.0, "Protein_g": 7.0, "Fat_g": 35.0, "Fiber_g": 4.0, "Calories": 536.0},
    {"Food_Item": "Oatmeal", "Category": "Grain", "Carbohydrates_g": 12.0, "Protein_g": 3.0, "Fat_g": 1.5, "Fiber_g": 1.7, "Calories": 68.0},
    {"Food_Item": "Almonds", "Category": "Snack", "Carbohydrates_g": 22.0, "Protein_g": 21.0, "Fat_g": 49.0, "Fiber_g": 12.0, "Calories": 579.0},
    {"Food_Item": "Greek Yogurt", "Category": "Dairy", "Carbohydrates_g": 3.6, "Protein_g": 10.0, "Fat_g": 0.4, "Fiber_g": 0.0, "Calories": 59.0},
    {"Food_Item": "Avocado", "Category": "Fruit", "Carbohydrates_g": 8.5, "Protein_g": 2.0, "Fat_g": 14.7, "Fiber_g": 6.7, "Calories": 160.0},
    {"Food_Item": "Pizza Margherita", "Category": "Fast Food", "Carbohydrates_g": 30.0, "Protein_g": 11.0, "Fat_g": 10.0, "Fiber_g": 2.2, "Calories": 250.0},
    {"Food_Item": "Beef Burger", "Category": "Fast Food", "Carbohydrates_g": 24.0, "Protein_g": 14.0, "Fat_g": 12.0, "Fiber_g": 1.5, "Calories": 260.0},
    {"Food_Item": "French Fries", "Category": "Fast Food", "Carbohydrates_g": 41.0, "Protein_g": 3.4, "Fat_g": 15.0, "Fiber_g": 3.8, "Calories": 312.0},
    {"Food_Item": "Chocolate Bar", "Category": "Snack", "Carbohydrates_g": 59.0, "Protein_g": 4.9, "Fat_g": 30.0, "Fiber_g": 3.4, "Calories": 535.0},
    {"Food_Item": "Coca Cola", "Category": "Beverage", "Carbohydrates_g": 10.6, "Protein_g": 0.0, "Fat_g": 0.0, "Fiber_g": 0.0, "Calories": 42.0},
    {"Food_Item": "Orange Juice", "Category": "Beverage", "Carbohydrates_g": 10.4, "Protein_g": 0.7, "Fat_g": 0.2, "Fiber_g": 0.2, "Calories": 45.0},
    {"Food_Item": "Butter", "Category": "Dairy", "Carbohydrates_g": 0.1, "Protein_g": 0.9, "Fat_g": 81.0, "Fiber_g": 0.0, "Calories": 717.0},
    {"Food_Item": "Olive Oil", "Category": "Fat", "Carbohydrates_g": 0.0, "Protein_g": 0.0, "Fat_g": 100.0, "Fiber_g": 0.0, "Calories": 884.0},
    {"Food_Item": "Peanut Butter", "Category": "Snack", "Carbohydrates_g": 20.0, "Protein_g": 25.0, "Fat_g": 50.0, "Fiber_g": 6.0, "Calories": 588.0},
    {"Food_Item": "Tofu", "Category": "Vegetable", "Carbohydrates_g": 1.9, "Protein_g": 8.0, "Fat_g": 4.8, "Fiber_g": 0.3, "Calories": 76.0},
    {"Food_Item": "White Rice", "Category": "Grain", "Carbohydrates_g": 28.0, "Protein_g": 2.7, "Fat_g": 0.3, "Fiber_g": 0.4, "Calories": 130.0},
    {"Food_Item": "Spaghetti", "Category": "Grain", "Carbohydrates_g": 31.0, "Protein_g": 6.0, "Fat_g": 0.6, "Fiber_g": 1.8, "Calories": 158.0},
    {"Food_Item": "Tomato", "Category": "Vegetable", "Carbohydrates_g": 3.9, "Protein_g": 0.9, "Fat_g": 0.2, "Fiber_g": 1.2, "Calories": 18.0},
]

def fetch_category_data(category, limit=70):
    print(f"Fetching category: {category}...")
    url = f"https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": category,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit
    }
    headers = {
        "User-Agent": "FoodCaloriePredictionApp/1.0 (developer.naveen@example.com)"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error status {response.status_code} for category {category}")
            return []
        
        data = response.json()
        products = data.get("products", [])
        
        cleaned_products = []
        for p in products:
            # Get name
            name = p.get("product_name") or p.get("product_name_en")
            if not name:
                continue
            
            nutr = p.get("nutriments", {})
            
            # Extract macronutrients
            carbs = nutr.get("carbohydrates_100g")
            protein = nutr.get("proteins_100g")
            fat = nutr.get("fat_100g")
            fiber = nutr.get("fiber_100g", 0)
            
            # Get calories (prefer kcal, convert from kJ if necessary)
            calories = nutr.get("energy-kcal_100g")
            if calories is None:
                energy_kj = nutr.get("energy_100g")
                if energy_kj is not None:
                    calories = round(float(energy_kj) / 4.184, 1)
            
            # Skip if critical values are missing
            if carbs is None or protein is None or fat is None or calories is None:
                continue
                
            try:
                carbs = float(carbs)
                protein = float(protein)
                fat = float(fat)
                fiber = float(fiber) if fiber is not None else 0.0
                calories = float(calories)
            except ValueError:
                continue
                
            # Basic sanity checks: macronutrients sum <= 100g, calories are reasonable
            if carbs < 0 or protein < 0 or fat < 0 or fiber < 0 or calories < 0:
                continue
            if carbs + protein + fat > 105: # allow small margin of error
                continue
            if calories > 950: # fat max is 900 kcal/100g
                continue
                
            cleaned_products.append({
                "Food_Item": name.strip().title(),
                "Category": category.title(),
                "Carbohydrates_g": round(carbs, 2),
                "Protein_g": round(protein, 2),
                "Fat_g": round(fat, 2),
                "Fiber_g": round(fiber, 2),
                "Calories": round(calories, 1)
            })
            
        print(f"Successfully scraped {len(cleaned_products)} products for {category}.")
        return cleaned_products
    except Exception as e:
        print(f"Network exception when fetching {category}: {e}")
        return []

def main():
    print("--- Starting Food Calorie Dataset Scraper/Fetcher ---")
    all_data = []
    
    for cat in CATEGORIES:
        cat_data = fetch_category_data(cat, limit=120)
        all_data.extend(cat_data)
        time.sleep(0.5) # Rate limit protection
    
    # Save directory setup
    os.makedirs("data", exist_ok=True)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Append fallback items to ensure baseline quality items are always present
    fallback_df = pd.DataFrame(FALLBACK_FOODS)
    
    if df.empty:
        print("Warning: Web fetching returned no data. Using fallback dataset.")
        df = fallback_df
    else:
        # Drop duplicates by name case-insensitive
        df["_lower_name"] = df["Food_Item"].str.lower()
        df = df.drop_duplicates(subset=["_lower_name"])
        df = df.drop(columns=["_lower_name"])
        
        # Merge with fallback to guarantee clean standard foods exist
        df = pd.concat([fallback_df, df], ignore_index=True)
        # Re-drop duplicates preferring standard fallback entries
        df["_lower_name"] = df["Food_Item"].str.lower()
        df = df.drop_duplicates(subset=["_lower_name"], keep="first")
        df = df.drop(columns=["_lower_name"])
        
    print(f"Total dataset size after cleaning and merging: {len(df)} items.")
    
    # Save to CSV
    output_path = os.path.join("data", "food_dataset.csv")
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully saved to: {output_path}")

if __name__ == "__main__":
    main()
