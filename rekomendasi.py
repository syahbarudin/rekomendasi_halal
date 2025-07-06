import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# --- FUNGSI BARU UNTUK IKON GITHUB ---
def tampilkan_ikon_github():
    """Menampilkan ikon GitHub dengan tulisan "Click Here" di atasnya."""
    # GANTI DENGAN URL GITHUB ANDA
    github_url = "https://github.com/username/repo"
    
    # CSS untuk styling wadah, teks, dan ikon
    st.markdown(f"""
    <style>
    #github-container {{
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 1000;
        text-align: center;
    }}
    .github-text {{
        font-size: 12px;
        color: grey;
        margin-bottom: 5px;
        font-family: sans-serif;
        text-decoration: none;
        font-weight: bold; /* Menambahkan tebal agar lebih terlihat */
    }}
    #github-link {{
        display: inline-block;
        transition: transform 0.2s ease-in-out;
    }}
    #github-link:hover {{
        transform: scale(1.15);
    }}
    .github-svg {{
        width: 25px;
        height: 25px;
    }}
    </style>
    
    <div id="github-container">
        <p class="github-text">Click here to view source code </p>
        
        <a href="{github_url}" target="_blank" id="github-link">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="github-svg">
                <path fill="grey" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
        </a>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """
    Memuat data dan menghitung statistik agregat untuk setiap produk.
    """
    try:
        nama_file = r'dataset_produk_halal.csv'
        df = pd.read_csv(
            nama_file,
            encoding='utf-8-sig',
            sep=None,
            engine='python'
        )
    except FileNotFoundError:
        st.error(f"File '{nama_file}' tidak ditemukan.")
        return None, None
    except Exception as e:
        st.error(f"Terjadi error saat membaca file CSV: {e}")
        return None, None

    # Validasi dan pembersihan data
    required_columns = {'user_id', 'item_id', 'rating'}
    if not required_columns.issubset(df.columns):
        st.error(f"Error: Kolom yang dibutuhkan {required_columns} tidak ditemukan.")
        return None, None
        
    df.dropna(inplace=True)
    df = df.astype({'user_id': 'int64', 'item_id': 'str', 'rating': 'float64'})
    if df.empty:
        st.error("Dataset kosong.")
        return None, None

    # Menghitung statistik produk: total rating untuk menentukan popularitas
    product_stats = df.groupby('item_id')['rating'].agg(
        total_ratings='count'
    ).sort_values(by='total_ratings', ascending=False).reset_index()
    
    return df, product_stats


# --- UI Aplikasi Streamlit ---
st.set_page_config(page_title="Analisis Produk & Pengguna", layout="wide")
st.title("Dashboard Analisis Produk & Pengguna Serupa 💡")

# Muat dan proses data
df, product_stats = load_and_process_data()

if df is not None:
    # Membuat dua tab utama
    tab1, tab2 = st.tabs(["⭐ Produk Terpopuler", "👥 Cari Pengguna Serupa"])

    # --- KONTEN TAB 1: PRODUK TERPOPULER ---
    with tab1:
        st.header("Produk Paling Banyak Dinilai Pengguna")
        st.write("Melihat produk mana yang paling populer berdasarkan jumlah rating yang diterima.")
        
        # Grafik Top 10 Produk Terpopuler
        top_10_products = product_stats.head(10)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(
            x='total_ratings', 
            y='item_id', 
            data=top_10_products, 
            palette='crest', 
            ax=ax
        )
        ax.set_title('Top 10 Produk Paling Populer', fontsize=16)
        ax.set_xlabel('Jumlah Total Rating Diterima', fontsize=12)
        ax.set_ylabel('Nama Produk', fontsize=12)
        # Menambahkan label jumlah di setiap bar
        for container in ax.containers:
            ax.bar_label(container, fmt='%d')
        st.pyplot(fig)
            
    # --- KONTEN TAB 2: CARI PENGGUNA SERUPA ---
    with tab2:
        st.header("Temukan Pengguna dengan Preferensi Sama")
        st.write("Pilih sebuah produk untuk melihat daftar semua pengguna yang pernah memberikan rating untuk produk tersebut.")
        
        # Dropdown untuk memilih item_id
        all_items = sorted(df['item_id'].unique())
        selected_item = st.selectbox("Pilih Produk:", all_items)
        
        # Tombol untuk menampilkan data
        if st.button("Tampilkan Data Pengguna"):
            if selected_item:
                # Filter DataFrame untuk menemukan semua baris dengan item_id yang dipilih
                similar_users_df = df[df['item_id'] == selected_item].sort_values(by='rating', ascending=False)
                
                st.subheader(f"Pengguna yang Menilai Produk: '{selected_item}'")
                
                if not similar_users_df.empty:
                    # Tampilkan tabel hasil
                    st.dataframe(
                        similar_users_df[['user_id', 'rating']].reset_index(drop=True),
                        use_container_width=True
                    )
                else:
                    st.info("Aneh, sepertinya tidak ada pengguna yang menilai produk ini.")

tampilkan_ikon_github()
