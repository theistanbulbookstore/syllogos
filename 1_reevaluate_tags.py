import pandas as pd
import json
import time
import os
from google import genai
from google.genai import types

# Replace with your actual key
API_KEY = "YOUR_API_KEY_HERE"
client = genai.Client(api_key=API_KEY)

# The strictly controlled vocabulary (Using lowercase 'of' and clean formatting)
STRICT_DISCIPLINES = [
    "Administration", "Aesthetics", "Agriculture", "Anthropology", "Archaeology", 
    "Architecture", "Art", "Art History", "Astronomy", "Bibliography", "Biography", 
    "Biology", "Botany", "Byzantine Studies", "Cardiology", "Chemistry", "Chronology", 
    "Classics", "Climatology", "Codicology", "Comparative Literature", "Cosmology", 
    "Criminology", "Cultural Studies", "Demography", "Dialectology", "Diplomatics", 
    "Drama", "Earth Sciences", "Economics", "Education", "Egyptology", "Engineering", 
    "Environmental Science", "Epidemiology", "Epigraphy", "Ethics", "Ethnography", 
    "Ethnology", "Eugenics", "Exploration", "Folklore", "Gender Studies", "Genealogy", 
    "Geography", "Geology", "Health", "Historiography", "History", "History of Architecture", 
    "History of Education", "History of Geography", "History of Medicine", "History of Philosophy", 
    "History of Science", "International Relations", "Islamic Studies", "Journalism", 
    "Labor Studies", "Law", "Library Science", "Linguistics", "Literary Criticism", 
    "Literature", "Logic", "Mathematics", "Medicine", "Meteorology", "Metrology", 
    "Mineralogy", "Mining", "Museology", "Music", "Musicology", "Mythology", 
    "Natural History", "Natural Sciences", "Neuroscience", "Numismatics", "Nursing", 
    "Nutrition", "Obstetrics", "Ophthalmology", "Ottoman Greek History", "Ottoman History", 
    "Paleography", "Pediatrics", "Philology", "Philosophy", 
    "Philosophy of Science", "Photography", "Physical Education", "Physics", "Physiology", 
    "Poetry", "Political Science", "Prehistory", "Psychiatry", "Psychology", "Public Health", 
    "Publishing", "Religion", "Rhetoric", "Science", "Seismology", "Sigillography", 
    "Sociology", "Sports History", "Sports Science", "Statistics", "Theater Studies", 
    "Theology", "Topography", "Toponymy", "Toxicology", "Travel", 
    "Urban Studies", "Women's Studies", "Zoology"
]

def clean_legacy_tags(tag_str):
    if pd.isna(tag_str) or str(tag_str).strip().lower() in ['n/a', 'null', 'none', '']:
        return tag_str
    
    tags = [t.strip() for t in str(tag_str).split(',')]
    normalized = []
    
    for t in tags:
        lower_t = t.lower()
        # Map legacy variants and casing inconsistencies directly to our strict list
        if lower_t == 'palaeography':
            normalized.append('Paleography')
        elif lower_t == 'travelogue':
            normalized.append('Travel')
        elif lower_t == 'pedagogy':
            normalized.append('Education')
        elif lower_t == 'history of science':
            normalized.append('History of Science')
        elif lower_t == 'history of medicine':
            normalized.append('History of Medicine')
        elif lower_t == 'history of education':
            normalized.append('History of Education')
        elif lower_t == 'history of architecture':
            normalized.append('History of Architecture')
        elif lower_t == 'history of philosophy':
            normalized.append('History of Philosophy')
        elif lower_t == 'history of geography':
            normalized.append('History of Geography')
        elif lower_t == 'philosophy of science':
            normalized.append('Philosophy of Science')
        elif lower_t in ['theater', 'theatre', 'theatre studies']:
            normalized.append('Theater Studies')
        elif lower_t == "women's studies":
            normalized.append("Women's Studies")
        else:
            # Match strict capitalization if it already exists in the valid set
            matching_strict = next((s for s in STRICT_DISCIPLINES if s.lower() == lower_t), t)
            normalized.append(matching_strict)
            
    # Deduplicate while preserving order
    seen = set()
    unique_tags = [x for x in normalized if not (x in seen or seen.add(x))]
    return ", ".join(unique_tags)

def get_additional_tags(title, entry_type, existing_tags, max_retries=3):
    ABSOLUTE_LIMIT = 4
    slots_left = ABSOLUTE_LIMIT - len(existing_tags)
    
    if slots_left <= 0:
        return []

    prompt = f"""
    You are an archivist classifying academic works from the 19th/20th-century Hellenic Philological Society.
    
    TITLE: "{title}"
    ENTRY TYPE: {entry_type}
    CURRENT TAGS: {existing_tags}
    
    Your task is to select up to a MAXIMUM of {slots_left} ADDITIONAL disciplines that strongly apply to this title, but are NOT already in the CURRENT TAGS.
    You do not have to select {slots_left} if fewer are appropriate. If no additional tags apply, return an empty array [].
    
    ALLOWED LIST: {', '.join(STRICT_DISCIPLINES)}
    
    Respond STRICTLY with a JSON array of strings. Example: ["Paleography"]
    """
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-pro-latest", 
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.0) 
            )
            text = response.text.replace("```json", "").replace("```", "").strip()
            new_tags = json.loads(text)
            
            valid_new_tags = [t for t in new_tags if t in STRICT_DISCIPLINES and t not in existing_tags]
            return valid_new_tags[:slots_left]
            
        except Exception as e:
            time.sleep(2)
            
    return []

def main():
    input_file = 'philological_society_deduped.csv'
    output_file = 'philological_society_deduped_ai_additive.csv'
    
    if os.path.exists(output_file):
        print(f"Found existing progress in '{output_file}'. Resuming automatically...")
        df = pd.read_csv(output_file)
        if 'processed' not in df.columns:
            df['processed'] = False
    else:
        print(f"Loading '{input_file}' from scratch...")
        df = pd.read_csv(input_file)
        df['disciplines'] = df['disciplines'].apply(clean_legacy_tags)
        df['processed'] = False
        
    total_rows = len(df)
    print(f"Processing {total_rows} entries with additive check & lowercase 'of' normalization (Max cap: 4)...")
    
    for index, row in df.iterrows():
        if row.get('processed') == True:
            continue
            
        title = str(row['title_english']) if pd.notna(row['title_english']) else str(row['title_greek'])
        
        existing_tags_str = str(row['disciplines']) if pd.notna(row['disciplines']) else ""
        existing_tags = [t.strip() for t in existing_tags_str.split(',')] if existing_tags_str and existing_tags_str.lower() != 'n/a' else []
        
        if title.lower() not in ['nan', 'none', '']:
            new_tags = get_additional_tags(title, row['entry_type'], existing_tags)
            combined_tags = existing_tags + new_tags
            
            if combined_tags:
                df.at[index, 'disciplines'] = ", ".join(combined_tags[:4])
            else:
                df.at[index, 'disciplines'] = "N/A"
                
        df.at[index, 'processed'] = True
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        if index % 25 == 0 or index == total_rows - 1:
            print(f"Processed {index + 1}/{total_rows}... -> {df.at[index, 'disciplines']}")
            
    df = df.drop(columns=['processed'])
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Complete! All {total_rows} records safely saved to '{output_file}'.")

if __name__ == "__main__":
    main()