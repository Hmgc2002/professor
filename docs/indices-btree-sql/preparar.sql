-- Base de treino do curso «Índices B-tree em SQL».
-- Correr uma vez:   createdb treino_indices && psql -d treino_indices -f preparar.sql
-- Um milhão de linhas: grande o suficiente para os planos serem a sério,
-- pequeno o suficiente para caber em memória e correr em segundos.

DROP TABLE IF EXISTS encomendas;

CREATE TABLE encomendas (
  id          bigint      PRIMARY KEY,
  cliente_id  integer     NOT NULL,
  estado      text        NOT NULL,
  pais        text        NOT NULL,
  criada_em   timestamptz NOT NULL,
  total_cents integer     NOT NULL
);

INSERT INTO encomendas (id, cliente_id, estado, pais, criada_em, total_cents)
SELECT
  i,
  -- i::bigint em todas as multiplicações: i é integer e i*7919 passa dos 2^31
  -- por volta da linha 271 000. Erro encontrado a correr, não a ler.
  -- 50 000 clientes: ~20 encomendas cada. Coluna seletiva.
  1 + (i::bigint * 7919) % 50000,
  -- Coluna POUCO seletiva, e de propósito desequilibrada:
  -- é o caso que faz o planeador decidir de maneiras diferentes para a mesma coluna.
  CASE WHEN i % 100 = 0 THEN 'cancelada'
       WHEN i % 100 < 3  THEN 'pendente'
       ELSE 'entregue' END,
  (ARRAY['PT','ES','FR','DE','BR'])[1 + (i::bigint * 31) % 5],
  TIMESTAMPTZ '2023-01-01' + ((i % 1000) * INTERVAL '1 day') + ((i % 86400) * INTERVAL '1 second'),
  100 + (i::bigint * 37) % 49900
FROM generate_series(1, 1000000) AS i;

ANALYZE encomendas;
