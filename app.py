import streamlit as st
import requests
import os
from datetime import date

st.set_page_config(
    page_title="Futbol Tahmin Sistemi",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Futbol Tahmin Sistemi")

API_KEY = os.getenv("API_FOOTBALL_KEY")

if not API_KEY:
    st.error("API_FOOTBALL_KEY Railway Variables içinde tanımlı değil.")
    st.stop()

headers = {
    "x-apisports-key": API_KEY
}


# Son 5 maç form puanı
@st.cache_data(ttl=3600)
def get_team_form(team_id):

    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            return 0

        data = response.json()

        if "response" not in data:
            return 0

        matches = data["response"]

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


selected_date = st.date_input(
    "Maç Tarihi",
    value=date.today()
)

fixture_url = (
    f"https://v3.football.api-sports.io/fixtures?date={selected_date}"
)

try:

    response = requests.get(
        fixture_url,
        headers=headers,
        timeout=30
    )

except Exception as e:

    st.error(f"Bağlantı hatası: {e}")
    st.stop()

if response.status_code != 200:

    st.error(f"API Hatası: {response.status_code}")
    st.stop()

data = response.json()

# API hesabı askıya alınmış mı?
if data.get("errors"):

    errors = data["errors"]

    if len(errors) > 0:

        st.error(f"API Hatası: {errors}")
        st.stop()

matches = data.get("response", [])

st.success(
    f"{selected_date} tarihinde toplam {len(matches)} maç bulundu"
)

if len(matches) == 0:

    st.warning("Bu tarih için maç bulunamadı.")
    st.stop()

for match in matches[:30]:

    try:

        home_team = match["teams"]["home"]["name"]
        away_team = match["teams"]["away"]["name"]

        home_id = match["teams"]["home"]["id"]
        away_id = match["teams"]["away"]["id"]

        league = match["league"]["name"]
        country = match["league"]["country"]

        home_form = get_team_form(home_id)
        away_form = get_team_form(away_id)

        total_form = home_form + away_form

        if total_form == 0:

            home_win = 40
            draw = 30
            away_win = 30

        else:

            home_win = round(
                (home_form / total_form) * 70
            )

            away_win = round(
                (away_form / total_form) * 70
            )

            draw = 100 - home_win - away_win

            if draw < 10:

                draw = 10

                factor = 90 / (home_win + away_win)

                home_win = round(home_win * factor)
                away_win = round(away_win * factor)

        confidence = abs(home_form - away_form)

        st.subheader(
            f"{home_team} 🆚 {away_team}"
        )

        st.write(f"🏆 Lig: {league}")
        st.write(f"🌍 Ülke: {country}")

        st.write("### 📈 Son 5 Maç Formu")

        st.write(
            f"🏠 Ev Sahibi Form Puanı: {home_form}/15"
        )

        st.write(
            f"🚗 Deplasman Form Puanı: {away_form}/15"
        )

        st.progress(home_win)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Ev Sahibi",
            f"%{home_win}"
        )

        col2.metric(
            "Beraberlik",
            f"%{draw}"
        )

        col3.metric(
            "Deplasman",
            f"%{away_win}"
        )

        if confidence >= 8:

            st.success(
                f"🔥 Güven Skoru: {confidence}/15"
            )

        elif confidence >= 4:

            st.warning(
                f"⚠️ Güven Skoru: {confidence}/15"
            )

        else:

            st.info(
                f"❓ Güven Skoru: {confidence}/15"
            )

        st.divider()

    except Exception as e:

        st.error(f"Maç işlenirken hata oluştu: {e}")
