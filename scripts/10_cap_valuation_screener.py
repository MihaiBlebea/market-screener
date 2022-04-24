from __future__ import annotations
from typing import List
import requests
import streamlit as st
from yahoo_fin_api import YahooFinApi, Client, FileCache, Universe, Ticker

BILLION = 1000000000

@st.cache
def load_data(index: str)-> List[Ticker]:
	if index == "FTSE":
		symbols = Universe.get_ftse_100_universe()
	elif index == "S&P":
		symbols = Universe.get_sp_500_universe()
	else:
		symbols = Universe.get_freetrade_universe()

	yf = YahooFinApi(Client(FileCache("./data")))
	if symbols is None:
		raise Exception("symbols not found")
	return yf.get_all(symbols)

def get_query_param(param: str, default):
	params = st.experimental_get_query_params()
	if param not in params:
		return default
	
	return params[param][0]

###########
# Sidebar #
###########
universe = st.sidebar.selectbox(
	"Use companies from index", 
	("S&P", "FTSE", "FREETRADE"),
	index=0,
)


########
# Main #
########
tickers = load_data(universe)

res = []
for t in tickers:
	fin_data = t.financial_data
	summary = t.summary_detail

	if fin_data is None or summary is None:
		continue

	if fin_data.free_cash_flow is None or summary.market_cap is None:
		continue

	if fin_data.free_cash_flow < 0:
		continue

	if summary.market_cap < 5 * BILLION:
		continue

	cap_rate = fin_data.free_cash_flow / summary.market_cap * 100

	if cap_rate > 10:
		res.append({
			"symbol": t.symbol,
			"title": t.title,
			"cap_rate": cap_rate,
			"market_cap": summary.market_cap,
			"fcf": fin_data.free_cash_flow,
			"current_price": fin_data.current_price,
			"profit_margin": fin_data.profit_margins
		})

	res = sorted(res, key=lambda r: r["cap_rate"], reverse=True)


st.title("Market Price Screener")
st.text(f"We found {len(res)} stocks matching the rules")

for r in res:
	st.text(r["symbol"])

res = requests.get("https://universal.hellopublic.com/companyLogos/AAPL@3x.png")

st.image(res.content)