import json
import os
import csv

CONFIG_FILE = "mybag_usuarios_config.json"


def carregar_dados_gerais():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "usuario_atual": "José Nilton",
        "perfis": {
            "José Nilton": {
                "foto_path": "",
                "historico_salvo": [],
                "total_produzido_hoje": 0,
                "meta_hoje": 720,
                "porcentagem_hoje": 0.0,
                "oee_semana": 0.0,
                "meta_mes_pct": 0.0,
                "tema_atual": "padrao"  # <-- Adicione esta linha para o sistema lembrar do tema
            }
        }
    }


DADOS_APP = carregar_dados_gerais()


def gerar_planilha_csv():
    try:
        with open("mybag_banco_dados.csv", mode="w", newline="", encoding="utf-8-sig") as arquivo_csv:
            campos = [
                "Nome do Usuário", "Caminho da Foto", "Meta Diária",
                "Total Produzido Hoje", "Porcentagem Concluída Hoje (%)",
                "OEE da Semana (%)", "Produção do Mês (%)", "Histórico de Relatórios Salvos"
            ]
            escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
            escritor.writeheader()

            for nome_usuario, perfil in DADOS_APP["perfis"].items():
                historico_str = " | ".join(perfil["historico_salvo"]) if perfil[
                    "historico_salvo"] else "Nenhum histórico"
                escritor.writerow({
                    "Nome do Usuário": nome_usuario,
                    "Caminho da Foto": perfil.get("foto_path", ""),
                    "Meta Diária": perfil.get("meta_hoje", 720),
                    "Total Produzido Hoje": perfil.get("total_produzido_hoje", 0),
                    "Porcentagem Concluída Hoje (%)": perfil.get("porcentagem_hoje", 0.0),
                    "OEE da Semana (%)": perfil.get("oee_semana", 0.0),
                    "Produção do Mês (%)": perfil.get("meta_mes_pct", 0.0),
                    "Histórico de Relatórios Salvos": historico_str
                })
    except Exception as e:
        print("Erro ao gerar planilha CSV:", e)


gerar_planilha_csv()


def salvar_dados_gerais():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DADOS_APP, f, ensure_ascii=False, indent=4)
        gerar_planilha_csv()
    except Exception as e:
        print("Erro ao salvar dados:", e)


def obter_perfil_atual():
    nome = DADOS_APP["usuario_atual"]
    if nome not in DADOS_APP["perfis"]:
        DADOS_APP["perfis"][nome] = {
            "foto_path": "",
            "historico_salvo": [],
            "total_produzido_hoje": 0,
            "meta_hoje": 720,
            "porcentagem_hoje": 0.0,
            "oee_semana": 0.0,
            "meta_mes_pct": 0.0
        }
    return DADOS_APP["perfis"][nome]

# Adicione ou substitua estas informações no seu database.py

DADOS_APP = {
    "usuario_atual": "Nilton",
    "meta_hoje": 720,
    "total_produzido_hoje": 0,
    "porcentagem_hoje": 0.0,
    "historico_salvo": [],
    "tema_atual": "padrao"  # Salva o tema escolhido ('padrao', 'escuro', 'azul')
}

# Dicionário com as paletas de cores completas para todo o app
PALETAS_TEMAS = {
    'padrao': {  # Tema 1: Bege Clássico
        'bg': (0.96, 0.93, 0.88, 1),          # Fundo bege claro
        'header_bg': (0.12, 0.14, 0.18, 1),   # Cabeçalho cinza escuro
        'header_text': (1.0, 0.82, 0.0, 1),   # Texto amarelo
        'text': (0.12, 0.14, 0.18, 1),        # Texto principal escuro
        'card_bg': (1.0, 1.0, 1.0, 1),        # Cartões brancos
        'card_text': (0.12, 0.14, 0.18, 1),
    },
    'escuro': {  # Tema 2: Stellantis Dark (Escuro)
        'bg': (0.10, 0.12, 0.15, 1),          # Fundo grafite escuro
        'header_bg': (0.05, 0.06, 0.08, 1),   # Cabeçalho quase preto
        'header_text': (1.0, 0.82, 0.0, 1),   # Texto amarelo
        'text': (0.90, 0.90, 0.90, 1),        # Texto claro
        'card_bg': (0.18, 0.22, 0.28, 1),   # Cartões em tom cinza escuro
        'card_text': (1.0, 1.0, 1.0, 1),
    },
    'azul': {    # Tema 3: Azul Industrial
        'bg': (0.85, 0.90, 0.95, 1),          # Fundo azul claro industrial
        'header_bg': (0.10, 0.25, 0.40, 1),   # Cabeçalho azul escuro
        'header_text': (1.0, 1.0, 1.0, 1),    # Texto branco
        'text': (0.05, 0.15, 0.25, 1),        # Texto azul marinho
        'card_bg': (1.0, 1.0, 1.0, 1),        # Cartões brancos
        'card_text': (0.05, 0.15, 0.25, 1),
    }
}

def obter_paleta_atual():
    tema = DADOS_APP.get("tema_atual", "padrao")
    return PALETAS_TEMAS.get(tema, PALETAS_TEMAS['padrao'])

def obter_perfil_atual():
    # Mantém o restante da sua função original de perfil
    return DADOS_APP

def salvar_dados_gerais():
    # Mantém a lógica de salvamento
    pass