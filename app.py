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

# Takımın son maç formunu hesapla
def get_team_form(team_id):

    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            return 0

        matches = response.json()["response"]

        points = 0

        for match in matches:

            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]

            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]

            if home_goals is None or away_goals is None:
                continue

            if team_id == home_id:

                if home_goals > away_goals:
                    points += 3
                elif home_goals == away_goals:
                    points += 1

            else:

                if away_goals > home_goals:
                    points += 3
                elif away_goals == home_goals:
                    points += 1

        return points

    except:
        return 0


today = date.today().strftime("%Y-%m-%d")

url = f"https://v3.football.api-sports.io/fixtures?date={today}"

response = requests.get(url, headers=headers)

if response.status_code == 200:

    data = response.json()
    matches = data["response"]

    st.success(f"Bugün toplam {len(matches)} maç bulundu")

    for match in matches[:20]:

        home_team = match["teams"]["home"]["name"]
        away_team = match["teams"]["away"]["name"]

        home_id = match["teams"]["home"]["id"]
        away_id = match["teams"]["away"]["id"]

        league = match["league"]["name"]
        country = match["league"]["country"]

        # Son 5 maç form puanları
        home_form = get_team_form(home_id)
        away_form = get_team_form(away_id)

        total = home_form + away_form

        if total == 0:
            home_win = 45
            draw = 25
            away_win = 30
        else:

            home_win = round((home_form / total) * 70)
            away_win = round((away_form / total) * 70)

            draw = 100 - home_win - away_win

            if draw < 10:
                draw = 10

                remaining = 90
                factor = remaining / (home_win + away_win)

                home_win = round(home_win * factor)
                away_win = round(away_win * factor)

        st.subheader(f"{home_team} 🆚 {away_team}")

        st.write(f"🏆 Lig: {league}")
        st.write(f"🌍 Ülke: {country}")

        st.write(f"📈 Son 5 Maç Formu")
        st.write(f"🏠 Ev Sahibi Puanı: {home_form}")
        st.write(f"🚗 Deplasman Puanı: {away_form}")

        st.progress(home_win)

        st.write(f"🏠 Ev Sahibi Kazanır: %{home_win}")
        st.write(f"🤝 Beraberlik: %{draw}")
        st.write(f"🚗 Deplasman Kazanır: %{away_win}")

        # Basit güven puanı
        confidence = abs(home_form - away_form)

        if confidence >= 8:
            st.success(f"🔥 Güven Skoru: {confidence}/15")
        elif confidence >= 4:
            st.warning(f"⚠️ Güven Skoru: {confidence}/15")
        else:
            st.info(f"❓ Güven Skoru: {confidence}/15")

        st.divider()

else:
    st.error(f"API Hatası: {response.status_code}")
