import os
from dotenv import load_dotenv

load_dotenv()

class Settings():

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Add these new JWT settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key") # Default for safety
    JWT_ALGORITHM = "HS256"
    
    print(f"✅ Loaded JWT Secret Key: '{JWT_SECRET_KEY[:10]}...'")


    MODEL_NAME = "llama-3.1-8b-instant"
    
    TEMPERATURE = 0.9

    MAX_RETRIES = 3


settings = Settings()