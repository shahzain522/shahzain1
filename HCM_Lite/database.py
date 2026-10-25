
import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime, date, time


DB_PATH = Path(__file__).parent / "hcm_lite.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                industry TEXT,
                company_size TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                UNIQUE (company_id, email)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                user_id INTEGER,
                employee_code TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                department TEXT,
                designation TEXT,
                hire_date TEXT,
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (company_id, employee_code),
                UNIQUE (company_id, email)
            )
        """)

        # Attendance Management
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                attendance_date TEXT NOT NULL,
                check_in TEXT,
                check_out TEXT,
                status TEXT NOT NULL DEFAULT 'Present'
                    CHECK (
                        status IN (
                            'Present', 'Late', 'Half Day', 'Absent'
                        )
                    ),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                UNIQUE (company_id, employee_id, attendance_date)
            )
        """)

        conn.commit()


def setup_complete():
    with get_connection() as conn:
        result = conn.execute(
            "SELECT COUNT(*) AS total FROM companies"
        ).fetchone()
        return result["total"] > 0


def create_company_and_admin(
    company_name,
    industry,
    company_size,
    admin_name,
    admin_email,
    admin_password
):
    if len(admin_password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    if len(admin_password.encode("utf-8")) > 72:
        raise ValueError("Password is too long.")

    password_hash = bcrypt.hashpw(
        admin_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM companies LIMIT 1"
        ).fetchone()

        if existing:
            raise ValueError("Company setup has already been completed.")

        cursor = conn.execute("""
            INSERT INTO companies (
                company_name, industry, company_size
            )
            VALUES (?, ?, ?)
        """, (company_name, industry, company_size))

        company_id = cursor.lastrowid

        conn.execute("""
            INSERT INTO users (
                company_id, email, password_hash, role
            )
            VALUES (?, ?, ?, 'Admin')
        """, (company_id, admin_email.strip().lower(), password_hash))

        conn.commit()
        return company_id



def verify_password(password, password_hash):
    try:
        if isinstance(password_hash, memoryview):
            password_hash = password_hash.tobytes()

        if isinstance(password_hash, str):
            password_hash = password_hash.encode("utf-8")

        if not isinstance(password_hash, bytes):
            return False

        if not password:
            return False

        password_bytes = password.encode("utf-8")

        if len(password_bytes) > 72:
            return False

        return bcrypt.checkpw(password_bytes, password_hash)

    except (ValueError, TypeError, AttributeError):
        return False



def get_company(company_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM companies WHERE id = ?",
            (company_id,)
        ).fetchone()


def count_users(company_id=None):
    with get_connection() as conn:
        if company_id is None:
            result = conn.execute(
                "SELECT COUNT(*) AS total FROM users"
            ).fetchone()
        else:
            result = conn.execute(
                "SELECT COUNT(*) AS total FROM users WHERE company_id = ?",
                (company_id,)
            ).fetchone()

        return result["total"]


def create_employee(
    company_id,
    employee_code,
    full_name,
    email,
    phone,
    department,
    designation,
    hire_date
):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO employees (
                company_id,
                employee_code,
                full_name,
                email,
                phone,
                department,
                designation,
                hire_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company_id,
            employee_code.strip(),
            full_name.strip(),
            email.strip().lower(),
            phone,
            department,
            designation,
            hire_date
        ))

        conn.commit()
        return cursor.lastrowid


def get_employees(company_id, search=""):
    with get_connection() as conn:
        if search.strip():
            term = f"%{search.strip()}%"
            return conn.execute("""
                SELECT * FROM employees
                WHERE company_id = ?
                  AND (
                      full_name LIKE ?
                      OR employee_code LIKE ?
                      OR email LIKE ?
                      OR department LIKE ?
                  )
                ORDER BY id DESC
            """, (company_id, term, term, term, term)).fetchall()

        return conn.execute("""
            SELECT * FROM employees
            WHERE company_id = ?
            ORDER BY id DESC
        """, (company_id,)).fetchall()


def count_employees(company_id, status=None):
    with get_connection() as conn:
        if status:
            result = conn.execute("""
                SELECT COUNT(*) AS total
                FROM employees
                WHERE company_id = ? AND status = ?
            """, (company_id, status)).fetchone()
        else:
            result = conn.execute("""
                SELECT COUNT(*) AS total
                FROM employees
                WHERE company_id = ?
            """, (company_id,)).fetchone()

        return result["total"]


def update_employee_status(company_id, employee_id, status):
    if status not in ("Active", "Inactive"):
        raise ValueError("Invalid employee status.")

    with get_connection() as conn:
        conn.execute("""
            UPDATE employees
            SET status = ?
            WHERE company_id = ? AND id = ?
        """, (status, company_id, employee_id))

        conn.commit()




def create_employee_login(company_id, employee_id, password):
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password is too long.")

    with get_connection() as conn:
        employee = conn.execute("""
            SELECT id, full_name, email, status, user_id
            FROM employees
            WHERE company_id = ? AND id = ?
        """, (company_id, employee_id)).fetchone()

        if employee is None:
            raise ValueError("Employee not found.")

        if employee["status"] != "Active":
            raise ValueError("Inactive employees cannot have a login.")

        if employee["user_id"] is not None:
            raise ValueError("This employee already has a login.")

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor = conn.execute("""
            INSERT INTO users (
                company_id, full_name, email,
                password_hash, role, is_active
            )
            VALUES (?, ?, ?, ?, 'Employee', 1)
        """, (
            company_id,
            employee["full_name"],
            employee["email"].strip().lower(),
            password_hash
        ))

        user_id = cursor.lastrowid

        conn.execute("""
            UPDATE employees
            SET user_id = ?
            WHERE company_id = ? AND id = ?
        """, (user_id, company_id, employee_id))

        conn.commit()
        return user_id


# ---------------- ATTENDANCE FUNCTIONS ----------------

def check_in_employee(company_id, employee_id):
    now = datetime.now()
    today = now.date().isoformat()
    current_time = now.strftime("%H:%M:%S")

    # 09:15 AM ke baad check-in Late hoga.
    grace_time = time(9, 15)
    status = "Late" if now.time() > grace_time else "Present"

    with get_connection() as conn:
        employee = conn.execute("""
            SELECT id, status
            FROM employees
            WHERE company_id = ? AND id = ?
        """, (company_id, employee_id)).fetchone()

        if employee is None:
            raise ValueError("Employee not found.")

        if employee["status"] != "Active":
            raise ValueError("Inactive employees cannot check in.")

        existing = conn.execute("""
            SELECT id, check_in
            FROM attendance
            WHERE company_id = ?
              AND employee_id = ?
              AND attendance_date = ?
        """, (company_id, employee_id, today)).fetchone()

        if existing and existing["check_in"]:
            raise ValueError("You have already checked in today.")

        if existing:
            conn.execute("""
                UPDATE attendance
                SET check_in = ?, status = ?
                WHERE id = ? AND company_id = ?
            """, (current_time, status, existing["id"], company_id))
        else:
            conn.execute("""
                INSERT INTO attendance (
                    company_id, employee_id, attendance_date,
                    check_in, status
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                company_id, employee_id, today, current_time, status
            ))

        conn.commit()

    return {
        "date": today,
        "check_in": current_time,
        "status": status
    }


def check_out_employee(company_id, employee_id):
    now = datetime.now()
    today = now.date().isoformat()
    current_time = now.strftime("%H:%M:%S")

    with get_connection() as conn:
        record = conn.execute("""
            SELECT id, check_in, check_out
            FROM attendance
            WHERE company_id = ?
              AND employee_id = ?
              AND attendance_date = ?
        """, (company_id, employee_id, today)).fetchone()

        if record is None or not record["check_in"]:
            raise ValueError("Check in before checking out.")

        if record["check_out"]:
            raise ValueError("You have already checked out today.")

        check_in_time = datetime.strptime(
            record["check_in"], "%H:%M:%S"
        ).time()

        check_in_dt = datetime.combine(now.date(), check_in_time)
        duration_hours = (
            datetime.combine(now.date(), now.time()) - check_in_dt
        ).total_seconds() / 3600

        current_status = conn.execute("""
            SELECT status FROM attendance WHERE id = ?
        """, (record["id"],)).fetchone()["status"]

        # 5 ghante se kam kaam hone par Half Day.
        if duration_hours < 5:
            new_status = "Half Day"
        else:
            new_status = current_status

        conn.execute("""
            UPDATE attendance
            SET check_out = ?, status = ?
            WHERE id = ? AND company_id = ?
        """, (current_time, new_status, record["id"], company_id))

        conn.commit()

    return {
        "date": today,
        "check_out": current_time,
        "duration_hours": round(duration_hours, 2),
        "status": new_status
    }


def get_employee_attendance(company_id, employee_id, limit=30):
    with get_connection() as conn:
        return conn.execute("""
            SELECT *
            FROM attendance
            WHERE company_id = ? AND employee_id = ?
            ORDER BY attendance_date DESC
            LIMIT ?
        """, (company_id, employee_id, limit)).fetchall()


def get_company_attendance(company_id, attendance_date=None):
    if attendance_date is None:
        attendance_date = date.today().isoformat()

    with get_connection() as conn:
        return conn.execute("""
            SELECT
                a.*,
                e.employee_code,
                e.full_name,
                e.department,
                e.designation
            FROM attendance AS a
            JOIN employees AS e
              ON e.id = a.employee_id
             AND e.company_id = a.company_id
            WHERE a.company_id = ?
              AND a.attendance_date = ?
            ORDER BY e.full_name
        """, (company_id, attendance_date)).fetchall()


def count_attendance(company_id, attendance_date=None, status=None):
    if attendance_date is None:
        attendance_date = date.today().isoformat()

    with get_connection() as conn:
        if status:
            result = conn.execute("""
                SELECT COUNT(*) AS total
                FROM attendance
                WHERE company_id = ?
                  AND attendance_date = ?
                  AND status = ?
            """, (company_id, attendance_date, status)).fetchone()
        else:
            result = conn.execute("""
                SELECT COUNT(*) AS total
                FROM attendance
                WHERE company_id = ?
                  AND attendance_date = ?
            """, (company_id, attendance_date)).fetchone()

        return result["total"]
