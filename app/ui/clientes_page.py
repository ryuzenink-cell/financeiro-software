from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt

from app.repositories.cliente_repository import (
    listar_clientes, buscar_clientes, cadastrar_cliente, atualizar_cliente, excluir_cliente
)


class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.setWindowTitle("Cliente")
        self.setMinimumWidth(480)
        layout = QFormLayout(self)

        self.nome_input = QLineEdit()
        self.documento_input = QLineEdit()
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        self.obs_input = QLineEdit()
        self.ativo_combo = QComboBox()
        self.ativo_combo.addItem("Ativo", 1)
        self.ativo_combo.addItem("Inativo", 0)

        layout.addRow("Nome:", self.nome_input)
        layout.addRow("Documento:", self.documento_input)
        layout.addRow("Telefone:", self.telefone_input)
        layout.addRow("E-mail:", self.email_input)
        layout.addRow("Endereço:", self.endereco_input)
        layout.addRow("Observações:", self.obs_input)
        layout.addRow("Status:", self.ativo_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if cliente:
            self.nome_input.setText(cliente["nome"] or "")
            self.documento_input.setText(cliente["documento"] or "")
            self.telefone_input.setText(cliente["telefone"] or "")
            self.email_input.setText(cliente["email"] or "")
            self.endereco_input.setText(cliente["endereco"] or "")
            self.obs_input.setText(cliente["observacoes"] or "")
            idx = self.ativo_combo.findData(cliente["ativo"])
            if idx >= 0:
                self.ativo_combo.setCurrentIndex(idx)

    def get_data(self):
        return {
            "nome": self.nome_input.text().strip(),
            "documento": self.documento_input.text().strip(),
            "telefone": self.telefone_input.text().strip(),
            "email": self.email_input.text().strip(),
            "endereco": self.endereco_input.text().strip(),
            "observacoes": self.obs_input.text().strip(),
            "ativo": self.ativo_combo.currentData(),
        }


class ClientesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.clientes = []
        self.setup_ui()
        self.carregar_clientes()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Clientes")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")
        subtitle = QLabel("Cadastre clientes para vincular receitas, contas a receber e histórico financeiro.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nome, documento, telefone ou e-mail...")
        self.search_input.textChanged.connect(self.carregar_clientes)
        self.search_input.setStyleSheet(self.input_style())

        self.btn_novo = QPushButton("Novo")
        self.btn_editar = QPushButton("Editar")
        self.btn_excluir = QPushButton("Excluir/Inativar")
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_novo.clicked.connect(self.novo_cliente)
        self.btn_editar.clicked.connect(self.editar_cliente)
        self.btn_excluir.clicked.connect(self.excluir)
        self.btn_atualizar.clicked.connect(self.carregar_clientes)

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
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Documento", "Telefone", "E-mail", "Status", "Criado em"])
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

    def carregar_clientes(self):
        termo = self.search_input.text().strip()
        self.clientes = buscar_clientes(termo) if termo else listar_clientes()
        self.table.setRowCount(len(self.clientes))
        for row_index, cliente in enumerate(self.clientes):
            valores = [
                cliente["id"], cliente["nome"], cliente["documento"], cliente["telefone"],
                cliente["email"], "Ativo" if cliente["ativo"] else "Inativo", cliente["criado_em"]
            ]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                item.setTextAlignment(Qt.AlignCenter if col in [0, 5] else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col, item)
        self.total_label.setText(f"Exibindo {len(self.clientes)} cliente(s).")

    def get_cliente(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.clientes[row]

    def novo_cliente(self):
        dialog = ClienteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "Nome é obrigatório.")
                return
            cadastrar_cliente(**data)
            self.carregar_clientes()
            QMessageBox.information(self, "Sucesso", "Cliente cadastrado.")

    def editar_cliente(self):
        cliente = self.get_cliente()
        if not cliente:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente.")
            return
        dialog = ClienteDialog(self, cliente)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "Nome é obrigatório.")
                return
            atualizar_cliente(cliente["id"], **data)
            self.carregar_clientes()
            QMessageBox.information(self, "Sucesso", "Cliente atualizado.")

    def excluir(self):
        cliente = self.get_cliente()
        if not cliente:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente.")
            return
        resposta = QMessageBox.question(self, "Confirmar", f"Excluir/inativar cliente:\n\n{cliente['nome']}?", QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            ok, inativado = excluir_cliente(cliente["id"])
            self.carregar_clientes()
            if ok and inativado:
                QMessageBox.information(self, "Sucesso", "Cliente tinha lançamentos e foi inativado.")
            elif ok:
                QMessageBox.information(self, "Sucesso", "Cliente excluído.")

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
