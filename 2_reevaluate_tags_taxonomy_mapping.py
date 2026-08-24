import pandas as pd

# Exhaustive Taxonomy Map for all 119 tags present in the dataset.
# Format: "Specific Subfield": ["Parent Field 1", "Parent Field 2"]
DISCIPLINE_MAP = {
    # --- HISTORY BRANCHES ---
    "Ottoman History": ["History"],
    "Ottoman Greek History": ["History"],
    "Byzantine Studies": ["History"],
    "Historiography": ["History"],
    "Prehistory": ["History", "Archaeology"],
    "Egyptology": ["History", "Archaeology"],
    "Chronology": ["History"],
    "Genealogy": ["History"],
    "Biography": ["History"],
    "Sports History": ["History", "Sports Science"],
    
    # --- HISTORY OF [X] ---
    "History of Architecture": ["History", "Architecture"],
    "History of Education": ["History", "Education"],
    "History of Geography": ["History", "Geography"],
    "History of Medicine": ["History", "Medicine"],
    "History of Philosophy": ["History", "Philosophy"],
    "History of Science": ["History", "Science"],
    "Art History": ["History", "Art"],

    # --- MEDICINE & HEALTH ---
    "Cardiology": ["Medicine"],
    "Epidemiology": ["Medicine", "Public Health"],
    "Health": ["Medicine"],
    "Neuroscience": ["Medicine", "Psychology"],
    "Nursing": ["Medicine"],
    "Nutrition": ["Medicine", "Health"],
    "Obstetrics": ["Medicine"],
    "Ophthalmology": ["Medicine"],
    "Pediatrics": ["Medicine"],
    "Psychiatry": ["Medicine", "Psychology"],
    "Public Health": ["Medicine"],
    "Toxicology": ["Medicine"],
    "Eugenics": ["Medicine", "Sociology"], 

    # --- SCIENCE, NATURE & MATH ---
    "Agriculture": ["Science"],
    "Astronomy": ["Science", "Natural Sciences"],
    "Biology": ["Science", "Natural Sciences"],
    "Botany": ["Science", "Natural Sciences"],
    "Chemistry": ["Science", "Natural Sciences"],
    "Climatology": ["Science", "Geography"],
    "Cosmology": ["Science", "Astronomy"],
    "Earth Sciences": ["Science", "Geology"],
    "Environmental Science": ["Science"],
    "Geology": ["Science", "Natural Sciences"],
    "Meteorology": ["Science", "Geography"],
    "Mineralogy": ["Science", "Natural Sciences"],
    "Natural History": ["Science", "Natural Sciences"],
    "Natural Sciences": ["Science"],
    "Physics": ["Science", "Natural Sciences"],
    "Physiology": ["Science", "Biology"],
    "Seismology": ["Science", "Geology"],
    "Zoology": ["Science", "Natural Sciences"],
    "Mathematics": ["Science"],
    "Statistics": ["Science", "Mathematics"],
    "Metrology": ["Science"],
    "Engineering": ["Science"],
    "Mining": ["Science", "Engineering"],

    # --- LITERATURE & TEXTS ---
    "Comparative Literature": ["Literature"],
    "Drama": ["Literature", "Theater Studies"],
    "Literary Criticism": ["Literature"],
    "Poetry": ["Literature"],
    "Rhetoric": ["Literature", "Philology"],
    
    # --- PHILOLOGY, LINGUISTICS & MANUSCRIPTS ---
    "Linguistics": ["Philology"],
    "Dialectology": ["Linguistics", "Philology"],
    "Codicology": ["Philology", "History"],
    "Paleography": ["Philology", "History"],
    "Diplomatics": ["Philology", "History"],
    "Epigraphy": ["Philology", "Archaeology", "History"],

    # --- ARCHAEOLOGY & ANTIQUITY ---
    "Classics": ["History", "Philology"],
    "Numismatics": ["Archaeology", "History"],
    "Sigillography": ["Archaeology", "History"],

    # --- GEOGRAPHY & PLACE ---
    "Topography": ["Geography"],
    "Toponymy": ["Geography", "Linguistics"],
    "Exploration": ["Geography", "History"],
    "Travel": ["Geography"],

    # --- PHILOSOPHY & RELIGION ---
    "Ethics": ["Philosophy"],
    "Logic": ["Philosophy"],
    "Aesthetics": ["Philosophy", "Art"],
    "Philosophy of Science": ["Philosophy", "Science"],
    "Theology": ["Religion"],
    "Mythology": ["Religion", "Folklore"],
    "Islamic Studies": ["Religion", "History"],

    # --- ARTS & CULTURE ---
    "Musicology": ["Music"],
    "Theater Studies": ["Art", "Literature"],
    "Photography": ["Art"],
    "Museology": ["Art", "History"],

    # --- SOCIAL SCIENCES & HUMANITIES ---
    "Ethnology": ["Anthropology"],
    "Ethnography": ["Anthropology"],
    "Demography": ["Sociology"],
    "Criminology": ["Sociology", "Law"],
    "Labor Studies": ["Sociology", "Economics"],
    "Urban Studies": ["Sociology", "Geography"],
    "Women's Studies": ["Sociology", "Cultural Studies"],
    "Gender Studies": ["Sociology", "Cultural Studies"],
    "International Relations": ["Political Science"],
    
    # --- PUBLISHING / INFO ---
    "Bibliography": ["Library Science", "Publishing"],
    "Journalism": ["Publishing"]
}

def expand_disciplines(discipline_str):
    if pd.isna(discipline_str) or str(discipline_str).strip().lower() in ['n/a', 'null', 'none', '']:
        return discipline_str
        
    current_tags = [d.strip() for d in str(discipline_str).split(',')]
    expanded_tags = set(current_tags) 
    
    for tag in current_tags:
        if tag in DISCIPLINE_MAP:
            for parent_tag in DISCIPLINE_MAP[tag]:
                expanded_tags.add(parent_tag)
                
    return ", ".join(sorted(list(expanded_tags)))

def apply_taxonomy():
    input_csv = 'philological_society_deduped_ai_additive.csv'
    output_csv = 'philological_society_deduped_final.csv'
    
    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    
    df['disciplines'] = df['disciplines'].apply(expand_disciplines)
    
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✅ Success! Taxonomy applied. Master dataset saved to '{output_csv}'.")

if __name__ == "__main__":
    apply_taxonomy()