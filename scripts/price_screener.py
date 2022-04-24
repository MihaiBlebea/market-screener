from __future__ import annotations
from typing import List
import streamlit as st
import pandas as pd
import numpy as np
from yahoo_fin_api import YahooFinApi, Client, Ticker
from yahoo_fin_api.universe import symbols as get_universe

@st.cache
def load_data():
	yf = YahooFinApi(
		Client(
			cache_response=True,
			download_folder_path="./data"
		)
	)
	universe = [ s.symbol for s in get_universe("./freetrade_universe.csv") ]
	return yf.get_all(universe)

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

def get_query_param(param: str, default):
	params = st.experimental_get_query_params()
	if param not in params:
		return default
	
	return params[param][0]

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

st.title("This is a demo app")
st.text(f"We found {len(data)} stocks matching the rules")
st.table(to_dataframe(data))