import pandas as pd
import json
import time
from google import genai
from google.genai import types

# Replace with your actual key
API_KEY = "YOUR_API_KEY_HERE"
client = genai.Client(api_key=API_KEY)

STRICT_DISCIPLINES = [
    "Administration", "Aesthetics", "Agriculture", "Anthropology", "Archaeology", 
    "Architecture", "Art", "Art History", "Astronomy", "Bibliography", "Biography", 
    "Biology", "Botany", "Byzantine Studies", "Cardiology", "Chemistry", "Chronology", 
    "Classics", "Climatology", "Codicology", "Comparative Literature", "Cosmology", 
    "Criminology", "Cultural Studies", "Demography", "Dialectology", "Diplomatics", 
    "Drama", "Earth Sciences", "Economics", "Education", "Egyptology", "Engineering", 
    "Environmental Science", "Epidemiology", "Epigraphy", "Ethics", "Ethnography", 
    "Ethnology", "Eugenics", "Exploration", "Folklore", "Gender Studies", "Genealogy", 
    "Geography", "Geology", "Health", "Historiography", "History", "History Of Architecture", 
    "History Of Education", "History Of Geography", "History Of Medicine", "History Of Philosophy", 
    "History Of Science", "International Relations", "Islamic Studies", "Journalism", 
    "Labor Studies", "Law", "Library Science", "Linguistics", "Literary Criticism", 
    "Literature", "Logic", "Mathematics", "Medicine", "Meteorology", "Metrology", 
    "Mineralogy", "Mining", "Museology", "Music", "Musicology", "Mythology", 
    "Natural History", "Natural Sciences", "Neuroscience", "Numismatics", "Nursing", 
    "Nutrition", "Obstetrics", "Ophthalmology", "Ottoman Greek History", "Ottoman History", 
    "Palaeography", "Paleography", "Pedagogy", "Pediatrics", "Philology", "Philosophy", 
    "Philosophy Of Science", "Photography", "Physical Education", "Physics", "Physiology", 
    "Poetry", "Political Science", "Prehistory", "Psychiatry", "Psychology", "Public Health", 
    "Publishing", "Religion", "Rhetoric", "Science", "Seismology", "Sigillography", 
    "Sociology", "Sports History", "Sports Science", "Statistics", "Theater Studies", 
    "Theology", "Topography", "Toponymy", "Toxicology", "Travel", "Travelogue", 
    "Urban Studies", "Women'S Studies", "Zoology"
]

def get_additional_tags(title, entry_type, existing_tags, max_retries=3):
    slots_left = 3 - len(existing_tags)
    
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
    
    Respond STRICTLY with a JSON array of strings. Example: ["Archaeology"]
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
    output_file = 'test_50_additive.csv'
    
    print(f"Loading '{input_file}' and testing first 50 rows...")
    df = pd.read_csv(input_file).head(50)  # ONLY TAKE FIRST 50 ROWS
        
    for index, row in df.iterrows():
        title = str(row['title_english']) if pd.notna(row['title_english']) else str(row['title_greek'])
        existing_tags_str = str(row['disciplines']) if pd.notna(row['disciplines']) else ""
        existing_tags = [t.strip() for t in existing_tags_str.split(',')] if existing_tags_str and existing_tags_str.lower() != 'n/a' else []
        
        if title.lower() not in ['nan', 'none', '']:
            new_tags = get_additional_tags(title, row['entry_type'], existing_tags)
            combined_tags = existing_tags + new_tags
            
            # Print the breakdown so you can see exactly what happened
            added_str = f"Added: {new_tags}" if new_tags else "Added: NOTHING"
            print(f"Row {index + 1} | Old: {existing_tags} | {added_str} | Final: {combined_tags[:3]}")
            
            if combined_tags:
                df.at[index, 'disciplines'] = ", ".join(combined_tags[:3])
            else:
                df.at[index, 'disciplines'] = "N/A"
                
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 50-row test complete! Check your terminal output above, or open '{output_file}' to review.")

if __name__ == "__main__":
    main()