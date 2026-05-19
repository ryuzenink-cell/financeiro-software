from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFormLayout,
    QGroupBox,
    QMessageBox,
    QComboBox,
    QScrollArea,
)
from PySide6.QtCore import Qt

from app.repositories.empresa_repository import obter_empresa_ativa, salvar_empresa


class EmpresaPage(QWidget):
    def __init__(self):
        super().__init__()
        self.empresa_atual = None
        self.setup_ui()
        self.carregar()

    def setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        title = QLabel("Minha Empresa")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #111827;")

        subtitle = QLabel(
            "Cadastre os dados do MEI/empresa que serão usados nos relatórios, configurações e identificação do sistema."
        )
        subtitle.setStyleSheet("font-size: 16px; color: #4b5563;")

        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 14px; color: #4b5563; padding: 8px 0;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        content = QWidget()
        content.setStyleSheet("QWidget { background-color: #ffffff; color: #111827; }")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)

        dados_box = QGroupBox("Dados cadastrais")
        dados_box.setStyleSheet(self.group_style())
        dados_form = QFormLayout(dados_box)
        dados_form.setLabelAlignment(Qt.AlignRight)
        dados_form.setFormAlignment(Qt.AlignTop)
        dados_form.setSpacing(12)

        self.nome_fantasia_input = QLineEdit()
        self.razao_social_input = QLineEdit()
        self.cnpj_input = QLineEdit()
        self.ie_input = QLineEdit()
        self.im_input = QLineEdit()
        self.mei_combo = QComboBox()
        self.mei_combo.addItem("Sim, é MEI", 1)
        self.mei_combo.addItem("Não", 0)
        self.cnae_input = QLineEdit()
        self.atividade_input = QLineEdit()

        for widget in [
            self.nome_fantasia_input,
            self.razao_social_input,
            self.cnpj_input,
            self.ie_input,
            self.im_input,
            self.cnae_input,
            self.atividade_input,
        ]:
            widget.setStyleSheet(self.input_style())

        self.mei_combo.setStyleSheet(self.input_style())

        dados_form.addRow("Nome fantasia*:", self.nome_fantasia_input)
        dados_form.addRow("Razão social:", self.razao_social_input)
        dados_form.addRow("CNPJ:", self.cnpj_input)
        dados_form.addRow("Inscrição estadual:", self.ie_input)
        dados_form.addRow("Inscrição municipal:", self.im_input)
        dados_form.addRow("Enquadramento:", self.mei_combo)
        dados_form.addRow("CNAE:", self.cnae_input)
        dados_form.addRow("Atividade principal:", self.atividade_input)

        contato_box = QGroupBox("Responsável e contato")
        contato_box.setStyleSheet(self.group_style())
        contato_form = QFormLayout(contato_box)
        contato_form.setLabelAlignment(Qt.AlignRight)
        contato_form.setSpacing(12)

        self.responsavel_input = QLineEdit()
        self.cpf_responsavel_input = QLineEdit()
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()

        for widget in [self.responsavel_input, self.cpf_responsavel_input, self.telefone_input, self.email_input]:
            widget.setStyleSheet(self.input_style())

        contato_form.addRow("Responsável:", self.responsavel_input)
        contato_form.addRow("CPF do responsável:", self.cpf_responsavel_input)
        contato_form.addRow("Telefone:", self.telefone_input)
        contato_form.addRow("E-mail:", self.email_input)

        endereco_box = QGroupBox("Endereço")
        endereco_box.setStyleSheet(self.group_style())
        endereco_form = QFormLayout(endereco_box)
        endereco_form.setLabelAlignment(Qt.AlignRight)
        endereco_form.setSpacing(12)

        self.cep_input = QLineEdit()
        self.endereco_input = QLineEdit()
        self.numero_input = QLineEdit()
        self.complemento_input = QLineEdit()
        self.bairro_input = QLineEdit()
        self.cidade_input = QLineEdit()
        self.uf_input = QLineEdit()
        self.uf_input.setMaxLength(2)

        for widget in [
            self.cep_input,
            self.endereco_input,
            self.numero_input,
            self.complemento_input,
            self.bairro_input,
            self.cidade_input,
            self.uf_input,
        ]:
            widget.setStyleSheet(self.input_style())

        endereco_form.addRow("CEP:", self.cep_input)
        endereco_form.addRow("Endereço:", self.endereco_input)
        endereco_form.addRow("Número:", self.numero_input)
        endereco_form.addRow("Complemento:", self.complemento_input)
        endereco_form.addRow("Bairro:", self.bairro_input)
        endereco_form.addRow("Cidade:", self.cidade_input)
        endereco_form.addRow("UF:", self.uf_input)

        obs_box = QGroupBox("Observações internas")
        obs_box.setStyleSheet(self.group_style())
        obs_layout = QVBoxLayout(obs_box)
        self.observacoes_input = QTextEdit()
        self.observacoes_input.setMinimumHeight(90)
        self.observacoes_input.setStyleSheet(self.input_style())
        obs_layout.addWidget(self.observacoes_input)

        buttons_bar = QHBoxLayout()
        buttons_bar.addStretch()
        self.btn_recarregar = QPushButton("Recarregar")
        self.btn_salvar = QPushButton("Salvar empresa")
        self.btn_recarregar.clicked.connect(self.carregar)
        self.btn_salvar.clicked.connect(self.salvar)
        for button in [self.btn_recarregar, self.btn_salvar]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(self.button_style())
        buttons_bar.addWidget(self.btn_recarregar)
        buttons_bar.addWidget(self.btn_salvar)

        content_layout.addWidget(dados_box)
        content_layout.addWidget(contato_box)
        content_layout.addWidget(endereco_box)
        content_layout.addWidget(obs_box)
        content_layout.addLayout(buttons_bar)
        content_layout.addStretch()
        scroll.setWidget(content)

        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)
        root_layout.addWidget(self.status_label)
        root_layout.addWidget(scroll)

        self.setStyleSheet("QWidget { background-color: #f3f4f6; color: #111827; }")

    def carregar(self):
        self.empresa_atual = obter_empresa_ativa()
        if not self.empresa_atual:
            self.limpar_campos()
            self.status_label.setText("Nenhuma empresa ativa cadastrada. Preencha os dados e clique em Salvar empresa.")
            return

        empresa = self.empresa_atual
        self.nome_fantasia_input.setText(empresa.get("nome_fantasia") or "")
        self.razao_social_input.setText(empresa.get("razao_social") or "")
        self.cnpj_input.setText(empresa.get("cnpj") or "")
        self.ie_input.setText(empresa.get("inscricao_estadual") or "")
        self.im_input.setText(empresa.get("inscricao_municipal") or "")
        index = self.mei_combo.findData(empresa.get("mei"))
        self.mei_combo.setCurrentIndex(index if index >= 0 else 0)
        self.cnae_input.setText(empresa.get("cnae") or "")
        self.atividade_input.setText(empresa.get("atividade_principal") or "")
        self.responsavel_input.setText(empresa.get("responsavel") or "")
        self.cpf_responsavel_input.setText(empresa.get("cpf_responsavel") or "")
        self.telefone_input.setText(empresa.get("telefone") or "")
        self.email_input.setText(empresa.get("email") or "")
        self.cep_input.setText(empresa.get("cep") or "")
        self.endereco_input.setText(empresa.get("endereco") or "")
        self.numero_input.setText(empresa.get("numero") or "")
        self.complemento_input.setText(empresa.get("complemento") or "")
        self.bairro_input.setText(empresa.get("bairro") or "")
        self.cidade_input.setText(empresa.get("cidade") or "")
        self.uf_input.setText(empresa.get("uf") or "")
        self.observacoes_input.setPlainText(empresa.get("observacoes") or "")

        nome = empresa.get("nome_fantasia") or "Empresa cadastrada"
        cnpj = empresa.get("cnpj") or "CNPJ não informado"
        self.status_label.setText(f"Empresa ativa: {nome} — {cnpj}")

    def limpar_campos(self):
        for widget in [
            self.nome_fantasia_input,
            self.razao_social_input,
            self.cnpj_input,
            self.ie_input,
            self.im_input,
            self.cnae_input,
            self.atividade_input,
            self.responsavel_input,
            self.cpf_responsavel_input,
            self.telefone_input,
            self.email_input,
            self.cep_input,
            self.endereco_input,
            self.numero_input,
            self.complemento_input,
            self.bairro_input,
            self.cidade_input,
            self.uf_input,
        ]:
            widget.clear()
        self.mei_combo.setCurrentIndex(0)
        self.observacoes_input.clear()

    def salvar(self):
        data = {
            "id": self.empresa_atual.get("id") if self.empresa_atual else None,
            "nome_fantasia": self.nome_fantasia_input.text().strip(),
            "razao_social": self.razao_social_input.text().strip(),
            "cnpj": self.cnpj_input.text().strip(),
            "inscricao_estadual": self.ie_input.text().strip(),
            "inscricao_municipal": self.im_input.text().strip(),
            "mei": self.mei_combo.currentData(),
            "cnae": self.cnae_input.text().strip(),
            "atividade_principal": self.atividade_input.text().strip(),
            "responsavel": self.responsavel_input.text().strip(),
            "cpf_responsavel": self.cpf_responsavel_input.text().strip(),
            "telefone": self.telefone_input.text().strip(),
            "email": self.email_input.text().strip(),
            "cep": self.cep_input.text().strip(),
            "endereco": self.endereco_input.text().strip(),
            "numero": self.numero_input.text().strip(),
            "complemento": self.complemento_input.text().strip(),
            "bairro": self.bairro_input.text().strip(),
            "cidade": self.cidade_input.text().strip(),
            "uf": self.uf_input.text().strip().upper(),
            "observacoes": self.observacoes_input.toPlainText().strip(),
        }

        if not data["nome_fantasia"]:
            QMessageBox.warning(self, "Atenção", "Informe pelo menos o nome fantasia da empresa.")
            return

        try:
            salvar_empresa(data)
            self.carregar()
            QMessageBox.information(self, "Sucesso", "Dados da empresa salvos com sucesso.")
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar a empresa:\n{exc}")

    def input_style(self):
        return """
            QLineEdit, QTextEdit, QComboBox {
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
                padding: 10px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """

    def group_style(self):
        return """
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 16px;
                padding: 16px;
                font-weight: bold;
                color: #111827;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #111827;
            }
        """
