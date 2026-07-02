from flask import Flask, jsonify, request, render_template, url_for, redirect
import sqlite3

app = Flask(__name__)
DATABASE = 'biblioteca.db'
app.secret_key = 'sua_chave_secreta_aqui'


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS livros(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                genero TEXT NOT NULL,
                ano INTEGER NOT NULL
            )
        ''')
        print("\n ---- BIBLIOTECA ABERTA ---- ")


@app.route('/', methods=['GET'])
def pagina_inicial():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        livros = cursor.execute("SELECT * FROM  livros").fetchall()

        resultado = [dict(row) for row in livros]
        return render_template('index.html', resultados=resultado)


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


@app.route('/livros', methods=['POST'])
def adicionar_livro():
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


@app.route('/livros/atualizar/<int:id>', methods=['POST'])
def atualizar_livros(id):
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


@app.route('/livros/deletar/<int:id>', methods=['POST'])
def deletar_livro(id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livros WHERE id=?", (id,))
        if cursor.rowcount == 0:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        conn.commit()
    return redirect(url_for('pagina_inicial'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0", port="5454")
