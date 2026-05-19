from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate

from app.repositories.financeiro_repository import (
    listar_contas_financeiras, registrar_conciliacao, listar_conciliacoes
)
from app.ui.lancamentos_financeiros_page import formatar_moeda, parse_moeda


class ConciliacaoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.registros = []
        self.setup_ui()
        self.carregar()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Conciliação de Caixa/Banco")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")
        subtitle = QLabel("Compare o saldo do sistema com o saldo real da conta financeira.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        form = QHBoxLayout()
        self.conta_combo = QComboBox()
        self.carregar_contas_combo()
        self.conta_combo.currentIndexChanged.connect(self.carregar)

        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setDisplayFormat("dd/MM/yyyy")

        self.saldo_real_input = QLineEdit()
        self.saldo_real_input.setPlaceholderText("Saldo real no banco/caixa")
        self.saldo_real_input.setStyleSheet(self.input_style())

        self.obs_input = QLineEdit()
        self.obs_input.setPlaceholderText("Observações")
        self.obs_input.setStyleSheet(self.input_style())

        self.btn_registrar = QPushButton("Registrar conciliação")
        self.btn_registrar.clicked.connect(self.registrar)
        self.btn_registrar.setStyleSheet(self.button_style())

        form.addWidget(QLabel("Conta:"))
        form.addWidget(self.conta_combo)
        form.addWidget(QLabel("Data:"))
        form.addWidget(self.data_input)
        form.addWidget(self.saldo_real_input)
        form.addWidget(self.obs_input)
        form.addWidget(self.btn_registrar)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #4b5563; font-size: 14px;")

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Data", "Conta", "Saldo sistema", "Saldo real", "Diferença", "Observações"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table_style())

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(form)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(self.table)
        self.setStyleSheet("QWidget { background-color: #ffffff; color: #111827; }")

    def carregar_contas_combo(self):
        self.conta_combo.clear()
        for conta in listar_contas_financeiras(ativas_apenas=True):
            self.conta_combo.addItem(conta["nome"], conta["id"])

    def registrar(self):
        conta_id = self.conta_combo.currentData()
        if not conta_id:
            QMessageBox.warning(self, "Atenção", "Cadastre/seleciona uma conta financeira.")
            return
        try:
            saldo_real = parse_moeda(self.saldo_real_input.text())
        except Exception:
            QMessageBox.warning(self, "Atenção", "Saldo real inválido.")
            return
        registrar_conciliacao(
            conta_id,
            self.data_input.date().toString("yyyy-MM-dd"),
            saldo_real,
            self.obs_input.text().strip(),
        )
        self.saldo_real_input.clear()
        self.obs_input.clear()
        self.carregar()
        QMessageBox.information(self, "Sucesso", "Conciliação registrada.")

    def carregar(self):
        conta_id = self.conta_combo.currentData() if hasattr(self, "conta_combo") else None
        self.registros = listar_conciliacoes(conta_id)
        self.table.setRowCount(len(self.registros))
        for row_index, row in enumerate(self.registros):
            valores = [
                row["id"], row["data_conciliacao"], row["conta_nome"],
                formatar_moeda(row["saldo_sistema"]), formatar_moeda(row["saldo_real"]),
                formatar_moeda(row["diferenca"]), row["observacoes"] or "",
            ]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter if col in [0, 1, 3, 4, 5] else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col, item)
        self.total_label.setText(f"Exibindo {len(self.registros)} conciliação(ões).")

    def input_style(self):
        return """
            QLineEdit {
                padding: 9px 12px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
                color: #111827;
            }
        """

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
