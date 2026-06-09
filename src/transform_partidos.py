import os
import json
import pandas as pd
from datetime import datetime


def transformar_partidos():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    caminho_origem = os.path.join(base_dir, "data", "raw", "partidos_bruto.json")
    pasta_destino = os.path.join(base_dir, "data", "silver")
    caminho_salvamento = os.path.join(pasta_destino, "dim_partidos.csv")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a transformação da Dimensão Partidos...")

    # 1. Valida se o arquivo bruto de partidos existe
    if not os.path.exists(caminho_origem):
        print(f"❌ Erro: Arquivo bruto de partidos não encontrado em: {caminho_origem}")
        return

    # 2. Carrega o JSON bruto para o DataFrame
    with open(caminho_origem, "r", encoding="utf-8") as f:
        dados_brutos = json.load(f)

    df = pd.DataFrame(dados_brutos)
    print(f"-> Dados brutos carregados: {df.shape[0]} registros encontrados.")

    # 3. LIMPEZA, TRATAMENTO E TIPAGEM (Regras de Negócio)

    # Remove a coluna de links HATEOAS que veio da API e não agrega valor ao DW/Supabase
    colunas_para_remover = ["uri"]
    df = df.drop(columns=colunas_para_remover, errors="ignore")

    # Garante a integridade e limpeza das strings textuais dos partidos
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["sigla"] = df["sigla"].astype(str).str.strip()
    df["nome"] = df["nome"].astype(str).str.strip()

    # Renomeia as colunas para o padrão amigável do modelo dimensional (Tabela Dimensão)
    dicionario_renomear = {
        "id": "ID_Partido",  # PK do Partido
        "sigla": "Sigla_Partido",
        "nome": "Nome_Partido"
    }
    df = df.rename(columns=dicionario_renomear)

    # Organiza a ordem das colunas de forma lógica
    colunas_ordenadas = ["ID_Partido", "Sigla_Partido", "Nome_Partido"]
    df = df[colunas_ordenadas]

    # 4. SALVAMENTO NA CAMADA SILVER (Como nossa Tabela Dimensão)
    os.makedirs(pasta_destino, exist_ok=True)

    # Salvando em CSV formatado para abrir perfeitamente em ferramentas de BI e Excel
    df.to_csv(caminho_salvamento, sep=";", index=False, encoding="utf-8-sig")

    print(f"\n======== PARTE SILVER CONCLUÍDA ========")
    print(f"Tabela 'dim_partidos' gerada com sucesso!")
    print(f"Dimensões finais: {df.shape[0]} linhas e {df.shape[1]} colunas.")
    print(f"Arquivo salvo em: {caminho_salvamento}")
    print(f"========================================")


if __name__ == "__main__":
    transformar_partidos()