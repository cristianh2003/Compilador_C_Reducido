from sly import Parser
from Analizador_lexico import AnalizadorLexico


class AnalizadorSintactico(Parser):

    tokens = AnalizadorLexico.tokens
    reserved = AnalizadorLexico.reserved
    
    debugfile = 'Sintactico.out'

    start = 'unidad_compilacion'

    precedence = (
        ('right', 'ASIGNACION'),       
        ('left', 'op_igual'),       
        ('left', 'op_relacional'), 
        ('left', 'op_suma'),  
        ('left', 'op_mul')
        # Parentheses, function calls are usually handled by grammar structure directly
    )

    # -- 1
    @_('unidad_compilacion declaracion_externa')
    def unidad_compilacion(self, p):
        return p.unidad_compilacion + [p.declaracion_externa]

    @_('declaracion_externa')
    def unidad_compilacion(self, p):
        return [p.declaracion_externa]  
    
    
    
    # -- 2
    @_('declaracion')
    def declaracion_externa(self, p):
        return p.declaracion

    @_('definicion_funcion')
    def declaracion_externa(self, p):
        return p.definicion_funcion
    
    
    # -- 3
    @_('encabezado_def_funcion cuerpo_funcion')
    def definicion_funcion(self, p):
        return ('definicion_funcion', p.encabezado_def_funcion, p.cuerpo_funcion)
        
    # -- 4
    @_('tipo_retorno ID I_PAREN def_parametros D_PAREN')
    def encabezado_def_funcion(self, p):
        return ('encabezado_funcion', p.tipo_retorno, p.ID, p.def_parametros)
    
    #@_('tipo_retorno ID I_PAREN D_PAREN') # Regla extra para funciones sin parámetros
    #def encabezado_def_funcion(self, p):
    #    return ('encabezado_funcion', p.tipo_retorno, p.ID, 'void')

    # -- 5
    @_('tipo')
    def tipo_retorno(self, p):
        return p.tipo
    
    @_('VOID')
    def tipo_retorno(self, p):
        return 'void'

    # -- 5.1 Se crean estas Producciones extras para "tipo"
    @_('INT')
    def tipo(self, p):
        return 'int'
    

    
    # -- 6
    @_('VOID')
    def def_parametros(self, p):
        return 'void'

    @_('lista_def_parametros')
    def def_parametros(self, p):
        return p.lista_def_parametros

    
    
    # -- 7
    @_('lista_def_parametros COMA tipo ID')
    def lista_def_parametros(self, p):
        p.lista_def_parametros.append((p.tipo, p.ID))
        return p.lista_def_parametros

    @_('tipo ID')
    def lista_def_parametros(self, p):
        return [(p.tipo, p.ID)]
    
        
    # -- 8    
    @_('I_LLAVE declaraciones lista_declaraciones D_LLAVE')
    def cuerpo_funcion(self, p):
        return ('cuerpo_funcion', p.declaraciones, p.lista_declaraciones)

    # -- 9
    @_('empty')
    def declaraciones(self, p):
        return []

    @_('declaraciones declaracion')
    def declaraciones(self, p):
        return p.declaraciones + [p.declaracion]

    

    @_('')  # Regla para λ (lambda) o vacío
    def empty(self, p):
        pass

    # -- 10
    @_('variable_declaracion')
    def declaracion(self, p):
        return p.variable_declaracion
    
    @_('declaracion_funcion')
    def declaracion(self, p):
        return p.declaracion_funcion
    
    # -- 11
    @_('tipo lista_identificadores PUNTO_COMA')       
    def variable_declaracion(self, p):
        return ('variable_declaracion', p.tipo, p.lista_identificadores)

    #@_('tipo lista_identificadores COMA variable_declaracion')  # regla extra para contemplar declaraciones de multiples variables separadas por coma
    #def variable_declaracion(self, p):
    #    p.lista_identificadores.extend(p.variable_declaracion[1])
    #    return ('variable_declaracion', p.tipo, p.lista_identificadores)


    




    # -- 12
    @_('tipo_retorno ID I_PAREN declaracion_parametros D_PAREN PUNTO_COMA')
    def declaracion_funcion(self, p):
       return ('declaracion_funcion', p.tipo_retorno, p.ID, p.def_parametros)

    # -- 13
    @_('lista_decl_parametros')
    def declaracion_parametros(self, p):
        return p.lista_decl_parametros
    
    @_('lista_decl_parametros COMA PUNTOS_SUSPENSIVOS')
    def declaracion_parametros(self, p):
        p.lista_decl_parametros.append('...')
        return p.lista_decl_parametros
    
    @_('VOID')
    def declaracion_parametros(self, p):
        return ['void']
    
    # -- 14
    @_('especificacion_decl_parametro')
    def lista_decl_parametros(self, p):
        return [p.especificacion_decl_parametro]
    
    @_('lista_decl_parametros COMA especificacion_decl_parametro')
    def lista_decl_parametros(self, p):
        p.lista_decl_parametros.append(p.especificacion_decl_parametro)
        return p.lista_decl_parametros
    
    # -- 15
    @_('tipo ID')
    def especificacion_decl_parametro(self, p):
        return (p.tipo, p.ID)
    
    @_('CHAR op_mul ID')
    def especificacion_decl_parametro(self, p):
        return ('char*', p.ID)  # Asumiendo que es un puntero a char
    
    # -- 16
    @_('lista_declaraciones declaracion')
    def lista_declaraciones(self, p):
        return p.lista_declaraciones + [p.declaracion]
    
    @_('declaracion')
    def lista_declaraciones(self, p):
        return [p.declaracion]
    
    # -- 17 
    @_('expresion PUNTO_COMA')
    def declaracion(self, p):
        return ('declaracion_expresion', p.expresion)
    
    @_('RETURN PUNTO_COMA')
    def declaracion(self, p):
        return ('declaracion_return', None)  # No hay expresión
    
    @_('RETURN expresion PUNTO_COMA')
    def declaracion(self, p):
        return ('declaracion_return', p.expresion)  # Retorna la expresión
    
    @_('WHILE I_PAREN expresion D_PAREN declaracion')
    def declaracion(self, p):
        return ('declaracion_while', p.expresion, p.declaracion)
    
    @_('IF I_PAREN expresion D_PAREN declaracion')
    def declaracion(self, p):
        return ('declaracion_if', p.expresion, p.declaracion)
    
    @_('IF I_PAREN expresion D_PAREN declaracion ELSE declaracion')
    def declaracion(self, p):
        return ('declaracion_if_else', p.expresion, p.declaracion0, p.declaracion1)
    
    @_('I_LLAVE lista_declaraciones D_LLAVE')
    def declaracion(self, p):
        return ('declaracion_bloque', p.lista_declaraciones)

    # -- 18
    @_('expresion_igualdad ASIGNACION expresion_igualdad')
    def expresion(self, p):
        return ('expresion_asignacion', p.expresion_igualdad0, p.expresion_igualdad1)
    
    @_('expresion_igualdad')
    def expresion(self, p):
        return p.expresion_igualdad
    
    # -- 19
    @_('expresion_relacional op_igual expresion_relacional')
    def expresion_igualdad(self, p):
        return ('expresion_igualdad', p.expresion_relacional0, p.expresion_relacional1)
    
    @_('expresion_relacional')
    def expresion_igualdad(self, p):
        return p.expresion_relacional
    
    # -- 20
    @_('expresion_simple op_relacional expresion_simple')
    def expresion_relacional(self, p):
        return ('expresion_relacional', p.expresion_simple0, p.expresion_simple1, p.op_relacional)
    
    @_('expresion_simple')
    def expresion_relacional(self, p):
        return p.expresion_simple
    
    # -- 21
    @_('expresion_simple op_suma term')
    def expresion_simple(self, p):
        return ('expresion_simple', p.expresion_simple, p.op_suma, p.term)
    
    @_('term')
    def expresion_simple(self, p):
        return p.term
    
    # -- 22
    @_('term op_mul factor')
    def term(self, p):
        return ('term', p.term, p.op_mul, p.factor)
    
    @_('factor')
    def term(self, p):
        return p.factor
    
    # -- 23
    @_('constant')
    def factor(self, p):
        return ('factor_constant', p.constant)

    @_('ID')
    def factor(self, p):
        return ('factor_id', p.ID)
    
    @_('I_PAREN expresion D_PAREN')
    def factor(self, p):
        return ('factor_parentesis', p.expresion)
    
    @_('op_suma factor')
    def factor(self, p):
        return ('factor_unario', p.op_suma, p.factor)
    
    @_('ID I_PAREN D_PAREN')
    def factor(self, p):
        return ('factor_llamada_funcion', p.ID, [])  # Llamada a función sin argumentos

    @_('ID I_PAREN lista_expresiones D_PAREN')
    def factor(self, p):
        return ('factor_llamada_funcion', p.ID, p.lista_expresiones)
    

    
    # -- 24
    @_('STRING_CONSTANT')
    def constant(self, p):
        return ('constant_string', p.STRING_CONSTANT)
    
    @_('numeric_constant')
    def constant(self, p):
        return ('constant_integer', p.numeric_constant)
    
    @_('CHAR_CONSTANT')
    def constant(self, p):
        return ('constant_char', p.CHAR_CONSTANT)
    
    # -- 25
    @_('INTEGER_CONSTANT')
    def numeric_constant(self, p):
        return ('numeric_constant', p.INTEGER_CONSTANT)
    
    #@_('floating_constant')     # <------ NO SE USA FLOAT EN ESTE COMPILADOR, PERO EXISTE UNA PRODUCCION PARA FLOATING_CONSTANT
    #def numeric_constant(self, p):
    #    return ('numeric_constant', p.floating_constant)
    
    # -- 26
    @_('expresion')
    def lista_expresiones(self, p):
        return [p.expresion]
    
    @_('lista_expresiones COMA expresion')
    def lista_expresiones(self, p):
        p.lista_expresiones.append(p.expresion)
        return p.lista_expresiones

    # -- 27
    @_('identificadortipo')
    def lista_identificadores(self, p):
        return [p.identificadortipo]
    
    @_('lista_identificadores COMA identificadortipo')
    def lista_identificadores(self, p):
        p.lista_identificadores.append(p.identificadortipo)
        return p.lista_identificadores
    
    # -- 28
    @_('INTEGER_CONSTANT')
    def identificadortipo(self, p):
        return ('identificador_tipo', p.INTEGER_CONSTANT)
    
    @_('CHAR_CONSTANT')
    def identificadortipo(self, p):
        return ('identificador_tipo', p.CHAR_CONSTANT)
    
    @_('ID')
    def identificadortipo(self, p):
        return ('identificador_tipo', p.ID)
    
    # -- 29 
    # -- REGLAS EXTRAS PARA FUNCIONES DE ENTRADA/SALIDA
    @_('SCANF I_PAREN STRING_CONSTANT D_PAREN PUNTO_COMA')
    def factor(self, p):
        return ('factor_scanf', p.STRING_CONSTANT)

    @_('PRINTF I_PAREN STRING_CONSTANT D_PAREN PUNTO_COMA')
    def factor(self, p):
        return ('factor_printf', p.STRING_CONSTANT)

    @_('PRINTF I_PAREN STRING_CONSTANT COMA expresion D_PAREN PUNTO_COMA')
    def factor(self, p):
        return ('factor_printf', p.STRING_CONSTANT, p.expresion)


    # ---- ERRORES DE SINTAXIS -----
    # def errors(self, tok):
    #    self.errors.append(tok)
    
    def error(self, p):
        if p:
            print(f"Error de sintaxis en el token {p.type} ('{p.value}') en la linea {p.lineno}")
        else:
            print("Error de sintaxis al final del archivo")
        # No llamar a super().error() ni dejar que SLY imprima mensajes extra
        # Lanzar excepción para que el flujo de tu app lo capture
        # raise SyntaxError(f"Error de sintaxis en el token {p.type} ('{p.value}') en la línea {p.lineno}") if p else SyntaxError("Error de sintaxis al final del archivo")

