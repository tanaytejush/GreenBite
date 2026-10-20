import pickle
from sklearn.metrics.pairwise import cosine_similarity

# --------- Step 1: Load Saved Files ---------
with open("model/recipe_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("model/recipe_vectors.pkl", "rb") as f:
    recipe_vectors = pickle.load(f)

with open("model/recipes.pkl", "rb") as f:
    recipes = pickle.load(f)

# --------- Step 2: Convert User Profile to Text ---------
def profile_to_text(profile):
    diet = profile.get("food_preference", "")
    goal = profile.get("dietary_goal", "")
    flavors = " ".join(profile.get("flavor_profile", []))
    ingredients = " ".join(profile.get("ingredients", []))
    tools = " ".join(profile.get("tools", []))
    skill = profile.get("skill", "")
    time = str(profile.get("time", ""))
    return f"{diet} {goal} {flavors} {ingredients} {tools} {skill} {time}"

# --------- Step 3: Normalize Ingredients ---------
def normalize_ingredients(ingredients):
    return set(i.lower().rstrip('s') for i in ingredients)

# --------- Step 4: Calculate Ingredient Match Score ---------
def calculate_ingredient_match_score(user_ingredients, recipe_ingredients):
    user_ingredients = set(user_ingredients)
    recipe_ingredients = set(recipe_ingredients)
    match_count = len(user_ingredients.intersection(recipe_ingredients))
    return match_count / len(user_ingredients) if user_ingredients else 0

# --------- Step 5: Penalize Persistent Recipes ---------
recommendation_counts = {}

def penalize_persistent_recipes(recipe_id):
    count = recommendation_counts.get(recipe_id, 0)
    penalty = 1 / (1 + count)
    recommendation_counts[recipe_id] = count + 1
    return penalty

# --------- Step 6: Diversify Recommendations ---------
def diversify_recommendations(recommendations, diversity_factor=0.5):
    diversified = []
    seen_categories = set()

    for recipe, score in recommendations:
        category = recipe.get("category", "uncategorized")
        if category not in seen_categories or len(diversified) < 5:
            diversified.append((recipe, score))
            seen_categories.add(category)

    return diversified

# --------- Step 7: Recommend Recipes ---------
def recommend_recipes(user_profile, top_n=5):
    user_text = profile_to_text(user_profile)
    user_vec = vectorizer.transform([user_text])

    similarities = cosine_similarity(user_vec, recipe_vectors)[0]
    sorted_indices = similarities.argsort()[::-1]

    user_ingredients = normalize_ingredients(user_profile.get("ingredients", []))
    allergies = set(a.lower() for a in user_profile.get("allergies", []))
    recommended = []

    for idx in sorted_indices:
        recipe = recipes[idx]
        recipe_ingredients = normalize_ingredients(recipe.get("ingredients", []))
        recipe_allergens = set(a.lower() for a in recipe.get("allergens", []))

        if allergies.intersection(recipe_allergens):
            continue

        ingredient_score = calculate_ingredient_match_score(user_ingredients, recipe_ingredients)
        final_score = 0.7 * ingredient_score + 0.3 * similarities[idx]

        penalty = penalize_persistent_recipes(recipe.get("id", 0))
        final_score *= penalty

        recommended.append((recipe, final_score))

    recommended = sorted(recommended, key=lambda x: x[1], reverse=True)
    recommended = diversify_recommendations(recommended)

    return [r[0] for r in recommended[:top_n]]
