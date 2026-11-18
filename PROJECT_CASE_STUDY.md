# Project case study

## Document Intelligence & Data Quality Analytics

### Business problem

Semi-structured documents often contain important operational information in inconsistent layouts and field labels. Manual review can make it difficult to standardize fields, identify exceptions, and monitor quality trends consistently.

### Project goal

Build a reproducible demonstration that converts synthetic supplier-document text into structured records, validates the extracted fields, and makes quality patterns visible through an interactive dashboard.

### Architecture

`Synthetic document text → Python extraction → normalization → validation rules → review queue → SQL analysis → Streamlit dashboard`

An optional branch adds prompt-driven LLM extraction for comparison. The deterministic parser remains the default so the core project runs without an API key.

### Dataset

47,000 synthetic records across five document categories and five regions. The generator intentionally introduces missing values, malformed email strings, and common status-label variations so validation and exception reporting can be demonstrated.

### Method

1. Generate data with a reproducible random seed.
2. Extract supplier name, spend, status, email, last-updated date, document type, region, and reference.
3. Normalize approved status variants.
4. Apply six field-level checks.
5. Create a quality score and exception count per record.
6. Aggregate by date, category, region, and exception type.
7. Present the metrics and drill-down workflow in Streamlit.

### Results from the included synthetic run

| Measure | Result |
|---|---:|
| Records | 47,000 |
| Passed all six checks | 42,316 |
| Routed to review | 4,684 |
| Pass rate | 90.03% |
| Average quality score | 97.71% |

### What the dashboard demonstrates

- Overall validation and quality KPIs
- Document-volume trends by month
- Category-level record distribution
- Validation exception counts
- Searchable record-level extraction results
- Downloadable filtered records and exception queues
- A sample extraction lab with optional live LLM call

### Limitations

These are synthetic data results. The local parser is rule-based, and the optional LLM branch is a prototype. No production accuracy, cost saving, or processing-time improvement is claimed. A production-grade implementation would require a labeled benchmark set, confidence calibration, security controls, audit logging, monitoring, and human review.

### Skills demonstrated

Python, Pandas, SQL, data extraction, data cleaning, data validation, anomaly/exception analysis, KPI design, Streamlit, Plotly, prompt engineering, and responsible AI workflow design.
