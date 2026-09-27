# Queen's Lards

A small family memory-sharing site: a landing page, sign-up/login, a home
feed for photos and stories, a people list, and profile pictures.

## Files

- `app.py` — the Python/Flask backend (routes, form validation, sessions)
- `templates/` — the HTML pages (Jinja templates)
- `static/style.css` — all the styling, in one shared file
- `static/uploads/` — where uploaded profile pictures get saved
- `requirements.txt`, `Procfile` — needed to deploy it (see below)

## Running it on your own computer

You need Python 3 installed. Then, in this folder:

```
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Putting it on GitHub

Putting the code on GitHub is just step one — GitHub stores the files, it
doesn't run them. For your family to actually open the site in their
browser, you need to deploy it to a service that runs Python apps. GitHub
Pages won't work here since it only serves static HTML, not a Flask app.

## Deploying it for free (Render)

1. Push this folder to a GitHub repository.
2. Go to [render.com](https://render.com) and sign up (you can sign in with
   GitHub).
3. Click **New +** → **Web Service**, then pick your repository.
4. Render should auto-detect the settings from `requirements.txt` and
   `Procfile`. If asked:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
5. Click **Create Web Service**. After a couple of minutes it'll give you a
   public link like `https://queens-lards.onrender.com` — that's what you
   share with your family.

(PythonAnywhere and Railway work the same way in spirit: connect the repo,
point it at `app.py`, and they run it for you.)

## Before you share the link with family

- **Change `app.secret_key`** in `app.py` to a long, random, private string
  — right now it's a placeholder anyone reading the code could see.
- **Accounts, posts, and the people list are stored in memory**, not in a
  real database. That means:
  - Everything resets whenever the server restarts.
  - Render's free tier spins the server down after periods of no traffic
    and restarts it on the next visit — so on the free tier, expect data to
    disappear from time to time. Fine for showing family a working preview;
    not fine for something you want to keep long-term.
  - When you're ready to make it permanent, swap the `users`, `posts`, and
    `people` in-memory lists/dicts in `app.py` for a real database (SQLite
    is the easiest first step and works well on Render).
- The "forgot password" page is still a placeholder — it doesn't send real
  emails yet.
