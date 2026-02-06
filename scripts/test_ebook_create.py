import os
import sys
from mindquest.studio import create_minibook

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)
    
    try:
        topic = input("Enter topic: ").strip()
        language = input("Enter language (default 'en'): ").strip() or "en"
        chapters_input = input("Enter number of chapters (default 7): ").strip()
        number_of_chapters = int(chapters_input) if chapters_input else 7
        
        if not topic:
            print("Error: Topic is required.")
            sys.exit(1)
            
    except EOFError:
        print("\nInput cancelled.")
        sys.exit(0)
    except ValueError:
        print("Error: Number of chapters must be an integer.")
        sys.exit(1)

    print(f"\n📖 Starting mini-book generation for: {topic} ({language}, {number_of_chapters} chapters)")
    
    try:
        output_path = create_minibook(
            api_key=api_key, 
            topic=topic, 
            language=language, 
            number_of_chapters=number_of_chapters
        )
        print(f"\n✅ Successfully created mini-book at: {output_path}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()