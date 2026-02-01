import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- LISTA PRACOWNIKÓW (Ułożona alfabetycznie) ---
PRACOWNICY = [
    "Azamat",
    "Bartek",
    "Ivan",
    "Kamil",
    "Krzysiek",
    "Łukasz",
    "Łukasz Ndg",
    "Maciek",
    "Marcel",
    "Marcin Brygadzista",
    "Marcin Nowy",
    "Marcin Sz.",
    "Marek",
    "Marek Gru",
    "Marek K.",
    "Misza",
    "Piotr S.",
    "Sasza"
]

# Konfiguracja folderów
FOLDER_ZDJEC = "zdjecia_pracownikow"
PLIK_LOGU = "rejestr_czasu.csv"

if not os.path.exists(FOLDER_ZDJEC):
    os.makedirs(FOLDER_ZDJEC)

st.set_page_config(page_title="Budowa - Logowanie", page_icon="🏗️")

st.title("🏗️ System Rejestracji Czasu")
st.write("Wybierz nazwisko, zrób zdjęcie i zatwierdź.")

# Wybór pracownika
osoba = st.selectbox("Kim jesteś?", ["-- Wybierz z listy --"] + PRACOWNICY)

if osoba != "-- Wybierz z listy --":
    try:
        # Wybór akcji
        typ = st.radio("Co rejestrujesz?", ["Wejście do pracy (START)", "Wyjście z pracy (KONIEC)"])
        
        # Aparat
        foto = st.camera_input("Zrób zdjęcie (Selfie)")

        if foto:
            if st.button("Zatwierdzam godzinę i zdjęcie"):
                teraz = datetime.now()
                czas_str = teraz.strftime("%Y-%m-%d %H:%M:%S")
                # Tworzenie bezpiecznej nazwy pliku
                bezpieczne_nazwisko = osoba.replace(" ", "_").replace(".", "")
                plik_foto = f"{teraz.strftime('%Y%m%d_%H%M%S')}_{bezpieczne_nazwisko}.jpg"
                
                # Zapis zdjęcia lokalnie
                with open(os.path.join(FOLDER_ZDJEC, plik_foto), "wb") as f:
                    f.write(foto.getbuffer())
                
                # Zapis danych do tabeli CSV
                dane = pd.DataFrame([[osoba, czas_str, typ, plik_foto]], 
                                    columns=["Pracownik", "Data/Godzina", "Typ", "Plik"])
                
                if not os.path.exists(PLIK_LOGU):
                    dane.to_csv(PLIK_LOGU, index=False)
                else:
                    dane.to_csv(PLIK_LOGU, mode='a', header=False, index=False)
                
                st.success(f"Dziękuję {osoba}! Zarejestrowano o {teraz.strftime('%H:%M')}.")
                st.balloons()
    except Exception as e:
        st.error(f"Wystąpił błąd. Spróbuj odświeżyć stronę.")

# Sekcja dla Szefa
with st.expander("Panel podglądu (dla szefa)"):
    if os.path.exists(PLIK_LOGU):
        df = pd.read_csv(PLIK_LOGU)
        st.write("Ostatnie 10 wpisów:")
        st.table(df.tail(10))
    else:
        st.write("Brak wpisów w rejestrze.")
