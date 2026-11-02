# 🌐 Catálogo de Rotas e Endpoints (Flask)

| Metadado | Informação |
| :--- | :--- |
| **Autor(a)** | Equipa de Desenvolvimento |
| **Data de Criação** | 2026-08-22 |
| **Última Atualização** | 2026-08-22 |
| **Versão** | 1.0.0 |
| **Módulo** | API & Rotas do Backend |

---

## 🔒 Regras de Autenticação
As rotas assinaladas com 🔒 requerem sessão ativa (`@login_obrigatorio`). Caso o utilizador não esteja autenticado, é redirecionado para `/`.

---

## 📑 Lista de Rotas

| Rota | Métodos | Auth | Descrição |
| :--- | :--- | :---: | :--- |
| `/` | `GET`, `POST` | 🔓 | Página inicial e login. |
| `/registo` | `GET`, `POST` | 🔓 | Formulário de registo de estudante em 3 passos. |
| `/logout` | `GET` | 🔒 | Termina a sessão e limpa os cookies. |
| `/perfil` | `GET` | 🔒 | Visualização do perfil e matriz de disponibilidade. |
| `/editar-perfil` | `GET`, `POST` | 🔒 | Alteração de curso, disponibilidade, tópicos e estilos. |
| `/sugestoes` | `GET` | 🔒 | Grupos recomendados por compatibilidade (horário, estilo, interesses, curso). Ver [matching](../architecture/matching.md). |
| `/grupos` | `GET` | 🔒 | Lista de grupos do utilizador e pedidos pendentes. |
| `/criar-grupo` | `GET`, `POST` | 🔒 | Criação de um novo grupo de estudo. |
| `/grupo/<int:grupo_id>` | `GET` | 🔒 | Detalhes do grupo, mapa de calor e membros. |
| `/grupo/<int:grupo_id>/pedir` | `POST` | 🔒 | Envia pedido de adesão para entrar num grupo. |
| `/grupo/<int:grupo_id>/sair` | `POST` | 🔒 | Sai do grupo em que é membro. |
| `/pedidos/<int:pedido_id>` | `POST` | 🔒 | Aceita (`decisao=aceitar`) ou rejeita (`recusar`) um pedido. |
| `/chat` | `GET` | 🔒 | Abre a conversa do primeiro grupo do utilizador. |
| `/chat/<int:grupo_id>` | `GET` | 🔒 | Abre o chat de um grupo específico. |
| `/chat/<int:grupo_id>/mensagem` | `POST` | 🔒 | Envia uma nova mensagem no chat do grupo. |

