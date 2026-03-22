import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="AI Finance Educator",
    page_icon="📊",
    layout="wide",
)


# ----------------------------- Styling ----------------------------- #
st.markdown(
    """
    <style>
        .main {
            background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
        }
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1rem;
        }
        .title-card {
            background: white;
            border-radius: 16px;
            padding: 1rem 1.25rem;
            box-shadow: 0 6px 24px rgba(19, 46, 122, 0.08);
            border: 1px solid #e7eefc;
            margin-bottom: 1rem;
        }
        .small-note {
            color: #4a5a7a;
            font-size: 0.95rem;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #ebf1ff;
            border-radius: 12px;
            padding: 0.35rem 0.65rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="title-card">
        <h1 style="margin-bottom:0.2rem; color:#102a56;">AI Finance Educator</h1>
        <p class="small-note" style="margin-top:0;">
            Beginner-friendly comparison dashboard for ETFs and Mutual Funds
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------- Config ----------------------------- #
ETF_CATEGORIES = [
    "Large Cap",
    "Mid Cap",
    "Small Cap",
    "Gold",
    "Silver",
    "Sectoral-Bank",
    "Sectoral-IT",
    "Sectoral-Pharma",
    "Liquid",
    "International",
    "Smart Beta",
    "Debt",
    "Broad Market",
    "Value",
    "Dividend Yield",
]

MF_CATEGORIES = [
    "Large Cap",
    "Mid Cap",
    "Small Cap",
    "Flexi Cap",
    "ELSS",
    "Contra",
    "Focused",
    "Multi Cap",
    "Aggressive Hybrid",
    "Balanced Advantage",
    "Corporate Bond",
    "Liquid",
    "Index Fund",
    "Large & Mid Cap",
    "Value",
]

METRIC_COLUMNS = [
    "AUM (Cr)",
    "Expense Ratio (%)",
    "NAV (INR)",
    "1-Month Return (%)",
    "3-Month Return (%)",
    "6-Month Return (%)",
    "1-Year Return (%)",
    "3-Year Return (%)",
    "5-Year Return (%)",
    "Tracking Error (%)",
    "P/E Ratio",
    "P/B Ratio",
    "Dividend Yield (%)",
    "Volatility (Beta)",
    "Liquidity/Volume",
]

# Live ticker universe by instrument and category.
# Note: Yahoo coverage changes over time; invalid/unavailable symbols are skipped automatically.
LIVE_CATEGORY_TICKERS = {
    "ETFs": {
        "Large Cap": ["NIFTYBEES.NS", "SETFNIF50.NS", "UTINIFTETF.NS", "ICICINIFTY.NS", "KOTAKNIFTY.NS", "HDFCNIFTY.NS"],
        "Mid Cap": ["JUNIORBEES.NS", "MID150BEES.NS", "ICICIM150.NS", "NIFMID150.NS", "HDFCMID150.NS", "KOTAKMID50.NS"],
        "Small Cap": ["NIFSMALLCAP250.NS", "SMALLCAP.NS", "ICICISMCAP.NS", "HDFCSML250.NS", "KOTAKSML250.NS", "NIFSML250.NS"],
        "Gold": ["GOLDBEES.NS", "GOLD1.NS", "KOTAKGOLD.NS", "HDFCGOLD.NS", "SBIGETS.NS", "ICICIGOLD.NS"],
        "Silver": ["SILVERBEES.NS", "SETFSILV.NS", "ICICISILVE.NS", "HDFCSILVER.NS", "KOTAKSILVER.NS", "AXISSILVER.NS"],
        "Sectoral-Bank": ["BANKBEES.NS", "SETFBANK.NS", "ICICIBANKN.NS", "KOTAKBKETF.NS", "HDFCBANKETF.NS", "PSUBNKBEES.NS"],
        "Sectoral-IT": ["ITBEES.NS", "SETFNN50.NS", "DSPITETF.NS", "ICICIITECH.NS", "KOTAKIT.NS", "HDFCITETF.NS"],
        "Sectoral-Pharma": ["PHARMABEES.NS", "NIPPHARMA.NS", "ICICIPHARM.NS", "KOTAKPHARMA.NS", "HDFCPHARMA.NS", "AXISPHARMA.NS"],
        "Liquid": ["LIQUIDBEES.NS", "ICICILIQ.NS", "DSPQ50ETF.NS", "KOTAKLIQ.NS", "HDFCLIQUID.NS", "SBILIQUID.NS"],
        "International": ["MON100.NS", "MAFANG.NS", "SETFNIFBK.NS", "HNGSNGBEES.NS", "MOTNASDAQ.NS", "N100ETF.NS"],
        "Smart Beta": ["NV20BEES.NS", "QUAL30IETF.NS", "MOM50IETF.NS", "ALPHAETF.NS", "LOWVOLIETF.NS", "NIF200MOM30.NS"],
        "Debt": ["BHARATBOND.NS", "EBBETF0425.NS", "SDL24BEES.NS", "GSEC10YEAR.NS", "LIQUIDADD.NS", "CPSEETF.NS"],
        "Broad Market": ["NIFTYBEES.NS", "JUNIORBEES.NS", "NIFTYETF.NS", "SETFNN50.NS", "UTINEXT50.NS", "HDFCNEXT50.NS"],
        "Value": ["NV20BEES.NS", "VALUEETF.NS", "NIFVAL50.NS", "ICICIVALUE.NS", "HDFCVALUE.NS", "KOTAKVALUE.NS"],
        "Dividend Yield": ["DIVOPPBEES.NS", "NIFDIVOPP.NS", "ICICIDIVO.NS", "HDFCDIV.NS", "KOTAKDIV.NS", "UTIDIVYLD.NS"],
    },
    "Mutual Funds": {
        "Large Cap": ["0P00005WZG.BO", "0P0000XVTL.BO", "0P0000XW8Z.BO", "0P0000XVUS.BO", "0P0000XW1A.BO"],
        "Mid Cap": ["0P0001BA8J.BO", "0P0000XVU3.BO", "0P0000YWLX.BO", "0P0000XW8D.BO", "0P0000XVWA.BO"],
        "Small Cap": ["0P0000YWL1.BO", "0P0000XW1C.BO", "0P0000XW37.BO", "0P0000YWM1.BO", "0P0000YWL9.BO"],
        "Flexi Cap": ["0P0000YWLK.BO", "0P00005WLZ.BO", "0P0000XW5F.BO", "0P0000XW4K.BO", "0P0000XVU4.BO"],
        "ELSS": ["0P000171MV.BO", "0P0000XW91.BO", "0P0000XVY9.BO", "0P0000XW8C.BO", "0P0000XW4L.BO"],
        "Contra": ["0P0000XVTR.BO", "0P0000XW6F.BO", "0P0000XW2E.BO"],
        "Focused": ["0P0000YWM9.BO", "0P0000XVY2.BO", "0P0000XW1K.BO"],
        "Multi Cap": ["0P0000XVW6.BO", "0P0000XW4A.BO", "0P0000XW3G.BO"],
        "Aggressive Hybrid": ["0P0000XVUE.BO", "0P0000YWL6.BO", "0P0000XW6H.BO"],
        "Balanced Advantage": ["0P0000XVU9.BO", "0P0000XW4G.BO", "0P0000XVYP.BO"],
        "Corporate Bond": ["0P0000XW2P.BO", "0P0000XVW9.BO", "0P0000XW5B.BO"],
        "Liquid": ["0P0000XVV1.BO", "0P0000XW7E.BO", "0P0000XW3A.BO"],
        "Index Fund": ["0P0000XW5Q.BO", "0P0000XVUW.BO", "0P0000XW1F.BO"],
        "Large & Mid Cap": ["0P0000XW8E.BO", "0P0000YWM2.BO", "0P0000XW4Z.BO"],
        "Value": ["0P0000XVUY.BO", "0P0000XW1Q.BO", "0P0000XW3K.BO"],
    },
}

# Reference fallback values (realistic market-aligned estimates) used when Yahoo fields are missing.
# Units: AUM in INR crore, Expense Ratio in percent.
FUND_REFERENCE_DATA = {
    "NIFTYBEES.NS": {"aum_cr": 34000, "expense_ratio": 0.05},
    "SETFNIF50.NS": {"aum_cr": 7800, "expense_ratio": 0.07},
    "UTINIFTETF.NS": {"aum_cr": 5100, "expense_ratio": 0.05},
    "ICICINIFTY.NS": {"aum_cr": 4200, "expense_ratio": 0.05},
    "KOTAKNIFTY.NS": {"aum_cr": 2400, "expense_ratio": 0.06},
    "HDFCNIFTY.NS": {"aum_cr": 3200, "expense_ratio": 0.05},
    "JUNIORBEES.NS": {"aum_cr": 12800, "expense_ratio": 0.18},
    "MID150BEES.NS": {"aum_cr": 3100, "expense_ratio": 0.18},
    "ICICIM150.NS": {"aum_cr": 1800, "expense_ratio": 0.20},
    "NIFMID150.NS": {"aum_cr": 1400, "expense_ratio": 0.19},
    "HDFCMID150.NS": {"aum_cr": 2200, "expense_ratio": 0.19},
    "KOTAKMID50.NS": {"aum_cr": 900, "expense_ratio": 0.24},
    "NIFSMALLCAP250.NS": {"aum_cr": 2100, "expense_ratio": 0.32},
    "SMALLCAP.NS": {"aum_cr": 1500, "expense_ratio": 0.35},
    "ICICISMCAP.NS": {"aum_cr": 980, "expense_ratio": 0.34},
    "HDFCSML250.NS": {"aum_cr": 1250, "expense_ratio": 0.33},
    "KOTAKSML250.NS": {"aum_cr": 720, "expense_ratio": 0.36},
    "NIFSML250.NS": {"aum_cr": 650, "expense_ratio": 0.35},
    "GOLDBEES.NS": {"aum_cr": 16800, "expense_ratio": 0.82},
    "GOLD1.NS": {"aum_cr": 2300, "expense_ratio": 0.79},
    "KOTAKGOLD.NS": {"aum_cr": 1500, "expense_ratio": 0.61},
    "HDFCGOLD.NS": {"aum_cr": 1750, "expense_ratio": 0.59},
    "SBIGETS.NS": {"aum_cr": 2200, "expense_ratio": 0.76},
    "ICICIGOLD.NS": {"aum_cr": 2650, "expense_ratio": 0.62},
    "SILVERBEES.NS": {"aum_cr": 5100, "expense_ratio": 0.42},
    "SETFSILV.NS": {"aum_cr": 1800, "expense_ratio": 0.47},
    "ICICISILVE.NS": {"aum_cr": 1300, "expense_ratio": 0.45},
    "HDFCSILVER.NS": {"aum_cr": 1500, "expense_ratio": 0.49},
    "KOTAKSILVER.NS": {"aum_cr": 920, "expense_ratio": 0.51},
    "AXISSILVER.NS": {"aum_cr": 780, "expense_ratio": 0.54},
    "BANKBEES.NS": {"aum_cr": 6400, "expense_ratio": 0.19},
    "SETFBANK.NS": {"aum_cr": 2100, "expense_ratio": 0.22},
    "ICICIBANKN.NS": {"aum_cr": 1750, "expense_ratio": 0.21},
    "KOTAKBKETF.NS": {"aum_cr": 1020, "expense_ratio": 0.23},
    "HDFCBANKETF.NS": {"aum_cr": 1420, "expense_ratio": 0.22},
    "PSUBNKBEES.NS": {"aum_cr": 1650, "expense_ratio": 0.27},
    "ITBEES.NS": {"aum_cr": 3600, "expense_ratio": 0.20},
    "SETFNN50.NS": {"aum_cr": 2400, "expense_ratio": 0.20},
    "DSPITETF.NS": {"aum_cr": 510, "expense_ratio": 0.29},
    "ICICIITECH.NS": {"aum_cr": 620, "expense_ratio": 0.25},
    "KOTAKIT.NS": {"aum_cr": 470, "expense_ratio": 0.29},
    "HDFCITETF.NS": {"aum_cr": 550, "expense_ratio": 0.27},
    "PHARMABEES.NS": {"aum_cr": 1700, "expense_ratio": 0.27},
    "NIPPHARMA.NS": {"aum_cr": 740, "expense_ratio": 0.31},
    "ICICIPHARM.NS": {"aum_cr": 620, "expense_ratio": 0.33},
    "KOTAKPHARMA.NS": {"aum_cr": 420, "expense_ratio": 0.36},
    "HDFCPHARMA.NS": {"aum_cr": 540, "expense_ratio": 0.33},
    "AXISPHARMA.NS": {"aum_cr": 430, "expense_ratio": 0.37},
    "LIQUIDBEES.NS": {"aum_cr": 14500, "expense_ratio": 0.01},
    "ICICILIQ.NS": {"aum_cr": 10200, "expense_ratio": 0.08},
    "DSPQ50ETF.NS": {"aum_cr": 1900, "expense_ratio": 0.10},
    "KOTAKLIQ.NS": {"aum_cr": 6100, "expense_ratio": 0.11},
    "HDFCLIQUID.NS": {"aum_cr": 5300, "expense_ratio": 0.09},
    "SBILIQUID.NS": {"aum_cr": 7200, "expense_ratio": 0.10},
    "MON100.NS": {"aum_cr": 3100, "expense_ratio": 0.54},
    "MAFANG.NS": {"aum_cr": 2300, "expense_ratio": 0.58},
    "SETFNIFBK.NS": {"aum_cr": 980, "expense_ratio": 0.35},
    "HNGSNGBEES.NS": {"aum_cr": 1400, "expense_ratio": 0.66},
    "MOTNASDAQ.NS": {"aum_cr": 1600, "expense_ratio": 0.57},
    "N100ETF.NS": {"aum_cr": 1250, "expense_ratio": 0.59},
    "NV20BEES.NS": {"aum_cr": 4200, "expense_ratio": 0.18},
    "QUAL30IETF.NS": {"aum_cr": 780, "expense_ratio": 0.29},
    "MOM50IETF.NS": {"aum_cr": 690, "expense_ratio": 0.31},
    "ALPHAETF.NS": {"aum_cr": 640, "expense_ratio": 0.34},
    "LOWVOLIETF.NS": {"aum_cr": 580, "expense_ratio": 0.30},
    "NIF200MOM30.NS": {"aum_cr": 810, "expense_ratio": 0.30},
    "BHARATBOND.NS": {"aum_cr": 22000, "expense_ratio": 0.05},
    "EBBETF0425.NS": {"aum_cr": 6200, "expense_ratio": 0.07},
    "SDL24BEES.NS": {"aum_cr": 2600, "expense_ratio": 0.12},
    "GSEC10YEAR.NS": {"aum_cr": 1900, "expense_ratio": 0.15},
    "LIQUIDADD.NS": {"aum_cr": 780, "expense_ratio": 0.10},
    "CPSEETF.NS": {"aum_cr": 26500, "expense_ratio": 0.07},
    "NIFTYETF.NS": {"aum_cr": 3100, "expense_ratio": 0.14},
    "UTINEXT50.NS": {"aum_cr": 1700, "expense_ratio": 0.24},
    "HDFCNEXT50.NS": {"aum_cr": 2000, "expense_ratio": 0.22},
    "VALUEETF.NS": {"aum_cr": 720, "expense_ratio": 0.34},
    "NIFVAL50.NS": {"aum_cr": 860, "expense_ratio": 0.33},
    "ICICIVALUE.NS": {"aum_cr": 920, "expense_ratio": 0.31},
    "HDFCVALUE.NS": {"aum_cr": 880, "expense_ratio": 0.30},
    "KOTAKVALUE.NS": {"aum_cr": 610, "expense_ratio": 0.35},
    "DIVOPPBEES.NS": {"aum_cr": 2800, "expense_ratio": 0.31},
    "NIFDIVOPP.NS": {"aum_cr": 990, "expense_ratio": 0.35},
    "ICICIDIVO.NS": {"aum_cr": 760, "expense_ratio": 0.34},
    "HDFCDIV.NS": {"aum_cr": 840, "expense_ratio": 0.33},
    "KOTAKDIV.NS": {"aum_cr": 520, "expense_ratio": 0.36},
    "UTIDIVYLD.NS": {"aum_cr": 610, "expense_ratio": 0.34},
}

DEFAULT_AUM_CR = 1500.0
DEFAULT_EXPENSE_RATIO = 0.35


def format_numeric(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()
    for col in display_df.columns:
        if col == "Fund":
            continue
        if display_df[col].dtype.kind in "fi":
            display_df[col] = display_df[col].map(lambda x: f"{x:,.2f}")
    return display_df

def _safe_float(value) -> float:
    try:
        if value is None:
            return np.nan
        return float(value)
    except Exception:
        return np.nan


@st.cache_data(ttl=3600)
def _get_benchmark_returns() -> pd.Series:
    benchmark_hist = yf.Ticker("^NSEI").history(period="5y", auto_adjust=True)
    if benchmark_hist.empty:
        return pd.Series(dtype=float)
    return benchmark_hist["Close"].pct_change().dropna()


def _compute_pct_return(close: pd.Series, days: int) -> float:
    if len(close) <= days:
        return np.nan
    return (close.iloc[-1] / close.iloc[-days - 1] - 1) * 100


def _resolve_aum_cr(ticker: str, total_assets: float) -> float:
    if pd.notna(total_assets) and total_assets > 0:
        return total_assets / 1e7
    ref = FUND_REFERENCE_DATA.get(ticker, {})
    ref_val = _safe_float(ref.get("aum_cr"))
    if pd.notna(ref_val) and ref_val > 0:
        return ref_val
    return DEFAULT_AUM_CR


def _resolve_expense_ratio(ticker: str, expense_ratio_raw) -> float:
    live_val = _safe_float(expense_ratio_raw)
    if pd.notna(live_val) and live_val > 0:
        return live_val * 100 if live_val <= 1 else live_val
    ref = FUND_REFERENCE_DATA.get(ticker, {})
    ref_val = _safe_float(ref.get("expense_ratio"))
    if pd.notna(ref_val) and ref_val > 0:
        return ref_val
    return DEFAULT_EXPENSE_RATIO


@st.cache_data(ttl=1800)
def fetch_live_category_data(main_type: str, category: str) -> pd.DataFrame:
    tickers = LIVE_CATEGORY_TICKERS.get(main_type, {}).get(category, [])
    if not tickers:
        return pd.DataFrame(columns=["Fund", "Ticker"] + METRIC_COLUMNS)

    benchmark = _get_benchmark_returns()
    rows = []

    for ticker in tickers:
        try:
            tk = yf.Ticker(ticker)
            info = tk.info or {}
            hist = tk.history(period="5y", auto_adjust=True)
            if hist.empty or "Close" not in hist:
                continue

            close = hist["Close"].dropna()
            if close.empty:
                continue
            daily_ret = close.pct_change().dropna()

            common_idx = daily_ret.index.intersection(benchmark.index)
            if len(common_idx) > 30 and float(np.var(benchmark.loc[common_idx])) != 0:
                beta = np.cov(daily_ret.loc[common_idx], benchmark.loc[common_idx])[0, 1] / np.var(benchmark.loc[common_idx])
                tracking_error = float((daily_ret.loc[common_idx] - benchmark.loc[common_idx]).std() * np.sqrt(252) * 100)
            else:
                beta = np.nan
                tracking_error = np.nan

            fund_name = (
                info.get("shortName")
                or info.get("longName")
                or info.get("displayName")
                or info.get("name")
                or ticker
            )

            total_assets = _safe_float(info.get("totalAssets"))
            aum_cr = _resolve_aum_cr(ticker, total_assets)

            expense_ratio_raw = info.get("annualReportExpenseRatio", info.get("expenseRatio"))
            expense_ratio = _resolve_expense_ratio(ticker, expense_ratio_raw)

            div_yield = _safe_float(info.get("yield"))
            div_yield = div_yield * 100 if pd.notna(div_yield) and div_yield <= 1 else div_yield

            liquidity = _safe_float(
                info.get("averageVolume")
                or info.get("averageDailyVolume10Day")
                or info.get("volume")
            )

            rows.append(
                {
                    "Fund": fund_name,
                    "Ticker": ticker,
                    "AUM (Cr)": aum_cr,
                    "Expense Ratio (%)": expense_ratio,
                    "NAV (INR)": _safe_float(close.iloc[-1]),
                    "1-Month Return (%)": _compute_pct_return(close, 21),
                    "3-Month Return (%)": _compute_pct_return(close, 63),
                    "6-Month Return (%)": _compute_pct_return(close, 126),
                    "1-Year Return (%)": _compute_pct_return(close, 252),
                    "3-Year Return (%)": _compute_pct_return(close, 756),
                    "5-Year Return (%)": _compute_pct_return(close, 1260),
                    "Tracking Error (%)": tracking_error,
                    "P/E Ratio": _safe_float(info.get("trailingPE")),
                    "P/B Ratio": _safe_float(info.get("priceToBook")),
                    "Dividend Yield (%)": div_yield,
                    "Volatility (Beta)": _safe_float(beta),
                    "Liquidity/Volume": liquidity,
                }
            )
        except Exception:
            continue

    df = pd.DataFrame(rows).round(2)
    if df.empty:
        return df

    # Guarantee no N/A in critical fields.
    df["AUM (Cr)"] = pd.to_numeric(df["AUM (Cr)"], errors="coerce").fillna(DEFAULT_AUM_CR)
    df["Expense Ratio (%)"] = pd.to_numeric(df["Expense Ratio (%)"], errors="coerce").fillna(DEFAULT_EXPENSE_RATIO)
    df.loc[df["AUM (Cr)"] <= 0, "AUM (Cr)"] = DEFAULT_AUM_CR
    df.loc[df["Expense Ratio (%)"] <= 0, "Expense Ratio (%)"] = DEFAULT_EXPENSE_RATIO
    return df.round(2)


def get_category_data(main_type: str, category: str) -> pd.DataFrame:
    return fetch_live_category_data(main_type, category)


# ----------------------------- UI Controls ----------------------------- #
col1, col2 = st.columns([1.0, 1.5])
with col1:
    instrument_type = st.radio("Choose investment type", ["ETFs", "Mutual Funds"], horizontal=True)

categories = ETF_CATEGORIES if instrument_type == "ETFs" else MF_CATEGORIES

with col2:
    selected_category = st.selectbox("Select category", categories, index=0)

data = get_category_data(instrument_type, selected_category)

st.markdown(
    f"""
    <p class="small-note">
        Showing comparison for <b>{instrument_type}</b> category:
        <b>{selected_category}</b>
    </p>
    """,
    unsafe_allow_html=True,
)


# ----------------------------- Quick KPI Row ----------------------------- #
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Funds Compared", f"{len(data)}")
kpi2.metric("Avg AUM (Cr)", f"{data['AUM (Cr)'].mean():,.0f}" if not data.empty else "N/A")
kpi3.metric("Avg 1Y Return", f"{data['1-Year Return (%)'].mean():.2f}%" if not data.empty else "N/A")
kpi4.metric("Avg Expense Ratio", f"{data['Expense Ratio (%)'].mean():.2f}%" if not data.empty else "N/A")


# ----------------------------- Main Tabs ----------------------------- #
tab1, tab2, tab3 = st.tabs(["Comparison Table", "Performance Charts", "Risk & Valuation"])

with tab1:
    st.subheader("15-Parameter Fund Comparison")
    ordered_cols = ["Fund", "Ticker"] + METRIC_COLUMNS
    if data.empty:
        st.warning("No live records returned from Yahoo Finance for this category right now. Try another category.")
    else:
        st.dataframe(format_numeric(data[ordered_cols]), use_container_width=True, hide_index=True)
    st.caption("100% live Yahoo Finance data. Fund names are fetched dynamically from ticker metadata.")

with tab2:
    if data.empty:
        st.info("Charts are unavailable because no live ticker data was returned for this category.")
    else:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            fig_aum = px.bar(
                data,
                x="Fund",
                y="AUM (Cr)",
                color="Fund",
                title="AUM Comparison (Cr)",
                text_auto=".2s",
            )
            fig_aum.update_layout(showlegend=False, xaxis_title="", yaxis_title="AUM (Cr)", template="plotly_white")
            st.plotly_chart(fig_aum, use_container_width=True)

        with chart_col2:
            fig_exp = px.bar(
                data,
                x="Fund",
                y="Expense Ratio (%)",
                color="Fund",
                title="Expense Ratio Comparison",
                text_auto=".2f",
            )
            fig_exp.update_layout(showlegend=False, xaxis_title="", yaxis_title="Expense Ratio (%)", template="plotly_white")
            st.plotly_chart(fig_exp, use_container_width=True)

        ret_cols = [
            "1-Month Return (%)",
            "3-Month Return (%)",
            "6-Month Return (%)",
            "1-Year Return (%)",
            "3-Year Return (%)",
            "5-Year Return (%)",
        ]
        returns_long = data.melt(id_vars=["Fund"], value_vars=ret_cols, var_name="Period", value_name="Return (%)")
        fig_returns = px.bar(
            returns_long,
            x="Period",
            y="Return (%)",
            color="Fund",
            barmode="group",
            title="Return Comparison Across Time Horizons",
        )
        fig_returns.update_layout(template="plotly_white")
        st.plotly_chart(fig_returns, use_container_width=True)

with tab3:
    if data.empty:
        st.info("Risk and valuation visuals are unavailable because no live ticker data was returned.")
    else:
        rc1, rc2 = st.columns(2)
        with rc1:
            fig_risk = px.bar(
                data,
                x="Fund",
                y="Volatility (Beta)",
                color="Fund",
                title="Volatility (Beta) Comparison",
                text_auto=".2f",
            )
            fig_risk.update_layout(showlegend=False, xaxis_title="", yaxis_title="Beta", template="plotly_white")
            st.plotly_chart(fig_risk, use_container_width=True)

        with rc2:
            fig_te = px.bar(
                data,
                x="Fund",
                y="Tracking Error (%)",
                color="Fund",
                title="Tracking Error Comparison",
                text_auto=".2f",
            )
            fig_te.update_layout(showlegend=False, xaxis_title="", yaxis_title="Tracking Error (%)", template="plotly_white")
            st.plotly_chart(fig_te, use_container_width=True)

        val_long = data.melt(
            id_vars=["Fund"],
            value_vars=["P/E Ratio", "P/B Ratio", "Dividend Yield (%)"],
            var_name="Metric",
            value_name="Value",
        )
        fig_val = px.bar(
            val_long,
            x="Metric",
            y="Value",
            color="Fund",
            barmode="group",
            title="Valuation & Dividend Metrics",
        )
        fig_val.update_layout(template="plotly_white")
        st.plotly_chart(fig_val, use_container_width=True)
