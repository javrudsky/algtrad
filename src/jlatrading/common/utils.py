from datetime import datetime

"""Common utility functions for the trading project.

This module contains helpers to work with dates and times in a consistent format.
"""


class DateFormat:
    YYYYMMDD_FORMAT = "%Y-%m-%d"


class DateUtils:

    @staticmethod
    def to_yyyymmdd_str(ts):
        """Convert a datetime to a YYYY-MM-DD formatted string.
            Args:
                ts: datetime instance to convert.
            Returns:
                A string in ISO-like date format "YYYY-MM-DD".
            Raises:
                ValueError: if the provided value cannot be formatted using strftime.
        """

        try:
            return ts.strftime(DateFormat.YYYYMMDD_FORMAT)
        except ValueError:
            pass
        raise ValueError(f"Unable to convert time to format {DateFormat.YYYYMMDD_FORMAT} string")

    @staticmethod
    def now_yyyymmdd_str():
        """Get the current date as a YYYY-MM-DD formatted string.
            Returns:
                A string representing the current date in "YYYY-MM-DD" format.
        """
        return DateUtils.to_yyyymmdd_str(datetime.now())

    @staticmethod
    def first_of_curr_month_yyyymmdd_str():
        """Get the first day of the current month as a YYYY-MM-DD formatted string.
            Returns:
                A string representing the first day of the current month in "YYYY-MM-DD" format.
        """
        now = datetime.now()
        first_of_month = datetime(year=now.year, month=now.month, day=1)
        return DateUtils.to_yyyymmdd_str(first_of_month)

    @staticmethod
    def is_valid_yyyymmdd_str(date_str):
        """Validate if a string is in the YYYY-MM-DD format.
            Args:
                date_str: The string to validate.
            Returns:
                True if the string is a valid date in "YYYY-MM-DD" format, False otherwise.
        """
        try:
            datetime.strptime(date_str, DateFormat.YYYYMMDD_FORMAT)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_date_range(start_date: str, end_date: str) -> bool:
        """
        Check if the start date is before or equal to the end date.
        """
        try:
            start = datetime.strptime(start_date, DateFormat.YYYYMMDD_FORMAT)
            end = datetime.strptime(end_date, DateFormat.YYYYMMDD_FORMAT)
            return start <= end
        except ValueError:
            return False
