import os
import requests
import json
import time
from datetime import datetime


def carregar_ids_deputados(caminho_deputados):
    """Lê o arquivo de deputados existente para extrair a lista de IDs mapeados."""
    if not os.path.exists(caminho_deputados):
        print(f"❌ Erro: O arquivo de deputados não foi encontrado em: {caminho_deputados}")
        print("Por favor, execute o script 'extract_deputados.py' primeiro.")
        return []

    with open(caminho_deputados, "r", encoding="utf-8") as f:
        deputados = json.load(f)

    # Extrai apenas o ID de cada deputado da lista
    return [str(d["id"]) for d in deputados if "id" in d]


def extrair_despesas_2026():
    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    caminho_deputados = os.path.join(base_dir, "data", "raw", "deputados_bruto.json")
    pasta_destino = os.path.join(base_dir, "data", "raw", "legado_2026")
    caminho_salvamento = os.path.join(pasta_destino, "despesas_2026.json")
    # =====================================

    # 1. Recupera os IDs dos deputados para guiar a extração
    ids_deputados = carregar_ids_deputados(caminho_deputados)
    if not ids_deputados:
        return

    headers = {"Accept": "application/json"}
    todas_despesas = []

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a extração de Despesas de 2026...")
    print(f"-> Foram mapeados {len(ids_deputados)} deputados para consulta.")

    # 2. Loop iterativo por deputado (Looping de requisições encadeadas)
    for index, id_deputado in enumerate(ids_deputados, start=1):
        url_despesas = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado}/despesas"
        pagina = 1

        if index % 20 == 0 or index == len(ids_deputados):
            print(f"-> Progresso: Consultando despesas do deputado {index}/{len(ids_deputados)}...")

        while True:
            params = {
                "ano": 2026,
                "itens": 100,
                "pagina": pagina,
                "ordem": "ASC",
                "ordenarPor": "ano"
            }

            try:
                response = requests.get(url_despesas, params=params, headers=headers, timeout=15)

                # Se o deputado não tiver despesas lançadas ainda, a API pode retornar 404 ou lista vazia
                if response.status_code == 404:
                    break

                response.raise_for_status()
                dados_pagina = response.json()
                elementos = dados_pagina.get("dados", [])

                if not elementos:
                    break

                # Vincula o ID do deputado ao registro da despesa para garantir a rastreabilidade (Chave Estrangeira)
                for despesa in elementos:
                    despesa["id_deputado_origem"] = id_deputado
                    todas_despesas.append(despesa)

                # Paginação interna do deputado
                links = dados_pagina.get("links", [])
                if not any(link.get("rel") == "next" for link in links):
                    break

                pagina += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Alerta ao buscar despesas do ID {id_deputado} na página {pagina}: {e}")
                break

        # Pausa estratégica milimétrica (0.05s) para respeitar o Rate Limit da API e evitar bloqueios
        time.sleep(0.05)

    # 3. Salvamento dos dados brutos consolidados
    if todas_despesas:
        os.makedirs(pasta_destino, exist_ok=True)
        with open(caminho_salvamento, "w", encoding="utf-8") as f:
            json.dump(todas_despesas, f, ensure_ascii=False, indent=4)

        print(f"\n======== EXTRAÇÃO FINANCEIRA CONCLUÍDA ========")
        print(f"Total de registros de despesas em 2026: {len(todas_despesas)}")
        print(f"Arquivo consolidado salvo com sucesso em: {caminho_salvamento}")
        print(f"=================================================")
    else:
        print("⚠️ Nenhuma despesa foi capturada para os parâmetros informados.")


if __name__ == "__main__":
    extrair_despesas_2026()