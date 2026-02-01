import streamlit as st
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.message import EmailMessage

# --- KONFIGURACJA KONTA ---
MOJ_EMAIL = "Mokoinvestgd@gmail.com"
# TUTAJ WKLEJ 16-ZNAKOWY KOD Z GOOGLE (ten z żółtego okienka)
HASLO_GMAIL = "yrzg qqhj ikey jzqc" 

# --- KONFIGURACJA APLIKACJI ---
PRACOWNICY = [
    "Alan", "Azamat", "Bartek", "Ivan", "Kamil", "Krzysiek", "Łukasz", 
    "Łukasz Ndg", "Maciek", "Marcel", "Marcin Brygadzista", 
    "Marcin Nowy", "Marcin Sz.", "Marek", "Marek Gru", 
    "Marek K.", "Misza", "Piotr S.", "Sasza"
]

HASLO_PANELU = "Moko123$"
PLIK_LOGU = "rejestr_czasu.csv"
KOLUMNY = ["Pracownik", "Data", "Wejście (START)", "Wyjście (KONIEC)", "Suma Godzin"]

def wyslij_raport_email(osoba, typ, godzina, foto_data):
    msg = EmailMessage()
    msg['Subject'] = f"Raport Pracy: {osoba} ({typ})"
    msg['From'] = MOJ_EMAIL
    msg['To'] = MOJ_EMAIL
    
    tresc = f"""
    Zarejestrowano nową aktywność w systemie MOKO:
    Pracownik: {osoba}
    Akcja: {typ}
    Godzina (czas telefonu): {godzina}
    Data: {datetime.now().strftime('%Y-%m-%d')}
    """
    msg.set_content(tresc)
    msg.add_attachment(foto_data, maintype='image', subtype='jpeg', filename=f"{osoba}_{typ}.jpg")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MOJ_EMAIL, HASLO_GMAIL)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Błąd wysyłki maila: {e}")
        return False

# --- UI APLIKACJI ---
st.set_page_config(page_title="MOKO Budowa", page_icon="🏗️")
st.title("🏗️ Rejestr Czasu MOKO")

osoba = st.selectbox("Wybierz pracownika:", ["-- Wybierz z listy --"] + PRACOWNICY)

if osoba != "-- Wybierz z listy --":
    teraz = datetime.now()
    godzina_teraz = teraz.strftime("%H:%M:%S")
    data_dzis = teraz.strftime("%Y-%m-%d")
    
    st.info(f"Godzina z Twojego telefonu: **{godzina_teraz}**")
    typ = st.radio("Akcja:", ["START (Początek pracy)", "KONIEC (Koniec pracy)"])
    foto = st.camera_input("Zrób zdjęcie (Selfie)")

    if foto:
        if st.button("ZATWIERDŹ I WYŚLIJ DO SZEFA"):
            # 1. Wysyłka maila ze zdjęciem
            if wyslij_raport_email(osoba, typ, godzina_teraz, foto.getvalue()):
                st.success("Zdjęcie i godzina zostały wysłane na maila Mokoinvestgd@gmail.com!")
            
            # 2. Zapis pomocniczy do tabeli
            df = pd.read_csv(PLIK_LOGU) if os.path.exists(PLIK_LOGU) else pd.DataFrame(columns=KOLUMNY)
            nowy = pd.DataFrame([[osoba, data_dzis, godzina_teraz if "START" in typ else "-", godzina_teraz if "KONIEC" in typ else "-", 0.0]], columns=KOLUMNY)
            df = pd.concat([df, nowy], ignore_index=True)
            df.to_csv(PLIK_LOGU, index=False)
            
            st.balloons()

# --- PANEL SZEFA (NA HASŁO) ---
st.markdown("---")
if st.checkbox("📊 PANEL ROZLICZEŃ (Dla Alana)"):
    kod = st.text_input("Podaj hasło Moko:", type="password")
    if kod == HASLO_PANELU:
        st.success("Witaj Alan! Oto historia wejść:")
        if os.path.exists(PLIK_LOGU):
            st.dataframe(pd.read_csv(PLIK_LOGU))
        else:
            st.write("Baza danych jest obecnie pusta.")
