import pandas as pd
import json
import random
import os

# ------------------ CONFIG ------------------

food_types = ["vegetarian", "vegan", "pescatarian", "non-vegetarian", "eggetarian"]
dietary_goals = [
    "bulking", "cutting", "maintenance", "keto", "paleo",
    "high protein", "low carb", "diabetic friendly"
]

allergen_keywords = {
    "gluten": ["wheat", "barley", "bread", "flour", "pasta"],
    "dairy": ["milk", "cheese", "butter", "yogurt", "cream"],
    "nuts": ["almond", "cashew", "walnut", "peanut", "hazelnut", "pistachio"],
    "soy": ["soy", "tofu", "soya"],
    "eggs": ["egg", "mayonnaise"],
    "seafood": ["fish", "shrimp", "prawn", "tuna", "salmon"]
}

flavor_keywords = {
    "spicy": ["chili", "pepper", "jalapeno", "hot sauce"],
    "sweet": ["sugar", "honey", "maple", "chocolate", "vanilla"],
    "savory": ["garlic", "onion", "soy", "butter"],
    "sour": ["lemon", "lime", "vinegar", "tamarind"],
    "bitter": ["coffee", "kale", "cocoa", "beer"],
    "umami": ["miso", "mushroom", "parmesan", "anchovy"],
    "smoky": ["smoked", "charred", "grilled"],
    "herby": ["basil", "parsley", "thyme", "oregano", "rosemary"],
    "citrusy": ["orange", "lime", "lemon", "grapefruit"],
    "earthy": ["beet", "mushroom", "truffle"],
    "nutty": ["almond", "peanut", "cashew", "walnut"],
    "tangy": ["vinegar", "pickle", "mustard"],
    "creamy": ["cream", "milk", "butter", "cheese", "yogurt"],
    "cheesy": ["cheddar", "mozzarella", "parmesan", "gouda"],
    "buttery": ["butter", "ghee"],
    "fruity": ["apple", "banana", "berry", "mango", "grape"],
    "salty": ["salt", "soy sauce", "anchovy"]
}

# ------------------ IMAGE MATCHING ------------------

# List all image filenames in static/ (case-insensitive lookup)
image_folder = "static"
image_files = {f.lower(): f for f in os.listdir(image_folder)}

def find_image_filename(name):
    if not name:
        return ""
    base_name = name.lower().strip()
    if not base_name.endswith((".jpg", ".jpeg", ".png")):
        for ext in [".jpg", ".jpeg", ".png"]:
            candidate = base_name + ext
            if candidate in image_files:
                return f"/static/{image_files[candidate]}"
    elif base_name in image_files:
        return f"/static/{image_files[base_name]}"
    return ""  # Image not found

# ------------------ LOAD CSV ------------------

df = pd.read_csv("dataset.csv")
processed = []

# ------------------ PROCESS EACH RECIPE ------------------

for _, row in df.iterrows():
    name = row.get("Title", "")
    ingredients_raw = row.get("Cleaned_Ingredients", "")
    instructions_raw = row.get("Instructions", "")
    image = find_image_filename(row.get("Image_Name", "").strip())

    if pd.isna(name) or pd.isna(ingredients_raw) or not ingredients_raw.strip():
        continue

    try:
        ingredients = eval(ingredients_raw)
        ingredients = [i.lower().strip() for i in ingredients if isinstance(i, str) and i.strip()]
    except:
        continue

    if not ingredients:
        continue

    # Diet
    food_type = random.choice(food_types)
    dietary_goal = random.choice(dietary_goals)
    diet = [food_type, dietary_goal]

    # Allergens
    detected_allergens = [
        allergen for allergen, keywords in allergen_keywords.items()
        if any(k in i for i in ingredients for k in keywords)
    ]

    # Flavors
    detected_flavors = [
        flavor for flavor, keywords in flavor_keywords.items()
        if any(k in i for i in ingredients for k in keywords)
    ]

    # Instructions
    instructions_list = (
        [step.strip() for step in instructions_raw.split('\n') if step.strip()]
        if isinstance(instructions_raw, str) and instructions_raw.strip()
        else ["Instructions not available."]
    )

    # Build the recipe object
    processed.append({
        "id": int(row["Unnamed: 0"]) if "Unnamed: 0" in row else random.randint(1000, 9999),
        "name": name,
        "ingredients": ingredients,
        "instructions": instructions_list,
        "diet": diet,
        "allergens": detected_allergens,
        "flavors": detected_flavors,
        "image": image
    })

# ------------------ SAVE TO JSON ------------------

with open("data/recipes.json", "w") as f:
    json.dump(processed, f, indent=2)

print(f"✅ Cleaned and saved {len(processed)} recipes to data/recipes.json")
