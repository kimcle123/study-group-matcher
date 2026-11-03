import os
import json
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

import matching

# Carregar configurações a partir do ficheiro .env
load_dotenv('ficheiro.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'chave_secreta_padrao_desenvolvimento_12345')

# ==========================================
# CONSTANTES E DADOS DE REFERÊNCIA
# ==========================================
CURSOS_DISPONIVEIS = [
    "Engenharia Informática",
    "Gestão",
    "Design",
    "Medicina",
    "Direito",
    "Economia",
    "Psicologia",
    "Engenharia Eletrotécnica"
]

ESTILOS_ESTUDO = [
    ('individual', 'Individual'),
    ('em_grupo', 'Em Grupo'),
    ('focado_discussao', 'Discussão e Debate'),
    ('focado_exercicios', 'Exercícios Práticos'),
    ('revisao_teorica', 'Revisão Teórica'),
    ('pomodoro', 'Técnica Pomodoro')
]

TOPICOS_INTERESSE = [
    "Matemática", "Programação", "História",
    "Física", "Biologia", "Marketing",
    "Algoritmos", "Bases de Dados", "Inteligência Artificial", "Finanças"
]

DISCIPLINAS_DISPONIVEIS = [
    "Programação I",
    "Álgebra Linear",
    "Cálculo I",
    "Bases de Dados",
    "Estruturas de Dados",
    "Microeconomia",
    "Contabilidade Geral",
    "Anatomia I",
    "Direito Constitucional",
    "Design de Interfaces"
]

# ==========================================
# FILTROS JINJA2 PERSONALIZADOS
# ==========================================
@app.template_filter('iniciais')
def iniciais_filter(nome):
    """
    Gera as iniciais de um nome para exibição no avatar.
    Exemplo: 'Miguel Silva' -> 'MS'
    """
    if not nome:
        return "?"
    partes = nome.strip().split()
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


# ==========================================
# GESTÃO DA BASE DE DADOS
# ==========================================
def get_db_connection():
    """
    Cria e devolve uma nova conexão com a base de dados MySQL.
    """
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'study_group_matcher')
    )


# ==========================================
# DECORADORES DE SEGURANÇA
# ==========================================
def login_obrigatorio(f):
    """
    Garante que a rota só pode ser acedida por utilizadores com sessão iniciada.
    """
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorada


# ==========================================
# FUNÇÕES AUXILIARES DE CÁLCULO E MATRIZ
# ==========================================
def obter_matriz_vazia():
    """Devolve uma grelha semanal 3x7 limpa com zeros."""
    return [[0 for _ in range(7)] for _ in range(3)]


def converter_matriz_segura(dados_json):
    """Garante que a matriz de disponibilidade está no formato 3x7 correto."""
    if not dados_json:
        return obter_matriz_vazia()
    try:
        if isinstance(dados_json, str):
            matriz = json.loads(dados_json)
        else:
            matriz = dados_json
            
        if isinstance(matriz, list) and len(matriz) == 3:
            return [[int(val) if val else 0 for val in linha] for linha in matriz]
    except Exception:
        pass
    return obter_matriz_vazia()


def calcular_horas_comuns(matriz_a, matriz_b):
    """
    Calcula as horas em comum entre duas matrizes e gera a grelha de sobreposição:
    0 = Ninguém
    1 = Utilizador (Tu)
    2 = Outro / Grupo
    3 = Ambos (Em comum)
    """
    horas = 0
    grelha_combinada = obter_matriz_vazia()
    
    for p in range(3):
        for d in range(7):
            val_a = matriz_a[p][d] if p < len(matriz_a) and d < len(matriz_a[p]) else 0
            val_b = matriz_b[p][d] if p < len(matriz_b) and d < len(matriz_b[p]) else 0
            
            if val_a and val_b:
                grelha_combinada[p][d] = 3
                horas += 2  # Cada bloco representa aprox. 2h de estudo
            elif val_a:
                grelha_combinada[p][d] = 1
            elif val_b:
                grelha_combinada[p][d] = 2
            else:
                grelha_combinada[p][d] = 0
                
    return horas, grelha_combinada


# ==========================================
# ROTAS DE AUTENTICAÇÃO E REGISTO
# ==========================================
@app.route('/', methods=['GET', 'POST'])
def index():
    """Página inicial e início de sessão (Login)."""
    if 'user_id' in session:
        return redirect(url_for('perfil'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('pass', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, senha_hash FROM utilizadores WHERE email = %s", (email,))
        utilizador = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if utilizador and check_password_hash(utilizador['senha_hash'], password):
            session['user_id'] = utilizador['id']
            session['user_name'] = utilizador['nome']
            return redirect(url_for('perfil'))
        else:
            return render_template('index.html', erro="Email ou palavra-passe incorretos.")
            
    return render_template('index.html')


@app.route('/registo', methods=['GET', 'POST'])
def registo():
    """Fluxo em 3 passos para criar uma nova conta de estudante."""
    if 'user_id' in session:
        return redirect(url_for('perfil'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('pass', '').strip()
        curso = request.form.get('curso', '').strip()
        ano = request.form.get('ano', '1.º').strip()
        estilo = request.form.get('estilos', 'em_grupo').strip()
        disponibilidade_raw = request.form.get('disponibilidade', '[]')
        topicos_selecionados = request.form.getlist('topicos')
        
        matriz_disponibilidade = converter_matriz_segura(disponibilidade_raw)
        senha_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Inserir dados principais do utilizador
            cursor.execute(
                """
                INSERT INTO utilizadores (nome, email, senha_hash, curso, ano, estilo_estudo_pref, disponibilidade_matriz)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (nome, email, senha_hash, curso, ano, estilo, json.dumps(matriz_disponibilidade))
            )
            user_id = cursor.lastrowid
            
            # 2. Inserir tópicos de interesse
            for topico in topicos_selecionados:
                cursor.execute(
                    "INSERT INTO topicos_interesse (utilizador_id, topico) VALUES (%s, %s)",
                    (user_id, topico)
                )
                
            conn.commit()
            
            # Iniciar sessão automaticamente após o registo
            session['user_id'] = user_id
            session['user_name'] = nome
            return redirect(url_for('perfil'))
            
        except mysql.connector.IntegrityError:
            conn.rollback()
            return render_template(
                'registo.html',
                cursos=CURSOS_DISPONIVEIS,
                estilos=ESTILOS_ESTUDO,
                topicos=TOPICOS_INTERESSE,
                erro="Esse email já se encontra registado."
            )
        finally:
            cursor.close()
            conn.close()
            
    return render_template(
        'registo.html',
        cursos=CURSOS_DISPONIVEIS,
        estilos=ESTILOS_ESTUDO,
        topicos=TOPICOS_INTERESSE
    )


@app.route('/logout')
def logout():
    """Terminar a sessão do utilizador."""
    session.clear()
    return redirect(url_for('index'))


# ==========================================
# ROTAS DO PERFIL
# ==========================================
@app.route('/perfil')
@login_obrigatorio
def perfil():
    """Exibe o perfil completo do utilizador com os seus horários e interesses."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obter dados do utilizador
    cursor.execute("SELECT id, nome, email, curso, ano, estilo_estudo_pref, disponibilidade_matriz FROM utilizadores WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        cursor.close()
        conn.close()
        session.clear()
        return redirect(url_for('index'))
        
    # Obter tópicos de interesse
    cursor.execute("SELECT topico FROM topicos_interesse WHERE utilizador_id = %s", (user_id,))
    topicos_rows = cursor.fetchall()
    topicos = [r['topico'] for r in topicos_rows]
    
    cursor.close()
    conn.close()
    
    # Formatar estilos para exibição
    estilos_labels = {k: v for k, v in ESTILOS_ESTUDO}
    estilo_formatado = [estilos_labels.get(user_data['estilo_estudo_pref'], user_data['estilo_estudo_pref'] or 'Em Grupo')]
    
    utilizador = {
        'id': user_data['id'],
        'nome': user_data['nome'],
        'email': user_data['email'],
        'curso': user_data['curso'],
        'ano': user_data['ano'] or '1.º',
        'disponibilidade': converter_matriz_segura(user_data['disponibilidade_matriz']),
        'estilos': estilo_formatado,
        'topicos': topicos if topicos else ["Geral"]
    }
    
    return render_template('perfil.html', utilizador=utilizador)


@app.route('/editar-perfil', methods=['GET', 'POST'])
@login_obrigatorio
def editar_perfil():
    """Permite alterar o curso, horários, estilo de estudo e tópicos."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        curso = request.form.get('curso', '').strip()
        disponibilidade_raw = request.form.get('disponibilidade', '[]')
        estilos_selecionados = request.form.getlist('estilos')
        topicos_selecionados = request.form.getlist('topicos')
        
        matriz_disponibilidade = converter_matriz_segura(disponibilidade_raw)
        estilo_principal = estilos_selecionados[0] if estilos_selecionados else 'em_grupo'
        
        # Atualizar tabela de utilizadores
        cursor.execute(
            """
            UPDATE utilizadores 
            SET curso = %s, estilo_estudo_pref = %s, disponibilidade_matriz = %s
            WHERE id = %s
            """,
            (curso, estilo_principal, json.dumps(matriz_disponibilidade), user_id)
        )
        
        # Atualizar tópicos de interesse
        cursor.execute("DELETE FROM topicos_interesse WHERE utilizador_id = %s", (user_id,))
        for topico in topicos_selecionados:
            cursor.execute("INSERT INTO topicos_interesse (utilizador_id, topico) VALUES (%s, %s)", (user_id, topico))
            
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('perfil'))
        
    # Carregar dados atuais para o formulário
    cursor.execute("SELECT curso, estilo_estudo_pref, disponibilidade_matriz FROM utilizadores WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    
    cursor.execute("SELECT topico FROM topicos_interesse WHERE utilizador_id = %s", (user_id,))
    topicos_rows = cursor.fetchall()
    topicos_atuais = [r['topico'] for r in topicos_rows]
    
    cursor.close()
    conn.close()
    
    estilos_apenas_nomes = [label for _, label in ESTILOS_ESTUDO]
    estilos_labels = {k: v for k, v in ESTILOS_ESTUDO}
    estilo_atual_label = estilos_labels.get(user_data['estilo_estudo_pref'], user_data['estilo_estudo_pref'])
    
    utilizador = {
        'curso': user_data['curso'],
        'disponibilidade': converter_matriz_segura(user_data['disponibilidade_matriz']),
        'estilos': [estilo_atual_label] if estilo_atual_label else [],
        'topicos': topicos_atuais
    }
    
    return render_template(
        'editar-perfil.html',
        utilizador=utilizador,
        cursos=CURSOS_DISPONIVEIS,
        estilos=estilos_apenas_nomes,
        topicos=TOPICOS_INTERESSE
    )


# ==========================================
# ROTAS DE SUGESTÕES DE GRUPOS (MATCHMAKING)
# ==========================================
@app.route('/sugestoes')
@login_obrigatorio
def sugestoes():
    """Sugere grupos ordenados por compatibilidade (horário, estilo, interesses e curso)."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        utilizador, grupos_candidatos = matching.carregar_candidatos(cursor, user_id)
    finally:
        cursor.close()
        conn.close()

    if utilizador is None:
        session.clear()
        return redirect(url_for('index'))

    lista_sugestoes = matching.sugerir_grupos(utilizador, grupos_candidatos)
    return render_template('sugestoes.html', sugestoes=lista_sugestoes)


# ==========================================
# ROTAS DE GESTÃO DE GRUPOS
# ==========================================
@app.route('/grupos')
@login_obrigatorio
def grupos():
    """Lista todos os grupos do utilizador e pedidos pendentes."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Obter grupos em que o utilizador participa
    cursor.execute(
        """
        SELECT g.id, g.nome, g.proximo_encontro, mg.is_admin,
               (SELECT COUNT(*) FROM membros_grupo WHERE grupo_id = g.id) as total_membros
        FROM grupos g
        JOIN membros_grupo mg ON g.id = mg.grupo_id
        WHERE mg.utilizador_id = %s
        ORDER BY g.criado_em DESC
        """,
        (user_id,)
    )
    meus_grupos_rows = cursor.fetchall()
    
    meus_grupos = []
    for g in meus_grupos_rows:
        meus_grupos.append({
            'id': g['id'],
            'nome': g['nome'],
            'membros': g['total_membros'],
            'proximo_encontro': g['proximo_encontro'],
            'admin': bool(g['is_admin'])
        })
        
    # 2. Obter pedidos de entrada pendentes para grupos que o utilizador administra
    cursor.execute(
        """
        SELECT pa.id, u.nome, g.nome as nome_grupo, u.disponibilidade_matriz, pa.grupo_id
        FROM pedidos_adesao pa
        JOIN utilizadores u ON pa.utilizador_id = u.id
        JOIN grupos g ON pa.grupo_id = g.id
        JOIN membros_grupo mg ON g.id = mg.grupo_id
        WHERE mg.utilizador_id = %s AND mg.is_admin = TRUE AND pa.status = 'pendente'
        """,
        (user_id,)
    )
    pedidos_rows = cursor.fetchall()
    
    # Obter matriz do admin para calcular horas em comum com o candidato
    cursor.execute("SELECT disponibilidade_matriz FROM utilizadores WHERE id = %s", (user_id,))
    admin_matriz = converter_matriz_segura(cursor.fetchone()['disponibilidade_matriz'])
    
    pedidos = []
    for p in pedidos_rows:
        candidato_matriz = converter_matriz_segura(p['disponibilidade_matriz'])
        horas_comuns, _ = calcular_horas_comuns(admin_matriz, candidato_matriz)
        pedidos.append({
            'id': p['id'],
            'nome': p['nome'],
            'grupo': p['nome_grupo'],
            'horas': horas_comuns
        })
        
    cursor.close()
    conn.close()
    
    return render_template('grupos.html', grupos=meus_grupos, pedidos=pedidos)


@app.route('/criar-grupo', methods=['GET', 'POST'])
@login_obrigatorio
def criar_grupo():
    """Formulário para criar um novo grupo de estudo."""
    user_id = session['user_id']
    estilos_nomes = [label for _, label in ESTILOS_ESTUDO]
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        objetivo = request.form.get('objetivo', '').strip()
        disciplina = request.form.get('disciplina', '').strip()
        max_membros = int(request.form.get('max', 6))
        aberto = bool(request.form.get('aberto'))
        aprovar = bool(request.form.get('aprovar', True))
        estilos_selecionados = request.form.getlist('estilos')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Inserir grupo
        cursor.execute(
            """
            INSERT INTO grupos (nome, objetivo, disciplina, criador_id, max_membros, aberto, aprovar_pedidos)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nome, objetivo, disciplina, user_id, max_membros, aberto, aprovar)
        )
        grupo_id = cursor.lastrowid
        
        # 2. Inserir criador como Administrador
        cursor.execute(
            "INSERT INTO membros_grupo (grupo_id, utilizador_id, is_admin) VALUES (%s, %s, TRUE)",
            (grupo_id, user_id)
        )
        
        # 3. Inserir etiquetas de estilo do grupo
        for est in estilos_selecionados:
            cursor.execute(
                "INSERT INTO grupo_estilos (grupo_id, estilo) VALUES (%s, %s)",
                (grupo_id, est)
            )
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('grupo', grupo_id=grupo_id))
        
    return render_template(
        'criar-grupo.html',
        disciplinas=DISCIPLINAS_DISPONIVEIS,
        estilos=estilos_nomes
    )


@app.route('/grupo/<int:grupo_id>')
@login_obrigatorio
def grupo(grupo_id):
    """Página de detalhes, membros e horários de um grupo."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Obter informações do grupo
    cursor.execute("SELECT * FROM grupos WHERE id = %s", (grupo_id,))
    grupo_data = cursor.fetchone()
    
    if not grupo_data:
        cursor.close()
        conn.close()
        return redirect(url_for('grupos'))
        
    # 2. Obter etiquetas / estilos
    cursor.execute("SELECT estilo FROM grupo_estilos WHERE grupo_id = %s", (grupo_id,))
    etiquetas = [r['estilo'] for r in cursor.fetchall()]
    if not etiquetas:
        etiquetas = [grupo_data['disciplina']]
        
    # 3. Obter membros
    cursor.execute(
        """
        SELECT u.id, u.nome, u.disponibilidade_matriz, mg.is_admin
        FROM membros_grupo mg
        JOIN utilizadores u ON mg.utilizador_id = u.id
        WHERE mg.grupo_id = %s
        ORDER BY mg.is_admin DESC, u.nome ASC
        """,
        (grupo_id,)
    )
    membros_rows = cursor.fetchall()
    
    membros = []
    sou_membro = False
    matriz_grupo = obter_matriz_vazia()
    total_membros = len(membros_rows)
    
    for m in membros_rows:
        if m['id'] == user_id:
            sou_membro = True
        membros.append({
            'nome': m['nome'],
            'admin': bool(m['is_admin'])
        })
        
        m_matriz = converter_matriz_segura(m['disponibilidade_matriz'])
        for p in range(3):
            for d in range(7):
                if m_matriz[p][d]:
                    matriz_grupo[p][d] += 1
                    
    # Calcular grelha de calor do grupo (0: Ninguém, 1: Alguns, 2: Todos)
    grelha_final = obter_matriz_vazia()
    for p in range(3):
        for d in range(7):
            contagem = matriz_grupo[p][d]
            if contagem == 0:
                grelha_final[p][d] = 0
            elif total_membros > 1 and contagem >= total_membros:
                grelha_final[p][d] = 2  # Todos
            else:
                grelha_final[p][d] = 1  # Alguns
                
    cursor.close()
    conn.close()
    
    grupo_obj = {
        'id': grupo_data['id'],
        'nome': grupo_data['nome'],
        'objetivo': grupo_data['objetivo'],
        'etiquetas': etiquetas,
        'proximo_encontro': grupo_data['proximo_encontro'],
        'faltam': "Em breve" if grupo_data['proximo_encontro'] else None,
        'grelha': grelha_final,
        'membros': membros,
        'sou_membro': sou_membro
    }
    
    return render_template('grupo.html', grupo=grupo_obj)


@app.route('/grupo/<int:grupo_id>/pedir', methods=['POST'])
@login_obrigatorio
def pedir_entrada(grupo_id):
    """Solicitar entrada num grupo de estudo."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT aberto, aprovar_pedidos FROM grupos WHERE id = %s", (grupo_id,))
    grupo_info = cursor.fetchone()
    
    if grupo_info:
        if grupo_info['aberto'] and not grupo_info['aprovar_pedidos']:
            # Entrada direta
            cursor.execute(
                "INSERT IGNORE INTO membros_grupo (grupo_id, utilizador_id, is_admin) VALUES (%s, %s, FALSE)",
                (grupo_id, user_id)
            )
        else:
            # Pedido pendente de aprovação
            cursor.execute(
                "INSERT INTO pedidos_adesao (grupo_id, utilizador_id, status) VALUES (%s, %s, 'pendente')",
                (grupo_id, user_id)
            )
        conn.commit()
        
    cursor.close()
    conn.close()
    return redirect(url_for('grupo', grupo_id=grupo_id))


@app.route('/grupo/<int:grupo_id>/sair', methods=['POST'])
@login_obrigatorio
def sair_grupo(grupo_id):
    """Permite ao utilizador sair de um grupo."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM membros_grupo WHERE grupo_id = %s AND utilizador_id = %s", (grupo_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('grupos'))


@app.route('/pedidos/<int:pedido_id>', methods=['POST'])
@login_obrigatorio
def responder_pedido(pedido_id):
    """Aprovar ou rejeitar um pedido de adesão por parte do Administrador."""
    user_id = session['user_id']
    decisao = request.form.get('decisao', 'recusar')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar se o utilizador autenticado é admin do grupo em causa
    cursor.execute(
        """
        SELECT pa.id, pa.grupo_id, pa.utilizador_id 
        FROM pedidos_adesao pa
        JOIN membros_grupo mg ON pa.grupo_id = mg.grupo_id
        WHERE pa.id = %s AND mg.utilizador_id = %s AND mg.is_admin = TRUE
        """,
        (pedido_id, user_id)
    )
    pedido = cursor.fetchone()
    
    if pedido:
        if decisao == 'aceitar':
            cursor.execute(
                "INSERT IGNORE INTO membros_grupo (grupo_id, utilizador_id, is_admin) VALUES (%s, %s, FALSE)",
                (pedido['grupo_id'], pedido['utilizador_id'])
            )
            cursor.execute("UPDATE pedidos_adesao SET status = 'aceite' WHERE id = %s", (pedido_id,))
        else:
            cursor.execute("UPDATE pedidos_adesao SET status = 'recusado' WHERE id = %s", (pedido_id,))
            
        conn.commit()
        
    cursor.close()
    conn.close()
    return redirect(url_for('grupos'))


# ==========================================
# ROTAS DO CHAT E MENSAGENS
# ==========================================
@app.route('/chat')
@app.route('/chat/<int:grupo_id>')
@login_obrigatorio
def chat(grupo_id=None):
    """Visualização da caixa de mensagens do grupo."""
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Se não foi fornecido grupo_id, abrir o primeiro grupo do utilizador
    if not grupo_id:
        cursor.execute(
            "SELECT grupo_id FROM membros_grupo WHERE utilizador_id = %s ORDER BY data_adesao ASC LIMIT 1",
            (user_id,)
        )
        primeiro_grupo = cursor.fetchone()
        if primeiro_grupo:
            cursor.close()
            conn.close()
            return redirect(url_for('chat', grupo_id=primeiro_grupo['grupo_id']))
        else:
            cursor.close()
            conn.close()
            return render_template('chat.html', conversa=None, mensagens=[])
            
    # Obter detalhes da conversa do grupo
    cursor.execute(
        """
        SELECT g.id, g.nome, 
               (SELECT COUNT(*) FROM membros_grupo WHERE grupo_id = g.id) as total_membros,
               (SELECT COUNT(*) FROM membros_grupo WHERE grupo_id = g.id AND utilizador_id = %s) as sou_membro
        FROM grupos g
        WHERE g.id = %s
        """,
        (user_id, grupo_id)
    )
    grupo_info = cursor.fetchone()
    
    if not grupo_info or not grupo_info['sou_membro']:
        cursor.close()
        conn.close()
        return redirect(url_for('grupos'))
        
    # Carregar mensagens trocadas
    cursor.execute(
        """
        SELECT m.id, m.texto, m.enviada_em, m.utilizador_id, u.nome as autor_nome
        FROM mensagens m
        JOIN utilizadores u ON m.utilizador_id = u.id
        WHERE m.grupo_id = %s
        ORDER BY m.enviada_em ASC
        """,
        (grupo_id,)
    )
    mensagens_rows = cursor.fetchall()
    
    mensagens = []
    for m in mensagens_rows:
        hora_formatada = m['enviada_em'].strftime('%H:%M') if isinstance(m['enviada_em'], datetime) else str(m['enviada_em'])[11:16]
        mensagens.append({
            'minha': m['utilizador_id'] == user_id,
            'autor': m['autor_nome'],
            'texto': m['texto'],
            'hora': hora_formatada
        })
        
    conversa = {
        'id': grupo_info['id'],
        'grupo': grupo_info['nome'],
        'membros': grupo_info['total_membros']
    }
    
    cursor.close()
    conn.close()
    return render_template('chat.html', conversa=conversa, mensagens=mensagens)


@app.route('/chat/<int:grupo_id>/mensagem', methods=['POST'])
@login_obrigatorio
def enviar_mensagem(grupo_id):
    """Envia uma nova mensagem no chat do grupo."""
    user_id = session['user_id']
    texto = request.form.get('texto', '').strip()
    
    if texto:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se o utilizador pertence ao grupo
        cursor.execute(
            "SELECT 1 FROM membros_grupo WHERE grupo_id = %s AND utilizador_id = %s",
            (grupo_id, user_id)
        )
        if cursor.fetchone():
            cursor.execute(
                "INSERT INTO mensagens (grupo_id, utilizador_id, texto) VALUES (%s, %s, %s)",
                (grupo_id, user_id, texto)
            )
            conn.commit()
            
        cursor.close()
        conn.close()
        
    return redirect(url_for('chat', grupo_id=grupo_id))


# ==========================================
# INICIALIZAÇÃO DO SERVIDOR
# ==========================================
if __name__ == '__main__':
    # Executar a aplicação em modo debug e acessível localmente
    app.run(debug=True, host='0.0.0.0', port=5000)
