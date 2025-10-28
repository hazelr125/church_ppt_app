import pandas as pd
import re
from bible_normalize import normalize_book   # use the centralized one

# Load BSB Excel once
df = pd.read_excel("bsb.xlsx", header=2)

def fetch_bible_passage(passage: str, lang: str = 'en'):
    """
    Fetch Bible passage text from bsb.xlsx.
    Returns a list of text blocks, each containing up to 3 verses.
    """
    if not passage:
        return []
    
    try:
        passage_pattern = re.search(r'([1-3]?\s?[A-Za-z\.]+\.?\s*\d+:\d+(-\d+)?)', passage)
        if passage_pattern:
            passage_to_parse = passage_pattern.group(1)
        else:
            passage_to_parse = passage.strip()


        # Parse input like "Genesis 1:1-4" or "Psalm 103:1-8"
        match = re.match(r"([1-3]?\s?[A-Za-z\.]+)\s+(\d+)(?::(\d+)(?:-(\d+))?)?", passage_to_parse)
        if not match:
            return [f"[Invalid passage format: {passage}]"]
    
        book, chapter, start_verse, end_verse = match.groups()
        normalized_book = normalize_book(book)   # ✅ standardized book name
        chapter = int(chapter)
        start_verse = int(start_verse) if start_verse else 1
        end_verse = int(end_verse) if end_verse else start_verse
        
        # --- Identify columns ---
        verse_column = None
        text_column = None
        
        if "Verse" in df.columns:
            verse_column = "Verse"
        elif len(df.columns) > 1:
            verse_column = df.columns[1]
            
        if "Berean Standard Bible" in df.columns:
            text_column = "Berean Standard Bible"
        else:
            bible_cols = [col for col in df.columns if 'Bible' in str(col)]
            if bible_cols:
                text_column = bible_cols[0]
            elif len(df.columns) > 2:
                text_column = df.columns[2]
        
        if not verse_column or not text_column:
            return [f"[Could not identify verse/text columns. Available: {df.columns.tolist()}]"]
        
        # --- Build references like "Psalm 103:1" ---
        verse_refs = [f"{normalized_book} {chapter}:{i}" for i in range(start_verse, end_verse+1)]
        
        verses = df[df[verse_column].isin(verse_refs)]
        
        if verses.empty:
            similar_verses = df[df[verse_column].str.contains(f"{normalized_book} {chapter}:", na=False)].head(5)
            if not similar_verses.empty:
                available = similar_verses[verse_column].tolist()
                return [f"[No verses found for {passage}. Available verses like: {', '.join(available)}]"]
            else:
                sample_verses = df[verse_column].dropna().head(10).tolist()
                return [f"[No verses found for book '{normalized_book}' chapter {chapter}. Sample verses in file: {sample_verses}]"]

        # --- Format result into blocks ---
        # Sort verses by verse number to ensure proper order
        verses = verses.copy()
        verses['verse_num'] = verses[verse_column].apply(lambda ref: int(re.search(r":(\d+)$", ref).group(1)) if re.search(r":(\d+)$", ref) else 0)
        verses = verses.sort_values(by='verse_num')
        
        verse_texts = []
        for _, v in verses.iterrows():
            verse_ref = v[verse_column]  # e.g., "Psalm 103:1"
            txt = str(v[text_column]).strip()
            
            if txt and txt.lower() != 'nan':
                verse_num = verse_ref.split(":")[-1]   # only the verse number
                verse_texts.append(f"{verse_num} {txt}")
        
        # Split into blocks of 3 verses each
        verses_per_block = 3
        blocks = []
        for i in range(0, len(verse_texts), verses_per_block):
            block_verses = verse_texts[i:i + verses_per_block]
            block_content = "\n".join(block_verses)
            blocks.append(block_content)
        
        return blocks
        
    except Exception as e:
        import traceback
        return [f"[Error fetching {passage}: {str(e)}]"]