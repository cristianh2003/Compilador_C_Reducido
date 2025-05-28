# Analizador_sintactico.py

from sly import Parser
# Asegúrate de que Analizador_lexico.py esté en el mismo directorio o en el PYTHONPATH
# o copia la clase AnalizadorLexico aquí si prefieres un solo archivo.
from Analizador_lexico import AnalizadorLexico

class AnalizadorSintactico(Parser):
    # Obtenemos la lista de tokens desde el lexer (requerido)
    tokens = AnalizadorLexico.tokens
    reserved = AnalizadorLexico.reserved

    # Opcional: para depuración, SLY generará un archivo parser.out
    debugfile = 'Analizador_sintactico_2.out'

    # Definición de precedencia y asociatividad de operadores (si es necesario)
    # Para esta gramática, muchas precedencias están implícitas en la estructura
    # de las reglas (expresion_aditiva -> termino -> factor).
    # Sin embargo, para una expresión más plana o para resolver ambigüedades:
    precedence = (
        ('right', 'ASIGNACION'),         # Asignación x = y = z  -> x = (y = z)
        ('left', 'op_igual'),
        ('left', 'op_relacional'),
        ('left', 'op_suma'),
        ('left', 'op_mul'),
        ('right', 'UNARY'),           # Operadores unarios como -factor
        # ('right', ELSE) # Para resolver ambigüedad de if-else, aunque SLY lo hace por defecto
    )

    # --- REGLAS DE PRODUCCIÓN ---

    # unidad_compilacion → { declaracion_externa }
    @_('declaraciones_externas_opt')
    def unidad_compilacion(self, p):
        return ('unidad_compilacion', p.declaraciones_externas_opt)

    @_('declaraciones_externas_opt declaracion_externa')
    def declaraciones_externas_opt(self, p):
        p.declaraciones_externas_opt.append(p.declaracion_externa)
        return p.declaraciones_externas_opt

    @_('empty')
    def declaraciones_externas_opt(self, p):
        return []

    # declaracion_externa → definicion_funcion | prototipo_funcion | declaracion_variable
    @_('definicion_funcion',
       'prototipo_funcion',
       'declaracion_variable')
    def declaracion_externa(self, p):
        return p[0] # Retorna el nodo AST de la regla que coincidió

    # definicion_funcion → encabezado_funcion cuerpo_funcion
    @_('encabezado_funcion cuerpo_funcion')
    def definicion_funcion(self, p):
        return ('definicion_funcion', p.encabezado_funcion, p.cuerpo_funcion)

    # prototipo_funcion → encabezado_funcion ";"
    @_('encabezado_funcion PUNTO_COMA')
    def prototipo_funcion(self, p):
        return ('prototipo_funcion', p.encabezado_funcion)

    # encabezado_funcion → tipo_retorno identificador "(" parametros ")"
    @_('tipo_retorno ID I_PAREN parametros D_PAREN')
    def encabezado_funcion(self, p):
        return ('encabezado_funcion', p.tipo_retorno, p.ID, p.parametros)

    # tipo_retorno → tipo | "void"
    @_('tipo')
    def tipo_retorno(self, p):
        return ('tipo_retorno', p.tipo)
    @_('VOID')
    def tipo_retorno(self, p):
        return ('tipo_retorno', p.VOID)


    # parametros → lista_parametros | "void"
    @_('lista_parametros')
    def parametros(self, p):
        return p.lista_parametros # lista_parametros ya devuelve una lista
    @_('VOID') # Indica sin parámetros
    def parametros(self, p):
        return [] # Lista vacía para "void" como parámetro

    # lista_parametros → especificacion_parametro { "," especificacion_parametro } [ "," "..." ]
    @_('lista_parametros_base opt_ellipsis')
    def lista_parametros(self, p):
        if p.opt_ellipsis:
            return ('lista_parametros_con_ellipsis', p.lista_parametros_base)
        return p.lista_parametros_base # Es una lista de especificaciones

    @_('lista_parametros_base COMA especificacion_parametro')
    def lista_parametros_base(self, p):
        p.lista_parametros_base.append(p.especificacion_parametro)
        return p.lista_parametros_base
    @_('especificacion_parametro')
    def lista_parametros_base(self, p):
        return [p.especificacion_parametro]

    @_('COMA PUNTOS_SUSPENSIVOS')
    def opt_ellipsis(self, p):
        return True
    @_('empty')
    def opt_ellipsis(self, p):
        return False


    # especificacion_parametro → tipo identificador | "char" "*" identificador
    @_('tipo ID')
    def especificacion_parametro(self, p):
        return ('espec_param', p.tipo, p.ID)
    @_('CHAR op_mul ID') # Asumimos que op_mul aquí será '*'
    def especificacion_parametro(self, p):
        if p.op_mul == '*':
            return ('espec_param_char_ptr', p.ID)
        else:
            # Esto no debería ocurrir si la gramática es correcta y el lexer también.
            # SLY manejaría esto como un error de sintaxis si op_mul fuera '/'.
            # Podríamos generar un error específico si quisiéramos ser más robustos aquí.
            print(f"Advertencia: Se esperaba '*' para puntero char, se obtuvo '{p.op_mul}' en especificacion_parametro.")
            # Para propósitos de seguir, podríamos tratarlo como un ID normal o fallar.
            # Por ahora, lo dejamos así; el parser debería fallar si no es '*'.
            # Considerar un token STAR dedicado en el lexer sería más limpio.
            pass # Dejar que SLY falle si op_mul no es lo esperado para esta regla

    # declaracion_variable → tipo lista_identificadores ";"
    @_('tipo lista_identificadores PUNTO_COMA')
    def declaracion_variable(self, p):
        return ('declaracion_variable', p.tipo, p.lista_identificadores)

    # lista_identificadores → identificador { "," identificador }
    @_('lista_identificadores COMA ID')
    def lista_identificadores(self, p):
        p.lista_identificadores.append(p.ID)
        return p.lista_identificadores
    @_('ID')
    def lista_identificadores(self, p):
        return [p.ID]

    # cuerpo_funcion → "{" declaraciones sentencias "}"
    @_('I_LLAVE declaraciones_opt sentencias_opt D_LLAVE')
    def cuerpo_funcion(self, p):
        return ('cuerpo_funcion', p.declaraciones_opt, p.sentencias_opt)

    # declaraciones → { declaracion_variable }
    @_('declaraciones_opt declaracion_variable')
    def declaraciones_opt(self, p):
        p.declaraciones_opt.append(p.declaracion_variable)
        return p.declaraciones_opt
    @_('empty')
    def declaraciones_opt(self, p):
        return []

    # sentencias → { sentencia }
    @_('sentencias_opt sentencia')
    def sentencias_opt(self, p):
        p.sentencias_opt.append(p.sentencia)
        return p.sentencias_opt
    @_('empty')
    def sentencias_opt(self, p):
        return []

    # sentencia (varias reglas)
    @_('expresion PUNTO_COMA')
    def sentencia(self, p):
        return ('sentencia_expresion', p.expresion)

    @_('RETURN PUNTO_COMA')
    def sentencia(self, p):
        return ('sentencia_return_void',)

    @_('RETURN expresion PUNTO_COMA')
    def sentencia(self, p):
        return ('sentencia_return_valor', p.expresion)

    @_('WHILE I_PAREN expresion D_PAREN sentencia')
    def sentencia(self, p):
        return ('sentencia_while', p.expresion, p.sentencia)

    # sentencia → "if" "(" expresion ")" sentencia [ "else" sentencia ]
    # SLY resuelve la ambigüedad del "dangling else" por defecto prefiriendo shift,
    # lo que asocia el ELSE con el IF más cercano, que es lo usual.
    # Si se prefiere, se puede hacer explícito con reglas como if_stmt_no_else / if_stmt_with_else
    # o usando %prec ELSE.
    @_('IF I_PAREN expresion D_PAREN sentencia ELSE sentencia')
    def sentencia(self, p):
        return ('sentencia_if_else', p.expresion, p.sentencia0, p.sentencia1)

    @_('IF I_PAREN expresion D_PAREN sentencia')
    def sentencia(self, p):
        return ('sentencia_if', p.expresion, p.sentencia) # p.sentencia0 es el cuerpo del if

    @_('I_LLAVE sentencias_opt D_LLAVE') # Bloque como sentencia
    def sentencia(self, p):
        return ('sentencia_bloque', p.sentencias_opt)


    # expresion → identificador "=" expresion | expresion_igualdad
    @_('ID ASIGNACION expresion')
    def expresion(self, p):
        return ('asignacion', p.ID, p.expresion)
    @_('expresion_igualdad')
    def expresion(self, p):
        return p.expresion_igualdad


    # expresion_igualdad → expresion_relacional { op_igual expresion_relacional }
    @_('expresion_igualdad op_igual expresion_relacional')
    def expresion_igualdad(self, p):
        return ('op_binaria', p.op_igual, p.expresion_igualdad, p.expresion_relacional)
    @_('expresion_relacional')
    def expresion_igualdad(self, p):
        return p.expresion_relacional


    # expresion_relacional → expresion_aditiva { op_relacional expresion_aditiva }
    # La asociatividad izquierda es común, pero las comparaciones a veces no son asociativas (a < b < c es error)
    # Si se quiere no asociatividad, se definiría como: expr_rel : expr_add OP_REL expr_add | expr_add
    # y se usaría ('nonassoc', op_relacional) en precedence.
    # La gramática con { } sugiere asociatividad izquierda.
    @_('expresion_relacional op_relacional expresion_aditiva')
    def expresion_relacional(self, p):
        return ('op_binaria', p.op_relacional, p.expresion_relacional, p.expresion_aditiva)
    @_('expresion_aditiva')
    def expresion_relacional(self, p):
        return p.expresion_aditiva


    # expresion_aditiva → termino { op_suma termino }
    @_('expresion_aditiva op_suma termino')
    def expresion_aditiva(self, p):
        return ('op_binaria', p.op_suma, p.expresion_aditiva, p.termino)
    @_('termino')
    def expresion_aditiva(self, p):
        return p.termino


    # termino → factor { op_mul factor }
    @_('termino op_mul factor')
    def termino(self, p):
        return ('op_binaria', p.op_mul, p.termino, p.factor)
    @_('factor')
    def termino(self, p):
        return p.factor


    # factor → constante | identificador | "(" expresion ")" | op_suma factor | identificador "(" [ lista_expresiones ] ")"
    @_('constante')
    def factor(self, p):
        return p.constante # constante ya retorna un nodo ('tipo_constante', valor)
    @_('ID')
    def factor(self, p):
        return ('identificador', p.ID)
    @_('I_PAREN expresion D_PAREN')
    def factor(self, p):
        return ('expr_agrupada', p.expresion) # o simplemente p.expresion

    @_('op_suma factor %prec UNARY') # Operador unario (+factor, -factor)
    def factor(self, p):
        return ('op_unaria', p.op_suma, p.factor)

    # Llamada a función: identificador "(" [ lista_expresiones ] ")"
    @_('ID I_PAREN lista_expresiones_opt D_PAREN')
    def factor(self, p):
        return ('llamada_funcion', p.ID, p.lista_expresiones_opt)

    @_('lista_expresiones')
    def lista_expresiones_opt(self, p):
        return p.lista_expresiones
    @_('empty')
    def lista_expresiones_opt(self, p):
        return [] # Lista vacía si no hay expresiones


    # lista_expresiones → expresion { "," expresion }
    @_('lista_expresiones COMA expresion')
    def lista_expresiones(self, p):
        p.lista_expresiones.append(p.expresion)
        return p.lista_expresiones
    @_('expresion')
    def lista_expresiones(self, p):
        return [p.expresion]


    # constante → string_constant | numeric_constant | char_constant
    @_('STRING_CONSTANT')
    def constante(self, p):
        return ('string_constante', p.STRING_CONSTANT)
    @_('numeric_constant')
    def constante(self, p):
        return p.numeric_constant # numeric_constant ya devuelve nodo etiquetado
    @_('CHAR_CONSTANT')
    def constante(self, p):
        return ('char_constante', p.CHAR_CONSTANT)


    # numeric_constant → integer_constant | floating_constant
    # Tu lexer solo tiene INTEGER_CONSTANT, así que omito floating_constant
    @_('INTEGER_CONSTANT')
    def numeric_constant(self, p):
        return ('integer_constante', p.INTEGER_CONSTANT)
    # @_('FLOATING_CONSTANT') # Si el lexer lo tuviera
    # def numeric_constant(self, p):
    #     return ('float_constante', p.FLOATING_CONSTANT)

    # tipo → "int" | "char"
    @_('INT')
    def tipo(self, p):
        return p.INT # El valor del token ya es 'int'
    @_('CHAR')
    def tipo(self, p):
        return p.CHAR # El valor del token ya es 'char'

    # Regla para producciones vacías (epsilon)
    @_('')
    def empty(self, p):
        pass # Opcionalmente: return None o una tupla específica como ('empty',)


    # MANEJO DE ERRORES
    def error(self, p):
        if p:
            print(f"Error de sintaxis en token {p.type} ('{p.value}') en linea {p.lineno}")
            # Podrías intentar alguna recuperación aquí, por ejemplo, buscando el próximo ';'
            # self.errok() # Si la recuperación es exitosa
        else:
            print("Error de sintaxis: Fin de archivo inesperado (EOF)")


# --- Código de prueba ---
if __name__ == '__main__':
    lexer = AnalizadorLexico()
    parser = AnalizadorSintactico()

    codigo_prueba = """
    int main(void) {
        int x, y, z;
        char c;
        char* s;

        x = 10;
        y = x * (5 + 3);
        if (y > 20) {
            printf("Mayor que 20\\n");
        } else {
            printf("Menor o igual a 20\\n");
            z = y - 1;
        }
        
        while (x > 0) {
            x = x - 1;
        }
        return 0;
    }

    void foo(int a, char b, ...) {
        int i;
        i = a + b; /* Esto podría ser un error semántico, pero sintácticamente ok */
    }
    
    int prototipo_func(int param1); 
    """

    print("--- Tokens ---")
    for tok in lexer.tokenize(codigo_prueba):
        print(f"type={tok.type}, value={repr(tok.value)}, line={tok.lineno}, index={tok.index}")

    print("\n--- Parseo ---")
    result = parser.parse(lexer.tokenize(codigo_prueba))
    
    if result:
        print("\nParseo exitoso.")
        # Para una visualización más bonita del AST, podrías usar pprint
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        # Descomenta la siguiente línea para ver el AST (puede ser muy grande)
        # pp.pprint(result) 
    else:
        print("\nFallo en el parseo.")

    codigo_con_error = """
    int main(void) {
        int x = 10 * (5 + ; // Error aquí
        return 0;
    }
    """
    print("\n--- Parseo con error ---")
    # Es necesario resetear el lexer si se va a usar para un nuevo texto (para lineno, etc.)
    # lexer = AnalizadorLexico() # Reinstanciar o tener un método reset
    # O simplemente tokenizar de nuevo:
    result_error = parser.parse(lexer.tokenize(codigo_con_error))
    if not result_error:
        print("Fallo en el parseo (esperado).")