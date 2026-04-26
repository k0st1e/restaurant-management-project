# Savory Haven - Flask Restaurant Website

## Features
- User registration and login
- Customer reviews (authenticated users can post)
- Restaurant menu page
- Blog page
- Contact page with embedded Google Map
- Responsive navbar and footer
- SQLite database with seed data
- Bundled placeholder images

## Run locally
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Then open: http://127.0.0.1:5000

## Notes
- Change `SECRET_KEY` in `app.py` before production.
- The database is automatically created on first run.
