"""
BigQuery Service.
Executes validated SQL queries and returns results.
"""

from google.cloud import bigquery
from app.config import GCP_PROJECT, MAX_BYTES_BILLED


def execute_query(sql_query: str) -> dict:
    try:
        client = bigquery.Client(project=GCP_PROJECT)

        job_config = bigquery.QueryJobConfig(
            maximum_bytes_billed=MAX_BYTES_BILLED
        )

        query_job = client.query(sql_query, job_config=job_config)
        results = query_job.result()

        rows = []
        columns = []

        for row in results:
            row_dict = dict(row)
            for key, value in row_dict.items():
                if hasattr(value, 'isoformat'):
                    row_dict[key] = value.isoformat()
            rows.append(row_dict)

        if query_job.schema:
            columns = [field.name for field in query_job.schema]
        elif rows:
            columns = list(rows[0].keys())

        return {
            "success": True,
            "data": rows,
            "row_count": len(rows),
            "columns": columns,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "columns": [],
            "error": str(e)
        }
