from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.llm_extractor import live_llm_extract  # noqa: E402
from src.pipeline import extract_fields, issue_summary, process_records  # noqa: E402
from data.generate_synthetic_data import generate  # noqa: E402

DATA_PATH = ROOT / "data" / "synthetic_documents.csv.gz"

st.set_page_config(
    page_title="Document Intelligence | Data Quality Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
:root { --ink:#e8eef7; --muted:#9aa9bc; --panel:#111c2c; --line:#24344a; --accent:#63e6be; }
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at 80% 0%, #18304a 0%, #0b1220 42%, #0b1220 100%); }
[data-testid="stSidebar"] { background: #0e1928; border-right: 1px solid #23354b; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1480px; }
.hero { padding: 1.35rem 1.55rem; border: 1px solid #263b53; border-radius: 18px; background: linear-gradient(125deg, rgba(28,54,79,.95), rgba(16,29,45,.94)); margin-bottom: 1.2rem; }
.eyebrow { color:#63e6be; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; }
.hero h1 { color:#f3f7fc; font-size:2.15rem; line-height:1.12; margin:.45rem 0 .5rem; }
.hero p { color:#b5c4d7; margin:0; max-width:880px; }
.kpi { border:1px solid #263b53; border-radius:15px; padding:1rem 1.05rem; background:linear-gradient(145deg,rgba(24,39,59,.98),rgba(16,27,43,.98)); min-height:118px; }
.kpi-label { color:#9fb0c5; font-size:.76rem; text-transform:uppercase; letter-spacing:.1em; font-weight:700; }
.kpi-value { color:#f4f8fc; font-size:1.85rem; font-weight:750; margin-top:.25rem; }
.kpi-note { color:#8fa2b9; font-size:.76rem; margin-top:.15rem; }
.section-title { color:#eaf2fa; font-size:1.12rem; font-weight:700; margin:.5rem 0 .15rem; }
.small-note { color:#95a8bd; font-size:.82rem; }
div[data-testid="stMetric"] { background:#142338; border:1px solid #293e58; padding:14px 16px; border-radius:13px; }
.stButton>button { border-radius:10px; border:1px solid #3d806f; }
[data-testid="stDataFrame"] { border:1px solid #263b53; border-radius:12px; overflow:hidden; }
.warning-note { border-left:3px solid #f0b35b; padding:.65rem .85rem; background:rgba(240,179,91,.08); color:#e7d7bc; border-radius:6px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner="Loading and validating synthetic documents...")
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        generate(rows=47_000, output=DATA_PATH)
    raw = pd.read_csv(DATA_PATH, compression="infer")
    return process_records(raw)


def plot_layout(fig, height: int = 320):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=12, r=12, t=42, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd7e6", family="Inter, Arial, sans-serif"),
        legend=dict(orientation="h", y=1.12, x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(140,165,190,.13)", zeroline=False)
    return fig


def apply_filters(frame: pd.DataFrame) -> pd.DataFrame:
    filtered = frame.copy()
    st.sidebar.markdown("### Explore the dataset")
    categories = sorted(filtered["category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect("Document category", categories, default=categories)
    regions = sorted(filtered["region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
    quality = st.sidebar.selectbox("Record quality", ["All records", "Valid only", "Needs review"])
    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]
    if selected_regions:
        filtered = filtered[filtered["region"].isin(selected_regions)]
    if quality == "Valid only":
        filtered = filtered[filtered["is_valid"]]
    elif quality == "Needs review":
        filtered = filtered[~filtered["is_valid"]]
    st.sidebar.caption(f"Showing {len(filtered):,} of {len(frame):,} records")
    return filtered


def render_overview(frame: pd.DataFrame) -> None:
    total = len(frame)
    valid = int(frame["is_valid"].sum())
    exceptions = total - valid
    valid_rate = valid / total * 100 if total else 0
    completeness = frame["quality_score"].mean() if total else 0
    avg_spend = frame["spend"].mean(skipna=True) if total else 0

    st.markdown(
        '<div class="hero"><div class="eyebrow">Portfolio project · synthetic data demo</div>'
        '<h1>Document Intelligence &amp; Data Quality Analytics</h1>'
        '<p>Transform semi-structured supplier documents into validated records, surface quality exceptions, and monitor operational KPIs with Python, SQL concepts, and an optional LLM extraction workflow.</p></div>',
        unsafe_allow_html=True,
    )
    if not total:
        st.info("No records match the selected filters. Adjust the filters in the sidebar.")
        return

    cols = st.columns(4)
    with cols[0]: metric_card("Documents in view", f"{total:,}", "Synthetic document records")
    with cols[1]: metric_card("Validation pass rate", f"{valid_rate:.1f}%", "All six QA rules passed")
    with cols[2]: metric_card("Records to review", f"{exceptions:,}", "One or more QA checks failed")
    with cols[3]: metric_card("Avg. quality score", f"{completeness:.1f}%", "Six field-level checks")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="section-title">Document volume over time</div>', unsafe_allow_html=True)
        trend = frame.dropna(subset=["record_date"]).groupby(frame["record_date"].dt.to_period("M").astype(str)).size().reset_index(name="documents")
        trend.columns = ["month", "documents"]
        fig = px.area(trend, x="month", y="documents", markers=True, color_discrete_sequence=["#63e6be"])
        fig.update_traces(line=dict(width=2.5), fillcolor="rgba(99,230,190,.13)")
        st.plotly_chart(plot_layout(fig, 330), use_container_width=True)
    with right:
        st.markdown('<div class="section-title">Records by document category</div>', unsafe_allow_html=True)
        category_counts = frame["category"].value_counts().rename_axis("category").reset_index(name="records")
        fig = px.bar(category_counts, x="records", y="category", orientation="h", color="records", color_continuous_scale=["#24445d", "#63e6be"])
        fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(plot_layout(fig, 330), use_container_width=True)

    left2, right2 = st.columns([1, 1])
    with left2:
        st.markdown('<div class="section-title">Quality status</div>', unsafe_allow_html=True)
        status_frame = pd.DataFrame({"status": ["Passed all checks", "Needs review"], "records": [valid, exceptions]})
        fig = px.pie(status_frame, names="status", values="records", hole=.68, color="status", color_discrete_map={"Passed all checks": "#63e6be", "Needs review": "#f0b35b"})
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(plot_layout(fig, 300), use_container_width=True)
    with right2:
        st.markdown('<div class="section-title">Spend distribution (INR)</div>', unsafe_allow_html=True)
        spend_frame = frame.dropna(subset=["spend"])
        fig = px.histogram(spend_frame, x="spend", nbins=32, color_discrete_sequence=["#8daeff"])
        fig.update_xaxes(title="Extracted spend (INR)", tickformat="~s")
        fig.update_yaxes(title="Documents")
        st.plotly_chart(plot_layout(fig, 300), use_container_width=True)

    st.markdown('<div class="small-note">Average extracted spend: ' + (f"₹{avg_spend:,.0f}" if pd.notna(avg_spend) else "Not available") + ' · All figures are generated from synthetic sample records.</div>', unsafe_allow_html=True)


def render_quality(frame: pd.DataFrame) -> None:
    st.markdown("## Data quality & audit workspace")
    st.caption("Each document is evaluated against six transparent validation rules. Issue counts can overlap when one record fails multiple checks.")
    summary = issue_summary(frame)
    left, right = st.columns([1.2, 1])
    with left:
        issue_df = summary.rename_axis("issue").reset_index(name="records")
        fig = px.bar(issue_df.sort_values("records"), x="records", y="issue", orientation="h", color="records", color_continuous_scale=["#314b66", "#ffb86b"])
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(plot_layout(fig, 360), use_container_width=True)
    with right:
        st.markdown("### Rule-level results")
        table = pd.DataFrame({"Validation rule": summary.index, "Failed records": summary.values})
        table["Failure rate"] = (table["Failed records"] / max(len(frame), 1) * 100).round(2).astype(str) + "%"
        st.dataframe(table, hide_index=True, use_container_width=True, height=330)
    st.markdown("### Records requiring review")
    cols = ["doc_id", "category", "region", "supplier_name", "spend", "status", "email", "quality_score", "issue_count"]
    exceptions = frame.loc[~frame["is_valid"], cols].sort_values(["issue_count", "quality_score"], ascending=[False, True])
    st.dataframe(exceptions.head(250), hide_index=True, use_container_width=True, height=360)
    st.download_button("Download exception queue (CSV)", exceptions.to_csv(index=False).encode("utf-8"), "data_quality_exceptions.csv", "text/csv")


def render_explorer(frame: pd.DataFrame) -> None:
    st.markdown("## Record explorer")
    query = st.text_input("Search supplier, document ID, email, or extracted status", placeholder="Try DOC-000120 or Northstar")
    view = frame.copy()
    if query.strip():
        q = query.strip().lower()
        searchable = view[["doc_id", "supplier_name", "email", "status"]].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
        view = view[searchable.str.contains(q, regex=False)]
    columns = ["doc_id", "record_date", "category", "region", "supplier_name", "spend", "status", "email", "quality_score", "is_valid"]
    st.caption(f"{len(view):,} matching records. Showing up to 500 rows in the table.")
    st.dataframe(view[columns].head(500), hide_index=True, use_container_width=True, height=430)
    st.download_button("Download current filtered records (CSV)", view[columns].to_csv(index=False).encode("utf-8"), "filtered_document_records.csv", "text/csv")

    if len(view):
        selected_id = st.selectbox("Inspect source document", view["doc_id"].head(500).tolist())
        selected = view.loc[view["doc_id"] == selected_id].iloc[0]
        with st.expander("View original unstructured document text"):
            st.code(selected["raw_text"], language="text")
        with st.expander("View extracted fields and QA flags"):
            details = {key: selected[key] for key in ["supplier_name", "spend", "status", "email", "last_updated", "document_type", "region", "reference", "quality_score", "issue_count", "is_valid"]}
            st.json(details)


def render_ai_lab(frame: pd.DataFrame) -> None:
    st.markdown("## AI extraction lab")
    st.caption("Try extracting fields from a sample document. Rule-based extraction runs locally; live LLM extraction is optional and requires your own private API key.")
    default_text = frame.iloc[0]["raw_text"] if len(frame) else "Supplier Name: Northstar Systems\nAnnual Spend: INR 125,000.00\nSupplier Status: Active\nContact Email: accounts@northstar.example\nLast Updated: 2026-10-01\nDocument Type: Invoice\nRegion: South\nReference: DEMO-0001"
    raw_text = st.text_area("Sample document text", value=default_text, height=220)
    left, right = st.columns(2)
    with left:
        if st.button("Run local extraction", type="primary", use_container_width=True):
            st.session_state["local_extract_result"] = extract_fields(raw_text)
    with right:
        llm_enabled = bool(os.getenv("OPENAI_API_KEY", "").strip())
        try:
            if not llm_enabled and "OPENAI_API_KEY" in st.secrets:
                os.environ["OPENAI_API_KEY"] = str(st.secrets["OPENAI_API_KEY"])
                llm_enabled = True
        except Exception:
            pass
        if st.button("Run live LLM extraction", disabled=not llm_enabled, use_container_width=True):
            try:
                with st.spinner("Calling the configured model..."):
                    st.session_state["llm_extract_result"] = live_llm_extract(raw_text)
                st.success("Live model extraction completed.")
            except Exception as exc:
                st.error(f"LLM extraction failed: {exc}")
    if not llm_enabled:
        st.markdown('<div class="warning-note">Live LLM extraction is disabled because no API key is configured. The local extraction demo works without one.</div>', unsafe_allow_html=True)
    if "local_extract_result" in st.session_state:
        st.markdown("### Local extraction result")
        st.json(st.session_state["local_extract_result"])
    if "llm_extract_result" in st.session_state:
        st.markdown("### Live LLM result")
        st.json(st.session_state["llm_extract_result"])
    st.markdown("### Workflow design")
    st.code("Unstructured text → extraction prompt / parser → structured JSON → Python cleaning → business-rule validation → SQL analytics → Power BI dashboard", language="text")
    st.caption("Human review remains important for missing, malformed, ambiguous, or low-confidence values. Do not submit confidential employer, customer, or personal data to this public demo.")


def render_methodology(frame: pd.DataFrame) -> None:
    st.markdown("## Methodology, assumptions & limitations")
    st.markdown("""
    **Dataset:** 47,000 synthetic supplier-document records generated with a fixed random seed. Company names, document IDs, and contact domains are fictional examples.

    **Extraction:** A deterministic Python parser supports common field-label variations for supplier name, spend, status, contact email, last-updated date, document category, region, and reference.

    **Validation:** Six checks evaluate supplier-name presence, spend presence, positive spend, valid status, email format, and date validity. A record is marked valid only when all six checks pass.

    **AI component:** A versioned extraction prompt is included. An optional OpenAI Responses API integration can be enabled with a private API key. The default public demo does not require external AI calls.

    **Important limitation:** This is a portfolio demonstration, not a production procurement system. Synthetic data and rule-based checks do not establish real-world model accuracy or business impact. LLM outputs require evaluation against labeled examples and human review.
    """)
    st.markdown("### Six validation checks")
    st.dataframe(pd.DataFrame({"Rule": ["Supplier name present", "Spend present", "Spend greater than zero", "Status in approved values", "Email has valid format", "Last-updated date is parseable"], "Purpose": ["Required identity field", "Required numeric field", "Positive amount check", "Normalize business status", "Basic syntax validation", "Date parsing and consistency"]}), hide_index=True, use_container_width=True)
    st.markdown("### Project artifacts")
    st.write("The repository includes the synthetic data generator, reusable Python extraction pipeline, SQL schema and queries, unit tests, prompt template, portfolio page, and deployment guide.")


try:
    data = load_data()
except Exception as exc:
    st.error(f"Could not load the demo dataset: {exc}")
    st.stop()

st.sidebar.markdown("## DOCUMENT INTELLIGENCE")
st.sidebar.caption("DATA QUALITY ANALYTICS · PORTFOLIO DEMO")
page = st.sidebar.radio("Navigation", ["Overview", "Quality & Audit", "Record Explorer", "AI Extraction Lab", "Methodology"])
filtered = apply_filters(data) if page != "AI Extraction Lab" else data
st.sidebar.divider()
st.sidebar.caption("47,000 synthetic records · No employer data")
st.sidebar.markdown("[View source code ↗](https://github.com/venkat5203/ai-document-intelligence-analytics)")

if page == "Overview":
    render_overview(filtered)
elif page == "Quality & Audit":
    render_quality(filtered)
elif page == "Record Explorer":
    render_explorer(filtered)
elif page == "AI Extraction Lab":
    render_ai_lab(data)
else:
    render_methodology(data)
