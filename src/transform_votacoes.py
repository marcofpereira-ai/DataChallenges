import os
import json
import pandas as pd
from datetime import datetime


def transformar_votacoes():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    caminho_origem = os.path.join(base_dir, "data", "raw", "votacoes_bruto.json")
    pasta_destino = os.path.join(base_dir, "data", "silver")
    caminho_salvamento = os.path.join(pasta_destino, "fato_votacoes.csv")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a transformação da Fato Votações 2026...")

    # 1. Valida se o arquivo bruto de votações existe
    if not os.path.exists(caminho_origem):
        print(f"❌ Erro: Arquivo bruto de votações não encontrado em: {caminho_origem}")
        return

    # 2. Carrega o JSON bruto para o DataFrame
    with open(caminho_origem, "r", encoding="utf-8") as f:
        dados_brutos = json.load(f)

    df = pd.DataFrame(dados_brutos)
    print(f"-> Dados brutos carregados: {df.shape[0]} registros encontrados.")

    # 3. LIMPEZA, TRATAMENTO E TIPAGEM (Regras de Negócio)

    # Remove colunas de metadados da API que não agregam valor analítico ao BI
    colunas_para_remover = ["uri", "uriProposicaoPrincipal", "uriEvento", "uriOrgao"]
    df = df.drop(columns=colunas_para_remover, errors="ignore")

    # Tratamento de Datas: Converte 'data' e 'dataHoraRegistro' para datetime do Pandas
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["dataHoraRegistro"] = pd.to_datetime(df["dataHoraRegistro"], errors="coerce")

    # Extração e limpeza de chaves textuais/IDs
    if "id" in df.columns:
        df["id"] = df["id"].astype(str).str.strip()

    # Tratamento de strings descritivas reais do endpoint (descricao e efeito)
    if "descricao" in df.columns:
        df["descricao"] = df["descricao"].astype(str).str.strip()

    if "efeito" in df.columns:
        df["efeito"] = df["efeito"].astype(str).str.strip()

    # Transforma flags em Booleanos puros para facilitar filtros e contagens no Power BI
    if "aprovada" in df.columns:
        df["aprovada"] = df["aprovada"].fillna(False).astype(bool)

    # Renomeia as colunas para o padrão descritivo amigável (Tabela Fato)
    dicionario_renomear = {
        "id": "ID_Votacao",  # PK da Votação
        "data": "Data_Votacao",
        "dataHoraRegistro": "Data_Hora_Registro",
        "idOrgao": "ID_Orgao",  # Chave FK do Órgão
        "efeito": "Efeito_Votacao",  # O que foi decidido na votação
        "descricao": "Descricao_Votacao",  # Detalhes da votação
        "aprovada": "Flg_Aprovada"  # True/False para o dashboard
    }
    df = df.rename(columns=dicionario_renomear)

    # Organiza as colunas de forma estruturada para o modelo relacional
    colunas_ordenadas = [
        "ID_Votacao", "Data_Votacao", "Data_Hora_Registro", "ID_Orgao",
        "Efeito_Votacao", "Descricao_Votacao", "Flg_Aprovada"
    ]
    # Garante que só vamos selecionar colunas que realmente existem após a renomeação
    colunas_ordenadas = [c for c in colunas_ordenadas if c in df.columns]
    df = df[colunas_ordenadas]

    # 4. SALVAMENTO NA CAMADA SILVER (Como nossa Tabela Fato)
    os.makedirs(pasta_destino, exist_ok=True)

    # Salva com o separador ';' e encoding correto para preservar acentuações
    df.to_csv(caminho_salvamento, sep=";", index=False, encoding="utf-8-sig")

    print(f"\n======== PARTE SILVER CONCLUÍDA ========")
    print(f"Tabela 'fato_votacoes' gerada com sucesso!")
    print(f"Dimensões finais: {df.shape[0]} linhas e {df.shape[1]} colunas.")
    print(f"Arquivo salvo em: {caminho_salvamento}")
    print(f"========================================")


if __name__ == "__main__":
    transformar_votacoes()