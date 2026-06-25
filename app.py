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


def get_team_stats(team_id):

    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            return None

        matches = response.json()["response"]

        points = 0
        goals_scored = 0
        goals_conceded = 0
        btts = 0
        over25 = 0

        for match in matches:

            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]

            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]

            if home_goals is None or away_goals is None:
                continue

            if team_id == home_id:

                scored = home_goals
                conceded = away_goals

                if home_goals > away_goals:
                    points += 3
                elif home_goals == away_goals:
                    points += 1

            else:

                scored = away_goals
                conceded = home_goals

                if away_goals > home_goals:
                    points += 3
                elif away_goals == home_goals:
                    points += 1

            goals_scored += scored
            goals_conceded += conceded

            if scored > 0 and conceded > 0:
                btts += 1

            if scored + conceded >= 3:
                over25 += 1

        played = max(len(matches), 1)

        return {
            "points": points,
            "avg_scored": goals_scored / played,
            "avg_conceded": goals_conceded / played,
            "btts": btts / played,
            "over25": over25 / played
        }

    except:
        return None


today = date.today().strftime("%Y-%m-%d")

fixtures_url = (
    f"https://v3.football.api-sports.io/fixtures?date={today}"
)

try:

    response = requests.get(
        fixtures_url,
        headers=headers,
        timeout=30
    )

    if response.status_code != 200:
        st.error(f"API Hatası: {response.status_code}")
        st.stop()

    data = response.json()

    matches = data.get("response", [])

    st.success(
        f"Bugün toplam {len(matches)} maç bulundu"
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

        home_score = (
            home["points"] * 3
            + home["avg_scored"] * 10
            - home["avg_conceded"] * 5
            + home["btts"] * 5
            + home["over25"] * 5
        )

        away_score = (
            away["points"] * 3
            + away["avg_scored"] * 10
            - away["avg_conceded"] * 5
            + away["btts"] * 5
            + away["over25"] * 5
        )

        home_score *= 1.10

        total = home_score + away_score

        if total == 0:
            home_win = 45
            draw = 25
            away_win = 30
        else:

            home_win = round(
                (home_score / total) * 80
            )

            away_win = round(
                (away_score / total) * 80
            )

            draw = 100 - home_win - away_win

            if draw < 8:

                draw = 8

                scale = 92 / (
                    home_win + away_win
                )

                home_win = round(
                    home_win * scale
                )

                away_win = round(
                    away_win * scale
                )

        confidence = abs(
            home["points"] - away["points"]
        )

        st.subheader(
            f"{home_team} 🆚 {away_team}"
        )

        st.write(f"🏆 Lig: {league}")
        st.write(f"🌍 Ülke: {country}")

        st.write("📈 Son 10 Maç Analizi")

        st.write(
            f"🏠 Ev Sahibi Form Puanı: "
            f"{home['points']}/30"
        )

        st.write(
            f"🚗 Deplasman Form Puanı: "
            f"{away['points']}/30"
        )

        st.write(
            f"⚽ Gol Ortalaması: "
            f"{home['avg_scored']:.2f} - "
            f"{away['avg_scored']:.2f}"
        )

        st.write(
            f"🛡️ Yenilen Gol Ort.: "
            f"{home['avg_conceded']:.2f} - "
            f"{away['avg_conceded']:.2f}"
        )

        st.write(
            f"🎯 BTTS: "
            f"%{round(home['btts']*100)} - "
            f"%{round(away['btts']*100)}"
        )

        st.write(
            f"🔥 Over 2.5: "
            f"%{round(home['over25']*100)} - "
            f"%{round(away['over25']*100)}"
        )

        st.progress(home_win)

        st.write(
            f"🏠 Ev Sahibi Kazanır: %{home_win}"
        )

        st.write(
            f"🤝 Beraberlik: %{draw}"
        )

        st.write(
            f"🚗 Deplasman Kazanır: %{away_win}"
        )

        if confidence >= 10:
            st.success(
                f"🔥 Güven Skoru: {confidence}/30"
            )

        elif confidence >= 5:
            st.warning(
                f"⚠️ Güven Skoru: {confidence}/30"
            )

        else:
            st.info(
                f"❓ Güven Skoru: {confidence}/30"
            )

        st.divider()

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
