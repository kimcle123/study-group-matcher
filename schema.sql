-- Criação da Base de Dados
CREATE DATABASE IF NOT EXISTS study_group_matcher
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE study_group_matcher;

-- 1. Tabela de Utilizadores
CREATE TABLE IF NOT EXISTS utilizadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    curso VARCHAR(100) NOT NULL,
    ano VARCHAR(10) DEFAULT NULL,
    estilo_estudo_pref VARCHAR(50) DEFAULT NULL,
    disponibilidade_matriz JSON DEFAULT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Tabela de Disponibilidades (Horários específicos por dia)
CREATE TABLE IF NOT EXISTS disponibilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT NOT NULL,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Tabela de Tópicos de Interesse
CREATE TABLE IF NOT EXISTS topicos_interesse (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT NOT NULL,
    topico VARCHAR(100) NOT NULL,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Tabela de Grupos de Estudo
CREATE TABLE IF NOT EXISTS grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    objetivo TEXT NOT NULL,
    disciplina VARCHAR(100) NOT NULL,
    criador_id INT NOT NULL,
    max_membros INT DEFAULT 6,
    aberto BOOLEAN DEFAULT FALSE,
    aprovar_pedidos BOOLEAN DEFAULT TRUE,
    proximo_encontro VARCHAR(100) DEFAULT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (criador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Tabela de Estilos de Estudo do Grupo
CREATE TABLE IF NOT EXISTS grupo_estilos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    estilo VARCHAR(50) NOT NULL,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. Tabela de Membros dos Grupos
CREATE TABLE IF NOT EXISTS membros_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    utilizador_id INT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    data_adesao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_grupo_utilizador (grupo_id, utilizador_id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Tabela de Pedidos de Adesão
CREATE TABLE IF NOT EXISTS pedidos_adesao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    utilizador_id INT NOT NULL,
    status ENUM('pendente', 'aceite', 'recusado') DEFAULT 'pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Tabela de Mensagens do Chat de Grupo
CREATE TABLE IF NOT EXISTS mensagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    utilizador_id INT NOT NULL,
    texto TEXT NOT NULL,
    enviada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

