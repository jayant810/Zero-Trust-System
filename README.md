# 🛡️ Advanced Zero Trust Security System

A research-grade full-stack security architecture featuring a FastAPI backend with a dynamic Risk Engine and a React/TypeScript frontend.

## 🚀 Key Zero Trust Capabilities

1.  **Contextual Binding:** Tokens are strictly bound to the client's **IP address** and a unique **Device Fingerprint**.
2.  **Risk-Based Decision Engine:** Every request is assigned a real-time **Risk Score (0-100)** based on context anomalies (IP change, fingerprint mismatch, time-of-day, etc.).
3.  **Policy Enforcement Layer:** Adaptive access control where different endpoints have varying risk tolerances (e.g., `/admin` is "Strict", `/dashboard` is "Normal").
4.  **Dual-Token Lifecycle:** Implementation of short-lived **Access Tokens** (15m) and long-lived **Refresh Tokens** (7d) with rotation.
5.  **Replay Attack Prevention:** Unique **JTI (JWT ID)** tracking for every token to prevent reuse of stolen credentials.
6.  **Enhanced Device Fingerprinting:** Multi-attribute hashing (screen resolution, timezone, language, hardware concurrency) to verify device identity beyond the User-Agent.
7.  **Backend Persistence:** A SQLite-backed **Security Audit Log** and Token Blacklist for persistent event analysis and session invalidation.
8.  **Session Invalidation:** Immediate global revocation via a `/logout` endpoint and blacklist.
9.  **Rate Limiting:** Integrated brute-force protection on authentication endpoints.
10. **Endpoint Classification:** Routes are categorized by sensitivity, applying "Strict" vs "Moderate" security policies dynamically.

## 📁 Project Structure
- `backend/`: FastAPI Application
  - `app/middleware/zero_trust.py`: The core verification engine.
  - `app/services/risk_service.py`: Real-time risk scoring and policy mapping.
  - `app/utils/database.py`: SQLite persistence for JTI tracking and blacklisting.
  - `logs/zero_trust.db`: Persistent security event store.
- `frontend/`: React Dashboard (Vite + TS)
  - `src/App.tsx`: Interactive lab with attack simulations and risk score visualization.
- `experiments/`: Research scripts for automated attack testing.

## ⚙️ Getting Started

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Simulation Scenarios
- **Device Fingerprint Mismatch:** Attempts to use a valid token from a device with a different hardware/browser profile.
- **Admin Security Breach:** Simulates access to strict resources with a moderate risk score, demonstrating adaptive blocking.
- **Brute Force Detection:** Triggers rate limiting after 5 rapid login attempts.
- **Session Revocation:** Verifies that tokens are immediately invalidated upon logout.
