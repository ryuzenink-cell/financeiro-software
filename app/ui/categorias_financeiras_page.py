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
)
from PySide6.QtCore import Qt

from app.repositories.financeiro_repository import (
    listar_categorias_financeiras,
    buscar_categorias_financeiras,
    cadastrar_categoria_financeira,
    atualizar_categoria_financeira,
    excluir_categoria_financeira,
    listar_plano_contas,
    restaurar_categorias_padrao_financeiras,
)


TIPOS_CATEGORIA = [
    ("Receita", "receita"),
    ("Despesa", "despesa"),
    ("Custo", "custo"),
    ("Transferência", "transferencia"),
]

GRUPOS_DRE = [
    "Receita Bruta",
    "Deduções/Impostos",
    "CMV/CSP",
    "Lucro Bruto",
    "Despesas Fixas",
    "Despesas Variáveis",
    "Despesas Comerciais",
    "Despesas Administrativas",
    "Retiradas",
    "Outras Receitas",
    "Não se aplica",
    "Outros",
]

GRUPOS_DFC = [
    "Operacional",
    "Investimento",
    "Financiamento",
    "Não se aplica",
]

GRUPOS_BP = [
    "Caixa/Bancos",
    "Contas a receber",
    "Estoque",
    "Ativo Imobilizado",
    "Contas a pagar",
    "Impostos a pagar",
    "Empréstimos",
    "Patrimônio Líquido",
    "Resultado",
    "Não se aplica",
]

NATUREZAS = [
    ("Crédito / aumenta resultado", "credito"),
    ("Débito / reduz resultado", "debito"),
    ("Neutra", "neutra"),
]


class CategoriaFinanceiraDialog(QDialog):
    def __init__(self, parent=None, categoria=None):
        super().__init__(parent)
        self.categoria = categoria
        self.plano_contas = listar_plano_contas()

        self.setWindowTitle("Categoria Financeira")
        self.setMinimumWidth(560)

        layout = QFormLayout(self)

        self.nome_input = QLineEdit()

        self.tipo_combo = QComboBox()
        for label, value in TIPOS_CATEGORIA:
            self.tipo_combo.addItem(label, value)

        self.grupo_dre_combo = QComboBox()
        self.grupo_dre_combo.setEditable(True)
        for grupo in GRUPOS_DRE:
            self.grupo_dre_combo.addItem(grupo)

        self.grupo_dfc_combo = QComboBox()
        self.grupo_dfc_combo.setEditable(True)
        for grupo in GRUPOS_DFC:
            self.grupo_dfc_combo.addItem(grupo)

        self.grupo_bp_combo = QComboBox()
        self.grupo_bp_combo.setEditable(True)
        for grupo in GRUPOS_BP:
            self.grupo_bp_combo.addItem(grupo)

        self.natureza_combo = QComboBox()
        for label, value in NATUREZAS:
            self.natureza_combo.addItem(label, value)

        self.plano_conta_combo = QComboBox()
        self.plano_conta_combo.addItem("Sem vínculo direto", None)
        for conta in self.plano_contas:
            self.plano_conta_combo.addItem(f"{conta['codigo']} - {conta['nome']}", conta["id"])

        self.incluir_combo = QComboBox()
        self.incluir_combo.addItem("Sim", 1)
        self.incluir_combo.addItem("Não", 0)

        self.observacoes_input = QLineEdit()

        self.ativo_combo = QComboBox()
        self.ativo_combo.addItem("Ativa", 1)
        self.ativo_combo.addItem("Inativa", 0)

        layout.addRow("Nome:", self.nome_input)
        layout.addRow("Tipo:", self.tipo_combo)
        layout.addRow("Grupo DRE:", self.grupo_dre_combo)
        layout.addRow("Grupo DFC:", self.grupo_dfc_combo)
        layout.addRow("Grupo BP:", self.grupo_bp_combo)
        layout.addRow("Natureza:", self.natureza_combo)
        layout.addRow("Plano de contas:", self.plano_conta_combo)
        layout.addRow("Entrar em relatórios:", self.incluir_combo)
        layout.addRow("Observações:", self.observacoes_input)
        layout.addRow("Status:", self.ativo_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if categoria:
            self.preencher_dados(categoria)

    def _set_combo_text(self, combo, text):
        text = text or ""
        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setEditText(text)

    def preencher_dados(self, categoria):
        self.nome_input.setText(categoria["nome"] or "")
        self.observacoes_input.setText(categoria["observacoes"] or "")

        tipo_index = self.tipo_combo.findData(categoria["tipo"])
        if tipo_index >= 0:
            self.tipo_combo.setCurrentIndex(tipo_index)

        self._set_combo_text(self.grupo_dre_combo, categoria["grupo_dre"])
        self._set_combo_text(self.grupo_dfc_combo, categoria["grupo_dfc"])
        self._set_combo_text(self.grupo_bp_combo, categoria["grupo_bp"])

        natureza_index = self.natureza_combo.findData(categoria["natureza"])
        if natureza_index >= 0:
            self.natureza_combo.setCurrentIndex(natureza_index)

        plano_index = self.plano_conta_combo.findData(categoria["plano_conta_id"])
        if plano_index >= 0:
            self.plano_conta_combo.setCurrentIndex(plano_index)

        incluir_index = self.incluir_combo.findData(categoria["incluir_relatorios"])
        if incluir_index >= 0:
            self.incluir_combo.setCurrentIndex(incluir_index)

        ativo_index = self.ativo_combo.findData(categoria["ativo"])
        if ativo_index >= 0:
            self.ativo_combo.setCurrentIndex(ativo_index)

    def get_data(self):
        return {
            "nome": self.nome_input.text().strip(),
            "tipo": self.tipo_combo.currentData(),
            "grupo_dre": self.grupo_dre_combo.currentText().strip(),
            "grupo_dfc": self.grupo_dfc_combo.currentText().strip(),
            "grupo_bp": self.grupo_bp_combo.currentText().strip(),
            "natureza": self.natureza_combo.currentData(),
            "plano_conta_id": self.plano_conta_combo.currentData(),
            "incluir_relatorios": self.incluir_combo.currentData(),
            "observacoes": self.observacoes_input.text().strip(),
            "ativo": self.ativo_combo.currentData(),
        }


class CategoriasFinanceirasPage(QWidget):
    def __init__(self):
        super().__init__()
        self.categorias = []
        self.setup_ui()
        self.carregar_categorias()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Categorias Financeiras")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")

        subtitle = QLabel("Classifique lançamentos para alimentar DRE, BP, DFC, fluxo de caixa e relatórios gerenciais.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nome, tipo, grupo DRE/DFC/BP...")
        self.search_input.textChanged.connect(self.carregar_categorias)
        self.search_input.setStyleSheet(self.input_style())

        self.btn_novo = QPushButton("Nova")
        self.btn_editar = QPushButton("Editar")
        self.btn_excluir = QPushButton("Excluir/Inativar")
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_restaurar = QPushButton("Restaurar padrões")

        self.btn_novo.clicked.connect(self.nova_categoria)
        self.btn_editar.clicked.connect(self.editar_categoria)
        self.btn_excluir.clicked.connect(self.excluir_categoria)
        self.btn_atualizar.clicked.connect(self.carregar_categorias)
        self.btn_restaurar.clicked.connect(self.restaurar_padroes)

        for button in [self.btn_novo, self.btn_editar, self.btn_excluir, self.btn_atualizar, self.btn_restaurar]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(self.button_style())

        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.btn_novo)
        top_bar.addWidget(self.btn_editar)
        top_bar.addWidget(self.btn_excluir)
        top_bar.addWidget(self.btn_atualizar)
        top_bar.addWidget(self.btn_restaurar)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #4b5563; font-size: 14px;")

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Tipo", "Grupo DRE", "Grupo DFC", "Grupo BP", "Natureza", "Relatórios", "Status"
        ])
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

    def carregar_categorias(self):
        termo = self.search_input.text().strip()
        self.categorias = buscar_categorias_financeiras(termo) if termo else listar_categorias_financeiras()
        self.table.setRowCount(len(self.categorias))

        for row_index, categoria in enumerate(self.categorias):
            valores = [
                categoria["id"],
                categoria["nome"],
                categoria["tipo"],
                categoria["grupo_dre"],
                categoria["grupo_dfc"],
                categoria["grupo_bp"],
                categoria["natureza"],
                "Sim" if categoria["incluir_relatorios"] else "Não",
                "Ativa" if categoria["ativo"] else "Inativa",
            ]
            for col_index, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                item.setTextAlignment(Qt.AlignCenter if col_index in [0, 2, 6, 7, 8] else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col_index, item)

        self.total_label.setText(f"Exibindo {len(self.categorias)} categoria(s) financeira(s).")

    def get_categoria_selecionada(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None
        return self.categorias[selected_row]

    def nova_categoria(self):
        dialog = CategoriaFinanceiraDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "O nome da categoria é obrigatório.")
                return
            cadastrar_categoria_financeira(**data)
            self.carregar_categorias()
            QMessageBox.information(self, "Sucesso", "Categoria cadastrada com sucesso.")

    def editar_categoria(self):
        categoria = self.get_categoria_selecionada()
        if not categoria:
            QMessageBox.warning(self, "Atenção", "Selecione uma categoria para editar.")
            return

        dialog = CategoriaFinanceiraDialog(self, categoria)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Atenção", "O nome da categoria é obrigatório.")
                return
            atualizar_categoria_financeira(categoria["id"], **data)
            self.carregar_categorias()
            QMessageBox.information(self, "Sucesso", "Categoria atualizada com sucesso.")

    def excluir_categoria(self):
        categoria = self.get_categoria_selecionada()
        if not categoria:
            QMessageBox.warning(self, "Atenção", "Selecione uma categoria para excluir ou inativar.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar",
            f"Deseja excluir/inativar a categoria:\n\n{categoria['nome']}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta == QMessageBox.Yes:
            ok, inativada = excluir_categoria_financeira(categoria["id"])
            self.carregar_categorias()
            if ok and inativada:
                QMessageBox.information(self, "Sucesso", "A categoria tinha lançamentos e foi inativada.")
            elif ok:
                QMessageBox.information(self, "Sucesso", "Categoria excluída com sucesso.")


    def restaurar_padroes(self):
        resposta = QMessageBox.question(
            self,
            "Restaurar categorias padrão",
            "Deseja recriar e reativar as categorias financeiras padrão para DRE, BP, DFC e fluxo de caixa?\n\n"
            "As categorias personalizadas não serão apagadas.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta != QMessageBox.Yes:
            return

        inseridas, atualizadas = restaurar_categorias_padrao_financeiras()
        self.carregar_categorias()
        QMessageBox.information(
            self,
            "Categorias restauradas",
            f"Categorias padrão inseridas: {inseridas}\nCategorias padrão reativadas/atualizadas: {atualizadas}"
        )

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
