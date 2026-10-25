from face_attendance import (
    capture_face_samples,
    train_face_model,
    recognize_and_mark_attendance
)
from ai_chat import ask_gemini
import io
import os
from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

load_dotenv()
import re
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from database import (
    init_db, setup_complete, get_connection, verify_password,
    create_company_and_admin, get_company, count_users,
    create_employee, create_employee_login, get_employees,
    count_employees, update_employee_status, check_in_employee,
    check_out_employee, get_employee_attendance,
    get_company_attendance, count_attendance,
)

st.set_page_config(
    page_title="HCM Lite | Human Capital Management",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===== HCM LITE PREMIUM THEME =====
st.markdown("""
<style>
/* ===== MAIN BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #080F1E, #101B30, #0B1728);
    color: #E8EEF8;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* ===== HEADINGS ===== */
h1 {
    color: #F4F8FF !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2 {
    color: #5EEAD4 !important;
    font-weight: 750 !important;
    border-bottom: 1px solid #263B55;
    padding-bottom: 8px;
}

h3 {
    color: #93C5FD !important;
    font-weight: 700 !important;
}

/* ===== ALL BUTTON TEXT ===== */
.stButton > button,
.stButton > button *,
.stDownloadButton > button,
.stDownloadButton > button *,
.stFormSubmitButton > button,
.stFormSubmitButton > button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
    opacity: 1;
    visibility: visible;
}

/* ===== BUTTON DESIGN ===== */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #0F766E, #1D4ED8) !important;
    border: 1px solid #60A5FA !important;
    border-radius: 10px !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.18);
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #14B8A6, #3B82F6) !important;
    border-color: #5EEAD4 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(20, 184, 166, 0.25);
}

/* Disabled buttons */
.stButton > button:disabled,
.stDownloadButton > button:disabled,
.stFormSubmitButton > button:disabled {
    color: #CBD5E1 !important;
    -webkit-text-fill-color: #CBD5E1 !important;
    opacity: 0.65 !important;
}

/* ===== PREMIUM SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #080F1E 0%,
        #101D32 55%,
        #0D2033 100%
    ) !important;
    border-right: 1px solid #263B55;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

/* Sidebar headings */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #5EEAD4 !important;
    font-weight: 800 !important;
    border-bottom: none;
    letter-spacing: 0.3px;
}

/* Sidebar text */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #D8E4F2 !important;
}

/* Sidebar navigation buttons */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 43px;
    background: #13243A !important;
    color: #E8F0FC !important;
    -webkit-text-fill-color: #E8F0FC !important;
    border: 1px solid #263B55 !important;
    border-radius: 10px !important;
    text-align: left;
    padding: 0.65rem 0.85rem !important;
    margin-bottom: 5px;
    font-size: 14px;
    font-weight: 650 !important;
    box-shadow: none !important;
    transform: none;
}

section[data-testid="stSidebar"] .stButton > button * {
    color: #E8F0FC !important;
    -webkit-text-fill-color: #E8F0FC !important;
}

/* Sidebar hover */
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(90deg, #0F766E, #164E63) !important;
    border-color: #2DD4BF !important;
    transform: translateX(3px);
    box-shadow: 0 4px 12px rgba(13, 148, 136, 0.18) !important;
}

/* Sidebar radio navigation */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: #13243A;
    border: 1px solid #263B55;
    border-radius: 9px;
    padding: 9px 12px;
    margin-bottom: 5px;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #164E63;
    border-color: #2DD4BF;
}

/* Sidebar inputs */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: #111F33 !important;
    color: #FFFFFF !important;
    border: 1px solid #30445F !important;
    border-radius: 8px !important;
}

/* Sidebar dropdown */
section[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #111F33 !important;
    border-radius: 8px !important;
}

/* Sidebar separators */
section[data-testid="stSidebar"] hr {
    border-color: #2A405C !important;
    margin-top: 14px;
    margin-bottom: 14px;
}

/* ===== METRIC CARDS ===== */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #14243A, #101B2D);
    border: 1px solid #2A405C;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}

div[data-testid="stMetricLabel"] {
    color: #9FB3CC !important;
}

div[data-testid="stMetricValue"] {
    color: #5EEAD4 !important;
    font-weight: 800 !important;
}

/* ===== INPUT FIELDS ===== */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #111F33 !important;
    color: #FFFFFF !important;
    border: 1px solid #30445F !important;
    border-radius: 9px !important;
}

/* Input focus */
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #2DD4BF !important;
    box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.15);
}

/* ===== SELECT BOXES ===== */
.stSelectbox div[data-baseweb="select"] {
    background-color: #111F33 !important;
    border-radius: 9px !important;
}

/* ===== TABS ===== */
button[data-baseweb="tab"] {
    color: #CBD5E1 !important;
    font-weight: 650 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #5EEAD4 !important;
    border-bottom-color: #2DD4BF !important;
}

/* ===== FORMS & EXPANDERS ===== */
div[data-testid="stForm"],
div[data-testid="stExpander"] {
    background: #101D30;
    border: 1px solid #263B55;
    border-radius: 12px;
}

/* ===== DATA TABLES ===== */
div[data-testid="stDataFrame"] {
    border: 1px solid #2A405C;
    border-radius: 10px;
}

/* ===== DIVIDERS ===== */
hr {
    border-color: #263B55 !important;
}

/* ===== HIDE STREAMLIT BRANDING ===== */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.stApp {background:#0B1220;color:#E5EAF3}
[data-testid="stSidebar"] {background:#101A2B;border-right:1px solid #26364D}
h1,h2,h3 {color:#F0F5FF!important}
p,label,.stMarkdown {color:#D1D9E6}
div[data-testid="stMetric"] {background:#111C2F;border:1px solid #26364D;padding:16px;border-radius:12px}
div[data-testid="stForm"] {background:#101A2B;border:1px solid #26364D;padding:16px;border-radius:12px}
.stButton>button,.stFormSubmitButton>button {background:#14B8A6;color:#07131F;border:0;border-radius:8px;font-weight:700;min-height:40px}
.stButton>button:hover,.stFormSubmitButton>button:hover {background:#2DD4BF;color:#07131F}
hr {border-color:#26364D}
</style>
""", unsafe_allow_html=True)

init_db()

# Create additional tables without deleting existing data.
with get_connection() as conn:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        reason TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'Pending',
        decision_comment TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS salary_structures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL UNIQUE,
        basic_salary REAL NOT NULL DEFAULT 0,
        allowance REAL NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS payroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        payroll_month TEXT NOT NULL,
        gross_salary REAL NOT NULL,
        deductions REAL NOT NULL DEFAULT 0,
        net_salary REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Draft',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company_id, employee_id, payroll_month)
    );

    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        created_by TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        actor_email TEXT,
        action TEXT NOT NULL,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        UNIQUE(company_id, name)
    );

    CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS holidays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        holiday_date TEXT NOT NULL,
        name TEXT NOT NULL,
        UNIQUE(company_id, holiday_date)
    );

    CREATE TABLE IF NOT EXISTS leave_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        annual_quota INTEGER NOT NULL DEFAULT 12,
        UNIQUE(company_id, name)
    );

    CREATE TABLE IF NOT EXISTS tax_slabs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        minimum_salary REAL NOT NULL DEFAULT 0,
        maximum_salary REAL,
        tax_percent REAL NOT NULL DEFAULT 0
    );
    """)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None


def valid_email(email):
    return bool(
        re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip())
    )


def company_rows(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def money(value):
    return f"Rs. {float(value):,.2f}"


def get_employee_for_user(cid, uid):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT *
            FROM employees
            WHERE company_id = ? AND user_id = ?
            LIMIT 1
            """,
            (cid, uid),
        ).fetchone()


def audit(action, details=""):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO audit_log
            (company_id, actor_email, action, details)
            VALUES (?, ?, ?, ?)
            """,
            (company_id, user["email"], action, str(details)),
        )
        conn.commit()


def authenticate(email, password):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM users
            WHERE lower(email) = ?
            ORDER BY id
            LIMIT 1
            """,
            (email.strip().lower(),),
        ).fetchone()

    if not row:
        return None

    u = dict(row)
    active = u.get("is_active", 1)

    if "status" in u and str(u["status"]).lower() in (
        "inactive", "disabled", "0"
    ):
        active = 0

    if not active or not verify_password(password, u["password_hash"]):
        return None

    emp = get_employee_for_user(u["company_id"], u["id"])
    name = (
        u.get("full_name")
        or (emp["full_name"] if emp else None)
        or u["email"].split("@")[0]
    )

    return {
        "id": u["id"],
        "company_id": u["company_id"],
        "full_name": name,
        "email": u["email"],
        "role": u["role"],
    }


# ================= FIRST-TIME SETUP =================
if not setup_complete():
    st.title("HCM Lite")
    st.caption("Human Capital Management System")
    st.subheader("Set up your company")

    with st.form("initial_setup_form"):
        company_name = st.text_input("Company name")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Education", "Healthcare", "Retail",
             "Manufacturing", "Other"],
        )
        company_size = st.selectbox(
            "Company size",
            ["1–10", "11–50", "51–200", "201–500", "500+"],
        )
        st.markdown("### Administrator account")
        admin_name = st.text_input("Admin full name")
        admin_email = st.text_input("Admin login email")
        admin_password = st.text_input("Password", type="password")
        confirm_password = st.text_input(
            "Confirm password", type="password"
        )
        setup_clicked = st.form_submit_button(
            "Create Company Workspace",
            use_container_width=True,
        )

    if setup_clicked:
        if not all([
            company_name.strip(), admin_name.strip(),
            admin_email.strip(), admin_password, confirm_password
        ]):
            st.error("Please complete all required fields.")
        elif not valid_email(admin_email):
            st.error("Enter a valid Admin email.")
        elif len(admin_password) < 8:
            st.error("Password must be at least 8 characters.")
        elif admin_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                create_company_and_admin(
                    company_name=company_name.strip(),
                    industry=industry,
                    company_size=company_size,
                    admin_name=admin_name.strip(),
                    admin_email=admin_email.strip().lower(),
                    admin_password=admin_password,
                )
                st.success("Company workspace created.")
                st.rerun()
            except Exception as exc:
                st.error(f"Setup failed: {exc}")

    st.stop()


# ================= LOGIN =================
if not st.session_state.authenticated:
    st.markdown("""
        <div style="text-align:center; padding:20px 0 10px;">
            <h1 style="color:#14B8A6 !important;">HCM Lite</h1>
            <p style="color:#A8B7CC;">
                Human Capital Management System
            </p>
        </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        st.subheader("Welcome back")
        st.caption("Select your account type to continue.")

        # Three role tabs
        admin_tab, hr_tab, employee_tab = st.tabs([
            "👑 Admin", "👥 HR", "🧑‍💼 Employee"
        ])

        def login_form_for_role(selected_role, form_key):
            with st.form(form_key):
                email = st.text_input(
                    "Email address",
                    key=f"{form_key}_email",
                    placeholder="Enter your email"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key=f"{form_key}_password",
                    placeholder="Enter your password"
                )
                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True
                )

            if submitted:
                if not email.strip() or not password:
                    st.error("Enter your email and password.")
                    return

                try:
                    logged = authenticate(email, password)

                    if logged is None:
                        st.error("Invalid credentials or inactive account.")
                    elif logged["role"].strip().lower() != selected_role.lower():
                        st.error(
                            f"This account is not registered as {selected_role}."
                        )
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user = logged
                        st.rerun()

                except Exception as exc:
                    st.error(f"Login failed: {exc}")

        with admin_tab:
            st.markdown("#### Administrator Login")
            st.caption("Manage your company workspace.")
            login_form_for_role("Admin", "admin_login_form")

        with hr_tab:
            st.markdown("#### HR Login")
            st.caption("Manage employees and HR operations.")
            login_form_for_role("HR", "hr_login_form")

        with employee_tab:
            st.markdown("#### Employee Login")
            st.caption("Access your personal workspace.")
            login_form_for_role("Employee", "employee_login_form")

    st.stop()


# ================= CURRENT USER =================
user = st.session_state.user
company_id = user["company_id"]
role = user["role"]

company_record = get_company(company_id)

if company_record is None:
    st.error("Company record could not be found.")
    st.stop()

company = company_record["company_name"]

admin_pages = [
    "Overview", "Employees", "Attendance", "Leave Management",
    "Payroll", "Departments & Policies", "Announcements",
    "AI Assistant", "Audit Log",
]
hr_pages = [
    "Overview", "Employees", "Attendance", "Leave Management",
    "Payroll", "Departments & Policies", "Announcements",
    "AI Assistant",
]
employee_pages = [
    "My Overview", "My Attendance", "My Leave", "My Payslips",
    "Announcements", "AI Assistant",
]

if role == "Admin":
    available_pages = admin_pages
elif role == "HR":
    available_pages = hr_pages
else:
    available_pages = employee_pages


# ================= SIDEBAR =================
with st.sidebar:
    st.title("HCM Lite")
    st.caption(company)
    st.divider()
    st.markdown(f"**{user['full_name']}**")
    st.caption(f"{role} account")

    page = st.radio(
        "WORKSPACE",
        available_pages,
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()


# ================= OVERVIEW =================
if page in ("Overview", "My Overview"):
    st.caption(f"{company.upper()} / WORKSPACE")
    st.title(
        "Workforce Overview"
        if role in ("Admin", "HR") else "My Overview"
    )
    st.write(f"Welcome back, {user['full_name']}.")

    if role in ("Admin", "HR"):
        total = count_employees(company_id)
        active = count_employees(company_id, "Active")
        inactive = count_employees(company_id, "Inactive")
        accounts = count_users(company_id)

        hr_count = company_rows(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE company_id = ? AND role = 'HR'
            """,
            (company_id,),
        )[0]["total"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Employees", total)
        c2.metric("Active Employees", active)
        c3.metric("Inactive Employees", inactive)
        c4.metric("Accounts", accounts)

        st.divider()
        st.subheader("Today's attendance")

        today = date.today().isoformat()
        a, b, c, d = st.columns(4)
        a.metric(
            "Present",
            count_attendance(company_id, today, "Present")
        )
        b.metric(
            "Late",
            count_attendance(company_id, today, "Late")
        )
        c.metric(
            "Half Day",
            count_attendance(company_id, today, "Half Day")
        )
        d.metric("HR Accounts", hr_count)

        # ============== WORKFORCE ANALYTICS ==============
        st.divider()
        st.subheader("Workforce Analytics")

        attendance_trend = company_rows(
            """
            SELECT substr(attendance_date, 1, 7) AS Month,
                   COUNT(*) AS Records
            FROM attendance
            WHERE company_id = ?
            GROUP BY substr(attendance_date, 1, 7)
            ORDER BY Month
            """,
            (company_id,),
        )

        payroll_trend = company_rows(
            """
            SELECT payroll_month AS Month,
                   SUM(net_salary) AS Net_Payroll
            FROM payroll
            WHERE company_id = ?
            GROUP BY payroll_month
            ORDER BY payroll_month
            """,
            (company_id,),
        )

        pending_leaves = company_rows(
            """
            SELECT COUNT(*) AS total
            FROM leave_requests
            WHERE company_id = ? AND status = 'Pending'
            """,
            (company_id,),
        )[0]["total"]

        x1, x2, x3 = st.columns(3)
        x1.metric("Pending Leave Requests", pending_leaves)
        x2.metric(
            "Attendance Records",
            sum(int(r["Records"]) for r in attendance_trend)
        )
        x3.metric("Payroll Months", len(payroll_trend))

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown("**Monthly Attendance Records**")
            if attendance_trend:
                df_att = pd.DataFrame(
                    [dict(r) for r in attendance_trend]
                )
                st.bar_chart(
                    df_att.set_index("Month")["Records"]
                )
            else:
                st.info("Attendance data will appear here.")

        with chart2:
            st.markdown("**Monthly Net Payroll**")
            if payroll_trend:
                df_pay = pd.DataFrame(
                    [dict(r) for r in payroll_trend]
                )
                st.bar_chart(
                    df_pay.set_index("Month")["Net_Payroll"]
                )
            else:
                st.info("Payroll data will appear here.")

    else:
        emp = get_employee_for_user(company_id, user["id"])

        if emp:
            c1, c2, c3 = st.columns(3)
            c1.metric("Employee ID", emp["employee_code"])
            c2.metric("Department", emp["department"] or "—")
            c3.metric("Status", emp["status"])

            st.write(
                f"**Designation:** {emp['designation'] or '—'}"
            )
            st.write(
                f"**Joining date:** {emp['hire_date'] or '—'}"
            )
        else:
            st.info(
                "Your employee profile is not linked yet. Contact HR."
            )


# ================= EMPLOYEE MANAGEMENT =================
elif page == "Employees":
    if role not in ("Admin", "HR"):
        st.error("Not authorized.")
        st.stop()

    st.title("Employee Management")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", count_employees(company_id))
    c2.metric("Active", count_employees(company_id, "Active"))
    c3.metric("Inactive", count_employees(company_id, "Inactive"))

    with st.expander(
        "＋ Add New Employee",
        expanded=(count_employees(company_id) == 0),
    ):
        with st.form("add_employee_form"):
            left, right = st.columns(2)

            with left:
                employee_code = st.text_input("Employee ID *")
                full_name = st.text_input("Full name *")
                employee_email = st.text_input("Email *")
                phone = st.text_input("Phone")

            with right:
                department = st.selectbox(
                    "Department",
                    ["Administration", "Human Resources", "Finance",
                     "Information Technology", "Sales", "Marketing",
                     "Operations", "Other"],
                )
                designation = st.text_input("Designation *")
                hire_date = st.date_input(
                    "Joining date", value=date.today()
                )

            save = st.form_submit_button(
                "Save Employee", use_container_width=True
            )

        if save:
            if not all([
                employee_code.strip(), full_name.strip(),
                employee_email.strip(), designation.strip()
            ]):
                st.error("Complete required fields.")
            elif not valid_email(employee_email):
                st.error("Enter a valid email.")
            else:
                try:
                    create_employee(
                        company_id=company_id,
                        employee_code=employee_code.strip(),
                        full_name=full_name.strip(),
                        email=employee_email.strip().lower(),
                        phone=phone.strip(),
                        department=department,
                        designation=designation.strip(),
                        hire_date=hire_date.isoformat(),
                    )
                    audit("Employee Created", employee_code)
                    st.success("Employee saved.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Unable to save employee: {exc}")

    st.subheader("Employee Directory")
    search = st.text_input("Search by ID, name, email or department")
    records = get_employees(company_id, search)

    if records:
        recs = [dict(r) for r in records]
        departments = sorted({
            r.get("department") or "Unassigned" for r in recs
        })
        selected_dept = st.selectbox(
            "Department filter", ["All Departments"] + departments
        )
        filtered = [
            r for r in recs
            if selected_dept == "All Departments"
            or (r.get("department") or "Unassigned") == selected_dept
        ]

        display = [{
            "Employee ID": r["employee_code"],
            "Name": r["full_name"],
            "Email": r["email"],
            "Phone": r.get("phone"),
            "Department": r.get("department"),
            "Designation": r.get("designation"),
            "Joining Date": r.get("hire_date"),
            "Status": r.get("status"),
        } for r in filtered]

        st.dataframe(display, use_container_width=True, hide_index=True)
        st.download_button(
            "Export employee CSV",
            pd.DataFrame(display).to_csv(index=False).encode("utf-8"),
            "employees.csv",
            "text/csv",
        )

        candidates = [
            r for r in recs
            if r.get("status") == "Active" and r.get("user_id") is None
        ]

        if candidates:
            st.subheader("Create Employee Login")
            options = {
                f'{r["employee_code"]} — {r["full_name"]}': r
                for r in candidates
            }

            with st.form("create_login_form"):
                label = st.selectbox("Employee", list(options))
                password = st.text_input("Temporary password", type="password")
                confirm = st.text_input("Confirm password", type="password")
                create_login = st.form_submit_button("Create login")

            if create_login:
                if len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif len(password.encode("utf-8")) > 72:
                    st.error("Password exceeds 72 UTF-8 bytes.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        create_employee_login(
                            company_id, options[label]["id"], password
                        )
                        audit("Employee Login Created", label)
                        st.success("Login created.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not create login: {exc}")

        if filtered:
            st.subheader("Update Employee Status")
            options = {
                f'{r["employee_code"]} — {r["full_name"]}': r
                for r in filtered
            }
            chosen = st.selectbox("Select employee", list(options))
            target = options[chosen]
            status = st.selectbox(
                "Status", ["Active", "Inactive"],
                index=0 if target["status"] == "Active" else 1,
            )

            if st.button("Update Status"):
                try:
                    update_employee_status(
                        company_id, target["id"], status
                    )
                    audit("Employee Status Updated", f"{chosen}: {status}")
                    st.success("Status updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Update failed: {exc}")

    else:
        st.info("No employees found.")

    st.divider()
    st.subheader("Import employees from CSV")
    uploaded = st.file_uploader(
        "Upload CSV containing employee_code, full_name, email, "
        "department and designation",
        type=["csv"],
    )

    if uploaded:
        try:
            import_df = pd.read_csv(uploaded)
            st.dataframe(import_df.head(10), use_container_width=True)

            if st.button("Import valid rows"):
                success = 0
                errors = []

                for idx, row in import_df.iterrows():
                    try:
                        required = [
                            str(row.get(k, "")).strip()
                            for k in [
                                "employee_code", "full_name", "email",
                                "department", "designation"
                            ]
                        ]

                        if not all(required) or not valid_email(required[2]):
                            raise ValueError("Missing fields or invalid email")

                        create_employee(
                            company_id=company_id,
                            employee_code=required[0],
                            full_name=required[1],
                            email=required[2],
                            phone=str(row.get("phone", "")),
                            department=required[3],
                            designation=required[4],
                            hire_date=str(
                                row.get("hire_date", date.today().isoformat())
                            ),
                        )
                        success += 1
                    except Exception as exc:
                        errors.append(f"Row {idx + 2}: {exc}")

                audit(
                    "Employee CSV Import",
                    f"Imported {success}; errors {len(errors)}",
                )
                st.success(f"Imported {success} rows.")
                if errors:
                    st.warning("; ".join(errors[:8]))
                st.rerun()

        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")


# ================= ATTENDANCE ADMIN =================
elif page == "Attendance":
    if role not in ("Admin", "HR"):
        st.error("Not authorized.")
        st.stop()

    st.title("Attendance Management")
    selected_date = st.date_input(
        "Attendance date", value=date.today(), key="admin_attendance_date"
    )
    dt = selected_date.isoformat()

    a, b, c, d = st.columns(4)
    a.metric("Present", count_attendance(company_id, dt, "Present"))
    b.metric("Late", count_attendance(company_id, dt, "Late"))
    c.metric("Half Day", count_attendance(company_id, dt, "Half Day"))
    d.metric("Absent", count_attendance(company_id, dt, "Absent"))

    rows = get_company_attendance(company_id, dt)

    if rows:
        data = [{
            "Employee ID": r["employee_code"],
            "Employee": r["full_name"],
            "Department": r["department"] or "—",
            "Date": r["attendance_date"],
            "Check In": r["check_in"] or "—",
            "Check Out": r["check_out"] or "—",
            "Status": r["status"],
        } for r in rows]

        st.dataframe(data, use_container_width=True, hide_index=True)
        st.download_button(
            "Download attendance CSV",
            pd.DataFrame(data).to_csv(index=False).encode(),
            f"attendance_{dt}.csv",
            "text/csv",
        )
    else:
        st.info("No attendance recorded for this date.")


# ================= EMPLOYEE ATTENDANCE =================
elif page == "My Attendance":
    st.title("My Attendance")
    emp = get_employee_for_user(company_id, user["id"])

    if not emp:
        st.warning("Employee profile is not linked. Contact HR.")
    elif emp["status"] != "Active":
        st.warning("Your employee account is inactive.")
    else:
        today = date.today().isoformat()
        rows = company_rows(
            """
            SELECT *
            FROM attendance
            WHERE company_id = ? AND employee_id = ?
              AND attendance_date = ?
            """,
            (company_id, emp["id"], today),
        )
        today_record = rows[0] if rows else None

        st.subheader(f"Hello, {emp['full_name']}")
        st.write(f"Today's date: {today}")

        if today_record:
            a, b, c = st.columns(3)
            a.metric("Check In", today_record["check_in"] or "—")
            b.metric("Check Out", today_record["check_out"] or "—")
            c.metric("Status", today_record["status"])
            st.subheader("Face Registration & Training")

        if st.button("📸 Register My Face", use_container_width=True):
            try:
                count = capture_face_samples(company_id, emp["id"])
                st.success(f"{count} face samples captured.")
            except Exception as exc:
                st.error(f"Registration failed: {exc}")

        if st.button("🧠 Train Face Model", use_container_width=True):
            try:
                count = train_face_model()
                st.success(f"Model trained with {count} images.")
            except Exception as exc:
                st.error(f"Training failed: {exc}")
            st.subheader("Face Recognition Attendance")

        if st.button("📸 Mark Attendance with Face", use_container_width=True):
            try:
                result = recognize_and_mark_attendance(company_id)
                st.success(result)
                audit("Face Recognition Check In", emp["employee_code"])
                st.rerun()
            except Exception as exc:
                st.error(f"Face attendance failed: {exc}")
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "✅ Check In",
                use_container_width=True,
                disabled=bool(today_record and today_record["check_in"]),
            ):
                try:
                    result = check_in_employee(company_id, emp["id"])
                    audit("Employee Check In", emp["employee_code"])
                    st.success(
                        f"Checked in at {result['check_in']} — "
                        f"{result['status']}"
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Check-in failed: {exc}")

        with col2:
            disabled = not (
                today_record
                and today_record["check_in"]
                and not today_record["check_out"]
            )
            if st.button(
                "🏁 Check Out",
                use_container_width=True,
                disabled=disabled,
            ):
                try:
                    result = check_out_employee(company_id, emp["id"])
                    audit("Employee Check Out", emp["employee_code"])
                    st.success(
                        f"Checked out at {result['check_out']}; "
                        f"hours: {result.get('duration_hours', '—')}"
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Check-out failed: {exc}")

        st.subheader("Recent attendance")
        history = get_employee_attendance(
            company_id, emp["id"], limit=60
        )
        if history:
            st.dataframe([{
                "Date": r["attendance_date"],
                "Check In": r["check_in"] or "—",
                "Check Out": r["check_out"] or "—",
                "Status": r["status"],
            } for r in history], use_container_width=True, hide_index=True)
        else:
            st.info("Attendance history will appear here.")


# ================= DEPARTMENTS & POLICIES =================
elif page == "Departments & Policies":
    if role not in ("Admin", "HR"):
        st.error("Not authorized.")
        st.stop()

    st.title("Departments, Policies & Holidays")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Departments", "Policies", "Holidays", "Leave Types"
    ])

    with tab1:
        with st.form("add_department"):
            dep_name = st.text_input("Department name")
            dep_desc = st.text_area("Description")
            dep_save = st.form_submit_button("Add department")

        if dep_save:
            if not dep_name.strip():
                st.error("Department name is required.")
            else:
                try:
                    with get_connection() as conn:
                        conn.execute(
                            """
                            INSERT INTO departments(company_id,name,description)
                            VALUES(?,?,?)
                            """,
                            (company_id, dep_name.strip(), dep_desc.strip()),
                        )
                        conn.commit()
                    audit("Department Added", dep_name)
                    st.success("Department added.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not add department: {exc}")

        deps = company_rows(
            "SELECT * FROM departments WHERE company_id=? ORDER BY name",
            (company_id,),
        )
        if deps:
            st.dataframe(
                [dict(x) for x in deps],
                use_container_width=True,
                hide_index=True,
            )
            options = {
                f'{x["name"]} (ID {x["id"]})': x["id"] for x in deps
            }
            chosen = st.selectbox("Department to delete", list(options))
            if st.button("Delete department"):
                with get_connection() as conn:
                    conn.execute(
                        "DELETE FROM departments WHERE id=? AND company_id=?",
                        (options[chosen], company_id),
                    )
                    conn.commit()
                audit("Department Deleted", chosen)
                st.rerun()
        else:
            st.info("No departments added yet.")

    with tab2:
        with st.form("add_policy"):
            title = st.text_input("Policy title")
            category = st.selectbox(
                "Category", ["Attendance", "Leave", "Payroll", "Conduct", "Other"]
            )
            description = st.text_area("Policy details")
            save_policy = st.form_submit_button("Save policy")

        if save_policy:
            if not title.strip() or not description.strip():
                st.error("Title and details are required.")
            else:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO policies(company_id,title,category,description)
                        VALUES(?,?,?,?)
                        """,
                        (company_id, title.strip(), category, description.strip()),
                    )
                    conn.commit()
                audit("Policy Added", title)
                st.success("Policy saved.")
                st.rerun()

        policies = company_rows(
            "SELECT * FROM policies WHERE company_id=? ORDER BY id DESC",
            (company_id,),
        )
        for policy in policies:
            with st.expander(
                f'{policy["title"]} · {policy["category"]}'
            ):
                st.write(policy["description"])
                if st.button(
                    "Delete policy", key=f'del_policy_{policy["id"]}'
                ):
                    with get_connection() as conn:
                        conn.execute(
                            "DELETE FROM policies WHERE id=? AND company_id=?",
                            (policy["id"], company_id),
                        )
                        conn.commit()
                    audit("Policy Deleted", policy["title"])
                    st.rerun()

    with tab3:
        with st.form("add_holiday"):
            holiday_name = st.text_input("Holiday name")
            holiday_date = st.date_input("Holiday date", value=date.today())
            save_holiday = st.form_submit_button("Add holiday")

        if save_holiday:
            if not holiday_name.strip():
                st.error("Holiday name is required.")
            else:
                try:
                    with get_connection() as conn:
                        conn.execute(
                            """
                            INSERT INTO holidays(company_id,holiday_date,name)
                            VALUES(?,?,?)
                            """,
                            (
                                company_id,
                                holiday_date.isoformat(),
                                holiday_name.strip(),
                            ),
                        )
                        conn.commit()
                    audit("Holiday Added", holiday_name)
                    st.success("Holiday added.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not add holiday: {exc}")

        holidays = company_rows(
            "SELECT * FROM holidays WHERE company_id=? ORDER BY holiday_date",
            (company_id,),
        )
        if holidays:
            st.dataframe(
                [dict(x) for x in holidays],
                use_container_width=True,
                hide_index=True,
            )
            options = {
                f'{x["holiday_date"]} — {x["name"]}': x["id"]
                for x in holidays
            }
            chosen = st.selectbox("Holiday to delete", list(options))
            if st.button("Delete holiday"):
                with get_connection() as conn:
                    conn.execute(
                        "DELETE FROM holidays WHERE id=? AND company_id=?",
                        (options[chosen], company_id),
                    )
                    conn.commit()
                audit("Holiday Deleted", chosen)
                st.rerun()

    with tab4:
        with st.form("add_leave_type"):
            type_name = st.text_input("Leave type name")
            quota = st.number_input(
                "Annual quota (days)", min_value=0, max_value=365, value=12
            )
            save_type = st.form_submit_button("Add leave type")

        if save_type:
            if not type_name.strip():
                st.error("Leave type name is required.")
            else:
                try:
                    with get_connection() as conn:
                        conn.execute(
                            """
                            INSERT INTO leave_types(company_id,name,annual_quota)
                            VALUES(?,?,?)
                            """,
                            (company_id, type_name.strip(), int(quota)),
                        )
                        conn.commit()
                    audit("Leave Type Added", type_name)
                    st.success("Leave type added.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not add leave type: {exc}")

        leave_types = company_rows(
            "SELECT * FROM leave_types WHERE company_id=? ORDER BY name",
            (company_id,),
        )
        if leave_types:
            st.dataframe(
                [dict(x) for x in leave_types],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No custom leave types added yet.")


# ================= LEAVE MANAGEMENT =================
elif page in ("Leave Management", "My Leave"):
    st.title("Leave Management")
    emp = get_employee_for_user(company_id, user["id"])

    if page == "My Leave":
        if not emp:
            st.warning("Your employee profile is not linked.")
            st.stop()

        st.subheader("Apply for Leave")

        custom_types = company_rows(
            "SELECT name FROM leave_types WHERE company_id=? ORDER BY name",
            (company_id,),
        )
        type_options = ["Casual", "Sick", "Annual", "Unpaid"]
        type_options += [
            r["name"] for r in custom_types
            if r["name"] not in type_options
        ]

        with st.form("leave_application"):
            leave_type = st.selectbox("Leave type", type_options)
            start_date = st.date_input(
                "Start date", min_value=date.today()
            )
            end_date = st.date_input(
                "End date", min_value=start_date
            )
            reason = st.text_area("Reason")
            submit_leave = st.form_submit_button("Submit Request")

        if submit_leave:
            if end_date < start_date:
                st.error("End date cannot be before start date.")
            else:
                start_text = start_date.isoformat()
                end_text = end_date.isoformat()

                overlap = company_rows(
                    """
                    SELECT id FROM leave_requests
                    WHERE company_id=? AND employee_id=?
                    AND status IN ('Pending','Approved')
                    AND start_date <= ? AND end_date >= ?
                    """,
                    (company_id, emp["id"], end_text, start_text),
                )
                holidays = company_rows(
                    """
                    SELECT holiday_date FROM holidays
                    WHERE company_id=? AND holiday_date BETWEEN ? AND ?
                    """,
                    (company_id, start_text, end_text),
                )

                if overlap:
                    st.error(
                        "These dates overlap an existing pending or approved request."
                    )
                elif holidays:
                    st.warning(
                        "The selected date range contains a company holiday. "
                        "Please review the dates."
                    )
                else:
                    with get_connection() as conn:
                        conn.execute(
                            """
                            INSERT INTO leave_requests
                            (company_id,employee_id,leave_type,start_date,
                             end_date,reason)
                            VALUES(?,?,?,?,?,?)
                            """,
                            (
                                company_id, emp["id"], leave_type,
                                start_text, end_text, reason.strip(),
                            ),
                        )
                        conn.commit()
                    audit("Leave Applied", leave_type)
                    st.success("Leave request submitted.")
                    st.rerun()

        own_requests = company_rows(
            """
            SELECT leave_type,start_date,end_date,reason,status,decision_comment
            FROM leave_requests
            WHERE company_id=? AND employee_id=?
            ORDER BY id DESC
            """,
            (company_id, emp["id"]),
        )
        st.subheader("My Requests")
        if own_requests:
            st.dataframe(
                [dict(r) for r in own_requests],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("You have not submitted any leave requests.")

    elif role in ("Admin", "HR"):
        requests = company_rows(
            """
            SELECT l.*,e.full_name,e.employee_code
            FROM leave_requests l
            JOIN employees e ON e.id=l.employee_id
            WHERE l.company_id=?
            ORDER BY l.id DESC
            """,
            (company_id,),
        )

        if requests:
            st.dataframe([{
                "ID": r["id"],
                "Employee": r["full_name"],
                "Employee ID": r["employee_code"],
                "Type": r["leave_type"],
                "From": r["start_date"],
                "To": r["end_date"],
                "Reason": r["reason"],
                "Status": r["status"],
                "Comment": r["decision_comment"],
            } for r in requests], use_container_width=True, hide_index=True)

            pending = [r for r in requests if r["status"] == "Pending"]
            if pending:
                options = {
                    f'{r["id"]} — {r["full_name"]} ({r["leave_type"]})': r
                    for r in pending
                }

                with st.form("leave_decision"):
                    chosen = st.selectbox("Pending request", list(options))
                    decision = st.selectbox(
                        "Decision", ["Approved", "Rejected"]
                    )
                    comment = st.text_input("Decision comment")
                    save_decision = st.form_submit_button("Save Decision")

                if save_decision:
                    req = options[chosen]
                    with get_connection() as conn:
                        conn.execute(
                            """
                            UPDATE leave_requests
                            SET status=?, decision_comment=?
                            WHERE id=? AND company_id=? AND status='Pending'
                            """,
                            (
                                decision, comment.strip(),
                                req["id"], company_id,
                            ),
                        )
                        conn.commit()
                    audit("Leave " + decision, f'Request ID {req["id"]}')
                    st.success("Decision saved.")
                    st.rerun()
        else:
            st.info("No leave requests yet.")


# ================= PAYROLL =================
elif page in ("Payroll", "My Payslips"):
    st.title("Payroll & Payslips")

    if page == "Payroll" and role in ("Admin", "HR"):
        employees = company_rows(
            """
            SELECT id,employee_code,full_name
            FROM employees
            WHERE company_id=? AND status='Active'
            ORDER BY full_name
            """,
            (company_id,),
        )

        if employees:
            choices = {
                f'{e["employee_code"]} — {e["full_name"]}': e["id"]
                for e in employees
            }

            with st.form("salary_setup"):
                selected = st.selectbox("Employee", list(choices))
                basic = st.number_input(
                    "Monthly basic salary (Rs.)",
                    min_value=0.0, step=1000.0,
                )
                allowance = st.number_input(
                    "Monthly allowance (Rs.)",
                    min_value=0.0, step=500.0,
                )
                save_salary = st.form_submit_button("Save salary structure")

            if save_salary:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO salary_structures
                        (company_id,employee_id,basic_salary,allowance)
                        VALUES(?,?,?,?)
                        ON CONFLICT(employee_id) DO UPDATE SET
                        company_id=excluded.company_id,
                        basic_salary=excluded.basic_salary,
                        allowance=excluded.allowance
                        """,
                        (
                            company_id, choices[selected], basic, allowance
                        ),
                    )
                    conn.commit()
                audit("Salary Structure Saved", selected)
                st.success("Salary structure saved.")
                st.rerun()

        st.subheader("Tax slabs")
        with st.form("tax_slab_form"):
            minimum = st.number_input(
                "Minimum monthly gross salary", min_value=0.0, step=1000.0
            )
            maximum = st.number_input(
                "Maximum salary (0 = no upper limit)",
                min_value=0.0, step=1000.0,
            )
            tax_pct = st.number_input(
                "Deduction percentage",
                min_value=0.0, max_value=100.0, step=0.5,
            )
            save_slab = st.form_submit_button("Add tax slab")

        if save_slab:
            if maximum and maximum < minimum:
                st.error("Maximum salary cannot be lower than minimum.")
            else:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO tax_slabs
                        (company_id,minimum_salary,maximum_salary,tax_percent)
                        VALUES(?,?,?,?)
                        """,
                        (
                            company_id, minimum,
                            maximum if maximum > 0 else None, tax_pct,
                        ),
                    )
                    conn.commit()
                audit("Tax Slab Added", f"{minimum}-{maximum}: {tax_pct}%")
                st.success("Tax slab added.")
                st.rerun()

        slabs = company_rows(
            "SELECT * FROM tax_slabs WHERE company_id=? ORDER BY minimum_salary",
            (company_id,),
        )
        if slabs:
            st.dataframe(
                [dict(s) for s in slabs],
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Generate monthly payroll")
        with st.form("run_payroll"):
            month = st.text_input(
                "Payroll month (YYYY-MM)",
                value=date.today().strftime("%Y-%m"),
            )
            run = st.form_submit_button("Generate draft payroll")

        if run:
            if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
                st.error("Enter month in YYYY-MM format.")
            else:
                salaries = company_rows(
                    """
                    SELECT employee_id,basic_salary,allowance
                    FROM salary_structures WHERE company_id=?
                    """,
                    (company_id,),
                )

                created = 0
                with get_connection() as conn:
                    for salary in salaries:
                        gross = (
                            float(salary["basic_salary"])
                            + float(salary["allowance"])
                        )
                        pct = 0.0
                        matched = [
                            x for x in slabs
                            if gross >= float(x["minimum_salary"])
                            and (
                                x["maximum_salary"] is None
                                or gross <= float(x["maximum_salary"])
                            )
                        ]
                        if matched:
                            pct = float(matched[-1]["tax_percent"])

                        deduction = round(gross * pct / 100, 2)
                        net = round(gross - deduction, 2)

                        cur = conn.execute(
                            """
                            INSERT INTO payroll
                            (company_id,employee_id,payroll_month,gross_salary,
                             deductions,net_salary)
                            VALUES(?,?,?,?,?,?)
                            ON CONFLICT(company_id,employee_id,payroll_month)
                            DO NOTHING
                            """,
                            (
                                company_id, salary["employee_id"], month,
                                gross, deduction, net,
                            ),
                        )
                        created += cur.rowcount

                    conn.commit()

                audit("Payroll Draft Generated", month)
                st.success(f"Created {created} new payroll records.")
                st.rerun()

        payroll_rows = company_rows(
            """
            SELECT p.*,e.full_name,e.employee_code
            FROM payroll p
            JOIN employees e ON e.id=p.employee_id
            WHERE p.company_id=?
            ORDER BY p.payroll_month DESC,e.full_name
            """,
            (company_id,),
        )

        if payroll_rows:
            st.dataframe(
                [dict(r) for r in payroll_rows],
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "Export payroll CSV",
                pd.DataFrame([dict(r) for r in payroll_rows])
                .to_csv(index=False).encode(),
                "payroll.csv",
                "text/csv",
            )
            st.caption(
                "Payroll records are drafts. Verify applicable tax rules "
                "before using these figures for actual payments."
            )

    elif page == "My Payslips":
        emp = get_employee_for_user(company_id, user["id"])
        if not emp:
            st.warning("Employee profile not linked.")
        else:
            pays = company_rows(
                """
                SELECT payroll_month,gross_salary,deductions,net_salary,status
                FROM payroll
                WHERE company_id=? AND employee_id=?
                ORDER BY payroll_month DESC
                """,
                (company_id, emp["id"]),
            )

            if pays:
                st.dataframe(
                    [dict(r) for r in pays],
                    use_container_width=True,
                    hide_index=True,
                )
                selected_month = st.selectbox(
                    "Select month for payslip",
                    [r["payroll_month"] for r in pays],
                )
                row = next(
                    r for r in pays if r["payroll_month"] == selected_month
                )
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=A4,
                    rightMargin=45,
                    leftMargin=45,
                    topMargin=50,
                    bottomMargin=40,
                )

                styles = getSampleStyleSheet()
                content = [
                    Paragraph("HCM LITE — PAYSLIP", styles["Title"]),
                    Spacer(1, 18),
                    Paragraph(f"<b>Company:</b> {company}", styles["Normal"]),
                    Paragraph(
                        f"<b>Employee:</b> {emp['full_name']} "
                        f"({emp['employee_code']})",
                        styles["Normal"],
                    ),
                    Paragraph(
                        f"<b>Payroll Month:</b> {row['payroll_month']}",
                        styles["Normal"],
                    ),
                    Spacer(1, 22),
                ]

                table = Table([
                    ["Description", "Amount"],
                    ["Gross Salary", money(row["gross_salary"])],
                    ["Deductions", money(row["deductions"])],
                    ["Net Salary", money(row["net_salary"])],
                    ["Payroll Status", str(row["status"])],
                ], colWidths=[260, 180])

                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B766E")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("PADDING", (0, 0), (-1, -1), 10),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#D9F3EE")),
                ]))

                content.extend([
                    table,
                    Spacer(1, 24),
                    Paragraph(
                        "Generated by HCM Lite. Verify payroll details "
                        "before using for actual payments.",
                        styles["Italic"],
                    ),
                ])

                doc.build(content)
                pdf_buffer.seek(0)

                st.download_button(
                    "Download Payslip (PDF)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"payslip_{selected_month}.pdf",
                    mime="application/pdf",
                )
            else:
                st.info("No payslips available yet.")


# ================= ANNOUNCEMENTS =================
elif page == "Announcements":
    st.title("Company Announcements")

    if role in ("Admin", "HR"):
        with st.form("new_announcement"):
            title_text = st.text_input("Announcement title")
            message_text = st.text_area("Announcement message")
            post = st.form_submit_button("Publish")

        if post:
            if not title_text.strip() or not message_text.strip():
                st.error("Enter both title and message.")
            else:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO announcements
                        (company_id,title,message,created_by)
                        VALUES(?,?,?,?)
                        """,
                        (
                            company_id, title_text.strip(),
                            message_text.strip(), user["email"],
                        ),
                    )
                    conn.commit()
                audit("Announcement Published", title_text.strip())
                st.success("Announcement published.")
                st.rerun()

    posts = company_rows(
        """
        SELECT title,message,created_by,created_at
        FROM announcements
        WHERE company_id=?
        ORDER BY id DESC
        """,
        (company_id,),
    )

    if posts:
        for post in posts:
            with st.container(border=True):
                st.subheader(post["title"])
                st.write(post["message"])
                st.caption(
                    f'Posted by {post["created_by"] or "HR"} · '
                    f'{post["created_at"]}'
                )
    else:
        st.info("No announcements have been published.")


# ================= AUDIT LOG =================
elif page == "Audit Log":
    if role != "Admin":
        st.error("Admin access required.")
        st.stop()

    st.title("Audit Log")
    logs = company_rows(
        """
        SELECT actor_email,action,details,created_at
        FROM audit_log
        WHERE company_id=?
        ORDER BY id DESC
        """,
        (company_id,),
    )

    if logs:
        st.dataframe(
            [dict(x) for x in logs],
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Export audit log CSV",
            pd.DataFrame([dict(x) for x in logs])
            .to_csv(index=False).encode(),
            "audit_log.csv",
            "text/csv",
        )
    else:
        st.info("No logged actions yet.")

# ================= AI ASSISTANT =================
elif page == "AI Assistant":
    st.title("HCM Lite Assistant")
    st.caption(
        "AI answers grounded in your company's application data."
    )

    question = st.text_input(
        "Ask about attendance, leave, payroll, policies or employees"
    )

    if question:
        today = date.today().isoformat()

        # Only aggregate company data for Admin/HR.
        # Employees receive a limited context.
        context_parts = [
            f"Company: {company}",
            f"Today's date: {today}",
            f"User role: {role}",
        ]

        if role in ("Admin", "HR"):
            total = count_employees(company_id)
            active = count_employees(company_id, "Active")
            present = count_attendance(
                company_id, today, "Present"
            )
            late = count_attendance(
                company_id, today, "Late"
            )

            context_parts.extend([
                f"Total employees: {total}",
                f"Active employees: {active}",
                f"Present today: {present}",
                f"Late today: {late}",
            ])

            # These tables are already used by your app.
            pending = company_rows(
                """
                SELECT COUNT(*) AS total
                FROM leave_requests
                WHERE company_id = ? AND status = 'Pending'
                """,
                (company_id,),
            )[0]["total"]

            payroll_total = company_rows(
                """
                SELECT COUNT(*) AS total
                FROM payroll
                WHERE company_id = ?
                """,
                (company_id,),
            )[0]["total"]

            context_parts.extend([
                f"Pending leave requests: {pending}",
                f"Payroll records: {payroll_total}",
            ])

        else:
            # Do not expose company-wide payroll or other
            # employees' personal records to an employee.
            emp = get_employee_for_user(
                company_id, user["id"]
            )

            if emp:
                context_parts.extend([
                    f"Your employee code: {emp['employee_code']}",
                    f"Your department: {emp['department'] or 'Not set'}",
                    f"Your employment status: {emp['status']}",
                ])
            else:
                context_parts.append(
                    "No linked employee profile was found."
                )

        # Fetch policies only for this company.
        policies = company_rows(
            """
            SELECT title, category, description
            FROM policies
            WHERE company_id = ?
            ORDER BY id DESC
            """,
            (company_id,),
        )

        if policies:
            context_parts.append("Company policies:")
            for p in policies:
                context_parts.append(
                    f"- {p['title']} ({p['category']}): "
                    f"{p['description']}"
                )

        context = "\n".join(context_parts)

        with st.spinner("Checking company data and generating answer..."):
            answer = ask_gemini(question, context)

        st.markdown("**Assistant**")
        st.write(answer)
