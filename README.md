# Medislot — Online Doctor Appointment Form

A Flask web app for booking doctor appointments, storing them in a SQLite
database, and viewing them through an admin login-protected dashboard.

## Run it locally

```bash
cd medislot
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

- Patient form: `/`
- Admin login: `/admin/login`
- Admin dashboard (appointments table): `/admin/dashboard`

## Demo admin credentials

- Username: `admin`
- Password: `admin123`

Change `ADMIN_USERNAME` and `ADMIN_PASSWORD` near the top of `app.py` before
using this anywhere beyond your own machine.

## What's inside

- `app.py` — Flask routes, SQLite setup (`medislot.db`, created automatically
  on first run), form handling, and login/session logic.
- `templates/` — `index.html` (booking form), `admin_login.html`,
  `admin_dashboard.html`, `base.html` (shared layout + flash messages).
- `static/style.css` — smooth blue themed styling.
- `uploads/` — where uploaded medical reports are saved.

## Notes

- This is a development setup (`app.run(debug=True)`). For real deployment,
  use a production server (e.g. gunicorn) and set a strong, secret
  `app.secret_key`, plus a real admin password.
- The appointments table lives in `medislot.db`, a single-file SQLite
  database — open it with any SQLite browser if you want to inspect the raw
  data directly.
