# parse_pdf.py
import pdfplumber
import re

def extract_verses_from_line(line: str):
    verse_match = re.search(r"\(Vs\.\s*([\d,\-&]+)\)", line)
    if not verse_match:
        return []
    verse_part = verse_match.group(1).replace("&", ",")
    verse_nums = []
    for part in verse_part.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            verse_nums.extend(range(int(start), int(end) + 1))
        elif part.isdigit():
            verse_nums.append(int(part))
    return sorted(set(verse_nums))

def parse_pdf_to_structured(pdf_path: str) -> dict:
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Normalize lines
    lines = [re.sub(r'^[\s\-\u2022\*]+', '', l).strip() for l in text.splitlines() if l.strip()]

    data = {
        "hymns": [],  
        "psalm": "",
        "old_testament": "",
        "new_testament": "",
        "gospel": "",
        "announcements_block": "",
        "birthday_names": [],
        "anniversary_names": [],
        "sermon": ""
    }

    bible_verse_pattern = re.compile(r'([1-3]?\s?[A-Za-z]+\.?\s*\d{1,3}:\d+(?:-\d+)?)', re.I)
    psalm_pattern = re.compile(r'Psalm\s*([0-9]{1,3}:\d+(?:-\d+)?)', re.I)

    # scan lines
    for i, ln in enumerate(lines):
        m_k = re.search(r'\bK[-\s]?(\d{1,4})\b', ln, re.I)
        if m_k:
            verses = extract_verses_from_line(ln)
            data['hymns'].append(('K', m_k.group(1), verses))
            continue

        m_t = re.search(r'\bT[-\s]?(\d{1,4})\b', ln, re.I)
        if m_t:
            verses = extract_verses_from_line(ln)
            data['hymns'].append(('T', m_t.group(1), verses))
            continue

        m_ps = psalm_pattern.search(ln)
        if m_ps and not data['psalm']:
            data['psalm'] = "Psalm " + m_ps.group(1)
            continue

        if re.search(r'Old Testament|O\.T\.|Old Testa|Old Test', ln, re.I):
            mv = bible_verse_pattern.search(ln) or (
                i+1 < len(lines) and bible_verse_pattern.search(lines[i+1])
            )
            if mv:
                data['old_testament'] = mv.group(1)
            continue

        if re.search(r'New Testament|N\.T\.|N\.T|New Testa', ln, re.I):
            mv = bible_verse_pattern.search(ln) or (
                i+1 < len(lines) and bible_verse_pattern.search(lines[i+1])
            )
            if mv:
                data['new_testament'] = mv.group(1)
            continue

        if re.search(r'Gospel Reading|Gospel', ln, re.I):
            mv = bible_verse_pattern.search(ln) or (
                i+1 < len(lines) and bible_verse_pattern.search(lines[i+1])
            )
            if mv:
                data['gospel'] = mv.group(1)
            continue

        if re.match(r'ANNOUNCEMENTS', ln, re.I):
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

        if re.search(r'Happy Birthday|Birthday', ln, re.I):
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

        m_ser = re.search(r'Sermon[:\s]*(.+)', ln, re.I)
        if m_ser and not data['sermon']:
            data['sermon'] = m_ser.group(1).strip()

    # dedupe hymn numbers while preserving order
    seen = set()
    deduped = []
    for h in data['hymns']:
        hashable_h = (h[0], h[1], tuple(h[2]) if len(h) > 2 else ())
        if hashable_h not in seen:
            deduped.append(h)
            seen.add(hashable_h)

    data['hymns'] = deduped  # store back

    return data  # ✅ always return dict, never None


# wrapper used by app
def parse_pdf_to_structured_wrapper(path):
    return parse_pdf_to_structured(path)
