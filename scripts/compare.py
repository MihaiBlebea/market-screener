from __future__ import annotations
from typing import List
import pandas as pd
import streamlit as st
import altair as alt
from st_compare_stock import st_compare_stock
from lib.utils import to_percentage, format_percentage
from yahoo_fin_api import YahooFinApi, Client, Universe, Ticker

symbols = Universe.get_freetrade_universe()

@st.experimental_memo
def load_data(symbol: str)-> Ticker:
	yf = YahooFinApi(Client())
	return yf.get_all([symbol])[0]

def current_price(ticker: Ticker)-> float | None:
	if ticker.financial_data is None:
		raise Exception("financial_data not found")
	return ticker.financial_data.current_price

def fair_share_price(ticker: Ticker, min_rate_return: float, growth_rate: float, margin_of_safety: float)-> float:
	if ticker.key_statistics is None or ticker.summary_detail is None:
		raise Exception("key_statistics or summary_detail not found")

	eps = ticker.key_statistics.trailing_eps
	if eps is None:
		raise Exception("eps not found")

	pe_ratio = ticker.summary_detail.forward_pe
	if pe_ratio is None:
		raise Exception("pe_ratio not found")

	future_eps = eps
	for i in range(10):
		if i == 0:
			continue

		future_eps = future_eps + (future_eps * growth_rate)

	fair_share_price = future_eps * pe_ratio
	for i in range(10):
		if i == 0:
			continue

		fair_share_price = fair_share_price / (1 + min_rate_return)

	return fair_share_price



###########
# Sidebar #
###########
symbol = st.sidebar.text_input(
	"Symbol", 
	value="AAPL"
)

symbol_benchmark = st.sidebar.text_input(
	"Benchmark symbol", 
	value="AAPL"
)

min_rate_return = st.sidebar.number_input(
	"Min rate of return", 
	value=0.15
)

growth_rate = st.sidebar.number_input(
	"Growth rate", 
	value=0.12
)


########
# Main #
########
ticker = load_data(symbol)

ticker_benchmark = load_data(symbol_benchmark)

st.title(ticker.title)
st.subheader(ticker.symbol)

fair_price = round(fair_share_price(ticker, min_rate_return, growth_rate, 0.50), 2)
curr_price = current_price(ticker)

col1, col2 = st.columns(2)
col1.metric(
	"Fair share price", 
	fair_price, 
	format_percentage(to_percentage(curr_price, fair_price)),
)

col2.metric(
	"Forward EPS", 
	ticker.key_statistics.forward_eps, 
	format_percentage(to_percentage(ticker.key_statistics.trailing_eps, ticker.key_statistics.forward_eps)),
)

cfs = ticker.get_cashflows()

data = {
	"item": [],
	"year": [],
	"value": [],
}
for cf in cfs:
	data["item"].append("operating activity")
	data["value"].append(cf.total_cash_from_operating_activities)
	data["year"].append(cf.fmt_end_date())

	data["item"].append("financing activity")
	data["value"].append(cf.total_cash_from_financing_activities)
	data["year"].append(cf.fmt_end_date())

	data["item"].append("investing activity")
	data["value"].append(cf.total_cashflows_from_investing_activities)
	data["year"].append(cf.fmt_end_date())


st.subheader("Profit margin")
st_compare_stock(
	symbol={
		"title": ticker.symbol,
		"value": round(ticker.key_statistics.profit_margins, 2),
		"description": f"{ticker.symbol} has a higher profit margin which means that it can generate more cashflow"
	},
	symbol_benchmark={
		"title": ticker_benchmark.symbol,
		"value": round(ticker_benchmark.key_statistics.profit_margins, 2),
		"description": f"{ticker.symbol} has a higher profit margin which means that it can generate more cashflow"
	}
)