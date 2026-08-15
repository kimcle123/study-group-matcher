CREATE DATABASE IF NOT EXISTS study_group_matcher;
USE study_group_matcher;

-- 1. Tabela de Utilizadores
CREATE TABLE IF NOT EXISTS utilizadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    curso VARCHAR(100) NOT NULL,
    estilo_estudo_pref ENUM('individual', 'em_grupo', 'focado_discussao', 'focado_exercicios') NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Disponibilidade dos Utilizadores
CREATE TABLE IF NOT EXISTS disponibilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT NOT NULL,
    dia_semana ENUM('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
);

-- 3. Tabela de Tópicos de Interesse por Utilizador
CREATE TABLE IF NOT EXISTS topicos_interesse (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT NOT NULL,
    topico VARCHAR(100) NOT NULL,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
);

-- 4. Tabela de Grupos de Estudo
CREATE TABLE IF NOT EXISTS grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    curso VARCHAR(100) NOT NULL,
    criador_id INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (criador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
);

-- 5. Tabela de Membros dos Grupos
CREATE TABLE IF NOT EXISTS membros_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    utilizador_id INT NOT NULL,
    funcao ENUM('admin', 'membro') DEFAULT 'membro',
    status ENUM('pendente', 'aprovado') DEFAULT 'aprovado',
    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE,
    UNIQUE(grupo_id, utilizador_id)
);

-- 6. Tabela do Sistema de Mensagens (Chat)
CREATE TABLE IF NOT EXISTS mensagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    emissor_id INT NOT NULL,
    conteudo TEXT NOT NULL,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (emissor_id) REFERENCES utilizadores(id) ON DELETE CASCADE
);