"""
OpenCV-based image processor for critique agent.
Handles blur detection, color extraction, and basic quality checks.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image

from app.services.logger import app_logger


class ImageProcessor:
    """Process images for quality and feature extraction."""
    
    def __init__(self):
        """Initialize image processor."""
        self.logger = app_logger
    
    def load_image(self, image_path: Path) -> Optional[np.ndarray]:
        """
        Load image from file path.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Image as numpy array (BGR format), or None if error
        """
        try:
            if not image_path.exists():
                self.logger.error(f"Image file not found: {image_path}")
                return None
            
            image = cv2.imread(str(image_path))
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return None
            
            return image
        except Exception as e:
            self.logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def detect_blur(self, image: np.ndarray, threshold: float = 100.0) -> Dict:
        """
        Detect blur in image using Laplacian variance.
        
        Higher variance = sharper image
        Lower variance = blurrier image
        
        Args:
            image: Image as numpy array (BGR)
            threshold: Blur threshold (default: 100.0)
        
        Returns:
            Dictionary with blur detection results:
            - is_blurry: bool
            - blur_score: float (Laplacian variance)
            - threshold: float
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            is_blurry = variance < threshold
            
            return {
                "is_blurry": is_blurry,
                "blur_score": float(variance),
                "threshold": threshold,
                "quality": "sharp" if not is_blurry else "blurry"
            }
        except Exception as e:
            self.logger.error(f"Error detecting blur: {e}")
            return {
                "is_blurry": True,
                "blur_score": 0.0,
                "threshold": threshold,
                "error": str(e)
            }
    
    def extract_colors(self, image: np.ndarray, num_colors: int = 5) -> Dict:
        """
        Extract dominant colors from image using histogram method.
        
        Args:
            image: Image as numpy array (BGR)
            num_colors: Number of dominant colors to extract
        
        Returns:
            Dictionary with color information:
            - dominant_colors: List of hex color codes
            - color_percentages: List of percentages
            - primary_color: str (hex)
        """
        # Use histogram method (no external dependencies)
        return self._extract_colors_histogram(image, num_colors)
    
    def _extract_colors_histogram(self, image: np.ndarray, num_colors: int = 5) -> Dict:
        """Fallback color extraction using histogram."""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Reshape to 2D
            pixels = rgb_image.reshape(-1, 3)
            
            # Simple histogram-based approach
            # Quantize colors to reduce palette
            quantized = (pixels // 32) * 32  # Quantize to 8 levels per channel
            
            # Get unique colors and counts
            unique_colors, counts = np.unique(quantized, axis=0, return_counts=True)
            
            # Sort by count
            sorted_indices = np.argsort(counts)[::-1][:num_colors]
            top_colors = unique_colors[sorted_indices]
            top_counts = counts[sorted_indices]
            
            # Calculate percentages
            total = counts.sum()
            percentages = (top_counts / total * 100).tolist()
            
            # Convert to hex
            hex_colors = [f"#{int(r):02x}{int(g):02x}{int(b):02x}" for r, g, b in top_colors]
            
            return {
                "dominant_colors": hex_colors,
                "color_percentages": percentages,
                "primary_color": hex_colors[0] if hex_colors else None,
                "num_colors": len(hex_colors)
            }
        except Exception as e:
            self.logger.error(f"Error in histogram color extraction: {e}")
            return {
                "dominant_colors": [],
                "color_percentages": [],
                "primary_color": None,
                "error": str(e)
            }
    
    def check_basic_quality(self, image: np.ndarray) -> Dict:
        """
        Perform basic quality checks on image.
        
        Args:
            image: Image as numpy array (BGR)
        
        Returns:
            Dictionary with quality metrics:
            - resolution: Tuple (width, height)
            - aspect_ratio: float
            - brightness: float (0-255)
            - contrast: float
            - has_artifacts: bool (basic check)
        """
        try:
            height, width = image.shape[:2]
            resolution = (width, height)
            aspect_ratio = width / height if height > 0 else 0
            
            # Convert to grayscale for brightness/contrast
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate brightness (mean pixel value)
            brightness = float(np.mean(gray))
            
            # Calculate contrast (standard deviation)
            contrast = float(np.std(gray))
            
            # Basic artifact detection (check for extreme values)
            # Artifacts often show as very bright or very dark patches
            has_artifacts = False
            if np.any(gray > 250) and np.any(gray < 5):
                # Very bright and very dark regions might indicate artifacts
                has_artifacts = True
            
            return {
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "brightness": brightness,
                "contrast": contrast,
                "has_artifacts": has_artifacts,
                "pixel_count": width * height
            }
        except Exception as e:
            self.logger.error(f"Error checking basic quality: {e}")
            return {
                "resolution": (0, 0),
                "aspect_ratio": 0.0,
                "brightness": 0.0,
                "contrast": 0.0,
                "has_artifacts": True,
                "error": str(e)
            }
    
    def process_image(self, image_path: Path) -> Dict:
        """
        Process image and extract all features.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with all processing results:
            - blur_detection: Dict
            - colors: Dict
            - quality: Dict
            - success: bool
        """
        self.logger.info(f"Processing image: {image_path}")
        
        image = self.load_image(image_path)
        if image is None:
            return {
                "success": False,
                "error": "Failed to load image"
            }
        
        # Perform all analyses
        blur_result = self.detect_blur(image)
        color_result = self.extract_colors(image)
        quality_result = self.check_basic_quality(image)
        
        return {
            "success": True,
            "image_path": str(image_path),
            "blur_detection": blur_result,
            "colors": color_result,
            "quality": quality_result
        }
    
    def extract_frame_from_video(self, video_path: Path, frame_number: int = 0) -> Optional[np.ndarray]:
        """
        Extract a frame from video for analysis.
        
        Args:
            video_path: Path to video file
            frame_number: Frame number to extract (0 = first frame)
        
        Returns:
            Frame as numpy array (BGR), or None if error
        """
        try:
            if not video_path.exists():
                self.logger.error(f"Video file not found: {video_path}")
                return None
            
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                self.logger.error(f"Failed to open video: {video_path}")
                return None
            
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                self.logger.error(f"Failed to read frame {frame_number} from video")
                return None
            
            return frame
        except Exception as e:
            self.logger.error(f"Error extracting frame from video: {e}")
            return None


# Global image processor instance
image_processor = ImageProcessor()
