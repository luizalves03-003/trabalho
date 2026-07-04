from flask import Flask, jsonify, request, render_template, url_for, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt

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
                nome TEXT NOT NULL,
                senha TEXT NOT NULL
            )
            
        ''')

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

# ---função de buscar livro por id---


@app.route('/livros/<int:id>', methods=['GET'])
def livro_id(id):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM livros WHERE id = ?", (id,))
        livro_row = cursor. fetchone()

        if livro_row:
            return jsonify(dict(livro_row))
        return jsonify({'erro': 'Livro não encontrado'}), 404

# ---função de buscar livro por gênero---


@app.route('/livros/genero/<string:genero_nome>', methods=['GET'])
def genero_livros(genero_nome):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livros WHERE genero = ?", (genero_nome,))
        livros_row = cursor.fetchall()

        if livros_row:
            resultado = [dict(row) for row in livros_row]
            return jsonify(resultado)
        return jsonify({'erro': 'livro não encontrado'}), 404


@app.route('/livros/genero', methods=['GET'])
def genero_livros_html():
    genero = request.args.get('genero')
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM livros WHERE genero LIKE ?", (f"%{genero}%",))
        livros_row = cursor.fetchall()

        if livros_row:
            resultado = [dict(row) for row in livros_row]
            return render_template('index.html', resultados=resultado)
        return jsonify({'erro': 'livro não encontrado'}), 404


# ---função de adicionar livro---
@app.route('/livros/add', methods=['POST'])
def adicionar_livro():

    if 'usuario' not in session:
        return redirect(url_for('login'))

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

            return redirect(url_for('pagina_inicial'))

        return render_template(
            'login.html',
            erro='Usuário ou senha incorretos.'
        )

    return render_template('login.html')


@app.route('/login/entrar', methods=['GET'])
def pagina_login():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        usuarios = cursor.execute("SELECT * FROM usuarios").fetchall()

        logar = [dict(row) for row in usuarios]
        return render_template('login.html', resultados=logar)


@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    if request.method =='POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            return render_template(
                'cadastro.html',
                erro='Preencha todos os campos.'
            )

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
                (nome, senha_hash)
            )

            conn.commit()

        return redirect(url_for('pagina_login'))

    return render_template('cadastro.html')

@app.route('/cadastro/novo', methods=['GET'])
def pagina_cadastro():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        usuarios = cursor.execute("SELECT * FROM usuarios").fetchall()

        resultado = [dict(row) for row in usuarios]
        return render_template('cadastro.html', resultados=resultado)


if __name__ == '__main__':
    init_db()
app.run(debug=True, host="0.0.0.0", port="5454")
