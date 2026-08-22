# 🎨 Guia de Frontend e Design System

| Metadado | Informação |
| :--- | :--- |
| **Autor(a)** | Equipa de Desenvolvimento |
| **Data de Criação** | 2026-08-22 |
| **Última Atualização** | 2026-08-22 |
| **Versão** | 1.0.0 |
| **Módulo** | Frontend & UI/UX |

---

## 🎨 1. Paleta de Cores e Tokens CSS
O ficheiro `static/css/design-system.css` define as variáveis globais:

| Variável | Valor Padrão | Utilização |
| :--- | :--- | :--- |
| `--c-bg` | `#0f1013` | Fundo principal da aplicação. |
| `--c-surface` | `#16181d` | Fundo de cartões e blocos (`.card`). |
| `--c-gold` | `#d8a62b` | Cor de destaque primária e ações. |
| `--c-text-1` | `#f4f4f5` | Texto principal com alto contraste. |
| `--c-text-2` | `#a1a1aa` | Texto secundário e legendas. |
| `--c-line` | `#27272a` | Linhas divisórias e bordas subtis. |

---

## 📅 2. Componente de Grelha de Disponibilidade (`grelha.js`)
* **Estrutura:** Renderiza uma tabela interativa ou de leitura com $3$ linhas (Manhã, Tarde, Noite) e $7$ colunas (Segunda a Domingo).
* **Classes de Destaque:**
  * `.is-me`: Bloco selecionado pelo utilizador (Dourado translúcido).
  * `.is-them`: Bloco ocupado pelo grupo (Verde translúcido).
  * `.is-both`: Bloco em comum entre utilizador e grupo (Dourado vivo).

