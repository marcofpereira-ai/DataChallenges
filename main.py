import time
from datetime import datetime

# ==============================================================================
# IMPORTAÇÃO DOS SCRIPTS MODULARES (ORQUESTRADOR CENTRAL)
# ==============================================================================
# FASE 1: Extração (Raw Stage)
from src.extract_deputados import extrair_deputados
from src.extract_partidos import extrair_partidos        # <-- Nova Importação!
from src.extract_votacoes import extrair_votacoes_2026   # <-- Nova Importação!
from src.extract_proposicoes import extrair_proposicoes_2026
from src.extract_despesas import extrair_despesas_2026

# FASE 2: Transformação (Silver Stage)
from src.transform_deputados import transformar_deputados
from src.transform_partidos import transformar_partidos    # <-- Nova Importação!
from src.transform_votacoes import transformar_votacoes    # <-- Nova Importação!
from src.transform_despesas import transformar_despesas
from src.transform_proposicoes import transformar_proposicoes

# FASE 3: Analytics Otimizado (Gold Stage - Parquet)
from src.gold_stage import processar_camada_gold

# FASE 4: Enriquecimento Cognitivo (Camada IA)
from src.enrich_proposicoes_ia import enriquecer_proposicoes_com_ia

# FASE 5: Infraestrutura Cloud (Load Stage)
from src.load_to_supabase import carregar_dados_no_supabase


def executar_pipeline():
    print("=" * 70)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] INICIANDO PIPELINE DE DADOS INTEGRAL: BÚSSOLA PÚBLICA 2026")
    print("=" * 70)

    inicio_geral = time.time()

    # --- ETAPA 1: EXTRAÇÃO (RAW STAGE) ---
    print("\n>>> FASE 1: EXTRAÇÃO DE DADOS BRUTOS (RAW) <<<")
    try:
        extrair_deputados()
        extrair_partidos()        # Coleta a tabela dimensão de partidos políticos
        extrair_votacoes_2026()   # Coleta as capturas históricas de votações
        extrair_proposicoes_2026()
        extrair_despesas_2026()
    except Exception as e:
        print(f"❌ Falha crítica na fase de Extração: {e}")
        return

    # --- ETAPA 2: TRANSFORMAÇÃO (SILVER STAGE) ---
    print("\n>>> FASE 2: TRANSFORMAÇÃO E LIMPEZA (SILVER) <<<")
    try:
        transformar_deputados()
        transformar_partidos()    # Limpa e gera a tabela dim_partidos
        transformar_votacoes()    # Trata efeitos, descrições e gera a fato_votacoes
        transformar_despesas()
        transformar_proposicoes()
    except Exception as e:
        print(f"❌ Falha crítica na fase de Transformação: {e}")
        return

    # --- ETAPA 3: ANALYTICS OTIMIZADO (GOLD STAGE) ---
    print("\n>>> FASE 3: DISPONIBILIZAÇÃO EM PARQUET (GOLD STAGE) <<<")
    try:
        # Este script já foi atualizado para processar os 5 arquivos locais para o formato .parquet
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
        # Este script já foi atualizado para subir as 5 tabelas finais espelhadas para a nuvem
        carregar_dados_no_supabase()
    except Exception as e:
        print(f"❌ Falha crítica na fase de Carga Cloud: {e}")
        return

    # --- FINALIZAÇÃO E MÉTRICAS ---
    tempo_total = (time.time() - inicio_geral) / 60
    print("\n" + "=" * 70)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] PIPELINE INTEGRAL EXECUTADO COM SUCESSO! 🎉")
    print(f"Tempo total de processamento: {tempo_total:.2f} minutos")
    print("=" * 70)


if __name__ == "__main__":
    executar_pipeline()