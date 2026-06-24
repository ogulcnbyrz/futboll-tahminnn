import streamlit as st
import requests
import os
from datetime import date

st.title("TEST")

API_KEY = os.getenv("API_FOOTBALL_KEY")

st.write("API_KEY =", API_KEY)

headers = {
    "x-apisports-key": API_KEY
}

today = date.today().strftime("%Y-%m-%d")

url = f"https://v3.football.api-sports.io/fixtures?date={today}"

response = requests.get(url, headers=headers)

st.write("Status Code:", response.status_code)

try:
    st.json(response.json())
except:
    st.write(response.text)
