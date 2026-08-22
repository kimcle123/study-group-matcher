# Study Group Matcher 🎓

Plataforma desenvolvida na comunidade **Build & Learn IT** para conectar estudantes universitários com base no curso, disponibilidade horária e estilo de estudo, facilitando a formação de grupos de estudo altamente compatíveis.

---

## 🚀 Funcionalidades Principais

* **Autenticação Segura:** Registo em 3 passos com seleção visual de horários e palavras-passe com hash seguro.
* **Matchmaking de Horários:** Algoritmo que calcula e destaca visualmente as horas em comum entre estudantes e grupos.
* **Gestão de Grupos de Estudo:** Criação de grupos com limites de membros, moderação de pedidos e papéis de administrador.
* **Chat Integrado:** Mensagens em tempo real dedicadas a cada grupo.
* **Design Moderno e Responsivo:** Tema escuro intuitivo com grelhas de disponibilidade semanais interativas.

---

## 📁 Estrutura do Projeto

* 📂 **`database/`**: Scripts de criação e evolução da base de dados MySQL.
* 📂 **`docs/`**: Documentação técnica completa, guias de setup e arquitetura.
* 📂 **`static/`**: Estilos CSS (Design System) e scripts JS (grelha semanal).
* 📂 **`templates/`**: Templates Jinja2 para a interface web.
* 📄 **`app.py`**: Servidor e rotas da aplicação Flask.
* 📄 **`ficheiro.env.example`**: Modelo de variáveis de ambiente.

---

## 📖 Documentação Detalhada

Toda a documentação técnica está centralizada na pasta [`docs/`](docs/README.md):
* [Modelo de Documentação (Template)](docs/template.md)
* [Guia de Instalação e Setup](docs/setup/installation-guide.md)
* [Arquitetura do Sistema](docs/architecture/system-overview.md)
* [Dicionário da Base de Dados](docs/database/data-dictionary.md)
* [Catálogo de Rotas e Endpoints](docs/api/routes.md)
* [Guia de Frontend e UI](docs/frontend/ui-guide.md)

---

## 🛠️ Como Iniciar Rapidamente

1. Crie e ative o seu ambiente virtual:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
3. Crie a base de dados MySQL:
   ```powershell
   & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database/schema.sql
   ```
4. Crie o ficheiro `ficheiro.env` com as suas credenciais a partir de `ficheiro.env.example`.
5. Execute a aplicação:
   ```powershell
   python app.py
   ```
