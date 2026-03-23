import httpx
import asyncio
import json
from jose import jwt

BASE_URL = "http://127.0.0.1:8000"
SECRET_KEY = "SUPER_SECRET_KEY_REPLACE_ME" # Must match backend
ALGORITHM = "HS256"

async def run_attack_simulations():
    print("🚀 Starting Zero Trust Attack Simulations...\n")

    # 1. Setup: Get a valid token
    async with httpx.AsyncClient() as client:
        print("--- [ SETUP ] Logging in to get valid token ---")
        login_res = await client.post(f"{BASE_URL}/auth/login", data={
            "username": "user@zero.trust",
            "password": "user123"
        })
        
        if login_res.status_code != 200:
            print("❌ Setup failed: Could not login. Is the server running?")
            return

        token = login_res.json()["access_token"]
        print("✅ Token acquired.\n")

        # --- ATTACK 1: Device Context Mismatch ---
        print("🔥 [ ATTACK 1 ] Simulating Token Theft (Different Device)")
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Hacker-Browser-9000" # Different from the login UA
        }
        res = await client.get(f"{BASE_URL}/api/dashboard", headers=headers)
        print(f"Result: Status {res.status_code}, Detail: {res.json().get('detail')}")
        if res.status_code == 403:
            print("🛡️  SUCCESS: Zero Trust blocked the request due to Device Mismatch.\n")
        else:
            print("❌ FAILURE: Zero Trust did not block the device change.\n")

        # --- ATTACK 2: Role Escalation (Modified Token) ---
        print("🔥 [ ATTACK 2 ] Simulating Role Escalation (Modifying JWT)")
        # Decode, modify, and re-sign
        # python-jose requires a key even if verify_signature is False
        payload = jwt.decode(token, key="", options={"verify_signature": False})
        payload["role"] = "admin"
        # We try to re-sign it with a wrong key (attacker doesn't know the real one)
        fake_token = jwt.encode(payload, "WRONG_SECRET", algorithm=ALGORITHM)
        
        headers = {"Authorization": f"Bearer {fake_token}"}
        res = await client.get(f"{BASE_URL}/api/admin", headers=headers)
        print(f"Result: Status {res.status_code}, Detail: {res.json().get('detail')}")
        if res.status_code == 401:
            print("🛡️  SUCCESS: System rejected the tampered token signature.\n")
        else:
            print("❌ FAILURE: System accepted a tampered token.\n")

        # --- ATTACK 3: Unauthorized Access (Admin Route with User Token) ---
        print("🔥 [ ATTACK 3 ] Simulating Unauthorized Access (User -> Admin Route)")
        headers = {"Authorization": f"Bearer {token}"}
        # Re-using the same User-Agent as login for this one
        headers["User-Agent"] = login_res.request.headers.get("user-agent")
        
        res = await client.get(f"{BASE_URL}/api/admin", headers=headers)
        print(f"Result: Status {res.status_code}, Detail: {res.json().get('detail')}")
        if res.status_code == 403:
            print("🛡️  SUCCESS: RBAC blocked the user from the admin route.\n")
        else:
            print("❌ FAILURE: User was able to access the admin route.\n")

if __name__ == "__main__":
    asyncio.run(run_attack_simulations())
