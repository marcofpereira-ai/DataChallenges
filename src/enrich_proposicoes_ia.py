import os
import json
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

# Carrega as chaves do .env
load_dotenv()

# Inicializa o cliente oficial da OpenAI (ele puxa a chave do .env automaticamente)
client = OpenAI()

# 1. Definição dos Macrotemas Estratégicos da Bússola Pública
TEMAS_ALVO = [
    "Finanças e Tributação (Impostos, Reforma Tributária, Subsídios)",
    "Tecnologia, Inteligência Artificial e Inovação (Regulação de IA, Dados, Internet)",
    "Meio Ambiente e Sustentabilidade (Clima, Carbono, Saneamento, Energia)",
    "Trabalho e Previdência (Direitos Trabalhistas, Emprego, Aposentadoria)",
    "Saúde e Vigilância Sanitária (Hospitais, Medicamentos, Pandemias)",
    "Educação e Cultura (Escolas, Universidades, Incentivos Culturais)",
    "Defesa e Segurança Pública (Polícia, Armas, Fronteiras, Forças Armadas)",
    "Infraestrutura e Transportes (Rodovias, Portos, Aeroportos, Logística)",
    "Direito Civil e Penal (Código Penal, Contratos, Processos Judiciais)",
    "Agronegócio e Setor Produtivo (Agricultura, Pecuária, Terras)"
]


def obter_embedding(texto):
    """Gera o vetor matemático (embedding) de um texto usando a OpenAI"""
    try:
        resposta = client.embeddings.create(
            input=[texto],
            model="text-embedding-3-small"
        )
        return resposta.data[0].embedding
    except Exception as e:
        print(f"❌ Erro ao gerar embedding: {e}")
        return None


def calcular_similaridade(vetor_a, vetor_b):
    """Calcula a similaridade de cosseno entre dois vetores"""
    dot_product = np.dot(vetor_a, vetor_b)
    norm_a = np.linalg.norm(vetor_a)
    norm_b = np.linalg.norm(vetor_b)
    return dot_product / (norm_a * norm_b)


def gerar_resumo_executivo(ementa):
    """Gera um resumo executivo de 3 linhas focado em negócios"""
    try:
        prompt = (
            "Você é um analista sênior de Relações Governamentais da consultoria Bússola Pública. "
            "Sua tarefa é resumir a ementa de um projeto de lei da Câmara dos Deputados de forma ultra-direta. "
            "Regras estritas:\n"
            "1. Escreva um resumo executivo em no máximo 3 linhas.\n"
            "2. Use linguagem clara, sem jargões jurídicos excessivos.\n"
            "3. Foque no impacto prático para empresas, negócios ou cidadãos.\n\n"
            f"Ementa para resumir: {ementa}"
        )

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente corporativo direto e analítico."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Erro ao gerar resumo: {e}")
        return "Resumo indisponível."


def enriquecer_proposicoes_com_ia():
    # === ANCORAGEM DE CAMINHO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)
    caminho_silver = os.path.join(base_dir, "data", "silver", "dim_proposicoes.csv")
    caminho_gold_ia = os.path.join(base_dir, "data", "gold", "dim_proposicoes_ia.csv")
    # ============================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a Camada de IA (Embeddings + LLM)...")

    if not os.path.exists(caminho_silver):
        print("❌ Erro: Tabela dim_proposicoes.csv não encontrada na camada Silver.")
        return

    # Carrega a dimensão de proposições
    df = pd.read_csv(caminho_silver, sep=";")

    # 🚨 TRAVA DE SEGURANÇA E CUSTO: Vamos processar apenas as 10 primeiras para validar sem gastar quase nada
    print("⚠️ ATENÇÃO: Executando trava de segurança. Processando apenas as 10 primeiras linhas para teste.")
    df_teste = df.head(10).copy()

    # Pré-calcula os embeddings dos nossos 10 temas fixos para economizar chamadas de API
    print("-> Pré-calculando vetores dos 10 macrotemas da consultoria...")
    embeddings_temas = {tema: obter_embedding(tema) for tema in TEMAS_ALVO}

    LISTA_TEMAS_CLASSIFICADOS = []
    LISTA_RESUMOS_EXECUTIVOS = []

    for idx, linha in df_teste.iterrows():
        id_prop = linha["ID_Proposicao"]
        ementa = str(linha["Ementa"])

        print(f"   [Processando {idx + 1}/10] ID: {id_prop}...")

        # --- CAMINHO A: CLASSIFICAÇÃO VIA EMBEDDINGS ---
        embedding_ementa = obter_embedding(ementa)

        if embedding_ementa:
            maior_similaridade = -1
            tema_escolhido = "Outros / Não Classificado"

            # Compara o vetor da ementa com o vetor de cada um dos 10 temas
            for tema, embedding_tema in embeddings_temas.items():
                if embedding_tema:
                    sim = calcular_similaridade(embedding_ementa, embedding_tema)
                    if sim > maior_similaridade:
                        maior_similaridade = sim
                        tema_escolhido = tema.split(" (")[0]  # Pega só o nome principal do tema

            LISTA_TEMAS_CLASSIFICADOS.append(tema_escolhido)
        else:
            LISTA_TEMAS_CLASSIFICADOS.append("Erro na Classificação")

        # --- CAMINHO B: RESUMO EXECUTIVO VIA LLM ---
        resumo = gerar_resumo_executivo(ementa)
        LISTA_RESUMOS_EXECUTIVOS.append(resumo)

    # Injeta as novas colunas geradas por IA no DataFrame de teste
    df_teste["Tema_IA"] = LISTA_TEMAS_CLASSIFICADOS
    df_teste["Resumo_Executivo_IA"] = LISTA_RESUMOS_EXECUTIVOS

    # Salva o resultado enriquecido na pasta Gold
    os.makedirs(os.path.dirname(caminho_gold_ia), exist_ok=True)
    df_teste.to_csv(caminho_gold_ia, sep=";", index=False, encoding="utf-8-sig")

    print(f"\n======== ETAPA DE IA CONCLUÍDA ========")
    print(f"Arquivo enriquecido salvo localmente em: {caminho_gold_ia}")
    print("========================================")


if __name__ == "__main__":
    enriquecer_proposicoes_com_ia()