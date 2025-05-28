from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QPlainTextEdit, QLabel, QTextEdit, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QFont, QColor, QTextFormat, QPainter, QIcon
from PyQt6.QtCore import Qt, QRect, QSize
import sys

from Analizador_lexico import AnalizadorLexico
from Analizador_sintactico import AnalizadorSintactico


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            # Color de fondo para la línea actual
            lineColor = QColor("#d0e7ff")  # Azul claro
            selection.format.setBackground(lineColor)

            # Color del texto para esa línea
            textColor = QColor("#000000")  # Negro
            selection.format.setForeground(textColor)

            # Aplicar formato a toda la línea
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)


    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.GlobalColor.lightGray)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(0, int(top), self.line_number_area.width(), int(self.fontMetrics().height()),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1


class IDEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IDE Compilador C Reducido")
        self.setWindowIcon(QIcon("ico.ico"))
        self.setGeometry(100, 100, 1000, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Botones superiores
        btn_layout = QHBoxLayout()
        btn_open = QPushButton("Abrir archivo .c")
        btn_open.clicked.connect(self.open_file)
        btn_analyze = QPushButton("Analizar código")
        btn_analyze.clicked.connect(self.analyze_code)
        btn_layout.addWidget(btn_open)
        btn_layout.addWidget(btn_analyze)
        layout.addLayout(btn_layout)

        # Editor con número de líneas
        self.editor = CodeEditor()
        self.editor.setFont(QFont("Courier", 11))
        layout.addWidget(self.editor)

        # Secciones ocultas inicialmente
        self.section_tokens = self.create_output_section("Tokens (Análisis Léxico):")
        self.section_parser = self.create_output_section("Mensajes del Analizador Sintáctico:")
        self.section_result = self.create_output_section("Resultado de la Compilación:")

        layout.addWidget(self.section_tokens["container"])
        layout.addWidget(self.section_parser["container"])
        layout.addWidget(self.section_result["container"])

        self.toggle_sections(False)

    def create_output_section(self, title):
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(container)
        label = QLabel(title)
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Courier", 10))
        text_edit.setReadOnly(True)
        layout.addWidget(label)
        layout.addWidget(text_edit)
        return {"container": container, "editor": text_edit}

    def toggle_sections(self, visible: bool):
        self.section_tokens["container"].setVisible(visible)
        self.section_parser["container"].setVisible(visible)
        self.section_result["container"].setVisible(visible)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo C", "", "Archivos C (*.c)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.editor.setPlainText(file.read())

    def analyze_code(self):
        self.toggle_sections(True)
        code = self.editor.toPlainText()

        # Reinicio de resultados
        self.section_tokens["editor"].clear()
        self.section_parser["editor"].clear()
        self.section_result["editor"].clear()

        # Léxico
        lexer = AnalizadorLexico()
        tokens_text = []
        try:
            tokens_text.append(f"{'Tipo':<20} {'Valor':<30} {'Línea':<5}")
            tokens_text.append('-' * 60)
            for tok in lexer.tokenize(code):
                tokens_text.append(f"{tok.type:<20} {str(tok.value):<30} {tok.lineno:<5}")
            self.section_tokens["editor"].setPlainText('\n'.join(tokens_text))
        except Exception as e:
            self.section_tokens["editor"].setPlainText(f"Error léxico: {str(e)}")

        # Sintáctico
        parser = AnalizadorSintactico()
        try:
            result = parser.parse(lexer.tokenize(code))
            self.section_parser["editor"].setPlainText("Análisis sintáctico exitoso.")
            self.section_result["editor"].setPlainText(str(result))
        except Exception as e:
            self.section_parser["editor"].setPlainText(f"Error de sintaxis: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IDEWindow()
    window.showMaximized()
    sys.exit(app.exec())
