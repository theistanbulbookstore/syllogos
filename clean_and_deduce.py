import pandas as pd
import unicodedata
import os

def universal_transliterate(text):
    if pd.isna(text) or str(text).strip() == '': return text
    
    t = str(text).strip().replace('«', '').replace('»', '').replace('”', '').replace('“', '')
    t = t.replace(' καὶ ', ' and ').replace(' - ', ' and ')
    t = t.replace('᾿', '').replace('῾', '').replace('´', '').replace("'", "")
    
    # Strip polytonic accents
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    
    # Greek Phonetic rules
    replacements = {
        'ου': 'ou', 'Ου': 'Ou', 'ΟΥ': 'OU', 'αυ': 'av', 'Αυ': 'Av', 'ευ': 'ev', 'Ευ': 'Ev', 
        'μπ': 'b', 'Μπ': 'B', 'ντ': 'nt', 'Ντ': 'Nt', 'τσ': 'ts', 'Τσ': 'Ts', 'τζ': 'tz', 'Τζ': 'Tz', 
        'γγ': 'ng', 'γκ': 'gk', 'Γκ': 'Gk'
    }
    for k, v in replacements.items(): t = t.replace(k, v)
    
    # Standard character mapping
    char_map = {
        'α':'a', 'β':'v', 'γ':'g', 'δ':'d', 'ε':'e', 'ζ':'z', 'η':'i', 'θ':'th', 'ι':'i', 'κ':'k', 'λ':'l', 'μ':'m', 'ν':'n', 
        'ξ':'x', 'ο':'o', 'π':'p', 'ρ':'r', 'σ':'s', 'ς':'s', 'τ':'t', 'υ':'y', 'φ':'f', 'χ':'ch', 'ψ':'ps', 'ω':'o',
        'Α':'A', 'Β':'V', 'Γ':'G', 'Δ':'D', 'Ε':'E', 'Ζ':'Z', 'Η':'I', 'Θ':'Th', 'Ι':'I', 'Κ':'K', 'Λ':'L', 'Μ':'M', 'Ν':'N', 
        'Ξ':'X', 'Ο':'O', 'Π':'P', 'Ρ':'R', 'Σ':'S', 'Τ':'T', 'Υ':'Y', 'Φ':'F', 'Χ':'Ch', 'Ψ':'Ps', 'Ω':'O'
    }
    res = "".join(char_map.get(c, c) for c in t)
    
    # Normalize typical 19th century Latin aliases (e.g. Ph -> F)
    res = res.replace('Ph', 'F').replace('ph', 'f')
    
    parts = res.split()
    for i in range(len(parts)-1):
        if len(parts[i]) <= 3 and not parts[i].endswith('.'):
            if parts[i].lower() != 'and':
                parts[i] += '.'
    return " ".join(parts).rstrip(',').rstrip('.')

def get_universal_stem(surname_english):
    s = surname_english.lower()
    # Strip universal suffixes (Latinized versions of Greek endings)
    suffixes = ['ous', 'ou', 'is', 'os', 'as', 'a', 'eos', 'evs', 'i', 'on', 'es']
    for suf in suffixes:
        if s.endswith(suf):
            s = s[:-len(suf)]
            break
            
    # Fuzzy normalization for typos (e.g. kalleuras vs kalevras, dethier vs dethiir)
    s = s.replace('ll', 'l').replace('eu', 'ev').replace('y', 'i').replace('c', 'k').replace('ie', 'ii')
    return s

def tokenize_initials(initial_str):
    return initial_str.replace('.', ' ').strip().lower().split()

def is_subset(init1, init2):
    t1 = tokenize_initials(init1)
    t2 = tokenize_initials(init2)
    
    if not t1 or not t2: return False
    if t1 == t2: return True 
    
    # Bidirectional matching: checks if either array starts with the other
    if t1[0].startswith(t2[0]) or t2[0].startswith(t1[0]):
        if len(t1) == 1 or len(t2) == 1: return True
        if len(t1) > 1 and len(t2) > 1:
            if t1[1].startswith(t2[1]) or t2[1].startswith(t1[1]): return True
            return False
    return False

def standardize_dataset(input_csv, output_csv, report_txt):
    df = pd.read_csv(input_csv)
    
    def parse_name(english_str):
        if pd.isna(english_str): return "", ""
        clean = str(english_str).strip().rstrip('.').rstrip(',').strip()
        
        titles = [' iatrou', ' patros', ' pasha', ' bey', ' efendi']
        for t in titles:
            if clean.lower().endswith(t): 
                clean = clean[:-len(t)].strip().rstrip(',').rstrip('.')
                
        parts = clean.split()
        if len(parts) == 1: return "", clean
        if ' and ' in clean.lower(): return "", clean
        
        # Everything before the last word is the initial/first name
        return " ".join(parts[:-1]), parts[-1]

    # Extreme Edge Cases for algorithmic un-parsable names
    extreme_edge_cases = {
        "A. P. Kerameos": "A. Papadopoulos-Kerameus", "A. Papadopoulos Kerameus": "A. Papadopoulos-Kerameus",
        "Ath Papadopoulos Kerameus": "A. Papadopoulos-Kerameus", "Athanasios Papadopoulos-Kerameus": "A. Papadopoulos-Kerameus",
        "Α. Παπαδ. Κεραμέως": "A. Papadopoulos-Kerameus", "Α. Π. Κεραμέως": "A. Papadopoulos-Kerameus",
        "Αθ. Παπαδόπουλος Κεραμεύς": "A. Papadopoulos-Kerameus", "Α. Παπαδόπουλος Κεραμεύς": "A. Papadopoulos-Kerameus",
        "A. Zoiros Pasha": "A. Zoiros", "Α. Ζωηροῦ πασᾶ": "A. Zoiros",
        "᾿Αβδουλλὰχ βέης.": "Dr. Abdoullah Bey", "᾿Αβδουλλὰχ βέης": "Dr. Abdoullah Bey", "Dr. Abdoullah Bey.": "Dr. Abdoullah Bey",
        "Dr Abdoullah Bey": "Dr. Abdoullah Bey"
    }

    unique_authors = df['author_greek'].dropna().unique()
    registry = []
    
    for auth in unique_authors:
        if auth.lower() in ['anonymous', 'ανώνυμος', 'nan']: continue
        
        # 1. We transliterate FIRST to unify Greek and Latin entries
        eng_auth = universal_transliterate(auth)
        
        # 2. Parse out initials and surname from the unified English string
        init, sur = parse_name(eng_auth)
        
        # 3. Get the universal stem
        stem = get_universal_stem(sur)
        
        registry.append({
            'original_greek': auth,
            'english_full': eng_auth,
            'initials': init, 
            'surname': sur, 
            'stem_stripped': stem
        })

    clusters = {}
    for entry in registry:
        st = entry['stem_stripped']
        if st not in clusters: clusters[st] = []
        clusters[st].append(entry)

    canonical_map = {}
    resolution_log = []
    
    for st, entries in clusters.items():
        resolved_identities = []
        
        for entry in entries:
            matched = False
            for identity in resolved_identities:
                # Compare the English initials using the bidirectional subset checker
                if is_subset(entry['initials'], identity['initials']):
                    
                    if entry['initials'] != identity['initials']:
                        resolution_log.append(f"MERGE: [{entry['initials']}] -> [{identity['initials']}] in Surname Stem: {st.upper()} | (Original: '{entry['original_greek']}')")
                    
                    # Keep the longest/most complete initial
                    if len(entry['initials']) > len(identity['initials']):
                        identity['initials'] = entry['initials']
                        
                    # Favor the nominative case ending ('s') for the unified surname
                    if entry['surname'].endswith('s') and not identity['surname'].endswith('s'):
                        identity['surname'] = entry['surname']
                        
                    canonical_map[entry['original_greek']] = identity
                    matched = True
                    break
            
            if not matched:
                new_id = {'initials': entry['initials'], 'surname': entry['surname']}
                resolved_identities.append(new_id)
                canonical_map[entry['original_greek']] = new_id

    for idx, row in df.iterrows():
        gr = row['author_greek']
        if pd.isna(gr) or str(gr).strip().lower() in ['anonymous', 'ανώνυμος', 'none', 'nan', 'null']:
            df.at[idx, 'normalized_author'] = "Anonymous"
            continue
            
        gr_str = str(gr).strip()
        
        if gr_str in extreme_edge_cases:
            df.at[idx, 'normalized_author'] = extreme_edge_cases[gr_str]
            continue
            
        if gr_str in canonical_map:
            target = canonical_map[gr_str]
            df.at[idx, 'normalized_author'] = f"{target['initials']} {target['surname']}".strip()
        else:
            df.at[idx, 'normalized_author'] = universal_transliterate(gr_str)

    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    with open(report_txt, "w", encoding="utf-8") as f:
        f.write("=== SUBSET EXPANSION RESOLUTION REPORT ===\n")
        f.write(f"Total Expansions Applied: {len(resolution_log)}\n\n")
        for log in sorted(resolution_log):
            f.write(log + "\n")
            
    print(f"✅ Success! Deduplication saved to {output_csv}")

if __name__ == "__main__":
    standardize_dataset('philological_society_master.csv', 'philological_society_deduped.csv', 'resolution_report.txt')