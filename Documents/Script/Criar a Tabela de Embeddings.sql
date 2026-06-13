-- 1. Tabela Dimensão: Partidos (Criar primeiro)
CREATE TABLE IF NOT EXISTS public.partidos (
    id_partido BIGINT PRIMARY KEY,
    sigla VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    uri VARCHAR(255)
);

-- 2. Garantir que a tabela deputados faça referência a partidos (Ajuste se necessário)
-- ALTER TABLE public.deputados ADD CONSTRAINT fk_deputados_partidos FOREIGN KEY (partido_id) REFERENCES public.partidos(id_partido);

-- 3. Tabela Fato: Votações
CREATE TABLE IF NOT EXISTS public.votacoes (
    id_votacao VARCHAR(100) PRIMARY KEY, -- A API costuma usar strings longas ou IDs complexos para votações
    id_proposicao BIGINT REFERENCES public.proposicoes(id_proposicao) ON DELETE SET NULL,
    data_votacao TIMESTAMP WITH TIME ZONE,
    descricao TEXT,
    aprovada BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, now()) NOT NULL
);