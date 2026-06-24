import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(page_title="Futbol Tahmin", page_icon="⚽")

st.title("⚽ Futbol Tahmin Sistemi")

API_KEY = os.getenv("api_key")  # Railway'de oluşturduğun değişken

if not API_KEY:
    st.error("API anahtarı bulunamadı.")
    st.stop()

headers = {
    "x-apisports-key": API_KEY
}

today = datetime.now().strftime("%Y-%m-%d")

try:
    response = requests.get(
        "https://v3.football.api-sports.io/fixtures",
        headers=headers,
        params={"date": today},
        timeout=20
    )

    data = response.json()

    matches = data.get("response", [])

    st.write(f"Bugünkü maç sayısı: {len(matches)}")

    if not matches:
        st.warning("Bugün maç bulunamadı.")
    else:
        for match in matches[:20]:
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]

            st.subheader(f"{home} vs {away}")
            st.write("📊 Tahmin sistemi sonraki adımda eklenecek")

except Exception as e:
    st.error(f"Hata: {e}")
