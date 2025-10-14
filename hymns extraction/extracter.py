import re
import csv
import os

source_folder = "."

pattern = re.compile(
    r'hymnInsert\(\s*([^,]+),\s*"((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*([^)]*)\)',
    re.DOTALL
)

data = []
kannada_count = 0
tulu_count = 0
last_kannada_num = 0
last_tulu_num = 0

def smart_decode(raw):
    if "\\u" in raw:
        try:
            return raw.encode("latin-1").decode("unicode_escape")
        except Exception:
            pass
    if "à²" in raw or "Ã" in raw:
        try:
            return raw.encode("latin-1").decode("utf-8")
        except Exception:
            pass
    return raw

def clean_text(text):
    text = text.strip()
    text = re.sub(r"^\d+\s+", "", text)
    return text

for root, _, files in os.walk(source_folder):
    for file in files:
        if file.endswith(".java"):
            with open(os.path.join(root, file), encoding="latin-1", errors="ignore") as f:
                text = f.read()
                for match in pattern.finditer(text):
                    raw_num = match.group(1).strip()

                    # Determine whether this is Kannada or Tulu
                    if raw_num.isdigit():
                        hymn_no = int(raw_num)
                        is_kannada = hymn_no <= 410
                    else:
                        # Guess category based on last known
                        is_kannada = last_kannada_num > 0 and tulu_count == 0

                    kannada = smart_decode(match.group(2))
                    english = smart_decode(match.group(3))
                    number_171 = match.group(4).strip()
                    author = match.group(5).strip()
                    kannada_category = match.group(6).strip()
                    english_category = match.group(7).strip()
                    last_num = match.group(8).strip()

                    kannada = clean_text(kannada.replace("\r", "").replace("\n", "\\n"))
                    english = clean_text(english.replace("\r", "").replace("\n", "\\n"))

                    if is_kannada:
                        if raw_num.isdigit():
                            last_kannada_num += 1
                        else:
                            last_kannada_num += 1  # auto-increment missing
                        data.append([
                            last_kannada_num, kannada, english, number_171, author,
                            kannada_category, english_category, last_num
                        ])
                    else:
                        if raw_num.isdigit():
                            last_tulu_num += 1
                        else:
                            last_tulu_num += 1  # auto-increment missing
                        data.append([
                            last_tulu_num, kannada, english, number_171, author,
                            "Tulu", "Tulu", last_num
                        ])

with open("hymns.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    writer.writerow([
        "Hymn No", "Kannada", "English", "Number", "Author",
        "Kannada Category", "English Category", "Last Num"
    ])
    writer.writerows(data)

print(f"✅ Extracted {len(data)} hymns to hymns.csv")
