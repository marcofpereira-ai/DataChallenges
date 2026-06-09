# 🏛️ Bússola Pública - Pipeline de Inteligência Governamental com IA

[![Python](https://img.shields.io/badge/Engine-Python_3.12_||_Pandas-yellow?style=flat-square&logo=python)](https://pandas.pydata.org/)
[![Environment](https://img.shields.io/badge/Package_Manager-uv-purple?style=flat-square)](https://github.com/astral-sh/uv)
[![PostgreSQL](https://img.shields.io/badge/Data_Warehouse-Supabase_PostgreSQL-blue?style=flat-square&logo=postgresql)](https://supabase.com/)
[![OpenAI](https://img.shields.io/badge/IA_Generativa-OpenAI_API-green?style=flat-square&logo=openai)](https://openai.com/)
[![Parquet](https://img.shields.io/badge/Storage-Apache_Parquet-red?style=flat-square)](https://parquet.apache.org/)

## 📝 Cenário de Negócio & Desafio

Este projeto consolida uma solução real de Engenharia de Dados desenvolvida para a **Bússola Pública**, uma consultoria de relações governamentais especializada em prover inteligência estratégica e analítica sobre o ecossistema legislativo brasileiro para clientes corporativos. 

**O Problema:** Originalmente, o monitoramento das atividades parlamentares, gastos de deputados e o teor de votações na Câmara era realizado através de processos manuais e planilhas descentralizadas. Esse formato gerava severo atraso na tomada de decisão, assimetria de informações, erros de categorização temática e impossibilidade de escala analítica.

**A Solução:** Um pipeline de dados robusto, resiliente e totalmente automatizado estruturado sob a **Arquitetura Medallion (Bronze/Raw → Silver → Gold)**. A solução extrai dados de deputados, partidos, despesas e votações direto da API da Câmara Federal, trata e tipaga as informações via Pandas, aplica Inteligência Artificial Cognitiva (Embeddings + LLM GPT-4o-mini) para categorização e geração de resumos executivos de negócios, otimiza o armazenamento analítico local em formato colunar Parquet e consolida o Data Warehouse na nuvem através do Supabase (PostgreSQL).

---

## 🏗️ Arquitetura da Solução e Fluxo de Dados

O ecossistema foi projetado utilizando práticas modernas de engenharia, estruturando o pipeline em camadas sequenciais de dados governadas por um orquestrador central (`main.py`):

1. **Camada Bronze (Raw Stage):** Ingestão isolada dos dados brutos em arquivos JSON diretamente da API pública da Câmara dos Deputados. Conta com políticas rigorosas de resiliência, incluindo *Retry Loops* com recuo de tempo (*backoff*) e timeouts estendidos para blindar o pipeline contra instabilidades de rede e erros de servidor (`504 Gateway Timeout`), garantindo a captura íntegra de mais de 5.000 registros históricos.
2. **Camada Silver (Processed Stage):** Processamento, limpeza e higienização dos dados usando Pandas. Nesta etapa, são aplicadas as regras de negócio: strings têm espaços limpos, colunas administrativas da API são descartadas, chaves substitutas (IDs) são padronizadas e tipos temporais/numéricos são convertidos para o padrão do banco de dados, gerando esquemas tabulares em arquivos CSV estruturados.
3. **Camada Gold Stage (Analytics & Parquet):** Conversão otimizada dos dados da camada Silver para arquivos binários e colunares **Apache Parquet (com compressão Snappy)**. Essa etapa assegura alta performance para queries analíticas locais, redução drástica do espaço em disco e tipagem forte nativa de datas e IDs para ferramentas de BI.
4. **Camada de Enriquecimento Cognitivo (IA):** Integração paralela com a API da OpenAI. Utiliza o modelo `text-embedding-3-small` para vetorizar as ementas dos projetos de lei e classificá-las por similaridade de cosseno em 10 macrotemas corporativos estratégicos. Em seguida, o modelo `gpt-4o-mini` gera resumos executivos focados em impactos de mercado em até 3 linhas.
5. **Camada Cloud Load (Data Warehouse):** Carga incremental automatizada via SQLAlchemy com inserção otimizada em blocos (*chunksize*) para a nuvem do Supabase, criando e populando um modelo dimensional estrela pronto para consumo.

---

## 📊 Modelagem do Data Warehouse (Star Schema)

Os dados são carregados no banco de dados seguindo a modelagem dimensional para otimizar a performance de relatórios e painéis no Power BI:

* **Tabelas Fato:**
  * `fato_despesas`: Registra os gastos parlamentares detalhados por fornecedor, CNPJ, tipo de despesa e valores líquidos. (Conecta-se a `dim_deputados`).
  * `fato_votacoes`: Consolida o histórico de eventos de votações ocorridas na Câmara, indicando o órgão legislativo, efeito prático e flag booleana de aprovação.
* **Tabelas Dimensão:**
  * `dim_deputados`: Cadastro completo dos parlamentares ativos.
  * `dim_partidos`: Listagem padronizada dos partidos políticos brasileiros, servindo de filtro corporativo.
  * `dim_proposicoes`: Contexto descritivo dos projetos de lei e emendas legislativas.
  * `dim_proposicoes_ia`: Extensão da dimensão de proposições enriquecida com os campos analíticos `Tema_IA` e `Resumo_Executivo_IA`.

---

## 🛠️ Tecnologias Utilizadas & Justificativas

* **Python 3.12:** Linguagem base de todo o ecossistema devido à flexibilidade e maturidade das bibliotecas de dados.
* **UV Package Manager:** Gerenciador de pacotes de última geração, responsável pela criação rápida do ambiente virtual (`.venv`) e instalação ultrarrápida de dependências.
* **Pandas:** Framework essencial utilizado para a transformação, junção, filtros e tipagem forte das colunas de dados.
* **PyArrow & Parquet:** Formato colunar escolhido para a camada Gold visando compressão e performance analítica superior ao CSV tradicional.
* **OpenAI (Embeddings + Chat):** Camada de IA responsável por transformar textos jurídicos complexos em insights analíticos claros de mercado.
* **Supabase (PostgreSQL) & SQLAlchemy:** Infraestrutura robusta e segura em nuvem para hospedar as tabelas relacionais do Data Warehouse sem complexidade de gerenciamento de servidores.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de possuir o **Python 3.12+** e o gerenciador **uv** instalados em sua máquina.

### 2. Configuração do Ambiente
Clone o repositório e inicialize o ambiente virtual através do terminal na raiz do projeto:
```bash
# Cria e sincroniza o ambiente virtual usando o uv
uv venv