import os
import requests
import json
from datetime import datetime


def carregar_dados_existentes(caminho_arquivo):
    """Lê o arquivo local se ele já existir para evitar perda de histórico."""
    if os.path.exists(caminho_arquivo):
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Arquivo existente corrompido ou vazio. Iniciando nova base.")
            return []
    return []


def extrair_proposicoes_2026():
    url_base = "https://dadosabertos.camara.leg.br/api/v2/proposicoes"

    # === ANCORAGEM DE CAMINHO ABSOLUTO ===
    # os.path.abspath(__file__) descobre onde o 'extract_proposicoes.py' está fisicamente (pasta src)
    # os.path.dirname volta os níveis até a raiz do seu projeto 'DataChallenges'
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)

    # Monta o caminho exato independente de onde o terminal ou o 'uv' chame o script
    pasta_destino = os.path.join(base_dir, "data", "raw", "legado_2026")
    caminho_salvamento = os.path.join(pasta_destino, "proposicoes_2026.json")
    # =====================================

    # 1. Carrega o histórico que já foi salvo anteriormente
    dados_locais = carregar_dados_existentes(caminho_salvamento)
    ids_existentes = {str(p["id"]) for p in dados_locais}

    params = {
        "ano": 2026,
        "itens": 100,
        "ordem": "ASC",
        "ordenarPor": "id"
    }
    headers = {"Accept": "application/json"}

    novos_dados = []
    pagina = 1

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extração incremental...")
    print(f"-> Verificando armazenamento local: {caminho_salvamento}")
    print(f"-> Base local carregada com sucesso! Já temos {len(ids_existentes)} proposições guardadas.")

    while True:
        params["pagina"] = pagina
        try:
            response = requests.get(url_base, params=params, headers=headers, timeout=15)
            response.raise_for_status()

            dados_pagina = response.json()
            elementos = dados_pagina.get("dados", [])

            if not elementos:
                break

            # 2. Checagem de ID ultra rápida (O(1)) para capturar apenas o que for novo
            for item in elementos:
                if str(item["id"]) not in ids_existentes:
                    novos_dados.append(item)

            # Controle de fluxo da paginação
            links = dados_pagina.get("links", [])
            if not any(link.get("rel") == "next" for link in links):
                break

            pagina += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão na página {pagina}: {e}")
            break

    # 3. Bloco de salvamento e mesclagem (Merge)
    if novos_dados:
        os.makedirs(pasta_destino, exist_ok=True)
        dados_finais = dados_locais + novos_dados

        with open(caminho_salvamento, "w", encoding="utf-8") as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=4)

        print(f"\n======== ATUALIZAÇÃO CONCLUÍDA ========")
        print(f"Novas proposições identificadas e inseridas: {len(novos_dados)}")
        print(f"Total consolidado no seu Data Lake: {len(dados_finais)}")
        print(f"=======================================")
    else:
        print("\n✓ Sem novidades! Sua base local já está perfeitamente sincronizada com a API.")


if __name__ == "__main__":
    extrair_proposicoes_2026()