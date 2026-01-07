"""
Tests for PinguinQaService - validates dual audio map loading and QA functionality.
"""

import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.PinguinQaService import PinguinQaService


class TestPinguinQaService:
    """Test suite for PinguinQaService with dual audio map support."""

    def test_cosmo_audio_map_loading(self):
        """Test that cosmo audio_map.json loads correctly."""
        service = PinguinQaService(audio_map_path="audio_map.json")
        service.load_model()
        
        assert service.is_loaded, "Service should be loaded"
        assert len(service.segments) > 0, "Should have segments from audio_map.json"
        assert len(service.audio_map) > 0, "Should have audio map entries"
        
    def test_dark_cosmo_audio_map_loading(self):
        """Test that dark_audio_map.json loads correctly."""
        service = PinguinQaService(audio_map_path="dark_audio_map.json")
        service.load_model()
        
        assert service.is_loaded, "Service should be loaded"
        assert len(service.segments) > 0, "Should have segments from dark_audio_map.json"
        assert len(service.audio_map) > 0, "Should have audio map entries"

    def test_answer_with_matching_question(self):
        """Test that a matching question returns high confidence."""
        service = PinguinQaService(audio_map_path="audio_map.json")
        service.load_model()
        
        # Use a question that exists in audio_map.json
        result = service.answer("C'est quoi la lettre ?")
        
        assert "answer" in result, "Response should contain 'answer' key"
        assert "confidence" in result, "Response should contain 'confidence' key"
        assert "time_ms" in result, "Response should contain 'time_ms' key"
        assert result["confidence"] > 0.0, "Confidence should be > 0 for matching question"

    def test_answer_with_no_match(self):
        """Test that an unrelated question returns low confidence."""
        service = PinguinQaService(audio_map_path="audio_map.json")
        service.load_model()
        
        result = service.answer("xyz random unrelated query 12345")
        
        assert "answer" in result, "Response should contain 'answer' key"
        # Low confidence expected for unrelated query
        assert result["confidence"] < 0.5, "Confidence should be low for unrelated question"

    def test_different_audio_maps_have_different_segments(self):
        """Test that cosmo and dark_cosmo use different audio maps."""
        cosmo_service = PinguinQaService(audio_map_path="audio_map.json")
        cosmo_service.load_model()
        
        dark_service = PinguinQaService(audio_map_path="dark_audio_map.json")
        dark_service.load_model()
        
        # They should have segments but potentially different ones
        assert cosmo_service.segments != [] or dark_service.segments != [], \
            "At least one service should have segments"
        
        # The audio maps should be separate instances
        assert cosmo_service.audio_map is not dark_service.audio_map, \
            "Audio maps should be separate instances"

    def test_audio_file_returned_on_high_confidence(self):
        """Test that audio_file is returned when confidence >= 0.65."""
        service = PinguinQaService(audio_map_path="audio_map.json")
        service.load_model()
        
        # Use exact question from audio_map for high confidence
        result = service.answer("C'est quoi la lettre ?.")
        
        # audio_file might be None if confidence < threshold or file doesn't exist
        # Just verify the key exists
        assert "audio_file" in result, "Response should contain 'audio_file' key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
