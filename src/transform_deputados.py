import os
import json
import pandas as pd
from datetime import datetime


def transformar_deputados():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    caminho_origem = os.path.join(base_dir, "data", "raw", "deputados_bruto.json")
    pasta_destino = os.path.join(base_dir, "data", "silver")
    caminho_salvamento = os.path.join(pasta_destino, "dim_deputados.csv")
    # =====================================

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a transformação da Dimensão Deputados...")

    # 1. Valida se o arquivo bruto existe
    if not os.path.exists(caminho_origem):
        print(f"❌ Erro: Arquivo bruto não encontrado em: {caminho_origem}")
        return

    # 2. Carrega o JSON bruto e joga para dentro do Pandas DataFrame
    with open(caminho_origem, "r", encoding="utf-8") as f:
        dados_brutos = json.load(f)

    df = pd.DataFrame(dados_brutos)
    print(f"-> Dados brutos carregados. Colunas originais: {list(df.columns)}")

    # 3. LIMPEZA E TRATAMENTO DE DADOS (Business Rules)
    # A API traz colunas como 'uri' e 'uriPartido' que só servem para a web. Vamos eliminá-las.
    colunas_para_remover = ["uri", "uriPartido"]
    df = df.drop(columns=colunas_para_remover, errors="ignore")

    # Garante que textos textuais não tenham espaços em branco extras nas pontas
    df["nome"] = df["nome"].astype(str).str.strip()
    df["siglaPartido"] = df["siglaPartido"].astype(str).str.strip()
    df["siglaUf"] = df["siglaUf"].astype(str).str.upper().str.strip()  # Garante UF em maiúsculo

    # Renomeia as colunas para um padrão amigável para o seu modelo dimensional (Star Schema) no Power BI
    dicionario_renomear = {
        "id": "ID_Deputado",
        "nome": "Nome_Deputado",
        "siglaPartido": "Partido",
        "siglaUf": "UF",
        "idLegislatura": "ID_Legislatura",
        "urlFoto": "URL_Foto"
    }
    df = df.rename(columns=dicionario_renomear)

    # 4. SALVAMENTO NA CAMADA SILVER
    os.makedirs(pasta_destino, exist_ok=True)

    # Salvamos em CSV com separador de ponto e vírgula (excelente para o mercado brasileiro) e sem o índice do Pandas
    df.to_csv(caminho_salvamento, sep=";", index=False, encoding="utf-8-sig")

    print(f"\n======== PARTE SILVER CONCLUÍDA ========")
    print(f"Tabela 'dim_deputados' gerada com sucesso!")
    # df.shape traz a quantidade de (linhas, colunas) do resultado
    print(f"Dimensões finais: {df.shape[0]} linhas e {df.shape[1]} colunas.")
    print(f"Arquivo salvo em: {caminho_salvamento}")
    print(f"========================================")


if __name__ == "__main__":
    transformar_deputados()