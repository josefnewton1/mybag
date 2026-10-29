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
                "meta_mes_pct": 0.0
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