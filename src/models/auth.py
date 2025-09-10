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

    def _add_column_safe(self, cursor, column_name: str, column_type: str):
        """Safely add a column to the users table if it doesn't exist."""
        try:
            cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
        except sqlite3.OperationalError as e:
            if f"duplicate column name: {column_name}" not in str(e):
                raise e # Re-raise error if it's not about a duplicate column

    def init_database(self):
        """Initialize the database and add new columns safely."""
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
        
        # Safely add the new column for the SaaS feature
        self._add_column_safe(cursor, "has_used_rag_trial", "BOOLEAN DEFAULT 0")
        
        conn.commit()
        conn.close()
    
    def _generate_jwt_token(self, user_id: int) -> str:
        """Generate JWT token"""
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(days=1),
            'iat': datetime.now(timezone.utc),
            'sub': str(user_id)
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def verify_token(self, token: str) -> Optional[int]:
        """Verify JWT token and return user_id if valid"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return int(payload['sub'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
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
        """Login user and return user data including RAG trial status."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, email, password_hash, has_used_rag_trial FROM users WHERE username = ?",
                (username,)
            )
            
            user_row = cursor.fetchone()
            
            if user_row and self.verify_password(password, user_row['password_hash']):
                user_id = user_row['id']
                token = self._generate_jwt_token(user_id)
                user_data = {
                    'id': user_id,
                    'username': user_row['username'],
                    'email': user_row['email'],
                    'has_used_rag_trial': user_row['has_used_rag_trial'],
                    'token': token
                }
                conn.close()
                return user_data
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Login error: {e}")
            return None

    def mark_rag_trial_as_used(self, user_id: int):
        """Update the database to mark the user's RAG trial as used."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET has_used_rag_trial = 1 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating RAG trial status: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated via a valid JWT in session state"""
        if 'token' in st.session_state and st.session_state.token:
            user_id = self.verify_token(st.session_state.token)
            if user_id:
                return True
        
        keys_to_clear = ['user', 'token']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        return False

    def get_current_user(self) -> Optional[Dict]:
        """Get current logged in user"""
        return st.session_state.get('user')

    def logout(self):
        """Logout current user and clear ALL session data"""
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            del st.session_state[key]
        st.rerun()