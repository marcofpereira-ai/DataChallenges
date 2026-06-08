import os
import json
import pandas as pd
from datetime import datetime


def transformar_despesas():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    caminho_origem = os.path.join(base_dir, "data", "raw", "legado_2026", "despesas_2026.json")
    pasta_destino = os.path.join(base_dir, "data", "silver")
    caminho_salvamento = os.path.join(pasta_destino, "fato_despesas.csv")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a transformação da Fato Despesas 2026...")

    # 1. Valida se o arquivo bruto de despesas existe
    if not os.path.exists(caminho_origem):
        print(f"❌ Erro: Arquivo bruto de despesas não encontrado em: {caminho_origem}")
        return

    # 2. Carrega o JSON bruto para o DataFrame
    with open(caminho_origem, "r", encoding="utf-8") as f:
        dados_brutos = json.load(f)

    df = pd.DataFrame(dados_brutos)
    print(f"-> Dados brutos carregados: {df.shape[0]} registros encontrados.")

    # 3. LIMPEZA, TRATAMENTO E TIPAGEM (Regras de Negócio)

    # Remove colunas de controle da API que não agregam valor ao BI
    colunas_para_remover = ["urlDocumento", "idDocumento", "idTipoDocumento", "codDocumento"]
    df = df.drop(columns=colunas_para_remover, errors="ignore")

    # Tratamento de Datas: Converte a coluna 'dataDocumento' para datetime (formato YYYY-MM-DD)
    # Qualquer data inválida vira NaT (Not a Time) e depois preenchemos com uma data padrão se necessário
    df["dataDocumento"] = pd.to_datetime(df["dataDocumento"], errors="coerce")

    # Tipagem Numérica: Garante que os valores líquidos e brutos sejam numéricos para cálculos de soma/média
    df["valorLiquido"] = pd.to_numeric(df["valorLiquido"], errors="coerce").fillna(0.0)
    df["valorGlosa"] = pd.to_numeric(df["valorGlosa"], errors="coerce").fillna(0.0)

    # Limpeza de strings: Remove espaços em branco dos textos dos fornecedores e tipos de despesa
    df["tipoDespesa"] = df["tipoDespesa"].astype(str).str.strip()
    df["nomeFornecedor"] = df["nomeFornecedor"].astype(str).str.strip()
    df["cnpjCpfFornecedor"] = df["cnpjCpfFornecedor"].astype(str).str.strip()

    # Renomeia as colunas para o padrão amigável do modelo dimensional (Tabela Fato)
    dicionario_renomear = {
        "id_deputado_origem": "ID_Deputado",  # Nossa chave de ligação (FK)
        "dataDocumento": "Data_Despesa",
        "tipoDespesa": "Tipo_Despesa",
        "nomeFornecedor": "Fornecedor",
        "cnpjCpfFornecedor": "CNPJ_CPF_Fornecedor",
        "valorLiquido": "Valor_Liquido",
        "valorGlosa": "Valor_Glosa",
        "numRessarcimento": "Num_Ressarcimento",
        "ano": "Ano",
        "mes": "Mes"
    }
    df = df.rename(columns=dicionario_renomear)

    # Organiza a ordem das colunas de forma lógica (opcional, mas boa prática para visualização humana)
    colunas_ordenadas = [
        "ID_Deputado", "Data_Despesa", "Ano", "Mes", "Tipo_Despesa",
        "Fornecedor", "CNPJ_CPF_Fornecedor", "Valor_Liquido", "Valor_Glosa"
    ]
    # Filtra apenas as colunas que renomeamos e que existem no DataFrame
    colunas_ordenadas = [c for c in colunas_ordenadas if c in df.columns]
    df = df[colunas_ordenadas]

    # 4. SALVAMENTO NA CAMADA SILVER (Como nossa Tabela Fato)
    os.makedirs(pasta_destino, exist_ok=True)

    # Salvando em CSV com o encoding 'utf-8-sig' para abrir perfeitamente no Excel brasileiro se necessário
    df.to_csv(caminho_salvamento, sep=";", index=False, encoding="utf-8-sig")

    print(f"\n======== PARTE SILVER CONCLUÍDA ========")
    print(f"Tabela 'fato_despesas' gerada com sucesso!")
    print(f"Dimensões finais: {df.shape[0]} linhas e {df.shape[1]} colunas.")
    print(f"Arquivo salvo em: {caminho_salvamento}")
    print(f"========================================")


if __name__ == "__main__":
    transformar_despesas()