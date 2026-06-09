import os
import requests
import json
from datetime import datetime


def extrair_partidos():
    """
    Busca a listagem completa de partidos políticos salvando o arquivo na pasta correta da raiz.
    """
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos"

    params = {
        "itens": 100,
        "ordem": "ASC",
        "ordenarPor": "sigla"
    }

    headers = {
        "Accept": "application/json"
    }

    todos_partidos = []
    pagina = 1

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a extração de partidos da API da Câmara...")

    while True:
        params["pagina"] = pagina
        print(f"-> Requisitando a página {pagina} para Partidos...")

        try:
            response = requests.get(url_base, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            dados_pagina = response.json()
            elementos = dados_pagina.get("dados", [])

            if not elementos:
                break

            todos_partidos.extend(elementos)

            links = dados_pagina.get("links", [])
            tem_proxima = any(link.get("rel") == "next" for link in links)

            if not tem_proxima:
                break

            pagina += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de comunicação com a API na página {pagina}: {e}")
            break

    # Persistência dinâmica garantindo a gravação na raiz do projeto
    if todos_partidos:
        # Ancoragem dinâmica escalável para a raiz
        caminho_script = os.path.abspath(__file__)
        diretorio_src = os.path.dirname(caminho_script)
        raiz_projeto = os.path.dirname(diretorio_src)

        pasta_destino = os.path.join(raiz_projeto, "data", "raw")
        os.makedirs(pasta_destino, exist_ok=True)

        caminho_salvamento = os.path.join(pasta_destino, "partidos_bruto.json")

        with open(caminho_salvamento, "w", encoding="utf-8") as f:
            json.dump(todos_partidos, f, ensure_ascii=False, indent=4)

        print(f"\n======== SUCESSO ========")
        print(f"Total de partidos extraídos: {len(todos_partidos)}")
        print(f"Arquivo salvo com sucesso na RAIZ em: {caminho_salvamento}")
        print(f"=========================")
    else:
        print("⚠️ Nenhum dado de partido foi extraído.")


if __name__ == "__main__":
    extrair_partidos()