"""
Configuration Management for ATS System
Handles environment variables, API keys, and system settings
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging


@dataclass
class LLMConfig:
    """LLM configuration for AutoGen agents"""
    provider: str = "openai"  # openai, azure, anthropic, google, ollama, none
    api_key: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 1000
    base_url: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///ats_system.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class AppConfig:
    """Application configuration"""
    name: str = "ATS Resume Scoring System"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "default-secret-key"
    session_timeout: int = 3600


@dataclass
class FileConfig:
    """File processing configuration"""
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = None
    upload_folder: str = "./uploads"
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ["pdf", "docx", "txt"]


@dataclass
class ScoringConfig:
    """Scoring algorithm configuration"""
    skills_weight: float = 0.30
    experience_weight: float = 0.25
    education_weight: float = 0.15
    format_weight: float = 0.15
    keywords_weight: float = 0.15
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to 1.0"""
        total = (self.skills_weight + self.experience_weight + 
                self.education_weight + self.format_weight + 
                self.keywords_weight)
        return abs(total - 1.0) < 0.001


class ConfigManager:
    """
    Central configuration manager for ATS system
    Loads settings from environment variables with fallback defaults
    """
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.load_environment()
        self.llm_config = self._load_llm_config()
        self.database_config = self._load_database_config()
        self.app_config = self._load_app_config()
        self.file_config = self._load_file_config()
        self.scoring_config = self._load_scoring_config()
        
        # Setup logging
        self._setup_logging()
    
    def load_environment(self):
        """Load environment variables from .env file if it exists"""
        env_path = Path(self.env_file)
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                logging.info(f"Loaded environment from {env_path}")
            except ImportError:
                logging.warning("python-dotenv not installed, skipping .env file loading")
    
    def _load_llm_config(self) -> LLMConfig:
        """Load LLM configuration"""
        
        # Determine provider based on available API keys
        provider = os.getenv("LLM_PROVIDER", "none").lower()
        
        if provider == "none" or provider == "":
            # Auto-detect based on available API keys
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("AZURE_OPENAI_API_KEY"):
                provider = "azure"
            elif os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            elif os.getenv("GOOGLE_API_KEY"):
                provider = "google"
            elif os.getenv("OLLAMA_BASE_URL"):
                provider = "ollama"
            else:
                provider = "none"
        
        config = LLMConfig(provider=provider)
        
        if provider == "openai":
            config.api_key = os.getenv("OPENAI_API_KEY")
            config.model = os.getenv("OPENAI_MODEL", "gpt-4")
            config.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
        
        elif provider == "azure":
            config.api_key = os.getenv("AZURE_OPENAI_API_KEY")
            config.base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
            config.model = os.getenv("AZURE_OPENAI_MODEL", "gpt-4")
        
        elif provider == "anthropic":
            config.api_key = os.getenv("ANTHROPIC_API_KEY")
            config.model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        
        elif provider == "google":
            config.api_key = os.getenv("GOOGLE_API_KEY")
            config.model = os.getenv("GOOGLE_MODEL", "gemini-pro")
        
        elif provider == "ollama":
            config.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            config.model = os.getenv("OLLAMA_MODEL", "llama2")
            config.api_key = None  # Ollama doesn't need API key
        
        return config
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///ats_system.db"),
            echo=os.getenv("DATABASE_ECHO", "False").lower() == "true",
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
        )
    
    def _load_app_config(self) -> AppConfig:
        """Load application configuration"""
        return AppConfig(
            name=os.getenv("APP_NAME", "ATS Resume Scoring System"),
            version=os.getenv("APP_VERSION", "1.0.0"),
            debug=os.getenv("DEBUG_MODE", "False").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            secret_key=os.getenv("SECRET_KEY", "default-secret-key-change-in-production"),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600"))
        )
    
    def _load_file_config(self) -> FileConfig:
        """Load file processing configuration"""
        extensions = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx,txt").split(",")
        return FileConfig(
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            allowed_extensions=[ext.strip() for ext in extensions],
            upload_folder=os.getenv("UPLOAD_FOLDER", "./uploads")
        )
    
    def _load_scoring_config(self) -> ScoringConfig:
        """Load scoring algorithm configuration"""
        config = ScoringConfig(
            skills_weight=float(os.getenv("SCORING_WEIGHTS_SKILLS", "0.30")),
            experience_weight=float(os.getenv("SCORING_WEIGHTS_EXPERIENCE", "0.25")),
            education_weight=float(os.getenv("SCORING_WEIGHTS_EDUCATION", "0.15")),
            format_weight=float(os.getenv("SCORING_WEIGHTS_FORMAT", "0.15")),
            keywords_weight=float(os.getenv("SCORING_WEIGHTS_KEYWORDS", "0.15"))
        )
        
        if not config.validate_weights():
            logging.warning("Scoring weights do not sum to 1.0, using defaults")
            config = ScoringConfig()  # Use defaults
        
        return config
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.app_config.log_level.upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('ats_system.log')
            ]
        )
    
    def get_autogen_config(self) -> Dict[str, Any]:
        """
        Get AutoGen configuration for LLM-based agents
        Returns None if no LLM provider is configured (pure Python mode)
        """
        
        if self.llm_config.provider == "none" or not self.llm_config.api_key:
            logging.info("No LLM provider configured - using pure Python agents")
            return None
        
        # AutoGen 0.7+ format - simplified config
        config = {
            "model": self.llm_config.model,
        }
        
        if self.llm_config.provider == "openai":
            config.update({
                "api_key": self.llm_config.api_key,
            })
        
        elif self.llm_config.provider == "azure":
            config.update({
                "api_key": self.llm_config.api_key,
                "base_url": self.llm_config.base_url,
                "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
            })
        
        elif self.llm_config.provider == "ollama":
            config.update({
                "base_url": self.llm_config.base_url,
            })
        
        return config
    
    def is_llm_enabled(self) -> bool:
        """Check if LLM functionality is enabled"""
        return (self.llm_config.provider != "none" and 
                (self.llm_config.api_key is not None or 
                 self.llm_config.provider == "ollama"))
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for debugging"""
        return {
            "llm_provider": self.llm_config.provider,
            "llm_enabled": self.is_llm_enabled(),
            "database_type": self.database_config.url.split("://")[0],
            "debug_mode": self.app_config.debug,
            "upload_folder": self.file_config.upload_folder,
            "max_file_size_mb": self.file_config.max_file_size / (1024 * 1024)
        }


# Global configuration instance
config = ConfigManager()


# Utility functions for easy access
def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config


def is_llm_enabled() -> bool:
    """Check if LLM functionality is enabled"""
    return config.is_llm_enabled()


def get_autogen_config() -> Optional[Dict[str, Any]]:
    """Get AutoGen configuration if available"""
    return config.get_autogen_config()


# Example usage and testing
def test_configuration():
    """Test configuration loading"""
    
    print("=== ATS System Configuration ===")
    print(f"Environment Info: {config.get_environment_info()}")
    
    print(f"\nLLM Configuration:")
    print(f"  Provider: {config.llm_config.provider}")
    print(f"  Model: {config.llm_config.model}")
    print(f"  Enabled: {config.is_llm_enabled()}")
    
    print(f"\nDatabase Configuration:")
    print(f"  URL: {config.database_config.url}")
    
    print(f"\nScoring Configuration:")
    print(f"  Skills Weight: {config.scoring_config.skills_weight}")
    print(f"  Experience Weight: {config.scoring_config.experience_weight}")
    print(f"  Weights Valid: {config.scoring_config.validate_weights()}")
    
    autogen_config = get_autogen_config()
    if autogen_config:
        print(f"\nAutoGen Configuration Available: {list(autogen_config.keys())}")
    else:
        print(f"\nAutoGen Configuration: Pure Python mode (no LLM)")


if __name__ == "__main__":
    test_configuration()
