import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv('ficheiro.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_dev')

def get_db_connection():
    # Use environment variables with a fallback to local docker-compose defaults
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', 3306))
    user = os.getenv('DB_USER', 'devuser')
    password = os.getenv('DB_PASSWORD', 'devpassword')
    database = os.getenv('DB_NAME', 'study_group_matcher')
    
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, senha_hash FROM utilizadores WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['senha_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['nome']
            return redirect(url_for('perfil'))
        else:
            return render_template('index.html', erro="Email ou palavra-passe incorretos.")
            
    return render_template('index.html')

@app.route('/registo', methods=['GET', 'POST'])
def registo():
    cursos = [
        "Engenharia Informática", 
        "Gestão", 
        "Design", 
        "Medicina", 
        "Direito", 
        "Economia"
    ]
    estilos = [
        ('individual', 'Individual'), 
        ('em_grupo', 'Em Grupo'), 
        ('focado_discussao', 'Discussão e Debate'), 
        ('focado_exercicios', 'Exercícios Práticos')
    ]
    topicos = [
        "Matemática", "Programação", "História", 
        "Física", "Biologia", "Marketing"
    ]

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('pass')
        curso = request.form.get('curso')
        estilo = request.form.get('estilos') # radio button single value
        disponibilidade_json = request.form.get('disponibilidade', '[]')
        topicos_selecionados = request.form.getlist('topicos')
        
        senha_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Insert into utilizadores
            cursor.execute(
                "INSERT INTO utilizadores (nome, email, senha_hash, curso, estilo_estudo_pref) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, senha_hash, curso, estilo)
            )
            user_id = cursor.lastrowid
            
            # 2. Insert into disponibilidades
            disponibilidades = json.loads(disponibilidade_json)
            # The grid structure might be different, assuming list of objects or parsing logic is needed here
            # For this simple backend, we map the grid if we understand the format from frontend, or just store a simplified version
            # Let's assume the frontend sends array of {dia: "segunda", inicio: "09:00", fim: "10:00"}
            if disponibilidades and isinstance(disponibilidades, list):
                for block in disponibilidades:
                    # Depending on how the grid returns data
                    # Here we might need to adjust based on the actual JS in grelha.js
                    # For now, let's insert if it has dia_semana, hora_inicio, hora_fim
                    dia = block.get('dia_semana', 'segunda')
                    inicio = block.get('hora_inicio', '00:00:00')
                    fim = block.get('hora_fim', '00:00:00')
                    if dia and inicio and fim:
                        cursor.execute(
                            "INSERT INTO disponibilidades (utilizador_id, dia_semana, hora_inicio, hora_fim) VALUES (%s, %s, %s, %s)",
                            (user_id, dia, inicio, fim)
                        )
            
            # 3. Insert into topicos_interesse
            for topico in topicos_selecionados:
                cursor.execute(
                    "INSERT INTO topicos_interesse (utilizador_id, topico) VALUES (%s, %s)",
                    (user_id, topico)
                )
                
            conn.commit()
            
            # Auto-login after registration
            session['user_id'] = user_id
            session['user_name'] = nome
            return redirect(url_for('perfil'))
            
        except mysql.connector.IntegrityError:
            conn.rollback()
            return render_template('registo.html', cursos=cursos, estilos=estilos, topicos=topicos, erro="Esse email já está registado.")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('registo.html', cursos=cursos, estilos=estilos, topicos=topicos)

@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('perfil.html', nome=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
