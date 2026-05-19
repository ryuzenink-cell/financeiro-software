from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDialog
)
from PySide6.QtCore import Qt

from app.repositories.financeiro_repository import (
    listar_contas_a_pagar,
    listar_contas_a_receber,
    marcar_lancamento_realizado,
    cancelar_lancamento,
)
from app.ui.lancamentos_financeiros_page import formatar_moeda, status_label, RealizarLancamentoDialog


class BaseContasPage(QWidget):
    titulo = "Contas"
    subtitulo = ""
    tipo_conta = "pagar"

    def __init__(self):
        super().__init__()
        self.registros = []
        self.setup_ui()
        self.carregar()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel(self.titulo)
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")
        subtitle = QLabel(self.subtitulo)
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por descrição, pessoa, conta ou categoria...")
        self.search_input.textChanged.connect(self.carregar)
        self.search_input.setStyleSheet(self.input_style())

        self.btn_realizar = QPushButton("Marcar como pago" if self.tipo_conta == "pagar" else "Marcar como recebido")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_realizar.clicked.connect(self.marcar_realizado)
        self.btn_cancelar.clicked.connect(self.cancelar)
        self.btn_atualizar.clicked.connect(self.carregar)

        for button in [self.btn_realizar, self.btn_cancelar, self.btn_atualizar]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(self.button_style())

        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.btn_realizar)
        top_bar.addWidget(self.btn_cancelar)
        top_bar.addWidget(self.btn_atualizar)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #4b5563; font-size: 14px;")

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Vencimento", "Status", "Descrição", "Pessoa", "Categoria", "Conta", "Valor", "Forma"
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

    def carregar(self):
        termo = self.search_input.text().strip()
        self.registros = listar_contas_a_pagar(termo) if self.tipo_conta == "pagar" else listar_contas_a_receber(termo)
        self.table.setRowCount(len(self.registros))
        total = 0.0
        vencido = 0.0
        for row_index, lancamento in enumerate(self.registros):
            valor = float(lancamento["valor"] or 0)
            total += valor
            if (lancamento["status_calculado"] if "status_calculado" in lancamento.keys() else lancamento["status"]) == "vencido":
                vencido += valor
            valores = [
                lancamento["id"],
                lancamento["data_vencimento"] or "",
                status_label(lancamento),
                lancamento["descricao"],
                lancamento["pessoa_nome"] or "",
                lancamento["categoria_nome"] or "",
                lancamento["conta_nome"] or "",
                formatar_moeda(valor),
                lancamento["forma_pagamento"] or "",
            ]
            for col_index, valor_item in enumerate(valores):
                item = QTableWidgetItem(str(valor_item) if valor_item is not None else "")
                item.setTextAlignment(Qt.AlignCenter if col_index in [0, 1, 2, 7] else Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_index, col_index, item)
        self.total_label.setText(
            f"Exibindo {len(self.registros)} registro(s). Total pendente: {formatar_moeda(total)} | Vencido: {formatar_moeda(vencido)}"
        )

    def get_selecionado(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None
        return self.registros[selected_row]

    def marcar_realizado(self):
        lancamento = self.get_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um registro.")
            return
        dialog = RealizarLancamentoDialog(self, lancamento)
        if dialog.exec() == QDialog.Accepted:
            marcar_lancamento_realizado(lancamento["id"], **dialog.get_data())
            self.carregar()
            QMessageBox.information(self, "Sucesso", "Registro atualizado com sucesso.")

    def cancelar(self):
        lancamento = self.get_selecionado()
        if not lancamento:
            QMessageBox.warning(self, "Atenção", "Selecione um registro.")
            return
        resposta = QMessageBox.question(self, "Confirmar", f"Cancelar:\n\n{lancamento['descricao']}?", QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            cancelar_lancamento(lancamento["id"])
            self.carregar()
            QMessageBox.information(self, "Sucesso", "Registro cancelado.")

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


class ContasPagarPage(BaseContasPage):
    titulo = "Contas a Pagar"
    subtitulo = "Despesas e custos pendentes gerados automaticamente pelos lançamentos financeiros."
    tipo_conta = "pagar"


class ContasReceberPage(BaseContasPage):
    titulo = "Contas a Receber"
    subtitulo = "Receitas pendentes geradas automaticamente pelos lançamentos financeiros."
    tipo_conta = "receber"
