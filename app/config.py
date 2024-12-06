# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Application Settings
    PORT = int(os.getenv('PORT', 8501))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/app.log')

    # File Processing Settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50))
    ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'csv,xlsx,xls').split(',')

    # Output Configuration
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'outputs'))
    JSON_PREFIX = os.getenv('JSON_PREFIX', 'reconciliation_')

    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        Path(cls.LOG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_allowed_extensions(cls):
        """Get list of allowed file extensions."""
        return [f'.{ext.strip()}' for ext in cls.ALLOWED_FILE_TYPES]