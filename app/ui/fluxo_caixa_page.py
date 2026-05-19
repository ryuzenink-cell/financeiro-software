from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate

from app.repositories.financeiro_repository import relatorio_fluxo_caixa, calcular_nfc
from app.ui.lancamentos_financeiros_page import formatar_moeda


class FluxoCaixaPage(QWidget):
    def __init__(self):
        super().__init__()
        self.registros = []
        self.setup_ui()
        self.carregar()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Fluxo de Caixa")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")
        subtitle = QLabel("Visualize caixa realizado, caixa projetado e necessidade de fluxo de caixa do MEI.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        filters = QHBoxLayout()
        self.modo_combo = QComboBox()
        self.modo_combo.addItem("Realizado", False)
        self.modo_combo.addItem("Projetado", True)
        self.modo_combo.currentIndexChanged.connect(self.carregar)

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.data_inicio.setDisplayFormat("dd/MM/yyyy")
        self.data_inicio.dateChanged.connect(self.carregar)

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate().addMonths(1))
        self.data_fim.setDisplayFormat("dd/MM/yyyy")
        self.data_fim.dateChanged.connect(self.carregar)

        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar)
        self.btn_atualizar.setStyleSheet(self.button_style())

        filters.addWidget(QLabel("Modo:"))
        filters.addWidget(self.modo_combo)
        filters.addWidget(QLabel("De:"))
        filters.addWidget(self.data_inicio)
        filters.addWidget(QLabel("Até:"))
        filters.addWidget(self.data_fim)
        filters.addWidget(self.btn_atualizar)
        filters.addStretch()

        self.cards_label = QLabel()
        self.cards_label.setStyleSheet("font-size: 15px; color: #111827; padding: 12px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px;")

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Data", "Tipo", "Descrição", "Categoria", "Conta", "Entrada", "Saída", "Saldo acumulado"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table_style())

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(filters)
        main_layout.addWidget(self.cards_label)
        main_layout.addWidget(self.table)
        self.setStyleSheet("QWidget { background-color: #ffffff; color: #111827; }")

    def carregar(self):
        projetado = self.modo_combo.currentData()
        inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        fim = self.data_fim.date().toString("yyyy-MM-dd")
        self.registros = relatorio_fluxo_caixa(inicio, fim, projetado=projetado)

        self.table.setRowCount(len(self.registros))
        total_entradas = 0.0
        total_saidas = 0.0
        saldo = 0.0
        for row_index, row in enumerate(self.registros):
            impacto = float(row["impacto_caixa"] or 0)
            entrada = impacto if impacto > 0 else 0.0
            saida = abs(impacto) if impacto < 0 else 0.0
            total_entradas += entrada
            total_saidas += saida
            saldo += impacto
            valores = [
                row["data_fluxo"] or "",
                row["tipo"],
                row["descricao"],
                row["categoria_nome"] or "",
                row["conta_nome"] or "",
                formatar_moeda(entrada) if entrada else "-",
                formatar_moeda(saida) if saida else "-",
                formatar_moeda(saldo),
            ]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter if col in [0, 1, 5, 6, 7] else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col, item)

        nfc = calcular_nfc(30, 20)
        self.cards_label.setText(
            f"Entradas: {formatar_moeda(total_entradas)}   |   Saídas: {formatar_moeda(total_saidas)}   |   "
            f"Saldo do período: {formatar_moeda(total_entradas - total_saidas)}   |   "
            f"NFC 30 dias com 20% de reserva: {formatar_moeda(nfc['nfc'])}"
        )

    def button_style(self):
        return """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """

    def table_style(self):
        return """
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                color: #111827;
                gridline-color: #e5e7eb;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                color: #111827;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """
