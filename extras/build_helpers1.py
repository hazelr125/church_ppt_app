# build_helpers.py
from parse_pdf import parse_pdf_to_structured
from hymns_db1 import load_hymn_db, split_hymn_into_placeholders
from bible_fetch import fetch_bible_passage
import re

def parse_pdf_to_structured_wrapper(path):
    return parse_pdf_to_structured(path)

def load_hymn_db_wrapper(path):
    return load_hymn_db(path)

def build_mapping_wrapper(parsed: dict, hymn_db: dict):
    """
    Build mapping of placeholders -> text and a simple announcements_table.
    The template must have placeholders like:
      {WELCOME},
      {HYMN1_KN_V1}, {HYMN1_EN_V1}, {HYMN1_KN_V2}, ...
      {PSALM_KN_V1}, {PSALM_EN_V1}, {PSALM_KN_V2}, ...
      {OT_EN}, {OT_KN}, {NT_EN}, {GOSPEL_EN}, etc.
      {ANNOUNCEMENTS_TEXT}, {ANNOUNCEMENTS_TABLE}
      {BIRTHDAY_NAMES}, {ANNIVERSARY_NAMES}, {SERMON}, {THANKYOU}
    """
    mapping = {}
    # welcome
    mapping['{WELCOME}'] = "Welcome! \n We are glad you are here."

    # Hymns — map sequentially (HYMN1, HYMN2, ...)
    hymns = parsed.get('hymns', [])[:6]
    for i, (lang_code, hymn_no, verses) in enumerate(hymns, start=1):
        verses_kn, verses_en = split_hymn_into_placeholders(hymn_no, hymn_db, lang_code)
        verses_to_use = verses or verses_en.keys()  # if no verses given, use all
        for vnum in verses_to_use:
            if vnum in verses_kn:
                mapping[f'{{HYMN{i}_KN_V{vnum}}}'] = verses_kn[vnum]
            if vnum in verses_en:
                mapping[f'{{HYMN{i}_EN_V{vnum}}}'] = verses_en[vnum]


    # Psalm — split into paired blocks
    ps_blocks_en = fetch_bible_passage(parsed.get('psalm',''), lang='en') or []
    ps_blocks_kn = fetch_bible_passage(parsed.get('psalm',''), lang='kn') or []
    # ensure same length
    max_pairs = max(len(ps_blocks_en), len(ps_blocks_kn))
    for idx in range(max_pairs):
        mapping[f'{{PSALM_EN_V{idx+1}}}'] = ps_blocks_en[idx] if idx < len(ps_blocks_en) else ""
        mapping[f'{{PSALM_KN_V{idx+1}}}'] = ps_blocks_kn[idx] if idx < len(ps_blocks_kn) else ""

    # Bible readings 
    mapping['{OT_EN}'] = "\n\n".join(fetch_bible_passage(parsed.get('old_testament',''), 'en')) if parsed.get('old_testament') else ""
    mapping['{NT_EN}'] = "\n\n".join(fetch_bible_passage(parsed.get('new_testament',''), 'en')) if parsed.get('new_testament') else ""
    mapping['{GOSPEL_EN}'] = "\n\n".join(fetch_bible_passage(parsed.get('gospel',''), 'en')) if parsed.get('gospel') else ""
    
    # announcements
    mapping['{ANNOUNCEMENTS_TEXT}'] = parsed.get('announcements_block','(No announcements provided)')
    # build simple announcements table rows from announcements_block lines
    rows = [["Particulars","Amount(RS)"]]
    for line in parsed.get('announcements_block','').splitlines():
        line = line.strip()
        if not line:
            continue
        # try to capture amount at end
        m = re.search(r'(\d{1,3}(?:[,\d]{0,})\/?-?)$', line.replace(' ', ' '))
        if m:
            amt = m.group(1)
            desc = line[:line.rfind(amt)].strip()
            rows.append([desc, amt])
        else:
            rows.append([line, ""])
    announcements_table = rows if len(rows)>1 else None

    # birthdays / anniversaries
    mapping['{BIRTHDAY_NAMES}'] = "\n".join(parsed.get('birthday_names',[]))
    mapping['{ANNIVERSARY_NAMES}'] = "\n".join(parsed.get('anniversary_names',[]))

    mapping['{THANKYOU}'] = "Thank you — May God bless you always."

    return mapping, announcements_table
