# AI Job Title Translator — English to Italian

A Python-based pipeline for translating English job titles into formal Italian job-market terminology using Google's Generative AI SDK.

The project processes job titles in batches, makes concurrent translation requests, saves progress to a checkpoint file, and supports resuming interrupted runs. It also contains an experimental English-to-Dutch translator and a script for analyzing the quality of the Italian translation dataset.

## Features

- Translates English job titles into Italian
- Uses formal Italian HR and labor-market terminology
- Processes titles in configurable batches
- Runs multiple translation requests concurrently
- Automatically retries failed API requests
- Saves progress continuously to a CSV checkpoint
- Resumes processing from the latest checkpoint
- Analyzes duplicates and detected languages in the translated dataset
- Includes an experimental English-to-Dutch translation script

## Project Structure

```text
AI_JobTitle_Translator_EN_To_IT/
├── JobTitleTranslatorENtoIT.py
├── JobTitleTranslatorENtoNL.py
├── Language_Similarity_Analysis.py
├── WJ Category Resolving Test Data 320K.csv
├── translated_jobtitles.csv
├── translation_progress_log.csv
├── translation_progress_log_nl.csv
└── Python_practice/
```

### Main files

| File | Description |
|---|---|
| `JobTitleTranslatorENtoIT.py` | Translates English job titles into Italian |
| `JobTitleTranslatorENtoNL.py` | Experimental English-to-Dutch translator |
| `Language_Similarity_Analysis.py` | Analyzes duplicates and language consistency |
| `WJ Category Resolving Test Data 320K.csv` | Source dataset containing job titles |
| `translation_progress_log.csv` | Italian translation checkpoint |
| `translated_jobtitles.csv` | Exported Italian translations |

## Requirements

- Python 3.10 or newer
- A Google Generative AI API key
- Access to the model configured in the translation script

Install the Python dependencies:

```bash
pip install pandas google-genai tqdm lingua-language-detector
```

## Input Format

The input CSV must contain a job-title column named `searchTerm`. Column names are normalized to lowercase by the translation script.

Example:

```csv
searchTerm,category
project engineer,Project Management
quality assurance manager,Manufacturing & Production
```

The default input file is:

```text
WJ Category Resolving Test Data 320K.csv
```

## Output Format

The Italian translator produces a CSV containing the original English title and its Italian translation:

```csv
searchterm,italian_jobtitles
project engineer,Ingegnere di progetto
quality assurance manager,Responsabile della garanzia della qualità
```

By default, the results are written to:

```text
translated_jobtitles.csv
```

Progress is saved separately in:

```text
translation_progress_log.csv
```

## Configuration

Translation settings are defined near the beginning of `JobTitleTranslatorENtoIT.py`:

```python
INPUT_FILE = "WJ Category Resolving Test Data 320K.csv"
OUTPUT_FILE = "translated_jobtitles.csv"
CHECKPOINT_FILE = "translation_progress_log.csv"

SOURCE_COLUMN = "searchterm"

BATCH_SIZE = 50
MAX_WORKERS = 5
MAX_RETRIES = 5
ROWS_TO_PROCESS_LIMIT = 20000
```

Adjust these values according to the size of the dataset and the API rate limits available to you.

Do not commit API keys to the repository. Store credentials in an environment variable or a local configuration file excluded by `.gitignore`.

Example environment variable:

### Windows PowerShell

```powershell
$env:GOOGLE_API_KEY="your-api-key"
```

### Linux or macOS

```bash
export GOOGLE_API_KEY="your-api-key"
```

The Python code must then read the value securely:

```python
API_KEY = os.environ["GOOGLE_API_KEY"]
```

## Running the Italian Translator

After configuring the API key and model, run:

```bash
python JobTitleTranslatorENtoIT.py
```

The script:

1. Loads the input CSV.
2. Checks the existing checkpoint.
3. Skips rows recorded as already processed.
4. Splits the remaining rows into batches.
5. Translates batches concurrently.
6. Appends results to the checkpoint.
7. Exports the completed checkpoint to the output CSV.

## Running the Data Quality Analysis

To analyze the generated Italian dataset, run:

```bash
python Language_Similarity_Analysis.py
```

The report includes:

- Total row count
- Exact duplicate rows
- Repeated English job titles
- Repeated Italian translations
- Number of unique translation pairs
- Same-language pairs
- Different-language pairs
- Ambiguous language detections

The analysis script expects these columns:

```text
searchterm
italian_jobtitles
```

## Checkpoint and Resume Behavior

The translator uses the number of rows already present in the checkpoint as its resume position.

If processing stops unexpectedly, running the script again continues from the recorded row count. To start again from the beginning, back up and remove the checkpoint file before launching the translator.

Because translation batches run concurrently, their completion order may differ from the original input order.

## Current Development Status

This repository is an experimental data-processing project. The scripts should be reviewed and configured before execution.

Known items requiring attention include:

- The Italian translator contains incomplete API configuration and a malformed translation function definition.
- The Dutch translator calls a prompt function whose name does not match the implemented function.
- API credentials must be removed from source code before the repository is published.
- Concurrent batches may be written in completion order instead of input order.
- Checkpoint resumption is based on row count rather than a stable record identifier.

## Recommended `.gitignore`

The following files and directories should normally not be committed:

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/

# IDE
.idea/
.vscode/

# Environment variables and secrets
.env
.env.*
*.key

# Generated translation files
translation_progress_log*.csv
translated_jobtitles*.csv

# Local datasets
WJ Category Resolving Test Data 320K.csv
```

Only exclude the dataset and generated CSV files if they are not intentionally part of the public repository.

## Data and Privacy

Make sure you have permission to publish and process the source dataset. Review it for personal, confidential, licensed, or proprietary information before uploading it to GitHub.

Large CSV files may also exceed GitHub's normal file-size limits. Consider Git Large File Storage or an external dataset-hosting service when publishing large data files.

## Security

Never commit API keys or other credentials. If a credential has previously been stored in source code, revoke it before publishing the repository—even if it is later removed from the latest commit.

## License

No license has been selected yet. Add a `LICENSE` file before distributing or accepting contributions to clarify how others may use the project.
