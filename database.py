import sqlite3
from sqlite3 import Error
import streamlit as st

def create_connection():
    try:
        conn = sqlite3.connect('auction_database.db')
        create_tables(conn)
        return conn
    except Error as e:
        print(f"Error: {e}")
        st.error(f"Error: {e}")
        return None

def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                whatsapp TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                image BLOB,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                starting_bid REAL NOT NULL,
                current_bid REAL NOT NULL,
                is_featured BOOLEAN DEFAULT 0,
                artwork_dimensions TEXT,
                artwork_technique TEXT,
                artwork_year INTEGER,
                artwork_status TEXT DEFAULT 'active'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auction_id INTEGER,
                user_id INTEGER,
                amount REAL NOT NULL,
                bid_time TIMESTAMP NOT NULL,
                FOREIGN KEY (auction_id) REFERENCES auctions (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
    except Error as e:
        print(f"Error creating tables: {e}")