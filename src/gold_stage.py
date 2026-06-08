import os
import pandas as pd
from datetime import datetime


def processar_camada_gold():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    pasta_silver = os.path.join(base_dir, "data", "silver")
    pasta_gold = os.path.join(base_dir, "data", "gold")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando processamento da Camada Gold (Otimização Parquet)...")
    os.makedirs(pasta_gold, exist_ok=True)

    # Lista de tabelas para processar: (Nome do arquivo Silver, Nome do arquivo Gold)
    tabelas = [
        ("dim_deputados.csv", "dim_deputados.parquet"),
        ("dim_proposicoes.csv", "dim_proposicoes.parquet"),
        ("fato_despesas.csv", "fato_despesas.parquet")
    ]

    for arquivo_silver, arquivo_gold in tabelas:
        caminho_silver = os.path.join(pasta_silver, arquivo_silver)
        caminho_gold = os.path.join(pasta_gold, arquivo_gold)

        if not os.path.exists(caminho_silver):
            print(f"⚠️ Alerta: Arquivo Silver não encontrado: {arquivo_silver}. Pulando...")
            continue

        print(f"-> Convertendo {arquivo_silver} para formato Parquet colunar...")

        # 1. Lê o arquivo CSV da Silver (especificando o separador que usamos)
        df = pd.read_csv(caminho_silver, sep=";")

        # 2. Pequeno ajuste de otimização de tipos para o Parquet
        # Garante que os IDs sejam tratados de forma consistente como strings/texto para evitar truncamento
        if "ID_Deputado" in df.columns:
            df["ID_Deputado"] = df["ID_Deputado"].astype(str)
        if "ID_Proposicao" in df.columns:
            df["ID_Proposicao"] = df["ID_Proposicao"].astype(str)

        # 3. Salva no formato Parquet (Compressão Snappy padrão, que é ultra rápida)
        df.to_parquet(caminho_gold, index=False, compression="snappy")

        print(f"   ✓ Sucesso! Salvo em: {arquivo_gold} ({df.shape[0]} linhas)")

    print(f"\n======== ETAPA GOLD CONCLUÍDA ========")
    print(f"Arquivos otimizados para Analytics disponíveis em: {pasta_gold}")
    print(f"=======================================")


if __name__ == "__main__":
    processar_camada_gold()