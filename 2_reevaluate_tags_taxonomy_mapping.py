import pandas as pd

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
    
    # --- HISTORY OF [X] ---
    "History of Architecture": ["History", "Architecture"],
    "History of Education": ["History", "Education"],
    "History of Geography": ["History", "Geography & Earth Sciences"],
    "History of Medicine": ["History", "Medicine"],
    "History of Philosophy": ["History", "Philosophy"],
    "History of Science": ["History", "Natural & Exact Science"],
    "Art History": ["History", "Art"],

    # --- MEDICINE & HEALTH ---
    "Health": ["Medicine"],
    "Nutrition": ["Medicine", "Health"],
    "Cardiology": ["Medicine"],
    "Epidemiology": ["Medicine", "Public Health"],
    "Neuroscience": ["Medicine", "Psychology"],
    "Nursing": ["Medicine"],
    "Obstetrics": ["Medicine"],
    "Ophthalmology": ["Medicine"],
    "Pediatrics": ["Medicine"],
    "Psychiatry": ["Medicine", "Psychology"],
    "Public Health": ["Medicine"],
    "Toxicology": ["Medicine"],
    "Eugenics": ["Medicine", "Sociology"], 

    # --- SCIENCE, NATURE & MATH ---
    "Science": ["Natural & Exact Science"],
    "Natural Sciences": ["Natural & Exact Science"],
    "Agriculture": ["Natural & Exact Science"],
    "Astronomy": ["Natural & Exact Science"],
    "Cosmology": ["Natural & Exact Science", "Astronomy"],
    "Biology": ["Natural & Exact Science"],
    "Physiology": ["Natural & Exact Science", "Biology"],
    "Botany": ["Natural & Exact Science"],
    "Chemistry": ["Natural & Exact Science"],
    "Environmental Science": ["Natural & Exact Science"],
    "Natural History": ["Natural & Exact Science"],
    "Physics": ["Natural & Exact Science"],
    "Zoology": ["Natural & Exact Science"],
    "Mathematics": ["Natural & Exact Science"],
    "Statistics": ["Natural & Exact Science", "Mathematics"],
    "Engineering": ["Natural & Exact Science"],
    "Mining": ["Natural & Exact Science", "Engineering"],

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
    "Geography": ["Geography & Earth Sciences"],
    "Earth Sciences": ["Geography & Earth Sciences"],
    "Topography": ["Geography & Earth Sciences"],
    "Toponymy": ["Geography & Earth Sciences", "Linguistics"],
    "Exploration": ["Geography & Earth Sciences", "History"],
    "Travel": ["Geography & Earth Sciences"],
    "Geology": ["Natural & Exact Science", "Geography & Earth Sciences"],
    "Mineralogy": ["Natural & Exact Science", "Geography & Earth Sciences"],
    "Seismology": ["Natural & Exact Science", "Geography & Earth Sciences"],
    "Climatology": ["Natural & Exact Science", "Geography & Earth Sciences"],
    "Meteorology": ["Natural & Exact Science", "Geography & Earth Sciences"],
    "Urban Studies": ["Sociology", "Geography & Earth Sciences"],

    # --- PHILOSOPHY & RELIGION ---
    "Ethics": ["Philosophy"],
    "Logic": ["Philosophy"],
    "Aesthetics": ["Philosophy", "Art"],
    "Philosophy of Science": ["Philosophy", "Natural & Exact Science"],
    "Theology": ["Religion"],
    "Mythology": ["Religion", "Folklore"],
    "Islamic Studies": ["Religion", "History"],

    # --- ARTS & CULTURE ---
    "Musicology": ["Music"],
    "Theater Studies": ["Art", "Literature"],
    "Photography": ["Art"],
    "Museology": ["Art", "History"],

    # --- SOCIAL SCIENCES & HUMANITIES ---
    "Folklore": ["Anthropology"],
    "Ethnology": ["Anthropology"],
    "Ethnography": ["Anthropology"],
    "Demography": ["Sociology"],
    "Criminology": ["Sociology", "Law & Political Science"],
    "Labor Studies": ["Sociology", "Economics"],
    "Women's Studies": ["Sociology", "Cultural Studies"],
    "Gender Studies": ["Sociology", "Cultural Studies"],
    
    # --- LAW & POLITICAL SCIENCE ---
    "Law": ["Law & Political Science"],
    "Political Science": ["Law & Political Science"],
    "International Relations": ["Law & Political Science"],

    # --- EDUCATION & SPORTS ---
    "Physical Education": ["Education"],
    "Sports Science": ["Education"],
    "Sports History": ["History", "Sports Science", "Education"],

    # --- ECONOMICS ---
    "Metrology": ["Natural & Exact Science", "Economics"],

    # --- PUBLISHING / INFO ---
    "Publishing": ["Education"],
    "Library Science": ["Philology"],
    "Bibliography": ["Library Science", "Philology"],
    "Journalism": ["Literature"]
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
    # Make sure this points to your specific "before mapping" file
    input_csv = 'yedek/philological_society_deduped_ai_additive-beforestep2-taxonomymapping.csv'
    output_csv = 'philological_society_deduped_final.csv'
    
    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    
    df['disciplines'] = df['disciplines'].apply(expand_disciplines)
    
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✅ Success! Taxonomy applied. Master dataset saved to root folder as '{output_csv}'.")

if __name__ == "__main__":
    apply_taxonomy()