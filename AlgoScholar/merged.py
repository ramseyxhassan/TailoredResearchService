import json
import os
from collections import defaultdict

files = {
    "cs": "ARXIV/combined_references_cs.json",
    "econ": "ARXIV/combined_references_econ.json",
    "q-fin": "ARXIV/combined_references_q-fin.json"
}

def load_data(path):
    with open(path, 'r') as file:
        return json.load(file)

combined_data = {}

for category, path in files.items():
    data = load_data(path)
    for entry in data:
        arxiv_id = entry['arxivId']
        if arxiv_id not in combined_data:
            entry['category'] = {category}
            if 'source_file' in entry:
                del entry['source_file']
            if 'references' in entry:
                entry['references'] = [ref for ref in entry['references'] if ref.get('abstract')]
            combined_data[arxiv_id] = entry
        else:
             combined_data[arxiv_id]['category'].add(category)

combined_data = {id: entry for id, entry in combined_data.items() if entry['abstract'] is not None}

for entry in combined_data.values():
    entry['category'] = ', '.join(sorted(entry['category']))

final_data = list(combined_data.values())

output_path = "ARXIV/combined_data.json"
with open(output_path, 'w') as outfile:
    json.dump(final_data, outfile, indent=4)

print(f"Combined data written to {output_path}")
