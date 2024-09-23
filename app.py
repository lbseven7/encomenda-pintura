import streamlit as st
from datetime import date, timedelta
import sqlite3
import pandas as pd
from fpdf import FPDF

# Função para criar conexão com o banco de dados
def create_connection():
    conn = sqlite3.connect('encomendas.db', check_same_thread=False)
    return conn

# Função para criar a tabela de pedidos, se não existir
def create_table(conn):
    cursor = conn.cursor()
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

# Função para salvar um pedido no banco de dados
def insert_pedido(conn, pedido):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO pedidos (
        cliente, tema, moldura, tamanho, tamanho_personalizado, 
        data_pedido, tempo_entrega, data_entrega, 
        condicoes_pagamento, forma_pagamento
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', pedido)
    conn.commit()

# Função para buscar todos os pedidos
def fetch_pedidos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos")
    return cursor.fetchall()

# Função para deletar um pedido
def delete_pedido(conn, pedido_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
    conn.commit()

# Função para atualizar um pedido
def update_pedido(conn, pedido):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE pedidos
    SET cliente = ?, tema = ?, moldura = ?, tamanho = ?, tamanho_personalizado = ?, 
        data_pedido = ?, tempo_entrega = ?, data_entrega = ?, 
        condicoes_pagamento = ?, forma_pagamento = ?
    WHERE id = ?
    ''', pedido)
    conn.commit()

# Função para gerar o relatório em PDF
def gerar_relatorio_pdf(pedidos):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Relatório de Pedidos", ln=True, align="C")
    
    pdf.set_font("Arial", "B", 12)
    pdf.ln(10)  # Espaçamento
    
    for pedido in pedidos:
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, f"ID: {pedido[0]} | Cliente: {pedido[1]} | Tema: {pedido[2]} | Moldura: {pedido[3]}", ln=True)
        pdf.cell(200, 10, f"Tamanho: {pedido[4]} | Data Pedido: {pedido[6]} | Entrega: {pedido[8]} | Pagamento: {pedido[10]}", ln=True)
        pdf.ln(5)  # Pequeno espaçamento entre pedidos

    pdf_file = "relatorio_pedidos.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Conectando ao banco de dados
conn = create_connection()
create_table(conn)

# Título da aplicação
st.title("Gerenciamento de Encomendas LBarbosa")

# Input do nome do cliente
cliente = st.text_input("Nome do Cliente")

# Dropdown para o tema da pintura
temas = ["Escolha o tema", "Animais", "Paisagem", "Figurativo", "Abstrato", "Retrato", "Marinha", "Natureza Morta"]
tema = st.selectbox("Tema da Pintura", temas)

# Dropdown para a moldura
moldura = ["Sem Moldura", "Com Moldura"]
moldura = st.selectbox("Moldura", moldura)

# Dropdown para o tamanho da tela
tamanho = ["Escolha o tamanho", "50cm x 70cm", "60cm x 80cm", "70cm x 90cm", "80cm x 100cm", "100cm x 150cm"]
tamanho = st.selectbox("Tamanho da Tela em (cm)", tamanho)
tamanho_personalizado = st.text_input("Tamanho personalizado em (cm)")

# Data atual do pedido
data_pedido = date.today()
st.write(f"Data do Pedido: {data_pedido}")

# Input para o tempo de entrega em dias
tempo_entrega = st.number_input("Tempo de Entrega (dias)", min_value=15, max_value=365, value=15)
data_entrega = data_pedido + timedelta(days=tempo_entrega)
st.write(f"Data Prevista de Entrega: {data_entrega}")

# Input para condições de pagamento
condicoes_pagamento = st.text_area("Condições de Pagamento (Opcional)")
pagamento = ["Dinheiro", "Cartão", "Pix", "Transferência", "Cheque", "Promissória"]
forma_pagamento = st.selectbox("Forma de pagamento", pagamento)

# Botão para salvar o pedido
if st.button("Salvar Pedido"):
    if cliente and tema != "Escolha o tema" and moldura and tamanho != "Escolha o tamanho":
        pedido = (
            cliente, tema, moldura, tamanho, tamanho_personalizado, 
            data_pedido, tempo_entrega, data_entrega, 
            condicoes_pagamento, forma_pagamento
        )
        insert_pedido(conn, pedido)
        st.success(f"Pedido salvo com sucesso! Entrega prevista para {data_entrega}.")
    else:
        st.error("Por favor, preencha todos os campos obrigatórios.")

# Seção para exibir os registros salvos
st.subheader("Pedidos Salvos")

# Exibir os pedidos salvos
if st.button("Mostrar Pedidos"):
    pedidos = fetch_pedidos(conn)
    
    if pedidos:
        df = pd.DataFrame(pedidos, columns=["ID", "Cliente", "Tema", "Moldura", "Tamanho", "Tamanho Personalizado", "Data Pedido", "Tempo Entrega", "Data Entrega", "Condições de Pagamento", "Forma de Pagamento"])
        st.dataframe(df)
    else:
        st.write("Nenhum pedido encontrado.")

# Seção para apagar um pedido
st.subheader("Apagar um Pedido")

# Carregar todos os IDs dos pedidos para o dropdown
pedido_ids = [pedido[0] for pedido in fetch_pedidos(conn)]

if pedido_ids:
    pedido_id = st.selectbox("Selecione o ID do Pedido para Apagar", pedido_ids)
    
    if st.button("Apagar Pedido"):
        delete_pedido(conn, pedido_id)
        st.success(f"Pedido com ID {pedido_id} apagado com sucesso.")
else:
    st.write("Nenhum pedido disponível para apagar.")

# Seção de Relatório
st.subheader("Gerar Relatório")

if st.button("Gerar Relatório em PDF"):
    pedidos = fetch_pedidos(conn)
    
    if pedidos:
        pdf_file = gerar_relatorio_pdf(pedidos)
        st.success("Relatório gerado com sucesso!")
        with open(pdf_file, "rb") as pdf:
            st.download_button(
                label="Baixar Relatório em PDF",
                data=pdf,
                file_name=pdf_file,
                mime="application/pdf"
            )
    else:
        st.write("Nenhum pedido encontrado para gerar o relatório.")

# Seção para editar um pedido
st.subheader("Editar um Pedido")

if pedido_ids:
    pedido_id = st.selectbox("Selecione o ID do Pedido para Editar", pedido_ids)

    # Carregar os dados do pedido selecionado
    pedido = next((p for p in fetch_pedidos(conn) if p[0] == pedido_id), None)

    if pedido:
        # Preencher os campos com os dados atuais
        cliente = st.text_input("Nome do Cliente", value=pedido[1], key=f"edit_cliente_{pedido_id}")
        
        tema_index = temas.index(pedido[2]) if pedido[2] in temas else 0
        tema = st.selectbox("Tema da Pintura", temas, index=tema_index, key=f"edit_tema_{pedido_id}")

        moldura_index = ["Sem Moldura", "Com Moldura"].index(pedido[3]) if pedido[3] in ["Sem Moldura", "Com Moldura"] else 0
        moldura = st.selectbox("Moldura", ["Sem Moldura", "Com Moldura"], index=moldura_index, key=f"edit_moldura_{pedido_id}")

        tamanho_index = tamanho.index(pedido[4]) if pedido[4] in tamanho else 0
        tamanho = st.selectbox("Tamanho da Tela em (cm)", tamanho, index=tamanho_index, key=f"edit_tamanho_{pedido_id}")

        tamanho_personalizado = st.text_input("Tamanho personalizado em (cm)", value=pedido[5], key=f"edit_tamanho_personalizado_{pedido_id}")

        tempo_entrega = st.number_input("Tempo de Entrega (dias)", min_value=15, max_value=365, value=pedido[7], key=f"edit_tempo_entrega_{pedido_id}")
        data_entrega = data_pedido + timedelta(days=tempo_entrega)
        st.write(f"Data Prevista de Entrega: {data_entrega}")

        condicoes_pagamento = st.text_area("Condições de Pagamento (Opcional)", value=pedido[9], key=f"edit_condicoes_pagamento_{pedido_id}")
        
        forma_pagamento_index = pagamento.index(pedido[10]) if pedido[10] in pagamento else 0
        forma_pagamento = st.selectbox("Forma de pagamento", pagamento, index=forma_pagamento_index, key=f"edit_forma_pagamento_{pedido_id}")

        # Botão para atualizar o pedido
        if st.button("Atualizar Pedido", key=f"atualizar_{pedido_id}"):
            updated_pedido = (
                cliente, tema, moldura, tamanho, tamanho_personalizado, 
                data_pedido, tempo_entrega, data_entrega, 
                condicoes_pagamento, forma_pagamento, pedido_id
            )
            update_pedido(conn, updated_pedido)
            st.success(f"Pedido com ID {pedido_id} atualizado com sucesso.")
