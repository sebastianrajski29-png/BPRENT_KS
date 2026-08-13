import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. NOWOCZESNA STYLIZACJA PREMIUM (DARK MODE FLOTY BP RENT)
st.set_page_config(page_title="BP RENT", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0b1329; color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; font-size: 16px; font-weight: bold; }
    .stTabs [data-baseweb="tab"] { background-color: #1a233d; border-radius: 12px; padding: 10px 20px; color: #94a3b8; }
    .stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }
    .stButton>button { width: 100%; height: 50px; font-size: 16px !important; font-weight: bold !important; border-radius: 14px !important; background: linear-gradient(135deg, #38bdf8, #0284c7) !important; color: white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: none; }
    div[data-testid="stDataFrame"] { box-shadow: 0 10px 20px rgba(0,0,0,0.4); border-radius: 16px; background-color: #1a233d; }
    .stSelectbox select, .stTextInput input, .stNumberInput input { font-size: 16px !important; padding: 12px !important; border-radius: 12px !important; background-color: #0b1329 !important; color: white !important; border: 1px solid #2d3748 !important; }
    .card-cost { border-radius: 18px; padding: 16px; background-color: #1a233d; border: 1px solid #2d3748; box-shadow: 0 10px 20px rgba(0,0,0,0.4); text-align: center; margin-bottom: 20px; }
    .cost-txt { font-size: 32px; color: #f43f5e; font-weight: 800; text-shadow: 0 0 15px rgba(244,63,94,0.3); }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ BP RENT - Książka Serwisowa")

# 2. INICJALIZACJA TRWAŁEJ BAZY DANYCH SQLITE
DB_NAME = "bp_rent_serwis.db"
conn = sqlite3.connect(DB_NAME); c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS auta (id INTEGER PRIMARY KEY AUTOINCREMENT, marka TEXT, model TEXT, rejestracja TEXT UNIQUE)')
c.execute('CREATE TABLE IF NOT EXISTS serwisy (id INTEGER PRIMARY KEY AUTOINCREMENT, samochod_id INTEGER, data TEXT, przebieg INTEGER, opis TEXT, koszt REAL)')
conn.commit(); conn.close()

# Funkcja pobierania aut z wymuszonym brakiem pamięci podręcznej chmury
def pobierz_auta_z_bazy():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, marka, model, rejestracja FROM auta", conn)
    conn.close()
    return df

df_a = pobierz_auta_z_bazy()

# 3. STRUKTURA ZAKŁADEK MOBILNYCH
tab1, tab2, tab3 = st.tabs(["📊 Garaż / Historia", "🔧 + Nowy Serwis", "🚘 + Nowe Auto"])

# --- ZAKŁADKA 3: DODAWANIE NOWEGO AUTA ---
with tab3:
    st.markdown("### 🚘 Rejestracja nowego pojazdu")
    mar = st.text_input("Marka pojazdu", key="c_mar")
    mod = st.text_input("Model pojazdu", key="c_mod")
    rej = st.text_input("Numer rejestracyjny", key="c_rej").upper()
    if st.button("🚀 ZAPISZ SAMOCHÓD INWENTARZOWY"):
        if mar and mod and rej:
            try:
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                c.execute("INSERT INTO auta (marka, model, rejestracja) VALUES (?, ?, ?)", (mar.strip(), mod.strip(), rej.strip()))
                conn.commit(); conn.close()
                st.cache_data.clear() # CZYSZCZENIE CACHE - WYMUSZENIE ODŚWIEŻENIA
                st.success("Pojazd dodany pomyślnie!")
                st.rerun()
            except: st.error("⚠️ Ten pojazd z tym numerem rejestracyjnym już istnieje!")
        else: st.warning("Wypełnij wszystkie pola!")

# --- JEŚLI BAZA AUT NIE JEST PUSTA, AKTYWUJEMY PODGLĄD I FORMULARZ SERWISU ---
if not df_a.empty:
    df_a['txt'] = df_a['marka'] + " " + df_a['model'] + " [" + df_a['rejestracja'] + "]"
    
    # --- ZAKŁADKA 2: DODAWANIE NAPRAWY ---
    with tab2:
        st.markdown("### 🔧 Dodaj wpis serwisowy / naprawę")
        sel_s = st.selectbox("Wybierz samochód z floty", df_a['txt'], key="s_box")
        id_s = int(df_a[df_a['txt'] == sel_s]['id'].values)
        dat = st.date_input("Data wykonania naprawy", datetime.now()).strftime("%Y-%m-%d")
        prz = st.number_input("Aktualny przebieg pojazdu (km)", min_value=0, step=1000, key="n_prz")
        kos = st.number_input("Koszt całkowity brutto (zł)", min_value=0.0, step=50.0, key="n_kos")
        opi = st.text_area("Dokładny opis naprawy i wymienionych części", key="n_opi")
        if st.button("🔧 ZAPISZ WPIS W HISTORII FLOTY"):
            if opi:
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                c.execute("INSERT INTO serwisy (samochod_id, data, przebieg, opis, koszt) VALUES (?, ?, ?, ?, ?)", (id_s, dat, prz, opi.strip(), kos))
                conn.commit(); conn.close()
                st.cache_data.clear() # CZYSZCZENIE CACHE - WYMUSZENIE ODŚWIEŻENIA
                st.success("Wpis serwisowy zapisany trwale!")
                st.rerun()
            else: st.warning("Opis naprawy nie może być pusty!")
            
    # --- ZAKŁADKA 1: PANEL GŁÓWNY I HISTORIA ---
    with tab1:
        sel_h = st.selectbox("Wybierz aktywny pojazd", df_a['txt'], key="h_box")
        id_h = int(df_a[df_a['txt'] == sel_h]['id'].values)
        conn = sqlite3.connect(DB_NAME); df_s = pd.read_sql_query(f"SELECT id, data AS Data, przebieg AS 'Przebieg (km)', opis AS 'Opis prac', koszt AS 'Koszt (zł)' FROM serwisy WHERE samochod_id = {id_h} ORDER BY data DESC", conn); conn.close()
        
        st.markdown(f"<div class='card-cost'><span style='color:#94a3b8; font-size:14px; font-weight:700;'>ŁĄCZNY KOSZT SERWISOWANIA POJAZDU</span><div class='cost-txt'>{df_s['Koszt (zł)'].sum():,.2f} zł</div></div>".replace(",", " "), unsafe_allow_html=True)
        if not df_s.empty:
            st.dataframe(df_s[['Data', 'Przebieg (km)', 'Opis prac', 'Koszt (zł)']], use_container_width=True)
            st.markdown("---")
            st.markdown("##### 🗑️ Usuwanie pojedynczego wpisu")
            del_id = st.selectbox("Wybierz numer ID wiersza z tabeli powyżej", df_s['id'].tolist(), key="del_s_box")
            if st.button("🗑️ USUŃ TEN WPIS SERWISOWY"):
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                c.execute("DELETE FROM serwisy WHERE id = ?", (int(del_id),))
                conn.commit(); conn.close()
                st.cache_data.clear() # CZYSZCZENIE CACHE - WYMUSZENIE ODŚWIEŻENIA
                st.success("Wpis usunięty!")
                st.rerun()
        else: st.info("ℹ️ Brak wpisów serwisowych dla tego pojazdu.")
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("❌ USUŃ TEN SAMOCHÓD CAŁKOWICIE Z GARAŻU"):
            conn = sqlite3.connect(DB_NAME); c = conn.cursor()
            c.execute("DELETE FROM serwisy WHERE samochod_id = ?", (id_h,))
            c.execute("DELETE FROM auta WHERE id = ?", (id_h,))
            conn.commit(); conn.close()
            st.cache_data.clear() # CZYSZCZENIE CACHE - WYMUSZENIE ODŚWIEŻENIA
            st.success("Pojazd wymazany z bazy floty!")
            st.rerun()
else:
    with tab1: 
        st.info("📋 Garaż firmy BP RENT jest pusty. Przejdź do zakładki '+ Auto' na górze, aby zarejestrować pierwszy pojazd floty.")

