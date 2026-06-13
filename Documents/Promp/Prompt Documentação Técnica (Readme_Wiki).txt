Atue como um Engenheiro/Arquiteto de Dados Sênior. Preciso gerar a documentação técnica (formato README.md) para o projeto 'Bússola Pública - Radar Legislativo'. O pipeline é composto por:
Camada de Ingestão: Script Python (main.py) rodando localmente (ou via GitHub Actions) que extrai dados de proposições, processa os arquivos em formato Parquet e alimenta a camada Gold no Supabase.*
Camada de IA: Enriquecimento analítico cognitivo feito via OpenAI (GPT-4o-mini) gerando resumos executivos automáticos e classificando as proposições por macrotemas corporativos.*
Camada de Orquestração e Mensageria: Fluxo automatizado no n8n que roda diariamente (Schedule Trigger) consumindo a API REST do Supabase com tratamento dinâmico de strings para filtros (in.("Tema1","Tema2")).*

Entrega: Nó de código JavaScript no n8n que normaliza os dados e distribui alertas formatados em HTML via Gmail e notificações rápidas em Markdown via Telegram.*
Gere uma documentação estruturada contendo: Arquitetura de Dados, Dicionário de Dados da tabela dim_proposicoes (campos: ID_Proposicao, Tipo_Proposicao, Numero_Proposicao, Ano_Proposicao, Ementa, Tema_IA, Resumo_Executivo_IA, dataApresentacao), fluxo de tratamento de erros no n8n para cenários sem novos dados (On Empty Result configurado como 'Never'), e instruções detalhadas de implantação.

