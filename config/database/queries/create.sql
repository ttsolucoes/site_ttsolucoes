CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    senha_hash TEXT NOT NULL,
    cargo TEXT NOT NULL DEFAULT 'user',
    acesso_api BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_usuarios (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    usuario_id INTEGER NOT NULL,
    acao TEXT NOT NULL,
    detalhes TEXT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS novos_usuarios (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recuperar_acesso (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    usuario_id INTEGER NOT NULL,
    username TEXT,
    email TEXT,
    motivo TEXT,
    status TEXT DEFAULT 'a validar',
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE diagnostico_pessoal (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    empresa TEXT,
    relacao TEXT,
    email TEXT,
    telefone TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE diagnostico_eixo (
    id SERIAL PRIMARY KEY,
    diagnostico_id INT REFERENCES diagnostico_pessoal(id),
    eixo TEXT,
    media NUMERIC,
    respostas JSONB
);

CREATE TABLE diagnostico_final (
    id SERIAL PRIMARY KEY,
    diagnostico_id INT REFERENCES diagnostico_pessoal(id),
    media_final NUMERIC,
    proposta TEXT
);
