# 🛡️ Zero Trust Authentication System

A complete full-stack web application featuring a FastAPI backend with Continuous Verification and a React/Vite/TypeScript frontend.

## 📁 Project Structure
- ackend/: Core API logic (FastAPI)
  - pp/auth/: JWT handling
  - pp/middleware/: Zero Trust continuous verification logic
  - pp/routes/: Authentication and protected endpoints
  - pp/services/: User lookup and authentication
  - pp/utils/: Password hashing and logging
  - logs/: Security audit logs (\security.log\)
- \rontend/\: Interactive React dashboard (Vite + TypeScript)
  - \src/App.tsx\: Main logic for login and dashboard access
- \experiments/\: Python attack simulation scripts

## 🚀 Getting Started

### 1. Run the Backend API
\\\ash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
\\\

### 2. Run the Frontend Dashboard
\\\ash
cd frontend
npm install
npm run dev
\\\

### 3. Run Attack Simulations
(Ensure the API is running in another terminal)
\\\ash
cd experiments
python attack_tests.py
\\\

## 🔐 Zero Trust Features
- **Continuous Verification:** Every request checks the JWT payload against the current client IP and User-Agent.
- **Short-lived Tokens:** Tokens expire after 15 minutes by default.
- **Security Logging:** All login attempts and verification failures are logged in \ackend/logs/security.log\.
- **RBAC:** Routes are protected by roles (\dmin\, \user\).

## 🧪 Testing Results
The \experiments/attack_tests.py\ script simulates:
1. **Token Theft:** Using a stolen token from a different device/browser.
2. **Role Escalation:** Tampering with a JWT to gain admin privileges.
3. **Access Control:** Attempting to access admin-only routes with a standard user token.
