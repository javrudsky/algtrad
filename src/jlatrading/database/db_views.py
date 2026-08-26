views_config = [
        {
            "view_name": "daily_bar_summary_v",
            "create_sql":
            """
            CREATE VIEW IF NOT EXISTS daily_bar_summary_v AS
                SELECT
                strftime(to_timestamp(min(date)) AT TIME ZONE 'UTC-3', '%d-%m-%Y') AS start_date,
                strftime(to_timestamp(max(date)) AT TIME ZONE 'UTC-3', '%d-%m-%Y') AS end_date,
                COUNT(*) AS total_rows,
                FROM daily_bar_history
            """
            },
        ]
