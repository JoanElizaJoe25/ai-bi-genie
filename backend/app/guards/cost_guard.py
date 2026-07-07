"""
Cost Guard.
Dry-run on BigQuery to check query cost before executing.
"""

from google.cloud import bigquery
from app.config import GCP_PROJECT, MAX_BYTES_BILLED


def check_query_cost(sql_query: str) -> dict:
    try:
        client = bigquery.Client(project=GCP_PROJECT)

        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False
        )

        query_job = client.query(sql_query, job_config=job_config)

        estimated_bytes = query_job.total_bytes_processed or 0
        estimated_mb = estimated_bytes / (1024 * 1024)
        limit_mb = MAX_BYTES_BILLED / (1024 * 1024)

        # Allow if estimated bytes is 0 (cached/free) or within limit
        is_ok = (estimated_bytes == 0) or (estimated_bytes <= MAX_BYTES_BILLED)

        return {
            "is_within_limit": is_ok,
            "estimated_bytes": estimated_bytes,
            "estimated_mb": round(estimated_mb, 2),
            "limit_mb": round(limit_mb, 2)
        }

    except Exception as e:
        return {
            "is_within_limit": False,
            "estimated_bytes": 0,
            "estimated_mb": 0,
            "limit_mb": round(MAX_BYTES_BILLED / (1024 * 1024), 2),
            "error": str(e)
        }

