import streamlit as st
import requests
import os
from datetime import date

st.set_page_config(
    page_title="Futbol Tahmin Sistemi",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ Futbol Tahmin Sistemi")

API_KEY = os.getenv("API_FOOTBALL_KEY")

if not API_KEY:
    st.error("API_FOOTBALL_KEY bulunamadı!")
    st.stop()

headers = {
    "x-apisports-key": API_KEY
}


# Takımın son 5 maç form puanını hesapla
def get_team_form(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            return 0

        data = response.json()
        matches = data.get("response", [])

        points = 0

        for match in matches:
            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]

            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]

            if home_goals is None or away_goals is None:
                continue

            # Takım ev sahibi ise
            if team_id == home_id:
                if home_goals > away_goals:
                    points += 3
                elif home_goals == away_goals:
                    points += 1

            # Takım deplasman ise
            elif team_id == away_id:
                if away_goals > home_goals:
                    points += 3
                elif away_goals == home_goals:
                    points += 1

        return points

    except Exception:
        return 0


# Dinamik tahmin yüzdesi hesapla
def calculate_prediction(home_form, away_form):

    total = home_form + away_form

    if total == 0:
        return 45, 25, 30

    home_win = round((home_form / total) * 70)
    away_win = round((away_form / total) * 70)

    draw = 100 - home_win - away_win

    if draw < 10:
        draw = 10

        scale = 90 / (home_win + away_win)

        home_win = round(home_win * scale)
        away_win = round(away_win * scale)

    return home_win, draw, away_win


# Günün maçlarını çek
today = date.today().strftime("%Y-%m-%d")

url = f"https://v3.football.api-sports.io/fixtures?date={today}"

try:
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        st.error(f"API Hatası: {response.status_code}")
        st.stop()

    data = response.json()
    matches = data.get("response", [])

    st.success(f"Bugün toplam {len(matches)} maç bulundu")

    for match in matches[:20]:

        home_team = match["teams"]["home"]["name"]
        away_team = match["teams"]["away"]["name"]

        home_id = match["teams"]["home"]["id"]
        away_id = match["teams"]["away"]["id"]

        league = match["league"]["name"]
        country = match["league"]["country"]

        home_form = get_team_form(home_id)
        away_form = get_team_form(away_id)

        home_win, draw, away_win = calculate_prediction(
            home_form,
            away_form
        )

        confidence = abs(home_form - away_form)

        st.subheader(f"{home_team} 🆚 {away_team}")

        st.write(f"🏆 Lig: {league}")
        st.write(f"🌍 Ülke: {country}")

        st.write("📈 Son 5 Maç Form Analizi")

        st.write(f"🏠 Ev Sahibi Form Puanı: {home_form}/15")
        st.write(f"🚗 Deplasman Form Puanı: {away_form}/15")

        st.progress(home_win)

        st.write(f"🏠 Ev Sahibi Kazanır: %{home_win}")
        st.write(f"🤝 Beraberlik: %{draw}")
        st.write(f"🚗 Deplasman Kazanır: %{away_win}")

        if confidence >= 8:
            st.success(f"🔥 Güven Skoru: {confidence}/15")

        elif confidence >= 4:
            st.warning(f"⚠️ Güven Skoru: {confidence}/15")

        else:
            st.info(f"❓ Güven Skoru: {confidence}/15")

        st.divider()

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
