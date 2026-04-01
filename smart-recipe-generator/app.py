import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from supabase import create_client, Client
import json
import requests

app = Flask(__name__, static_url_path='/static')

# Supabase setup
SUPABASE_URL = "https://hazgghhpurqmxaywejxi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhhemdnaGhwdXJxbXhheXdlanhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzYyNzIsImV4cCI6MjA1OTQ1MjI3Mn0.66YnxFAv1udH-E4ov4uphWxH2-d3Wzsf1wHg9WDd8uk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Load recipes
with open("data/recipes.json", "r") as f:
    RECIPES = json.load(f)

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    return redirect(url_for("generate_form"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if hasattr(response, "error") and response.error:
                return render_template("signup.html", error_message=response.error.message)

            if not hasattr(response, "user") or response.user is None:
                return render_template("signup.html", error_message="Signup failed. No user returned.")

            user = response.user
            user_id = user.id

            supabase.table("users").upsert({
                "user_id": user_id,
                "name": name,
                "email": email
            }).on_conflict("email").execute()

            session["user_id"] = user_id
            session["email"] = email
            session["name"] = name

            return redirect(url_for("profile"))

        except Exception as e:
            return render_template("signup.html", error_message=f"Signup error: {str(e)}")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if hasattr(response, 'error') and response.error:
                error_message = response.error.message
                return render_template("login.html", error_message=error_message)

            if hasattr(response, 'user') and not response.user:
                return render_template("login.html", error_message="Login failed. No user returned.")

            user = response.user
            user_id = user.id

            session["user_id"] = user_id
            session["email"] = email

            # Check if profile already exists
            user_profile_response = supabase.table("users").select("*").eq("user_id", user_id).execute()
            user_profile = user_profile_response.data[0] if user_profile_response.data else {}

            if user_profile.get("food_preference") and user_profile.get("dietary_goal"):
                return redirect(url_for("generate_form"))
            else:
                return redirect(url_for("profile"))

        except Exception as e:
            return render_template("login.html", error_message=f"Login error: {str(e)}")

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session or "email" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    email = session["email"]

    if request.method == "POST":
        food_preference = request.form.get("food_preference")
        dietary_goal = request.form.get("dietary_goal")
        allergies = request.form.getlist("allergies")
        flavors = request.form.getlist("flavors")

        data = {
            "user_id": user_id,
            "email": email,
            "food_preference": food_preference,
            "dietary_goal": dietary_goal,
            "allergies": allergies,
            "flavor_profile": flavors
        }

        try:
            supabase.table("users").upsert(data).execute()
            return redirect(url_for("generate_form"))
        except Exception as e:
            return f"<h3>Error saving profile: {e}</h3>"

    user_response = supabase.table("users").select("*").eq("user_id", user_id).execute()
    user_profile = user_response.data[0] if user_response.data else {}

    return render_template("profile.html", profile=user_profile)

@app.route("/generate", methods=["GET"])
def generate_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("generate.html")

@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    ingredients = [i.strip().lower() for i in request.form.getlist("ingredients[]") if i.strip()]
    if not ingredients:
        return "<h3>Error: Please provide at least one ingredient.</h3>"

    tools = request.form.getlist("tools")
    time = int(request.form.get("time", 0))
    skill = request.form.get("skill", "Beginner")

    response = supabase.table("users").select("*").eq("user_id", session['user_id']).execute()
    if not response.data:
        return "No user profile found."

    user = response.data[0]

    user_profile = {
        "food_preference": user.get("food_preference", ""),
        "dietary_goal": user.get("dietary_goal", ""),
        "allergies": user.get("allergies", []),
        "flavor_profile": user.get("flavor_profile", []),
        "ingredients": ingredients,
        "tools": tools,
        "time": time,
        "skill": skill,
        "chef_mode": request.form.get("chef_mode", "Quick & Easy")
    }

    try:
        from recommend import recommend_recipes
        recipes = recommend_recipes(user_profile)
        return render_template("recipes.html", recipes=recipes)
    except Exception as e:
        flash(f"Error generating recipes: {e}", "danger")
        return redirect(url_for("generate_form"))


@app.route('/recipe_detail/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = next((r for r in RECIPES if r["id"] == recipe_id), None)

    if not recipe:
        return render_template("404.html"), 404

    return render_template("recipe_detail.html", recipe=recipe)


@app.route("/save_favorite", methods=["POST"])
def save_favorite():
    recipe_id = request.form.get("recipe_id")
    title = request.form.get("title")
    image = request.form.get("image")

    try:
        data = {
            "recipe_id": recipe_id,
            "title": title,
            "image": image,
            "user_id": session['user_id']
        }
        supabase.table("favorites").insert(data).execute()
        flash("Recipe saved to favorites!", "success")
        return redirect(url_for("favorites"))
    except Exception as e:
        flash(f"Error saving favorite: {e}", "danger")
        return redirect(url_for("generate_form"))


@app.route("/favorites")
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        response = supabase.table("favorites").select("*").eq("user_id", session['user_id']).execute()
        recipes = response.data
        return render_template("favorites.html", recipes=recipes)
    except Exception as e:
        flash(f"Error fetching favorites: {e}", "danger")
        return redirect(url_for("generate_html"))


@app.route("/remove_favorite/<int:id>", methods=["POST"])
def remove_favorite(id):
    try:
        supabase.table("favorites").delete().eq("id", id).execute()
        flash("Favorite removed successfully!", "success")
        return redirect(url_for("favorites"))
    except Exception as e:
        flash(f"Error removing favorite: {e}", "danger")
        return redirect(url_for("favorites"))

from flask import request, jsonify
import requests
import json

import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Load recipes.json once at startup
with open("recipes.json", "r", encoding="utf-8") as f:
    all_recipes = json.load(f)

# Helper to find recipe by ID
def get_recipe_by_id(recipe_id):
    return next((r for r in all_recipes if str(r.get("id")) == str(recipe_id)), None)

@app.route("/ask_assistant", methods=["POST"])
def ask_assistant():
    data = request.get_json()
    question = data.get("question")
    recipe_id = data.get("recipe_id")

    if not question or not recipe_id:
        return jsonify({"response": "Missing question or recipe ID."}), 400

    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({"response": "Recipe not found."}), 404

    # Format recipe without extra headers
    formatted = (
        f"Title: {recipe.get('name')}\n"
        f"Ingredients: {', '.join(recipe.get('ingredients', []))}\n"
        f"Instructions: {' '.join(recipe.get('instructions', []))}"
    )

    prompt = (
        f"You are a cooking assistant. The user is viewing the following recipe:\n\n"
        f"{formatted}\n\n"
        f"The user asked: '{question}'. "
        f"Answer using only what's relevant from the recipe. "
        f"Do not say 'Ingredients:' or 'Instructions:' in your response."
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            json={"model": "llama2", "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        result = response.json()
        reply = result.get("response", "Sorry, I don't have the answer.")
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"response": f"There was an error talking to the assistant: {str(e)}"}), 500

CORS(app)  # Add this to allow JS frontend to talk to Flask if needed

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question')
    recipe = data.get('recipe')

    if not recipe or not question:
        return jsonify({'response': "Missing recipe or question."}), 400

    response = generate_answer(question, recipe)
    return jsonify({'response': response})

def generate_answer(question, recipe):
    question = question.lower()

    ingredients = recipe.get('ingredients', '')
    instructions = recipe.get('instructions', '')
    title = recipe.get('title') or recipe.get('name', '')

    if 'ingredient' in question:
        return ', '.join(ingredients) if isinstance(ingredients, list) else ingredients
    elif 'how to' in question or 'cook' in question or 'make' in question:
        return ' '.join(instructions) if isinstance(instructions, list) else instructions
    elif 'name' in question or 'what is this' in question:
        return f"This recipe is called {title}."
    else:
        return "I'm not sure, but I can help with ingredients or how to make it!"


if __name__ == "__main__":
    app.run(debug=True)
