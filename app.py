import streamlit as st
import requests
import os
from datetime import date

st.set_page_config(page_title="Futbol Tahmin Sistemi")

st.title("⚽ Futbol Tahmin Sistemi")

API_KEY = os.getenv("API_FOOTBALL_KEY")

headers = {
    "x-apisports-key": API_KEY
}

today = date.today().strftime("%Y-%m-%d")

url = f"https://v3.football.api-sports.io/fixtures?date={today}"

response = requests.get(url, headers=headers)

if response.status_code == 200:

    data = response.json()
    matches = data["response"]

    st.success(f"Bugün toplam {len(matches)} maç bulundu")

    for match in matches[:20]:

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        league = match["league"]["name"]
        country = match["league"]["country"]

        st.subheader(f"{home} 🆚 {away}")

        st.write(f"🏆 Lig: {league}")
        st.write(f"🌍 Ülke: {country}")

        # Geçici örnek tahmin yüzdeleri
        home_win = 45
        draw = 25
        away_win = 30

        st.progress(home_win)
        st.write(f"🏠 Ev Sahibi Kazanır: %{home_win}")
        st.write(f"🤝 Beraberlik: %{draw}")
        st.write(f"🚗 Deplasman Kazanır: %{away_win}")

        st.divider()

else:
    st.error(f"API Hatası: {response.status_code}")
