"""
Test suite for mindquest.studio module.
"""

import pytest
from pathlib import Path
from mindquest.studio import (
    Chapter,
    MiniBook,
    create_minibook,
    generate_podcast_script,
    synthesize_podcast,
)


class TestCreateMinibook:
    """Test mini-book creation functionality."""

    def test_create_default_minibook(self):
        """Should create a mini-book with default parameters."""
        book = create_minibook("Robotics")
        
        assert book["topic"] == "Robotics"
        assert book["language"] == "en"
        assert book["age_group"] == "8-12"
        assert book["title"] == "Robotics for Kids (8-12)"
        assert len(book["chapters"]) == 7
        
    def test_create_minibook_custom_params(self):
        """Should create a mini-book with custom parameters."""
        book = create_minibook(
            "Space",
            language="he",
            age_group="10-14",
            title="Space Adventures",
            chapters_count=5,
            words_per_chapter=1500,
        )
        
        assert book["topic"] == "Space"
        assert book["language"] == "he"
        assert book["age_group"] == "10-14"
        assert book["title"] == "Space Adventures"
        assert len(book["chapters"]) == 5

    def test_chapter_structure(self):
        """Each chapter should have required fields."""
        book = create_minibook("Python")
        
        for chapter in book["chapters"]:
            assert "title" in chapter
            assert "content" in chapter
            assert "questions" in chapter
            assert "answers" in chapter
            assert len(chapter["questions"]) == 3
            assert len(chapter["answers"]) == 3

    def test_chapters_numbered_correctly(self):
        """Chapters should be numbered sequentially."""
        book = create_minibook("Math", chapters_count=3)
        
        for i, chapter in enumerate(book["chapters"], 1):
            assert f"Chapter {i}" in chapter["title"]


class TestGeneratePodcastScript:
    """Test podcast script generation."""

    def test_generate_basic_script(self):
        """Should generate a basic podcast script."""
        chapter: Chapter = {
            "title": "Introduction to Robots",
            "content": "Robots are machines that can perform tasks automatically.",
            "questions": ["What is a robot?"],
            "answers": ["A machine that performs tasks automatically."],
        }
        
        script = generate_podcast_script(chapter)
        
        assert "Introduction to Robots" in script
        assert "Robots are machines" in script
        assert "Question 1: What is a robot?" in script

    def test_generate_script_without_questions(self):
        """Should generate script without questions when disabled."""
        chapter: Chapter = {
            "title": "Test Chapter",
            "content": "Test content.",
            "questions": ["Q1?", "Q2?"],
            "answers": ["A1", "A2"],
        }
        
        script = generate_podcast_script(chapter, include_questions=False)
        
        assert "Test content" in script
        assert "Q1?" not in script
        assert "Question 1" not in script

    def test_generate_script_with_language(self):
        """Should include language hint when specified."""
        chapter: Chapter = {
            "title": "Test",
            "content": "Content",
            "questions": [],
            "answers": [],
        }
        
        script = generate_podcast_script(chapter, language="he")
        
        assert "[he]" in script

    def test_generate_script_custom_narrator_style(self):
        """Should include narrator style in script."""
        chapter: Chapter = {
            "title": "Test",
            "content": "Content",
            "questions": [],
            "answers": [],
        }
        
        script = generate_podcast_script(chapter, narrator_style="excited")
        
        assert "excited" in script


class TestSynthesizePodcast:
    """Test audio synthesis (stub implementation)."""

    def test_synthesize_creates_files(self, tmp_path):
        """Should create audio file and script sidecar."""
        script = "This is a test podcast script."
        audio_path = tmp_path / "test_podcast.wav"
        
        result = synthesize_podcast(script, out_path=audio_path)
        
        assert result == audio_path
        assert audio_path.exists()
        assert audio_path.with_suffix(".txt").exists()

    def test_synthesize_script_sidecar_content(self, tmp_path):
        """Script sidecar should contain voice and script text."""
        script = "Hello world!"
        audio_path = tmp_path / "output.wav"
        
        synthesize_podcast(script, voice="custom_voice", out_path=audio_path)
        
        sidecar = audio_path.with_suffix(".txt")
        content = sidecar.read_text(encoding="utf-8")
        
        assert "VOICE=custom_voice" in content
        assert "Hello world!" in content

    def test_synthesize_creates_parent_dirs(self, tmp_path):
        """Should create parent directories if they don't exist."""
        audio_path = tmp_path / "deep" / "nested" / "podcast.wav"
        script = "Test"
        
        result = synthesize_podcast(script, out_path=audio_path)
        
        assert result.exists()
        assert result.parent.exists()


class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_full_pipeline(self, tmp_path):
        """Should create book, generate script, and synthesize audio."""
        # Create mini-book
        book = create_minibook("Animals", chapters_count=2)
        assert len(book["chapters"]) == 2
        
        # Generate script for first chapter
        script = generate_podcast_script(book["chapters"][0])
        assert len(script) > 0
        
        # Synthesize audio
        audio_path = tmp_path / "animals_ch1.wav"
        result = synthesize_podcast(script, out_path=audio_path)
        
        assert result.exists()
        assert result.with_suffix(".txt").exists()

    def test_multilingual_pipeline(self, tmp_path):
        """Should handle non-English language."""
        book = create_minibook("Science", language="he", chapters_count=1)
        assert book["language"] == "he"
        
        script = generate_podcast_script(
            book["chapters"][0],
            language="he",
            narrator_style="friendly"
        )
        assert "[he]" in script
        
        audio_path = tmp_path / "science_he.wav"
        synthesize_podcast(script, out_path=audio_path)
        assert audio_path.exists()
