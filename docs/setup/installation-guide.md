# 🚀 Guia de Instalação e Configuração

| Metadado | Informação |
| :--- | :--- |
| **Autor(a)** | Equipa de Desenvolvimento |
| **Data de Criação** | 2026-08-22 |
| **Última Atualização** | 2026-08-22 |
| **Versão** | 1.0.0 |
| **Módulo** | Setup & Ambiente |

---

## 📋 Pré-requisitos
* **Python** 3.10+ instalado.
* **MySQL Server** 8.0+ instalado e em execução (porta padrão: `3306`).
* **Git** instalado.

---

## 🛠️ Passo a Passo de Instalação

### 1. Clonar o Repositório e Criar Ambiente Virtual
```powershell
# Criar o ambiente virtual (venv)
python -m venv .venv

# Ativar o ambiente virtual no Windows
.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências Python
```powershell
pip install -r requirements.txt
```

### 3. Configurar a Base de Dados MySQL
Execute o script de criação da base de dados e tabelas:

```powershell
# Execução direta pelo cliente MySQL
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database/schema.sql
```
*(Ou abra o ficheiro `database/schema.sql` no MySQL Workbench e execute).*

### 4. Configurar as Variáveis de Ambiente
Copie o ficheiro de exemplo `ficheiro.env.example` para `ficheiro.env`:

```powershell
Copy-Item ficheiro.env.example ficheiro.env
```

Edite o `ficheiro.env` com as suas credenciais locais:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=a_sua_senha_do_mysql
DB_NAME=study_group_matcher
SECRET_KEY=uma_chave_secreta_longa_e_aleatoria
```

---

## ▶️ Executar a Aplicação

```powershell
python app.py
```

Aceda no seu navegador a: [http://localhost:5000](http://localhost:5000)

