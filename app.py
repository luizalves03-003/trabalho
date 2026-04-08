from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'tarefa.db' 

def init_db():
    """Cria a tabela no banco de dados se ela não existir."""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 titulo TEXT NOT NULL,
                 concluida INTEGER DEFAULT 0
            )
        ''')

@app.route('/tarefas', methods=['POST'])
def criar_tarefa():
    """Cria uma nova tarefa (POST)."""
    dados = request.json

    if not dados or 'titulo' not in dados:
        return jsonify({"erro": "Título é obrigatório"}), 400
    
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            "INSERT INTO tarefas (titulo) VALUES (?)",
            (dados['titulo'],)
        )
        conn.commit()
    
    return jsonify({"mensagem": "Tarefa criada!"}), 201

@app.route('/tarefas', methods=['GET'])
def lista_tarefas():
    """Lista todas as tarefas (GET)."""
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        tarefas = conn.execute("SELECT * FROM tarefas").fetchall()
    
    return jsonify([dict(t) for t in tarefas])

@app.route('/tarefas/<int:id>/concluir', methods=['PUT'])
def concluir_tarefa(id):
    """Marca uma tarefa específica como concluída (PUT)."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute(
            "UPDATE tarefas SET concluida = 1 WHERE id = ?",
            (id,)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"erro": "Tarefa não encontrada"}), 404

    return jsonify({"mensagem": "Tarefa concluída!"})

@app.route('/tarefas/<int:id>', methods=['DELETE'])
def deletar_tarefa(id):
    """Deleta uma tarefa pelo ID (DELETE)."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("DELETE FROM tarefas WHERE id = ?", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"erro": "Tarefa não encontrada"}), 404

    return jsonify({"mensagem": "Tarefa deletada!"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)