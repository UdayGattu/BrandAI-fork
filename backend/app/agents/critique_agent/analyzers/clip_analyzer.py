"""
CLIP-based analyzer for logo and product similarity matching.
Uses CLIP model to compare generated ads with brand assets.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

from app.services.logger import app_logger


class CLIPAnalyzer:
    """Analyze images using CLIP for similarity matching."""
    
    def __init__(self):
        """Initialize CLIP analyzer."""
        self.logger = app_logger
        self.model = None
        self.preprocess = None
        self._initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize CLIP model."""
        try:
            import clip
            
            # Load CLIP model
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model, self.preprocess = clip.load("ViT-B/32", device=device)
            self.device = device
            self._initialized = True
            
            self.logger.info(f"CLIP model loaded on {device}")
        except ImportError:
            self.logger.warning("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")
            self._initialized = False
        except Exception as e:
            self.logger.error(f"Error initializing CLIP: {e}")
            self._initialized = False
    
    def encode_image(self, image_path: Path) -> Optional[torch.Tensor]:
        """
        Encode image to CLIP embedding.
        
        Args:
            image_path: Path to image file
        
        Returns:
            CLIP embedding tensor, or None if error
        """
        if not self._initialized:
            self.logger.warning("CLIP not initialized, cannot encode image")
            return None
        
        try:
            image = Image.open(image_path).convert("RGB")
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                # Normalize features
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features
        except Exception as e:
            self.logger.error(f"Error encoding image {image_path}: {e}")
            return None
    
    def encode_text(self, text: str) -> Optional[torch.Tensor]:
        """
        Encode text to CLIP embedding.
        
        Args:
            text: Text description
        
        Returns:
            CLIP embedding tensor, or None if error
        """
        if not self._initialized:
            self.logger.warning("CLIP not initialized, cannot encode text")
            return None
        
        try:
            text_tokens = clip.tokenize([text]).to(self.device)
            
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                # Normalize features
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            return text_features
        except Exception as e:
            self.logger.error(f"Error encoding text: {e}")
            return None
    
    def compute_similarity(
        self,
        embedding1: torch.Tensor,
        embedding2: torch.Tensor
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding tensor
            embedding2: Second embedding tensor
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            # Compute cosine similarity
            similarity = torch.cosine_similarity(embedding1, embedding2)
            # Convert to float and ensure 0-1 range
            score = float(similarity.item())
            return max(0.0, min(1.0, score))
        except Exception as e:
            self.logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def match_logo(
        self,
        ad_image_path: Path,
        logo_image_path: Path
    ) -> Dict:
        """
        Match logo in generated ad with brand logo.
        
        Args:
            ad_image_path: Path to generated ad image
            logo_image_path: Path to brand logo image
        
        Returns:
            Dictionary with matching results:
            - similarity_score: float (0.0 to 1.0)
            - logo_detected: bool
            - confidence: float
        """
        if not self._initialized:
            return {
                "similarity_score": 0.0,
                "logo_detected": False,
                "confidence": 0.0,
                "error": "CLIP not initialized"
            }
        
        try:
            # Encode both images
            ad_embedding = self.encode_image(ad_image_path)
            logo_embedding = self.encode_image(logo_image_path)
            
            if ad_embedding is None or logo_embedding is None:
                return {
                    "similarity_score": 0.0,
                    "logo_detected": False,
                    "confidence": 0.0,
                    "error": "Failed to encode images"
                }
            
            # Compute similarity
            similarity = self.compute_similarity(ad_embedding, logo_embedding)
            
            # Threshold for logo detection (adjustable)
            threshold = 0.3
            logo_detected = similarity >= threshold
            
            return {
                "similarity_score": similarity,
                "logo_detected": logo_detected,
                "confidence": similarity,
                "threshold": threshold
            }
        except Exception as e:
            self.logger.error(f"Error matching logo: {e}")
            return {
                "similarity_score": 0.0,
                "logo_detected": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def match_product(
        self,
        ad_image_path: Path,
        product_image_path: Path
    ) -> Dict:
        """
        Match product in generated ad with reference product image.
        
        Args:
            ad_image_path: Path to generated ad image
            product_image_path: Path to reference product image
        
        Returns:
            Dictionary with matching results:
            - similarity_score: float (0.0 to 1.0)
            - product_detected: bool
            - confidence: float
        """
        if not self._initialized:
            return {
                "similarity_score": 0.0,
                "product_detected": False,
                "confidence": 0.0,
                "error": "CLIP not initialized"
            }
        
        try:
            # Encode both images
            ad_embedding = self.encode_image(ad_image_path)
            product_embedding = self.encode_image(product_image_path)
            
            if ad_embedding is None or product_embedding is None:
                return {
                    "similarity_score": 0.0,
                    "product_detected": False,
                    "confidence": 0.0,
                    "error": "Failed to encode images"
                }
            
            # Compute similarity
            similarity = self.compute_similarity(ad_embedding, product_embedding)
            
            # Threshold for product detection (adjustable)
            threshold = 0.4
            product_detected = similarity >= threshold
            
            return {
                "similarity_score": similarity,
                "product_detected": product_detected,
                "confidence": similarity,
                "threshold": threshold
            }
        except Exception as e:
            self.logger.error(f"Error matching product: {e}")
            return {
                "similarity_score": 0.0,
                "product_detected": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def analyze_ad(
        self,
        ad_image_path: Path,
        logo_image_path: Optional[Path] = None,
        product_image_path: Optional[Path] = None
    ) -> Dict:
        """
        Analyze ad image for logo and product matching.
        
        Args:
            ad_image_path: Path to generated ad image
            logo_image_path: Optional path to brand logo
            product_image_path: Optional path to product image
        
        Returns:
            Dictionary with all analysis results
        """
        results = {
            "ad_path": str(ad_image_path),
            "clip_initialized": self._initialized
        }
        
        if logo_image_path and logo_image_path.exists():
            logo_match = self.match_logo(ad_image_path, logo_image_path)
            results["logo_match"] = logo_match
        
        if product_image_path and product_image_path.exists():
            product_match = self.match_product(ad_image_path, product_image_path)
            results["product_match"] = product_match
        
        return results


# Global CLIP analyzer instance
clip_analyzer = CLIPAnalyzer()
