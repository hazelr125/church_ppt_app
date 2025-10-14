# hymns_db.py
import csv
import re
import os

def load_hymn_db(csv_path):
    db = {}
    if not os.path.exists(csv_path):
        return db
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hymn_no = str(row.get('Hymn_No', '')).strip()
            if not hymn_no:
                continue
            kn = (row.get('Kannada') or '').strip()
            en = (row.get('English') or '').strip()
            category = (row.get('Kannada Category') or '').strip()
            db[hymn_no] = {
                'kn': kn,
                'en': en,
                'category': category
            }
    return db


def split_into_verses(text, return_lines=False):
    # 1) Normalize actual line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n').strip()
    # 2) Convert literal "\n" sequences (from CSVs etc.) into real newlines
    text = text.replace('\\n', '\n')

    # 3) Grab each numbered verse: from "N." (or "N)") up to the next number or end
    pat = re.compile(r'(?m)^\s*(\d+)[\.\)]\s*(.*?)(?=^\s*\d+[\.\)]\s*|\Z)', re.DOTALL)
    verses = {}
    for num, body in pat.findall(text):
        body = body.strip()
        if not body:
            continue
        if return_lines:
            # split verse body into lines wherever there’s a newline
            lines = [ln.strip() for ln in re.split(r'\n+', body) if ln.strip()]
            verses[int(num)] = [f"{num}. {lines[0]}"] + lines[1:]
        else:
            verses[int(num)] =  f"{num}. {body}"

    # 4) Fallback: if no numbered verses were found, just split on newlines
    if not verses:
        if return_lines:
            return {i+1: ln.strip() for i, ln in enumerate(re.split(r'\n+', text)) if ln.strip()}
        else:
            blocks = [blk.strip() for blk in re.split(r'\n{2,}', text) if blk.strip()]
            return {i+1: blk for i, blk in enumerate(blocks)}

    return verses

def split_hymn_into_placeholders(Hymn_No, hymn_db, lang_code):
    hymn = hymn_db.get(Hymn_No)
    if not hymn:
        return {}, {}
    if lang_code.upper() == 'K' and hymn['category'].lower()== 'kannada':
        verses_local = split_into_verses(hymn['kn'])  # Tulu text in 'kn'
    elif lang_code.upper() == 'T' and hymn['category'].lower() == 'tulu':
        verses_local = split_into_verses(hymn['kn'])  # Kannada text in 'kn'
    else:
        verses_local = {}

    verses_en = split_into_verses(hymn['en'])
    return verses_local, verses_en