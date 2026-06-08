import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Carrega as credenciais seguras do .env
load_dotenv()


def carregar_dados_no_supabase():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)
    pasta_silver = os.path.join(base_dir, "data", "silver")
    pasta_gold = os.path.join(base_dir, "data", "gold")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando carga de dados no PostgreSQL (Supabase)...")

    db_url = os.getenv("DB_URL")
    if not db_url:
        print("❌ Erro: Variável DB_URL não encontrada no arquivo .env")
        return

    engine = create_engine(db_url)

    # MAPEAMENTO ATUALIZADO: dim_proposicoes agora puxa da pasta Gold com o sufixo _ia
    cargas = [
        {"caminho": os.path.join(pasta_silver, "dim_deputados.csv"), "tabela": "dim_deputados", "tipo": "Dimensão"},
        {"caminho": os.path.join(pasta_gold, "dim_proposicoes_ia.csv"), "tabela": "dim_proposicoes",
         "tipo": "Dimensão Enriquecida com IA"},
        {"caminho": os.path.join(pasta_silver, "fato_despesas.csv"), "tabela": "fato_despesas", "tipo": "Fato"}
    ]

    for item in cargas:
        caminho_arquivo = item["caminho"]

        if not os.path.exists(caminho_arquivo):
            print(f"⚠️ Alerta: Arquivo {caminho_arquivo} não encontrado para carga. Pulando...")
            continue

        print(f"-> Carregando tabela {item['tipo']} '{item['tabela']}'...")
        df = pd.read_csv(caminho_arquivo, sep=";")

        if "Data_Despesa" in df.columns:
            df["Data_Despesa"] = pd.to_datetime(df["Data_Despesa"], errors="coerce")

        # Envia para o PostgreSQL na nuvem
        df.to_sql(
            name=item["tabela"],
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=5000,
            method="multi"
        )
        print(f"   ✓ {df.shape[0]} linhas inseridas com sucesso na tabela '{item['tabela']}'.")

    print(f"\n======== ETAPA DE CARGA CONCLUÍDA ========")
    print(f"Todas as tabelas (incluindo IA) estão na nuvem do Supabase!")
    print(f"==========================================")


if __name__ == "__main__":
    carregar_dados_no_supabase()