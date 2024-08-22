import streamlit as st
from datetime import date, timedelta
import sqlite3

# Conectando ao banco de dados (ou criando-o)
conn = sqlite3.connect('encomendas.db')
cursor = conn.cursor()

# Criando a tabela de pedidos se não existir
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

# Título da aplicação
st.title("Gerenciamento de Encomendas LBarbosa")

# Input do nome do cliente
cliente = st.text_input("Nome do Cliente")

# Dropdown para o tema da pintura
temas = ["Escolha o tema","Paisagem", "Figurativo", "Abstrato", "Retrato", "Marinha", "Natureza Morta"]
tema = st.selectbox("Tema da Pintura", temas)

# Dropdown para a moldura
moldura = ["Escolha","Com Moldura", "Sem Moldura"]
moldura = st.selectbox("Moldura", moldura)

# Dropdown para o tamanho da tela
tamanho = ["Escolha o tamanho","50cm x 70cm","60cm x 80cm", "70cm x 90cm","80cm x 100cm"]
tamanho = st.selectbox("Tamanho da Tela em (cm)", tamanho)
tamanho_personalizado = st.text_input("Tamanho personalizado em (cm)", "Digite o tamanho (cm x cm)")

# Data atual do pedido
data_pedido = date.today()
st.write(f"Data do Pedido: {data_pedido}")

# Input para o tempo de entrega em dias
tempo_entrega = st.number_input("Tempo de Entrega (dias)", min_value=15, max_value=365, value=15)
data_entrega = data_pedido + timedelta(days=tempo_entrega)
st.write(f"Data Prevista de Entrega:")
st.write(data_entrega)

# Input para condições de pagamento
condicoes_pagamento = st.text_area("Condições de Pagamento (Opcional)")
pagamento = ["Dinheiro", "Cartão", "Pix", "Transferência", "Cheque", "Promissória"]
forma_pagamento = st.selectbox("Forma de pagamento", pagamento)

# Botão para salvar o pedido
if st.button("Salvar Pedido"):
    # Salvando os dados no banco de dados
    cursor.execute('''
    INSERT INTO pedidos (
        cliente, tema, moldura, tamanho, tamanho_personalizado, 
        data_pedido, tempo_entrega, data_entrega, 
        condicoes_pagamento, forma_pagamento
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        cliente, tema, moldura, tamanho, tamanho_personalizado, 
        data_pedido, tempo_entrega, data_entrega, 
        condicoes_pagamento, forma_pagamento
    ))
    
    conn.commit()
    st.success(f"Pedido salvo com sucesso! Entrega prevista para {data_entrega}.")
