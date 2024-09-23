# database.py

import sqlite3

# Função para conectar ao banco de dados
def conectar():
    conn = sqlite3.connect('encomendas.db')
    return conn, conn.cursor()

# Função para criar a tabela de pedidos (caso não exista)
def criar_tabela():
    conn, cursor = conectar()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        tema TEXT,
        moldura TEXT,
        tamanho TEXT,
        tamanho_personalizado TEXT,
        data_pedido DATE,
        tempo_entrega INTEGER,
        data_entrega DATE,
        condicoes_pagamento TEXT,
        forma_pagamento TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Função para listar pedidos
def listar_pedidos():
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

# Função para editar um pedido
def editar_pedido(id, cliente, tema, moldura, tamanho, tamanho_personalizado, data_pedido, tempo_entrega, data_entrega, condicoes_pagamento, forma_pagamento):
    conn, cursor = conectar()
    cursor.execute('''
    UPDATE pedidos SET 
    cliente = ?, tema = ?, moldura = ?, tamanho = ?, tamanho_personalizado = ?, 
    data_pedido = ?, tempo_entrega = ?, data_entrega = ?, 
    condicoes_pagamento = ?, forma_pagamento = ?
    WHERE id = ?
    ''', (cliente, tema, moldura, tamanho, tamanho_personalizado, data_pedido, tempo_entrega, data_entrega, condicoes_pagamento, forma_pagamento, id))
    conn.commit()
    conn.close()

# Função para excluir um pedido
def excluir_pedido(id):
    conn, cursor = conectar()
    cursor.execute('DELETE FROM pedidos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
