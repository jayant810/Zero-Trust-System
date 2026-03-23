from datetime import datetime
from typing import Optional
from app.utils.database import SessionLocal, TokenBlacklist

class RiskService:
    @staticmethod
    def calculate_risk_score(
        current_ip: str, 
        current_fingerprint: str, 
        payload_ip: str, 
        payload_fingerprint: str,
        user_sub: str
    ) -> int:
        score = 0
        
        # 1. IP Context (Moderate Risk)
        if current_ip != payload_ip:
            score += 30
            
        # 2. Fingerprint Context (High Risk)
        if current_fingerprint != payload_fingerprint:
            score += 50
            
        # 3. Time-of-Day Anomaly (Low Risk - e.g., 1 AM to 5 AM)
        hour = datetime.utcnow().hour
        if 1 <= hour <= 5:
            score += 15
            
        # 4. History Check: Recent Revocations for this User
        db = SessionLocal()
        recent_revocations = db.query(TokenBlacklist).filter(
            TokenBlacklist.user_sub == user_sub,
            TokenBlacklist.token_type == 'access'
        ).count()
        db.close()
        
        if recent_revocations > 2:
            score += 20

        return min(score, 100)

    @staticmethod
    def get_action_for_score(score: int, sensitivity: str = "normal") -> str:
        # Sensitivity-based thresholds
        thresholds = {
            "strict": 20,  # Admin routes
            "normal": 60,  # Standard routes
            "low": 90      # Public/Utility
        }
        
        limit = thresholds.get(sensitivity, 60)
        
        if score >= limit:
            return "BLOCK"
        elif score >= (limit / 2):
            return "MONITOR"
        return "ALLOW"
