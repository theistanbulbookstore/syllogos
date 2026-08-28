import pandas as pd
from sentence_transformers import SentenceTransformer
import json

print("Loading database...")
df = pd.read_csv("philological_society_deduped_august28.csv").fillna("")

print("Loading Multilingual AI Model (paraphrase-multilingual-MiniLM-L12-v2)...")
# This model perfectly aligns Greek and English concepts in the same vector space
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

print("Preparing texts for embedding...")
# We explicitly label the English and Greek so the AI builds parallel meaning, 
# and use 'normalized_author' as it appears in the CSV header.
texts_to_embed = df.apply(
    lambda row: f"English Title: {row['title_english']} | Greek Title: {row['title_greek']} | Author: {row['normalized_author']} | Disciplines: {row['disciplines']} {row['primary_disciplines']}", 
    axis=1
).tolist()

print("Generating mathematical vector embeddings (this will take a minute or two)...")
embeddings = model.encode(texts_to_embed, show_progress_bar=True, normalize_embeddings=True)

print("Formatting and saving to corpus_embeddings.json...")
output_data = []
for idx, row in df.iterrows():
    # If normalized_author is empty, default to "Anonymous" to match the frontend logic
    author_name = row['normalized_author'] if row['normalized_author'] else "Anonymous"
    
    output_data.append({
        "id": idx,
        "title": row['title_english'] if row['title_english'] else row['title_greek'],
        "author": author_name,
        "year": row['volume_or_year_greek'],
        "type": row['entry_type'],
        "disciplines": row['primary_disciplines'],
        "embedding": [round(float(val), 5) for val in embeddings[idx]]
    })

with open("corpus_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f)

print("✅ Success! Multilingual corpus_embeddings.json is ready for the website.")