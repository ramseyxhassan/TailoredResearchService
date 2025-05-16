import json
import csv
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('stsb-roberta-large')

input_file_path = 'ARXIV/combined_data.json'
with open(input_file_path, 'r') as file:
    data = json.load(file)

output_file_path = 'ARXIV/similarity_scores.csv'
with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['arxivId', 'referenceId', 'similarityScore'])

    for item in data:
        arxiv_id = item['arxivId']
        abstract = item['abstract']
        references = item.get('references', [])

        if references:
            source_embedding = model.encode(abstract, convert_to_tensor=True)

            for ref in references:
                ref_id = ref['arxivId']
                ref_abstract = ref['abstract']
                if ref_abstract:
                    ref_embedding = model.encode(ref_abstract, convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(source_embedding, ref_embedding).item()
                    writer.writerow([arxiv_id, ref_id, similarity])

print(f"Similarity scores saved to {output_file_path}")
