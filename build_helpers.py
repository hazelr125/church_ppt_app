# build_helpers.py
from parse_pdf import parse_pdf_to_structured
from bible_fetch import fetch_bible_passage
from hymns_db import HymnDatabase, get_hymn_verses
import re

def parse_pdf_to_structured_wrapper(path):
    return parse_pdf_to_structured(path)

def build_mapping_wrapper(parsed: dict, hymn_db: "HymnDatabase"):
    """
    Build mapping of placeholders -> text and a simple announcements_table.
    The template must have placeholders like:
      {WELCOME},
      {HYMN1_KN_V1}, {HYMN1_EN_V1}, {HYMN1_KN_V2}, ...
       {PSALM_EN_V1}, ...
      {OT_EN}, {NT_EN}, {GOSPEL_EN}, etc.
      {ANNOUNCEMENTS_TEXT}, {ANNOUNCEMENTS_TABLE}
      {BIRTHDAY_NAMES}, {ANNIVERSARY_NAMES}, {SERMON}, {THANKYOU}
    """
    mapping = {}
    # welcome
    mapping['{WELCOME}'] = "Welcome! \n We are glad you are here."

    if parsed.get("psalm"):
        psalm_ref = parsed["psalm"]
        if not psalm_ref.lower().startswith("psalm"):
            psalm_ref = f"Psalms {psalm_ref}"
        mapping["{PSALMS_DES}"] = f"Responsive Psalm - {psalm_ref} | {parsed['psalm_kn']}"
    if parsed.get("old_testament"):
        mapping["{OT_DES}"] = f"Old Testament - {parsed['old_testament']} | {parsed.get('old_testament_kn','')}"
    if parsed.get("new_testament"):
        mapping["{NT_DES}"] = f"New Testament - {parsed['new_testament']} | {parsed.get('new_testament_kn','')}"
    if parsed.get("gospel"):
        mapping["{GOSPEL_DES}"] = f"Gospel Reading - {parsed['gospel']} | {parsed.get('gospel_kn','')}"

    # Hymns — map sequentially (HYMN1, HYMN2, ...)
    hymns = parsed.get('hymns', [])[:6]
    for i, hymn_info in enumerate(hymns, start=1):
        if len(hymn_info) == 3:
            lang_code, hymn_no, hymn_line = hymn_info
        else:
            lang_code, hymn_no = hymn_info
            hymn_line = f"{lang_code}-{hymn_no}"
    
        # Add description placeholder
        mapping[f'{{HYMN{i}_DES}}'] = hymn_line
        
        language = "kannada" if lang_code.upper() == "K" else "tulu"
        verses_local, verses_en = get_hymn_verses(hymn_no, None, language, hymn_db)
        
        for vnum, txt in verses_local.items():
            mapping[f'{{HYMN{i}_KN_V{vnum}}}'] = txt
        for vnum, txt in verses_en.items():
            mapping[f'{{HYMN{i}_EN_V{vnum}}}'] = txt

    def populate_verse_blocks(passage_key, placeholder_prefix):
        if not parsed.get(passage_key):
            return
        
        blocks = fetch_bible_passage(parsed[passage_key], 'en')
        for idx, block in enumerate(blocks):
            mapping[f'{{{placeholder_prefix}_EN_V{idx+1}}}'] = block
    
    populate_verse_blocks('psalm', 'PSALM')
    populate_verse_blocks('old_testament', 'OT')  
    populate_verse_blocks('new_testament', 'NT')
    populate_verse_blocks('gospel', 'GOSPEL')

    # Psalm — split into paired blocks
    #ps_blocks_en = fetch_bible_passage(parsed.get('psalm',''), 'en') or []
    # ensure same length
    #max_pairs = len(ps_blocks_en)
    #for idx in range(max_pairs):
    #    mapping[f'{{PSALM_EN_V{idx+1}}}'] = ps_blocks_en[idx] if idx < len(ps_blocks_en) else ""

    # Bible readings 
    #mapping['{OT_EN}'] = parsed.get("old_testament_en", "")
    #mapping['{NT_EN}'] = parsed.get("new_testament_en", "")
    #mapping['{GOSPEL_EN}'] = parsed.get("gospel_en", "")
    
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