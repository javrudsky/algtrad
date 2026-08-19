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
            },
        {
            "table_name": "instruments_prices",
            "insert_sql":
            """
            CREATE TABLE IF NOT EXISTS instruments_prices (
                id BIGINT PRIMARY KEY DEFAULT nextval('instruments_prices_id_seq'),
                symbol TEXT NOT NULL,
                bid_quantity BIGINT,
                bid_price DOUBLE PRECISION,
                ask_price DOUBLE PRECISION,
                ask_quantity BIGINT,
                close_price DOUBLE PRECISION,
                percent_change DOUBLE PRECISION,
                open_price DOUBLE PRECISION,
                high_price DOUBLE PRECISION,
                low_price DOUBLE PRECISION,
                previous_close DOUBLE PRECISION,
                volume BIGINT,
                operations_count BIGINT,
                timestamp TEXT,
                option_type TEXT,
                strike_price DOUBLE PRECISION,
                expiration_date TEXT,
                market TEXT,
                currency TEXT,
                description TEXT,
                settlement_term TEXT,
                minimum_lot_size BIGINT,
                lot_size BIGINT,
                download_timestamp BIGINT DEFAULT EPOCH(NOW()),
                UNIQUE (symbol, timestamp, settlement_term)
                )
                """
            },
        {
            "table_name": "selected_tickers",
            "insert_sql":
            """
            CREATE TABLE IF NOT EXISTS selected_tickers (
                id BIGINT PRIMARY KEY DEFAULT nextval('selected_tickers_id_seq'),
                ticker_list TEXT NOT NULL,
                rol_avg_start_date BIGINT NOT NULL,
                rol_avg_end_date BIGINT NOT NULL,
                timestamp BIGINT DEFAULT EPOCH(NOW()),
                UNIQUE (timestamp)
            )
            """
            },
        {
            "table_name": "tickers_sectors",
            "insert_sql":
            """
            CREATE TABLE IF NOT EXISTS tickers_sectors (
                id BIGINT PRIMARY KEY DEFAULT nextval('tickers_sectors_id_seq'),
                ticker TEXT NOT NULL,
                sector TEXT NOT NULL,
                industry TEXT NOT NULL,
                timestamp BIGINT DEFAULT EPOCH(NOW()),
                UNIQUE (ticker)
            )
            """
            },


        ]
