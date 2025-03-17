import streamlit as st
from datetime import datetime
from database import create_connection
from PIL import Image
import io
import time
from sqlite3 import Error  # Add this import

st.set_page_config(page_title="Art Auction", layout="wide")

def init_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None

def main():
    init_session_state()
    
    # Add login status in the sidebar
    with st.sidebar:
        if st.session_state.username:
            st.success(f"Logged in as: {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.user_id = None
                st.session_state.username = None
                st.rerun()
    
    st.title("Art Auction Gallery")
    
    menu = ["Home", "Auctions"]
    if not st.session_state.user_id:
        menu.extend(["Login", "Register"])
    
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Home":
        show_home()
    elif choice == "Auctions":
        show_auctions()
    elif choice == "Login":
        show_login()
    elif choice == "Register":
        show_register()

def show_home():
    st.header("Welcome to Art Auction")
    st.write("Discover unique paintings and participate in live auctions!")

def show_login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                         (username, password))
            user = cursor.fetchone()
            
            if user:
                st.session_state.user_id = user[0]  # ID is first column
                st.session_state.username = user[1]  # Username is second column
                st.success("Logged in successfully!")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials")
            conn.close()

def show_register():
    st.header("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    whatsapp = st.text_input("WhatsApp Number")
    
    if st.button("Register"):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, whatsapp) VALUES (?, ?, ?)",
                             (username, password, whatsapp))
                conn.commit()
                st.success("Registration successful! Please login.")
                time.sleep(1)
                st.rerun()
            except Error as e:
                st.error(f"Error: {e}")
            conn.close()

def show_auctions():
    st.header("Leilões Ativos")
    
    if st.session_state.user_id:
        show_add_auction_form()  # Exibe o formulário diretamente
            
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auctions WHERE end_time > datetime('now')")
        auctions = cursor.fetchall()
        
        for auction in auctions:
            col1, col2 = st.columns([1, 2])
            with col1:
                if auction[3]:
                    try:
                        image = Image.open(io.BytesIO(auction[3]))
                        st.image(image, caption=auction[1])
                    except Exception:
                        st.image("placeholder.png", caption=auction[1])
            with col2:
                st.subheader(auction[1])
                st.write(auction[2])
                st.write(f"Lance atual: R${auction[7]:.2f}")
                
                if st.session_state.user_id:
                    bid_amount = st.number_input(
                        "Seu lance",
                        min_value=float(auction[7] + 1),
                        key=f"bid_{auction[0]}"
                    )
                    if st.button("Fazer Lance", key=f"button_{auction[0]}"):
                        place_bid(auction[0], bid_amount)
                else:
                    st.warning("Faça login para dar lances")
        conn.close()


def show_add_auction_form():
    st.subheader("Adicionar Novo Leilão")
    with st.form(key='auction_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Título*")
            description = st.text_area("Descrição*", height=50)
            image = st.file_uploader("Upload da Imagem da Obra*", type=['png', 'jpg', 'jpeg'])
        
        with col2:
            start_date = st.date_input("Data de Início*")
            end_date = st.date_input("Data de Término*")
            starting_bid = st.number_input("Lance Inicial (R$)*", min_value=100.0, step=50.0)
        
        st.markdown("---")
        col3, col4 = st.columns(2)
        
        with col3:
            dimensions = st.text_input("Dimensões da Obra* (ex: 60x80cm)")
            technique = st.text_input("Técnica*")
        
        with col4:
            year = st.number_input("Ano*", min_value=1900, max_value=2100, value=2024)
        
        st.markdown("*Campos obrigatórios")
        submit_button = st.form_submit_button(label='Criar Leilão')
    
    if submit_button:
        # Validate all required fields
        if not title:
            st.error("Por favor, insira um título.")
            return
        if not description:
            st.error("Por favor, insira uma descrição.")
            return
        if not image:
            st.error("Por favor, faça upload de uma imagem.")
            return
        if not dimensions:
            st.error("Por favor, insira as dimensões da obra.")
            return
        if not technique:
            st.error("Por favor, insira a técnica utilizada.")
            return
        if end_date <= start_date:
            st.error("A data de término deve ser posterior à data de início.")
            return
    
        try:
            # Process and optimize image
            img = Image.open(image)
            img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            img_byte_arr = img_byte_arr.getvalue()
            
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    print(f"Debug - Inserindo leilão: {title}")
                    cursor.execute("""
                        INSERT INTO auctions (
                            title, description, image, start_time, end_time,
                            starting_bid, current_bid, artwork_dimensions,
                            artwork_technique, artwork_year
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        title, description, img_byte_arr,
                        start_date.strftime('%Y-%m-%d 00:00:00'),
                        end_date.strftime('%Y-%m-%d 23:59:59'),
                        starting_bid, starting_bid, dimensions,
                        technique, year
                    ))
                    conn.commit()
                    print("Debug - Leilão inserido com sucesso")
                    st.success("Leilão criado com sucesso!")
                    time.sleep(1)
                    st.rerun()
                except Error as e:
                    print(f"Debug - Erro no banco de dados: {e}")
                    st.error(f"Erro ao criar leilão: {e}")
                finally:
                    conn.close()
        except Exception as e:
            print(f"Debug - Erro ao processar imagem: {e}")
            st.error(f"Erro ao processar a imagem: {e}")

def place_bid(auction_id, amount):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO bids (auction_id, user_id, amount, bid_time)
                VALUES (?, ?, ?, datetime('now'))
            """, (auction_id, st.session_state.user_id, amount))
            
            cursor.execute("UPDATE auctions SET current_bid = ? WHERE id = ?",
                         (amount, auction_id))
            conn.commit()
            st.success("Bid placed successfully!")
        except Error as e:
            st.error(f"Error placing bid: {e}")
        conn.close()

def show_auctions():
    st.header("Leilões Ativos")
    
    if st.session_state.user_id:
        show_add_auction_form()  # Exibe o formulário diretamente
            
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auctions WHERE end_time > datetime('now')")
        auctions = cursor.fetchall()
        
        for auction in auctions:
            col1, col2 = st.columns([1, 2])
            with col1:
                if auction[3]:
                    try:
                        image = Image.open(io.BytesIO(auction[3]))
                        st.image(image, caption=auction[1])
                    except Exception:
                        st.image("placeholder.png", caption=auction[1])
            with col2:
                st.subheader(auction[1])
                st.write(auction[2])
                st.write(f"Lance atual: R${auction[7]:.2f}")
                
                if st.session_state.user_id:
                    bid_amount = st.number_input(
                        "Seu lance",
                        min_value=float(auction[7] + 1),
                        key=f"bid_{auction[0]}"
                    )
                    if st.button("Fazer Lance", key=f"button_{auction[0]}"):
                        place_bid(auction[0], bid_amount)
                else:
                    st.warning("Faça login para dar lances")
            
            # Recupera e exibe os lances para este leilão
            cursor.execute("""
                SELECT u.username, b.amount, b.bid_time
                FROM bids b
                JOIN users u ON b.user_id = u.id
                WHERE b.auction_id = ?
                ORDER BY b.bid_time DESC
            """, (auction[0],))
            bids = cursor.fetchall()
            
            if bids:
                st.write("### Lances Realizados")
                bid_data = {
                    "Usuário": [bid[0] for bid in bids],
                    "Valor do Lance (R$)": [f"{bid[1]:.2f}" for bid in bids],
                    "Data e Hora": [bid[2] for bid in bids]
                }
                st.table(bid_data)
            else:
                st.write("Nenhum lance realizado ainda.")
            
            st.markdown("---")
        
        conn.close()


if __name__ == "__main__":
    main()