# GreenBite

A **smart recipe generator**. Enter the ingredients you have at home and GreenBite recommends recipes that match, lets you save favourites, and answers questions about a recipe through a built-in assistant.

## Features

- **Ingredient-based recommendations**: recipes are ranked by how closely they match your ingredients, using TF-IDF vectors and cosine similarity (scikit-learn)
- **Accounts**: sign up, log in and manage a profile (Supabase)
- **Favourites**: save and remove recipes
- **Recipe details** with images, ingredients and step-by-step instructions
- **Recipe assistant**: ask questions about the recipe you are viewing
- Large recipe dataset with pre-computed vectors for fast lookups

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask, Flask-CORS |
| Recommendation | pandas, scikit-learn (TF-IDF + cosine similarity) |
| Auth and storage | Supabase |
| Frontend | HTML templates, CSS, JavaScript |

## Project structure

```
smart-recipe-generator/
  app.py                 Flask app and routes
  recommend.py           Recipe recommendation logic
  preprocess.py          Dataset cleaning
  vectorize_recipes.py   Builds the TF-IDF vectors
  dataset.csv            Recipe dataset (titles, ingredients, instructions)
  model/                 Saved vectorizer and recipe vectors (.pkl)
  data/                  recipes.json, users.json
  templates/             HTML pages
  static/                Recipe images
```

## Getting started

```bash
cd smart-recipe-generator
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
pip install pandas scikit-learn flask-cors requests
python app.py
```

Then open <http://127.0.0.1:5000>.

### Supabase

The app uses Supabase for accounts and favourites. Create your own Supabase project and put its URL and key in `supabase_config.py`. Prefer reading them from environment variables (`python-dotenv` is already a dependency) so keys are never committed.

### Rebuilding the model

`preprocess.py` cleans the dataset and `vectorize_recipes.py` builds the TF-IDF vectors saved in `model/`. Re-run them after changing `dataset.csv`.

## Main routes

| Route | Purpose |
|-------|---------|
| `/` | Home page |
| `/signup`, `/login`, `/profile` | Accounts |
| `/generate`, `/generate_recipe` | Enter ingredients and get recommendations |
| `/recipe_detail/<id>` | Recipe page |
| `/favorites`, `/save_favorite`, `/remove_favorite/<id>` | Favourites |
| `/ask_assistant`, `/chat` | Recipe assistant |
