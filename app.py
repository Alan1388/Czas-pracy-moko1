import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- TWOJA LISTA PRACOWNIKÓW ---
PRACOWNICY = ["Alan",
    "Azamat", "Bartek", "Ivan", "Kamil", "Krzysiek", "Łukasz", 
    "Łukasz Ndg", "Maciek", "Marcel", "Marcin Brygadzista", 
    "Marcin Nowy", "Marcin Sz.", "Marek", "Marek Gru", 
    "Marek K.", "Misza", "Piotr S.", "Sasza"
]

FOLDER_ZDJEC = "zdjecia_pracownikow"
PLIK_LOGU = "rejestr_czasu.csv"

if not os.path.exists(FOLDER_ZDJEC):
    os.makedirs(FOLDER_ZDJEC)

st.set_page_config(page_title="Budowa - Rejestr", page_icon="🏗️")
st.title("🏗️ System Godzinowy MOKO")

osoba = st.selectbox("Wybierz pracownika:", ["-- Wybierz z listy --"] + PRACOWNICY)

if osoba != "-- Wybierz z listy --":
    typ = st.radio("Status:", ["Wejście (START)", "Wyjście (KONIEC)"])
    foto = st.camera_input("Zrób zdjęcie")

    if foto:
        if st.button("Zapisz i zatwierdź"):
            teraz = datetime.now()
            data_dzis = teraz.strftime("%Y-%m-%d")
            czas_str = teraz.strftime("%H:%M:%S")
            
            # Zapis zdjęcia
            plik_foto = f"{teraz.strftime('%Y%m%d_%H%M%S')}_{osoba.replace(' ', '_')}.jpg"
            with open(os.path.join(FOLDER_ZDJEC, plik_foto), "wb") as f:
                f.write(foto.getbuffer())
            
            # Liczenie czasu pracy
            h_sesji = 0.0
            if typ == "Wyjście (KONIEC)" and os.path.exists(PLIK_LOGU):
                try:
                    df_h = pd.read_csv(PLIK_LOGU)
                    ostatni_start = df_h[(df_h['Pracownik'] == osoba) & 
                                         (df_h['Typ'] == "Wejście (START)") & 
                                         (df_h['Data'] == data_dzis)].tail(1)
                    if not ostatni_start.empty:
                        start_t = datetime.strptime(ostatni_start.iloc[0]['Godzina'], "%H:%M:%S")
                        roznica = teraz - datetime.combine(teraz.date(), start_t.time())
                        h_sesji = round(roznica.total_seconds() / 3600, 2)
                except: h_sesji = 0.0

            # Zapis do CSV
            nowy_wpis = pd.DataFrame([[osoba, data_dzis, czas_str, typ, h_sesji]], 
                                    columns=["Pracownik", "Data", "Godzina", "Typ", "Suma_H"])
            
            if not os.path.exists(PLIK_LOGU) or os.stat(PLIK_LOGU).st_size == 0:
                nowy_wpis.to_csv(PLIK_LOGU, index=False)
            else:
                nowy_wpis.to_csv(PLIK_LOGU, mode='a', header=False, index=False)
            
            st.success(f"Zapisano! Sesja: {h_sesji} h. Miłej pracy!")
            st.balloons()

# --- PANEL SZEFA - SUMOWANIE ---
st.markdown("---")
if st.checkbox("📊 PANEL ROZLICZEŃ (Dla Szefa)"):
    if os.path.exists(PLIK_LOGU) and os.stat(PLIK_LOGU).st_size > 0:
        df = pd.read_csv(PLIK_LOGU)
        df['Data'] = pd.to_datetime(df['Data'])
        
        widok = st.radio("Zakres podsumowania:", ["Dzisiaj", "Ten Miesiąc"])
        
        if widok == "Dzisiaj":
            dzis = datetime.now().strftime("%Y-%m-%d")
            df_dzis = df[df['Data'].dt.strftime('%Y-%m-%d') == dzis]
            st.write(f"### Raport z dnia {dzis}")
            st.dataframe(df_dzis)
            st.metric("Suma godzin wszystkich pracowników (DZIŚ)", round(df_dzis['Suma_H'].sum(), 2))
            
        else:
            mies = datetime.now().month
            rok = datetime.now().year
            df_m = df[(df['Data'].dt.month == mies) & (df['Data'].dt.year == rok)]
            st.write(f"### Podsumowanie za miesiąc: {mies}/{rok}")
            
            # Tabela sumaryczna per pracownik
            tabela_plac = df_m.groupby('Pracownik')['Suma_H'].sum().reset_index()
            tabela_plac.columns = ['Pracownik', 'Łączna suma godzin (MIESIĄC)']
            st.table(tabela_plac)
            
            # Przycisk pobierania
            csv = tabela_plac.to_csv(index=False).encode('utf-8')
            st.download_button("Pobierz gotowe rozliczenie (CSV)", csv, f"suma_{mies}_{rok}.csv", "text/csv")
    else:
        st.info("Baza jest jeszcze pusta. Czekam na pierwszy wpis!")
