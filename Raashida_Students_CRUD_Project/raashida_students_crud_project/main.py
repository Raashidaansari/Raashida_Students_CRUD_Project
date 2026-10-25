from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import os
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "students.db")))


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Student Database CRUD API",
    description="A student record management API built with FastAPI and SQLite for the EWB Edu Tech internship assignment.",
    version="1.0.0",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    date_of_birth: date
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: date = Field(default_factory=date.today)


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None


def row_to_dict(row):
    return dict(row) if row else None


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return HTMLResponse(r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student Record Manager</title><style>
:root{font-family:Arial,sans-serif;color:#182230;background:#f4f7fb}body{margin:0}.hero{background:linear-gradient(120deg,#123b72,#2877b8);color:white;padding:28px 18px}.wrap{max-width:1050px;margin:auto;padding:20px}.hero h1{margin:0 0 8px}.hero p{margin:0;color:#e7f1ff}.card{background:white;border-radius:14px;padding:20px;margin:16px 0;box-shadow:0 5px 20px #183b6510}h2{margin-top:0;color:#164477}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}label{font-size:13px;font-weight:bold;display:block;margin-bottom:5px}input{box-sizing:border-box;width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:8px}button,.linkbtn{background:#1769aa;color:white;border:0;border-radius:8px;padding:10px 14px;cursor:pointer;text-decoration:none;display:inline-block;margin:6px 4px 0 0}button.secondary{background:#536579}button.danger{background:#b42318}.status{padding:10px;border-radius:8px;background:#eef6ff;margin:10px 0;display:none}.tablewrap{overflow:auto}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #e5eaf0;font-size:14px}th{background:#f0f5fa}.muted{color:#526173;font-size:13px}.actions button{margin:2px}.toplinks{margin-top:12px}.toplinks a{color:white;margin-right:14px}@media(max-width:550px){.wrap{padding:12px}.card{padding:14px}}
</style></head><body><header class="hero"><div class="wrap"><h1>Student Record Manager</h1><p>Internship Project · Python + FastAPI + SQLite</p><div class="toplinks"><a href="/docs" target="_blank">Interactive API Docs</a><a href="/health" target="_blank">Health Check</a></div></div></header>
<main class="wrap"><section class="card"><h2 id="formTitle">Add a Student</h2><div id="status" class="status"></div><form id="studentForm"><input type="hidden" id="editId"><div class="grid">
<div><label for="name">Full name *</label><input id="name" required minlength="2" maxlength="100" placeholder="Example: Asha Kumar"></div>
<div><label for="dob">Date of birth *</label><input id="dob" type="date" required></div>
<div><label for="email">Email *</label><input id="email" type="email" required placeholder="asha@example.com"></div>
<div><label for="phone">Phone</label><input id="phone" maxlength="30" placeholder="Optional"></div>
<div><label for="course">Course</label><input id="course" maxlength="100" placeholder="Example: MCA"></div>
<div><label for="enrollment">Enrollment date</label><input id="enrollment" type="date"></div>
<div style="grid-column:1/-1"><label for="address">Address</label><input id="address" maxlength="250" placeholder="Optional; use dummy data for demonstrations"></div>
</div><button type="submit" id="saveBtn">Save Student</button><button type="button" class="secondary" onclick="resetForm()">Clear</button></form></section>
<section class="card"><h2>Student Records</h2><p class="muted">Search by name, email, or course. Use dummy records only for public demos.</p><div class="grid"><div><label for="search">Search records</label><input id="search" placeholder="Type a name, email, or course"></div><div style="align-self:end"><button onclick="loadStudents()">Refresh Records</button><a class="linkbtn" href="/docs" target="_blank">Open API Docs</a></div></div><div class="tablewrap"><table><thead><tr><th>ID</th><th>Name</th><th>Date of Birth</th><th>Email</th><th>Phone</th><th>Course</th><th>Actions</th></tr></thead><tbody id="rows"><tr><td colspan="7">Loading records…</td></tr></tbody></table></div></section>
<section class="card"><h2>About this project</h2><p>This application demonstrates Create, Read, Update, and Delete (CRUD) operations using FastAPI and SQLite. The API documentation is available at <code>/docs</code>.</p></section></main>
<script>
const $=id=>document.getElementById(id); let records=[];
function showStatus(message, bad=false){const el=$('status');el.textContent=message;el.style.display='block';el.style.background=bad?'#fff0ef':'#eef6ff';el.style.color=bad?'#9f1c13':'#164477';}
function resetForm(){$('studentForm').reset();$('editId').value='';$('formTitle').textContent='Add a Student';$('saveBtn').textContent='Save Student';$('enrollment').value=new Date().toISOString().slice(0,10);}
async function loadStudents(){try{const q=$('search').value.trim();const url=q?'/students?search='+encodeURIComponent(q):'/students';const res=await fetch(url);const data=await res.json();if(!res.ok)throw new Error(data.detail||'Could not load records');records=data;renderRows();}catch(e){$('rows').innerHTML='<tr><td colspan="7">Unable to load records: '+escapeHtml(e.message)+'</td></tr>';}}
function escapeHtml(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function renderRows(){if(!records.length){$('rows').innerHTML='<tr><td colspan="7">No records found. Add a student above.</td></tr>';return;} $('rows').innerHTML=records.map(s=>`<tr><td>${s.id}</td><td>${escapeHtml(s.name)}</td><td>${escapeHtml(s.date_of_birth)}</td><td>${escapeHtml(s.email)}</td><td>${escapeHtml(s.phone||'—')}</td><td>${escapeHtml(s.course||'—')}</td><td class="actions"><button class="secondary" onclick="editStudent(${s.id})">Edit</button><button class="danger" onclick="deleteStudent(${s.id})">Delete</button></td></tr>`).join('');}
$('studentForm').addEventListener('submit',async e=>{e.preventDefault();const id=$('editId').value;const body={name:$('name').value.trim(),date_of_birth:$('dob').value,email:$('email').value.trim(),phone:$('phone').value.trim()||null,course:$('course').value.trim()||null,address:$('address').value.trim()||null,enrollment_date:$('enrollment').value||new Date().toISOString().slice(0,10)};try{const res=await fetch(id?'/students/'+id:'/students',{method:id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await res.json();if(!res.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail));showStatus(id?'Student updated successfully.':'Student added successfully.');resetForm();await loadStudents();}catch(err){showStatus(err.message,true);}});
function editStudent(id){const s=records.find(x=>x.id===id);if(!s)return;$('editId').value=s.id;$('name').value=s.name;$('dob').value=s.date_of_birth;$('email').value=s.email;$('phone').value=s.phone||'';$('course').value=s.course||'';$('address').value=s.address||'';$('enrollment').value=s.enrollment_date||'';$('formTitle').textContent='Edit Student #'+id;$('saveBtn').textContent='Update Student';window.scrollTo({top:0,behavior:'smooth'});}
async function deleteStudent(id){if(!confirm('Delete student record #'+id+'? This cannot be undone.'))return;try{const res=await fetch('/students/'+id,{method:'DELETE'});if(!res.ok){const data=await res.json();throw new Error(data.detail||'Delete failed');}showStatus('Student record deleted.');await loadStudents();}catch(e){showStatus(e.message,true);}}
$('search').addEventListener('input',()=>{clearTimeout(window.searchTimer);window.searchTimer=setTimeout(loadStudents,250);});$('enrollment').value=new Date().toISOString().slice(0,10);loadStudents();
</script></body></html>''')


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Student Record Manager"}


@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO students (name, date_of_birth, email, phone, course, address, enrollment_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (student.name.strip(), student.date_of_birth.isoformat(), str(student.email).lower(),
                 student.phone, student.course, student.address, student.enrollment_date.isoformat()),
            )
            row = conn.execute("SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as exc:
        if "email" in str(exc).lower():
            raise HTTPException(status_code=409, detail="A student with this email already exists.")
        raise HTTPException(status_code=400, detail="Could not create student record.")


@app.get("/students")
def list_students(search: Optional[str] = Query(default=None, description="Filter by name, email, or course")):
    with get_connection() as conn:
        if search and search.strip():
            term = f"%{search.strip()}%"
            rows = conn.execute(
                """SELECT * FROM students WHERE name LIKE ? OR email LIKE ? OR course LIKE ? ORDER BY id DESC""",
                (term, term, term),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
        return [row_to_dict(row) for row in rows]


@app.get("/students/{student_id}")
def get_student(student_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found.")
    return row_to_dict(row)


@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    updates = student.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update.")
    for field in ("date_of_birth", "enrollment_date"):
        if updates.get(field) is not None:
            updates[field] = updates[field].isoformat()
    if updates.get("email") is not None:
        updates["email"] = str(updates["email"]).lower()
    if updates.get("name") is not None:
        updates["name"] = updates["name"].strip()
    allowed = {"name", "date_of_birth", "email", "phone", "course", "address", "enrollment_date"}
    updates = {k: v for k, v in updates.items() if k in allowed}
    try:
        with get_connection() as conn:
            existing = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Student not found.")
            set_clause = ", ".join(f"{key} = ?" for key in updates)
            conn.execute(f"UPDATE students SET {set_clause} WHERE id = ?", [*updates.values(), student_id])
            row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as exc:
        if "email" in str(exc).lower():
            raise HTTPException(status_code=409, detail="A student with this email already exists.")
        raise HTTPException(status_code=400, detail="Could not update student record.")


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found.")
    return {"message": "Student deleted successfully.", "student_id": student_id}
