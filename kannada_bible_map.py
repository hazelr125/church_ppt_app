# kannada_bible_map.py

# Mapping of English Bible book names to Kannada
ENGLISH_TO_KANNADA_BOOKS = {
    # Old Testament
    "Genesis": "ಆದಿಕಾಂಡ",
    "Exodus": "ಪ್ರಯಾಣಕಾಂಡ",
    "Leviticus": "ಲೇವಿಕಾಂಡ",
    "Numbers": "ಸಂಖ್ಯಾಕಾಂಡ",
    "Deuteronomy": "ದ್ವಿತೀಯೋಪದೇಶಕಾಂಡ",
    "Joshua": "ಯೆಹೋಶುವ",
    "Judges": "ನ್ಯಾಯಾಧಿಕಾರಿಗಳು",
    "Ruth": "ರೂತ್",
    "1 Samuel": "1 ಶಮುವೇಲ",
    "2 Samuel": "2 ಶಮುವೇಲ",
    "1 Kings": "1 ಅರಸರ",
    "2 Kings": "2 ಅರಸರ",
    "1 Chronicles": "1 ದಿನವೃತ್ತಾಂತ",
    "2 Chronicles": "2 ದಿನವೃತ್ತಾಂತ",
    "Ezra": "ಎಜ್ರಾ",
    "Nehemiah": "ನೆಹೆಮಿಯ",
    "Esther": "ಎಸ್ತೇರ್",
    "Job": "ಅಯೋಬ",
    "Psalms": "ಸ್ತೋತ್ರಗೀತೆಗಳು",
    "Psalm": "ಸ್ತೋತ್ರಗೀತೆ",  # singular form (for safety)
    "Proverbs": "ಜ್ಞಾನೋಕ್ತಿಗಳು",
    "Ecclesiastes": "ಸಭಾಪ್ರಸಂಗಿ",
    "Song of Solomon": "ಗೀತಾಗೀತ",
    "Isaiah": "ಯೆಶಾಯ",
    "Jeremiah": "ಯೆರೇಮಿಯ",
    "Lamentations": "ಪ್ರಲಾಪಗೀತೆಗಳು",
    "Ezekiel": "ಯೆಹೆಜ್ಕೇಲ",
    "Daniel": "ದಾನಿಯೇಲ",
    "Hosea": "ಹೋಶೇಯ",
    "Joel": "ಯೋವೇಲ",
    "Amos": "ಆಮೋಸ",
    "Obadiah": "ಓಬದಿಯ",
    "Jonah": "ಯೋನ",
    "Micah": "ಮೀಕ",
    "Nahum": "ನಹೂಮ್",
    "Habakkuk": "ಹಬಕ್ಕೂಕ",
    "Zephaniah": "ಸೆಫನ್ಯ",
    "Haggai": "ಹಗ್ಗಾಯ",
    "Zechariah": "ಜೆಕರ್ಯ",
    "Malachi": "ಮಲಾಕಿ",

    # New Testament
    "Matthew": "ಮತ್ತಾಯ",
    "Mark": "ಮಾರ್ಕ",
    "Luke": "ಲೂಕ",
    "John": "ಯೋಹಾನ",
    "Acts": "ಅಪೋಸ್ತಲರ ಕೃತ್ಯಗಳು",
    "Romans": "ರೋಮಾಪುರದವರಿಗೆ",
    "1 Corinthians": "1 ಕೊರಿಂಥದವರಿಗೆ",
    "2 Corinthians": "2 ಕೊರಿಂಥದವರಿಗೆ",
    "Galatians": "ಗಲಾತ್ಯದವರಿಗೆ",
    "Ephesians": "ಎಫೆಸದವರಿಗೆ",
    "Philippians": "ಫಿಲಿಪ್ಪಿಯವರಿಗೆ",
    "Colossians": "ಕೊಲೊಸ್ಸೆಯವರಿಗೆ",
    "1 Thessalonians": "1 ಥೆಸ್ಸಲೋನಿಕದವರಿಗೆ",
    "2 Thessalonians": "2 ಥೆಸ್ಸಲೋನಿಕದವರಿಗೆ",
    "1 Timothy": "1 ತಿಮೋಥೆಗೆ",
    "2 Timothy": "2 ತಿಮೋಥೆಗೆ",
    "Titus": "ತೀತನಿಗೆ",
    "Philemon": "ಫಿಲೆಮೋನಿಗೆ",
    "Hebrews": "ಹೆಬ್ರೂಗಳವರಿಗೆ",
    "James": "ಯಾಕೋಬ",
    "1 Peter": "1 ಪೇತ್ರ",
    "2 Peter": "2 ಪೇತ್ರ",
    "1 John": "1 ಯೋಹಾನ",
    "2 John": "2 ಯೋಹಾನ",
    "3 John": "3 ಯೋಹಾನ",
    "Jude": "ಯೂದ",
    "Revelation": "ಪ್ರಕಟನೆ",
}

# Section titles mapping (English → Heading in output)
ENGLISH_TO_KANNADA_PREFIX = {
    "Psalm": "Responsive Psalm",
    "Old Testament": "Old Testament",
    "New Testament": "New Testament",
    "Gospel": "Gospel Reading"
}

# Digit mapping for Kannada numerals
DIGIT_MAP = {
    "0": "೦", "1": "೧", "2": "೨", "3": "೩", "4": "೪",
    "5": "೫", "6": "೬", "7": "೭", "8": "೮", "9": "೯"
}

def to_kannada_numerals(num_str: str) -> str:
    """Convert digits in a string to Kannada numerals."""
    return "".join(DIGIT_MAP.get(ch, ch) for ch in num_str)
