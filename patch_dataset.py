import pandas as pd
import time
from google import genai
from google.genai import types

# 1. Setup API and Files
API_KEY = "YOUR_API_KEY_HERE" # Replace with your actual key
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-pro-latest" # Matches your original script's model

input_file = "philological_society_master.csv"
output_file = "philological_society_master_final.csv"
df = pd.read_csv(input_file)

print("Building author memory from existing dataset...")

# 2. Build Author Memory (Non-destructive)
existing_eng_map = {}
existing_norm_map = {}

def is_empty(val):
    """Matches the exact empty-check logic from your original script"""
    return pd.isna(val) or str(val).strip().lower() in ['', 'null', 'none', 'nan']

for _, row in df.iterrows():
    gr = str(row['author_greek']).strip() if not is_empty(row['author_greek']) else ""
    en = str(row['author_english']).strip() if not is_empty(row['author_english']) else ""
    norm = str(row['normalized_author']).strip() if not is_empty(row['normalized_author']) else ""
    
    if gr and en and gr not in existing_eng_map: 
        existing_eng_map[gr] = en
    if gr and norm and gr not in existing_norm_map: 
        existing_norm_map[gr] = norm

def fallback_transliterate(text):
    if is_empty(text): return text
    t = str(text)
    replacements = {'ου': 'ou', 'Ου': 'Ou', 'ΟΥ': 'OU', 'αυ': 'av', 'Αυ': 'Av', 'ευ': 'ev', 'Ευ': 'Ev', 'μπ': 'b', 'Μπ': 'B', 'ντ': 'nt', 'Ντ': 'Nt', 'τσ': 'ts', 'Τσ': 'Ts', 'τζ': 'tz', 'Τζ': 'Tz', 'γγ': 'ng', 'γκ': 'gk', 'Γκ': 'Gk', 'θ': 'th', 'Θ': 'Th', 'χ': 'ch', 'Χ': 'Ch', 'ψ': 'ps', 'Ψ': 'Ps', 'ω': 'o', 'Ω': 'O', 'η': 'i', 'Η': 'I', 'υ': 'y', 'Υ': 'Y'}
    for k, v in replacements.items(): t = t.replace(k, v)
    char_map = {'α':'a', 'β':'v', 'γ':'g', 'δ':'d', 'ε':'e', 'ζ':'z', 'ι':'i', 'κ':'k', 'λ':'l', 'μ':'m', 'ν':'n', 'ξ':'x', 'ο':'o', 'π':'p', 'ρ':'r', 'σ':'s', 'ς':'s', 'τ':'t', 'φ':'f', 'ά':'a', 'έ':'e', 'ή':'i', 'ί':'i', 'ό':'o', 'ύ':'y', 'ώ':'o', 'ϊ':'i', 'ϋ':'y', 'ΐ':'i', 'ΰ':'y', 'Α':'A', 'Β':'V', 'Γ':'G', 'Δ':'D', 'Ε':'E', 'Ζ':'Z', 'Ι':'I', 'Κ':'K', 'Λ':'L', 'Μ':'M', 'Ν':'N', 'Ξ':'X', 'Ο':'O', 'Π':'P', 'Ρ':'R', 'Σ':'S', 'Τ':'T', 'Φ':'F', 'Ά':'A', 'Έ':'E', 'Ή':'I', 'Ί':'I', 'Ό':'O', 'Ύ':'Y', 'Ώ':'O'}
    return "".join(char_map.get(c, c) for c in t)

def fallback_normalize(name):
    if is_empty(name): return name
    parts = str(name).strip().split()
    if len(parts) > 1: return f"{parts[-1]}, {' '.join(parts[:-1])}".replace('.,', ',')
    return name

# 3. Target Specific Lecture Rows
lectures_1908 = df[(df['volume_or_year_greek'] == '1908 - 1909') & (df['entry_type'] == 'Public Lecture')].index.tolist()
lectures_1909 = df[(df['volume_or_year_greek'] == '1909 - 1910') & (df['entry_type'] == 'Public Lecture')].index.tolist()
lectures_1910 = df[(df['volume_or_year_greek'] == '1910 - 1911') & (df['entry_type'] == 'Public Lecture')].index.tolist()

target_title_indices = set()
if lectures_1908: target_title_indices.update(lectures_1908[1:])
if lectures_1909: target_title_indices.update(lectures_1909)
if lectures_1910: target_title_indices.add(lectures_1910[0])

# 4. Gemini Translation Function (Matches your original prompt context)
def translate_title_with_gemini(greek_title):
    prompt = f"""
    You are an expert archivist working with a catalog of the Hellenic Philological Society.
    Translate the following Greek title into English. 
    Output ONLY the English translation. Do not add quotes or formatting.
    
    Greek Title: {greek_title}
    """
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3) # Matches your original 0.3 temp
        )
        time.sleep(1) # Prevent rate limiting
        return response.text.strip()
    except Exception as e:
        print(f"  API Error: {e}")
        return None

print("Patching dataset based on rules...")

# 5. Apply Fixes
for idx, row in df.iterrows():
    # FIX AUTHORS (Uses memory map or fallback transliteration)
    gr_author = str(row['author_greek']).strip() if not is_empty(row['author_greek']) else ""
    if gr_author:
        if is_empty(row['author_english']):
            df.at[idx, 'author_english'] = existing_eng_map.get(gr_author, fallback_transliterate(gr_author))
        if is_empty(row['normalized_author']):
            df.at[idx, 'normalized_author'] = existing_norm_map.get(gr_author, fallback_normalize(df.at[idx, 'author_english']))

    # FIX TITLES (Translates missing ones or specifically targeted lecture rows)
    gr_title = row['title_greek']
    is_missing_title = is_empty(row['title_english'])
    
    if (idx in target_title_indices or is_missing_title) and not is_empty(gr_title):
        print(f"Translating row {idx} via Gemini...")
        eng_translation = translate_title_with_gemini(str(gr_title))
        if eng_translation:
            df.at[idx, 'title_english'] = eng_translation

# 6. Save safely
df.to_csv(output_file, index=False, encoding='utf-8-sig') # Matches your original encoding
print(f"Complete! Clean dataset saved as '{output_file}'")