import sys
import os
import pandas as pd
import json
import time
import requests

sys.path.append(os.getcwd())

from arxivscraper import Scraper

def get_paper_info(paper_ids):
    url = "https://api.semanticscholar.org/graph/v1/paper/batch"
    max_retries = 3
    fields = "paperId,title,abstract,year,venue,isOpenAccess,authors,references"
    for attempt in range(max_retries):
        response = requests.post(
            url,
            params={'fields': fields},
            json={"ids": paper_ids}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            wait_time = 2 ** attempt
            print(f"Rate limited. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"Failed with status code: {response.status_code}")
            return None
    return {"error": "Max retries exceeded"}

def scrape_ai(start_date, end_date, max_limit, categories):
    folder = "ARXIV"
    if not os.path.exists(folder):
        os.makedirs(folder)
    all_arxiv_ids = {}
    for category in categories:
        file_path = f'{folder}/arxiv_data_{category}_{start_date}_{end_date}.json'
        category_arxiv_ids = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                existing_data = json.load(file)
                for entry in existing_data:
                    entry['category'] = category
                    category_arxiv_ids[entry['id']] = category
        print(f"Initializing Scraper for category: {category}")
        scraper = Scraper(category=category, date_from=start_date, date_until=end_date, max_records=max_limit)
        print(f"Scraping data for category: {category}")
        output = scraper.scrape()
        cols = ('id', 'title', 'abstract', 'doi', 'created', 'url', 'category')
        df = pd.DataFrame(output, columns=cols)
        df['category'] = category
        new_entries = []
        for entry in output:
            if entry['id'] not in category_arxiv_ids:
                category_arxiv_ids[entry['id']] = category
                entry['category'] = category
                new_entries.append(entry)
        if new_entries:
            df = pd.DataFrame(new_entries, columns=cols)
            json_data = df.to_json(orient='records')
            formatted_json = json.loads(json_data)
            with open(file_path, 'w') as file:
                json.dump(formatted_json, file, indent=4)
        all_arxiv_ids[category] = category_arxiv_ids
    return all_arxiv_ids


def get_reference_details(paper_id):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,abstract,externalIds"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("title"), data.get("abstract"), data.get("externalIds")
        else:
            print(f"Failed to retrieve details for reference {paper_id}")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while retrieving details for reference {paper_id}: {str(e)}")
        return None, None, None

def fetch_paper_details(all_arxiv_ids, output_file):
    merged_data = {}
    encountered_ids = set()

    for category, arxiv_ids in all_arxiv_ids.items():
        for arxiv_id in arxiv_ids:
            if arxiv_id not in encountered_ids:
                response = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}?fields=paperId,title,abstract,references")
                if response.status_code == 200:
                    paper_data = response.json()
                    paper_id = paper_data.get("paperId")
                    if paper_id:
                        merged_data[paper_id] = {
                            "arxivId": arxiv_id,
                            "category": category,
                            "title": paper_data.get("title"),
                            "abstract": paper_data.get("abstract"),
                            "references": paper_data.get("references"),
                        }
                        encountered_ids.add(arxiv_id)

    for paper in merged_data.values():
        filtered_references = []
        references = paper.get("references", [])
        for reference in references:
            paper_id = reference.get("paperId")
            if paper_id and paper_id not in encountered_ids:
                title, abstract, external_ids = get_reference_details(paper_id)
                if external_ids and "ArXiv" in external_ids:
                    filtered_reference = {
                        "arxivId": external_ids["ArXiv"],
                        "title": title,
                        "abstract": abstract
                    }
                    filtered_references.append(filtered_reference)
                encountered_ids.add(paper_id)
        paper["references"] = filtered_references

    with open(output_file, 'w') as file:
        json.dump(list(merged_data.values()), file, indent=2)

    print(f"Paper details have been written to {output_file}.")

start_date = '2024-04-17'
end_date = '2024-04-17'
max_limit = 100
categories = ['q-fin']
output_file = 'ARXIV/merged_data_with_references.json'

all_arxiv_ids = scrape_ai(start_date, end_date, max_limit, categories)
fetch_paper_details(all_arxiv_ids, output_file) 