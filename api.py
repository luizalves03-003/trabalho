from flask import Flask, jsonify, request, render_template, url_for, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
DATABASE = 'biblioteca.db'
app.secret_key = 'chave_secreta'
bcrypt = Bcrypt(app)


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS livros(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                genero TEXT NOT NULL,
                ano INTEGER NOT NULL
            )

        '''),
        conn.execute('''
            CREATE TABLE IF NOT EXISTS usuarios(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                perfil TEXT NOT NULL DEFAULT 'usuario'
            )
            
        ''')
        conn.execute('''
                CREATE TABLE IF NOT EXISTS emprestimos(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     usuario_id INTEGER NOT NULL,
                     livro_id INTEGER NOT NULL,
                     data_emprestimo TEXT,
                     devolver INTEGER DEFAULT 0,
                     
                     FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                     FOREIGN KEY(livro_id) REFERENCES livros(id)
        )

        ''')

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]

        if total_usuarios == 0:
            senha_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
            cursor.execute(
                "INSERT INTO usuarios (nome, senha, perfil) VALUES (?, ?, ?)",
                ('admin', senha_hash, 'admin')
            )
            conn.commit()

            print("Usuário administrador criado com sucesso!")
            print("Nome de usuário: admin")
            print("Senha: admin")

        print("\n ---- BIBLIOTECA ABERTA ---- ")

# ---função de página inicial---


@app.route('/', methods=['GET'])
def pagina_inicial():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        livros = cursor.execute("SELECT * FROM  livros").fetchall()

        resultado = [dict(row) for row in livros]
        return render_template('index.html', resultados=resultado)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---função de buscar livro por gênero---


@app.route('/livros/busca', methods=['GET'])
def busca_livros():

    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    ano = request.args.get('ano')
    nome = request.args.get('nome')
    genero = request.args.get('genero')



    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        busca = request.args.get('busca')
        if busca.isdigit():
            cursor.execute("SELECT * FROM livros WHERE nome = ? OR genero LIKE ? OR ano = ?", f"%{busca}%", f"%{busca}%", (int(busca)))
        else:
            cursor.execute("SELECT * FROM livros WHERE genero LIKE ? OR nome LIKE ?", (f"%{busca}%", f"%{busca}%"))
        
        livros = cursor.fetchall()
        resultado = [dict(row) for row in livros]
        return render_template('index.html', resultados=resultado)


# ---função de adicionar livro---
@app.route('/livros/add', methods=['POST'])
def adicionar_livro():

    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if not administrador():
        return "Acesso negado. Apenas administradores podem adicionar livros.", 403

    nome = request.form.get('nome')
    genero = request.form.get('genero')
    try:
        ano = int(request.form.get('ano'))
    except (ValueError, TypeError):
        return jsonify({'erro': 'Erro: O ano deve ser um número válido'}), 404

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if not nome or not genero:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        cursor.execute(
            "INSERT INTO livros (nome, genero, ano) VALUES (?,?,?)",
            (nome, genero, ano)
        )
        conn.commit()
    return redirect(url_for('pagina_inicial'))

# ---função de página de adicionar livro---


@app.route('/livros/add', methods=['GET'])
def pagina_adicionar():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        livros = cursor.execute("SELECT * FROM livros").fetchall()

        resultado = [dict(row) for row in livros]
        return render_template('adicionar.html', resultados=resultado)


# ---função de atualizar livro---
@app.route('/livros/atualizar/<int:id>', methods=['POST'])
def atualizar_livros(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if not administrador():
        return "Acesso negado. Apenas administradores podem atualizar livros.", 403

    nome = request.form.get('nome')
    genero = request.form.get('genero')
    try:
        ano = int(request.form.get('ano'))
    except (ValueError, TypeError):
        return jsonify({'erro': 'O ano deve ser um número válido'}), 404

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if not nome or not genero:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        cursor.execute(
            "UPDATE livros SET nome=?, genero=?, ano=? WHERE id=?",
            (nome, genero, ano, id)
        )
        if cursor.rowcount == 0:
            return jsonify({'erro': 'Livro não encontrado'}), 404

        conn.commit()
        return redirect(url_for('pagina_inicial'))


# ---função de editar livro---
@app.route('/livros/editar/<int:id>', methods=['GET'])
def pagina_editar(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))   

    if not administrador():
        return "Acesso negado. Apenas administradores podem editar livros.", 403 

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        livro = cursor.execute(
            "SELECT * FROM livros WHERE id=?", (id,)).fetchone()

    if livro is None:
        return "Livro não encontrado", 404

    return render_template("editar.html", livro=dict(livro))


# ---função de deletar livro---
@app.route('/livros/deletar/<int:id>', methods=['POST'])
def deletar_livro(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if not administrador():
        return "Acesso negado. Apenas administradores podem deletar livros.", 403

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livros WHERE id=?", (id,))
        if cursor.rowcount == 0:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        conn.commit()
    return redirect(url_for('pagina_inicial'))


# ---função de login---
@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            return render_template(
                'login.html',
                erro='Preencha todos os campos.'
            )

        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            usuario = cursor.execute(
                "SELECT * FROM usuarios WHERE nome=?",
                (nome,)
            ).fetchone()

        if usuario and bcrypt.check_password_hash(usuario['senha'], senha):

            session['usuario'] = usuario['nome']
            session['usuario_id'] = usuario['id']
            session['perfil'] = usuario['perfil']

            return redirect(url_for('pagina_inicial'))

        return render_template(
            'login.html',
            erro='Usuário ou senha incorretos.'
        )

    return render_template('login.html')


#--- função para verificar o perfil do usuário---
def administrador():
    return session.get('perfil') == 'admin'


#---função de cadastro de usuário---
@app.route('/cadastro', methods=['GET','POST'])
def cadastro():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    if not administrador():
        return "Acesso negado.", 403

    if request.method =='POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            return render_template(
                'cadastro.html',
                erro='Preencha todos os campos.'
            )
        


        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

        perfil = request.form.get('perfil')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            try:
                usuario = cursor.execute(
                    "INSERT INTO usuarios (nome, senha, perfil) VALUES (?, ?, ?)",
                    (nome, senha_hash, perfil)
                )

                conn.commit()

            except sqlite3.IntegrityError:
                return render_template(
                    'cadastro.html',
                    erro='Erro: Nome de usuário já existe.'
                )   
            return redirect(url_for('pagina_inicial'))

    return render_template('cadastro.html')


@app.route('/livros/emprestar/<int:id>', methods=['POST'])
def emprestar_livro(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))

    if session['perfil'] != 'usuario':
        return "Somente usuários podem pegar livros.", 403

    usuario_id = session['usuario_id']

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()


        livro = cursor.execute("SELECT * FROM livros WHERE id=?", (id,)).fetchone()

        if livro is None:
            return "Livro não encontrado.", 404

        emprestado = cursor.execute(
            """ SELECT * FROM emprestimos WHERE livro_id=? AND devolver=0 """, (id,)).fetchone()

        if emprestado:
            return "Livro já está emprestado."

        cursor.execute(
            """ INSERT INTO emprestimos (usuario_id, livro_id, data_emprestimo) VALUES (?, ?, ?) """,( usuario_id, id, datetime.now().strftime("%d/%m/%Y")))

        conn.commit()

    return redirect(url_for('pagina_inicial'))

@app.route('/devolver/<int:id>', methods=['POST'])
def devolver(id):

    if 'usuario' not in session:
         return redirect(url_for('login'))

    if session['perfil'] != 'admin':
        return "Acesso negado", 403

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE emprestimos
            SET devolver=1
            WHERE id=?
        """, (id,))

        conn.commit()

    return redirect(url_for('listar_emprestimos'))


if __name__ == '__main__':
    init_db()
app.run(debug=True, host="0.0.0.0", port="5454")
