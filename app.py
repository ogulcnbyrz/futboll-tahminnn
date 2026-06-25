import streamlit as st
import requests
import os
from datetime import date

st.set_page_config(
    page_title="Futbol Tahmin Sistemi",
    page_icon="⚽",
    layout="wide"
)

API_KEY = os.getenv("API_FOOTBALL_KEY")

if not API_KEY:
    st.error("API_FOOTBALL_KEY bulunamadı!")
    st.stop()

headers = {
    "x-apisports-key": API_KEY
}

st.title("⚽ Futbol Tahmin Sistemi")

selected_date = st.date_input(
    "Maç Tarihi",
    value=date.today()
)

today = selected_date.strftime("%Y-%m-%d")


@st.cache_data(ttl=3600)
def get_team_stats(team_id):

    try:

        url = (
            f"https://v3.football.api-sports.io/"
            f"fixtures?team={team_id}&last=10"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            return None

        matches = response.json().get("response", [])

        if len(matches) == 0:
            return None

        points = 0
        goals_scored = 0
        goals_conceded = 0
        btts = 0
        over25 = 0

        for match in matches:

            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]

            hg = match["goals"]["home"]
            ag = match["goals"]["away"]

            if hg is None or ag is None:
                continue

            if team_id == home_id:

                scored = hg
                conceded = ag

                if hg > ag:
                    points += 3
                elif hg == ag:
                    points += 1

            else:

                scored = ag
                conceded = hg

                if ag > hg:
                    points += 3
                elif ag == hg:
                    points += 1

            goals_scored += scored
            goals_conceded += conceded

            if scored > 0 and conceded > 0:
                btts += 1

            if scored + conceded >= 3:
                over25 += 1

        played = len(matches)

        return {
            "points": points,
            "avg_scored": goals_scored / played,
            "avg_conceded": goals_conceded / played,
            "btts": (btts / played) * 100,
            "over25": (over25 / played) * 100
        }

    except:
        return None


def calculate_prediction(home, away):

    home_score = (
        home["points"] * 3
        + home["avg_scored"] * 10
        - home["avg_conceded"] * 5
        + home["btts"] * 0.2
        + home["over25"] * 0.2
    )

    away_score = (
        away["points"] * 3
        + away["avg_scored"] * 10
        - away["avg_conceded"] * 5
        + away["btts"] * 0.2
        + away["over25"] * 0.2
    )

    home_score *= 1.10

    total = home_score + away_score

    if total <= 0:
        return 45, 25, 30

    home_win = round((home_score / total) * 80)
    away_win = round((away_score / total) * 80)

    draw = 100 - home_win - away_win

    if draw < 10:

        draw = 10

        scale = 90 / (home_win + away_win)

        home_win = round(home_win * scale)
        away_win = round(away_win * scale)

    return home_win, draw, away_win


try:

    fixtures_url = (
        f"https://v3.football.api-sports.io/"
        f"fixtures?date={today}"
    )

    response = requests.get(
        fixtures_url,
        headers=headers,
        timeout=30
    )

    if response.status_code != 200:
        st.error(
            f"API Hatası: {response.status_code}"
        )
        st.stop()

    data = response.json()

    matches = data.get("response", [])

    st.success(
        f"{today} tarihinde toplam "
        f"{len(matches)} maç bulundu"
    )

    if len(matches) == 0:
        st.warning(
            "Bu tarih için maç bulunamadı."
        )

    for match in matches[:20]:

        home_team = match["teams"]["home"]["name"]
        away_team = match["teams"]["away"]["name"]

        home_id = match["teams"]["home"]["id"]
        away_id = match["teams"]["away"]["id"]

        league = match["league"]["name"]
        country = match["league"]["country"]

        home = get_team_stats(home_id)
        away = get_team_stats(away_id)

        if not home or not away:
            continue

        home_win, draw, away_win = (
            calculate_prediction(
                home,
                away
            )
        )

        confidence = abs(
            home["points"]
            - away["points"]
        )

        st.markdown("---")

        st.subheader(
            f"{home_team} 🆚 {away_team}"
        )

        st.write(f"🏆 Lig: {league}")
        st.write(f"🌍 Ülke: {country}")

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"📈 Form Puanı: "
                f"{home['points']}/30"
            )

            st.write(
                f"⚽ Gol Ort: "
                f"{home['avg_scored']:.2f}"
            )

            st.write(
                f"🛡️ Yenilen: "
                f"{home['avg_conceded']:.2f}"
            )

        with col2:

            st.write(
                f"📈 Form Puanı: "
                f"{away['points']}/30"
            )

            st.write(
                f"⚽ Gol Ort: "
                f"{away['avg_scored']:.2f}"
            )

            st.write(
                f"🛡️ Yenilen: "
                f"{away['avg_conceded']:.2f}"
            )

        st.write(
            f"🎯 BTTS: "
            f"%{round(home['btts'])} - "
            f"%{round(away['btts'])}"
        )

        st.write(
            f"🔥 Over 2.5: "
            f"%{round(home['over25'])} - "
            f"%{round(away['over25'])}"
        )

        st.progress(home_win)

        st.success(
            f"🏠 Ev Sahibi: %{home_win}"
        )

        st.info(
            f"🤝 Beraberlik: %{draw}"
        )

        st.error(
            f"🚗 Deplasman: %{away_win}"
        )

        if confidence >= 10:
            st.success(
                f"🔥 Güven Skoru: "
                f"{confidence}/30"
            )

        elif confidence >= 5:
            st.warning(
                f"⚠️ Güven Skoru: "
                f"{confidence}/30"
            )

        else:
            st.info(
                f"❓ Güven Skoru: "
                f"{confidence}/30"
            )

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
