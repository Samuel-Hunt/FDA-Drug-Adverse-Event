import os
from dotenv import load_dotenv
from pathlib import Path
import time
import json
import requests

#access the API_key from 
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


#CONFIGURE API_KEY AND BASE_URL
API_KEY = os.getenv("OPENFDA_API_KEY")
BASE_URL = "https://api.fda.gov/drug/event.json?search=receivedate:[20230101+TO+20231231]"
#BASE_URL = "https://api.fda.gov/drug/event.json"


#TARGET PARAMERERS FOR EXTRACTION
SEARCH_QUERY = "recievedate:20230101"
BATCH_LIMIT = 100
TARGET_RECORDS = 1000
OUTPUT_DIR = "data/raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR,"raw_adverse_events_2023.jsonl" )

#setting up directories
os.makedirs(OUTPUT_DIR, exist_ok=True)





#BEGIN EXTRACTION DATA
def extract_openfda_events():
    skip = 0
    total_data_fetched = 0

    print(f"starting extraction for query: {SEARCH_QUERY}")
    print(f"attempting : {TARGET_RECORDS}")

    with open(OUTPUT_FILE, 'w', encoding = "utf-8") as out_file:
        while total_data_fetched < TARGET_RECORDS:
            params = {
                "api_key": API_KEY,
               # "search" : SEARCH_QUERY,
                "limit": BATCH_LIMIT,
                "skip": skip
            }
            try:
                response = requests.get(BASE_URL, params=params, timeout=10)

                if response.status_code == 429:
                    print("Rate limit reached. Wait 5 seconds...")
                    time.sleep(5)
                    continue
                if response.status_code != 200:
                    print(f"request failed with status {response.status_code}: {response.text}")
                    break

                payload = response.json()
                results = payload.get("results", [])

                if not results:
                    print("no more results returned from API.")
                    break

                for record in results:
                    out_file.write(json.dumps(record) + "\n")

                fetched_in_batch = len(results)
                total_data_fetched += fetched_in_batch
                skip += fetched_in_batch

                print(f"Fetched {total_data_fetched} out of {TARGET_RECORDS} records")

                if skip >= 25000:
                    print("Reached the limit for openFDA threshold for the skip slice")
                    break

                time.sleep(0.25)

            except requests.exceptions.RequestException as err:
                print(f"Network error: {err}")
                time.sleep(2)
    print(f"Extraction completed. {total_data_fetched} raw records saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_openfda_events()