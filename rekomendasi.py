import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_and_process_data():
    """
    Memuat data dan menghitung statistik agregat untuk setiap produk.
    """
    try:
        nama_file = r'F:\Perkuliahan\Semester 6\Data Mining\dataset_produk_halal.csv'
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