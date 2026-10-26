# SmartAttendance System

A Flask-based Smart Attendance System designed to simplify student attendance management through voice-based attendance marking, student record management, attendance reports, and syllabus tracking.

## Features

- **User Authentication:** Login and registration functionality.
- **Voice-Based Attendance:** Uses speech recognition to support attendance marking.
- **Student Management:** Manage student records.
- **Attendance Management:** Record and manage student attendance.
- **Attendance Reports:** Generate and view attendance reports.
- **Syllabus Tracker:** Track syllabus progress.
- **Web Interface:** User interface built with HTML, CSS, and JavaScript.

## Technologies Used

- **Python:** Core programming language.
- **Flask:** Backend web framework.
- **Faster-Whisper:** Speech-to-text transcription.
- **HTML:** Web page structure.
- **CSS:** Styling and layout.
- **JavaScript:** Frontend interactions.

## Project Structure

```text
smart_attendace_final/
├── app.py
├── config.py
├── database.py
├── models.py
├── auth_routes.py
├── attendance_routes.py
├── report_routes.py
├── student_routes.py
├── syllabus_routes.py
├── requirements.txt
├── .env.example
├── .gitignore
├── services/
│   ├── __init__.py
│   ├── attendance_service.py
│   ├── report_service.py
│   └── speech_service.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── attendance.js
├── templates/
├── test/
└── readme.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/JanhaviGavhane/smart_attendance.git
cd smart_attendance
```

### 2. Create a Virtual Environment

For Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Review the `.env.example` file and configure the environment variables required by the application.

Create a local `.env` file if required by your configuration.

### 5. Run the Application

```bash
python app.py
```

Open the local address displayed in the terminal in your web browser.