from __future__ import annotations
import streamlit as st
import requests

def get_query_param(param: str, default):
	params = st.experimental_get_query_params()
	if param not in params:
		return default
	
	return params[param][0]

def get_symbol_img(symbol: str)-> bytes | None:
	symbol = symbol.upper()
	res = requests.get(f"https://universal.hellopublic.com/companyLogos/{symbol}@3x.png")

	if res.status_code != 200:
		return None

	return res.content

def format_amount(value: float | int | None)-> str:
	return "${:,}".format(value) if value is not None else "$0"

def format_percentage(value: float)-> str:
	return f"{round(value, 2)}%"

def to_percentage(initial: float, final: float)-> float:
	diff = (final - initial) / initial * 100
	return round(diff)