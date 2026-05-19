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
    QHeaderView
)
from PySide6.QtCore import Qt

from app.repositories.fornecedor_repository import (
    listar_fornecedores,
    buscar_fornecedores,
    cadastrar_fornecedor,
    atualizar_fornecedor,
    excluir_fornecedor,
    contar_fornecedores
)


class FornecedorDialog(QDialog):
    def __init__(self, parent=None, fornecedor=None):
        super().__init__(parent)

        self.fornecedor = fornecedor

        self.setWindowTitle("Fornecedor")
        self.setMinimumWidth(420)

        layout = QFormLayout(self)

        self.nome_input = QLineEdit()
        self.documento_input = QLineEdit()
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()

        layout.addRow("Nome:", self.nome_input)
        layout.addRow("Documento:", self.documento_input)
        layout.addRow("Telefone:", self.telefone_input)
        layout.addRow("E-mail:", self.email_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        if fornecedor:
            self.nome_input.setText(fornecedor["nome"] or "")
            self.documento_input.setText(fornecedor["documento"] or "")
            self.telefone_input.setText(fornecedor["telefone"] or "")
            self.email_input.setText(fornecedor["email"] or "")

    def get_data(self):
        return {
            "nome": self.nome_input.text().strip(),
            "documento": self.documento_input.text().strip(),
            "telefone": self.telefone_input.text().strip(),
            "email": self.email_input.text().strip(),
        }


class FornecedoresPage(QWidget):
    def __init__(self):
        super().__init__()

        self.fornecedores = []

        self.setup_ui()
        self.carregar_fornecedores()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Fornecedores")
        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #111827;
        """)

        subtitle = QLabel("Cadastro, consulta, edição e exclusão de fornecedores.")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #4b5563;
        """)

        top_bar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nome, documento, telefone ou e-mail...")
        self.search_input.textChanged.connect(self.carregar_fornecedores)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
        """)

        self.btn_novo = QPushButton("Novo")
        self.btn_editar = QPushButton("Editar")
        self.btn_excluir = QPushButton("Excluir")
        self.btn_atualizar = QPushButton("Atualizar")

        self.btn_novo.clicked.connect(self.novo_fornecedor)
        self.btn_editar.clicked.connect(self.editar_fornecedor)
        self.btn_excluir.clicked.connect(self.excluir_fornecedor)
        self.btn_atualizar.clicked.connect(self.carregar_fornecedores)

        for button in [
            self.btn_novo,
            self.btn_editar,
            self.btn_excluir,
            self.btn_atualizar
        ]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #111827;
                    color: white;
                    padding: 10px 16px;
                    border-radius: 8px;
                    font-size: 14px;
                    border: none;
                }

                QPushButton:hover {
                    background-color: #1f2937;
                }

                QPushButton:pressed {
                    background-color: #374151;
                }
            """)

        self.btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #991b1b;
                color: white;
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 14px;
                border: none;
            }

            QPushButton:hover {
                background-color: #7f1d1d;
            }
        """)

        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.btn_novo)
        top_bar.addWidget(self.btn_editar)
        top_bar.addWidget(self.btn_excluir)
        top_bar.addWidget(self.btn_atualizar)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("""
            color: #4b5563;
            font-size: 14px;
        """)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nome",
            "Documento",
            "Telefone",
            "E-mail",
            "Criado em"
        ])

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9fafb;
                color: #111827;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                gridline-color: #e5e7eb;
                font-size: 14px;
            }

            QHeaderView::section {
                background-color: #f9fafb;
                color: #111827;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e5e7eb;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 8px;
                background-color: transparent;
                color: #111827;
            }

            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #111827;
            }
        """)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(self.table)

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #111827;
            }

            QLabel {
                background-color: #ffffff;
                color: #111827;
            }
        """)

    def carregar_fornecedores(self):
        termo = self.search_input.text().strip()

        if termo:
            self.fornecedores = buscar_fornecedores(termo, limite=300, offset=0)
        else:
            self.fornecedores = listar_fornecedores(limite=300, offset=0)

        self.table.setRowCount(len(self.fornecedores))

        for row_index, fornecedor in enumerate(self.fornecedores):
            valores = [
                fornecedor["id"],
                fornecedor["nome"],
                fornecedor["documento"],
                fornecedor["telefone"],
                fornecedor["email"],
                fornecedor["criado_em"],
            ]

            for col_index, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

                if col_index == 0:
                    item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(row_index, col_index, item)

        total_geral = contar_fornecedores()

        if termo:
            self.total_label.setText(
                f"{len(self.fornecedores)} resultado(s) encontrado(s) | Total geral: {total_geral}"
            )
        else:
            self.total_label.setText(
                f"Exibindo {len(self.fornecedores)} fornecedor(es) | Total geral: {total_geral}"
            )

    def get_fornecedor_selecionado(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            return None

        return self.fornecedores[selected_row]

    def novo_fornecedor(self):
        dialog = FornecedorDialog(self)

        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()

            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "O nome do fornecedor é obrigatório.")
                return

            cadastrar_fornecedor(
                nome=data["nome"],
                documento=data["documento"],
                telefone=data["telefone"],
                email=data["email"]
            )

            self.carregar_fornecedores()
            QMessageBox.information(self, "Sucesso", "Fornecedor cadastrado com sucesso.")

    def editar_fornecedor(self):
        fornecedor = self.get_fornecedor_selecionado()

        if not fornecedor:
            QMessageBox.warning(self, "Atenção", "Selecione um fornecedor para editar.")
            return

        dialog = FornecedorDialog(self, fornecedor)

        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()

            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "O nome do fornecedor é obrigatório.")
                return

            atualizar_fornecedor(
                id_fornecedor=fornecedor["id"],
                nome=data["nome"],
                documento=data["documento"],
                telefone=data["telefone"],
                email=data["email"]
            )

            self.carregar_fornecedores()
            QMessageBox.information(self, "Sucesso", "Fornecedor atualizado com sucesso.")

    def excluir_fornecedor(self):
        fornecedor = self.get_fornecedor_selecionado()

        if not fornecedor:
            QMessageBox.warning(self, "Atenção", "Selecione um fornecedor para excluir.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o fornecedor:\n\n{fornecedor['nome']}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta == QMessageBox.Yes:
            ok, inativado = excluir_fornecedor(fornecedor["id"])
            self.carregar_fornecedores()
            if ok and inativado:
                QMessageBox.information(self, "Sucesso", "Fornecedor tinha lançamentos e foi inativado.")
            elif ok:
                QMessageBox.information(self, "Sucesso", "Fornecedor excluído com sucesso.")