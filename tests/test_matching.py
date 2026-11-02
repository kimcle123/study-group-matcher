"""Testes do Módulo F (matching) com mock data - não precisam de MySQL."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matching  # noqa: E402


def matriz(*celulas):
    """Cria uma matriz 3x7 com 1 nas células (periodo, dia) indicadas."""
    m = [[0] * 7 for _ in range(3)]
    for p, d in celulas:
        m[p][d] = 1
    return m


def membro(celulas, curso="Engenharia Informática", topicos=()):
    return {"curso": curso, "topicos": list(topicos), "matriz": matriz(*celulas)}


def grupo(id, membros, estilos=(), disciplina="Programação I", max_membros=6, nome=None):
    return {"id": id, "nome": nome or f"G{id}", "disciplina": disciplina,
            "max_membros": max_membros, "estilos": list(estilos), "membros": membros}


UTILIZADOR = {
    "curso": "Engenharia Informática",
    "estilo": "focado_exercicios",
    "topicos": ["Programação", "Algoritmos"],
    "matriz": matriz((0, 0), (0, 2), (1, 4), (2, 1)),
}


# ---------- normalização ----------
def test_chave_estilo_aceita_chave_e_rotulo():
    assert matching.chave_estilo("focado_exercicios") == "focado_exercicios"
    assert matching.chave_estilo("Exercícios Práticos") == "focado_exercicios"
    assert matching.chave_estilo("  EM GRUPO ") == "em_grupo"
    assert matching.chave_estilo("") is None
    assert matching.chave_estilo(None) is None


def test_matriz_segura_entradas_invalidas():
    vazia = [[0] * 7 for _ in range(3)]
    assert matching.matriz_segura(None) == vazia
    assert matching.matriz_segura("lixo") == vazia
    assert matching.matriz_segura([[1, 1]]) == vazia
    assert matching.matriz_segura("[[1,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,1]]")[2][6] == 1


# ---------- horário ----------
def test_sobreposicao_horas_e_grelha():
    horas, grelha, cobertura = matching.sobreposicao_horaria(
        matriz((0, 0), (1, 1)), [matriz((0, 0), (2, 2))])
    assert horas == 2            # 1 bloco em comum x 2h
    assert grelha[0][0] == 3     # ambos
    assert grelha[1][1] == 1     # só o utilizador
    assert grelha[2][2] == 2     # só o grupo
    assert cobertura == 0.5      # cobre 1 de 2 blocos do utilizador


def test_cobertura_pondera_fracao_de_membros_livres():
    todos = matching.sobreposicao_horaria(
        matriz((0, 0)), [matriz((0, 0)), matriz((0, 0))])[2]
    metade = matching.sobreposicao_horaria(
        matriz((0, 0)), [matriz((0, 0)), matriz()])[2]
    assert todos == 1.0 and metade == 0.5


def test_utilizador_sem_horario_tem_cobertura_zero():
    assert matching.sobreposicao_horaria(matriz(), [matriz((0, 0))])[2] == 0.0


# ---------- estilo / interesses / curso ----------
def test_estilo_compara_chave_com_rotulo():
    assert matching.pontuacao_estilo("focado_exercicios", ["Exercícios Práticos"]) == 1.0
    assert matching.pontuacao_estilo("individual", ["Em Grupo"]) == 0.0
    assert matching.pontuacao_estilo("individual", []) == 0.5      # neutro
    assert matching.pontuacao_estilo(None, ["Em Grupo"]) == 0.5    # neutro


def test_interesses_usam_membros_e_disciplina():
    pont, comuns = matching.pontuacao_interesses(
        ["Programação", "Finanças"], {"Programação"}, "Microeconomia")
    assert pont == 1.0 and comuns == ["Finanças", "Programação"]
    assert matching.pontuacao_interesses([], {"X"}, "Cálculo I") == (0.5, [])


def test_curso_proporcao():
    assert matching.pontuacao_curso("Gestão", ["Gestão", "Direito"]) == 0.5
    assert matching.pontuacao_curso("Gestão", []) == 0.0


# ---------- avaliação e ranking ----------
def test_grupo_cheio_ou_vazio_nao_e_elegivel():
    cheio = grupo(1, [membro([(0, 0)]), membro([(0, 0)])], max_membros=2)
    assert matching.avaliar_grupo(UTILIZADOR, cheio) is None
    assert matching.avaliar_grupo(UTILIZADOR, grupo(2, [])) is None


def test_grupo_perfeito_pontua_100():
    g = grupo(1, [membro([(0, 0), (0, 2), (1, 4), (2, 1)],
                         topicos=["Programação", "Algoritmos"])],
              estilos=["Exercícios Práticos"])
    assert matching.avaliar_grupo(UTILIZADOR, g)["pontuacao"] == 100


def test_sem_horario_em_comum_e_excluido():
    g = grupo(1, [membro([(2, 6)])], estilos=["Exercícios Práticos"])
    assert matching.sugerir_grupos(UTILIZADOR, [g]) == []


def test_ranking_ordena_por_compatibilidade():
    melhor = grupo(1, [membro([(0, 0), (0, 2), (1, 4)], topicos=["Programação"])],
                   estilos=["Exercícios Práticos"])
    medio = grupo(2, [membro([(0, 0)], curso="Gestão")], estilos=["Em Grupo"])
    pior = grupo(3, [membro([(0, 0)], curso="Gestão")], estilos=["Individual"],
                 disciplina="Anatomia I")
    ids = [r["id"] for r in matching.sugerir_grupos(UTILIZADOR, [pior, medio, melhor])]
    assert ids == [1, 2, 3]


def test_desempate_por_horas_e_limite():
    a = grupo(1, [membro([(0, 0)])], nome="A")
    b = grupo(2, [membro([(0, 0), (0, 2)])], nome="B")
    u = {**UTILIZADOR, "estilo": None, "topicos": [], "matriz": matriz((0, 0), (0, 2))}
    resultado = matching.sugerir_grupos(u, [a, b], limite=1)
    assert len(resultado) == 1


def test_razoes_explicam_a_sugestao():
    g = grupo(1, [membro([(0, 0)], topicos=["Algoritmos"])], estilos=["Exercícios Práticos"])
    razoes = matching.avaliar_grupo(UTILIZADOR, g)["razoes"]
    assert "2h em comum" in razoes
    assert "Mesmo estilo de estudo" in razoes
    assert any(r.startswith("Interesses:") for r in razoes)
    assert "Colegas do teu curso" in razoes


# ---------- carregar_candidatos (cursor falso) ----------
class CursorFalso:
    """Devolve respostas pré-definidas pela ordem das queries."""
    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.atual = None
        self.queries = []

    def execute(self, sql, params=None):
        self.queries.append(sql)
        self.atual = self.respostas.pop(0)

    def fetchone(self):
        return self.atual

    def fetchall(self):
        return self.atual


def test_carregar_candidatos_monta_estrutura():
    cur = CursorFalso([
        {"curso": "Gestão", "estilo_estudo_pref": "em_grupo",
         "disponibilidade_matriz": "[[1,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]"},
        [{"topico": "Finanças"}],
        [{"id": 7, "nome": "G7", "disciplina": "Microeconomia", "max_membros": 6}],
        [{"grupo_id": 7, "estilo": "Em Grupo"}],
        [{"grupo_id": 7, "uid": 9, "curso": "Gestão",
          "disponibilidade_matriz": "[[1,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]"}],
        [{"utilizador_id": 9, "topico": "Finanças"}],
    ])
    utilizador, grupos = matching.carregar_candidatos(cur, 1)
    assert utilizador["topicos"] == ["Finanças"]
    assert grupos[0]["estilos"] == ["Em Grupo"]
    assert grupos[0]["membros"][0]["topicos"] == ["Finanças"]
    assert len(cur.queries) == 6
    assert matching.sugerir_grupos(utilizador, grupos)[0]["pontuacao"] == 100


def test_carregar_candidatos_utilizador_inexistente():
    assert matching.carregar_candidatos(CursorFalso([None]), 99) == (None, [])
