from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QSizePolicy
from PySide6.QtCore import Qt

from app.repositories.financeiro_repository import obter_resumo_dashboard, listar_contas_financeiras
from app.ui.lancamentos_financeiros_page import formatar_moeda


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cards = {}
        self.setup_ui()
        self.carregar_resumo()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")
        subtitle = QLabel("Resumo gerencial do sistema financeiro: competência, caixa, pendências e saldo.")
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        self.periodo_label = QLabel()
        self.periodo_label.setStyleSheet("font-size: 14px; color: #6b7280;")

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setContentsMargins(0, 0, 0, 0)

        card_defs = [
            ("receitas_competencia", "Receitas por competência"),
            ("custos_competencia", "Custos por competência"),
            ("despesas_competencia", "Despesas por competência"),
            ("resultado_competencia", "Resultado por competência"),
            ("receitas_realizadas", "Entradas realizadas"),
            ("saidas_realizadas", "Saídas realizadas"),
            ("resultado_realizado", "Resultado de caixa"),
            ("saldo_total", "Saldo total em contas"),
            ("receitas_pendentes", "A receber no mês"),
            ("saidas_pendentes", "A pagar no mês"),
            ("receber_7_dias", "Receber em 7 dias"),
            ("pagar_7_dias", "Pagar em 7 dias"),
            ("receber_vencido", "Recebíveis vencidos"),
            ("pagar_vencido", "Pagáveis vencidos"),
            ("total_pendentes", "Lançamentos pendentes"),
            ("total_contas", "Contas ativas"),
        ]

        for idx, (key, label) in enumerate(card_defs):
            card = self.create_card(label)
            self.cards[key] = card["value"]
            grid.addWidget(card["frame"], idx // 4, idx % 4)

        self.insights = QLabel()
        self.insights.setWordWrap(True)
        self.insights.setStyleSheet("font-size: 15px; color: #111827; padding: 14px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px;")

        self.contas_label = QLabel()
        self.contas_label.setWordWrap(True)
        self.contas_label.setStyleSheet("font-size: 14px; color: #374151; padding: 14px; background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px;")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(self.periodo_label)
        main_layout.addLayout(grid)
        main_layout.addWidget(self.insights)
        main_layout.addWidget(self.contas_label)
        main_layout.addStretch()

        self.setStyleSheet("QWidget { background-color: #f3f4f6; color: #111827; }")

    def create_card(self, label_text):
        frame = QFrame()
        frame.setMinimumHeight(104)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(6)

        label = QLabel(label_text)
        label.setMinimumHeight(20)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        label.setStyleSheet("font-size: 13px; color: #6b7280; background: transparent; border: none;")

        value = QLabel("-")
        value.setMinimumHeight(42)
        value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value.setStyleSheet("font-size: 24px; font-weight: 700; color: #111827; background: transparent; border: none; padding-top: 2px; padding-bottom: 2px;")

        layout.addWidget(label)
        layout.addWidget(value)
        layout.addStretch(1)
        return {"frame": frame, "value": value}

    def carregar_resumo(self):
        resumo = obter_resumo_dashboard()
        self.periodo_label.setText(f"Período atual: {resumo['periodo']}")

        money_keys = {
            "receitas_competencia", "custos_competencia", "despesas_competencia", "resultado_competencia",
            "receitas_realizadas", "saidas_realizadas", "resultado_realizado", "saldo_total",
            "receitas_pendentes", "saidas_pendentes", "receber_7_dias", "pagar_7_dias",
            "receber_vencido", "pagar_vencido"
        }
        for key, widget in self.cards.items():
            value = resumo.get(key, 0)
            widget.setText(formatar_moeda(value) if key in money_keys else str(value or 0))

            # Destaque visual sem prejudicar leitura.
            if key in {"resultado_competencia", "resultado_realizado", "saldo_total"}:
                try:
                    numero = float(value or 0)
                except (TypeError, ValueError):
                    numero = 0

                cor = "#166534" if numero > 0 else "#991b1b" if numero < 0 else "#111827"
                widget.setStyleSheet(
                    f"font-size: 24px; font-weight: 700; color: {cor}; "
                    "background: transparent; border: none; padding-top: 2px; padding-bottom: 2px;"
                )

        self.insights.setText(
            f"Maior categoria de saída no mês: {resumo['maior_categoria_nome']} ({formatar_moeda(resumo['maior_categoria_total'])}). "
            f"Maior despesa/custo individual: {resumo['maior_despesa_descricao']} ({formatar_moeda(resumo['maior_despesa_valor'])}). "
            "Use estes indicadores para comparar competência x caixa e evitar falta de dinheiro no curto prazo."
        )

        contas = listar_contas_financeiras(ativas_apenas=True)
        if contas:
            partes = [f"{conta['nome']}: {formatar_moeda(conta['saldo_atual'])}" for conta in contas[:8]]
            self.contas_label.setText("Saldos por conta: " + " | ".join(partes))
        else:
            self.contas_label.setText("Nenhuma conta financeira ativa cadastrada.")
