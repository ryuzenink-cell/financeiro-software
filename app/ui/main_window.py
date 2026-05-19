from app.ui.dashboard_page import DashboardPage
from app.ui.fornecedores_page import FornecedoresPage
from app.ui.clientes_page import ClientesPage
from app.ui.contas_financeiras_page import ContasFinanceirasPage
from app.ui.categorias_financeiras_page import CategoriasFinanceirasPage
from app.ui.lancamentos_financeiros_page import LancamentosFinanceirosPage
from app.ui.contas_pagar_receber_page import ContasPagarPage, ContasReceberPage
from app.ui.fluxo_caixa_page import FluxoCaixaPage
from app.ui.relatorios_basicos_page import RelatoriosBasicosPage
from app.ui.conciliacao_page import ConciliacaoPage
from app.ui.empresa_page import EmpresaPage

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QStackedWidget,
    QToolBar,
    QMenu,
    QStatusBar,
    QSizePolicy,
    QStyle,
    QToolButton,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Financeiro Software")
        self.setMinimumSize(1200, 720)

        self.setup_ui()
        self.setup_top_menu()
        self.setup_status_bar()

    def setup_ui(self):
        self.pages = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.fornecedores_page = FornecedoresPage()

        self.clientes_page = ClientesPage()
        self.empresa_page = EmpresaPage()

        self.produtos_page = self.create_page(
            "Produtos e Serviços",
            "Cadastro de produtos, serviços, preços e informações comerciais."
        )

        self.contas_financeiras_page = ContasFinanceirasPage()
        self.categorias_financeiras_page = CategoriasFinanceirasPage()
        self.lancamentos_financeiros_page = LancamentosFinanceirosPage()
        self.contas_pagar_page = ContasPagarPage()
        self.contas_receber_page = ContasReceberPage()
        self.fluxo_caixa_page = FluxoCaixaPage()
        self.conciliacao_page = ConciliacaoPage()

        self.notas_fiscais_page = self.create_page(
            "Notas Fiscais",
            "Registro manual de notas emitidas e recebidas."
        )

        self.relatorios_page = RelatoriosBasicosPage()

        self.configuracoes_page = self.create_page(
            "Configurações",
            "Dados da empresa, preferências do sistema e backup."
        )

        for page in [
            self.dashboard_page,
            self.fornecedores_page,
            self.clientes_page,
            self.empresa_page,
            self.produtos_page,
            self.contas_financeiras_page,
            self.categorias_financeiras_page,
            self.lancamentos_financeiros_page,
            self.contas_pagar_page,
            self.contas_receber_page,
            self.fluxo_caixa_page,
            self.conciliacao_page,
            self.notas_fiscais_page,
            self.relatorios_page,
            self.configuracoes_page,
        ]:
            self.pages.addWidget(page)

        self.setCentralWidget(self.pages)

    def setup_top_menu(self):
        toolbar = QToolBar("Menu Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(34, 34))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                spacing: 10px;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e5e7eb;
            }

            QToolButton {
                color: #111827;
                background-color: transparent;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 13px;
                min-width: 90px;
            }

            QToolButton:hover {
                background-color: #f3f4f6;
            }

            QToolButton:pressed {
                background-color: #e5e7eb;
            }

            QMenu {
                background-color: white;
                color: #111827;
                border: 1px solid #d1d5db;
                padding: 6px;
                font-size: 14px;
            }

            QMenu::item {
                padding: 8px 32px 8px 24px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #e5e7eb;
                color: #111827;
            }
        """)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(left_spacer)

        icon_inicio = self.style().standardIcon(QStyle.SP_DirHomeIcon)
        icon_cadastros = self.style().standardIcon(QStyle.SP_DirIcon)
        icon_financeiro = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        icon_fiscal = self.style().standardIcon(QStyle.SP_FileIcon)
        icon_relatorios = self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        icon_sistema = self.style().standardIcon(QStyle.SP_ComputerIcon)

        toolbar.addWidget(self.create_toolbar_button("Início", icon_inicio, callback=lambda: self.show_page(self.dashboard_page, "Dashboard")))
        toolbar.addWidget(self.create_toolbar_button("Cadastros", icon_cadastros, menu=self.create_cadastros_menu()))
        toolbar.addWidget(self.create_toolbar_button("Financeiro", icon_financeiro, menu=self.create_financeiro_menu()))
        toolbar.addWidget(self.create_toolbar_button("Fiscal", icon_fiscal, menu=self.create_fiscal_menu()))
        toolbar.addWidget(self.create_toolbar_button("Relatórios", icon_relatorios, menu=self.create_relatorios_menu()))
        toolbar.addWidget(self.create_toolbar_button("Sistema", icon_sistema, menu=self.create_sistema_menu()))

        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(right_spacer)

    def create_toolbar_button(self, text, icon, callback=None, menu=None):
        button = QToolButton()
        button.setText(text)
        button.setIcon(icon)
        button.setIconSize(QSize(34, 34))
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setCursor(Qt.PointingHandCursor)

        if menu is not None:
            button.setMenu(menu)
            button.setPopupMode(QToolButton.InstantPopup)
        elif callback is not None:
            button.clicked.connect(callback)

        return button

    def create_cadastros_menu(self):
        menu = QMenu(self)

        icon_fornecedor = self.style().standardIcon(QStyle.SP_DirIcon)
        icon_cliente = self.style().standardIcon(QStyle.SP_FileDialogListView)
        icon_empresa = self.style().standardIcon(QStyle.SP_ComputerIcon)
        icon_produto = self.style().standardIcon(QStyle.SP_FileDialogNewFolder)

        fornecedores_action = QAction(icon_fornecedor, "Fornecedores", self)
        fornecedores_action.triggered.connect(lambda: self.show_page(self.fornecedores_page, "Fornecedores"))

        clientes_action = QAction(icon_cliente, "Clientes", self)
        clientes_action.triggered.connect(lambda: self.show_page(self.clientes_page, "Clientes"))

        empresa_action = QAction(icon_empresa, "Minha Empresa", self)
        empresa_action.triggered.connect(lambda: self.show_page(self.empresa_page, "Minha Empresa"))

        produtos_action = QAction(icon_produto, "Produtos e Serviços", self)
        produtos_action.triggered.connect(lambda: self.show_page(self.produtos_page, "Produtos e Serviços"))

        menu.addAction(empresa_action)
        menu.addSeparator()
        menu.addAction(fornecedores_action)
        menu.addAction(clientes_action)
        menu.addSeparator()
        menu.addAction(produtos_action)
        return menu

    def create_financeiro_menu(self):
        menu = QMenu(self)

        icon_contas = self.style().standardIcon(QStyle.SP_DriveHDIcon)
        icon_categorias = self.style().standardIcon(QStyle.SP_FileDialogListView)
        icon_lancamentos = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        icon_pagar = self.style().standardIcon(QStyle.SP_ArrowDown)
        icon_receber = self.style().standardIcon(QStyle.SP_ArrowUp)
        icon_caixa = self.style().standardIcon(QStyle.SP_DriveHDIcon)
        icon_conciliacao = self.style().standardIcon(QStyle.SP_DialogApplyButton)

        contas_financeiras_action = QAction(icon_contas, "Contas Financeiras", self)
        contas_financeiras_action.triggered.connect(lambda: self.show_page(self.contas_financeiras_page, "Contas Financeiras"))

        categorias_action = QAction(icon_categorias, "Categorias Financeiras", self)
        categorias_action.triggered.connect(lambda: self.show_page(self.categorias_financeiras_page, "Categorias Financeiras"))

        lancamentos_action = QAction(icon_lancamentos, "Lançamentos Financeiros", self)
        lancamentos_action.triggered.connect(lambda: self.show_page(self.lancamentos_financeiros_page, "Lançamentos Financeiros"))

        contas_pagar_action = QAction(icon_pagar, "Contas a Pagar", self)
        contas_pagar_action.triggered.connect(lambda: self.show_page(self.contas_pagar_page, "Contas a Pagar"))

        contas_receber_action = QAction(icon_receber, "Contas a Receber", self)
        contas_receber_action.triggered.connect(lambda: self.show_page(self.contas_receber_page, "Contas a Receber"))

        fluxo_caixa_action = QAction(icon_caixa, "Fluxo de Caixa", self)
        fluxo_caixa_action.triggered.connect(lambda: self.show_page(self.fluxo_caixa_page, "Fluxo de Caixa"))

        conciliacao_action = QAction(icon_conciliacao, "Conciliação", self)
        conciliacao_action.triggered.connect(lambda: self.show_page(self.conciliacao_page, "Conciliação"))

        menu.addAction(contas_financeiras_action)
        menu.addAction(categorias_action)
        menu.addAction(lancamentos_action)
        menu.addSeparator()
        menu.addAction(contas_pagar_action)
        menu.addAction(contas_receber_action)
        menu.addSeparator()
        menu.addAction(fluxo_caixa_action)
        menu.addAction(conciliacao_action)
        return menu

    def create_fiscal_menu(self):
        menu = QMenu(self)
        icon_nota = self.style().standardIcon(QStyle.SP_FileIcon)
        notas_fiscais_action = QAction(icon_nota, "Notas Fiscais", self)
        notas_fiscais_action.triggered.connect(lambda: self.show_page(self.notas_fiscais_page, "Notas Fiscais"))
        menu.addAction(notas_fiscais_action)
        return menu

    def create_relatorios_menu(self):
        menu = QMenu(self)
        icon_relatorio = self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        relatorio_financeiro_action = QAction(icon_relatorio, "Relatórios Gerenciais", self)
        relatorio_financeiro_action.triggered.connect(lambda: self.show_page(self.relatorios_page, "Relatórios Gerenciais"))
        menu.addAction(relatorio_financeiro_action)
        return menu

    def create_sistema_menu(self):
        menu = QMenu(self)

        icon_configuracoes = self.style().standardIcon(QStyle.SP_ComputerIcon)
        icon_backup = self.style().standardIcon(QStyle.SP_DialogSaveButton)

        configuracoes_action = QAction(icon_configuracoes, "Configurações da Empresa", self)
        configuracoes_action.triggered.connect(lambda: self.show_page(self.empresa_page, "Configurações da Empresa"))

        backup_action = QAction(icon_backup, "Backup do Banco de Dados", self)
        backup_action.triggered.connect(lambda: self.show_page(self.configuracoes_page, "Backup"))

        menu.addAction(configuracoes_action)
        menu.addAction(backup_action)
        return menu

    def setup_status_bar(self):
        status_bar = QStatusBar()
        status_bar.showMessage("Sistema iniciado com sucesso.")
        self.setStatusBar(status_bar)

    def show_page(self, page, title):
        if hasattr(page, "carregar_resumo"):
            page.carregar_resumo()
        elif hasattr(page, "carregar_contas"):
            page.carregar_contas()
        elif hasattr(page, "carregar_categorias"):
            page.carregar_categorias()
        elif hasattr(page, "carregar_lancamentos"):
            page.carregar_lancamentos()
        elif hasattr(page, "carregar"):
            page.carregar()

        self.pages.setCurrentWidget(page)
        self.statusBar().showMessage(f"Módulo atual: {title}")

    def create_page(self, title_text, subtitle_text):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #111827;
        """)

        subtitle = QLabel(subtitle_text)
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #4b5563;
        """)

        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)

        card_layout = QVBoxLayout(card)

        placeholder = QLabel("Área de trabalho do módulo")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            font-size: 18px;
            color: #6b7280;
            padding: 80px;
        """)

        card_layout.addWidget(placeholder)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(card)

        page.setStyleSheet("""
            QWidget {
                background-color: #f3f4f6;
            }
        """)
        return page
