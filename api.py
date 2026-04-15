from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)
DATABASE = 'biblioteca.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS livros(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                genero TEXT NOT NULL,
                preco REAL NOT NULL
            )
        ''')
        print("\n ---- BIBLIOTECA ABERTA ---- ")

@app.route('/livros', methods=['GET'])
def listar_livros():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        livros = cursor.execute("SELECT * FROM  livros").fetchall()

        resultado = [dict(row) for row in livros]
        return jsonify(resultado)
    
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
        return jsonify({'erro': 'Livro não encontrdo'}), 404

@app.route('/livros', methods=['POST'])
def adicionar_livro():
    dados = request.json
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO livros (nome, genero, preco) VALUES (?,?,?)",
            (dados['nome'], dados['genero'], dados['preco'])
        )
        conn.commit()
    return jsonify({"mensagem": "livro adicionado!"}),201

@app.route('/livros/<int:id>', methods=['PUT'])
def ataulizar_livros(id):
    dados = request.json
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            "UPDATE livros SET nome=?, genero=?, preco=? WHERE id=?",
            (dados['nome'], dados['genero'], dados['preco'], id)
        )
        conn.commit()
    return jsonify({"mensagem":"livro atualizado!"})

@app.route('/livros/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM livros WHERE id=?",(id,))
        conn.commit()
    return jsonify({"mensagem":"livro removido!"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)