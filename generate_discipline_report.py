import pandas as pd

# Load the deduplicated dataset
df = pd.read_csv('philological_society_deduped.csv')

# Initialize an empty list to hold every individual discipline tag
all_disciplines = []

# Loop through the disciplines column
for d_str in df['disciplines'].dropna():
    # Ignore empty or N/A values
    if str(d_str).strip().lower() not in ['n/a', 'null', 'none', '']:
        # Split by comma for entries with multiple tags (e.g. "Medicine, History")
        for d in str(d_str).split(','):
            # Title case it (e.g. "medicine" -> "Medicine") to ensure exact matching
            all_disciplines.append(d.strip().title())

# Convert the master list to a pandas Series to count frequencies
disc_series = pd.Series(all_disciplines)
counts = disc_series.value_counts().reset_index()

# Rename the output columns for clarity
counts.columns = ['Discipline', 'Total_Entries']

# Save the final tally to a new CSV file
counts.to_csv('discipline_frequencies.csv', index=False, encoding='utf-8-sig')

print(f"✅ Successfully counted {len(counts)} unique disciplines.")
print("📄 Saved breakdown to 'discipline_frequencies.csv'")