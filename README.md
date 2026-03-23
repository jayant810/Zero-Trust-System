# 🛡️ Zero Trust Authentication System

A FastAPI-based web API with Continuous Verification and Role-Based Access Control.

## 📁 Project Structure
- `backend/`: Core API logic
  - `app/auth/`: JWT handling
  - `app/middleware/`: Zero Trust continuous verification logic
  - `app/routes/`: Authentication and protected endpoints
  - `app/services/`: User lookup and authentication
  - `app/utils/`: Password hashing and logging
- `experiments/`: Attack simulation scripts
- `logs/`: Security audit logs

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Run the API**
   ```bash
   cd backend/app
   uvicorn main:app --reload
   ```

3. **Run Attack Simulations**
   (Ensure the API is running in another terminal)
   ```bash
   python experiments/attack_tests.py
   ```

## 🔒 Zero Trust Features
- **Continuous Verification:** Every request checks the JWT payload against the current client IP and User-Agent.
- **Short-lived Tokens:** Tokens expire after 15 minutes by default.
- **Security Logging:** All login attempts and verification failures are logged in `logs/security.log`.
- **RBAC:** Routes are protected by roles (`admin`, `user`).

## 🧪 Testing Results
The `experiments/attack_tests.py` script simulates:
1. **Token Theft:** Using a stolen token from a different device/browser.
2. **Role Escalation:** Tampering with a JWT to gain admin privileges.
3. **Access Control:** Attempting to access admin-only routes with a standard user token.
