# Start here — publish the project in order

This is the short route from the ZIP file to a public GitHub repository, portfolio website, and interactive dashboard.

## Step 1 — Extract and review

1. Download `ai-document-intelligence-analytics.zip`.
2. Extract it into a folder on your computer.
3. Open `README.md` and `DEPLOYMENT_CHECKLIST.md`.
4. Keep the provided synthetic data. Do not add real employer, supplier, customer, or personal records.

## Step 2 — Create the GitHub repository

1. Sign in to GitHub and create a **public** repository named `ai-document-intelligence-analytics`.
2. Upload the contents of the extracted project folder (not the outer ZIP file).
3. Commit the files to the `main` branch.
4. Check that the repository page displays the README and the dashboard preview.

Expected repository URL:

`https://github.com/venkat5203/ai-document-intelligence-analytics`

If you use a different username or repository name, update the GitHub links in `index.html` and `README.md`.

## Step 3 — Publish the portfolio website and interactive dashboard

1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select branch `main` and folder `/ (root)`, then save.
4. Wait for the Pages URL to appear.
5. Open the portfolio homepage and click **Open interactive dashboard**.
6. In the dashboard, test category, region, and quality filters; search records; and use the CSV download button.

The website and browser dashboard are static files. They do not need an API key or a separate app server once GitHub Pages is enabled.

Expected URL pattern:

`https://venkat5203.github.io/ai-document-intelligence-analytics/`

Dashboard page:

`https://venkat5203.github.io/ai-document-intelligence-analytics/dashboard.html`

## Step 4 — Optional Python-backed dashboard

The repository also includes a fuller Streamlit dashboard at `dashboard/app.py`.

1. Open Streamlit Community Cloud and sign in with GitHub.
2. Create an app from this repository.
3. Set branch to `main` and main file path to `dashboard/app.py`.
4. Deploy and test the dashboard tabs.
5. Add the Streamlit URL to your LinkedIn Featured section if you decide to publish it.

The Streamlit app works without an API key. The live LLM extraction button is optional and requires an authorized private API key; API usage may incur charges.

## Step 5 — Add the project to LinkedIn

Use `PROJECT_CASE_STUDY.md` for the Projects section and `LINKEDIN_LAUNCH_POST.md` for a post announcing the project. Add these items to Featured:

1. GitHub repository.
2. Interactive dashboard URL (`.../dashboard.html`).
3. Portfolio homepage URL.

Make sure the description says the 47,000 records and dashboard results are **synthetic portfolio data**, not employer production results.

## Step 6 — Final quality check

Use `DEPLOYMENT_CHECKLIST.md`. Confirm all links work on desktop and mobile before sharing the profile publicly.
