import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import os
os.makedirs("model", exist_ok=True)

# --------- Step 1: Load Recipes ---------
with open("data/recipes.json", "r") as f:
    recipes = json.load(f)

# --------- Step 2: Convert Each Recipe to Personalized Text ---------
def recipe_to_text(r):
    diet = " ".join(r.get("diet", []))
    flavors = " ".join(r.get("flavors", []))
    ingredients = " ".join(r.get("ingredients", []))
    allergens = " ".join(r.get("allergens", []))
    
    # These fields don't exist in the new dataset
    tools = " ".join(r.get("tools", [])) if "tools" in r else ""
    skill = r.get("skill", "") if "skill" in r else ""
    time = str(r.get("time", "")) if "time" in r else ""
    
    return f"{diet} {flavors} {ingredients} {allergens} {tools} {skill} {time}"

corpus = [recipe_to_text(r) for r in recipes]

# --------- Step 3: Vectorize Using TF-IDF ---------
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

# --------- Step 4: Save Vectorizer, Matrix, and Recipes ---------
with open("model/recipe_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("model/recipe_vectors.pkl", "wb") as f:
    pickle.dump(X, f)

with open("model/recipes.pkl", "wb") as f:
    pickle.dump(recipes, f)

print("✅ Recipe vectorization complete. Files saved to /model")
