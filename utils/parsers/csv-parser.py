# /utils/parsers/csv/parser.py

import csv
import yaml
import re
from datetime import datetime


class Parser:

    def __init__(self, input_file: str, skip_rows: int = 0):
        self.input_file = input_file
        self.skip_rows = skip_rows
        self.config = self._load_config()

    def _load_config(self) -> dict:
        with open("utils/parsers/csv/config.yaml", "r") as f:
            return yaml.safe_load(f)

    def validate(self) -> bool:
        try:
            delimiter = self.config.get("delimiter", ",")
            margin = self.config.get("margin", False)
            expected_columns = self.config.get("columns", [])

            with open(self.input_file, newline='', encoding='utf-8') as csvfile:

                # Validación de margin
                if not margin:
                    for line in csvfile:
                        if re.search(r",\s+", line):
                            print("Espacios entre delimitadores no permitidos")
                            return False
                    csvfile.seek(0)

                reader = csv.reader(csvfile, delimiter=delimiter)

                # Saltar filas iniciales
                for _ in range(self.skip_rows):
                    next(reader)

                header = next(reader)
                expected_header = [col["name"] for col in expected_columns]

                if header != expected_header:
                    print("Header inválido")
                    return False

                # Validar filas
                for row in reader:
                    if len(row) != len(expected_columns):
                        print("Número incorrecto de columnas")
                        return False

                    for value, rules in zip(row, expected_columns):
                        if not self._validate_value(value, rules):
                            print(f"Error en columna: {rules['name']}")
                            return False

            return True

        except Exception as e:
            print(f"[CSV Parser ERROR]: {e}")
            return False

    def _validate_value(self, value: str, rules: dict) -> bool:

        # requerido
        if rules.get("required", False) and value.strip() == "":
            return False

        # max_length
        if "max_length" in rules:
            if len(value) > rules["max_length"]:
                return False

        # tipo
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

            elif t == "date":
                return self._validate_date(value, rules)

            else:
                return False

            return True

        except:
            return False
    
    def _validate_date(self, value, rules):
        if value.strip() == "":
            return not rules.get("required", False)

        # formato obligatorio si se define tipo date
        date_format = rules.get("format")

        if not date_format:
            # fallback: formatos comunes
            common_formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y"
            ]

            for fmt in common_formats:
                try:
                    datetime.strptime(value, fmt)
                    return True
                except:
                    continue

            return False

        # validación estricta
        try:
            datetime.strptime(value, date_format)
            return True
        except:
            return False