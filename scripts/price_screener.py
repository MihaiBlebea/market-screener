from __future__ import annotations
from typing import List
import streamlit as st
import pandas as pd
import numpy as np
from lib.utils import get_query_param
from yahoo_fin_api import YahooFinApi, Client, FileCache, Universe, Ticker

@st.experimental_memo
def load_data()-> List[Ticker]:
	yf = YahooFinApi(Client(FileCache("./data")))
	symbols = Universe.get_ftse_100_universe()
	if symbols is None:
		raise Exception("symbols not found")
	return yf.get_all(symbols)

def to_dataframe(tickers: List[Ticker])-> pd.DataFrame:
	table = {
		"Symbol": [],
		"Title": [],
		"Price": []
	}

	counter = 0
	for t in tickers:
		if t.financial_data is None:
			continue

		table["Symbol"].append(t.symbol)
		table["Title"].append(t.title)
		table["Price"].append(t.financial_data.current_price)

		counter += 1

	return pd.DataFrame(data=table, index=np.arange(1, counter+1))


###########
# Sidebar #
###########
max_limit = st.sidebar.number_input(
	"Price max limit", 
	min_value=10, 
	value=int(get_query_param("max_limit", 1000))
)
min_limit = st.sidebar.number_input(
	"Price min limit", 
	min_value=0, 
	value=int(get_query_param("min_limit", 10))
)
sort_reverse = st.sidebar.checkbox(
	"Sort reversed", 
	value=True if get_query_param("reverse", "true") == "true" else False,
)


########
# Main #
########
data = load_data()
data = [
	t for t in data 
	if t.financial_data is not None 
	and t.financial_data.current_price < max_limit
	and t.financial_data.current_price > min_limit
]

data = sorted(data, key=lambda t: t.financial_data.current_price, reverse=sort_reverse)

st.title("Market Price Screener")
st.text(f"We found {len(data)} stocks matching the rules")
st.table(to_dataframe(data))