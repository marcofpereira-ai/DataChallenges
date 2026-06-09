import os
import requests
import json
import time
from datetime import datetime


def extrair_votacoes_2026():
    """
    Busca todas as votações ocorridas na Câmara dos Deputados no ano de 2026 salvando o arquivo na raiz.
    """
    url_base = "https://dadosabertos.camara.leg.br/api/v2/votacoes"
    ano_atual = 2026
    mes_atual = datetime.now().month

    meses_periodos = [
        ("01-01", "01-31"),
        ("02-01", "02-28"),
        ("03-01", "03-31"),
        ("04-01", "04-30"),
        ("05-01", "05-31"),
        ("06-01", datetime.now().strftime("%m-%d"))
    ]

    headers = {
        "Accept": "application/json"
    }

    todas_votacoes = []

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extração histórica segmentada de votações de 2026...")

    for i in range(mes_atual):
        inicio_sub, fim_sub = meses_periodos[i]
        data_inicio = f"{ano_atual}-{inicio_sub}"
        data_fim = f"{ano_atual}-{fim_sub}"

        print(f"\n📅 Coletando período: {data_inicio} até {data_fim}")
        pagina = 1

        while True:
            params = {
                "dataInicio": data_inicio,
                "dataFim": data_fim,
                "itens": 100,
                "ordem": "ASC",
                "ordenarPor": "dataHoraRegistro",
                "pagina": pagina
            }

            tentativas_maximas = 3
            sucesso_pagina = False
            dados_pagina = {}

            for tentativa in range(tentativas_maximas):
                try:
                    response = requests.get(url_base, params=params, headers=headers, timeout=30)

                    if response.status_code in [502, 503, 504]:
                        print(
                            f"⏳ [Aviso] Servidor da Câmara instável (Status {response.status_code}) na página {pagina} (Tentativa {tentativa + 1}/{tentativas_maximas}). Retentando em 2s...")
                        time.sleep(2)
                        continue

                    elif response.status_code != 200:
                        print(f"⚠️ Resposta inesperada no período {data_inicio}. Status: {response.status_code}")
                        break

                    response.raise_for_status()
                    dados_pagina = response.json()
                    elementos = dados_pagina.get("dados", [])

                    todas_votacoes.extend(elementos)
                    sucesso_pagina = True
                    break

                except requests.exceptions.Timeout:
                    print(
                        f"⏳ [Aviso] Timeout de rede na página {pagina} (Tentativa {tentativa + 1}/{tentativas_maximas}). Reaplicando chamada em 2s...")
                    time.sleep(2)
                except requests.exceptions.RequestException as e:
                    print(f"❌ Erro crítico de comunicação na página {pagina}: {e}")
                    break

            if not sucesso_pagina or not dados_pagina.get("dados"):
                break

            links = dados_pagina.get("links", [])
            tem_proxima = any(link.get("rel") == "next" for link in links)

            if not tem_proxima:
                break

            pagina += 1

    # Persistência dinâmica garantindo a gravação na raiz do projeto
    if todas_votacoes:
        # Ancoragem dinâmica escalável para a raiz
        caminho_script = os.path.abspath(__file__)
        diretorio_src = os.path.dirname(caminho_script)
        raiz_projeto = os.path.dirname(diretorio_src)

        pasta_destino = os.path.join(raiz_projeto, "data", "raw")
        os.makedirs(pasta_destino, exist_ok=True)

        caminho_salvamento = os.path.join(pasta_destino, "votacoes_bruto.json")

        with open(caminho_salvamento, "w", encoding="utf-8") as f:
            json.dump(todas_votacoes, f, ensure_ascii=False, indent=4)

        print(f"\n======== SUCESSO ========")
        print(f"Total de votações consolidadas em 2026: {len(todas_votacoes)}")
        print(f"Arquivo salvo com sucesso na RAIZ em: {caminho_salvamento}")
        print(f"=========================")
    else:
        print("⚠️ Nenhuma votação pôde ser extraída.")


if __name__ == "__main__":
    extrair_votacoes_2026()