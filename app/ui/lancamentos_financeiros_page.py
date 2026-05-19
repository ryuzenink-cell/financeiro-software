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
    QTextEdit,
    QSpinBox,
    QFileDialog,
)
from PySide6.QtCore import Qt, QDate

from app.repositories.financeiro_repository import (
    listar_lancamentos,
    cadastrar_lancamento,
    cadastrar_lancamento_parcelado,
    atualizar_lancamento,
    excluir_lancamento,
    listar_contas_financeiras,
    listar_categorias_financeiras,
    listar_pessoas,
    marcar_lancamento_realizado,
    cancelar_lancamento,
    duplicar_lancamento,
    adicionar_anexo_lancamento,
    listar_anexos_lancamento,
)


TIPOS_LANCAMENTO = [
    ("Receita", "receita"),
    ("Despesa", "despesa"),
    ("Custo", "custo"),
    ("Transferência", "transferencia"),
]

STATUS_POR_TIPO = {
    "receita": [("Pendente", "pendente"), ("Recebido", "recebido"), ("Cancelado", "cancelado")],
    "despesa": [("Pendente", "pendente"), ("Pago", "pago"), ("Cancelado", "cancelado")],
    "custo": [("Pendente", "pendente"), ("Pago", "pago"), ("Cancelado", "cancelado")],
    "transferencia": [("Pendente", "pendente"), ("Realizada", "pago"), ("Cancelada", "cancelado")],
}

FORMAS_PAGAMENTO = [
    "Pix",
    "Dinheiro",
    "Cartão de débito",
    "Cartão de crédito",
    "Boleto",
    "Transferência",
    "Outro",
]


def formatar_moeda(valor):
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_moeda(texto):
    texto = str(texto or "0").strip().replace("R$", "").replace(".", "").replace(",", ".")
    return float(texto or 0)


def qdate_from_iso(value):
    if value:
        data = QDate.fromString(value, "yyyy-MM-dd")
        if data.isValid():
            return data
    return QDate.currentDate()


def status_label(lancamento):
    status = lancamento["status_calculado"] if "status_calculado" in lancamento.keys() else lancamento["status"]
    labels = {
        "pendente": "Pendente",
        "pago": "Pago",
        "recebido": "Recebido",
        "vencido": "Vencido",
        "cancelado": "Cancelado",
    }
    return labels.get(status, status)


class RealizarLancamentoDialog(QDialog):
    def __init__(self, parent=None, lancamento=None):
        super().__init__(parent)
        self.lancamento = lancamento
        self.contas = listar_contas_financeiras(ativas_apenas=True)

        self.setWindowTitle("Marcar como pago/recebido")
        self.setMinimumWidth(420)
        layout = QFormLayout(self)

        self.conta_combo = QComboBox()
        for conta in self.contas:
            self.conta_combo.addItem(conta["nome"], conta["id"])

        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setDisplayFormat("dd/MM/yyyy")

        self.forma_combo = QComboBox()
        self.forma_combo.setEditable(True)
        for forma in FORMAS_PAGAMENTO:
            self.forma_combo.addItem(forma)

        if lancamento and lancamento["conta_financeira_id"]:
            idx = self.conta_combo.findData(lancamento["conta_financeira_id"])
            if idx >= 0:
                self.conta_combo.setCurrentIndex(idx)
        if lancamento and lancamento["forma_pagamento"]:
            idx = self.forma_combo.findText(lancamento["forma_pagamento"])
            if idx >= 0:
                self.forma_combo.setCurrentIndex(idx)
            else:
                self.forma_combo.setEditText(lancamento["forma_pagamento"])

        if lancamento and lancamento["tipo"] != "transferencia":
            layout.addRow("Conta financeira:", self.conta_combo)
        layout.addRow("Data:", self.data_input)
        layout.addRow("Forma:", self.forma_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "conta_financeira_id": self.conta_combo.currentData(),
            "data_movimento": self.data_input.date().toString("yyyy-MM-dd"),
            "forma_pagamento": self.forma_combo.currentText().strip(),
        }


class LancamentoFinanceiroDialog(QDialog):
    def __init__(self, parent=None, lancamento=None):
        super().__init__(parent)
        self.lancamento = lancamento
        self.contas = listar_contas_financeiras(ativas_apenas=True)
        self.categorias = listar_categorias_financeiras(ativas_apenas=True)
        self.pessoas = listar_pessoas()

        self.setWindowTitle("Lançamento Financeiro")
        self.setMinimumWidth(620)

        layout = QFormLayout(self)

        self.descricao_input = QLineEdit()

        self.tipo_combo = QComboBox()
        for label, value in TIPOS_LANCAMENTO:
            self.tipo_combo.addItem(label, value)
        self.tipo_combo.currentIndexChanged.connect(self.atualizar_campos_por_tipo)

        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Ex.: 150,00")

        self.data_competencia_input = QDateEdit()
        self.data_competencia_input.setCalendarPopup(True)
        self.data_competencia_input.setDate(QDate.currentDate())
        self.data_competencia_input.setDisplayFormat("dd/MM/yyyy")

        self.data_vencimento_input = QDateEdit()
        self.data_vencimento_input.setCalendarPopup(True)
        self.data_vencimento_input.setDate(QDate.currentDate())
        self.data_vencimento_input.setDisplayFormat("dd/MM/yyyy")

        self.data_movimento_input = QDateEdit()
        self.data_movimento_input.setCalendarPopup(True)
        self.data_movimento_input.setDate(QDate.currentDate())
        self.data_movimento_input.setDisplayFormat("dd/MM/yyyy")

        self.status_combo = QComboBox()

        self.conta_combo = QComboBox()
        self.conta_combo.addItem("Selecione", None)
        for conta in self.contas:
            self.conta_combo.addItem(conta["nome"], conta["id"])

        self.conta_origem_combo = QComboBox()
        self.conta_origem_combo.addItem("Selecione", None)
        self.conta_destino_combo = QComboBox()
        self.conta_destino_combo.addItem("Selecione", None)
        for conta in self.contas:
            self.conta_origem_combo.addItem(conta["nome"], conta["id"])
            self.conta_destino_combo.addItem(conta["nome"], conta["id"])

        self.categoria_combo = QComboBox()

        self.pessoa_combo = QComboBox()

        self.forma_pagamento_combo = QComboBox()
        self.forma_pagamento_combo.setEditable(True)
        for forma in FORMAS_PAGAMENTO:
            self.forma_pagamento_combo.addItem(forma)

        self.parcelas_input = QSpinBox()
        self.parcelas_input.setMinimum(1)
        self.parcelas_input.setMaximum(120)
        self.parcelas_input.setValue(1)
        if lancamento:
            self.parcelas_input.setEnabled(False)

        self.observacoes_input = QTextEdit()
        self.observacoes_input.setFixedHeight(80)

        layout.addRow("Descrição:", self.descricao_input)
        layout.addRow("Tipo:", self.tipo_combo)
        layout.addRow("Valor total:", self.valor_input)
        layout.addRow("Data de competência:", self.data_competencia_input)
        layout.addRow("Data de vencimento:", self.data_vencimento_input)
        layout.addRow("Data de pagamento/recebimento:", self.data_movimento_input)
        layout.addRow("Status:", self.status_combo)
        layout.addRow("Conta financeira:", self.conta_combo)
        layout.addRow("Conta origem:", self.conta_origem_combo)
        layout.addRow("Conta destino:", self.conta_destino_combo)
        layout.addRow("Categoria:", self.categoria_combo)
        layout.addRow("Cliente/Fornecedor:", self.pessoa_combo)
        layout.addRow("Forma de pagamento:", self.forma_pagamento_combo)
        layout.addRow("Parcelas/recorrências:", self.parcelas_input)
        layout.addRow("Observações:", self.observacoes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if lancamento:
            tipo_index = self.tipo_combo.findData(lancamento["tipo"])
            if tipo_index >= 0:
                self.tipo_combo.setCurrentIndex(tipo_index)
        self.atualizar_campos_por_tipo()

        if lancamento:
            self.preencher_dados(lancamento)

    def atualizar_campos_por_tipo(self):
        tipo = self.tipo_combo.currentData()
        status_atual = self.status_combo.currentData()
        categoria_atual = self.categoria_combo.currentData()
        pessoa_atual = self.pessoa_combo.currentData()

        self.status_combo.clear()
        for label, value in STATUS_POR_TIPO.get(tipo, STATUS_POR_TIPO["despesa"]):
            self.status_combo.addItem(label, value)
        if status_atual:
            idx = self.status_combo.findData(status_atual)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)

        self.categoria_combo.clear()
        self.categoria_combo.addItem("Sem categoria", None)
        for categoria in self.categorias:
            if categoria["tipo"] == tipo or tipo == "transferencia":
                self.categoria_combo.addItem(categoria["nome"], categoria["id"])
        if categoria_atual:
            idx = self.categoria_combo.findData(categoria_atual)
            if idx >= 0:
                self.categoria_combo.setCurrentIndex(idx)

        self.pessoa_combo.clear()
        self.pessoa_combo.addItem("Sem vínculo", None)
        pessoa_tipo_esperado = "cliente" if tipo == "receita" else "fornecedor" if tipo in ("despesa", "custo") else None
        for pessoa in self.pessoas:
            if pessoa_tipo_esperado is None or pessoa["pessoa_tipo"] == pessoa_tipo_esperado:
                prefixo = "Cliente" if pessoa["pessoa_tipo"] == "cliente" else "Fornecedor"
                self.pessoa_combo.addItem(f"{prefixo}: {pessoa['nome']}", (pessoa["pessoa_tipo"], pessoa["id"]))
        if pessoa_atual:
            idx = self.pessoa_combo.findData(pessoa_atual)
            if idx >= 0:
                self.pessoa_combo.setCurrentIndex(idx)

        is_transferencia = tipo == "transferencia"
        self.conta_combo.setEnabled(not is_transferencia)
        self.conta_origem_combo.setEnabled(is_transferencia)
        self.conta_destino_combo.setEnabled(is_transferencia)
        self.pessoa_combo.setEnabled(not is_transferencia)

    def preencher_dados(self, lancamento):
        self.descricao_input.setText(lancamento["descricao"] or "")
        self.valor_input.setText(str(lancamento["valor"] or 0).replace(".", ","))
        self.data_competencia_input.setDate(qdate_from_iso(lancamento["data_competencia"]))
        self.data_vencimento_input.setDate(qdate_from_iso(lancamento["data_vencimento"]))
        self.data_movimento_input.setDate(qdate_from_iso(lancamento["data_movimento"]))
        self.observacoes_input.setPlainText(lancamento["observacoes"] or "")

        status_index = self.status_combo.findData(lancamento["status"])
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)

        conta_index = self.conta_combo.findData(lancamento["conta_financeira_id"])
        if conta_index >= 0:
            self.conta_combo.setCurrentIndex(conta_index)

        origem_index = self.conta_origem_combo.findData(lancamento["conta_origem_id"])
        if origem_index >= 0:
            self.conta_origem_combo.setCurrentIndex(origem_index)

        destino_index = self.conta_destino_combo.findData(lancamento["conta_destino_id"])
        if destino_index >= 0:
            self.conta_destino_combo.setCurrentIndex(destino_index)

        categoria_index = self.categoria_combo.findData(lancamento["categoria_id"])
        if categoria_index >= 0:
            self.categoria_combo.setCurrentIndex(categoria_index)

        if lancamento["pessoa_tipo"] and lancamento["pessoa_id"]:
            pessoa_index = self.pessoa_combo.findData((lancamento["pessoa_tipo"], lancamento["pessoa_id"]))
            if pessoa_index >= 0:
                self.pessoa_combo.setCurrentIndex(pessoa_index)

        forma = lancamento["forma_pagamento"] or ""
        forma_index = self.forma_pagamento_combo.findText(forma)
        if forma_index >= 0:
            self.forma_pagamento_combo.setCurrentIndex(forma_index)
        else:
            self.forma_pagamento_combo.setEditText(forma)

    def get_data(self):
        status = self.status_combo.currentData()
        data_movimento = None
        if status in ["pago", "recebido"]:
            data_movimento = self.data_movimento_input.date().toString("yyyy-MM-dd")

        pessoa_data = self.pessoa_combo.currentData()
        pessoa_tipo, pessoa_id = ("", None)
        if isinstance(pessoa_data, tuple):
            pessoa_tipo, pessoa_id = pessoa_data

        return {
            "descricao": self.descricao_input.text().strip(),
            "tipo": self.tipo_combo.currentData(),
            "valor": parse_moeda(self.valor_input.text()),
            "data_competencia": self.data_competencia_input.date().toString("yyyy-MM-dd"),
            "data_vencimento": self.data_vencimento_input.date().toString("yyyy-MM-dd"),
            "data_movimento": data_movimento,
            "status": status,
            "categoria_id": self.categoria_combo.currentData(),
            "conta_financeira_id": self.conta_combo.currentData(),
            "conta_origem_id": self.conta_origem_combo.currentData(),
            "conta_destino_id": self.conta_destino_combo.currentData(),
            "forma_pagamento": self.forma_pagamento_combo.currentText().strip(),
            "pessoa_tipo": pessoa_tipo,
            "pessoa_id": pessoa_id,
            "observacoes": self.observacoes_input.toPlainText().strip(),
            "parcelas": self.parcelas_input.value(),
        }


class LancamentosFinanceirosPage(QWidget):
    def __init__(self):
        super().__init__()
        self.lancamentos = []
        self.setup_ui()
        self.carregar_lancamentos()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(14)

        title = QLabel("Lançamentos Financeiros")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")

        subtitle = QLabel("Motor central: receitas, despesas, custos, transferências, vencimentos, pagamentos e recebimentos.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por descrição, pessoa, tipo, status, conta ou categoria...")
        self.search_input.textChanged.connect(self.carregar_lancamentos)
        self.search_input.setStyleSheet(self.input_style())

        self.btn_novo = QPushButton("Novo")
        self.btn_editar = QPushButton("Editar")
        self.btn_realizar = QPushButton("Marcar pago/recebido")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_duplicar = QPushButton("Duplicar")
        self.btn_excluir = QPushButton("Excluir")
        self.btn_anexar = QPushButton("Anexar")
        self.btn_ver_anexos = QPushButton("Ver anexos")
        self.btn_atualizar = QPushButton("Atualizar")

        self.btn_novo.clicked.connect(self.novo_lancamento)
        self.btn_editar.clicked.connect(self.editar_lancamento)
        self.btn_realizar.clicked.connect(self.marcar_realizado)
        self.btn_cancelar.clicked.connect(self.cancelar)
        self.btn_duplicar.clicked.connect(self.duplicar)
        self.btn_excluir.clicked.connect(self.excluir_lancamento)
        self.btn_anexar.clicked.connect(self.anexar_comprovante)
        self.btn_ver_anexos.clicked.connect(self.ver_anexos)
        self.btn_atualizar.clicked.connect(self.carregar_lancamentos)

        for button in [self.btn_novo, self.btn_editar, self.btn_realizar, self.btn_cancelar, self.btn_duplicar, self.btn_excluir, self.btn_anexar, self.btn_ver_anexos, self.btn_atualizar]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(self.button_style())

        top_bar.addWidget(self.search_input)
        for button in [self.btn_novo, self.btn_editar, self.btn_realizar, self.btn_cancelar, self.btn_duplicar, self.btn_excluir, self.btn_anexar, self.btn_ver_anexos, self.btn_atualizar]:
            top_bar.addWidget(button)

        filters_bar = QHBoxLayout()
        self.tipo_filter = QComboBox()
        self.tipo_filter.addItem("Todos os tipos", None)
        for label, value in TIPOS_LANCAMENTO:
            self.tipo_filter.addItem(label, value)
        self.tipo_filter.currentIndexChanged.connect(self.carregar_lancamentos)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos os status", None)
        self.status_filter.addItem("Pendente", "pendente")
        self.status_filter.addItem("Vencido", "vencido")
        self.status_filter.addItem("Pago", "pago")
        self.status_filter.addItem("Recebido", "recebido")
        self.status_filter.addItem("Cancelado", "cancelado")
        self.status_filter.currentIndexChanged.connect(self.carregar_lancamentos)

        self.campo_data_filter = QComboBox()
        self.campo_data_filter.addItem("Competência", "data_competencia")
        self.campo_data_filter.addItem("Vencimento", "data_vencimento")
        self.campo_data_filter.addItem("Movimento", "data_movimento")
        self.campo_data_filter.currentIndexChanged.connect(self.carregar_lancamentos)

        self.data_inicio_filter = QDateEdit()
        self.data_inicio_filter.setCalendarPopup(True)
        self.data_inicio_filter.setDate(QDate.currentDate().addMonths(-1))
        self.data_inicio_filter.setDisplayFormat("dd/MM/yyyy")
        self.data_inicio_filter.dateChanged.connect(self.carregar_lancamentos)

        self.data_fim_filter = QDateEdit()
        self.data_fim_filter.setCalendarPopup(True)
        self.data_fim_filter.setDate(QDate.currentDate().addMonths(1))
        self.data_fim_filter.setDisplayFormat("dd/MM/yyyy")
        self.data_fim_filter.dateChanged.connect(self.carregar_lancamentos)

        self.btn_limpar = QPushButton("Limpar filtros")
        self.btn_limpar.setStyleSheet(self.secondary_button_style())
        self.btn_limpar.clicked.connect(self.limpar_filtros)

        filters_bar.addWidget(QLabel("Tipo:"))
        filters_bar.addWidget(self.tipo_filter)
        filters_bar.addWidget(QLabel("Status:"))
        filters_bar.addWidget(self.status_filter)
        filters_bar.addWidget(QLabel("Data:"))
        filters_bar.addWidget(self.campo_data_filter)
        filters_bar.addWidget(QLabel("De:"))
        filters_bar.addWidget(self.data_inicio_filter)
        filters_bar.addWidget(QLabel("Até:"))
        filters_bar.addWidget(self.data_fim_filter)
        filters_bar.addWidget(self.btn_limpar)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #4b5563; font-size: 14px;")

        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "ID", "Comp.", "Venc.", "Mov.", "Tipo", "Descrição", "Categoria", "Pessoa", "Conta", "Origem", "Destino", "Status", "Valor"
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
        main_layout.addLayout(filters_bar)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(self.table)

        self.setStyleSheet("QWidget { background-color: #ffffff; color: #111827; }")

    def montar_filtros(self):
        return {
            "tipo": self.tipo_filter.currentData(),
            "status": self.status_filter.currentData(),
            "campo_data": self.campo_data_filter.currentData(),
            "data_inicio": self.data_inicio_filter.date().toString("yyyy-MM-dd"),
            "data_fim": self.data_fim_filter.date().toString("yyyy-MM-dd"),
        }

    def carregar_lancamentos(self):
        termo = self.search_input.text().strip()
        self.lancamentos = listar_lancamentos(limite=1000, termo=termo, filtros=self.montar_filtros())
        self.table.setRowCount(len(self.lancamentos))

        total_entradas = 0.0
        total_saidas = 0.0
        for row_index, lancamento in enumerate(self.lancamentos):
            if lancamento["tipo"] == "receita":
                total_entradas += float(lancamento["valor"] or 0)
            elif lancamento["tipo"] in ("despesa", "custo"):
                total_saidas += float(lancamento["valor"] or 0)

            valores = [
                lancamento["id"],
                lancamento["data_competencia"],
                lancamento["data_vencimento"] or "",
                lancamento["data_movimento"] or "",
                lancamento["tipo"],
                lancamento["descricao"],
                lancamento["categoria_nome"] or "",
                lancamento["pessoa_nome"] or "",
                lancamento["conta_nome"] or "",
                lancamento["conta_origem_nome"] or "",
                lancamento["conta_destino_nome"] or "",
                status_label(lancamento),
                formatar_moeda(lancamento["valor"]),
            ]

            for col_index, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                item.setTextAlignment(Qt.AlignCenter if col_index in [0, 1, 2, 3, 4, 11, 12] else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col_index, item)

        resultado = total_entradas - total_saidas
        self.total_label.setText(
            f"Exibindo {len(self.lancamentos)} lançamento(s). Entradas: {formatar_moeda(total_entradas)} | "
            f"Saídas: {formatar_moeda(total_saidas)} | Resultado: {formatar_moeda(resultado)}"
        )

    def limpar_filtros(self):
        self.search_input.clear()
        self.tipo_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.campo_data_filter.setCurrentIndex(0)
        self.data_inicio_filter.setDate(QDate.currentDate().addYears(-10))
        self.data_fim_filter.setDate(QDate.currentDate().addYears(10))
        self.carregar_lancamentos()

    def get_lancamento_selecionado(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None
        return self.lancamentos[selected_row]

    def novo_lancamento(self):
        if not listar_contas_financeiras(ativas_apenas=True):
            QMessageBox.warning(self, "Atenção", "Cadastre uma conta financeira antes de criar lançamentos.")
            return

        dialog = LancamentoFinanceiroDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            parcelas = data.pop("parcelas", 1)
            if not self.validar_lancamento(data):
                return
            if parcelas > 1:
                cadastrar_lancamento_parcelado(parcelas=parcelas, **data)
            else:
                cadastrar_lancamento(**data)
            self.carregar_lancamentos()
            QMessageBox.information(self, "Sucesso", "Lançamento cadastrado com sucesso.")

    def editar_lancamento(self):
        lancamento = self.get_lancamento_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um lançamento para editar.")
            return

        dialog = LancamentoFinanceiroDialog(self, lancamento)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            data.pop("parcelas", None)
            if not self.validar_lancamento(data):
                return
            atualizar_lancamento(lancamento["id"], **data)
            self.carregar_lancamentos()
            QMessageBox.information(self, "Sucesso", "Lançamento atualizado com sucesso.")

    def marcar_realizado(self):
        lancamento = self.get_lancamento_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um lançamento.")
            return
        if lancamento["status"] in ["pago", "recebido"]:
            QMessageBox.information(self, "Informação", "Este lançamento já está realizado.")
            return
        if lancamento["status"] == "cancelado":
            QMessageBox.warning(self, "Atenção", "Lançamento cancelado não pode ser realizado.")
            return

        dialog = RealizarLancamentoDialog(self, lancamento)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            marcar_lancamento_realizado(lancamento["id"], **data)
            self.carregar_lancamentos()
            QMessageBox.information(self, "Sucesso", "Lançamento marcado como realizado.")

    def cancelar(self):
        lancamento = self.get_lancamento_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um lançamento.")
            return
        resposta = QMessageBox.question(self, "Confirmar", f"Cancelar o lançamento:\n\n{lancamento['descricao']}?", QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            cancelar_lancamento(lancamento["id"])
            self.carregar_lancamentos()
            QMessageBox.information(self, "Sucesso", "Lançamento cancelado.")

    def duplicar(self):
        lancamento = self.get_lancamento_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um lançamento para duplicar.")
            return
        duplicar_lancamento(lancamento["id"])
        self.carregar_lancamentos()
        QMessageBox.information(self, "Sucesso", "Lançamento duplicado como pendente.")


    def anexar_comprovante(self):
        lancamento = self.get_lancamento_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um lançamento para anexar comprovante.")
            return
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar comprovante",
            "",
            "Arquivos (*.pdf *.png *.jpg *.jpeg *.webp *.txt *.docx *.xlsx);;Todos os arquivos (*.*)"
        )
        if arquivo:
            adicionar_anexo_lancamento(lancamento["id"], arquivo, tipo="comprovante")
            QMessageBox.information(self, "Sucesso", "Comprovante/anexo vinculado ao lançamento.")

    def ver_anexos(self):
        lancamento = self.get_lancamento_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um lançamento para ver anexos.")
            return
        anexos = listar_anexos_lancamento(lancamento["id"])
        if not anexos:
            QMessageBox.information(self, "Anexos", "Este lançamento ainda não possui anexos.")
            return
        texto = "\n".join([f"{a['criado_em']} - {a['caminho_arquivo']}" for a in anexos])
        QMessageBox.information(self, "Anexos do lançamento", texto)

    def excluir_lancamento(self):
        lancamento = self.get_lancamento_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um lançamento para excluir.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o lançamento:\n\n{lancamento['descricao']}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta == QMessageBox.Yes:
            excluir_lancamento(lancamento["id"])
            self.carregar_lancamentos()
            QMessageBox.information(self, "Sucesso", "Lançamento excluído com sucesso.")

    def validar_lancamento(self, data):
        if not data["descricao"]:
            QMessageBox.warning(self, "Atenção", "A descrição é obrigatória.")
            return False
        if data["valor"] <= 0:
            QMessageBox.warning(self, "Atenção", "O valor precisa ser maior que zero.")
            return False
        if data["tipo"] == "transferencia":
            if not data["conta_origem_id"] or not data["conta_destino_id"]:
                QMessageBox.warning(self, "Atenção", "Transferência precisa de conta origem e conta destino.")
                return False
            if data["conta_origem_id"] == data["conta_destino_id"]:
                QMessageBox.warning(self, "Atenção", "Conta origem e destino não podem ser iguais.")
                return False
        else:
            if not data["conta_financeira_id"] and data["status"] in ["pago", "recebido"]:
                QMessageBox.warning(self, "Atenção", "Lançamentos realizados precisam de uma conta financeira.")
                return False
        return True

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
                padding: 9px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """

    def secondary_button_style(self):
        return """
            QPushButton {
                background-color: #f3f4f6;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e5e7eb; }
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
