# Count instruments rows download by date
select count(*), download_date from (select strftime(download_timestamp, '%d-%m-%Y') as download_date from instruments_prices) group by download_date;

# Check for Nan values in daily bar data download for yfinance
SELECT count(*) FROM (
SELECT 1 FROM daily_bar_history WHERE open == -1
UNION ALL
SELECT 1 FROM daily_bar_history WHERE close == -1
UNION ALL
SELECT 1 FROM daily_bar_history WHERE high == -1
UNION ALL
SELECT 1 FROM daily_bar_history WHERE low == -1
);

# Tickers containing no data vs ticket having real data
SELECT sum(no_data) AS no_data, sum(has_data) AS has_data, ticker FROM (
SELECT count(*) AS no_data, 0 AS has_data, ticker FROM daily_bar_history WHERE open == -1 GROUP BY ticker
UNION ALL
SELECT 0 AS no_data, count(*) AS has_data, ticker FROM daily_bar_history WHERE open > -1 GROUP BY ticker
)
GROUP BY ticker;


# Creating a summary of the daily bar history view
SELECT 
strftime(to_timestamp(min(date)) AT TIME ZONE 'UTC-3', '%d-%m-%Y') AS start_date, 
strftime(to_timestamp(max(date)) AT TIME ZONE 'UTC-3', '%d-%m-%Y') AS end_date, 
COUNT(*) AS total_rows,
FROM daily_bar_history;



