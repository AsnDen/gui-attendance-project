VALID_PERSON_DATA = [
    # --- Classic Names & Base Cases ---
    ("Egor Kuz", "Anonymous user for system testing purposes"),
    ("Alice Liubimova", "Backend developer from Mosvow, 19 y.o."),
    ("Mary-Jane Watson", "Actress and freelance journalist"),
    ("Alexander", ""),  # Case with None description
    # --- Extreme Lengths (Short & Long) ---
    ("J", "Single letter name, but description is standard length"),
    ("X", "X"),  # Minimum possible length for both fields
    (
        "Christopher-Maximilian-Hubertus_Vanderbilt",
        """A user with an exceptionally long first and last name to test
        how the UI or database handles text overflow, wrapping,
        and truncation algorithms without breaking layout.""",
    ),
    # --- Symbols, Numbers & Punctuation ---
    ("User_404", "Status: Active. Created via API-v2. [Internal]"),
    ("O'Connor", "Irish origin name containing an apostrophe"),
    ("id_#12345", 'Description with symbols: ~!@#$%^&*()_+{}|:"<>?'),
    ("3.14159", "Pi lover and mathematics department contact"),
    # --- Emojis & Unicode (Encoding check) ---
    ("Alex 👨‍💻", "Information security specialist 🔐"),
    ("Elon 🚀", "Going to Mars mood 🌌✨"),
    ("木村 拓哉", "Takuya Kimura - Japanese name format support check"),
    # --- Case Sensitivity & Strange Formatting ---
    ("JOHN STERN", "ALL CAPS TEXT IN BOTH FIELDS FOR TESTING"),
    ("lowercase_user", "all text here is strictly lowercase"),
    ("iNVERTED cASE", "sOME STRANGE TYPING STYLE"),
    # --- System / Technical Placeholders ---
    ("N/A", "Not Available status profile"),
    ("Undefined", ""),
    ("Unknown Person", "No data provided during the hardware scan event"),
    ("---", "---"),
    # --- Bilingual & Mixed Strings ---
    ("Peter (Петр) Perzovskiy", "Senior QA / Тестировщик автоматизатор"),
    ("Clean Code", "Refactoring enthusiast (Python, PySide6, SQL)"),
]

INVALID_PERSON_DATA = [("", ""), ("", "Test case"), ("", "Empty wizard")]
