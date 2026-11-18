-- 1. Overall quality KPIs
SELECT
    COUNT(*) AS total_documents,
    SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) AS valid_documents,
    SUM(CASE WHEN is_valid = 0 THEN 1 ELSE 0 END) AS records_needing_review,
    ROUND(100.0 * AVG(CASE WHEN is_valid = 1 THEN 1.0 ELSE 0.0 END), 2) AS validation_pass_rate_pct,
    ROUND(AVG(quality_score), 2) AS average_quality_score_pct
FROM document_records;

-- 2. Volume and quality by month
SELECT
    substr(record_date, 1, 7) AS month,
    COUNT(*) AS document_count,
    ROUND(100.0 * AVG(CASE WHEN is_valid = 1 THEN 1.0 ELSE 0.0 END), 2) AS pass_rate_pct
FROM document_records
GROUP BY substr(record_date, 1, 7)
ORDER BY month;

-- 3. Document category comparison
SELECT
    category,
    COUNT(*) AS document_count,
    ROUND(AVG(quality_score), 2) AS average_quality_score,
    SUM(CASE WHEN is_valid = 0 THEN 1 ELSE 0 END) AS exception_count
FROM document_records
GROUP BY category
ORDER BY exception_count DESC;

-- 4. Operational review queue
SELECT doc_id, category, region, supplier_name, spend, status, email, quality_score, issue_count
FROM document_records
WHERE is_valid = 0
ORDER BY issue_count DESC, quality_score ASC
LIMIT 250;

-- 5. Spend profile by region
SELECT
    region,
    COUNT(spend) AS records_with_spend,
    ROUND(AVG(spend), 2) AS average_spend,
    ROUND(SUM(spend), 2) AS total_spend
FROM document_records
GROUP BY region
ORDER BY total_spend DESC;
