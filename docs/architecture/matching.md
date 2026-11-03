# 🧩 Módulo F — Lógica de Matching

| Metadado | Informação |
| :--- | :--- |
| **Módulo** | F — Lógica de Matching (Pessoa 5) |
| **Ficheiros** | `matching.py`, `tests/test_matching.py` |
| **Rota** | `/sugestoes` (🔒) |

## Objetivo
Sugerir ao utilizador os grupos de estudo mais compatíveis, ordenados por uma pontuação de 0 a 100 %.

## Pontuação

| Critério | Peso | Como é calculado |
| :--- | :---: | :--- |
| Horário | 45 % | Média, sobre os blocos livres do utilizador, da fração de membros do grupo também livres nesse bloco. |
| Estilo de estudo | 25 % | 1 se o estilo do utilizador está entre os do grupo, 0 se não; 0,5 (neutro) se faltar informação. |
| Interesses | 20 % | Fração dos tópicos do utilizador presentes nos membros do grupo ou na disciplina do grupo. |
| Curso | 10 % | Proporção de membros do mesmo curso. |

## Regras
- Só aparecem grupos com **pelo menos 1 bloco horário em comum**.
- Grupos **cheios** (`max_membros`) e grupos onde o utilizador já é membro ou tem pedido pendente **não aparecem**.
- Desempate: mais horas em comum → grupo mais pequeno → nome.
- Os pesos estão no topo de `matching.py` (`PESO_*`) e podem ser ajustados.

## Estrutura do código
- **Funções puras** (`sobreposicao_horaria`, `pontuacao_*`, `avaliar_grupo`, `sugerir_grupos`): sem Flask nem BD; testáveis com mock data.
- **`carregar_candidatos(cursor, user_id)`**: lê tudo da BD com no máximo 6 queries, independentemente do número de grupos.
- **`app.py`**: a rota `/sugestoes` apenas liga as duas coisas e renderiza `sugestoes.html`.

## Nota sobre estilos
Os estilos do utilizador são guardados como chave (`focado_exercicios`) e os do grupo como rótulo (`Exercícios Práticos`). `matching.chave_estilo()` normaliza ambos antes de comparar.

## Testes
```bash
pip install pytest
python -m pytest tests -q
```
