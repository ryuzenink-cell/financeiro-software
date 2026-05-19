from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate

from app.repositories.financeiro_repository import relatorio_por_categoria, relatorio_saldo_contas
from app.ui.lancamentos_financeiros_page import formatar_moeda


class RelatoriosBasicosPage(QWidget):
    def __init__(self):
        super().__init__()
        self.registros = []
        self.setup_ui()
        self.carregar()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Relatórios Gerenciais")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")
        subtitle = QLabel("Relatórios intermediários para validar a base antes da DRE, BP e DFC completos.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        filters = QHBoxLayout()
        self.relatorio_combo = QComboBox()
        self.relatorio_combo.addItem("Receitas por categoria", "receita")
        self.relatorio_combo.addItem("Custos por categoria", "custo")
        self.relatorio_combo.addItem("Despesas por categoria", "despesa")
        self.relatorio_combo.addItem("Todos por categoria", "todos")
        self.relatorio_combo.addItem("Saldo por conta", "saldos")
        self.relatorio_combo.currentIndexChanged.connect(self.carregar)

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.data_inicio.setDisplayFormat("dd/MM/yyyy")
        self.data_inicio.dateChanged.connect(self.carregar)

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        self.data_fim.setDisplayFormat("dd/MM/yyyy")
        self.data_fim.dateChanged.connect(self.carregar)

        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar)
        self.btn_atualizar.setStyleSheet(self.button_style())

        filters.addWidget(QLabel("Relatório:"))
        filters.addWidget(self.relatorio_combo)
        filters.addWidget(QLabel("De:"))
        filters.addWidget(self.data_inicio)
        filters.addWidget(QLabel("Até:"))
        filters.addWidget(self.data_fim)
        filters.addWidget(self.btn_atualizar)
        filters.addStretch()

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #4b5563; font-size: 14px;")

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table_style())

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(filters)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(self.table)
        self.setStyleSheet("QWidget { background-color: #ffffff; color: #111827; }")

    def carregar(self):
        tipo = self.relatorio_combo.currentData()
        if tipo == "saldos":
            self.carregar_saldos()
        else:
            tipo_param = None if tipo == "todos" else tipo
            inicio = self.data_inicio.date().toString("yyyy-MM-dd")
            fim = self.data_fim.date().toString("yyyy-MM-dd")
            self.registros = relatorio_por_categoria(inicio, fim, tipo=tipo_param)
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(["Tipo", "Categoria", "Grupo DRE", "Grupo DFC", "Qtd.", "Total"])
            self.table.setRowCount(len(self.registros))
            total = 0.0
            for row_index, row in enumerate(self.registros):
                total += float(row["total"] or 0)
                valores = [row["tipo"], row["categoria"], row["grupo_dre"], row["grupo_dfc"], row["quantidade"], formatar_moeda(row["total"])]
                for col, valor in enumerate(valores):
                    item = QTableWidgetItem(str(valor))
                    item.setTextAlignment(Qt.AlignCenter if col in [0, 4, 5] else Qt.AlignVCenter | Qt.AlignLeft)
                    self.table.setItem(row_index, col, item)
            self.total_label.setText(f"Total do relatório: {formatar_moeda(total)}")

    def carregar_saldos(self):
        self.registros = relatorio_saldo_contas()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Conta", "Tipo", "Saldo inicial", "Saldo atual", "Status"])
        self.table.setRowCount(len(self.registros))
        total = 0.0
        for row_index, row in enumerate(self.registros):
            total += float(row["saldo_atual"] or 0)
            valores = [row["id"], row["nome"], row["tipo"], formatar_moeda(row["saldo_inicial"]), formatar_moeda(row["saldo_atual"]), "Ativa" if row["ativo"] else "Inativa"]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter if col in [0, 2, 3, 4, 5] else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col, item)
        self.total_label.setText(f"Saldo total das contas: {formatar_moeda(total)}")

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
