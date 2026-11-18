# Go-live checklist

## Before GitHub upload
- [ ] Confirm the repository name and GitHub username.
- [ ] Check that `.env` and `.streamlit/secrets.toml` are not included.
- [ ] Keep only synthetic records in `data/`.
- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Run `streamlit run dashboard/app.py` and test all five pages.

## GitHub
- [ ] Create a public repository named `ai-document-intelligence-analytics`.
- [ ] Upload/push all project files to `main`.
- [ ] Confirm README, project structure, data notice, and dashboard preview render correctly.

## Streamlit Community Cloud
- [ ] Create app from the repository.
- [ ] Set branch to `main`.
- [ ] Set main file path to `dashboard/app.py`.
- [ ] Deploy and test Overview, Quality & Audit, Record Explorer, AI Extraction Lab, and Methodology.
- [ ] Copy the public `streamlit.app` URL.
- [ ] Leave the API key unconfigured unless live LLM testing is explicitly needed.

## GitHub Pages
- [ ] Settings → Pages → Deploy from a branch → `main` → `/ (root)`.
- [ ] Save and wait until the Pages URL appears.
- [ ] Replace `DASHBOARD_URL` inside `script.js` with the real Streamlit URL.
- [ ] Verify GitHub, LinkedIn, and project links in `index.html`.
- [ ] Open the `dashboard.html` page and test category, region, quality, search, chart updates, and CSV export.
- [ ] Test the portfolio page on phone and desktop.

## LinkedIn
- [ ] Add repository URL to Featured.
- [ ] Add public Streamlit dashboard URL to Featured.
- [ ] Add portfolio website URL to Featured.
- [ ] Add this project to the Projects section using measured synthetic-data results.
- [ ] Clearly label the dataset as synthetic.
