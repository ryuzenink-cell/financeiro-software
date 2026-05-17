import sqlite3
from pathlib import Path

DB_DIR = Path("data")
DB_PATH = DB_DIR / "financeiro_teste.db"


EMPRESAS_FAKE = [
    ("Astra Comercial Ltda", "61.111.222/0001-61", "(35) 99701-3001", "contato@astracomercial.com"),
    ("Blue River Suprimentos", "62.222.333/0001-62", "(35) 99702-3002", "vendas@blueriver.com"),
    ("Céu Claro Serviços ME", "63.333.444/0001-63", "(35) 99703-3003", "atendimento@ceuclaro.com"),
    ("Domínio Office Center", "64.444.555/0001-64", "(35) 99704-3004", "contato@dominiooffice.com"),
    ("Elite Soluções Corporativas", "65.555.666/0001-65", "(35) 99705-3005", "comercial@elitesolucoes.com"),
    ("Fonte Nova Distribuidora", "66.666.777/0001-66", "(35) 99706-3006", "vendas@fontenova.com"),
    ("Golden Print Express", "67.777.888/0001-67", "(35) 99707-3007", "orcamento@goldenprint.com"),
    ("HiperTech Informática", "68.888.999/0001-68", "(35) 99708-3008", "suporte@hipertech.com"),
    ("Ideal Pack Embalagens", "69.999.000/0001-69", "(35) 99709-3009", "pedidos@idealpack.com"),
    ("Júpiter Serviços Gerais", "70.000.111/0001-70", "(35) 99710-3010", "contato@jupiterservicos.com"),

    ("Kanzen Consultoria Empresarial", "71.111.222/0001-71", "(35) 99711-3011", "contato@kanzenconsultoria.com"),
    ("Líder Papelaria e Escritório", "72.222.333/0001-72", "(35) 99712-3012", "vendas@liderpapelaria.com"),
    ("MetroSul Logística", "73.333.444/0001-73", "(35) 99713-3013", "operacional@metrosul.com"),
    ("Nobre Café Corporativo", "74.444.555/0001-74", "(35) 99714-3014", "pedidos@nobrecafe.com"),
    ("Onix Segurança Eletrônica", "75.555.666/0001-75", "(35) 99715-3015", "contato@onixseguranca.com"),
    ("Padrão Limpeza Profissional", "76.666.777/0001-76", "(35) 99716-3016", "compras@padraolimpeza.com"),
    ("Quantum Sistemas ME", "77.777.888/0001-77", "(35) 99717-3017", "suporte@quantumsistemas.com"),
    ("Realce Comunicação Visual", "78.888.999/0001-78", "(35) 99718-3018", "contato@realcevisual.com"),
    ("Sigma Materiais Industriais", "79.999.000/0001-79", "(35) 99719-3019", "vendas@sigmamateriais.com"),
    ("Tríade Gestão e Apoio", "80.000.111/0001-80", "(35) 99720-3020", "atendimento@triadegestao.com"),

    ("UltraNet Telecom", "81.111.222/0001-81", "(35) 99721-3021", "suporte@ultranet.com"),
    ("Vértice Norte Distribuição", "82.222.333/0001-82", "(35) 99722-3022", "comercial@verticenorte.com"),
    ("WebMais Soluções Digitais", "83.333.444/0001-83", "(35) 99723-3023", "contato@webmais.com"),
    ("Xpress Office Entregas", "84.444.555/0001-84", "(35) 99724-3024", "logistica@xpressoffice.com"),
    ("YamaTech Assistência", "85.555.666/0001-85", "(35) 99725-3025", "suporte@yamatech.com"),
    ("Zenit Comercial ME", "86.666.777/0001-86", "(35) 99726-3026", "vendas@zenitcomercial.com"),
    ("Alvorada Serviços Contábeis", "87.777.888/0001-87", "(35) 99727-3027", "contato@alvoradacontabil.com"),
    ("Brava Soluções Administrativas", "88.888.999/0001-88", "(35) 99728-3028", "atendimento@bravasolucoes.com"),
    ("Casa Forte Equipamentos", "89.999.000/0001-89", "(35) 99729-3029", "vendas@casaforteequip.com"),
    ("Dinamika Business Center", "90.000.111/0001-90", "(35) 99730-3030", "contato@dinamikabusiness.com"),

    ("Essencial Materiais de Escritório", "91.111.222/0001-91", "(35) 99731-3031", "vendas@essencialmateriais.com"),
    ("Foco Digital Marketing", "92.222.333/0001-92", "(35) 99732-3032", "hello@focodigital.com"),
    ("Grão Nobre Distribuidora", "93.333.444/0001-93", "(35) 99733-3033", "pedidos@graonobre.com"),
    ("Horizonte Fiscal Apoio MEI", "94.444.555/0001-94", "(35) 99734-3034", "contato@horizontefiscal.com"),
    ("Ícone Design e Impressão", "95.555.666/0001-95", "(35) 99735-3035", "orcamento@iconedesign.com"),
    ("Jardim Office Móveis", "96.666.777/0001-96", "(35) 99736-3036", "vendas@jardimoffice.com"),
    ("Kroma Comunicação Visual", "97.777.888/0001-97", "(35) 99737-3037", "contato@kromavisual.com"),
    ("Lótus Tecnologia Empresarial", "98.888.999/0001-98", "(35) 99738-3038", "suporte@lotustech.com"),
    ("Minas Forte Atacadista", "99.999.000/0001-99", "(35) 99739-3039", "compras@minasforte.com"),
    ("Nova Linha Uniformes", "10.101.202/0001-10", "(35) 99740-3040", "vendas@novalinhauniformes.com"),

    ("Órbita Soluções Comerciais", "11.202.303/0001-11", "(35) 99741-3041", "comercial@orbitasolucoes.com"),
    ("Ponte Alta Transportes", "12.303.404/0001-12", "(35) 99742-3042", "operacional@pontealta.com"),
    ("Quality Paper Distribuição", "13.404.505/0001-13", "(35) 99743-3043", "vendas@qualitypaper.com"),
    ("Rádio Link Telecom", "14.505.606/0001-14", "(35) 99744-3044", "suporte@radiolink.com"),
    ("Santo Forte Manutenção", "15.606.707/0001-15", "(35) 99745-3045", "servicos@santoforte.com"),
    ("Terra Azul Energia Solar", "16.707.808/0001-16", "(35) 99746-3046", "contato@terraazulsolar.com"),
    ("União Express Entregas", "17.808.909/0001-17", "(35) 99747-3047", "logistica@uniaoexpress.com"),
    ("Valor Certo Consultoria", "18.909.010/0001-18", "(35) 99748-3048", "contato@valorcerto.com"),
    ("WorkPro Serviços Empresariais", "19.010.111/0001-19", "(35) 99749-3049", "atendimento@workpro.com"),
    ("Zeta Prime Suprimentos", "20.111.212/0001-20", "(35) 99750-3050", "vendas@zetaprime.com"),
]


def conectar():
    DB_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def criar_tabela_fornecedores():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            documento TEXT,
            telefone TEXT,
            email TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def cadastrar_empresas_fake():
    conn = conectar()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO fornecedores (nome, documento, telefone, email)
        VALUES (?, ?, ?, ?)
    """, EMPRESAS_FAKE)

    conn.commit()
    conn.close()


def contar_fornecedores():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM fornecedores")
    total = cursor.fetchone()[0]

    conn.close()
    return total


def listar_ultimos_fornecedores():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, documento, telefone, email
        FROM fornecedores
        ORDER BY id DESC
        LIMIT 30
    """)

    fornecedores = cursor.fetchall()
    conn.close()

    print("\n=== ÚLTIMOS 30 FORNECEDORES CADASTRADOS ===")

    for fornecedor in fornecedores:
        print(f"""
ID: {fornecedor[0]}
Nome: {fornecedor[1]}
Documento: {fornecedor[2]}
Telefone: {fornecedor[3]}
E-mail: {fornecedor[4]}
-----------------------------
""")


if __name__ == "__main__":
    criar_tabela_fornecedores()
    cadastrar_empresas_fake()

    total = contar_fornecedores()

    print(f"\n30 empresas fake cadastradas com sucesso!")
    print(f"Total de fornecedores no banco: {total}")

    listar_ultimos_fornecedores()