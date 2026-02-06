"""
MindQuest Interactive CLI
=========================

This is the main entry point for the MindQuest interactive studio.
It guides the user through creating educational content like scripts,
podcasts, and mini-books.
"""

import os
import sys
import textwrap
from mindquest.studio import create_script, generate_podcast, create_minibook


def print_header():
    """Print the application welcome header."""
    print("\n" + "=" * 60)
    print("🌟  Welcome to MindQuest Studio  🌟")
    print("=" * 60)
    print("Create educational adventures for kids using AI!")
    print("-" * 60)


def check_api_key():
    """Check for the OPENAI_API_KEY environment variable."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it and restart the application.")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    return api_key


def get_user_input(prompt: str, required=True, default=None):
    """
    Get input from the user with optional default and validation.

    Args:
        prompt: The display prompt.
        required: Whether input is required (default: True).
        default: Default value if input is empty.

    Returns:
        The user's input string.
    """
    while True:
        user_input = input(
            f"{prompt}" + (f" [{default}]" if default else "") + ": "
        ).strip()
        if not user_input and default is not None:
            return default
        if not user_input and required:
            print("❌ Input is required. Please try again.")
            continue
        return user_input


def handle_create_script(api_key: str):
    """Handle the podcast script creation workflow."""
    print("\n--- Create Podcast Script ---")
    topic = get_user_input("Enter the educational topic")
    words = get_user_input("Target word count", default="500")

    try:
        print("\n⏳ Generating script... this may take a moment.")
        script = create_script(api_key=api_key, topic=topic, number_of_words=int(words))
        print("\n✅ Script Generated Successfully!")
        print("-" * 40)
        print(textwrap.shorten(script, width=300, placeholder="..."))
        print("-" * 40)

        save = get_user_input("Save to file? (y/N)", required=False, default="n")
        if save.lower() == "y":
            filename = get_user_input(
                "Filename", default=f"{topic.replace(' ', '_')}.txt"
            )
            with open(filename, "w", encoding="utf-8") as file_handle:
                file_handle.write(script)
            print(f"Saved to {filename}")

    except Exception as error:  # pylint: disable=broad-exception-caught
        print(f"\n❌ Error generating script: {error}")


def handle_generate_podcast(api_key: str):
    """Handle the full podcast generation workflow."""
    print("\n--- Generate Full Podcast (Script + Audio) ---")
    topic = get_user_input("Enter the educational topic")

    try:
        print("\n⏳ Starting podcast production...")
        output_file = get_user_input(
            "Output filename", default=f"{topic.replace(' ', '_')}.mp3"
        )

        path = generate_podcast(topic=topic, api_key=api_key, output_file=output_file)
        print(f"\n✅ Podcast created successfully at: {path}")

    except Exception as error:  # pylint: disable=broad-exception-caught
        print(f"\n❌ Error generating podcast: {error}")


def handle_create_minibook(api_key: str):
    """Handle the mini-book creation workflow."""
    print("\n--- Create Mini-Book (EPUB/PDF) ---")
    topic = get_user_input("Enter the educational topic")
    lang = get_user_input("Language code", default="en")
    chapters = get_user_input("Number of chapters", default="5")
    fmt = get_user_input("Format (epub/pdf)", default="epub")

    try:
        print(f"\n⏳ Creating mini-book on '{topic}'...")
        path = create_minibook(
            api_key=api_key,
            topic=topic,
            language=lang,
            number_of_chapters=int(chapters),
            format=fmt,
        )
        print(f"\n✅ Mini-book created successfully at: {path}")

    except Exception as error:  # pylint: disable=broad-exception-caught
        print(f"\n❌ Error creating mini-book: {error}")


def main():
    """Main application loop."""
    print_header()
    api_key = check_api_key()

    while True:
        print("\nAvailable Capabilities:")
        print("1. 📝 Create Podcast Script")
        print("2. 🎙️  Generate Full Podcast")
        print("3. 📖 Create Mini-Book")
        print("4. 🚪 Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            handle_create_script(api_key)
        elif choice == "2":
            handle_generate_podcast(api_key)
        elif choice == "3":
            handle_create_minibook(api_key)
        elif choice == "4":
            print("\nGoodbye! Happy learning! 👋")
            break
        else:
            print("\n❌ Invalid option. Please choose 1-4.")


if __name__ == "__main__":
    main()
