# parse_pdf.py
import pdfplumber
import re
from kannada_bible_map import ENGLISH_TO_KANNADA_BOOKS, ENGLISH_TO_KANNADA_PREFIX, to_kannada_numerals
from bible_fetch import fetch_bible_passage
from bible_normalize import normalize_book


def to_kannada_ref(ref: str) -> str:
    """
    Convert 'Nehemiah 8:1-8' -> 'ನೆಹೆಮಿಯ ೮:೧-೮'
    using kannada_bible_map and to_kannada_numerals.
    """
    if not ref:
        return ""

    m = re.match(r"([1-3]?\s?[A-Za-z]+\.?)\s+(\d+:\d+(?:-\d+)?)", ref)
    if not m:
        return ref

    book, verses = m.groups()
    book_clean = normalize_book(book)
    kn_book = ENGLISH_TO_KANNADA_BOOKS.get(book_clean, book_clean)
    kn_prefix = ENGLISH_TO_KANNADA_PREFIX.get(book_clean, "")
    return f"{kn_prefix}{kn_book} {to_kannada_numerals(verses)}"

def parse_pdf_to_structured(pdf_path: str) -> dict:
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Normalize lines
    lines = [re.sub(r'^[\s\-\u2022\*]+', '', l).strip() for l in text.splitlines() if l.strip()]

    data = {
        #"hymns": [],
        "psalm_en": "",
        "psalm_kn": "",
        "old_testament_en": "",
        "old_testament_kn": "",
        "new_testament_en": "",
        "new_testament_kn": "",
        "gospel_en": "",
        "gospel_kn": "",
        "psalm": "",
        "old_testament": "",
        "new_testament": "",
        "gospel": "",
        "announcements_block": "",
        "birthday_names": [],
        "anniversary_names": [],
    }

    # patterns
    #hymn_num_pattern = re.compile(r'(?:Hymn|Kan\. Hymn|Kannada Hymn|K-|T-)\s*[:]?\s*([A-Za-z0-9\-\s]+(?:\d+)?)', re.I)
    #simple_num_pattern = re.compile(r'\bK-?\s*(\d+)\b|\bT-?\s*(\d+)\b', re.I)
    bible_verse_pattern = re.compile(r'([1-3]?\s?[A-Za-z]+\.?\s*\d{1,3}:\d+(?:-\d+)?)', re.I)
    psalm_pattern = re.compile(r'Psalm\s*([0-9]{1,3}:\d+(?:-\d+)?)', re.I)

    # scan lines for hymns and readings
    for i, ln in enumerate(lines):

        #m_k = re.search(r'(?<!M\.)\bK[-\s]?(\d{1,4})\b', ln, re.I)
        #if m_k:
        #    data['hymns'].append(('K', m_k.group(1), ln.strip()))  # store line
        #    continue

        # Hymn Tulu (T-294 etc.)
        #m_t = re.search(r'(?<!M\.)\bT[-\s]?(\d{1,4})\b', ln, re.I)
        #if m_t:
         #   data['hymns'].append(('T', m_t.group(1), ln.strip()))
         #   continue

        # Psalm
        m_ps = psalm_pattern.search(ln)
        if m_ps and not data['psalm']:
            ref = "Psalm " + m_ps.group(1)
            data['psalm'] = ref
            passages = fetch_bible_passage(ref, "en")
            data['psalm_en'] = "\n\n".join(passages)
            data['psalm_kn'] = to_kannada_ref(ref)
            continue

        # Old Testament
        if re.search(r'Old Testament|O\.T\.|Old Test', ln, re.I):
            mv = bible_verse_pattern.search(ln) or (bible_verse_pattern.search(lines[i+1]) if i+1 < len(lines) else None)
            if mv:
                ref = mv.group(1)
                data['old_testament'] = ref
                passages = fetch_bible_passage(ref, "en")
                data['old_testament_en'] = "\n\n".join(passages)
                data['old_testament_kn'] = to_kannada_ref(ref)
            continue

        # New Testament
        if re.search(r'New Testament|N\.T\.|New Testa', ln, re.I):
            mv = bible_verse_pattern.search(ln) or (bible_verse_pattern.search(lines[i+1]) if i+1 < len(lines) else None)
            if mv:
                ref = mv.group(1)
                data['new_testament'] = ref
                passages = fetch_bible_passage(ref, "en")
                data['new_testament_en'] = "\n\n".join(passages)
                data['new_testament_kn'] = to_kannada_ref(ref)
            continue

        # Gospel
        if re.search(r'Gospel Reading|Gospel', ln, re.I):
            mv = bible_verse_pattern.search(ln) or (bible_verse_pattern.search(lines[i+1]) if i+1 < len(lines) else None)
            if mv:
                ref = mv.group(1)
                data['gospel'] = ref
                passages = fetch_bible_passage(ref, "en")
                data['gospel_en'] = "\n\n".join(passages)
                data['gospel_kn'] = to_kannada_ref(ref)
            continue

        # Announcements
        if re.match(r'ANNOUNCEMENTS', ln, re.I):
            # gather subsequent lines until an obvious heading end
            j = i+1
            block = []
            while j < len(lines):
                nxt = lines[j]
                if re.match(r'^(Praise|Off|Hymn|Lord\'s Prayer|THANK|Birthday|Happy Birthday)', nxt, re.I):
                    break
                block.append(nxt)
                j += 1
            data['announcements_block'] = "\n".join(block).strip()
            continue

        # Birthday / Anniversary entries (simple heuristic)
        if re.search(r'Happy Birthday|Birthday', ln, re.I):
            # gather following lines which are names until empty or next section
            j = i+1
            names = []
            while j < len(lines) and lines[j].strip():
                names.append(lines[j].strip())
                j += 1
            data['birthday_names'].extend(names[:20])
            continue

        if re.search(r'Happy Anniversary|Anniversary', ln, re.I):
            j = i+1
            names = []
            while j < len(lines) and lines[j].strip():
                names.append(lines[j].strip())
                j += 1
            data['anniversary_names'].extend(names[:20])
            continue

    return data

# wrapper used by app
def parse_pdf_to_structured_wrapper(path):
    return parse_pdf_to_structured(path)
