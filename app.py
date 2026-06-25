import streamlit as st
import requests
import os
from datetime import date

st.set_page_config(page_title="Futbol Tahmin Sistemi", layout="wide")

API_KEY = os.getenv("API_FOOTBALL_KEY")

headers = {
    "x-apisports-key": API_KEY
}

st.title("⚽ Futbol Tahmin Sistemi")

selected_date = st.date_input(
    "Maç Tarihi",
    value=date.today()
)

# Son 5 maç formu
def get_team_form(team_id):

    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"

    try:
        r = requests.get(url, headers=headers, timeout=20)

        if r.status_code != 200:
            return 0

        matches = r.json()["response"]

        points = 0

        for m in matches:

            home_id = m["teams"]["home"]["id"]
            away_id = m["teams"]["away"]["id"]

            hg = m["goals"]["home"]
            ag = m["goals"]["away"]

            if hg is None or ag is None:
                continue

            if team_id == home_id:

                if hg > ag:
                    points += 3
                elif hg == ag:
                    points += 1

            else:

                if ag > hg:
                    points += 3
                elif ag == hg:
                    points += 1

        return points

    except:
        return 0


fixture_url = (
    f"https://v3.football.api-sports.io/fixtures?date={selected_date}"
)

response = requests.get(
    fixture_url,
    headers=headers,
    timeout=30
)
st.write("Seçilen tarih:", selected_date)

st.write("Status Code:", response.status_code)

try:
    st.json(response.json())
except:
    st.write(response.text)
if response.status_code != 200:

    st.error(f"API Hatası: {response.status_code}")
    st.stop()

matches = response.json()["response"]

st.success(
    f"{selected_date} tarihinde toplam {len(matches)} maç bulundu"
)

if len(matches) == 0:
    st.warning("Bu tarih için maç bulunamadı.")
    st.stop()

for match in matches[:30]:

    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]

    home_id = match["teams"]["home"]["id"]
    away_id = match["teams"]["away"]["id"]

    league = match["league"]["name"]
    country = match["league"]["country"]

    home_form = get_team_form(home_id)
    away_form = get_team_form(away_id)

    total = home_form + away_form

    if total == 0:

        home_pct = 40
        draw_pct = 30
        away_pct = 30

    else:

        home_pct = round(home_form / total * 70)
        away_pct = round(away_form / total * 70)

        draw_pct = 100 - home_pct - away_pct

        if draw_pct < 10:

            draw_pct = 10

            scale = 90 / (home_pct + away_pct)

            home_pct = round(home_pct * scale)
            away_pct = round(away_pct * scale)

    confidence = abs(home_form - away_form)

    st.subheader(f"{home} 🆚 {away}")

    st.write(f"🏆 Lig: {league}")
    st.write(f"🌍 Ülke: {country}")

    st.write("### Son 5 Maç Formu")

    st.write(f"🏠 {home}: {home_form} puan")
    st.write(f"🚗 {away}: {away_form} puan")

    st.progress(home_pct)

    col1, col2, col3 = st.columns(3)

    col1.metric("Ev Sahibi", f"%{home_pct}")
    col2.metric("Beraberlik", f"%{draw_pct}")
    col3.metric("Deplasman", f"%{away_pct}")

    if confidence >= 8:
        st.success(f"🔥 Güven Skoru: {confidence}/15")

    elif confidence >= 4:
        st.warning(f"⚠️ Güven Skoru: {confidence}/15")

    else:
        st.info(f"❓ Güven Skoru: {confidence}/15")

    st.divider()
