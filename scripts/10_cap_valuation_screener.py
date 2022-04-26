from __future__ import annotations
from typing import List
import streamlit as st
from yahoo_fin_api import YahooFinApi, Client, FileCache, Universe, Ticker

from lib.utils import get_symbol_img, format_amount, format_percentage

BILLION = 1000000000
HOUR = 60 * 60 #in seconds

@st.experimental_memo(ttl=HOUR)
def load_data(index: str)-> List[Ticker]:
	if index == "FTSE":
		symbols = Universe.get_ftse_100_universe()
	elif index == "S&P":
		symbols = Universe.get_sp_500_universe()
	else:
		symbols = Universe.get_freetrade_universe()

	yf = YahooFinApi(Client())
	if symbols is None:
		raise Exception("symbols not found")
	return yf.get_all(symbols)

def build_cap_valuation(tickers: List[Ticker], market_cap: int, show_top_limit: int)-> List[dict]:
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

		if summary.market_cap < market_cap * BILLION:
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
				"profit_margin": fin_data.profit_margins * 100
			})

	return sorted(res, key=lambda r: r["cap_rate"], reverse=True)[0:show_top_limit]

def display_company_title(title: str)-> str:
	count = len(title.split(" "))
	short = " ".join(title.split(" ")[0:3]).replace(",", "")

	return title if count < 4 else short

def display_stock_list(container, data: list)-> None:
	for i, r in enumerate(data):
		symbol = r["symbol"]
		title = display_company_title(r["title"])
		market_cap = r["market_cap"]
		fcf = r["fcf"]
		profit_margin = r["profit_margin"]
		cap_rate = r["cap_rate"]

		container.markdown(f"#### {i + 1}. {title}")
		symbol_img = get_symbol_img(symbol)
		if symbol_img is not None:
			container.image(symbol_img, width=50)

		container.markdown(f"**{symbol}**")
		container.markdown(display_line("Market cap", format_amount(market_cap)), unsafe_allow_html=True)
		container.markdown(display_line("Free cash flow", format_amount(fcf)), unsafe_allow_html=True)
		container.markdown(display_line("Profit margin", format_percentage(profit_margin)), unsafe_allow_html=True)
		container.markdown(display_line("Cap rate", f"<span style='color:yellow;'>{format_percentage(cap_rate)}</span>"), unsafe_allow_html=True)
		container.markdown(f"[See more](https://uk.finance.yahoo.com/quote/{symbol})")

def display_line(label: str, value: str)-> str:
	return f"""
	<span style='display: flex; justify-content: space-between'>
		<p><strong>{label}:</strong></p>
		<p>{value}</p>
	</span>""".strip()

###########
# Sidebar #
###########
market_cap_limit = st.sidebar.number_input(
	"Market cap min limit (in bil $)",
	min_value=1,
	value=1,
)

show_top_limit = st.sidebar.number_input(
	"Show top limit",
	min_value=1,
	value=10,
)

########
# Main #
########

st.title("10 Cap Valuation Screener")

col1, _, col2 = st.columns([2, 0.5, 2])

############
# Column 1 #
############
col1.header("FTSE 100")

ftse = build_cap_valuation(load_data("FTSE"), market_cap_limit, show_top_limit)
col1.text(f"We found {len(ftse)} stocks matching the rules")

display_stock_list(col1, ftse)

############
# Column 2 #
############
col2.header("S&P 500")

sp = build_cap_valuation(load_data("S&P"), market_cap_limit, show_top_limit)
col2.text(f"We found {len(sp)} stocks matching the rules")

display_stock_list(col2, sp)