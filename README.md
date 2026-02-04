# CinemaApplication-Automation

This repository contains the **Automation Testing Framework** for the **CineBH** Cinema Application. It utilizes **Pytest** and **Playwright** to perform end-to-end (E2E) testing, API testing, and database verification against the deployed environment.

##  Project Structure

The project follows a modular structure to separate concerns between UI interactions, API tasks, and test logic.

```text
CinemaApplication-Atlantbh/
├── .venv/                  # Virtual environment
├── data/                   # Test data generation
├── database/               # Database migration or scripts
├── pages/                  # Page Object Model (POM) classes
├── reports/                # Test execution reports
├── tasks/                  # Business logic tasks
│   ├── api_tasks.py        # API wrappers for backend interaction
│   └── ui_tasks.py         # UI interaction logic
├── tests/                  # Test suites
│   ├── api/                # API-focused tests
│   └── ui/                 # UI-focused tests 
├── utils/                  # Shared utility functions
├── .env                    # Environment variables (Gitignored)
├── .gitignore              # Git ignore rules
├── api_client.py           # Core API client handler
├── conftest.py             # Pytest configuration and fixtures
├── pytest.ini              # Pytest settings
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies

```
## Setup & Installation
Follow these steps to set up the automation framework on your local machine.

## 1. Clone the Repository
```
git clone [https://github.com/your-username/CinemaApplication-Automation.git](https://github.com/your-username/CinemaApplication-Automation.git)
```
```
cd CinemaApplication-Automation

```
## 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.
```
macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
Windows:
python -m venv .venv
.venv\Scripts\activate
```
## 3. Install Dependencies
Install the required Python packages listed in requirements.txt:
```
pip install -r requirements.txt
```
## 4. Install Playwright Browsers
Playwright requires its own browser binaries (Chromium, Firefox, WebKit).
```
playwright install
```
## Configuration
Create a .env file in the root directory of the project. This file will store the connection details for the deployed application and database.
# Application URLs 
```
# Application URLs 
BASE_URL="[https://cinebh.local:3000/](https://cinebh.local:3000/)"
BASE_API_URL="[https://cinebh-api.local:8443/api/](https://cinebh-api.local:8443/api/)"

# Database Connection
DB_HOST=localhost
DB_PORT=5434
DB_NAME=cinebh
DB_USER=postgres
DB_PASSWORD=postgres

# Email Integration (Gmail IMAP)
HOST="imap.gmail.com"
TARGET_USER="strsevicnejra@gmail.com"
GMAIL_APP_PASSWORD="rsee pujn uqkd zvho"
```
## Running Tests
This framework uses Pytest as the test runner.

## Run All Tests
```
pytest
```
Run Smoke Tests Only
Executes tests marked with @pytest.mark.smoke or @pytest.mark.ui.

```
pytest -m ui
pytest -m -api
pytest --headed
```
## Test Reporting (Allure)
We use Allure to generate detailed, interactive test reports.
## 2. Generate & View Report
This command serves the report locally in your default browser.
```
allure serve allure-results
```
Note: You need the Allure command-line tool installed on your machine

## Tech Stack
Language: Python 3.10+
Test Runner: Pytest 9.0.2
Automation Tool: Playwright 1.57.0
Reporting: Allure 2.15.2
Database Client: Psycopg2 (PostgreSQL)
API Client: Requests
Utilities: python-dotenv