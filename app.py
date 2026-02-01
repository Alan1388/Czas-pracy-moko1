import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- LISTA PRACOWNIKÓW ---
PRACOWNICY = [
    "Alan", "Azamat", "Bartek", "Ivan", "Kamil", "Krzysiek", "Łukasz", 
    "Łukasz Ndg", "Maciek", "Marcel", "Marcin Brygadzista", 
    "Marcin Nowy", "Marcin Sz.", "Marek", "Marek Gru", 
    "Marek K.", "Misza", "Piotr S.", "Sasza"
]

FOLDER_ZDJEC = "zdjecia_pracownikow"
PLIK_LOGU = "rejestr_czasu.csv"
KOLUMNY = ["Pracownik", "Data", "Wejście (START)", "Wyjście (KONIEC)", "Suma Godzin", "Plik Foto"]

if not os.path.exists(FOLDER_ZDJEC):
    os.makedirs(FOLDER_ZDJEC)

def wczytaj_dane():
    if os.path.exists(PLIK_LOGU) and os.path.getsize(PLIK_LOGU) > 0:
        try:
            return pd.read_csv(PLIK_LOGU)
        except:
            return pd.DataFrame(columns=KOLUMNY)
    return pd.DataFrame(columns=KOLUMNY)

st.set_page_config(page_title="Budowa MOKO", page_icon="🏗️")
st.title("🏗️ Automatyczny Rejestr Czasu")

osoba = st.selectbox("Wybierz pracownika:", ["-- Wybierz z listy --"] + PRACOWNICY)

if osoba != "-- Wybierz z listy --":
    # System sam pobiera aktualną godzinę z urządzenia
    teraz = datetime.now()
    godzina_teraz = teraz.strftime("%H:%M:%S")
    data_dzis = teraz.strftime("%Y-%m-%d")
    
    st.write(f"Aktualna godzina: **{godzina_teraz}**")
    
    typ = st.radio("Akcja:", ["START (Początek pracy)", "KONIEC (Koniec pracy)"])
    foto = st.camera_input("Zrób zdjęcie (potwierdzenie)")

    if foto:
        if st.button("ZATWIERDŹ I WYŚLIJ"):
            bezp_nazwa = osoba.replace(" ", "_")
            plik_foto = f"{teraz.strftime('%Y%m%d_%H%M%S')}_{bezp_nazwa}.jpg"
            
            with open(os.path.join(FOLDER_ZDJEC, plik_foto), "wb") as f:
                f.write(foto.getbuffer())

            df = wczytaj_dane()
            h_suma = 0.0
            
            if typ == "START (Początek pracy)":
                nowy_wpis = pd.DataFrame([[osoba, data_dzis, godzina_teraz, "-", 0.0, plik_foto]], columns=KOLUMNY)
            else:
                # Szukamy wejścia z dzisiaj, żeby policzyć czas
                mask = (df['Pracownik'] == osoba) & (df['Data'] == data_dzis) & (df['Wejście (START)'] != "-")
                indexy = df[mask].index
                
                if not indexy.empty:
                    idx = indexy[-1]
                    start_str = df.at[idx, 'Wejście (START)']
                    start_dt = datetime.strptime(start_str, "%H:%M:%S")
                    roznica = teraz - datetime.combine(teraz.date(), start_dt.time())
                    h_suma = round(roznica.total_seconds() / 3600, 2)
                    
                    df.at[idx, 'Wyjście (KONIEC)'] = godzina_teraz
                    df.at[idx, 'Suma Godzin'] = h_suma
                    nowy_wpis = None
                else:
                    nowy_wpis = pd.DataFrame([[osoba, data_dzis, "-", godzina_teraz, 0.0, plik_foto]], columns=KOLUMNY)

            if nowy_wpis is not None:
                df = pd.concat([df, nowy_wpis], ignore_index=True)
            
            df.to_csv(PLIK_LOGU, index=False)
            st.success(f"Zarejestrowano pomyślnie o {godzina_teraz}!")
            st.balloons()

# --- PANEL ROZLICZEŃ ---
st.markdown("---")
if st.checkbox("📊 PANEL ROZLICZEŃ (Dla Szefa)"):
    df = wczytaj_dane()
    if not df.empty:
        df['Data'] = pd.to_datetime(df['Data'])
        m, r = datetime.now().month, datetime.now().year
        
        # Filtrowanie bieżącego miesiąca
        df_m = df[(df['Data'].dt.month == m) & (df['Data'].dt.year == r)]
        
        st.subheader(f"Podsumowanie miesiąca {m}/{r}")
        suma_mies = df_m.groupby('Pracownik')['Suma Godzin'].sum().reset_index()
        st.table(suma_mies)
        
        st.subheader("Szczegółowa historia")
        st.dataframe(df.sort_values(by="Data", ascending=False))
    else:
        st.info("Brak wpisów w bazie.")
