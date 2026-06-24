import streamlit as st
import requests
import os

API_KEY = os.getenv("api_key")

st.title("⚽ Futbol Tahmin Sistemi")
st.write("YENİ KOD ÇALIŞIYOR")
headers = {
    "x-apisports-key": API_KEY
}

url = "https://v3.football.api-sports.io/fixtures?next=10"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()

    for match in data["response"]:
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        st.subheader(f"{home} - {away}")

        st.write("1: %45")
        st.write("X: %30")
        st.write("2: %25")
        st.divider()

else:
    st.error("API bağlantı hatası")
