# /ejemplo.py

from utils.parseroperator import ParserOperator

if __name__ == "__main__":

    operator = ParserOperator(
        input_file="ejemplo.csv",
        parse_type="csv",
        skip_rows=0
    )

    result = operator.execute()

    print("¿Archivo válido?:", result)