import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- LISTA PRACOWNIKÓW ---
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

st.set_page_config(page_title="Rejestr Budowa", page_icon="🏗️")
st.title("🏗️ System Godzinowy")

osoba = st.selectbox("Wybierz pracownika:", ["-- Wybierz z listy --"] + PRACOWNICY)

if osoba != "-- Wybierz z listy --":
    typ = st.radio("Status:", ["Wejście do pracy (START)", "Wyjście z pracy (KONIEC)"])
    foto = st.camera_input("Zrób zdjęcie")

    if foto:
        if st.button("Zapisz godzinę"):
            teraz = datetime.now()
            data_dzis = teraz.strftime("%Y-%m-%d")
            
            # Zapis zdjęcia
            bezpieczne_nazwisko = osoba.replace(" ", "_").replace(".", "")
            plik_foto = f"{teraz.strftime('%Y%m%d_%H%M%S')}_{bezpieczne_nazwisko}.jpg"
            with open(os.path.join(FOLDER_ZDJEC, plik_foto), "wb") as f:
                f.write(foto.getbuffer())
            
            # Liczenie czasu
            przepracowane_h = 0.0
            if typ == "Wyjście z pracy (KONIEC)" and os.path.exists(PLIK_LOGU):
                df_hist = pd.read_csv(PLIK_LOGU)
                # Szukamy ostatniego STARTU z dzisiaj dla tej osoby
                ostatni_start = df_hist[(df_hist['Pracownik'] == osoba) & 
                                        (df_hist['Typ'] == "Wejście do pracy (START)") & 
                                        (df_hist['Data'] == data_dzis)].tail(1)
                if not ostatni_start.empty:
                    start_dt = datetime.strptime(ostatni_start.iloc[0]['Godzina'], "%H:%M:%S")
                    roznica = teraz - datetime.combine(teraz.date(), start_dt.time())
                    przepracowane_h = round(roznica.total_seconds() / 3600, 2)

            # Zapis do bazy
            nowy_wpis = pd.DataFrame([[
                osoba, data_dzis, teraz.strftime("%H:%M:%S"), typ, plik_foto, przepracowane_h
            ]], columns=["Pracownik", "Data", "Godzina", "Typ", "Plik", "Godziny_Suma"])
            
            if not os.path.exists(PLIK_LOGU):
                nowy_wpis.to_csv(PLIK_LOGU, index=False)
            else:
                nowy_wpis.to_csv(PLIK_LOGU, mode='a', header=False, index=False)
            
            st.success(f"Zapisano! Sesja: {przepracowane_h} h")

# --- PANEL DLA SZEFA ---
st.markdown("---")
if st.checkbox("📊 PANEL ROZLICZEŃ (Dla Szefa)"):
    if os.path.exists(PLIK_LOGU):
        df = pd.read_csv(PLIK_LOGU)
        df['Data'] = pd.to_datetime(df['Data'])
        
        t1, t2 = st.tabs(["Dzisiejsze wpisy", "SUMA MIESIĘCZNA"])
        
        with t1:
            dzis = datetime.now().strftime("%Y-%m-%d")
            df_dzis = df[df['Data'].dt.strftime('%Y-%m-%d') == dzis]
            st.dataframe(df_dzis[["Pracownik", "Godzina", "Typ", "Godziny_Suma"]])
        
        with t2:
            obecny_miesiac = datetime.now().month
            obecny_rok = datetime.now().year
            df_mies = df[(df['Data'].dt.month == obecny_miesiac) & (df['Data'].dt.year == obecny_rok)]
            
            # Tabela sumaryczna
            st.subheader(f"Podsumowanie za miesiąc: {obecny_miesiac}/{obecny_rok}")
            suma_mies = df_mies.groupby('Pracownik')['Godziny_Suma'].sum().reset_index()
            suma_mies.columns = ['Pracownik', 'Suma przepracowanych godzin']
            st.table(suma_mies)
            
            # Przycisk do pobrania danych
            csv = suma_mies.to_csv(index=False).encode('utf-8')
            st.download_button("Pobierz listę płac (CSV)", csv, "suma_godzin_miesiac.csv", "text/csv")
    else:
        st.write("Brak danych.")
