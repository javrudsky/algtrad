# This is not the best way to manage database tables, but for now it is ok.
tables_config = [
        {
            "table_name": "daily_bar_history",
            "insert_sql":
            """
            CREATE TABLE IF NOT EXISTS daily_bar_history (
                id BIGINT PRIMARY KEY DEFAULT nextval('daily_bar_history_id_seq'),
                ticker TEXT NOT NULL,
                date BIGINT NOT NULL,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume BIGINT,
                UNIQUE (ticker, date)
            )
            """
            }
        ]
