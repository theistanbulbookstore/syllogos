import pandas as pd
import re

# Load the dataset
df = pd.read_csv("philological_society_master.csv")

# 1. THE OVERWRITE DICTIONARY (Fixing LLM Hallucinations)
# This forces the hallucinated masculine English artifacts back into pure Greek genitive transliterations
correction_aliases = {
    "a. karatheodoris": "A. Karatheodori",
    "karatheodoris, a.": "A. Karatheodori",
    
    "a. kopasis": "A. Kopasi",
    "kopasis, a.": "A. Kopasi",
    
    "d. chaviaras": "D. Chaviara",
    "chaviaras, d.": "D. Chaviara",
    
    "i. miliopoulos": "I. Miliopoulou",
    "miliopoulos, i.": "I. Miliopoulou",
    
    "i. vasiadis": "I. Vasiadou",
    "vasiadis, i.": "I. Vasiadou",
    
    "k. kontopoulos": "K. Kontopoulou",
    "kontopoulos, k.": "K. Kontopoulou",
    
    "p. kelaiditos": "P. Kelaiditou",
    "kelaiditos, p.": "P. Kelaiditou",
    
    "s. manasseidis": "S. Manasseidou",
    "manasseidis, s.": "S. Manasseidou",
    
    "s. mavrogenis": "S. Mavrogenous",
    "mavrogenis, s.": "S. Mavrogenous",
    
    "x. a. sideropoulos": "X. A. Sideropoulou",
    "sideropoulos, x. a.": "X. A. Sideropoulou",
    
    "x. sideridis": "X. Sideridou",
    "sideridis, x.": "X. Sideridou"
}

# 2. THE VIP DICTIONARY (Only historically verified nominative/genitive pairs remain)
author_aliases = {
    "makri, k.": "K. Makris", "k. makre": "K. Makris", "k. makri": "K. Makris",
    "κ. μακρῆ": "K. Makris", "κ. μακρής": "K. Makris", "κ. μακρῆς": "K. Makris", "κωνσταντίνος μακρῆς": "K. Makris",
    "m. paranika": "M. Paranikas", "m paranika": "M. Paranikas", "paranika, m.": "M. Paranikas",
    "paranikas, m.": "M. Paranikas", "paranikas, matthaios": "M. Paranikas", "matthaios paranikas": "M. Paranikas",
    "μ. παρανίκα": "M. Paranikas", "μ. παρανίκας": "M. Paranikas",
    "gedeon, m.": "M. Gedeon", "μ. γεδεών": "M. Gedeon", "μανουήλ γεδεών": "M. Gedeon", "manouil gedeon": "M. Gedeon",
    "ioannis aristoklis": "I. Aristoklis", "aristoklis, i.": "I. Aristoklis", "ι. αριστοκλής": "I. Aristoklis",
    "papadopoulos kerameus, a.": "A. Papadopoulos Kerameus", "a. papadopoulou kerameos": "A. Papadopoulos Kerameus", "ἀ. παπαδόπουλος κεραμεύς": "A. Papadopoulos Kerameus",
    "pantazidis, chr.": "Chr. Pantazidis", "χ. πανταζίδης": "Chr. Pantazidis",
    "chatzichristou, chr.": "Chr. Chatzichristou", "christos chatzichristou": "Chr. Chatzichristou", "chatzichristou, christos": "Chr. Chatzichristou",
    "karolidou, i.": "I. Karolidis", "karolidis, i.": "I. Karolidis", "karolidis, pavlos": "P. Karolidis",
    "stamatiadou, d.": "D. Stamatiadis", "stamatiadis, d.": "D. Stamatiadis", "δημήτριος σταματιάδης": "D. Stamatiadis",
    "kalliadis, k.": "K. Kalliadis", "oikonomidis, d.": "D. Oikonomidis", "vasiadis, ir.": "Ir. Vasiadis",
    "ιωάννης ζίφος": "I. Zifos", "zifos, i.": "I. Zifos",
    
    # Verified genitive/nominative pairs (proved by Greek text)
    "a. paspati": "A. Paspatis", "paspatis, a.": "A. Paspatis", "paspati, a. g.": "A. Paspatis", "αλέξανδρος πασπάτης": "A. Paspatis",
    "a. zoirou": "A. Zoiros", "d. antipa": "D. Antipas", "d. mostratou": "D. Mostratos",
    "d. oikonomidou": "D. Oikonomidis", "i. aspriotou": "I. Aspriotis", "i. papadopoulou": "I. Papadopoulos",
    "i. valavani": "I. Valavanis", "l. limaraki": "L. Limarakis", "m. afthentopoulou": "M. Afthentopoulos",
    "p. k. vizoukidou": "P. Vizoukidis", "v. konou": "V. Konos", "v. ritsou": "V. Ritsos",
    "v. mystakidou": "V. Mystakidis" 
}

def standardize_row(row):
    # 1. Force fix the english author column if it was hallucinated
    en_raw = str(row['author_english']).strip()
    if en_raw.lower() in correction_aliases:
        row['author_english'] = correction_aliases[en_raw.lower()]
        
    # 2. Grab the name to normalize
    raw_name = str(row['normalized_author']) if pd.notna(row['normalized_author']) else \
               str(row['author_english']) if pd.notna(row['author_english']) else \
               str(row['author_greek']) if pd.notna(row['author_greek']) else "Anonymous"
               
    raw_name = raw_name.strip()
    if raw_name.endswith('.'):
        parts = raw_name.split()
        if len(parts) > 0 and len(parts[-1]) > 2:
            raw_name = raw_name[:-1]

    lower_name = raw_name.lower()

    if lower_name in ["anonymous", "ανώνυμος", "various", "unknown", "nan", "n/a"]:
        row['normalized_author'] = "Anonymous"
        return row

    # 3. Apply reverse-corrections first
    if lower_name in correction_aliases:
        row['normalized_author'] = correction_aliases[lower_name]
        return row
        
    # 4. Check VIP dictionary
    if lower_name in author_aliases:
        row['normalized_author'] = author_aliases[lower_name]
        return row

    # 5. Flip commas and check dictionaries again
    match = re.match(r"^([^,]+),\s*(.+)$", raw_name)
    if match:
        reversed_name = f"{match.group(2).strip()} {match.group(1).strip()}"
        rev_lower = reversed_name.lower()
        if rev_lower in correction_aliases:
            row['normalized_author'] = correction_aliases[rev_lower]
        elif rev_lower in author_aliases:
            row['normalized_author'] = author_aliases[rev_lower]
        else:
            row['normalized_author'] = reversed_name
        return row

    row['normalized_author'] = raw_name
    return row

# Apply standardizer
df = df.apply(standardize_row, axis=1)

# Save
df.to_csv("philological_society_master.csv", index=False)
print("Dataset successfully cleaned. Hallucinations burned out!")