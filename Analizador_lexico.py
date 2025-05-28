# Analizador_lexico.py

from sly import Lexer

class AnalizadorLexico(Lexer):
    # PALABRAS RESERVADAS
    reserved = {
        'int': 'INT',
        'char': 'CHAR',
        'void': 'VOID',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        'printf': 'PRINTF',
        'scanf': 'SCANF'
    }

    # TOKENS
    # En SLY, 'tokens' es un conjunto (set) de los NOMBRES de los tokens.
    # Estos nombres deben coincidir con las variables de clase para reglas simples,
    # o los nombres de los métodos para reglas con acciones.
    tokens = {
        # Nombres de tokens que se definirán como variables/métodos
        'ID', 'INTEGER_CONSTANT', 'CHAR_CONSTANT', 'STRING_CONSTANT',
        'op_suma', 'op_mul',
        'op_igual', 'op_relacional',
        'ASIGNACION',
        'I_PAREN', 'D_PAREN', 'I_LLAVE', 'D_LLAVE',
        'COMA', 'PUNTO_COMA', 'PUNTOS_SUSPENSIVOS', #'PORCENTAJE',

        # Añadimos los valores del diccionario 'reserved' al conjunto de tokens
        # ya que estos también son tipos de token válidos que la regla ID puede generar.
        *reserved.values()
    }

        # COMENTARIOS Y ESPACIOS


    # Ignorar comentarios tipo C /* ... */
    # Se utilizan los flags inline de modo DOTALL ((?s)) para permitir que el . incluya saltos de línea.
    ignore_comment = r'(?s)/\*.*?\*/'

    # String que contiene caracteres ignorados (espacios y tabulaciones)
    ignore = ' \t\r' 

    # Literales
    # literals = {'...', '%', '\"' }

    # REGLAS LEXICAS SIMPLES (expresiones regulares)
    op_suma            = r'\+|-'
    op_mul             = r'\*|/'
    op_igual           = r'==|!='
    op_relacional      = r'<|<=|>=|>' # Corresponds to ' < ' | ' <= ' | ' >= ' | ' > ' as per user prompt; SLY's longest match handles precedence.

    # Remaining tokens from the original selection
    ASIGNACION         = r'='
    I_PAREN            = r'\('
    D_PAREN            = r'\)'
    I_LLAVE            = r'\{'
    D_LLAVE            = r'\}'
    COMA               = r','
    PUNTO_COMA         = r';'
    PUNTOS_SUSPENSIVOS = r'\.\.\.'
    #COMILLAS =            r'\"' # Kept as commented from original selection
    #PORCENTAJE         = r'%'

    # REGLAS CON CÓDIGO
    # Se definen como métodos. El nombre del método es el nombre del token.
    # La expresión regular se pasa al decorador @_()

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        # Revisa si el identificador es una palabra reservada
        t.type = self.reserved.get(t.value, 'ID') 
        return t

    @_(r'0|([1-9][0-9]*)')
    def INTEGER_CONSTANT(self, t):
        t.value = int(t.value)
        return t

    @_(r"\'([^\\\n]|(\\.))\'")
    def CHAR_CONSTANT(self, t):
        return t 

    @_(r'\"([^\\\n]|(\\[n"\\]))*\"')
    def STRING_CONSTANT(self, t):
        # El valor ya es la cadena completa, incluyendo las comillas.
        # Si quieres quitar las comillas del valor del token:
        # t.value = t.value[1:-1] # Esto puede necesitar más lógica si hay escapes
        return t

    # Regla para manejar nuevas líneas y contar números de línea
    @_(r'\n+')
    def ignore_newline(self, t): 
        self.lineno += t.value.count('\n')

    # ERRORES
    def error(self, t):
        print(f"Error lexico en linea {self.lineno}: caracter ilegal '{t.value[0]}'")
        self.index += 1 # Avanza al siguiente carácter

