# hymns_db.py
import csv
import re
import os

class HymnDatabase:
    def __init__(self, kannada_csv_path, tulu_csv_path, english_csv_path):
        """Initialize hymn database with both Kannada and Tulu CSV files"""
        self.kannada_db = self.load_hymn_db(kannada_csv_path, "Kannada")
        self.tulu_db = self.load_hymn_db(tulu_csv_path, "Tulu")
        self.english_db = self.load_hymn_db(english_csv_path, "English") if english_csv_path else {}
    
    def load_hymn_db(self, csv_path, language):
        """Load hymn database from CSV file"""
        db = {}
        if not os.path.exists(csv_path):
            print(f"Warning: {language} CSV file not found at {csv_path}")
            return db
        
        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, 1):
                    hymn_no_raw = str(row.get('Hymn_No', '')).strip()
                    if not hymn_no_raw:
                        continue
                    
                    try:
                        # Normalize hymn number (remove leading zeros, etc.)
                        hymn_no = str(int(hymn_no_raw))
                    except ValueError:
                        # If it's not a pure number, keep as string but strip spaces
                        hymn_no = hymn_no_raw
                    
                    # For Kannada CSV: Kannada and English columns
                    # For Tulu CSV: Kannada (actually Tulu text) and English columns
                    if language.lower() == "tulu":
                        local_text = (row.get('Tulu') or '').strip()  # actually Tulu column in that CSV
                    else:
                        local_text = (row.get('Kannada') or '').strip()  # Kannada text

                    english_text = (row.get('English') or '').strip()

                    db[hymn_no] = {
                        'local': local_text,
                        'english': english_text,
                        'language': language.lower()
                    }

                    
            print(f"Loaded {len(db)} {language} hymns from {csv_path}")
            
        except Exception as e:
            print(f"Error loading {language} CSV file {csv_path}: {e}")
            return {}
        
        return db
    
    def get_hymn(self, hymn_number, language="kannada"):
        """Get hymn from appropriate database based on language"""
        try:
            hymn_no = str(int(hymn_number.strip()))
        except ValueError:
            hymn_no = hymn_number.strip()
        
        if language.lower() == "tulu":
            return self.tulu_db.get(hymn_no)
        elif language.lower() == "english":
            return self.english_db.get(hymn_no)
        return self.kannada_db.get(hymn_no)
    
    def get_available_hymns(self, language="kannada"):
        """Get list of available hymn numbers for a language"""
        if language.lower() == "tulu":
            return sorted([int(k) for k in self.tulu_db.keys() if k.isdigit()])
        else:
            return sorted([int(k) for k in self.kannada_db.keys() if k.isdigit()])

def split_into_verses(text, return_lines=False):
    """Split hymn text into numbered verses"""
    if not text:
        return {}
        
    text = text.replace('\r\n', '\n').replace('\r', '\n').strip()
    text = text.replace('\\n', '\n')
    
    # Pattern to match numbered verses (1. or 1) followed by content)
    pat = re.compile(r'(?m)^\s*(\d+)[\.\)]\s*(.*?)(?=^\s*\d+[\.\)]\s*|\Z)', re.DOTALL)
    verses = {}
    
    for num, body in pat.findall(text):
        body = body.strip()
        if not body:
            continue
            
        try:
            verse_num = int(num)
            if return_lines:
                lines = [ln.strip() for ln in re.split(r'\n+', body) if ln.strip()]
                verses[verse_num] = [f"{verse_num}. {lines[0]}"] + lines[1:]
            else:
                verses[verse_num] = f"{verse_num}. {body}"
        except ValueError:
            continue
    
    # Fallback if no numbered verses found
    if not verses:
        if return_lines:
            lines = [ln.strip() for ln in re.split(r'\n+', text) if ln.strip()]
            return {i+1: ln for i, ln in enumerate(lines)}
        else:
            blocks = [blk.strip() for blk in re.split(r'\n{2,}', text) if blk.strip()]
            return {i+1: blk for i, blk in enumerate(blocks)}
    
    return verses

def parse_verse_selection(verse_text):
    """
    Parse verse selection from user input
    Examples:
      '1,3,5,7' -> [1,3,5,7]
      '1,2' -> [1,2]
      '1-3' -> [1,2,3]
      '1,2,4-6' -> [1,2,4,5,6]
      '' or None -> None (all verses)
    """
    if not verse_text or not verse_text.strip():
        return None
    
    verse_text = verse_text.strip()
    verses = []
    
    # Split by commas first
    parts = [part.strip() for part in verse_text.split(',')]
    
    for part in parts:
        if '-' in part:
            # Handle ranges like "4-6"
            try:
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                verses.extend(range(start, end + 1))
            except ValueError:
                # If range parsing fails, try to parse as single number
                try:
                    verses.append(int(part.strip()))
                except ValueError:
                    continue
        else:
            # Handle single numbers
            try:
                verses.append(int(part))
            except ValueError:
                continue
    
    return sorted(list(set(verses))) if verses else None

def get_hymn_verses(hymn_number, verse_selection, language, hymn_db):
    """
    Get hymn verses based on user input
    
    Args:
        hymn_number (str): The hymn number (e.g., "140", "113")
        verse_selection (str): Verse selection (e.g., "1,3,5" or empty for all)
        language (str): "kannada" or "tulu"
        hymn_db (HymnDatabase): The hymn database instance
    
    Returns:
        tuple: (local_verses, english_verses) dictionaries
    """
    if not hymn_number or not hymn_number.strip():
        return {}, {}
    
    # Normalize hymn number
    try:
        hymn_no = str(int(hymn_number.strip()))
    except ValueError:
        hymn_no = hymn_number.strip()
    
    print(f"Looking for hymn number: {hymn_no} in {language}")
    
    # Get hymn from appropriate database
    hymn = hymn_db.get_hymn(hymn_no, language)
    
    if not hymn:
        print(f"Hymn {hymn_no} not found in {language} database")
        available_hymns = hymn_db.get_available_hymns(language)[:10]
        print(f"Available {language} hymn numbers (first 10): {available_hymns}")
        return {}, {}
    
    print(f"Found hymn {hymn_no} in {language} database")
    
    # Split into verses
    verses_local = split_into_verses(hymn.get('local', ''))
    verses_english = split_into_verses(hymn.get('english', ''))
    
    print(f"Hymn {hymn_no} has {len(verses_local)} {language} verses, {len(verses_english)} English verses")
    
    # Parse verse selection
    verses_req = parse_verse_selection(verse_selection)
    
    # Filter to requested verses if specified
    if verses_req:
        verses_local = {i: verses_local[i] for i in verses_req if i in verses_local}
        verses_english = {i: verses_english[i] for i in verses_req if i in verses_english}
        print(f"Filtered to requested verses: {verses_req}")
        print(f"Available {language} verses: {list(verses_local.keys())}")
        print(f"Available English verses: {list(verses_english.keys())}")
    else:
        print(f"Using all verses - {language}: {list(verses_local.keys())}, English: {list(verses_english.keys())}")
    
    return verses_local, verses_english

def process_user_hymns(form_data, hymn_db):
    placeholders = {}
    
    # Find all hymn numbers in form data (dynamically detect how many hymns were submitted)
    hymn_indices = set()
    for key in form_data.keys():
        if key.startswith('hymn') and key.endswith('_number'):
            # Extract the hymn index from keys like "hymn1_number", "hymn6_number", etc.
            try:
                index = int(key.replace('hymn', '').replace('_number', ''))
                hymn_indices.add(index)
            except ValueError:
                continue
    
    # Process all found hymns
    for i in sorted(hymn_indices):
        hymn_number = form_data.get(f'hymn{i}_number', '').strip()
        verse_selection = form_data.get(f'hymn{i}_verses', '').strip()
        language = form_data.get(f'hymn{i}_language', 'kannada').strip().lower()
        
        if not hymn_number:
            continue
        
        print(f"\nProcessing Hymn {i}: Number={hymn_number}, Verses={verse_selection or 'all'}, Language={language}")
        
        verses_local, verses_english = get_hymn_verses(hymn_number, verse_selection, language, hymn_db)
        
        # Create placeholders for this hymn
        
        for verse_num in sorted(set(list(verses_local.keys()) + list(verses_english.keys()))):
            if verse_num in verses_local:
                placeholders[f'HYMN{i}_KN_V{verse_num}'] = verses_local[verse_num]
            if verse_num in verses_english:
                placeholders[f'HYMN{i}_EN_V{verse_num}'] = verses_english[verse_num]
        
        lang_code = "E" if language == "english" else "K" if language == "kannada" else "T"
        verses_str = f"(Vs. {verse_selection})" if verse_selection else "(All Verses)"
        description = f"{lang_code} - {hymn_number} {verses_str}"
        placeholders[f'HYMN{i}_DES'] = description

        added_placeholders = len([k for k in placeholders.keys() if f'HYMN{i}_' in k])
        print(f"Added {added_placeholders} placeholders for Hymn {i} ({language})")
    
    return placeholders
