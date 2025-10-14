from docx import Document
import re

def parse_announcements_docx(docx_path: str):
    """
    Read DOCX and return (table_rows, extra_text).
    Table rows = all lines ending with a Rs amount (e.g. 25,300/-).
    Extra text = everything else.
    """
    doc = Document(docx_path)
    table_rows = [["Particulars", "Amount (Rs)"]]
    extra_lines = []

    for para in doc.paragraphs:
        line = para.text.strip()
        if not line:
            continue

        # Look for amounts like "25,300/-" or "25300/-"
        m = re.search(r'(\d[\d,]*\s*/-)', line)
        if m:
            amt = m.group(1).strip()  # keep commas
            desc = line[:m.start()].strip().rstrip(":")
            table_rows.append([desc, amt])
        else:
            extra_lines.append(line)

    if len(table_rows) == 1:  # no matches, only header
        table_rows = None

    return table_rows, "\n".join(extra_lines)
