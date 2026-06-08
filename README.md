# 🛰️ Radar Legislativo - Inteligência Governamental com IA

## 🏢 O Cenário de Negócio: Bússola Pública
A **Bússola Pública** é uma consultoria de relações governamentais que vende inteligência legislativa para grandes clientes corporativos. Anteriormente, o monitoramento de projetos de lei, votações e gastos de deputados era feito manualmente por analistas que preenchiam planilhas pessoais — um processo descentralizado, suscetível a erros e impossível de escalar.

**A Solução:** Desenvolvimento de um pipeline de Engenharia de Dados automatizado, resiliente e escalável que extrai dados diários da API aberta da Câmara dos Deputados, padroniza as informações seguindo a arquitetura Medalhão e armazena os dados estruturados em um banco de dados relacional na nuvem, pronto para consumo analítico e enriquecido com Inteligência Artificial.

---

## 🏗️ Arquitetura do Pipeline de Dados (Medalhão)

O projeto foi construído seguindo os padrões modernos de Engenharia de Dados, dividindo o ciclo de vida dos dados em camadas de maturação:

1. **Camada Raw (Bronze):** Ingestão e salvamento do JSON bruto local para garantir idempotência.
2. **Camada Silver:** Limpeza, tipagem, deduplicação e tratamento de strings usando **Pandas**.
3. **Camada Gold:** Otimização e armazenamento analítico em formato colunar **Parquet** (`pyarrow`).
4. **Camada Cloud (PostgreSQL):** Ingestão do modelo dimensional no **Supabase** via `SQLAlchemy`.

---

## 📋 Detalhamento do Desenvolvimento por Etapas

### 🧭 Etapa 1: Exploração da API
Análise minuciosa da documentação da API de Dados Abertos da Câmara dos Deputados para mapeamento dos endpoints estratégicos (`/deputados`, `/proposicoes` e `/deputados/{id}/despesas`), identificando chaves de relacionamento, volumetria e regras de paginação.

### 🔌 Etapa 2: Extração Resiliente (Python)
Desenvolvimento de scripts modulares em Python utilizando a biblioteca `requests` para o consumo dos dados.
* **Garantia de Idempotência:** Os dados brutos são salvos localmente em JSON antes de qualquer transformação. Se o pipeline falhar adiante, não há necessidade de re-onerar a API.
* **Tratamento de Erros e Rate Limit:** Implementação de blocos `try/except` para falhas de rede, controle de paginação dinâmica via laços `while` e pausas milimétricas estratégicas para respeitar as políticas de requisições da Câmara.

### ⚡ Etapa 3: Transformação (Pandas) e Carga em Nuvem (PostgreSQL)
* **Modelagem Dimensional (Star Schema):** Estruturação dos dados brutos em tabelas de dimensões (`dim_deputados`, `dim_proposicoes`) e fatos (`fato_despesas`), estabelecendo chaves primárias e estrangeiras transparentes.
* **Qualidade de Dados:** Remoção de colunas web redundantes, padronização de siglas partidárias e estados (UFs), conversão rigorosa de strings de datas para formato `datetime` e garantia de tipagem flutuante para valores monetários (gerando mais de 70.000 linhas de despesas tratadas apenas para o ano corrente).
* **Carga Cloud:** Ingestão otimizada em lotes (`chunksize`) utilizando `SQLAlchemy` para o **Supabase (PostgreSQL)** na nuvem.

### 🧠 Etapa 4: Camada de Inteligência Artificial
*(Fase em desenvolvimento)* - Integração com LLMs via API para enriquecimento das proposições.

### 🎛️ Etapa 5: Automação e Orquestração (n8n)
*(Fase em desenvolvimento)* - Criação de workflows automatizados para monitoramento e alertas.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Python 3.10+
* Gerenciador de pacotes virtualizado **`uv`** instalado na máquina.

### 1. Clonar o Repositório e Instalar Dependências
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd DataChallenges
uv pip install -r requirements.txt