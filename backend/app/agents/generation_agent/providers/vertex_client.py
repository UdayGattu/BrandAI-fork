"""
Shared Vertex AI client for GCP services.
Handles authentication and initialization for Imagen and Veo.
"""
import os
from typing import Optional
from google.cloud import aiplatform
from google.oauth2 import service_account

from app.config import settings
from app.services.logger import app_logger


class VertexAIClient:
    """Shared Vertex AI client for GCP services."""
    
    def __init__(self):
        """Initialize Vertex AI client."""
        self.logger = app_logger
        self.project_id = settings.GCP_PROJECT_ID
        self.region = settings.GCP_REGION
        self._client = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize Vertex AI client.
        
        Returns:
            True if initialized successfully, False otherwise
        """
        if self._initialized:
            return True
        
        try:
            # Set credentials if provided
            creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
            if os.path.exists(creds_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
                self.logger.info(f"Using credentials from: {creds_path}")
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.region
            )
            
            self._initialized = True
            self.logger.info(
                f"Vertex AI initialized: project={self.project_id}, region={self.region}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Vertex AI: {e}")
            return False
    
    def get_client(self):
        """
        Get initialized Vertex AI client.
        
        Returns:
            Initialized client or None
        """
        if not self._initialized:
            if not self.initialize():
                return None
        
        return aiplatform
    
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._initialized
    
    def get_project_id(self) -> str:
        """Get GCP project ID."""
        return self.project_id
    
    def get_region(self) -> str:
        """Get GCP region."""
        return self.region


# Global Vertex AI client instance
vertex_client = VertexAIClient()
