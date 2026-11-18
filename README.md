# Document Intelligence & Data Quality Analytics

**A GitHub-ready, interactive portfolio project built with Python, SQL, Streamlit, Plotly, and an optional LLM extraction workflow.**

> **Data notice:** All 47,000 document records in this repository are synthetic. Company names, document identifiers, and contact domains are fictional examples. No employer, supplier, customer, or personal records are included.

## Live experience

- **Interactive browser dashboard:** `dashboard.html` (published automatically with the GitHub Pages portfolio).
- **Python-backed dashboard:** `dashboard/app.py` (optional Streamlit Community Cloud deployment).
- **Portfolio website:** Enable GitHub Pages for this repository; the same Pages site also hosts the interactive browser dashboard.
- **Source code:** `https://github.com/venkat5203/ai-document-intelligence-analytics`

The browser dashboard runs from GitHub Pages with no backend or API key. The Python-backed Streamlit dashboard runs locally or on Streamlit Community Cloud without an API key. An optional live LLM extraction action can be enabled using a private OpenAI API key; API calls may incur charges. The public demo does not call an external model unless the owner configures a key and a visitor explicitly runs the LLM action.

---

## 1. Project objective

Transform semi-structured supplier-document text into structured records, apply explainable data-quality checks, route exceptions for review, and visualize operational quality KPIs.

The project demonstrates a practical analytics workflow:

1. Generate or ingest synthetic document text.
2. Extract supplier, spend, status, email, date, category, region, and reference fields.
3. Normalize common label and status variations.
4. Validate extracted fields using explicit business rules.
5. Create a review queue for records that fail one or more checks.
6. Explore trends, category patterns, exception types, and record-level details in an interactive dashboard.
7. Optionally compare deterministic extraction with a prompt-driven LLM extraction call.

## 2. Dataset and current run results

The repository includes a reproducible dataset of **47,000 synthetic records**.

| Metric | Current generated result |
|---|---:|
| Documents generated | 47,000 |
| Records passing all six checks | 42,316 |
| Records routed for review | 4,684 |
| Validation pass rate | 90.03% |
| Average quality score | 97.71% |
| Document categories | 5 |
| Field-level validation checks | 6 |

These values are generated from the included synthetic dataset with seed `42`. They are **portfolio-demo results**, not work achievements or production outcomes from an employer. The issue categories can overlap because one record may fail multiple checks.

### Fields extracted

- Supplier / vendor name
- Spend amount
- Supplier status
- Contact email
- Last-updated date
- Document category
- Region
- Document reference

### Validation checks

1. Supplier name is present.
2. Spend is present.
3. Spend is greater than zero.
4. Status is one of `Active`, `Inactive`, or `Pending` after normalization.
5. Email follows a basic email-address format.
6. Last-updated date can be parsed.

A record passes only when all six checks pass. The quality score is the percentage of these checks passed by that record; it is not a model-confidence score.

## 3. Interactive dashboard features

Run `streamlit run dashboard/app.py` to open the Python-backed dashboard; `dashboard.html` is the static browser dashboard.

- **Browser dashboard (`dashboard.html`):** interactive category, region, and quality filters; charts; 900-row record sample search; CSV export; full-dataset KPI aggregates.
- **Python dashboard (`dashboard/app.py`):** volume trend, category mix, validation pass rate, records needing review, average quality score, spend distribution, and full record exploration.
- **Quality & Audit:** issue counts, rule-level failure rates, exception table, and CSV download.
- **Record Explorer:** search by document ID, supplier, email, or status; inspect original source text and extracted fields; export filtered records.
- **AI Extraction Lab:** test a document sample with the local parser; optionally call a configured LLM.
- **Methodology:** dataset assumptions, validation rules, limitations, and project artifacts.

## 4. Repository structure

```text
ai-document-intelligence-analytics/
├── dashboard/
│   └── app.py                       # Python-backed Streamlit dashboard
├── dashboard.html                  # Interactive browser dashboard for GitHub Pages
├── dashboard-static.css
├── dashboard-static.js
├── data/
│   ├── synthetic_documents.csv.gz   # 47K synthetic source records
│   ├── processed_documents.csv.gz  # Extracted and validated records
│   ├── quality_summary.csv          # Validation issue counts
│   ├── run_metrics.json             # Run-level KPI summary
│   └── generate_synthetic_data.py   # Reproducible data generator
├── src/
│   ├── pipeline.py                  # Extraction, normalization, QA checks
│   ├── llm_extractor.py              # Optional OpenAI Responses API call
│   └── run_pipeline.py               # End-to-end local pipeline runner
├── sql/
│   ├── schema.sql                    # SQLite-compatible analysis schema
│   └── analysis_queries.sql          # KPI and exception queries
├── tests/
│   └── test_pipeline.py              # Unit tests
├── assets/
│   ├── dashboard-preview.png         # Static dashboard preview image
│   └── dashboard-data.json           # Full aggregates + 900-row browser sample
├── index.html                        # Portfolio landing page (GitHub Pages)
├── styles.css
├── script.js                         # Project filters and dashboard URL
├── prompts_document_extraction.md    # Versioned extraction prompt
├── requirements.txt
├── requirements-dev.txt
├── PROJECT_CASE_STUDY.md
├── LINKEDIN_LAUNCH_POST.md
├── DEPLOYMENT_CHECKLIST.md
├── LICENSE
└── README.md
```

## 5. Run locally on Windows

### Prerequisites

- Python 3.10 or newer (Python 3.11 recommended).
- Git, or use GitHub's browser upload option.
- A modern browser.

### Setup

Open PowerShell in the project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### Start the interactive dashboard

```powershell
streamlit run dashboard/app.py
```

Streamlit will print a local address, usually `http://localhost:8501`. Open it in your browser. The Python dashboard reads the included compressed CSV. If that file is missing, the app generates the default 47,000-row dataset automatically. The browser dashboard reads `assets/dashboard-data.json`; it works after the repository is served through GitHub Pages or a local web server.

### Re-generate the dataset and run the pipeline

```powershell
python data/generate_synthetic_data.py --rows 47000 --seed 42
python -m src.run_pipeline
```

This creates or refreshes `processed_documents.csv.gz`, `quality_summary.csv`, and `run_metrics.json`.

### Load the processed records into SQLite

```powershell
python -m src.load_sqlite
```

This creates `data/document_analytics.db` locally (the database file is ignored by Git). Open it in a SQLite client and run the queries in `sql/analysis_queries.sql`.

### Run tests

```powershell
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## 6. Publish the code to GitHub

### Option A — Upload using the GitHub website

1. Sign in to GitHub and create a new **public** repository named `ai-document-intelligence-analytics`.
2. Do not initialize it with a second README if you plan to upload this repository's existing README.
3. Extract the ZIP file you downloaded.
4. Open the new GitHub repository and choose **Add file → Upload files**.
5. Drag the contents of the extracted project folder into the upload area (upload the files and folders, not the outer ZIP file).
6. Keep `.gitignore`, `README.md`, `requirements.txt`, and all project folders.
7. Commit the upload to the `main` branch.

### Option B — Git from PowerShell

From inside the extracted project folder:

```powershell
git init
git add .
git commit -m "Build document intelligence analytics portfolio project"
git branch -M main
git remote add origin https://github.com/venkat5203/ai-document-intelligence-analytics.git
git push -u origin main
```

If you created the repository under a different name or account, replace the remote URL with your own repository URL.

## 7. Deploy the Python-backed dashboard (optional)

The static interactive dashboard is already included as `dashboard.html` and is published with GitHub Pages in the next section. For the fuller Python-backed version, Streamlit Community Cloud can deploy the app from GitHub and provides a shareable `streamlit.app` URL.

1. Sign in to Streamlit Community Cloud using GitHub.
2. Choose **Create app**.
3. Select your repository: `venkat5203/ai-document-intelligence-analytics`.
4. Choose branch: `main`.
5. Set the app file path to `dashboard/app.py`.
6. Deploy and wait for the build to complete.
7. Open the generated public app URL and test every dashboard tab.
8. Copy the final `https://...streamlit.app` URL for your LinkedIn Featured section.

No API key is required for the standard dashboard. The optional live LLM extraction is disabled until a key is configured.

### Optional: enable live LLM extraction

1. Use an API key only when you are authorized to use the account and understand that API usage may be billed; obtain the account holder’s permission where needed.
2. For local use, copy `.env.example` to `.env` and enter the key there; the optional extractor loads `.env` locally. The `.env` file is excluded by `.gitignore`. You can also set the environment variable directly.
3. For Streamlit Community Cloud, open the app's settings and add the key under **Secrets**:

```toml
OPENAI_API_KEY = "your-private-key"
OPENAI_MODEL = "gpt-4.1-mini"
```

4. Reboot the app. The **Run live LLM extraction** button should become enabled.

Never paste API keys into source code, screenshots, README files, chat messages, or Git commits. The optional model call sends only the text sample submitted in the AI Extraction Lab to the configured provider. Do not enter confidential employer, customer, supplier, or personal data.

## 8. Publish the portfolio website with GitHub Pages

The root `index.html`, `styles.css`, `script.js`, `dashboard.html`, `dashboard-static.css`, `dashboard-static.js`, and `assets/` folder form a standalone static website with an interactive dashboard.

1. Push the repository to GitHub.
2. Open repository **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select branch `main` and folder `/ (root)`, then save.
5. Wait for GitHub Pages to publish the site. The Pages section will show the public website URL.
6. Open the URL on desktop and mobile to test the navigation, project filters, and links.

### Connect the Python dashboard (optional)

The portfolio website already links to `dashboard.html`, which runs entirely in the browser. If you also deploy Streamlit, add its URL to a visible link in `dashboard.html` or the portfolio page so visitors can open the fuller Python-backed version.

Also update the GitHub and LinkedIn URLs in `index.html` if your public profile URLs differ.

## 9. Suggested LinkedIn publishing copy

**Project title:** Document Intelligence & Data Quality Analytics | Python, SQL, Streamlit & AI-Ready Extraction

**Project description:**

Built an end-to-end analytics portfolio project using 47,000 synthetic supplier-document records. Developed a Python extraction and normalization pipeline, applied six field-level data-quality checks, created an exception review queue, and built interactive browser and Streamlit dashboards for trend analysis, record exploration, and KPI monitoring. Added a versioned LLM extraction prompt and an optional Responses API integration while keeping deterministic extraction available without an API key. The generated dataset achieved a 90.03% validation pass rate, with 4,684 records routed for review. All data and results are synthetic and intended for demonstration.

**Suggested tags:** Python · SQL · Data Analysis · Data Quality · Data Validation · Streamlit · Plotly · Generative AI · Prompt Engineering · Workflow Automation

## 10. Limitations and responsible use

- The data is fully synthetic and intended for portfolio demonstration only.
- The local parser uses transparent rules; it is not a trained machine-learning model.
- The optional LLM integration is an extraction prototype, not evidence of measured production accuracy.
- No extraction-accuracy or automation-time-reduction claim is made without a labeled test set and measured baseline.
- A production system would need security controls, access management, audit logging, robust schema validation, monitoring, and human review.
- Never upload private work documents or records to this public project.

## 11. Credits and technologies

Python · Pandas · NumPy · SQL (SQLite-compatible examples) · Streamlit · Plotly · OpenAI Responses API (optional) · HTML · CSS · JavaScript
