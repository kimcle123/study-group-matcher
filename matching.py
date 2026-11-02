"""
Módulo F - Lógica de Matching.

Calcula a compatibilidade entre um utilizador e os grupos de estudo existentes
e devolve sugestões ordenadas da mais para a menos compatível.

O núcleo (funções puras) não depende de Flask nem da base de dados, o que
permite testá-lo com mock data (ver tests/test_matching.py). A função
`carregar_candidatos` é a única que fala com a base de dados.

Pontuação final (0-100):
    Horário    45 %  - cobertura da disponibilidade do utilizador pelos membros do grupo
    Estilo     25 %  - estilo de estudo do utilizador vs. estilos do grupo
    Interesses 20 %  - tópicos do utilizador vs. tópicos dos membros e da disciplina
    Curso      10 %  - proporção de membros do mesmo curso
"""

import json

# ==========================================
# CONFIGURAÇÃO
# ==========================================
PESO_HORARIO = 45
PESO_ESTILO = 25
PESO_INTERESSES = 20
PESO_CURSO = 10

PERIODOS = 3
DIAS = 7
HORAS_POR_BLOCO = 2  # Cada bloco da grelha representa ~2h (igual a app.calcular_horas_comuns)

# Os estilos do utilizador são guardados como chave ('focado_exercicios') e os do
# grupo como rótulo ('Exercícios Práticos'). Este mapa permite compará-los.
ESTILOS_ROTULOS = {
    'individual': 'Individual',
    'em_grupo': 'Em Grupo',
    'focado_discussao': 'Discussão e Debate',
    'focado_exercicios': 'Exercícios Práticos',
    'revisao_teorica': 'Revisão Teórica',
    'pomodoro': 'Técnica Pomodoro',
}

# Relação entre disciplinas e tópicos de interesse (usada para dar pontos de
# interesse quando o grupo ainda tem poucos membros com tópicos preenchidos).
DISCIPLINA_TOPICOS = {
    'Programação I': {'Programação', 'Algoritmos'},
    'Álgebra Linear': {'Matemática'},
    'Cálculo I': {'Matemática'},
    'Bases de Dados': {'Bases de Dados', 'Programação'},
    'Estruturas de Dados': {'Algoritmos', 'Programação'},
    'Microeconomia': {'Finanças'},
    'Contabilidade Geral': {'Finanças'},
    'Anatomia I': {'Biologia'},
    'Direito Constitucional': {'História'},
    'Design de Interfaces': {'Marketing'},
}


# ==========================================
# NORMALIZAÇÃO
# ==========================================
def _normalizar_texto(valor):
    return (valor or '').strip().lower()


def chave_estilo(valor):
    """
    Converte um estilo (chave ou rótulo) para a chave canónica.
    'Exercícios Práticos' -> 'focado_exercicios'; 'focado_exercicios' -> 'focado_exercicios'.
    Devolve None se o valor for vazio.
    """
    texto = _normalizar_texto(valor)
    if not texto:
        return None
    if texto in ESTILOS_ROTULOS:
        return texto
    for chave, rotulo in ESTILOS_ROTULOS.items():
        if texto == rotulo.lower():
            return chave
    return texto


def matriz_segura(dados):
    """Garante uma matriz 3x7 de inteiros (0/1), aceitando JSON em texto ou lista."""
    vazia = [[0] * DIAS for _ in range(PERIODOS)]
    if not dados:
        return vazia
    try:
        matriz = json.loads(dados) if isinstance(dados, str) else dados
        if not isinstance(matriz, list) or len(matriz) != PERIODOS:
            return vazia
        resultado = []
        for linha in matriz:
            linha = list(linha)[:DIAS]
            linha += [0] * (DIAS - len(linha))
            resultado.append([1 if v else 0 for v in linha])
        return resultado
    except (ValueError, TypeError):
        return vazia


def _total_blocos(matriz):
    return sum(sum(linha) for linha in matriz)


# ==========================================
# COMPONENTES DA PONTUAÇÃO (cada um devolve 0.0 - 1.0)
# ==========================================
def sobreposicao_horaria(matriz_utilizador, matrizes_membros):
    """
    Compara o utilizador com os membros do grupo.

    Devolve (horas_comuns, grelha, cobertura):
      - horas_comuns: horas em que o utilizador e pelo menos um membro estão livres
      - grelha: 0 ninguém | 1 só tu | 2 só o grupo | 3 ambos (formato da UI)
      - cobertura: 0.0-1.0, média ponderada da fração de membros livres em cada
        bloco do utilizador (um bloco em que todos os membros estão livres vale
        mais do que um em que só um está).
    """
    n_membros = len(matrizes_membros)
    grelha = [[0] * DIAS for _ in range(PERIODOS)]
    blocos_comuns = 0
    soma_fracoes = 0.0

    for p in range(PERIODOS):
        for d in range(DIAS):
            meu = matriz_utilizador[p][d]
            livres = sum(m[p][d] for m in matrizes_membros)
            grupo = livres > 0
            if meu and grupo:
                grelha[p][d] = 3
                blocos_comuns += 1
                soma_fracoes += livres / n_membros
            elif meu:
                grelha[p][d] = 1
            elif grupo:
                grelha[p][d] = 2

    blocos_utilizador = _total_blocos(matriz_utilizador)
    cobertura = soma_fracoes / blocos_utilizador if blocos_utilizador else 0.0
    return blocos_comuns * HORAS_POR_BLOCO, grelha, cobertura


def pontuacao_estilo(estilo_utilizador, estilos_grupo):
    """
    1.0 se o estilo do utilizador está entre os do grupo; 0.0 se não está.
    Sem informação de um dos lados devolve 0.5 (neutro, não penaliza).
    """
    estilo = chave_estilo(estilo_utilizador)
    estilos = {chave_estilo(e) for e in estilos_grupo} - {None}
    if not estilo or not estilos:
        return 0.5
    return 1.0 if estilo in estilos else 0.0


def pontuacao_interesses(topicos_utilizador, topicos_membros, disciplina):
    """
    Fração dos tópicos do utilizador cobertos pelos tópicos dos membros do grupo
    ou pela disciplina do grupo. Sem tópicos no utilizador devolve 0.5 (neutro).
    Devolve também os tópicos em comum (para explicar a sugestão).
    """
    meus = {t for t in topicos_utilizador if t}
    if not meus:
        return 0.5, []
    do_grupo = set(topicos_membros) | DISCIPLINA_TOPICOS.get(disciplina, set())
    comuns = sorted(meus & do_grupo)
    return len(comuns) / len(meus), comuns


def pontuacao_curso(curso_utilizador, cursos_membros):
    """Proporção de membros que estudam o mesmo curso que o utilizador."""
    if not cursos_membros:
        return 0.0
    curso = _normalizar_texto(curso_utilizador)
    iguais = sum(1 for c in cursos_membros if _normalizar_texto(c) == curso)
    return iguais / len(cursos_membros)


# ==========================================
# MATCHING UTILIZADOR <-> GRUPO
# ==========================================
def avaliar_grupo(utilizador, grupo):
    """
    Calcula a compatibilidade de um utilizador com um grupo.

    utilizador: {'curso', 'estilo', 'topicos': [...], 'matriz': 3x7}
    grupo: {'id', 'nome', 'disciplina', 'max_membros', 'estilos': [...],
            'membros': [{'curso', 'topicos': [...], 'matriz': 3x7}, ...]}

    Devolve None se o grupo não for elegível (cheio ou sem membros).
    """
    membros = grupo.get('membros', [])
    if not membros:
        return None
    max_membros = grupo.get('max_membros')
    if max_membros and len(membros) >= max_membros:
        return None

    matriz_u = matriz_segura(utilizador.get('matriz'))
    matrizes = [matriz_segura(m.get('matriz')) for m in membros]

    horas, grelha, cobertura = sobreposicao_horaria(matriz_u, matrizes)
    estilo = pontuacao_estilo(utilizador.get('estilo'), grupo.get('estilos', []))
    topicos_membros = {t for m in membros for t in m.get('topicos', [])}
    interesses, topicos_comuns = pontuacao_interesses(
        utilizador.get('topicos', []), topicos_membros, grupo.get('disciplina'))
    curso = pontuacao_curso(utilizador.get('curso'), [m.get('curso') for m in membros])

    pontuacao = (
        cobertura * PESO_HORARIO
        + estilo * PESO_ESTILO
        + interesses * PESO_INTERESSES
        + curso * PESO_CURSO
    )

    razoes = []
    if horas:
        razoes.append(f"{horas}h em comum")
    if estilo == 1.0:
        razoes.append("Mesmo estilo de estudo")
    if topicos_comuns:
        razoes.append("Interesses: " + ", ".join(topicos_comuns))
    if curso > 0:
        razoes.append("Colegas do teu curso")

    return {
        'id': grupo['id'],
        'nome': grupo['nome'],
        'disciplina': grupo['disciplina'],
        'membros': len(membros),
        'max_membros': max_membros,
        'horas': horas,
        'grelha': grelha,
        'etiquetas': grupo.get('estilos') or [grupo['disciplina']],
        'pontuacao': round(pontuacao),
        'razoes': razoes,
    }


def sugerir_grupos(utilizador, grupos, minimo_blocos=1, limite=None):
    """
    Devolve os grupos compatíveis, do mais para o menos compatível.

    Só entram grupos com pelo menos `minimo_blocos` blocos horários em comum
    (sem horário em comum o grupo não é viável). Em caso de empate na
    pontuação, ganha o grupo com mais horas em comum e depois o mais pequeno.
    """
    resultados = []
    for grupo in grupos:
        r = avaliar_grupo(utilizador, grupo)
        if r is None or r['horas'] < minimo_blocos * HORAS_POR_BLOCO:
            continue
        resultados.append(r)

    resultados.sort(key=lambda r: (-r['pontuacao'], -r['horas'], r['membros'], r['nome']))
    return resultados[:limite] if limite else resultados


# ==========================================
# ACESSO À BASE DE DADOS
# ==========================================
def carregar_candidatos(cursor, user_id):
    """
    Lê da base de dados o utilizador e os grupos onde ainda pode entrar
    (exclui grupos onde já é membro e com pedido pendente).
    `cursor` deve ser um cursor com dictionary=True. Usa no máximo 6 queries no total,
    independentemente do número de grupos.
    Devolve (utilizador, grupos) no formato esperado por `sugerir_grupos`.
    """
    cursor.execute(
        "SELECT curso, estilo_estudo_pref, disponibilidade_matriz FROM utilizadores WHERE id = %s",
        (user_id,))
    u = cursor.fetchone()
    if not u:
        return None, []

    cursor.execute("SELECT topico FROM topicos_interesse WHERE utilizador_id = %s", (user_id,))
    utilizador = {
        'curso': u['curso'],
        'estilo': u['estilo_estudo_pref'],
        'matriz': u['disponibilidade_matriz'],
        'topicos': [r['topico'] for r in cursor.fetchall()],
    }

    cursor.execute(
        """
        SELECT id, nome, disciplina, max_membros FROM grupos
        WHERE id NOT IN (SELECT grupo_id FROM membros_grupo WHERE utilizador_id = %s)
          AND id NOT IN (SELECT grupo_id FROM pedidos_adesao
                         WHERE utilizador_id = %s AND status = 'pendente')
        """,
        (user_id, user_id))
    grupos = {
        g['id']: {**g, 'estilos': [], 'membros': []} for g in cursor.fetchall()
    }
    if not grupos:
        return utilizador, []

    ids = list(grupos)
    marcadores = ", ".join(["%s"] * len(ids))

    cursor.execute(
        f"SELECT grupo_id, estilo FROM grupo_estilos WHERE grupo_id IN ({marcadores})", ids)
    for r in cursor.fetchall():
        grupos[r['grupo_id']]['estilos'].append(r['estilo'])

    cursor.execute(
        f"""
        SELECT mg.grupo_id, u.id AS uid, u.curso, u.disponibilidade_matriz
        FROM membros_grupo mg JOIN utilizadores u ON u.id = mg.utilizador_id
        WHERE mg.grupo_id IN ({marcadores})
        """, ids)
    membros_por_uid = {}
    for r in cursor.fetchall():
        membro = {'curso': r['curso'], 'matriz': r['disponibilidade_matriz'], 'topicos': []}
        grupos[r['grupo_id']]['membros'].append(membro)
        membros_por_uid.setdefault(r['uid'], []).append(membro)

    if membros_por_uid:
        uids = list(membros_por_uid)
        marc_u = ", ".join(["%s"] * len(uids))
        cursor.execute(
            f"SELECT utilizador_id, topico FROM topicos_interesse WHERE utilizador_id IN ({marc_u})",
            uids)
        for r in cursor.fetchall():
            for membro in membros_por_uid[r['utilizador_id']]:
                membro['topicos'].append(r['topico'])

    return utilizador, list(grupos.values())
