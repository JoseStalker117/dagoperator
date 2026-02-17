# /utils/parsers/csv/parser.py

import csv
import re


class ParserOperator:

    def __init__(self, input_file: str, config: dict):
        self.input_file = input_file
        self.config = config

        self.file_config = config.get("file", {})
        self.structure = config.get("structure", {})
        self.columns = config.get("columns", [])

    def validate(self) -> bool:
        try:
            delimiter = self.file_config.get("delimiter", ",")
            margin = self.file_config.get("margin", False)
            encoding = self.file_config.get("encoding", "utf-8")
            skip_rows = self.structure.get("skip_rows", 0)

            with open(self.input_file, encoding=encoding) as f:

                # validar margin
                if not margin:
                    for line in f:
                        if re.search(r",\s+", line):
                            print("Espacios entre delimitadores detectados")
                            return False
                    f.seek(0)

                reader = csv.reader(f, delimiter=delimiter)

                for _ in range(skip_rows):
                    next(reader)

                # header
                if self.structure.get("header", True):
                    header = next(reader)
                    expected = [c["name"] for c in self.columns]
                    if header != expected:
                        print("Header inválido")
                        return False

                # validar filas
                for row in reader:
                    if len(row) != len(self.columns):
                        return False

                    for value, rules in zip(row, self.columns):
                        if not self._validate_value(value, rules):
                            print(f"Error columna: {rules['name']}")
                            return False

            return True

        except Exception as e:
            print(e)
            return False

    def _validate_value(self, value, rules):

        if rules.get("required") and value.strip() == "":
            return False

        if "max_length" in rules:
            if len(value) > rules["max_length"]:
                return False

        if "type" in rules:
            if not self._validate_type(value, rules):
                return False

        return True

    def _validate_type(self, value, rules):
        t = rules["type"]

        try:
            if t == "int":
                int(value)

            elif t == "float":
                float(value)

                if "max_decimals" in rules:
                    decimals = value.split(".")
                    if len(decimals) == 2:
                        if len(decimals[1]) > rules["max_decimals"]:
                            return False

            elif t == "string":
                str(value)

            else:
                return False

            return True

        except:
            return False