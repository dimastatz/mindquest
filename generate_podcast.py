#!/usr/bin/env python3
"""
Simple script to generate a podcast and save audio to a file.
Usage: python3 generate_podcast.py [topic] [api_key]
"""

import sys
import os
from pathlib import Path
from mindquest import create_script, voice_over

def main():
    # Get API key from argument or environment
    if len(sys.argv) > 2:
        api_key = sys.argv[2]
    else:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: Gemini API key not provided")
        print("\nUsage:")
        print("  python3 generate_podcast.py 'Your Topic' 'your-api-key'")
        print("  OR set GEMINI_API_KEY environment variable")
        print("\nGet API key from: https://ai.google.dev/")
        sys.exit(1)
    
    # Get topic from argument or use default
    topic = sys.argv[1] if len(sys.argv) > 1 else "The Moon"
    
    print(f"🎙️ Generating podcast about: {topic}")
    print("⏳ Creating script...")
    
    try:
        # Create script
        script = create_script(topic, api_key)
        print(f"✅ Script created ({len(script)} characters)")
        print("\n📝 Script preview:")
        print("-" * 60)
        print(script[:500] + "..." if len(script) > 500 else script)
        print("-" * 60)
        
        # Generate voice-over
        print("\n🔊 Generating audio...")
        audio_bytes = voice_over(api_key, script, "en")
        
        # Save to file
        output_file = Path("podcast_audio.mp3")
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        file_size = output_file.stat().st_size
        print(f"✅ Audio saved: {output_file}")
        print(f"📊 File size: {file_size:,} bytes")
        print(f"\n🎵 Ready to play! Use:")
        print(f"   afplay podcast_audio.mp3")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
