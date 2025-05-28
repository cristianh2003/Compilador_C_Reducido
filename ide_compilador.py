import tkinter as tk
from tkinter import scrolledtext, messagebox
from Analizador_lexico import AnalizadorLexico
from Analizador_sintactico_2 import AnalizadorSintactico

class IDECompilador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Compilador - C reducido")
        self.geometry("900x700")
        self.create_widgets()

    def create_widgets(self):
        # Código fuente
        tk.Label(self, text="Código fuente (C reducido):").pack(anchor='w')
        self.text_code = scrolledtext.ScrolledText(self, height=15, width=100)
        self.text_code.pack(padx=5, pady=5)

        # Botón analizar
        tk.Button(self, text="Analizar", command=self.analizar).pack(pady=5)

        # Tokens
        tk.Label(self, text="Tokens (Analizador Léxico):").pack(anchor='w')
        self.text_tokens = scrolledtext.ScrolledText(self, height=10, width=100, state='disabled')
        self.text_tokens.pack(padx=5, pady=5)

        # Mensajes sintácticos
        tk.Label(self, text="Mensajes del Analizador Sintáctico:").pack(anchor='w')
        self.text_sintactico = scrolledtext.ScrolledText(self, height=6, width=100, state='disabled')
        self.text_sintactico.pack(padx=5, pady=5)

        # Resultado compilación
        tk.Label(self, text="Resultado de la Compilación:").pack(anchor='w')
        self.text_resultado = scrolledtext.ScrolledText(self, height=8, width=100, state='disabled')
        self.text_resultado.pack(padx=5, pady=5)

    def analizar(self):
        codigo = self.text_code.get("1.0", tk.END)
        self.text_tokens.config(state='normal')
        self.text_tokens.delete("1.0", tk.END)
        self.text_sintactico.config(state='normal')
        self.text_sintactico.delete("1.0", tk.END)
        self.text_resultado.config(state='normal')
        self.text_resultado.delete("1.0", tk.END)
        
        lexer = AnalizadorLexico()
        tokens = []
        errores_lexicos = []
        try:
            # Encabezado de tabla
            tokens.append(f"{'Tipo':<20} {'Valor':<30} {'Línea':<5}")
            tokens.append('-'*60)
            for tok in lexer.tokenize(codigo):
                tokens.append(f"{tok.type:<20} {str(tok.value):<30} {tok.lineno:<5}")
            self.text_tokens.insert(tk.END, '\n'.join(tokens))
        except Exception as e:
            errores_lexicos.append(str(e))
            self.text_tokens.insert(tk.END, '\n'.join(tokens) + f"\nError léxico: {e}")
        self.text_tokens.config(state='disabled')

        # Sintáctico (modificado para mostrar mensajes similar a test.py)
        parser = AnalizadorSintactico()
        try:
            result = parser.parse(lexer.tokenize(codigo))
            msg = f"Análisis sintáctico exitoso.\nResultado Analizador sintactico: ", result
            self.text_sintactico.insert(tk.END, msg)
            self.text_resultado.insert(tk.END, str(result))
        except Exception as e:
            self.text_sintactico.insert(tk.END, f"Error de sintaxis: {e}")
        self.text_sintactico.config(state='disabled')
        self.text_resultado.config(state='disabled')

if __name__ == "__main__":
    app = IDECompilador()
    app.mainloop()
