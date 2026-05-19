from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QHeaderView,
    QComboBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, QDate

from app.repositories.financeiro_repository import (
    listar_contas_financeiras,
    buscar_contas_financeiras,
    cadastrar_conta_financeira,
    atualizar_conta_financeira,
    excluir_conta_financeira,
)


TIPOS_CONTA = [
    ("Caixa", "caixa"),
    ("Banco", "banco"),
    ("Carteira digital", "carteira_digital"),
    ("Maquininha", "maquininha"),
    ("Cartão de crédito", "cartao_credito"),
    ("Outros", "outros"),
]


def formatar_moeda(valor):
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_moeda(texto):
    texto = str(texto or "0").strip().replace("R$", "").replace(".", "").replace(",", ".")
    return float(texto or 0)


class ContaFinanceiraDialog(QDialog):
    def __init__(self, parent=None, conta=None):
        super().__init__(parent)
        self.conta = conta

        self.setWindowTitle("Conta Financeira")
        self.setMinimumWidth(460)

        layout = QFormLayout(self)

        self.nome_input = QLineEdit()
        self.tipo_combo = QComboBox()
        for label, value in TIPOS_CONTA:
            self.tipo_combo.addItem(label, value)

        self.saldo_input = QLineEdit()
        self.saldo_input.setPlaceholderText("Ex.: 1500,00")

        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setDisplayFormat("dd/MM/yyyy")

        self.observacoes_input = QLineEdit()

        self.ativo_combo = QComboBox()
        self.ativo_combo.addItem("Ativa", 1)
        self.ativo_combo.addItem("Inativa", 0)

        layout.addRow("Nome:", self.nome_input)
        layout.addRow("Tipo:", self.tipo_combo)
        layout.addRow("Saldo inicial:", self.saldo_input)
        layout.addRow("Data do saldo inicial:", self.data_input)
        layout.addRow("Observações:", self.observacoes_input)
        layout.addRow("Status:", self.ativo_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if conta:
            self.nome_input.setText(conta["nome"] or "")
            self.saldo_input.setText(str(conta["saldo_inicial"] or 0).replace(".", ","))
            self.observacoes_input.setText(conta["observacoes"] or "")

            tipo_index = self.tipo_combo.findData(conta["tipo"])
            if tipo_index >= 0:
                self.tipo_combo.setCurrentIndex(tipo_index)

            ativo_index = self.ativo_combo.findData(conta["ativo"])
            if ativo_index >= 0:
                self.ativo_combo.setCurrentIndex(ativo_index)

            if conta["data_saldo_inicial"]:
                data = QDate.fromString(conta["data_saldo_inicial"], "yyyy-MM-dd")
                if data.isValid():
                    self.data_input.setDate(data)

    def get_data(self):
        return {
            "nome": self.nome_input.text().strip(),
            "tipo": self.tipo_combo.currentData(),
            "saldo_inicial": parse_moeda(self.saldo_input.text()),
            "data_saldo_inicial": self.data_input.date().toString("yyyy-MM-dd"),
            "observacoes": self.observacoes_input.text().strip(),
            "ativo": self.ativo_combo.currentData(),
        }


class ContasFinanceirasPage(QWidget):
    def __init__(self):
        super().__init__()
        self.contas = []
        self.setup_ui()
        self.carregar_contas()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Contas Financeiras")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")

        subtitle = QLabel("Cadastre caixa, banco, carteira digital, maquininha e outras contas do MEI.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nome ou tipo...")
        self.search_input.textChanged.connect(self.carregar_contas)
        self.search_input.setStyleSheet(self.input_style())

        self.btn_novo = QPushButton("Nova")
        self.btn_editar = QPushButton("Editar")
        self.btn_excluir = QPushButton("Excluir/Inativar")
        self.btn_atualizar = QPushButton("Atualizar")

        self.btn_novo.clicked.connect(self.nova_conta)
        self.btn_editar.clicked.connect(self.editar_conta)
        self.btn_excluir.clicked.connect(self.excluir_conta)
        self.btn_atualizar.clicked.connect(self.carregar_contas)

        for button in [self.btn_novo, self.btn_editar, self.btn_excluir, self.btn_atualizar]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(self.button_style())

        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.btn_novo)
        top_bar.addWidget(self.btn_editar)
        top_bar.addWidget(self.btn_excluir)
        top_bar.addWidget(self.btn_atualizar)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #4b5563; font-size: 14px;")

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Tipo", "Saldo inicial", "Saldo atual", "Status", "Criado em"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table_style())

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(self.table)

        self.setStyleSheet("QWidget { background-color: #ffffff; color: #111827; }")

    def carregar_contas(self):
        termo = self.search_input.text().strip()
        self.contas = buscar_contas_financeiras(termo) if termo else listar_contas_financeiras()

        self.table.setRowCount(len(self.contas))

        for row_index, conta in enumerate(self.contas):
            valores = [
                conta["id"],
                conta["nome"],
                conta["tipo"],
                formatar_moeda(conta["saldo_inicial"]),
                formatar_moeda(conta["saldo_atual"]),
                "Ativa" if conta["ativo"] else "Inativa",
                conta["criado_em"],
            ]

            for col_index, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                item.setTextAlignment(Qt.AlignCenter if col_index == 0 else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col_index, item)

        self.total_label.setText(f"Exibindo {len(self.contas)} conta(s) financeira(s).")

    def get_conta_selecionada(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None
        return self.contas[selected_row]

    def nova_conta(self):
        dialog = ContaFinanceiraDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "O nome da conta é obrigatório.")
                return
            cadastrar_conta_financeira(**data)
            self.carregar_contas()
            QMessageBox.information(self, "Sucesso", "Conta financeira cadastrada com sucesso.")

    def editar_conta(self):
        conta = self.get_conta_selecionada()
        if not conta:
            QMessageBox.warning(self, "Atenção", "Selecione uma conta para editar.")
            return

        dialog = ContaFinanceiraDialog(self, conta)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "O nome da conta é obrigatório.")
                return
            atualizar_conta_financeira(conta["id"], **data)
            self.carregar_contas()
            QMessageBox.information(self, "Sucesso", "Conta financeira atualizada com sucesso.")

    def excluir_conta(self):
        conta = self.get_conta_selecionada()
        if not conta:
            QMessageBox.warning(self, "Atenção", "Selecione uma conta para excluir ou inativar.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar",
            f"Deseja excluir/inativar a conta:\n\n{conta['nome']}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta == QMessageBox.Yes:
            ok, inativada = excluir_conta_financeira(conta["id"])
            self.carregar_contas()
            if ok and inativada:
                QMessageBox.information(self, "Sucesso", "A conta tinha lançamentos e foi inativada.")
            elif ok:
                QMessageBox.information(self, "Sucesso", "Conta excluída com sucesso.")

    @staticmethod
    def input_style():
        return """
            QLineEdit { padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: white; }
        """

    @staticmethod
    def button_style():
        return """
            QPushButton { background-color: #111827; color: white; padding: 10px 16px; border-radius: 8px; font-size: 14px; border: none; }
            QPushButton:hover { background-color: #1f2937; }
        """

    @staticmethod
    def table_style():
        return """
            QTableWidget { background-color: #ffffff; alternate-background-color: #f9fafb; color: #111827; border: 1px solid #e5e7eb; border-radius: 10px; gridline-color: #e5e7eb; font-size: 14px; }
            QHeaderView::section { background-color: #f9fafb; color: #111827; padding: 10px; border: none; border-bottom: 1px solid #e5e7eb; font-weight: bold; }
            QTableWidget::item { padding: 8px; background-color: transparent; color: #111827; }
            QTableWidget::item:selected { background-color: #dbeafe; color: #111827; }
        """
