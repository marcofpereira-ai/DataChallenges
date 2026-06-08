import time
from datetime import datetime

# Importa as funções de execução de cada um dos seus scripts modulares
from src.extract_deputados import extrair_deputados
from src.extract_proposicoes import extrair_proposicoes_2026
from src.extract_despesas import extrair_despesas_2026
from src.transform_deputados import transformar_deputados
from src.transform_despesas import transformar_despesas
from src.transform_proposicoes import transformar_proposicoes
from src.gold_stage import processar_camada_gold
from src.enrich_proposicoes_ia import enriquecer_proposicoes_com_ia  # <-- Nova Importação de IA!
from src.load_to_supabase import carregar_dados_no_supabase


def executar_pipeline():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] INICIANDO PIPELINE DE DADOS INTEGRAL COM IA")
    print("=" * 60)

    inicio_geral = time.time()

    # --- ETAPA 1: EXTRAÇÃO (RAW STAGE) ---
    print("\n>>> FASE 1: EXTRAÇÃO DE DADOS BRUTOS (RAW) <<<")
    try:
        extrair_deputados()
        extrair_proposicoes_2026()
        extrair_despesas_2026()
    except Exception as e:
        print(f"❌ Falha crítica na fase de Extração: {e}")
        return

    # --- ETAPA 2: TRANSFORMAÇÃO (SILVER STAGE) ---
    print("\n>>> FASE 2: TRANSFORMAÇÃO E LIMPEZA (SILVER) <<<")
    try:
        transformar_deputados()
        transformar_despesas()
        transformar_proposicoes()
    except Exception as e:
        print(f"❌ Falha crítica na fase de Transformação: {e}")
        return

    # --- ETAPA 3: ANALYTICS OTIMIZADO (GOLD STAGE) ---
    print("\n>>> FASE 3: DISPONIBILIZAÇÃO EM PARQUET (GOLD) <<<")
    try:
        processar_camada_gold()
    except Exception as e:
        print(f"❌ Falha crítica na fase Gold local: {e}")
        return

    # --- ETAPA 4: ENRIQUECIMENTO COM INTELIGÊNCIA ARTIFICIAL ---
    print("\n>>> FASE 4: ENRIQUECIMENTO COM IA (EMBEDDINGS & LLM) <<<")
    try:
        enriquecer_proposicoes_com_ia()
    except Exception as e:
        print(f"❌ Falha crítica na fase de IA Generativa: {e}")
        return

    # --- ETAPA 5: INFRAESTRUTURA CLOUD (LOAD STAGE) ---
    print("\n>>> FASE 5: CARGA NO POSTGRESQL NUVEM (SUPABASE) <<<")
    try:
        carregar_dados_no_supabase()
    except Exception as e:
        print(f"❌ Falha crítica na fase de Carga Cloud: {e}")
        return

    # --- FINALIZAÇÃO ---
    tempo_total = (time.time() - inicio_geral) / 60
    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] PIPELINE INTEGRAL EXECUTADO COM SUCESSO! 🎉")
    print(f"Tempo total de processamento: {tempo_total:.2f} minutos")
    print("=" * 60)


if __name__ == "__main__":
    executar_pipeline()