# 🚀 SmartAttendance Web — Full Codex Build Prompt

## OVERVIEW
You are building **SmartAttendance Web** — a full-stack Flask web application that replicates and extends a Tkinter desktop attendance system. The app must be production-ready, mobile-responsive, and deployable to Railway.app or Render.com for free.

The final app must have **two completely separate portals**: a **Teacher Portal** and a **Student Portal**, accessible from a single landing page.

---

## TECH STACK
- **Backend:** Python 3.11+, Flask 3.x, Flask-Login, Flask-SQLAlchemy, Flask-WTF, Flask-Migrate
- **Database:** MySQL (use PyMySQL driver: `mysql+pymysql://`)
- **Frontend:** Jinja2 templates + Bootstrap 5 (dark theme via `bootstrap-darkly` from Bootswatch CDN) + vanilla JS
- **Charts:** Chart.js (CDN)
- **Export:** openpyxl (Excel export)
- **Auth:** Werkzeug password hashing (pbkdf2:sha256), Flask-Login sessions
- **Deployment:** Gunicorn, Procfile, railway.json

---

## DATABASE SCHEMA
Write the complete SQL in `migrations/schema.sql`. Tables:

```sql
CREATE TABLE teachers (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    full_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    roll_number VARCHAR(50)  NOT NULL UNIQUE,
    class       VARCHAR(20)  NOT NULL,
    section     VARCHAR(10)  NOT NULL,
    contact     VARCHAR(20),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_accounts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT,
    name        VARCHAR(100) NOT NULL,
    roll_number VARCHAR(50)  NOT NULL UNIQUE,
    class       VARCHAR(20)  NOT NULL,
    section     VARCHAR(10)  NOT NULL,
    contact     VARCHAR(20),
    password    VARCHAR(255) NOT NULL,
    approved    TINYINT(1)   DEFAULT 0,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);

CREATE TABLE attendance (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date       DATE NOT NULL,
    status     ENUM('Present','Absent','Late') NOT NULL,
    marked_by  INT,
    UNIQUE KEY unique_attendance (student_id, date),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by)  REFERENCES teachers(id) ON DELETE SET NULL
);
```

---

## FOLDER STRUCTURE (already created — fill every file)

```
SmartAttendanceWeb/
├── run.py                          # App entry point
├── config.py                       # Config classes (Dev, Prod)
├── requirements.txt                # All pip dependencies
├── .env.example                    # Environment variable template
├── Procfile                        # For Railway/Render: web: gunicorn run:app
├── railway.json                    # Railway deploy config
├── migrations/
│   └── schema.sql                  # Full DB schema (above)
└── app/
    ├── __init__.py                 # create_app() factory
    ├── models/
    │   ├── __init__.py
    │   ├── teacher.py              # Teacher SQLAlchemy model + UserMixin
    │   ├── student.py              # Student + StudentAccount models
    │   └── attendance.py           # Attendance model
    ├── routes/
    │   ├── __init__.py
    │   ├── auth.py                 # /login /signup /logout for both teacher & student
    │   ├── teacher.py              # All teacher dashboard routes
    │   ├── student.py              # All student portal routes
    │   └── api.py                  # JSON API endpoints for AJAX (attendance, charts)
    ├── static/
    │   ├── css/main.css            # Custom overrides on top of Bootstrap dark
    │   ├── js/main.js              # Global JS utilities
    │   ├── js/attendance.js        # Attendance marking page JS
    │   └── js/charts.js            # Chart.js dashboard charts
    └── templates/
        ├── base.html               # Master layout with navbar, sidebar, flash messages
        ├── auth/
        │   ├── landing.html        # Landing page: two portals side by side
        │   ├── teacher_login.html
        │   ├── teacher_signup.html
        │   ├── student_login.html
        │   └── student_signup.html
        ├── teacher/
        │   ├── dashboard.html      # Stats cards + section filter + recent table + charts
        │   ├── students.html       # Add/Edit/Delete/Search students table
        │   ├── attendance.html     # Mark attendance: select class+section+date → radio list
        │   ├── reports.html        # Filter + table + Excel export + bar chart
        │   └── approvals.html      # Approve/reject pending student account registrations
        └── student/
            └── dashboard.html      # Student sees own attendance record + summary stats
```

---

## FEATURE REQUIREMENTS — implement ALL of these exactly

### 🔐 AUTH SYSTEM

**Teacher Auth** (`/teacher/login`, `/teacher/signup`, `/teacher/logout`):
- Signup: full_name, email, password (min 6 chars), confirm_password
- Login: email + password
- Hash passwords with `werkzeug.security.generate_password_hash` / `check_password_hash`
- After login → redirect to `/teacher/dashboard`
- Flask-Login `current_user` for session management

**Student Auth** (`/student/login`, `/student/signup`, `/student/logout`):
- Signup: full_name, roll_number, class, section, contact, password, confirm_password
- Student account starts with `approved = 0` — cannot login until teacher approves
- Login: roll_number + password (only works if `approved = 1`)
- Show clear message "Your account is pending teacher approval" if approved=0
- After login → redirect to `/student/dashboard`

**Landing Page** (`/`):
- Two side-by-side cards: "Teacher Portal" and "Student Portal"
- Each card has Login and Sign Up buttons
- Dark theme, centered, logo at top

---

### 👩‍🏫 TEACHER PORTAL

#### Dashboard (`/teacher/dashboard`)
- **4 stat cards (overall):** Total Students | Today Present | Today Absent | Attendance %
- **Section filter dropdown:** populated from DB (all distinct class+section combos). On change (AJAX), updates section-specific stat cards below without page reload.
- **4 section stat cards:** same metrics but for selected class+section
- **Recent attendance table:** last 10 records across all students (name, class, section, date, status). Filters by section if one is selected.
- **Bar chart** (Chart.js): Present vs Absent vs Late counts for today

#### Student Management (`/teacher/students`)
- **Add student form:** name, roll_number, class (dropdown 1–12), section (dropdown A–D), contact
- **Students table:** sortable, searchable (live search via JS filtering). Columns: ID | Name | Roll No | Class | Section | Contact | Actions
- **Edit:** click row → form pre-fills → update button
- **Delete:** confirmation dialog before deleting
- Inline flash messages for success/error

#### Attendance Marking (`/teacher/attendance`)
- **Filters:** Class (dropdown 1–12), Section (dropdown A–D), Date (date picker, default today)
- **Load Students button:** fetches students via AJAX, renders list dynamically
- **Per-student radio buttons:** Present (green) | Absent (red) | Late (yellow)
- **Select All Present / Select All Absent** buttons for quick marking
- **Submit button:** POST all attendance data at once, show success toast

#### Reports (`/teacher/reports`)
- **Filter bar:** student name (text), class (text), date from, date to
- **Generate button:** fetches filtered data, populates table
- **Table columns:** Name | Roll No | Class | Section | Date | Status
- **Export to Excel button:** downloads `.xlsx` file using openpyxl
- **Bar chart** (Chart.js): Present vs Absent vs Late count for filtered data, rendered inline below table

#### Student Approvals (`/teacher/approvals`)
- Table of all pending student account registrations (approved=0)
- Columns: Name | Roll No | Class | Section | Contact | Registered At | Actions
- **Approve button** (green): sets approved=1, shows success flash
- **Reject/Delete button** (red): deletes the account request
- Badge on sidebar nav showing count of pending approvals

---

### 🎓 STUDENT PORTAL

#### Dashboard (`/student/dashboard`)
- **Welcome header** with student name
- **3 info cards:** Roll Number | Class | Section
- **Attendance summary row:** Total Days | Present | Absent | Late | Attendance %
- **Full attendance table:** Date | Status (color-coded: green=Present, red=Absent, yellow=Late)
- Student can only see their own attendance records

---

## UI / DESIGN REQUIREMENTS

- **Theme:** Bootstrap 5 Darkly (Bootswatch) — import via CDN in base.html
- **Color palette:**
  - Background: `#1a1a2e` / `#16213e`
  - Accent blue (teacher): `#17a2b8` (Bootstrap info)
  - Accent green (student): `#28a745` (Bootstrap success)
  - Cards: `#0f3460` or Bootstrap's `bg-dark`
- **Sidebar** (teacher portal only): fixed left sidebar, 220px wide, dark background, nav links with icons, teacher name badge, logout at bottom, version at very bottom
- **Navbar** (student portal): top navbar with student name and logout
- **Flash messages:** Bootstrap alerts, auto-dismiss after 4 seconds via JS
- **Mobile responsive:** sidebar collapses to hamburger menu on small screens
- **Icons:** use Bootstrap Icons (CDN) throughout — dashboard, students, attendance, reports, logout, etc.
- **Modals:** use Bootstrap modals for delete confirmations
- **Toast notifications:** Bootstrap toasts for success/error in attendance submission

---

## API ENDPOINTS (JSON — for AJAX)

```
GET  /api/students?class=10&section=A        → list of students for attendance page
GET  /api/section-stats?class=10&section=A   → {total, present, absent, percent}
GET  /api/chart-data                         → {present, absent, late} counts for today
POST /api/attendance                         → submit {student_id: status} dict, returns {saved: N}
GET  /api/report-chart?...filters...         → chart data for report page
```

All API routes require `@login_required` and return JSON.

---

## config.py — write these classes

```python
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-this')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/smart_attendance')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Set on Railway/Render

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig
}
```

---

## requirements.txt — include exactly

```
Flask==3.0.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-WTF==1.2.1
PyMySQL==1.1.1
python-dotenv==1.0.1
openpyxl==3.1.5
gunicorn==22.0.0
Werkzeug==3.0.3
WTForms==3.1.2
cryptography==42.0.8
```

---

## .env.example

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@host:port/dbname
FLASK_ENV=development
```

---

## Procfile

```
web: gunicorn run:app
```

---

## railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "gunicorn run:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## run.py

```python
from app import create_app
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

---

## IMPORTANT IMPLEMENTATION NOTES

1. **Two separate UserMixin classes** — Teacher and Student cannot share a Flask-Login loader. Use a `login_manager.user_loader` that checks a session variable `user_type` to decide which model to query.

2. **Separate `@login_required` decorators** — create `teacher_required` and `student_required` decorators that check `session['user_type']` and redirect appropriately.

3. **Attendance is keyed on `(student_id, date)`** — use `INSERT ... ON DUPLICATE KEY UPDATE` or SQLAlchemy `merge()` so re-submitting attendance on the same day updates instead of errors.

4. **The `students` table and `student_accounts` table are separate** — teachers manually add students to `students`. Students self-register via `student_accounts`. When a teacher approves a `student_account`, optionally link it to the matching `students` row by roll_number.

5. **Excel export** — use `openpyxl`, stream the file with `send_file` using `io.BytesIO`, set mimetype to `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.

6. **AJAX for attendance page** — when teacher clicks "Load Students", fetch `/api/students?class=X&section=Y` and render the radio-button list dynamically in JS. On submit, POST JSON to `/api/attendance`.

7. **Section filter on dashboard** — use `fetch('/api/section-stats?class=X&section=Y')` to update stat cards without reload. Use `fetch('/api/recent-attendance?class=X&section=Y')` to update the table.

8. **Chart.js** — render a bar chart on the dashboard and report page. Initialize charts after DOM load. On the reports page, destroy and re-render the chart each time a new report is generated.

9. **Pending approvals badge** — inject the pending count into the Jinja context using a `context_processor` so the sidebar always shows the live count.

10. **Flash messages** — use `flash(message, category)` where category maps to Bootstrap alert classes (success, danger, warning, info). Auto-dismiss with a small JS snippet.

---

## DEPLOYMENT STEPS (write in README.md)

1. Push code to GitHub
2. Create a new project on Railway.app
3. Add a MySQL plugin inside Railway
4. Set environment variables: `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=production`
5. Railway auto-detects Python via Nixpacks and runs the Procfile
6. Run `migrations/schema.sql` on the Railway MySQL instance via Railway's query tab or a DB client like TablePlus

---

## FINAL CHECKLIST — every item must be implemented

- [ ] Landing page with two portals
- [ ] Teacher signup / login / logout
- [ ] Student signup (pending approval) / login / logout
- [ ] Teacher dashboard with 4 overall stat cards
- [ ] Teacher dashboard section filter (AJAX, no reload)
- [ ] Teacher dashboard 4 section stat cards
- [ ] Teacher dashboard recent attendance table
- [ ] Teacher dashboard bar chart (Chart.js)
- [ ] Add / Edit / Delete students
- [ ] Live search on students table
- [ ] Mark attendance (class + section + date → radio list)
- [ ] Select All Present / Select All Absent
- [ ] Submit attendance via AJAX
- [ ] Reports with filters
- [ ] Export to Excel (.xlsx)
- [ ] Bar chart on reports page
- [ ] Student approvals page with approve/reject
- [ ] Pending approval badge on sidebar
- [ ] Student dashboard with own attendance table
- [ ] Student attendance summary stats
- [ ] Mobile-responsive sidebar
- [ ] Bootstrap 5 Darkly dark theme throughout
- [ ] Flash messages auto-dismiss
- [ ] Procfile + railway.json for deployment
- [ ] README with setup and deployment steps
