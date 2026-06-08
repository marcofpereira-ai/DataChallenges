import os
import json
import pandas as pd
from datetime import datetime


def transformar_proposicoes():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    caminho_origem = os.path.join(base_dir, "data", "raw", "legado_2026", "proposicoes_2026.json")
    pasta_destino = os.path.join(base_dir, "data", "silver")
    caminho_salvamento = os.path.join(pasta_destino, "dim_proposicoes.csv")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a transformação da Dimensão Proposições 2026...")

    # 1. Valida se o arquivo bruto de proposições existe
    if not os.path.exists(caminho_origem):
        print(f"❌ Erro: Arquivo bruto de proposições não encontrado em: {caminho_origem}")
        return

    # 2. Carrega o JSON bruto para o DataFrame
    with open(caminho_origem, "r", encoding="utf-8") as f:
        dados_brutos = json.load(f)

    df = pd.DataFrame(dados_brutos)
    print(f"-> Dados brutos carregados: {df.shape[0]} registros encontrados.")

    # 3. LIMPEZA E ESTRUTURAÇÃO (Business Rules)

    # Remove a coluna 'uri' que é irrelevante para a modelagem no Power BI
    df = df.drop(columns=["uri"], errors="ignore")

    # Limpeza de strings e remoção de quebras de linha/espaços excessivos nas ementas (resumos dos projetos)
    df["ementa"] = df["ementa"].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
    df["siglaTipo"] = df["siglaTipo"].astype(str).str.upper().str.strip()

    # Tratamento de valores numéricos de controle de tempo
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").fillna(2026).astype(int)
    df["numero"] = pd.to_numeric(df["numero"], errors="coerce").fillna(0).astype(int)

    # Renomeia as colunas para o padrão do Star Schema
    dicionario_renomear = {
        "id": "ID_Proposicao",
        "siglaTipo": "Tipo_Proposicao",
        "numero": "Numero_Proposicao",
        "ano": "Ano_Proposicao",
        "ementa": "Ementa"
    }
    df = df.rename(columns=dicionario_renomear)

    # 4. SALVAMENTO NA CAMADA SILVER (Como Tabela Dimensão)
    os.makedirs(pasta_destino, exist_ok=True)

    # Salvando em CSV com separador ';' e encoding compatível
    df.to_csv(caminho_salvamento, sep=";", index=False, encoding="utf-8-sig")

    print(f"\n======== PARTE SILVER CONCLUÍDA ========")
    print(f"Tabela 'dim_proposicoes' gerada com sucesso!")
    print(f"Dimensões finais: {df.shape[0]} linhas e {df.shape[1]} colunas.")
    print(f"Arquivo saved em: {caminho_salvamento}")
    print(f"========================================")


if __name__ == "__main__":
    transformar_proposicoes()