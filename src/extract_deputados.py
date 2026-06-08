import os
import requests
import json
from datetime import datetime


def extrair_deputados():
    """
    Busca a listagem de deputados federais da API da Câmara dos Deputados
    respeitando o limite de 100 itens por requisição e realizando paginação.
    """
    url_base = "https://dadosabertos.camara.leg.br/api/v2/deputados"

    # Configuração dos parâmetros respeitando a documentação oficial da API
    params = {
        "itens": 100,  # Teto máximo permitido por chamada para maior eficiência
        "ordem": "ASC",
        "ordenarPor": "nome"
    }

    # Headers explícitos para garantir o retorno em JSON puro, conforme a arquitetura REST
    headers = {
        "Accept": "application/json"
    }

    todos_deputados = []
    pagina = 1

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando a extração dos dados da API da Câmara...")

    while True:
        params["pagina"] = pagina
        print(f"-> Requisitando a página {pagina}...")

        try:
            # Timeout de 15 segundos prevenindo travamentos caso a API esteja instável
            response = requests.get(url_base, params=params, headers=headers, timeout=15)

            # Se a API retornar erro (ex: 500, 404), interrompe e vai para o except
            response.raise_for_status()

            dados_pagina = response.json()
            elementos = dados_pagina.get("dados", [])

            if not elementos:
                break

            todos_deputados.extend(elementos)

            # Verificação inteligente de próxima página pelos links do cabeçalho da API
            links = dados_pagina.get("links", [])
            tem_proxima = any(link.get("rel") == "next" for link in links)

            if not tem_proxima:
                break

            pagina += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de comunicação com a API na página {pagina}: {e}")
            print("O pipeline salvará os dados coletados até o momento para evitar perda de histórico.")
            break

    # Se conseguimos extrair dados, salvamos o estado bruto (Data Lake - Raw Stage)
    if todos_deputados:
        # Garante que a pasta de destino exista
        os.makedirs("data/raw", exist_ok=True)

        caminho_salvamento = "data/raw/deputados_bruto.json"

        with open(caminho_salvamento, "w", encoding="utf-8") as f:
            json.dump(todos_deputados, f, ensure_ascii=False, indent=4)

        print(f"\n======== SUCESSO ========")
        print(f"Total de deputados extraídos: {len(todos_deputados)}")
        print(f"Arquivo salvo com sucesso em: {caminho_salvamento}")
        print(f"=========================")
    else:
        print("⚠️ Nenhum dado foi extraído. Verifique sua conexão ou o status da API.")


if __name__ == "__main__":
    extrair_deputados()