"""
Content generation service for PocketFlow.

This module provides content generation functionality for different types of content.
"""

import os
import subprocess
import tempfile
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

from ..core.types import ContentGenerationRequest, ContentType
from ..config.settings import get_settings
from ..utils.errors import ContentGenerationError
from ..utils.logging import get_logger


class ContentService:
    """Service for generating different types of content."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("ContentService")
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        output_dir = Path(self.settings.CONTENT_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Content output directory: {output_dir}")
    
    def generate_content(self, request: ContentGenerationRequest) -> Optional[str]:
        """
        Generate content based on the request.
        
        Args:
            request: ContentGenerationRequest with generation parameters
            
        Returns:
            Path to the generated file, or None if generation failed
            
        Raises:
            ContentGenerationError: If content generation fails
        """
        try:
            self.logger.info(f"Generating {request.content_type} content: {request.prompt}")
            
            if request.content_type == ContentType.SOUND:
                return self._generate_sound(request)
            elif request.content_type == ContentType.IMAGE:
                return self._generate_image(request)
            elif request.content_type == ContentType.DOCUMENT:
                return self._generate_document(request)
            elif request.content_type == ContentType.PODCAST:
                return self._generate_podcast(request)
            elif request.content_type == ContentType.SONG:
                return self._generate_song(request)
            else:
                raise ContentGenerationError(f"Unsupported content type: {request.content_type}")
                
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise ContentGenerationError(f"Content generation failed: {e}")
    
    def _generate_sound(self, request: ContentGenerationRequest) -> Optional[str]:
        """Generate sound content."""
        try:
            # Use audiocraft for sound generation
            output_path = self._get_output_path("sound", "wav")
            
            # Create a simple script to generate sound
            script_content = f"""
import torch
from audiocraft.models import MusicGen
import torchaudio

# Load model
model = MusicGen.get_pretrained('melody')
model.set_generation_params(duration={request.duration or 10})

# Generate audio
wav = model.generate(["{request.prompt}"])
wav = wav.squeeze(0)

# Save audio
torchaudio.save("{output_path}", wav, 32000)
"""
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            # Execute script
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Clean up script
            os.unlink(script_path)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"Sound generated: {output_path}")
                return output_path
            else:
                self.logger.error(f"Sound generation failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Sound generation error: {e}")
            return None
    
    def _generate_image(self, request: ContentGenerationRequest) -> Optional[str]:
        """Generate image content."""
        try:
            # Use stable diffusion or similar for image generation
            output_path = self._get_output_path("image", "png")
            
            # For now, create a placeholder image
            # TODO: Integrate with actual image generation service
            self._create_placeholder_image(output_path, request.prompt)
            
            self.logger.info(f"Image generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Image generation error: {e}")
            return None
    
    def _generate_document(self, request: ContentGenerationRequest) -> Optional[str]:
        """Generate document content."""
        try:
            output_path = self._get_output_path("document", "pdf")
            
            # Create a simple document based on the prompt
            document_content = self._create_document_content(request.prompt)
            
            # Save as PDF (simplified - in real implementation, use proper PDF library)
            with open(output_path, 'w') as f:
                f.write(document_content)
            
            self.logger.info(f"Document generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Document generation error: {e}")
            return None
    
    def _generate_podcast(self, request: ContentGenerationRequest) -> Optional[str]:
        """Generate podcast content."""
        try:
            output_path = self._get_output_path("podcast", "mp3")
            
            # For now, create a simple audio file
            # TODO: Integrate with podcast generation service
            self._create_placeholder_audio(output_path, request.prompt, request.duration or 60)
            
            self.logger.info(f"Podcast generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Podcast generation error: {e}")
            return None
    
    def _generate_song(self, request: ContentGenerationRequest) -> Optional[str]:
        """Generate song content."""
        try:
            output_path = self._get_output_path("song", "mp3")
            
            # Use audiocraft for song generation (similar to sound generation)
            return self._generate_sound(request)
            
        except Exception as e:
            self.logger.error(f"Song generation error: {e}")
            return None
    
    def _get_output_path(self, content_type: str, extension: str) -> str:
        """Get output path for generated content."""
        import uuid
        filename = f"{content_type}_{uuid.uuid4().hex[:8]}.{extension}"
        return os.path.join(self.settings.CONTENT_OUTPUT_DIR, filename)
    
    def _create_placeholder_image(self, output_path: str, prompt: str):
        """Create a placeholder image (for testing)."""
        try:
            # Create a simple text-based image
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a blank image
            img = Image.new('RGB', (512, 512), color='white')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Wrap text
            words = prompt.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if len(test_line) * 10 > 480:  # Approximate width
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            # Draw text
            y_position = 50
            for line in lines[:10]:  # Limit to 10 lines
                draw.text((50, y_position), line, fill='black', font=font)
                y_position += 30
            
            img.save(output_path)
            
        except Exception as e:
            self.logger.warning(f"Failed to create placeholder image: {e}")
            # Create a simple text file as fallback
            with open(output_path, 'w') as f:
                f.write(f"Placeholder image for: {prompt}")
    
    def _create_placeholder_audio(self, output_path: str, prompt: str, duration: int):
        """Create a placeholder audio file (for testing)."""
        try:
            # Create a simple sine wave as placeholder
            import numpy as np
            import soundfile as sf
            
            # Generate a simple tone
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 440  # A4 note
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            # Save as audio file
            sf.write(output_path, audio, sample_rate)
            
        except Exception as e:
            self.logger.warning(f"Failed to create placeholder audio: {e}")
            # Create a simple text file as fallback
            with open(output_path, 'w') as f:
                f.write(f"Placeholder audio for: {prompt}")
    
    def _create_document_content(self, prompt: str) -> str:
        """Create document content based on prompt."""
        return f"""
# Generated Document

**Prompt:** {prompt}

## Content

This is a generated document based on your request: "{prompt}"

### Key Points

1. This is a placeholder document
2. In a real implementation, this would contain actual generated content
3. The content would be based on the provided prompt

### Summary

The document generation service is designed to create content based on user prompts. This is a demonstration of the system's capability to generate various types of content.

---
*Generated by PocketFlow Content Service*
"""
    
    def validate_content_type(self, content_type: str) -> bool:
        """Validate if the content type is supported."""
        try:
            ContentType(content_type)
            return True
        except ValueError:
            return False
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported content types."""
        return [ct.value for ct in ContentType]
    
    def get_content_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about generated content."""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            file_info = {
                "path": file_path,
                "size": os.path.getsize(file_path),
                "created": os.path.getctime(file_path),
                "extension": Path(file_path).suffix
            }
            
            return file_info
            
        except Exception as e:
            return {"error": str(e)} 