# test analizador lexico

from Analizador_lexico import AnalizadorLexico
from Analizador_sintactico import AnalizadorSintactico

if __name__ == '__main__':
    data = """ 
        /* ejemplo en c reducido */
        int main() {
            int x;
            int y;
            x = 10;
            y = 0;

            while (x > 0) {
                y = y + x;
                x = x - 1;
            }

            print(y);
        }
    """
    lexer = AnalizadorLexico()
    for tok in lexer.tokenize(data):
        print(f"type={tok.type!r}, value={tok.value!r}, lineno={tok.lineno}")    # print(f"type={tok.type!r}, value={tok.value!r}, lineno={tok.lineno}, index={tok.index}")

    parser = AnalizadorSintactico()
    try:
        result = parser.parse(lexer.tokenize(data))
        print("Resultado Analizador sintactico:", result)
    except Exception as e:
        print(f"Error de sintaxis: {e}")

