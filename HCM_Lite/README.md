# HCM Lite
### AI-Powered Human Capital Management System

**Simplifying HR Operations Through Intelligent Automation**

HCM Lite is an AI-assisted Human Capital Management platform designed to streamline everyday HR operations through a centralized, role-based web application. It brings employee management, attendance tracking, leave administration, payroll processing, and data-driven insights together in one place.

Built for the **Saylani Hackathon**, HCM Lite aims to make HR workflows more organized, accessible, and efficient through modern web technologies and AI-powered assistance.

---

## Overview

Managing employees and daily HR activities can be time-consuming when information is scattered across different systems. HCM Lite addresses this challenge by providing a unified platform for administrators, HR professionals, and employees, with features tailored to their respective responsibilities.

The platform is designed to support a smoother employee lifecycle, from onboarding and attendance to leave approvals and payroll.

## Key Features

- **Role-Based Access Control** — Separate access and interfaces for Admin, HR, and Employees.
- **Organization Management** — Configure company information, departments, designations, and relevant HR settings.
- **Employee Management** — Register and manage employee records efficiently.
- **Attendance Tracking** — Record employee check-ins and check-outs.
- **Leave Management** — Submit, review, and approve employee leave requests.
- **Payroll Management** — Process monthly payroll and generate payslips.
- **Analytics & Dashboards** — Present HR information and operational insights in an accessible format.
- **AI Assistant** — Provide AI-assisted answers and support for available HR-related queries.
- **Notifications & Audit Logs** — Support communication and activity tracking where implemented.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Application Framework | Streamlit |
| Database | SQLite |
| AI Integration | Google Gemini API |
| Reporting | PDF generation |

*The technologies listed above should reflect the actual implementation of the submitted project.*

## Getting Started

Follow these steps to run HCM Lite locally.

### Prerequisites

- Python 3.10 or a compatible version
- pip package manager
- Required environment variables for enabled integrations

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd HCM_Lite
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file using `.env.example` as a reference. Add the required API credentials and configuration values for the features enabled in your application.

**Security note:** Never upload real API keys, passwords, or private credentials to GitHub.

### 4. Launch the Application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to access the application.

## First-Time Setup

HCM Lite is intended to begin with an initial organization setup rather than relying on preloaded demonstration records.

1. Create the initial Admin account through the available setup flow.
2. Configure company information and organizational settings.
3. Set up HR access and register employees.
4. Test the available attendance and leave workflows.
5. Run payroll and review the available reports and dashboards.

*Steps depend on the setup functionality implemented in the current version.*

## Project Links

- **Live Application:** YOUR_DEPLOYED_APP_URL
- **GitHub Repository:** YOUR_GITHUB_REPOSITORY_URL

## Project Status

HCM Lite is being developed as an AI-assisted HR management solution for the Saylani Hackathon.

This repository contains the project implementation and instructions for running the application. The availability of individual features depends on the current submitted version.

- **Implemented:** List the features that have been tested and are working.
- **In Progress:** List partially completed features.
- **Planned:** List features that have not yet been implemented.

## Future Enhancements

Potential improvements include enhanced analytics, more comprehensive HR automation, improved mobile responsiveness, and additional AI-assisted workflows.

## Security & Privacy

- Keep API credentials and database passwords confidential.
- Apply appropriate access restrictions to sensitive employee and payroll information.
- Avoid publishing private employee records or confidential data.
- Configure deployment secrets through the hosting provider's environment settings.

## Acknowledgment

Developed for the **Saylani Hackathon — HCM Lite Challenge**, with the goal of making human resource management more efficient through accessible web technology and AI-assisted workflows.

**Submission Portal:** https://lms.saylaniit.com/
