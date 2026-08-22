# 📚 Documentação do Projeto · Study Group Matcher

| Metadado | Informação |
| :--- | :--- |
| **Projeto** | Study Group Matcher |
| **Comunidade** | Build & Learn IT |
| **Última Atualização** | 2026-08-22 |
| **Versão Global** | 1.0.0 |

Bem-vindo ao centro de documentação do **Study Group Matcher**. Toda a informação do sistema está organizada modularmente nas seguintes subpastas:

---

## 📁 Índice da Documentação

1. **[Modelo de Documentação (Template)](template.md)**  
   * Padrão oficial com cabeçalho de data, autor e versões para novos documentos.

2. **[Guia de Instalação e Configuração (Setup)](setup/installation-guide.md)**  
   * Passo a passo para configurar o ambiente Python, MySQL, variáveis de ambiente e execução local.

3. **[Arquitetura do Sistema](architecture/system-overview.md)**  
   * Visão geral da arquitetura, fluxo de dados, estrutura de pastas e algoritmo de compatibilidade.

4. **[Base de Dados e Esquema Relacional](database/data-dictionary.md)**  
   * Dicionário de dados completo, tabelas, chaves primárias/estrangeiras e regras de integridade.

5. **[Rotas e Endpoints (API/Backend)](api/routes.md)**  
   * Catálogo detalhado de todas as rotas Flask, métodos HTTP, parâmetros e controlo de acesso.

6. **[Frontend e Design System](frontend/ui-guide.md)**  
   * Guia visual, tokens de design (cores, tipografia, espaçamentos) e lógica da grelha de disponibilidade ($3 \times 7$).

---

## 📂 Estrutura de Diretórios do Projeto

```text
study-group-matcher/
├── .gitignore               # Regras de exclusão do Git
├── README.md                # Apresentação do repositório
├── requirements.txt         # Dependências Python
├── ficheiro.env.example     # Modelo de variáveis de ambiente
├── app.py                   # Servidor Flask e rotas do backend
├── schema.sql               # Script SQL de criação da base de dados
├── database/                # Scripts e migrações da base de dados
│   └── schema.sql
├── docs/                    # Documentação centralizada
│   ├── template.md
│   ├── README.md
│   ├── setup/
│   ├── architecture/
│   ├── database/
│   ├── api/
│   └── frontend/
├── static/                  # Recursos estáticos
│   ├── css/
│   │   └── design-system.css
│   └── js/
│       └── grelha.js
└── templates/               # Páginas HTML (Jinja2)
    ├── base.html
    ├── _nav.html
    ├── index.html
    ├── registo.html
    ├── perfil.html
    ├── editar-perfil.html
    ├── grupos.html
    ├── criar-grupo.html
    ├── grupo.html
    ├── sugestoes.html
    └── chat.html
```

