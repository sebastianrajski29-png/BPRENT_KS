import sqlite3, os, pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from datetime import datetime
from google.colab import drive

# 1. Połączenie z Dyskiem Google i baza danych SQL
drive.mount('/content/drive', force_remount=True)
DB_DIR = "/content/drive/MyDrive/Ksiazka_Serwisowa"
os.makedirs(DB_DIR, exist_ok=True)
DB_NAME = os.path.join(DB_DIR, "auto_serwis_bp_rent_final.db")

conn = sqlite3.connect(DB_NAME); c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS auta (id INTEGER PRIMARY KEY AUTOINCREMENT, marka TEXT, model TEXT, rejestracja TEXT UNIQUE)')
c.execute('CREATE TABLE IF NOT EXISTS serwisy (id INTEGER PRIMARY KEY AUTOINCREMENT, samochod_id INTEGER, data TEXT, przebieg INTEGER, opis TEXT, koszt REAL)')
conn.commit(); conn.close()
# 2. DESIGN PREMIUM SMARTFONA Z DUŻYMI CZCIONKAMI (CSS)
css = """
<style>
    .phone-body { max-width: 365px; height: 690px; margin: 15px auto; border: 12px solid #1e293b; border-radius: 40px; background: #0b1329; overflow: hidden; position: relative; box-shadow: 0 30px 60px -15px rgba(0,0,0,0.8); display: flex; flex-direction: column; font-family: -apple-system, sans-serif; }
    .phone-notch { width: 110px; height: 20px; background: #1e293b; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; position: absolute; top: 0; left: 50%; transform: translateX(-50%); z-index: 200; }
    .app-header { background: #1a233d; border-bottom: 2px solid #38bdf8; color: #f8fafc; padding: 32px 10px 12px 10px; font-weight: 800; text-align: center; font-size: 20px; letter-spacing: 1px; }
    .card-c { border-radius: 18px; padding: 14px; background: #1a233d; border: 1px solid #2d3748; box-shadow: 0 10px 20px rgba(0,0,0,0.4); margin-bottom: 12px; }
    .card-h { background: #1e293b; border-left: 5px solid #38bdf8 !important; border-radius: 14px; padding: 12px; margin-bottom: 10px; position: relative; border: 1px solid #2d3748; }
    .cost-txt { font-size: 30px; color: #f43f5e; font-weight: 800; text-shadow: 0 0 15px rgba(244,63,94,0.4); }
    .badge-d { background: #2d3748; color: #38bdf8; border: 1px solid #4a5568; padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 11px; }
    .lbl-white { color: #f8fafc !important; font-weight: 700 !important; font-size: 15px !important; display: block; margin-top: 8px; margin-bottom: 4px; }
    .nav-c button { background: #1a233d !important; color: #94a3b8 !important; border: none !important; font-weight: 700 !important; font-size: 13px !important; border-top: 1px solid #2d3748 !important; }
    .widget-text input, .widget-dropdown select, .widget-textarea textarea { background: #0b1329 !important; border: 2px solid #334155 !important; color: #f8fafc !important; border-radius: 12px !important; font-size: 16px !important; padding: 12px !important; height: auto !important; }
    .widget-dropdown select { font-weight: 700 !important; border-color: #38bdf8 !important; background-color: #1a233d !important; }
    .widget-button button { font-weight: 800 !important; border-radius: 14px !important; font-size: 15px !important; height: 48px !important; }
</style>
"""
display(HTML(css))
# 3. KONTROLKI I POWIĘKSZONE POLA SYSTEMOWE (DUŻY WIDOK)
out = widgets.Output(layout=widgets.Layout(flex='1', overflow_y='auto', padding='12px'))

# Górny wybór pojazdu (Maksymalnie powiększony)
s_car = widgets.Dropdown(layout=widgets.Layout(width='100%', height='50px')).add_class("top-car-select")

# Formularz: Nowe Auto
t_mar = widgets.Text(placeholder='np. Skoda', layout=widgets.Layout(width='100%'))
t_mod = widgets.Text(placeholder='np. Octavia', layout=widgets.Layout(width='100%'))
t_rej = widgets.Text(placeholder='np. WI12345', layout=widgets.Layout(width='100%'))
b_car = widgets.Button(description='🚀 ZAPISZ SAMOCHÓD', button_style='primary', layout=widgets.Layout(width='100%'))

# Formularz: Nowy Serwis (Wyraziste opisy)
t_dat = widgets.DatePicker(value=datetime.now(), layout=widgets.Layout(width='100%'))
t_prz = widgets.IntText(value=0, layout=widgets.Layout(width='100%'))
t_kos = widgets.FloatText(value=0.0, layout=widgets.Layout(width='100%'))
t_opi = widgets.Textarea(placeholder='Wpisz zakres naprawy...', layout=widgets.Layout(width='100%', height='90px'))
b_srv = widgets.Button(description='🔧 ZAPISZ WPIS SERWISOWY', button_style='warning', layout=widgets.Layout(width='100%'))

# Usuwanie wpisu oraz pojazdu
s_del = widgets.Dropdown(layout=widgets.Layout(width='62%'))
b_del_srv = widgets.Button(description='🗑️ Usuń', button_style='danger', layout=widgets.Layout(width='35%', height='36px'))
b_del_car = widgets.Button(description='❌ USUŃ POJAZD Z GARAŻU', button_style='danger', layout=widgets.Layout(width='100%'))
# 4. FUNKCJE PRZETWARZANIA SQL W PYTHONIE
def dodaj_auto_sql(b):
    if not (t_mar.value and t_mod.value and t_rej.value): return
    try:
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("INSERT INTO auta (marka, model, rejestracja) VALUES (?, ?, ?)", (t_mar.value.strip(), t_mod.value.strip(), t_rej.value.strip().upper()))
        conn.commit(); conn.close()
    except: pass
    t_mar.value = ''; t_mod.value = ''; t_rej.value = ''; odswiez_baze_i_opcje(); klik_menu('home')

def dodaj_serwis_sql(b):
    if not (s_car.value and t_opi.value and t_prz.value and t_kos.value): return
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO serwisy (samochod_id, data, przebieg, opis, koszt) VALUES (?, ?, ?, ?, ?)", (int(s_car.value), t_dat.value.strftime('%Y-%m-%d'), int(t_prz.value), t_opi.value.strip(), float(t_kos.value)))
    conn.commit(); conn.close()
    t_prz.value = 0; t_kos.value = 0.0; t_opi.value = ''; odswiez_baze_i_opcje(); klik_menu('home')

def usun_serwis_sql(b):
    if not s_del.value: return
    conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("DELETE FROM serwisy WHERE id = ?", (int(s_del.value),)); conn.commit(); conn.close(); odswiez_ekran()

def usun_auto_sql(b):
    if not s_car.value: return
    conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("DELETE FROM serwisy WHERE samochod_id = ?", (int(s_car.value),)); c.execute("DELETE FROM auta WHERE id = ?", (int(s_car.value),)); conn.commit(); conn.close(); odswiez_baze_i_opcje(); klik_menu('home')

b_car.on_click(dodaj_auto_sql); b_srv.on_click(dodaj_serwis_sql); b_del_srv.on_click(usun_serwis_sql); b_del_car.on_click(usun_auto_sql); s_car.observe(lambda change: odswiez_ekran() if change['name'] == 'value' else None)
# 5. UKŁAD STRON MOBILNYCH Z ETYKIETAMI I RENDER SMARTFONA BP RENT
page_home = widgets.VBox([])
page_srv = widgets.VBox([
    widgets.HTML("<span class='lbl-white'>Data wykonania:</span>"), t_dat,
    widgets.HTML("<span class='lbl-white'>Aktualny przebieg (km):</span>"), t_prz,
    widgets.HTML("<span class='lbl-white'>Koszt całkowity naprawy (zł):</span>"), t_kos,
    widgets.HTML("<span class='lbl-white'>Opis wykonanych prac i części:</span>"), t_opi,
    widgets.HTML("<br>"), b_srv
], layout=widgets.Layout(display='none'))

page_car = widgets.VBox([
    widgets.HTML("<span class='lbl-white'>Marka pojazdu:</span>"), t_mar,
    widgets.HTML("<span class='lbl-white'>Model pojazdu:</span>"), t_mod,
    widgets.HTML("<span class='lbl-white'>Numer rejestracyjny:</span>"), t_rej,
    widgets.HTML("<br>"), b_car
], layout=widgets.Layout(display='none'))

def klik_menu(p):
    page_home.layout.display = 'block' if p=='home' else 'none'
    page_srv.layout.display = 'block' if p=='srv' else 'none'
    page_car.layout.display = 'block' if p=='car' else 'none'
    b_h.style.button_color = '#1a233d' if p=='home' else None
    b_s.style.button_color = '#1a233d' if p=='srv' else None
    b_c.style.button_color = '#1a233d' if p=='car' else None

b_h = widgets.Button(icon='grid-1x2-fill', description='Garaż', layout=widgets.Layout(flex='1', height='52px')); b_h.on_click(lambda b: klik_menu('home'))
b_s = widgets.Button(icon='tools', description='+ Serwis', layout=widgets.Layout(flex='1', height='52px')); b_s.on_click(lambda b: klik_menu('srv'))
b_c = widgets.Button(icon='plus-square-fill', description='+ Auto', layout=widgets.Layout(flex='1', height='52px')); b_c.on_click(lambda b: klik_menu('car'))
nav_bar = widgets.HBox([b_h, b_s, b_c], layout=widgets.Layout(width='100%')).add_class('nav-c')

def odswiez_baze_i_opcje():
    conn = sqlite3.connect(DB_NAME); df_a = pd.read_sql_query("SELECT id, marka, model, rejestracja FROM auta", conn); conn.close()
    s_car.options = [(f"🚘 {r['marka']} {r['model']} [{r['rejestracja']}]", r['id']) for _, r in df_a.iterrows()] if not df_a.empty else [('-- Brak aut w bazie --', '')]
    odswiez_ekran()

def odswiez_ekran():
    with out:
        clear_output(wait=True)
        if not s_car.value or s_car.value == '':
            display(HTML("<div class='text-center text-muted small py-5' style='color:#94a3b8 !important;'>Garaż firmy BP RENT jest pusty.<br><br>Dodaj auto w zakładce '+ Auto' na dolnym pasku.</div>")); return
        conn = sqlite3.connect(DB_NAME); df_s = pd.read_sql_query(f"SELECT id, data, przebieg, opis, koszt FROM serwisy WHERE samochod_id = {int(s_car.value)} ORDER BY data DESC", conn); conn.close()
        s_del.options = [(f"Wpis ID: {r['id']} ({r['data']})", r['id']) for _, r in df_s.iterrows()] if not df_s.empty else [('Brak napraw', '')]
        
        display(HTML(f"<div class='card-c text-center'><span style='color:#94a3b8; font-size:12px; font-weight:700; letter-spacing:0.5px;'>ŁĄCZNY KOSZT SERWISOWANIA</span><div class='cost-txt'>{df_s['koszt'].sum() if not df_s.empty else 0:,.2f} zł</div></div>".replace(",", " ")))
        display(HTML("<h6 style='color:#38bdf8; font-weight:800; font-size:13px; margin: 12px 0 8px 2px; letter-spacing:0.5px;'><i class='bi bi-clock-history me-2'></i>HISTORIA NAPRAW</h6>"))
        
        if df_s.empty: display(HTML("<div class='card-c text-center text-muted small' style='color:#94a3b8 !important;'>Brak wpisów serwisowych dla tego auta.</div>"))
        else:
            for _, s in df_s.iterrows():
                display(HTML(f"<div class='card-h'><div class='d-flex justify-content-between mb-2'><span class='badge-d'>{s['data']}</span><b style='color:#f8fafc; font-size:14px;'>{s['przebieg']:,} km</b></div><div style='color:#cbd5e1; font-size:15px; margin:6px 0; line-height:1.4;'>{s['opis']}</div><div class='text-end text-info fw-bold' style='font-size:14px; color:#38bdf8 !important;'>[ID: {s['id']}] {s['koszt']:.2f} zł</div></div>".replace(",", " ")))
        display(HTML("<hr style='border-color:#2d3748; margin:14px 0;'>"), widgets.HTML("<b style='color:#f43f5e; font-size:12px; display:block; margin-bottom:6px;'>⚙️ PANEL ZARZĄDZANIA POJAZDEM</b>"), widgets.HBox([s_del, b_del_srv]), widgets.HTML("<br>"), b_del_car)

# Wyrysowanie kompletnej obudowy luksusowego smartfona z dużymi polami
phone_layout = widgets.VBox([widgets.HTML("<div class='phone-notch'></div><div class='app-header'>🛡️ BP RENT</div>"), widgets.VBox([s_car, page_home, page_srv, page_car, out], layout=widgets.Layout(flex='1', overflow='hidden', padding='12px')), nav_bar]).add_class('phone-body')
display(phone_layout); odswiez_baze_i_opcje(); klik_menu('home')
