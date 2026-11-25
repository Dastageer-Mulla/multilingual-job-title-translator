import pandas as pd
import json
import os
import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from google import genai
from tqdm import tqdm

# --- CONFIGURATION ---
# API_KEY = "AIzaSyA5E81858QrcDDCY3xeGY8IIxvO-mFMsvM"
# MODEL_ID = "gemma-3-27b-it"
INPUT_FILE = "WJ Category Resolving Test Data 320K.csv"
OUTPUT_FILE = "translated_jobtitles.csv"
CHECKPOINT_FILE = "translation_progress_log.csv"

# --- COLUMN SETTINGS ---
SOURCE_COLUMN = "searchterm"

# --- BATCHING & THREADING ---
BATCH_SIZE = 50  # Items per API call
MAX_WORKERS = 5  # Number of parallel threads (Adjust based on your API limits)
MAX_RETRIES = 5
ROWS_TO_PROCESS_LIMIT = 20000

client = genai.Client(api_key=API_KEY)
csv_lock = threading.Lock()


def get_pure_italian_prompt(titles):
    titles_str = "\n".join([f"- {t}" for t in titles])
    return f"""
### ROLE
Professional Italian HR Linguist.

### OBJECTIVE
Translate job titles to PURE Italian. NO English loanwords allowed.

### RULES
1. NO ENGLISH: "Project Manager" -> "Responsabile di progetto", "Developer" -> "Sviluppatore".
2. FORMAL: Use official Italian labor market terminology.
3. FORMAT: Return ONLY a JSON list of strings.

### INPUT:
{titles_str}

### JSON OUTPUT:
"""


def clean_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?', '', text)
        text = re.sub(r'```$', '', text)
    return text.strip()


def (batch_list):
    retry_delay = 5
    for attempt in rantranslate_batchge(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=get_pure_italian_prompt(batch_list),
                config={'temperature': 0.0}
            )

            clean_text = clean_json_response(response.text)
            translated = json.loads(clean_text)

            if isinstance(translated, list) and len(translated) == len(batch_list):
                return translated
            else:
                print(f"\n[Warning] Batch size mismatch. Retrying...")
        except Exception as e:
            time.sleep(retry_delay)
            retry_delay *= 2

    return ["ERROR"] * len(batch_list)


def process_and_save_batch(batch_data, pbar):
    """Worker function for threads"""
    batch_titles = batch_data[SOURCE_COLUMN].tolist()
    results = translate_batch(batch_titles)

    batch_df = pd.DataFrame({
        SOURCE_COLUMN: batch_titles,
        'italian_jobtitles': results
    })

    # Thread-safe writing to CSV
    with csv_lock:
        batch_df.to_csv(CHECKPOINT_FILE, mode='a', index=False, header=False)

    pbar.update(len(batch_data))


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    # Load data and normalize headers
    df = pd.read_csv(INPUT_FILE)
    df.columns = [c.lower().strip() for c in df.columns]

    # Handle Checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        processed_df = pd.read_csv(CHECKPOINT_FILE)
        start_idx = len(processed_df)
        print(f"Resuming from row {start_idx}...")
    else:
        start_idx = 0
        pd.DataFrame(columns=[SOURCE_COLUMN, 'italian_jobtitles']).to_csv(CHECKPOINT_FILE, index=False)

    # Define the range for this run (e.g., 20001 to 40000)
    end_idx = min(start_idx + ROWS_TO_PROCESS_LIMIT, len(df))
    rows_to_do = end_idx - start_idx

    if rows_to_do <= 0:
        print("All rows already processed or limit reached.")
        return

    print(f"Processing {rows_to_do} rows (From {start_idx} to {end_idx}) using {MAX_WORKERS} threads.")

    # Prepare batches
    batches = []
    for i in range(start_idx, end_idx, BATCH_SIZE):
        batches.append(df.iloc[i: min(i + BATCH_SIZE, end_idx)])

    # Threaded Execution
    with tqdm(total=rows_to_do, desc="Total Progress") as pbar:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Pass each batch to the executor
            futures = [executor.submit(process_and_save_batch, batch, pbar) for batch in batches]

            # Wait for all threads to finish
            for future in futures:
                future.result()

    # Final Save/Export
    final_df = pd.read_csv(CHECKPOINT_FILE)
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nDONE! {len(final_df)} rows now exist in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()