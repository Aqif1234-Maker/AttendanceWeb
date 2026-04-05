# SmartAttendance Web

SmartAttendance Web is a Flask-based attendance management system with separate Teacher and Student portals. Teachers manage students, mark attendance, approve student accounts, and generate reports. Students can view their attendance history and summary stats.

## Tech Stack
- Python 3.11+
- Flask 3.x, Flask-Login, Flask-SQLAlchemy, Flask-Migrate
- MySQL (PyMySQL)
- Bootstrap 5 Darkly (Bootswatch)
- Chart.js

## Setup
1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and update the values.
3. Create the MySQL database and run the schema in `migrations/schema.sql`.
4. Run the app locally:
   ```bash
   python run.py
   ```

## Deployment (Railway)
1. Push code to GitHub.
2. Create a new project on Railway.app.
3. Add a MySQL plugin inside Railway.
4. Set environment variables: `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=production`.
5. Railway auto-detects Python via Nixpacks and runs the Procfile.
6. Run `migrations/schema.sql` on the Railway MySQL instance via Railway's query tab or a DB client like TablePlus.
