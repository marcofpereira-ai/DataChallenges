import os
import pandas as pd
from datetime import datetime


def processar_camada_gold():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    pasta_silver = os.path.join(base_dir, "data", "silver")
    # Mantendo o padrão consolidado do seu ecossistema: gold_stage
    pasta_gold_stage = os.path.join(base_dir, "data", "gold_stage")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando processamento da Camada Gold Stage (Otimização Parquet)...")
    os.makedirs(pasta_gold_stage, exist_ok=True)

    # LISTA DE TABELAS ATUALIZADA: Mapeamento de origens e destinos colunares
    tabelas = [
        ("dim_deputados.csv", "dim_deputados.parquet"),
        ("dim_partidos.csv", "dim_partidos.parquet"),
        ("dim_proposicoes.csv", "dim_proposicoes.parquet"),
        ("fato_despesas.csv", "fato_despesas.parquet"),
        ("fato_votacoes.csv", "fato_votacoes.parquet")
    ]

    for arquivo_silver, arquivo_gold in tabelas:
        caminho_silver = os.path.join(pasta_silver, arquivo_silver)
        caminho_gold = os.path.join(pasta_gold_stage, arquivo_gold)

        if not os.path.exists(caminho_silver):
            print(f"⚠️ Alerta: Arquivo Silver não encontrado: {arquivo_silver}. Pulando...")
            continue

        print(f"-> Convertendo {arquivo_silver} para formato Parquet colunar...")

        # 1. Lê o arquivo CSV da Camada Silver
        df = pd.read_csv(caminho_silver, sep=";")

        # 2. Ajuste de otimização e consistência de tipos para o Parquet
        if "ID_Deputado" in df.columns:
            df["ID_Deputado"] = df["ID_Deputado"].astype(str)
        if "ID_Partido" in df.columns:
            df["ID_Partido"] = df["ID_Partido"].astype(str)
        if "ID_Proposicao" in df.columns:
            df["ID_Proposicao"] = df["ID_Proposicao"].astype(str)
        if "ID_Votacao" in df.columns:
            df["ID_Votacao"] = df["ID_Votacao"].astype(str)

        # Tipagem explícita de campos temporais
        if "Data_Despesa" in df.columns:
            df["Data_Despesa"] = pd.to_datetime(df["Data_Despesa"], errors="coerce")
        if "Data_Votacao" in df.columns:
            df["Data_Votacao"] = pd.to_datetime(df["Data_Votacao"], errors="coerce")
        if "Data_Hora_Registro" in df.columns:
            df["Data_Hora_Registro"] = pd.to_datetime(df["Data_Hora_Registro"], errors="coerce")

        # 3. Salva no formato Parquet (Compressão Snappy)
        df.to_parquet(caminho_gold, index=False, compression="snappy")

        print(f"   ✓ Sucesso! Salvo em: {arquivo_gold} ({df.shape[0]} linhas)")

    print(f"\n======== ETAPA GOLD STAGE CONCLUÍDA ========")
    print(f"Todos os arquivos otimizados para Analytics estão em: {pasta_gold_stage}")
    print(f"=============================================")


if __name__ == "__main__":
    processar_camada_gold()