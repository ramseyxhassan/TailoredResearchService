from __future__ import print_function
import xml.etree.ElementTree as ET
import datetime
import time
import sys
from typing import Dict, List

PYTHON3 = sys.version_info[0] == 3
if PYTHON3:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError
else:
    from urllib import urlencode
    from urllib2 import HTTPError, urlopen

from constants import OAI, ARXIV, BASE


class Record(object):
    def __init__(self, xml_record):
        self.xml = xml_record
        self.id = self._get_text(ARXIV, "id")
        self.url = "https://arxiv.org/abs/" + self.id
        self.title = self._get_text(ARXIV, "title")
        self.abstract = self._get_text(ARXIV, "abstract")
        self.cats = self._get_text(ARXIV, "categories")
        self.created = self._get_text(ARXIV, "created")
        self.updated = self._get_text(ARXIV, "updated")
        self.doi = self._get_text(ARXIV, "doi")
        self.authors = self._get_authors()
        self.affiliation = self._get_affiliation()

    def _get_text(self, namespace: str, tag: str) -> str:
        try:
            return (
                self.xml.find(namespace + tag).text.strip().lower().replace("\n", " ")
            )
        except:
            return ""

    def _get_name(self, parent, attribute) -> str:
        try:
            return parent.find(ARXIV + attribute).text.lower()
        except:
            return "n/a"

    def _get_authors(self) -> List:
        authors_xml = self.xml.findall(ARXIV + "authors/" + ARXIV + "author")
        last_names = [self._get_name(author, "keyname") for author in authors_xml]
        first_names = [self._get_name(author, "forenames") for author in authors_xml]
        full_names = [a + " " + b for a, b in zip(first_names, last_names)]
        return full_names

    def _get_affiliation(self) -> str:
        authors = self.xml.findall(ARXIV + "authors/" + ARXIV + "author")
        try:
            affiliation = [
                author.find(ARXIV + "affiliation").text.lower() for author in authors
            ]
            return affiliation
        except:
            return []

    def output(self) -> Dict:
        return {
            "title": self.title,
            "id": self.id,
            "abstract": self.abstract,
            "categories": self.cats,
            "doi": self.doi,
            "created": self.created,
            "updated": self.updated,
            "authors": self.authors,
            "affiliation": self.affiliation,
            "url": self.url,
        }


class Scraper(object):
    def __init__(
        self,
        category: str,
        date_from: str = None,
        date_until: str = None,
        t: int = 30,
        timeout: int = 300,
        filters: Dict[str, str] = {},
        max_records: int = 1000,
    ):
        self.cat = str(category)
        self.t = t
        self.timeout = timeout
        self.max_records = max_records
        DateToday = datetime.date.today()
        self.f = str(DateToday.replace(day=1)) if date_from is None else date_from
        self.u = str(DateToday) if date_until is None else date_until
        self.url = (
            BASE
            + "from="
            + self.f
            + "&until="
            + self.u
            + "&metadataPrefix=arXiv&set=%s" % self.cat
        )
        self.filters = filters
        self.append_all = not filters
        self.keys = filters.keys() if filters else []

    def scrape(self) -> List[Dict]:
        t0 = time.time()
        url = self.url
        ds = []
        while len(ds) < self.max_records:
            try:
                response = urlopen(url)
                xml = response.read()
                root = ET.fromstring(xml)
                records = root.findall(OAI + "ListRecords/" + OAI + "record")
                for record in records:
                    if len(ds) >= self.max_records:
                        break
                    meta = record.find(OAI + "metadata").find(ARXIV + "arXiv")
                    rec = Record(meta).output()
                    if self.append_all or any(
                        word.lower() in rec[key]
                        for key in self.keys
                        for word in self.filters[key]
                    ):
                        ds.append(rec)

                token = root.find(OAI + "ListRecords").find(OAI + "resumptionToken")
                if not token or not token.text or len(ds) >= self.max_records:
                    break
                url = BASE + "resumptionToken=%s" % token.text
            except HTTPError as e:
                if e.code == 503:
                    time.sleep(int(e.hdrs.get("retry-after", 30)))
                else:
                    raise
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        t1 = time.time()
        print(f"Fetching is completed in {t1 - t0:.1f} seconds.")
        print(f"Total number of records: {len(ds)}")
        return ds

def search_all(df, col, *words):
    import numpy as np

    return df[np.logical_and.reduce([df[col].str.contains(word) for word in words])]