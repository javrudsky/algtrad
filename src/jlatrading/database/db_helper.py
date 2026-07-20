import re


class DbHelper:
    @staticmethod
    def normalize_sql(value: str) -> str:
        return re.sub(r"\s+", " ", value.replace("\n", " ")).strip()

    @staticmethod
    def quote_identifier(identifier: str) -> str:
        return f'"{identifier.replace(chr(34), chr(34) * 2)}"'
