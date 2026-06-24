import streamlit as st
import requests
import os
from datetime import date

st.set_page_config(page_title="Futbol Tahmin Sistemi")

st.title("⚽ Futbol Tahmin Sistemi")

API_KEY = os.getenv("API_FOOTBALL_KEY")
st.write("API KEY:", API_KEY)
headers = {
    "x-apisports-key": API_KEY
}

today = date.today().strftime("%Y-%m-%d")

url = f"https://v3.football.api-sports.io/fixtures?date={today}"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()

    matches = data["response"]

    if len(matches) == 0:
        st.warning("Bugün maç bulunamadı.")
    else:
        for match in matches[:20]:
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]

            st.subheader(f"{home} vs {away}")

else:
    st.error("API bağlantı hatası.")
