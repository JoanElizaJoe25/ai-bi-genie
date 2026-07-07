"""
Chart Service.
Detects best chart type and formats data for frontend.
Bar = rankings, Line = time series, Pie = proportions.
"""


def detect_chart_type(columns: list, data: list, sql_query: str) -> str:
    if not data or not columns or len(data) < 2:
        return "none"

    sql_upper = sql_query.upper()

    time_keywords = ["TIMESTAMP", "DATE", "MONTH", "YEAR", "WEEK", "DAY", "QUARTER"]
    has_time_column = any(
        any(tk in col.upper() for tk in time_keywords)
        for col in columns
    )

    time_sql_patterns = ["DATE_TRUNC", "EXTRACT(", "FORMAT_DATE", "FORMAT_TIMESTAMP"]
    has_time_sql = any(p in sql_upper for p in time_sql_patterns)

    proportion_patterns = ["PERCENTAGE", "PERCENT", "SHARE", "RATIO", "PROPORTION"]
    has_proportion = any(p in sql_upper for p in proportion_patterns)

    numeric_cols = [
        col for col in columns
        if data[0].get(col) is not None and isinstance(data[0].get(col), (int, float))
    ]

    if numeric_cols:
        first_numeric = numeric_cols[0]
        values = [row.get(first_numeric, 0) for row in data if row.get(first_numeric) is not None]
        total = sum(values)
        if 98 <= total <= 102 or 0.98 <= total <= 1.02:
            has_proportion = True

    if has_time_column or has_time_sql:
        return "line"
    elif has_proportion and len(data) <= 10:
        return "pie"
    elif len(data) <= 15:
        return "bar"
    else:
        return "bar"


def format_chart_data(columns: list, data: list, chart_type: str) -> dict:
    if chart_type == "none" or not data or not columns:
        return {}

    label_col = None
    value_col = None

    for col in columns:
        sample = data[0].get(col)
        if sample is not None:
            if isinstance(sample, str) and label_col is None:
                label_col = col
            elif isinstance(sample, (int, float)) and value_col is None:
                value_col = col

    if label_col is None:
        label_col = columns[0]
    if value_col is None and len(columns) > 1:
        value_col = columns[1]
    if value_col is None:
        return {}

    labels = [str(row.get(label_col, "")) for row in data]
    values = [row.get(value_col, 0) for row in data]

    return {
        "labels": labels,
        "values": values,
        "label_column": label_col,
        "value_column": value_col,
        "series_name": value_col.replace("_", " ").title()
    }
