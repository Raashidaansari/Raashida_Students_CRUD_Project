# Student Record Manager — EWB Edu Tech Internship Project

A beginner-friendly student database CRUD application built with **Python, FastAPI, and SQLite**. It includes a simple browser interface and interactive API documentation.

## Features

- Create student records
- List and search students by name, email, or course
- Retrieve one student by ID
- Update student information
- Delete student records
- Input validation and duplicate-email handling
- SQLite database persistence in the local project folder
- Browser interface at `/` and Swagger API documentation at `/docs`

## Student fields

Required: name, date of birth, email. Optional: phone, course, address. Enrollment date defaults to today.

## Requirements

- Python 3.10 or newer
- Internet connection for installing dependencies

## Run locally on Windows

1. Extract the project ZIP.
2. Open the extracted folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

5. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run:

   ```cmd
   .venv\Scripts\activate.bat
   ```

6. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

7. Start the server:

   ```powershell
   uvicorn main:app --reload
   ```

8. Open `http://127.0.0.1:8000` for the browser interface or `http://127.0.0.1:8000/docs` for API testing.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List students; optional `?search=term` |
| GET | `/students/{student_id}` | Retrieve one student |
| PUT | `/students/{student_id}` | Update a student |
| DELETE | `/students/{student_id}` | Delete a student |
| GET | `/health` | Health check |

### Example request body

```json
{
  "name": "Shapnam Dazy",
  "date_of_birth": "2005-06-11",
  "email": "shapnam.demo@example.com",
  "phone": "9000000000",
  "course": "MCA",
  "address": "Demo address",
  "enrollment_date": "2026-10-22"
}
```

Use only dummy data for demonstrations. Do not upload real student personal information or secrets to a public repository.

## Deployment notes

The app can be deployed as a Python web service using a hosting provider that supports FastAPI. Set the start command to:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Set `DATABASE_PATH` to a path on a persistent disk if your hosting provider offers one and you want SQLite records to survive service restarts or redeployments. Some free hosting filesystems are temporary, so database records may reset. Test the deployed app after deployment.

## Technology stack

- Python
- FastAPI
- SQLite
- Pydantic
- HTML, CSS, and JavaScript (simple frontend)
