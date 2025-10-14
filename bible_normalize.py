# bible_normalize.py
import re

# Master normalization map (abbreviations → standard English book name)
BOOK_NORMALIZATION = {
    # Pentateuch
    "gen": "Genesis", "genesis": "Genesis",
    "ex": "Exodus", "exo": "Exodus", "exodus": "Exodus",
    "lev": "Leviticus", "leviticus": "Leviticus",
    "num": "Numbers", "numbers": "Numbers",
    "deut": "Deuteronomy", "deuteronomy": "Deuteronomy", "dt": "Deuteronomy",

    # Historical
    "josh": "Joshua", "jos": "Joshua", "joshua": "Joshua",
    "judg": "Judges", "judges": "Judges",
    "rut": "Ruth", "ruth": "Ruth",
    "1sam": "1 Samuel", "1 samuel": "1 Samuel", "i samuel": "1 Samuel",
    "2sam": "2 Samuel", "2 samuel": "2 Samuel", "ii samuel": "2 Samuel",
    "1kgs": "1 Kings", "1 kings": "1 Kings", "i kings": "1 Kings",
    "2kgs": "2 Kings", "2 kings": "2 Kings", "ii kings": "2 Kings",
    "1chr": "1 Chronicles", "1 chronicles": "1 Chronicles", "i chronicles": "1 Chronicles",
    "2chr": "2 Chronicles", "2 chronicles": "2 Chronicles", "ii chronicles": "2 Chronicles",
    "ezra": "Ezra",
    "neh": "Nehemiah", "nehemiah": "Nehemiah",
    "est": "Esther", "esth": "Esther", "esther": "Esther",

    # Poetry / Wisdom
    "job": "Job",
    "ps": "Psalm", "psa": "Psalm", "psalm": "Psalm", "psalms": "Psalm",
    "prov": "Proverbs", "pro": "Proverbs", "proverbs": "Proverbs",
    "ecc": "Ecclesiastes", "ecclesiastes": "Ecclesiastes", "qohelet": "Ecclesiastes",
    "song": "Song of Solomon", "song of songs": "Song of Solomon", "sos": "Song of Solomon",

    # Major Prophets
    "isa": "Isaiah", "isaiah": "Isaiah",
    "jer": "Jeremiah", "jeremiah": "Jeremiah", "jeri": "Jeremiah",
    "lam": "Lamentations", "lamentations": "Lamentations",
    "eze": "Ezekiel", "ezekiel": "Ezekiel",
    "dan": "Daniel", "daniel": "Daniel",

    # Minor Prophets
    "hos": "Hosea", "hosea": "Hosea",
    "joel": "Joel",
    "amos": "Amos",
    "obad": "Obadiah", "obadiah": "Obadiah",
    "jon": "Jonah", "jonah": "Jonah",
    "mic": "Micah", "micah": "Micah",
    "nah": "Nahum", "nahum": "Nahum",
    "hab": "Habakkuk", "habakkuk": "Habakkuk",
    "zep": "Zephaniah", "zephaniah": "Zephaniah",
    "hag": "Haggai", "haggai": "Haggai",
    "zec": "Zechariah", "zechariah": "Zechariah",
    "mal": "Malachi", "malachi": "Malachi",

    # Gospels
    "mt": "Matthew", "matt": "Matthew", "matthew": "Matthew",
    "mk": "Mark", "mrk": "Mark", "mark": "Mark",
    "lk": "Luke", "luk": "Luke", "luke": "Luke",
    "jn": "John", "jhn": "John", "john": "John",

    # Acts & Paul
    "acts": "Acts",
    "rom": "Romans", "romans": "Romans", "romns": "Romans",
    "1cor": "1 Corinthians", "1 corinthians": "1 Corinthians", "i corinthians": "1 Corinthians",
    "2cor": "2 Corinthians", "2 corinthians": "2 Corinthians", "ii corinthians": "2 Corinthians",
    "gal": "Galatians", "galatians": "Galatians",
    "eph": "Ephesians", "ephesians": "Ephesians",
    "phil": "Philippians", "philip": "Philippians", "philippians": "Philippians",
    "col": "Colossians", "colossians": "Colossians",
    "1thess": "1 Thessalonians", "1 thes": "1 Thessalonians", "1 thessalonians": "1 Thessalonians",
    "2thess": "2 Thessalonians", "2 thessalonians": "2 Thessalonians",
    "1tim": "1 Timothy", "1 timothy": "1 Timothy",
    "2tim": "2 Timothy", "2 timothy": "2 Timothy",
    "titus": "Titus",
    "philem": "Philemon", "philemon": "Philemon",
    "heb": "Hebrews", "hebrews": "Hebrews",

    # General Epistles
    "jam": "James", "james": "James",
    "1pet": "1 Peter", "1 peter": "1 Peter",
    "2pet": "2 Peter", "2 peter": "2 Peter",
    "1jn": "1 John", "1 john": "1 John",
    "2jn": "2 John", "2 john": "2 John",
    "3jn": "3 John", "3 john": "3 John",
    "jude": "Jude",

    # Revelation
    "rev": "Revelation", "revelation": "Revelation", "apocalypse": "Revelation",
}

def normalize_book(book: str) -> str:
    """Normalize any Bible book name/abbr → Standard English form."""
    if not book:
        return ""
    key = book.lower().replace(".", "").strip()
    return BOOK_NORMALIZATION.get(key, book.strip().capitalize())
