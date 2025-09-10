import streamlit as st
import sqlite3
import hashlib
from typing import Optional, Dict
import jwt
from datetime import datetime, timedelta, timezone
from src.config.settings import settings

class AuthManager:
    def __init__(self, db_path: str = "studyai.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                total_quizzes INTEGER DEFAULT 0,
                total_score REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _generate_jwt_token(self, user_id: int) -> str:
        """Generate JWT token"""
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(days=1),
            'iat': datetime.now(timezone.utc),
            'sub': str(user_id)  # <-- FIX: Convert user_id to string
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def verify_token(self, token: str) -> Optional[int]:
        """Verify JWT token and return user_id if valid"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return int(payload['sub'])  # <-- FIX: Convert subject back to integer
        except jwt.ExpiredSignatureError:
            st.error("Session has expired. Please log in again.")
            print("❌ JWT Error: Token has expired.")
            return None
        except jwt.InvalidTokenError as e:
            st.error("Invalid token. Please log in again.")
            print(f"❌ JWT Error: Invalid token. Reason: {e}")
            return None

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == hashed
    
    def register_user(self, username: str, email: str, password: str) -> bool:
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def login_user(self, username: str, password: str) -> Optional[Dict]:
        """Login user and return user data along with JWT token"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, email, password_hash, total_quizzes, total_score FROM users WHERE username = ?",
                (username,)
            )
            
            user_row = cursor.fetchone()
            
            if user_row:
                stored_password_hash = user_row['password_hash']
                
                if self.verify_password(password, stored_password_hash):
                    user_id = user_row['id']
                    token = self._generate_jwt_token(user_id)
                    
                    user_data = {
                        'id': user_id,
                        'username': user_row['username'],
                        'email': user_row['email'],
                        'total_quizzes': user_row['total_quizzes'] if user_row['total_quizzes'] else 0,
                        'total_score': user_row['total_score'] if user_row['total_score'] else 0.0,
                        'token': token
                    }
                    
                    conn.close()
                    return user_data
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated via a valid JWT in session state"""
        if 'token' in st.session_state and st.session_state.token:
            user_id = self.verify_token(st.session_state.token)
            if user_id:
                return True
        
        if 'user' in st.session_state:
            del st.session_state.user
        if 'token' in st.session_state:
            del st.session_state.token
        return False

    def get_current_user(self) -> Optional[Dict]:
        """Get current logged in user"""
        if self.is_authenticated():
            return st.session_state.user
        return None
    
    def logout(self):
        """Logout current user and clear ALL session data"""
        keys_to_clear = [
            'user', 'token', 'quiz_manager', 'quiz_generated', 'quiz_submitted',
            'current_topic', 'current_sub_topic', 'current_difficulty',
            'viewing_quiz_id', 'view_mode', 'show_history', 'retake_topic',
            'retake_difficulty', 'retake_type', 'retake_questions', 'rerun_trigger'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.rerun()