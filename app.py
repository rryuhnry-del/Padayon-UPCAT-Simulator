import streamlit as st
import google.generativeai as genai
import json
import time
import math
import numpy as np
import re

# ==========================================
# SESSION STATE INIT
# ==========================================
defaults = {
    'user_answers_math': {}, 'user_answers_sci': {},
    'submitted': False, 'test_data': None,
    'flagged_items': set(),
    'font_size': 'medium',
    'active_subtest': 'math',
    'math_start_time': None, 'sci_start_time': None,
    'elapsed_math': 0, 'elapsed_sci': 0,
    'competencies_math': '', 'competencies_sci': '',
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Padayon! UPCAT 2026 Simulator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

FONT_SIZES = {'small': '0.85rem', 'medium': '1rem', 'large': '1.1rem', 'x-large': '1.2rem'}
fs = FONT_SIZES.get(st.session_state.get('font_size', 'medium'), '1rem')

# ==========================================
# CSS
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {{
  --bg0: #070b12;
  --bg1: #0e1520;
  --bg2: #141d2e;
  --bg3: #1a2540;
  --bg4: #223050;
  --blue:   #4d9fff;
  --teal:   #2dd4bf;
  --green:  #34d399;
  --amber:  #fbbf24;
  --red:    #f87171;
  --purple: #a78bfa;
  --blue-dim:  rgba(77,159,255,0.10);
  --teal-dim:  rgba(45,212,191,0.10);
  --green-dim: rgba(52,211,153,0.10);
  --amber-dim: rgba(251,191,36,0.10);
  --red-dim:   rgba(248,113,113,0.10);
  --fg0: #f0f4f8;
  --fg1: #9aaabb;
  --fg2: #5a6a7a;
  --border: rgba(255,255,255,0.06);
  --border2: rgba(255,255,255,0.12);
  --r: 8px; --r2: 12px; --r3: 16px;
  --font-display: 'Syne', sans-serif;
  --font-body: 'Source Serif 4', Georgia, serif;
  --font-mono: 'IBM Plex Mono', monospace;
  --fs: {fs};
  --shadow: 0 4px 24px rgba(0,0,0,0.5);
  --shadow2: 0 8px 40px rgba(0,0,0,0.7);
  --t: 0.18s cubic-bezier(0.4,0,0.2,1);
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

.stApp, body {{
  background: var(--bg0) !important;
  color: var(--fg0) !important;
  font-family: var(--font-body) !important;
  font-size: var(--fs) !important;
}}

#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
  padding-top: 1.5rem !important;
  padding-bottom: 6rem !important;
  max-width: 1380px !important;
}}

h1,h2,h3,h4,h5,h6 {{
  font-family: var(--font-display) !important;
  color: var(--fg0) !important;
  letter-spacing: -0.02em !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: var(--bg1) !important;
  border-right: 1px solid var(--border) !important;
}}
section[data-testid="stSidebar"] * {{ color: var(--fg1) !important; }}
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] label {{ color: var(--fg0) !important; font-family: var(--font-display) !important; }}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] textarea {{
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--fg0) !important;
  border-radius: var(--r) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.82rem !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
  background: var(--bg2) !important; border-color: var(--border2) !important; color: var(--fg0) !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] * {{ color: var(--fg0) !important; background: var(--bg2) !important; }}
[data-baseweb="popover"] * {{ background: var(--bg3) !important; color: var(--fg0) !important; border-color: var(--border2) !important; }}

/* ── Buttons ── */
.stButton > button {{
  font-family: var(--font-display) !important;
  font-weight: 700 !important; font-size: 0.82rem !important;
  letter-spacing: 0.04em !important; text-transform: uppercase !important;
  border-radius: var(--r) !important; transition: all var(--t) !important;
  min-height: 42px !important;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, #1a56db 0%, var(--blue) 100%) !important;
  border: none !important; color: #fff !important;
  box-shadow: 0 0 0 1px rgba(77,159,255,0.3), 0 4px 16px rgba(26,86,219,0.5) !important;
}}
.stButton > button[kind="primary"]:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 0 0 1px rgba(77,159,255,0.5), 0 8px 24px rgba(26,86,219,0.6) !important;
}}
.stButton > button[kind="secondary"] {{
  background: var(--bg2) !important; border: 1px solid var(--border2) !important; color: var(--fg1) !important;
}}
.stButton > button[kind="secondary"]:hover {{
  background: var(--bg3) !important; border-color: var(--blue) !important; color: var(--fg0) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 2px; background: var(--bg1); border: 1px solid var(--border) !important;
  border-radius: var(--r2); padding: 4px; flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
  font-family: var(--font-display) !important; font-size: 0.75rem !important;
  font-weight: 700 !important; letter-spacing: 0.05em !important;
  text-transform: uppercase !important; padding: 7px 14px !important;
  border-radius: var(--r) !important; background: transparent !important;
  color: var(--fg2) !important; border: none !important; transition: all var(--t) !important;
}}
.stTabs [aria-selected="true"] {{ background: var(--bg3) !important; color: var(--blue) !important; }}

/* ── Radio ── */
.stRadio > label {{ display: none !important; }}
.stRadio [data-testid="stWidgetLabel"] {{ display: none !important; }}
.stRadio > div {{ display: flex !important; flex-direction: column !important; gap: 6px !important; }}
.stRadio > div > label {{
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important; padding: 11px 16px !important;
  cursor: pointer !important; transition: all var(--t) !important;
  font-family: var(--font-body) !important; font-size: var(--fs) !important;
  line-height: 1.7 !important; color: var(--fg0) !important;
  display: flex !important; align-items: center !important; gap: 10px !important;
}}
.stRadio > div > label:hover {{
  border-color: var(--blue) !important; background: var(--blue-dim) !important;
  transform: translateX(3px) !important;
}}
.stRadio > div > label[data-checked="true"] {{
  border-color: var(--blue) !important; background: var(--blue-dim) !important;
}}
/* KaTeX inside radio labels */
.stRadio > div > label .katex {{ color: var(--fg0) !important; }}
.stRadio > div > label .katex * {{ color: var(--fg0) !important; }}

/* ── Expanders ── */
.streamlit-expanderHeader {{
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important; color: var(--fg0) !important;
  font-family: var(--font-display) !important; font-size: 0.82rem !important;
  font-weight: 700 !important; letter-spacing: 0.04em !important;
  text-transform: uppercase !important; min-height: 44px !important; padding: 0 14px !important;
}}
.streamlit-expanderContent {{
  background: var(--bg1) !important; border: 1px solid var(--border) !important;
  border-top: none !important; border-radius: 0 0 var(--r) var(--r) !important; padding: 16px !important;
}}

/* ── Textarea ── */
.stTextArea textarea {{
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  color: var(--fg0) !important; border-radius: var(--r) !important;
  font-family: var(--font-mono) !important; font-size: 0.82rem !important; line-height: 1.7 !important;
}}
.stTextArea textarea:focus {{ border-color: var(--blue) !important; box-shadow: 0 0 0 2px rgba(77,159,255,0.2) !important; }}

/* ── Alerts ── */
.stAlert {{ background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: var(--r) !important; color: var(--fg0) !important; }}

/* ── Select / Number ── */
.stSelectbox > div > div, .stNumberInput > div > div > input {{
  background: var(--bg2) !important; border-color: var(--border2) !important;
  color: var(--fg0) !important; border-radius: var(--r) !important; font-family: var(--font-mono) !important;
}}

/* ── Metric ── */
[data-testid="metric-container"] {{
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important; padding: 16px !important;
}}
[data-testid="metric-container"] label {{ color: var(--fg2) !important; font-size: 0.72rem !important; font-family: var(--font-display) !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{ color: var(--blue) !important; font-family: var(--font-display) !important; font-size: 1.6rem !important; }}

/* ── Progress ── */
[data-testid="stProgress"] > div > div {{ background: var(--bg3) !important; border-radius: 4px; }}
[data-testid="stProgress"] > div > div > div {{ background: linear-gradient(90deg, var(--blue), var(--teal)) !important; border-radius: 4px; }}

/* ── Checkbox ── */
.stCheckbox label span {{ color: var(--fg1) !important; font-family: var(--font-display) !important; font-size: 0.82rem !important; }}

/* ==========================================
   CUSTOM COMPONENTS
   ========================================== */

/* Hero */
.hero {{
  position: relative; background: linear-gradient(145deg, #070b12 0%, #0c1628 50%, #071420 100%);
  border: 1px solid var(--border2); border-radius: 20px; overflow: hidden;
  margin-bottom: 24px; box-shadow: var(--shadow2);
}}
.hero-glow-l {{ position: absolute; width: 500px; height: 500px; border-radius: 50%; top: -150px; left: -100px; background: radial-gradient(circle, rgba(77,159,255,0.08) 0%, transparent 70%); pointer-events: none; }}
.hero-glow-r {{ position: absolute; width: 400px; height: 400px; border-radius: 50%; bottom: -100px; right: -50px; background: radial-gradient(circle, rgba(45,212,191,0.07) 0%, transparent 70%); pointer-events: none; }}
.hero-inner {{ position: relative; z-index: 2; padding: 48px 56px 40px; }}
.hero-eyebrow {{
  font-family: var(--font-mono); font-size: 0.6rem; font-weight: 600;
  letter-spacing: 0.25em; text-transform: uppercase; color: var(--blue);
  background: rgba(77,159,255,0.1); border: 1px solid rgba(77,159,255,0.2);
  padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 20px;
}}
.hero-title {{
  font-family: var(--font-display) !important; font-size: clamp(2rem, 4vw, 3.4rem) !important;
  font-weight: 800 !important; line-height: 1.05 !important; letter-spacing: -0.03em !important;
  color: #fff !important; margin-bottom: 16px !important;
}}
.hero-title .accent {{ color: var(--blue); }}
.hero-title .accent2 {{ color: var(--teal); }}
.hero-sub {{ font-family: var(--font-body); font-size: 0.9rem; line-height: 1.8; color: rgba(255,255,255,0.45); max-width: 640px; margin-bottom: 28px; }}
.hero-rule {{ height: 1px; background: linear-gradient(90deg, rgba(77,159,255,0.3), transparent); margin-bottom: 24px; }}
.hero-stats {{ display: flex; gap: 36px; flex-wrap: wrap; }}
.hs-num {{ font-family: var(--font-display); font-size: 1.8rem; font-weight: 800; color: var(--blue); line-height: 1; }}
.hs-lbl {{ font-family: var(--font-mono); font-size: 0.58rem; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 0.12em; margin-top: 4px; }}

/* Section title */
.sec-title {{
  font-family: var(--font-display) !important; font-size: 0.72rem !important;
  font-weight: 700 !important; letter-spacing: 0.2em !important; text-transform: uppercase !important;
  color: var(--fg2) !important; display: flex; align-items: center; gap: 10px; margin: 28px 0 14px;
}}
.sec-title::after {{ content: ''; flex: 1; height: 1px; background: var(--border); }}

/* Notice */
.notice {{
  display: flex; gap: 12px; background: var(--bg2); border: 1px solid var(--border2);
  border-left: 3px solid var(--blue); border-radius: var(--r); padding: 12px 16px;
  font-family: var(--font-body); font-size: 0.84rem; color: var(--fg1); line-height: 1.7; margin-bottom: 14px;
}}
.notice.warn {{ border-left-color: var(--amber); }}
.notice.sci  {{ border-left-color: var(--teal); }}
.notice.red  {{ border-left-color: var(--red); }}
.notice.green{{ border-left-color: var(--green); }}
.notice strong {{ color: var(--fg0); }}
.ni {{ font-size: 1rem; flex-shrink: 0; margin-top: 1px; }}

/* Competency wrap */
.comp-wrap {{ background: var(--bg1); border: 1px solid var(--border2); border-radius: var(--r2); padding: 16px 20px; margin-bottom: 12px; }}
.comp-wrap.math {{ border-top: 2px solid var(--blue); }}
.comp-wrap.sci  {{ border-top: 2px solid var(--teal); }}
.comp-head {{ font-family: var(--font-display); font-size: 0.85rem; font-weight: 700; color: var(--fg0); margin-bottom: 4px; }}
.comp-sub {{ font-family: var(--font-mono); font-size: 0.62rem; color: var(--fg2); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px; }}

/* Question card */
.q-card {{
  background: var(--bg1); border: 1px solid var(--border); border-left: 3px solid var(--blue);
  border-radius: var(--r2); padding: 20px 24px; margin-bottom: 14px;
  transition: box-shadow var(--t); scroll-margin-top: 80px;
}}
.q-card.sci {{ border-left-color: var(--teal); }}
.q-card.answered {{ border-left-color: var(--green); }}
.q-card.flagged {{ border-left-color: var(--amber); }}
.q-card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}

/* Question meta row */
.q-meta {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }}
.q-badge {{
  font-family: var(--font-mono); font-size: 0.58rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase; padding: 3px 9px; border-radius: 4px;
  display: inline-block; white-space: nowrap;
}}
.q-badge.math {{ color: var(--blue); background: var(--blue-dim); border: 1px solid rgba(77,159,255,0.2); }}
.q-badge.sci  {{ color: var(--teal); background: var(--teal-dim); border: 1px solid rgba(45,212,191,0.2); }}
.q-badge.tag  {{ color: var(--fg2); background: var(--bg3); border: 1px solid var(--border2); }}
.q-badge.flag {{ color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(251,191,36,0.2); }}
.q-badge.ok   {{ color: var(--green); background: var(--green-dim); border: 1px solid rgba(52,211,153,0.2); }}

/* Question stem — KaTeX will render here */
.q-stem {{
  font-family: var(--font-body); font-size: var(--fs); line-height: 1.9;
  color: var(--fg0); margin-bottom: 16px;
}}
.q-stem .katex {{ font-size: 1.05em !important; }}
.q-stem .katex * {{ color: var(--fg0) !important; }}
.q-stem .katex-display {{
  background: var(--bg3); border-radius: var(--r); padding: 12px 16px;
  margin: 10px 0; overflow-x: auto; border: 1px solid var(--border);
}}
.q-stem .katex-display .katex {{ font-size: 1.15em !important; }}

/* Science stimuli */
.stim-passage {{
  background: var(--bg2); border: 1px solid var(--border2); border-left: 3px solid var(--teal);
  border-radius: var(--r); padding: 14px 18px; margin-bottom: 14px;
  font-family: var(--font-body); font-size: 0.875rem; line-height: 1.85; color: var(--fg1);
}}
.stim-data {{
  background: var(--bg2); border: 1px solid var(--border2); border-left: 3px solid var(--amber);
  border-radius: var(--r); padding: 14px 18px; margin-bottom: 14px;
  font-family: var(--font-mono); font-size: 0.78rem; line-height: 1.7; color: var(--fg1); overflow-x: auto;
}}
.stim-diagram {{
  background: var(--bg2); border: 1px solid var(--border2); border-left: 3px solid var(--purple);
  border-radius: var(--r); padding: 14px 18px; margin-bottom: 14px;
  font-family: var(--font-mono); font-size: 0.78rem; line-height: 1.7; color: var(--fg1); overflow-x: auto;
}}
.stim-label {{
  font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.14em;
  text-transform: uppercase; margin-bottom: 8px; display: block; font-weight: 600;
}}
.stim-label.p {{ color: var(--teal); }}
.stim-label.d {{ color: var(--amber); }}
.stim-label.g {{ color: var(--purple); }}

/* Science data table */
.sci-tbl {{ width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 0.82rem; }}
.sci-tbl th {{
  background: var(--bg3); color: var(--fg0); padding: 8px 12px; text-align: left;
  border-bottom: 1px solid var(--border2); font-size: 0.72rem; letter-spacing: 0.04em;
  font-family: var(--font-display);
}}
.sci-tbl td {{ padding: 7px 12px; border-bottom: 1px solid var(--border); color: var(--fg1); }}
.sci-tbl tr:last-child td {{ border-bottom: none; }}
.sci-tbl tr:hover td {{ background: var(--bg3); }}

/* Navigator */
.nav-box {{
  background: var(--bg1); border: 1px solid var(--border2); border-radius: var(--r2);
  padding: 14px 18px; margin-bottom: 18px; position: sticky; top: 10px; z-index: 99;
  box-shadow: var(--shadow);
}}
.nav-title {{ font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg2); margin-bottom: 10px; }}
.nav-grid {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.nav-dot {{
  min-width: 32px; height: 28px; border-radius: 5px; display: inline-flex;
  align-items: center; justify-content: center; font-family: var(--font-mono);
  font-size: 0.6rem; font-weight: 600; cursor: pointer;
  background: var(--bg3); color: var(--fg2); border: 1px solid var(--border);
  transition: all var(--t);
}}
.nav-dot:hover {{ border-color: var(--blue); color: var(--blue); transform: scale(1.1); }}
.nav-dot.am {{ background: var(--blue-dim); color: var(--blue); border-color: rgba(77,159,255,0.3); }}
.nav-dot.as {{ background: var(--teal-dim); color: var(--teal); border-color: rgba(45,212,191,0.3); }}
.nav-dot.fl {{ background: var(--amber-dim); color: var(--amber); border-color: rgba(251,191,36,0.3); }}

/* Progress bar */
.pbar-wrap {{ margin-bottom: 12px; }}
.pbar-row {{ display: flex; justify-content: space-between; font-family: var(--font-mono); font-size: 0.6rem; color: var(--fg2); margin-bottom: 5px; }}
.pbar-track {{ height: 4px; background: var(--bg3); border-radius: 2px; overflow: hidden; }}
.pbar-fill-m {{ height: 100%; border-radius: 2px; background: linear-gradient(90deg, #1a56db, var(--blue)); transition: width 0.5s ease; }}
.pbar-fill-s {{ height: 100%; border-radius: 2px; background: linear-gradient(90deg, #0d6b63, var(--teal)); transition: width 0.5s ease; }}

/* Timer */
.timer {{
  position: fixed; top: 16px; right: 20px; z-index: 99999;
  font-family: var(--font-mono); font-size: 0.95rem; font-weight: 600;
  padding: 8px 18px; border-radius: 24px; border: 1px solid rgba(77,159,255,0.3);
  background: var(--bg1); color: var(--blue); box-shadow: var(--shadow); letter-spacing: 0.06em;
}}
.timer.s {{ color: var(--teal); border-color: rgba(45,212,191,0.3); }}
.timer.w {{ color: var(--amber); border-color: rgba(251,191,36,0.4); }}
.timer.d {{ color: var(--red); border-color: rgba(248,113,113,0.4); animation: pulse 1s infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.6; }} }}

/* Stat row */
.stat-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 12px 0; }}
.stat-pill {{ background: var(--bg2); border: 1px solid var(--border2); border-radius: var(--r); padding: 12px 18px; flex: 1; min-width: 90px; text-align: center; }}
.sp-n {{ font-family: var(--font-display); font-size: 1.6rem; font-weight: 800; line-height: 1; }}
.sp-l {{ font-family: var(--font-mono); font-size: 0.55rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg2); margin-top: 4px; }}

/* Results */
.res-hero {{
  background: linear-gradient(145deg, #070b12, #0c1628, #071420);
  border: 1px solid var(--border2); border-radius: 20px; padding: 52px 48px;
  text-align: center; position: relative; overflow: hidden; margin-bottom: 24px; box-shadow: var(--shadow2);
}}
.res-hero-glow {{ position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(77,159,255,0.07) 0%, transparent 65%); pointer-events: none; }}
.upg-label {{ font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 10px; position: relative; z-index: 1; }}
.upg-val {{ font-family: var(--font-display); font-size: clamp(4rem, 9vw, 7rem); font-weight: 800; line-height: 1; position: relative; z-index: 1; letter-spacing: -0.04em; }}
.upg-verdict {{ font-family: var(--font-body); font-size: 1rem; color: rgba(255,255,255,0.5); margin-top: 12px; position: relative; z-index: 1; }}

.upg-cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }}
.upg-card {{ background: var(--bg1); border: 1px solid var(--border2); border-radius: var(--r2); padding: 22px 26px; }}
.upg-card.m {{ border-top: 2px solid var(--blue); }}
.upg-card.s {{ border-top: 2px solid var(--teal); }}
.upg-card-title {{ font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 10px; }}
.upg-card.m .upg-card-title {{ color: var(--blue); }}
.upg-card.s .upg-card-title {{ color: var(--teal); }}
.upg-card-val {{ font-family: var(--font-display); font-size: 2.8rem; font-weight: 800; line-height: 1; margin-bottom: 6px; }}
.upg-card.m .upg-card-val {{ color: var(--blue); }}
.upg-card.s .upg-card-val {{ color: var(--teal); }}
.upg-card-sub {{ font-family: var(--font-body); font-size: 0.8rem; color: var(--fg1); }}
.upg-br {{ margin-top: 14px; }}
.upg-br-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); font-family: var(--font-body); font-size: 0.8rem; }}
.upg-br-row:last-child {{ border-bottom: none; }}
.upg-br-lbl {{ color: var(--fg1); }}
.upg-br-val {{ font-family: var(--font-mono); font-weight: 600; font-size: 0.78rem; }}

.score-panel {{ background: var(--bg1); border: 1px solid var(--border2); border-radius: var(--r2); padding: 20px 24px; }}
.score-panel h4 {{ font-family: var(--font-display) !important; font-size: 0.85rem !important; font-weight: 700 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; margin-bottom: 14px !important; padding-bottom: 12px !important; border-bottom: 1px solid var(--border) !important; }}
.s-row {{ display: flex; justify-content: space-between; align-items: center; padding: 7px 0; border-bottom: 1px solid var(--border); font-family: var(--font-body); font-size: 0.84rem; }}
.s-row:last-child {{ border-bottom: none; }}
.s-lbl {{ color: var(--fg1); }}
.s-val {{ font-family: var(--font-mono); font-weight: 600; font-size: 0.8rem; }}
.s-val.c {{ color: var(--green); }}
.s-val.w {{ color: var(--red); }}
.s-val.g {{ color: var(--blue); }}

/* Heatmap */
.heat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }}
.heat-row {{ display: flex; align-items: center; gap: 8px; font-family: var(--font-body); font-size: 0.75rem; padding: 7px 10px; border-radius: var(--r); border: 1px solid var(--border); background: var(--bg2); }}
.heat-bar-out {{ flex: 1; height: 4px; background: var(--bg3); border-radius: 2px; overflow: hidden; }}
.heat-bar-in {{ height: 100%; border-radius: 2px; transition: width 0.8s ease; }}
.heat-bar-in.hi {{ background: var(--green); }}
.heat-bar-in.mid {{ background: var(--amber); }}
.heat-bar-in.lo {{ background: var(--red); }}
.heat-pct {{ font-family: var(--font-mono); font-size: 0.58rem; font-weight: 700; min-width: 32px; text-align: right; }}

/* Review answer boxes */
.ir-c {{ background: var(--green-dim); border: 1px solid rgba(52,211,153,0.25); border-radius: var(--r); padding: 9px 14px; font-family: var(--font-body); color: var(--green); margin: 4px 0; font-size: var(--fs); }}
.ir-w {{ background: var(--red-dim); border: 1px solid rgba(248,113,113,0.25); border-radius: var(--r); padding: 9px 14px; font-family: var(--font-body); color: var(--red); margin: 4px 0; font-size: var(--fs); }}
.ir-o {{ background: var(--bg2); border: 1px solid var(--border); border-radius: var(--r); padding: 9px 14px; font-family: var(--font-body); color: var(--fg1); margin: 4px 0; font-size: var(--fs); }}

/* Campus cards */
.campus-card {{ background: var(--bg1); border: 1px solid var(--border2); border-radius: var(--r2); overflow: hidden; margin-bottom: 14px; }}
.campus-hdr {{ padding: 14px 20px; background: linear-gradient(135deg, #0a2a16, #0d3820); border-bottom: 1px solid var(--border2); }}
.campus-hdr.fail {{ background: linear-gradient(135deg, #2a0a0a, #3a1010); }}
.campus-hdr h4 {{ color: var(--fg0) !important; font-size: 0.95rem !important; margin-bottom: 3px !important; }}
.campus-hdr p {{ color: var(--fg1) !important; font-family: var(--font-mono); font-size: 0.62rem !important; }}
.campus-body {{ padding: 14px 20px; }}
.prog-row {{ display: flex; justify-content: space-between; align-items: center; padding: 9px 0; border-bottom: 1px solid var(--border); font-family: var(--font-body); font-size: 0.84rem; }}
.prog-row:last-child {{ border-bottom: none; }}
.prog-name {{ font-weight: 600; color: var(--fg0); font-family: var(--font-display); }}
.prog-sub {{ font-family: var(--font-mono); font-size: 0.58rem; color: var(--fg2); margin-top: 2px; }}
.badge {{ font-family: var(--font-mono); font-size: 0.6rem; font-weight: 700; padding: 3px 10px; border-radius: 4px; }}
.badge.pass {{ color: var(--green); background: var(--green-dim); border: 1px solid rgba(52,211,153,0.25); }}
.badge.risk {{ color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(251,191,36,0.25); }}
.badge.fail {{ color: var(--red); background: var(--red-dim); border: 1px solid rgba(248,113,113,0.25); }}

/* Chart wrap */
.chart-wrap {{ background: var(--bg2); border: 1px solid var(--border2); border-radius: var(--r2); padding: 8px; margin: 12px 0; }}

@media (max-width: 768px) {{
  .hero-inner {{ padding: 28px 24px; }}
  .upg-cards {{ grid-template-columns: 1fr; }}
  .heat-grid {{ grid-template-columns: 1fr; }}
}}
@media print {{
  section[data-testid="stSidebar"], .timer, .stButton {{ display: none !important; }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition-duration: 0.01ms !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA
# ==========================================
SCHOOL_TIERS = {
    "PSHS (Philippine Science High School)": {"modifier": 0.30, "palugit": True},
    "DepEd Specialized Science & Math (PSHS-Affiliate)": {"modifier": 0.22, "palugit": True},
    "DepEd Laboratory School (UP, PNU, etc.)": {"modifier": 0.18, "palugit": True},
    "DepEd Legislated Special School": {"modifier": 0.14, "palugit": True},
    "Public — Special Program (STEM, TVL, ABM)": {"modifier": 0.07, "palugit": True},
    "Public — Regular National High School": {"modifier": 0.04, "palugit": True},
    "Public — Barangay / Community High School": {"modifier": 0.09, "palugit": True},
    "Public — Vocational / Technical": {"modifier": 0.06, "palugit": True},
    "Private — International School (IB, AP, Cambridge)": {"modifier": 0.08, "palugit": False},
    "Private — University Affiliated / Sectarian Elite": {"modifier": -0.04, "palugit": False},
    "Private — Regular Sectarian": {"modifier": -0.08, "palugit": False},
    "Private — Non-Sectarian": {"modifier": -0.12, "palugit": False},
}

CAMPUS_DATA = {
    "UP Diliman":          {"cutoff": 2.20, "recon": 0.0,   "note": "Strictest. No appeals."},
    "UP Manila":           {"cutoff": 2.10, "recon": 2.580, "note": "Health sciences hub."},
    "UP Los Baños":        {"cutoff": 2.30, "recon": 2.800, "note": "Agri/forestry flagship."},
    "UP Baguio":           {"cutoff": 2.50, "recon": 2.700, "note": "Arts & sciences."},
    "UP Cebu":             {"cutoff": 2.60, "recon": 2.800, "note": "Growing campus."},
    "UP Mindanao":         {"cutoff": 2.60, "recon": 2.800, "note": "Priority for Mindanaoan applicants."},
    "UP Visayas (Iloilo)": {"cutoff": 2.70, "recon": 2.700, "note": "Marine & fisheries."},
    "UP Open University":  {"cutoff": 2.80, "recon": 2.800, "note": "Distance learning."},
}

PROGRAM_TIERS = {
    "UP Diliman": {
        "Triple Quota": ["BS Architecture","BS Biology","BS Business Administration & Accountancy","BS Civil Engineering","BS Computer Science","BS Electrical Engineering","BS Mechanical Engineering","BS Molecular Biology & Biotech","BS Psychology","BS Chemical Engineering"],
        "Double Quota": ["BA Broadcast Communication","BS Business Administration","BS Business Economics","BS Computer Engineering","BS Economics","BS Industrial Engineering","BA Political Science","BA Psychology","BS Mathematics"],
        "Single Quota": ["BS Applied Physics","BS Chemistry","BS Food Technology","BS Geodetic Engineering","BS Materials Engineering","BS Physics","BS Statistics","BS Geology"],
        "Less Popular": ["BA Anthropology","BA Araling Pilipino","BA Art Studies","BA English Studies","BA Filipino","BA History","BS Social Work","BA Sociology"]
    },
    "UP Manila": {
        "Triple Quota": ["BS Biochemistry","BS Biology","BS Nursing","BS Public Health","BS Pharmacy"],
        "Double Quota": ["BS Computer Science","D Dental Medicine","BS Occupational Therapy","BS Physical Therapy","BS Speech Pathology"],
        "Single Quota": ["BS Applied Physics","BA Behavioral Sciences","BA Political Science"],
        "Less Popular": ["BA Development Studies","BA Philippine Arts","BA Social Work"]
    },
    "UP Los Baños": {
        "Triple Quota": ["BS Biology","BS Chemical Engineering","BS Civil Engineering","BS Computer Science","D Veterinary Medicine"],
        "Double Quota": ["BS Accountancy","BS Economics","BS Electrical Engineering","BS Industrial Engineering","BS Mechanical Engineering"],
        "Single Quota": ["BS Agribusiness Management","BS Food Technology","BS Mathematics","BS Statistics"],
        "Less Popular": ["BS Agriculture","BS Forestry","BS Human Ecology","BS Nutrition"]
    },
    "UP Baguio": {
        "Triple Quota": ["BS Computer Science","BS Biology","BS Mathematics"],
        "Double Quota": ["BA Communication","BS Physics","BS Management Economics"],
        "Single Quota": ["BA Languages & Literature","BS Statistics"],
        "Less Popular": ["BA Social Sciences"]
    },
    "UP Cebu": {
        "Triple Quota": ["BS Accountancy","BS Biology","BS Computer Science","BS Management"],
        "Double Quota": ["BA Political Science","BS Mathematics","BS Statistics"],
        "Single Quota": ["BA Communication"],
        "Less Popular": ["BA Arts & Humanities"]
    },
    "UP Mindanao": {
        "Triple Quota": ["BS Architecture","BS Biology","BS Computer Science","BS Data Science"],
        "Double Quota": ["BS Agribusiness Economics","BS Food Technology"],
        "Single Quota": ["BA English","BS Environmental Science"],
        "Less Popular": ["BA Anthropology","BA Mindanao Studies"]
    },
    "UP Visayas (Iloilo)": {
        "Triple Quota": ["BS Accountancy","BS Biology","BS Business Administration","BS Chemical Engineering","BS Computer Science","BS Economics","BS Fisheries","BS Management","BS Public Health"],
        "Double Quota": ["BS Chemistry","BS Food Technology","BS Statistics","BS Marine Biology"],
        "Single Quota": ["BS Applied Mathematics","BS Fisheries Engineering"],
        "Less Popular": ["BS Community Development","BA History","BA Literature"]
    },
    "UP Open University": {
        "Triple Quota": [],
        "Double Quota": [],
        "Single Quota": ["BA Multi Media Studies","B Education Studies"],
        "Less Popular": ["BA Social Sciences","BA Journalism"]
    }
}

def get_all_programs(campus):
    progs = []
    for tier, plist in PROGRAM_TIERS.get(campus, {}).items():
        progs.extend(plist)
    return sorted(progs)

def get_program_tier(campus, program):
    for tier, plist in PROGRAM_TIERS.get(campus, {}).items():
        if program in plist:
            return tier
    return "Less Popular"

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style='background:linear-gradient(135deg,var(--bg1),var(--bg2));border-bottom:1px solid var(--border);padding:24px 20px 20px;text-align:center;'>
      <div style='font-family:var(--font-display);font-size:1.15rem;font-weight:800;color:var(--fg0);letter-spacing:-0.02em;margin-bottom:4px;'>PADAYON!</div>
      <div style='font-family:var(--font-mono);font-size:0.55rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--fg2);'>UPCAT Agham + Matematika · 2026</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-title" style="margin:18px 0 10px;padding-left:12px;font-size:0.6rem;">🔑 API Config</div>', unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", help="aistudio.google.com — free")
    gemini_model = st.selectbox("Model", [
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview",
    ], index=0)

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">♿ Display</div>', unsafe_allow_html=True)
    font_size = st.select_slider("Text Size", options=["small","medium","large","x-large"], value=st.session_state.get('font_size','medium'))
    if font_size != st.session_state.get('font_size'):
        st.session_state['font_size'] = font_size; st.rerun()
    show_timer = st.checkbox("Show Countdown Timer", value=True)
    show_nav   = st.checkbox("Show Item Navigator", value=True)
    enable_flag= st.checkbox("Enable Item Flagging 🚩", value=True)

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">🏫 School Type</div>', unsafe_allow_html=True)
    jhs_type = st.selectbox("JHS School Type", list(SCHOOL_TIERS.keys()), index=5)
    shs_type = st.selectbox("SHS School Type", list(SCHOOL_TIERS.keys()), index=5)
    jhs_mod = SCHOOL_TIERS[jhs_type]["modifier"]
    shs_mod = SCHOOL_TIERS[shs_type]["modifier"]
    palugit_active = SCHOOL_TIERS[jhs_type]["palugit"] or SCHOOL_TIERS[shs_type]["palugit"]
    if palugit_active:
        st.caption(f"✅ Palugit: JHS {jhs_mod:+.2f} / SHS {shs_mod:+.2f}")

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">📐 Math Grades G8–G11</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        g8_math     = st.number_input("G8 Math",       60.0,100.0,87.0,0.5)
        g9_math     = st.number_input("G9 Math",       60.0,100.0,87.0,0.5)
        g10_math    = st.number_input("G10 Math",      60.0,100.0,88.0,0.5)
        g11_precalc = st.number_input("Pre-Calculus",  60.0,100.0,88.0,0.5)
    with c2:
        g11_calc    = st.number_input("Basic Calculus",60.0,100.0,87.0,0.5)
        g11_stats   = st.number_input("Stats & Prob",  60.0,100.0,88.0,0.5)
        g11_genmath = st.number_input("Gen. Math",     60.0,100.0,88.0,0.5)

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">🔬 Science Grades G8–G11</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        g8_sci   = st.number_input("G8 Science",  60.0,100.0,87.0,0.5)
        g9_sci   = st.number_input("G9 Science",  60.0,100.0,87.0,0.5)
        g10_sci  = st.number_input("G10 Science", 60.0,100.0,88.0,0.5)
        g11_bio1 = st.number_input("Gen Bio 1",   60.0,100.0,88.0,0.5)
    with c4:
        g11_bio2  = st.number_input("Gen Bio 2",  60.0,100.0,88.0,0.5)
        g11_earth = st.number_input("Earth Sci",  60.0,100.0,87.0,0.5)

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">🎯 Campus & Program Choices</div>', unsafe_allow_html=True)
    campus_1 = st.selectbox("1st Choice Campus", list(CAMPUS_DATA.keys()), index=0)
    c1_p1 = st.selectbox("Priority 1", get_all_programs(campus_1), key="c1p1")
    c1_p2 = st.selectbox("Priority 2", get_all_programs(campus_1), key="c1p2")
    c1_p3 = st.selectbox("Priority 3", get_all_programs(campus_1), key="c1p3")
    campus_2 = st.selectbox("2nd Choice Campus", list(CAMPUS_DATA.keys()), index=2)
    c2_p1 = st.selectbox("Priority 1", get_all_programs(campus_2), key="c2p1")
    c2_p2 = st.selectbox("Priority 2", get_all_programs(campus_2), key="c2p2")
    c2_p3 = st.selectbox("Priority 3", get_all_programs(campus_2), key="c2p3")

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">⚙️ Simulation Parameters</div>', unsafe_allow_html=True)
    math_items = st.slider("Math Items",    10, 50, 25, 5)
    sci_items  = st.slider("Science Items", 10, 45, 20, 5)
    difficulty = st.select_slider("Difficulty", options=["Standard","Competitive","Brutal","Massacre"], value="Competitive")

# ==========================================
# DIFFICULTY CONFIG
# ==========================================
DIFF_MAP = {
    "Standard":    ("Items solvable in under 60s. Test basic recall and single-step reasoning. ~50% of prepared applicants score above 60%.", 0.52, 0.16),
    "Competitive": ("Items require 2–4 steps. Test conceptual understanding over formula memorization. ~Top 20% ceiling.", 0.44, 0.15),
    "Brutal":      ("Items test deep conceptual knowledge. Multi-step reasoning, non-obvious entry points. ~Top 8% ceiling.", 0.37, 0.14),
    "Massacre":    ("Items appear simple but require precise logical reasoning. ~Top 2–3% ceiling. Zero items solvable by rote recall.", 0.31, 0.13),
}
diff_instruction, MEAN_BASELINE, SIGMA = DIFF_MAP[difficulty]

# ==========================================
# SVG CHART HELPERS
# ==========================================
def generate_bar_chart_svg(labels, values, title="", color="#4d9fff", width=500, height=260):
    if not labels or not values: return ""
    max_v = max(values) if max(values) > 0 else 1
    ml, mr, mt, mb = 55, 20, 38, 58
    cw = width - ml - mr
    ch = height - mt - mb
    bw = cw / len(values) * 0.65
    bg = cw / len(values)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="font-family:\'IBM Plex Mono\',monospace;background:#141d2e;border-radius:8px;">',
        f'<rect width="{width}" height="{height}" fill="#141d2e" rx="8"/>',
    ]
    if title:
        parts.append(f'<text x="{(width-mr)//2}" y="22" text-anchor="middle" fill="#9aaabb" font-size="11" font-weight="600">{title[:60]}</text>')
    for i in range(5):
        yv = max_v * i / 4
        yp = mt + ch - (yv / max_v * ch)
        parts.append(f'<line x1="{ml}" y1="{yp:.1f}" x2="{ml+cw}" y2="{yp:.1f}" stroke="#1a2540" stroke-width="1"/>')
        parts.append(f'<text x="{ml-5}" y="{yp+4:.1f}" text-anchor="end" fill="#5a6a7a" font-size="9">{yv:.2g}</text>')
    for i, (lbl, val) in enumerate(zip(labels, values)):
        bh = (val / max_v) * ch
        x  = ml + i * bg + (bg - bw) / 2
        y  = mt + ch - bh
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" opacity="0.85" rx="2"/>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{y-4:.1f}" text-anchor="middle" fill="#f0f4f8" font-size="9" font-weight="600">{val:.2g}</text>')
        lbl_s = str(lbl)[:10]
        parts.append(f'<text x="{x+bw/2:.1f}" y="{mt+ch+14:.1f}" text-anchor="middle" fill="#9aaabb" font-size="9" transform="rotate(-25,{x+bw/2:.1f},{mt+ch+14:.1f})">{lbl_s}</text>')
    parts.append('</svg>')
    return "".join(parts)

def generate_line_chart_svg(x_vals, y_series, title="", width=500, height=260):
    if not x_vals or not y_series: return ""
    colors = ["#4d9fff","#2dd4bf","#fbbf24","#f87171","#a78bfa"]
    all_y = [v for s in y_series.values() for v in s]
    mn, mx = (min(all_y) if all_y else 0), (max(all_y) if all_y else 1)
    if mx == mn: mx = mn + 1
    ml, mr, mt, mb = 55, 110, 38, 48
    cw = width - ml - mr
    ch = height - mt - mb
    n  = len(x_vals)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="font-family:\'IBM Plex Mono\',monospace;background:#141d2e;border-radius:8px;">',
        f'<rect width="{width}" height="{height}" fill="#141d2e" rx="8"/>',
    ]
    if title:
        parts.append(f'<text x="{(width-mr)//2}" y="22" text-anchor="middle" fill="#9aaabb" font-size="11" font-weight="600">{title[:60]}</text>')
    for i in range(5):
        yv = mn + (mx - mn) * i / 4
        yp = mt + ch - ((yv - mn) / (mx - mn) * ch)
        parts.append(f'<line x1="{ml}" y1="{yp:.1f}" x2="{ml+cw}" y2="{yp:.1f}" stroke="#1a2540" stroke-width="1"/>')
        parts.append(f'<text x="{ml-5}" y="{yp+4:.1f}" text-anchor="end" fill="#5a6a7a" font-size="9">{yv:.2g}</text>')
    for i, xv in enumerate(x_vals):
        xp = ml + i * cw / max(1, n - 1)
        parts.append(f'<text x="{xp:.1f}" y="{mt+ch+14:.1f}" text-anchor="middle" fill="#9aaabb" font-size="9">{str(xv)[:8]}</text>')
    for ci, (name, yvs) in enumerate(y_series.items()):
        clr = colors[ci % len(colors)]
        if len(yvs) < 1: continue
        pts = []
        for i, yv in enumerate(yvs):
            xp = ml + i * cw / max(1, n - 1)
            yp = mt + ch - ((yv - mn) / (mx - mn) * ch)
            pts.append(f"{xp:.1f},{yp:.1f}")
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{clr}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, yv in enumerate(yvs):
            xp = ml + i * cw / max(1, n - 1)
            yp = mt + ch - ((yv - mn) / (mx - mn) * ch)
            parts.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="3" fill="{clr}"/>')
        ly = mt + ci * 18
        parts.append(f'<rect x="{width-mr+6}" y="{ly}" width="10" height="10" fill="{clr}" rx="2"/>')
        parts.append(f'<text x="{width-mr+20}" y="{ly+9:.1f}" fill="#9aaabb" font-size="9">{name[:16]}</text>')
    parts.append('</svg>')
    return "".join(parts)

def build_svg_from_data(chart_data):
    if not chart_data or not isinstance(chart_data, dict): return ""
    t = chart_data.get("type", "bar")
    title = chart_data.get("title", "")
    try:
        if t == "bar":
            return generate_bar_chart_svg(chart_data.get("labels",[]), chart_data.get("values",[]), title, chart_data.get("color","#4d9fff"))
        elif t == "line":
            return generate_line_chart_svg(chart_data.get("x_values",[]), chart_data.get("y_series",{}), title)
    except Exception:
        pass
    return ""

# ==========================================
# JSON CLEANER — robust, math-safe
# ==========================================
# ==========================================
# JSON CLEANER & MARKDOWN SAFEGUARD
# ==========================================
def safe_md(text):
    """Protects Math backslashes from being eaten by Streamlit's parser"""
    if not text: return ""
    return str(text).replace('\\', '\\\\')

def clean_json(raw: str) -> str:
    s = raw.strip()
    # Remove markdown fences
    s = re.sub(r'^```(?:json)?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'```\s*$', '', s)
    s = s.strip()
    # Extract outermost JSON object
    first = s.find('{')
    last  = s.rfind('}')
    if first != -1 and last != -1:
        s = s[first:last+1]
    return s.strip()

# ==========================================
# PROMPT SYSTEM
# ==========================================
MATH_SYSTEM = """You are the chief UPCAT Mathematics item writer for UP Office of Admissions.
Generate items ONLY for the competencies explicitly listed.

STRICT LaTeX RULES (ZERO EXCEPTIONS):
- Every mathematical expression MUST be wrapped in LaTeX delimiters.
- Inline math: use single dollar signs: $x^2 + 3x = 4$
- Display math: use double dollar signs on their own line: $$\\frac{a+b}{c} = d$$
- Fractions: $\\frac{numerator}{denominator}$
- Square roots: $\\sqrt{x}$ or $\\sqrt[3]{x}$
- Exponents: $x^{2}$, $2^{10}$
- Subscripts: $x_{1}$, $a_{n}$
- Greek letters: $\\pi$, $\\theta$, $\\alpha$
- Set notation: $\\mathbb{Z}$, $\\mathbb{R}$, $\\mathbb{Q}$
- Absolute value: $|x|$
- Overline (repeating decimal): $0.\\overline{36}$
- All options with math MUST use LaTeX. Never write plain-text math like x^2 or sqrt(x).

PSYCHOMETRIC RULES:
- No calculator. All arithmetic solvable by hand in under 90 seconds.
- 4 options A/B/C/D. Correct answer distributed equally across A/B/C/D.
- Each wrong option represents a NAMED student error: SIGN_ERROR, ARITHMETIC_ERROR, FORMULA_CONFUSION, CONCEPTUAL_ERROR, or INCOMPLETE_SOLUTION.
- Options must be similar in length and form to avoid giveaways.
- Word problems: use Filipino contexts naturally.
- Full step-by-step solution required. Minimum 4 labeled steps.

OUTPUT: Return ONLY valid JSON. No markdown fences. No preamble. No trailing text."""

SCI_SYSTEM = """You are the chief UPCAT Science item writer for UP Office of Admissions.
Generate items ONLY for the competencies explicitly listed.

STIMULUS RULES:
- At least 60% of items must include a stimulus.
- TEXT_PASSAGE: 60–120 word scientific scenario.
- DATA_TABLE: Use clean HTML with this EXACT format:
  <table class="sci-tbl"><thead><tr><th>Col1</th><th>Col2</th></tr></thead><tbody><tr><td>val</td><td>val</td></tr></tbody></table>
  DO NOT add extra attributes. DO NOT wrap in any other tags.
- DIAGRAM: Text-based ASCII or labeled description of a biological/geological/physical diagram.
- For quantitative data items, include a "chart" field (optional).

PSYCHOMETRIC RULES:
- No pure memorization. Test APPLICATION and ANALYSIS.
- 4 options A/B/C/D.
- Each wrong option represents a named misconception: MISCONCEPTION, PARTIAL_TRUTH, REVERSED_CAUSATION, SCOPE_ERROR, or MAGNIFIED_DETAIL.
- LaTeX for chemical formulas: $H_2O$, $CO_2$, $O_2$.
- Full scientific explanation required. Minimum 4 sentences.

OUTPUT: Return ONLY valid JSON. No markdown fences. No preamble."""


def build_math_prompt(competencies: str, num_items: int, difficulty: str, diff_instr: str) -> str:
    lines = [l.strip() for l in competencies.strip().split('\n') if l.strip()]
    n = len(lines)
    base = max(1, num_items // max(1, n))
    rem  = num_items - base * n
    assign = "\n".join(
        f"  [{base + (1 if i < rem else 0)} item(s)] {c}"
        for i, c in enumerate(lines)
    )
    return f"""Generate exactly {num_items} UPCAT Mathematics items.

DIFFICULTY: {difficulty}
{diff_instr}

COMPETENCY ASSIGNMENT (generate items ONLY for these):
{assign}

Return this JSON structure with exactly {num_items} items:
{{
  "exam_metadata": {{"subtest":"Mathematics","total_items":{num_items},"difficulty":"{difficulty}","calculator_allowed":false}},
  "items": [
    {{
      "item_number": 1,
      "competency": "exact competency text",
      "topic": "short topic label",
      "subtopic": "specific concept",
      "grade_level_origin": "Grade 7/8/9/10/11",
      "question_text": "Full question. ALL math uses LaTeX: $inline$ or $$display$$.",
      "stimulus": null,
      "options": {{"A":"$LaTeX option$","B":"$LaTeX option$","C":"$LaTeX option$","D":"$LaTeX option$"}},
      "correct_answer": "C",
      "distractor_analysis": {{
        "A": {{"type":"SIGN_ERROR","error":"specific error description"}},
        "B": {{"type":"ARITHMETIC_ERROR","error":"specific error description"}},
        "D": {{"type":"INCOMPLETE_SOLUTION","error":"specific error description"}}
      }},
      "solution": "Step 1: ... Step 2: ... Step 3: ... Final answer: ...",
      "key_concept": "one-sentence core concept",
      "common_mistake": "most common student error on this item type"
    }}
  ]
}}"""


def build_sci_prompt(competencies: str, num_items: int, difficulty: str, diff_instr: str) -> str:
    lines = [l.strip() for l in competencies.strip().split('\n') if l.strip()]
    n = len(lines)
    base = max(1, num_items // max(1, n))
    rem  = num_items - base * n
    assign = "\n".join(
        f"  [{base + (1 if i < rem else 0)} item(s)] {c}"
        for i, c in enumerate(lines)
    )
    return f"""Generate exactly {num_items} UPCAT Science items.

DIFFICULTY: {difficulty}
{diff_instr}

COMPETENCY ASSIGNMENT (generate items ONLY for these):
{assign}

Return this JSON structure with exactly {num_items} items:
{{
  "exam_metadata": {{"subtest":"Science","total_items":{num_items},"difficulty":"{difficulty}"}},
  "items": [
    {{
      "item_number": 1,
      "competency": "exact competency text",
      "topic": "short topic label",
      "subtopic": "specific concept",
      "grade_level_origin": "Grade 8/9/10",
      "science_discipline": "Biology|Chemistry|Physics|Earth Science",
      "stimulus_type": "TEXT_PASSAGE|DATA_TABLE|DIAGRAM|null",
      "stimulus": "passage text OR html table OR null",
      "chart": null,
      "question_text": "Full question referencing stimulus data.",
      "options": {{"A":"option text","B":"option text","C":"option text","D":"option text"}},
      "correct_answer": "B",
      "distractor_analysis": {{
        "A": {{"type":"MISCONCEPTION","error":"specific misconception"}},
        "C": {{"type":"PARTIAL_TRUTH","error":"true but not from stimulus"}},
        "D": {{"type":"REVERSED_CAUSATION","error":"cause/effect inverted"}}
      }},
      "solution": "1. Key stimulus variable. 2. Scientific principle. 3. Why correct. 4. Why distractors fail.",
      "key_concept": "one-sentence core concept",
      "passage_reference": "exact data point from stimulus proving the answer"
    }}
  ]
}}"""


def post_process_items(items):
    """Clean up common AI formatting issues in items."""
    for q in items:
        # Fix correct_answer — must be a single uppercase letter
        ca = str(q.get('correct_answer', '')).strip().upper()
        q['correct_answer'] = ca[0] if ca and ca[0] in 'ABCD' else 'A'

        # Fix options — strip leading "A) " artifacts that sometimes appear
        for k in ['A','B','C','D']:
            opt = q.get('options', {}).get(k, '')
            if not isinstance(opt, str): opt = str(opt)
            # Remove patterns like "A) " or "A." from start of option text
            opt = re.sub(r'^[A-D][)\.]\s*', '', opt.strip())
            q['options'][k] = opt

        # Ensure question_text is a string
        if not isinstance(q.get('question_text'), str):
            q['question_text'] = str(q.get('question_text', ''))

    return items


def generate_subtest(model, system: str, user: str, name: str):
    response = model.generate_content(f"{system}\n\n{user}")
    raw = clean_json(response.text)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fix trailing commas, then retry
        fixed = re.sub(r',\s*([}\]])', r'\1', raw)
        data = json.loads(fixed)

    if 'items' not in data or not data['items']:
        raise ValueError(f"No items returned for {name}")

    data['items'] = post_process_items(data['items'])
    return data


def run_generation(do_math: bool, do_sci: bool):
    if not api_key:
        st.error("❌ Enter your Gemini API Key in the sidebar.")
        return
    mc = st.session_state.get('competencies_math','').strip()
    sc = st.session_state.get('competencies_sci','').strip()
    if do_math and not mc:
        st.error("❌ Enter Math competencies first."); return
    if do_sci and not sc:
        st.error("❌ Enter Science competencies first."); return

    prog = st.progress(0)
    status = st.empty()
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            gemini_model,
            generation_config={"response_mime_type":"application/json","temperature":0.75,"top_p":0.92,"max_output_tokens":32000}
        )
        new_data = dict(st.session_state.get('test_data') or {})

        if do_math:
            status.info("📐 Generating Mathematics items…")
            prog.progress(10)
            md = generate_subtest(model, MATH_SYSTEM, build_math_prompt(mc, math_items, difficulty, diff_instruction), "Math")
            new_data['math'] = md
            prog.progress(50)
            status.success(f"✅ Math: {len(md['items'])} items generated!")

        if do_sci:
            status.info("🔬 Generating Science items…")
            prog.progress(55 if do_math else 10)
            sd = generate_subtest(model, SCI_SYSTEM, build_sci_prompt(sc, sci_items, difficulty, diff_instruction), "Science")
            new_data['sci'] = sd
            prog.progress(96)
            status.success(f"✅ Science: {len(sd['items'])} items generated!")

        prog.progress(100)
        mc_ = len(new_data.get('math',{}).get('items',[]))
        sc_ = len(new_data.get('sci', {}).get('items',[]))
        status.success(f"🎉 Ready — Math: {mc_} · Science: {sc_} · {difficulty}")
        st.session_state.update({
            'test_data': new_data,
            'user_answers_math': {}, 'user_answers_sci': {},
            'flagged_items': set(), 'submitted': False,
            'math_start_time': None, 'sci_start_time': None,
            'elapsed_math': 0, 'elapsed_sci': 0,
        })
        time.sleep(0.6)
        st.rerun()
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON parse error — try Gemini 2.5 Pro. Detail: {str(e)[:300]}")
    except Exception as e:
        st.error(f"❌ {str(e)[:500]}")

# ==========================================
# HERO
# ==========================================
st.markdown("""
<div class="hero" role="banner">
  <div class="hero-glow-l"></div>
  <div class="hero-glow-r"></div>
  <div class="hero-inner">
    <div class="hero-eyebrow">🎓 UPCAT Elite Simulator · March 2026 Edition</div>
    <h1 class="hero-title">
      <span class="accent">Padayon!</span><br>
      <span class="accent2">Agham</span> at Matematika
    </h1>
    <p class="hero-sub">
      Research-grade psychometric simulation of the UPCAT Mathematics (50 items · 60 min · no calculator)
      and Science (45 items · 45 min · ~60% passage-based) subtests.
      Competency-locked: every question maps to <em>your</em> DepEd MELCs.
      135,000+ applicants. ~7.8% first-choice rate. Train smarter.
    </p>
    <div class="hero-rule"></div>
    <div class="hero-stats">
      <div><div class="hs-num">135k+</div><div class="hs-lbl">Applicants / Year</div></div>
      <div><div class="hs-num">7.8%</div><div class="hs-lbl">1st-Choice Rate</div></div>
      <div><div class="hs-num">50+45</div><div class="hs-lbl">Items (Full UPCAT)</div></div>
      <div><div class="hs-num">−0.25</div><div class="hs-lbl">Wrong Penalty (RMW)</div></div>
      <div><div class="hs-num">60%</div><div class="hs-lbl">Sci. Passage-Based</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
  <span class="ni">ℹ️</span>
  <div><strong>March 2026 Edition:</strong> Competency-locked generation — items generated
  <em>exclusively</em> from your provided DepEd MELCs. LaTeX renders via KaTeX (auto-render on DOM changes).
  Graphs auto-generated for quantitative Science items. UPG is a research model — not official UP methodology.</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# COMPETENCY INPUT
# ==========================================
st.markdown('<div class="sec-title">📋 Competency Input (Required)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="notice sci">
  <span class="ni">🔑</span>
  <div><strong>This simulator generates questions ONLY from competencies you provide.</strong>
  Paste DepEd MELCs (Most Essential Learning Competencies) below — one per line.
  Source from <em>curriculum.deped.gov.ph</em>, your textbook, or teacher's guide.
  The AI distributes items evenly across all competencies listed.</div>
</div>
""", unsafe_allow_html=True)

cc1, cc2 = st.columns(2)
with cc1:
    st.markdown('<div class="comp-wrap math"><div class="comp-head">🔢 Mathematics Competencies</div><div class="comp-sub">One competency per line · MELCs format recommended</div></div>', unsafe_allow_html=True)
    math_comp_val = st.text_area(
        "Math competencies", value=st.session_state.get('competencies_math',''),
        height=200, label_visibility="collapsed",
        placeholder="Paste competencies here, one per line:\n\nFactors completely different types of polynomials (M8AL-Ia-b-1)\nSolves rational algebraic expressions\nIllustrates quadratic inequalities\nSolves quadratic equations by factoring\nGraphs quadratic functions",
        key="math_comp_input"
    )
    st.session_state['competencies_math'] = math_comp_val
    mc_n = len([l for l in math_comp_val.strip().split('\n') if l.strip()])
    if mc_n > 0:
        st.caption(f"✅ {mc_n} competencies · {math_items} items → ~{max(1, math_items//mc_n)} items/competency")
    else:
        st.caption("⚠️ Enter at least 1 Math competency.")

with cc2:
    st.markdown('<div class="comp-wrap sci"><div class="comp-head">🔬 Science Competencies</div><div class="comp-sub">One per line · include discipline tag for clarity</div></div>', unsafe_allow_html=True)
    sci_comp_val = st.text_area(
        "Science competencies", value=st.session_state.get('competencies_sci',''),
        height=200, label_visibility="collapsed",
        placeholder="Paste competencies here, one per line:\n\n[Biology] Describe structure and functions of cell organelles\n[Biology] Explain mitosis and meiosis\n[Chemistry] Balance chemical equations\n[Physics] Apply Newton's Laws\n[Earth Science] Describe Earth's layers",
        key="sci_comp_input"
    )
    st.session_state['competencies_sci'] = sci_comp_val
    sc_n = len([l for l in sci_comp_val.strip().split('\n') if l.strip()])
    if sc_n > 0:
        st.caption(f"✅ {sc_n} competencies · {sci_items} items → ~{max(1, sci_items//sc_n)} items/competency")
    else:
        st.caption("⚠️ Enter at least 1 Science competency.")

# ==========================================
# GENERATE SECTION
# ==========================================
st.markdown('<div class="sec-title">🚀 Generate Simulation</div>', unsafe_allow_html=True)

time_m = max(10, int((math_items / 50) * 60))
time_s = max(10, int((sci_items  / 45) * 45))

gi1, gi2 = st.columns(2)
with gi1:
    st.markdown(f"""
    <div style='background:var(--bg1);border:1px solid var(--border2);border-top:2px solid var(--blue);border-radius:var(--r2);padding:16px 20px;'>
      <div style='font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--blue);margin-bottom:8px;'>🔢 Mathematics</div>
      <div style='font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--fg0);margin-bottom:6px;'>{math_items} Items · ~{time_m} min · No Calculator</div>
      <div style='font-family:var(--font-body);font-size:0.8rem;color:var(--fg1);line-height:1.7;'>
        72 s/item budget · Filipino contexts · Full KaTeX rendering · Items locked to your competencies only.
      </div>
    </div>""", unsafe_allow_html=True)
with gi2:
    st.markdown(f"""
    <div style='background:var(--bg1);border:1px solid var(--border2);border-top:2px solid var(--teal);border-radius:var(--r2);padding:16px 20px;'>
      <div style='font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--teal);margin-bottom:8px;'>🔬 Science</div>
      <div style='font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--fg0);margin-bottom:6px;'>{sci_items} Items · ~{time_s} min · Passage-Based</div>
      <div style='font-family:var(--font-body);font-size:0.8rem;color:var(--fg1);line-height:1.7;'>
        60 s/item budget · Data tables · Auto-generated charts · Items locked to your competencies only.
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
g1, g2, g3 = st.columns([2,1,1])
with g1: gen_both = st.button(f"🚀 Generate Both ({math_items + sci_items} Items)", type="primary", use_container_width=True)
with g2: gen_math = st.button(f"🔢 Math Only ({math_items})",  use_container_width=True)
with g3: gen_sci  = st.button(f"🔬 Science Only ({sci_items})", use_container_width=True)

if gen_both: run_generation(True, True)
elif gen_math: run_generation(True, False)
elif gen_sci:  run_generation(False, True)

# ==========================================
# EXAM INTERFACE
# ==========================================
if st.session_state.get('test_data') and not st.session_state.get('submitted'):
    test_data = st.session_state['test_data']
    math_data = test_data.get('math', {}).get('items', [])
    sci_data  = test_data.get('sci',  {}).get('items', [])
    flagged   = st.session_state.get('flagged_items', set())

    ans_m = len(st.session_state['user_answers_math'])
    ans_s = len(st.session_state['user_answers_sci'])
    tot_m, tot_s = len(math_data), len(sci_data)
    tot_all = tot_m + tot_s
    tot_ans = ans_m + ans_s
    pct_m = (ans_m / max(1, tot_m)) * 100
    pct_s = (ans_s / max(1, tot_s)) * 100

    # Progress bars
    if tot_m > 0 and tot_s > 0:
        pb1, pb2 = st.columns(2)
        with pb1:
            st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔢 MATH — {ans_m}/{tot_m}</span><span>{pct_m:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-m" style="width:{pct_m:.1f}%"></div></div></div>', unsafe_allow_html=True)
        with pb2:
            st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔬 SCIENCE — {ans_s}/{tot_s}</span><span>{pct_s:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-s" style="width:{pct_s:.1f}%"></div></div></div>', unsafe_allow_html=True)
    elif tot_m > 0:
        st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔢 MATH — {ans_m}/{tot_m}</span><span>{pct_m:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-m" style="width:{pct_m:.1f}%"></div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔬 SCIENCE — {ans_s}/{tot_s}</span><span>{pct_s:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-s" style="width:{pct_s:.1f}%"></div></div></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="notice warn">
      <span class="ni">⚠️</span>
      <div><strong>RMW Scoring:</strong> +1.00 correct · −0.25 wrong · 0.00 blank.
      Guess only when you can eliminate ≥2 options.
      Math: all computations by hand — no calculator.
      Science: read the stimulus <em>before</em> the question text.</div>
    </div>""", unsafe_allow_html=True)

    # Timer
    if show_timer:
        active = st.session_state.get('active_subtest','math')
        if   active == 'math' and st.session_state.get('math_start_time'):
            remaining = max(0, 3600 - int(time.time() - st.session_state['math_start_time']))
        elif active == 'sci'  and st.session_state.get('sci_start_time'):
            remaining = max(0, 2700 - int(time.time() - st.session_state['sci_start_time']))
        else:
            remaining = 3600 if active == 'math' else 2700
        lbl  = "🔬" if active == "sci" else "🔢"
        tcls = "s" if active == "sci" else ""
        st.components.v1.html(f"""
        <div id="tc" class="timer {tcls}">{lbl} <span id="tv">--:--</span></div>
        <style>
        .timer{{position:fixed;top:16px;right:20px;z-index:99999;font-family:'IBM Plex Mono',monospace;font-size:.9rem;font-weight:600;padding:8px 18px;border-radius:24px;border:1px solid rgba(77,159,255,.3);background:#0e1520;color:#4d9fff;letter-spacing:.06em;box-shadow:0 4px 16px rgba(0,0,0,.5);}}
        .timer.s{{color:#2dd4bf;border-color:rgba(45,212,191,.3);}}
        .timer.w{{color:#fbbf24;}}
        .timer.d{{color:#f87171;animation:pulse 1s infinite;}}
        @keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.6;}}}}
        </style>
        <script>
        (function(){{
          var tl={remaining};
          function tick(){{
            if(tl<0)tl=0;
            var m=Math.floor(tl/60),s=tl%60;
            var el=document.getElementById('tv'),box=document.getElementById('tc');
            if(el){{
              el.textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
              if(tl<=300&&tl>60)box.className='timer {tcls} w';
              if(tl<=60)box.className='timer {tcls} d';
              if(tl<=0)el.textContent='TIME UP';
            }}
            if(tl>0){{tl--;setTimeout(tick,1000);}}
          }}
          setTimeout(tick,300);
        }})();
        </script>
        """, height=0)

    # Build tabs
    tab_labels = []
    if math_data: tab_labels.append(f"🔢 Math ({tot_m} items · {ans_m} answered)")
    if sci_data:  tab_labels.append(f"🔬 Science ({tot_s} items · {ans_s} answered)")

    if len(tab_labels) == 2:
        tab_m, tab_s = st.tabs(tab_labels)
        render_pairs = [(tab_m,'math',math_data),(tab_s,'sci',sci_data)]
    elif len(tab_labels) == 1:
        only = st.tabs(tab_labels)[0]
        render_pairs = [(only, 'math' if math_data else 'sci', math_data or sci_data)]
    else:
        render_pairs = []

    def render_subtest(tab, key, items):
        with tab:
            if not items: return
            is_math  = key == 'math'
            ans_key  = f'user_answers_{key}'
            dot_ans  = 'am' if is_math else 'as'
            badge_cls= 'math' if is_math else 'sci'

            # Start timer on first view
            if not st.session_state.get(f'{key}_start_time'):
                st.session_state[f'{key}_start_time'] = time.time()
                st.session_state['active_subtest'] = key

            # Item navigator
            if show_nav:
                nav = f'<div class="nav-box"><div class="nav-title">{"Math" if is_math else "Science"} navigator — click to scroll</div><div class="nav-grid">'
                for q in items:
                    inum = q.get('item_number')
                    fkey = f"{key}_{inum}"
                    cls  = 'fl' if fkey in flagged else (dot_ans if inum in st.session_state[ans_key] else '')
                    nav += f'<div class="nav-dot {cls}" onclick="document.getElementById(\'{key}_{inum}\').scrollIntoView({{behavior:\'smooth\'}})">{inum}</div>'
                nav += '</div></div>'
                st.markdown(nav, unsafe_allow_html=True)

            for q in items:
                inum      = q.get('item_number')
                topic     = q.get('topic', '')
                grade_o   = q.get('grade_level_origin', '')
                qtext     = q.get('question_text', '')
                stimulus  = q.get('stimulus')
                stim_type = q.get('stimulus_type')
                chart_d   = q.get('chart')
                comp      = q.get('competency', '')
                disc      = q.get('science_discipline','')
                is_ans    = inum in st.session_state[ans_key]
                is_flg    = f"{key}_{inum}" in flagged

                card_cls = f"q-card{' sci' if not is_math else ''}{' answered' if is_ans else ''}{' flagged' if is_flg else ''}"

                # ── CARD HEADER (pure Python strings, no HTML that might leak) ──
                topic_s = topic[:28] + ('…' if len(topic) > 28 else '')
                comp_s  = comp[:45] + ('…' if len(comp) > 45 else '')

                # Build meta badges HTML carefully — escape any HTML in user-provided strings
                def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

                badge_html = f'<span class="q-badge {badge_cls}">{"MTH" if is_math else "SCI"} {inum:02d}</span>'
                if topic_s:
                    badge_html += f'<span class="q-badge tag" title="{esc(topic)}">{esc(topic_s)}</span>'
                if grade_o:
                    badge_html += f'<span class="q-badge tag">{esc(grade_o)}</span>'
                if disc and not is_math:
                    badge_html += f'<span class="q-badge tag">{esc(disc)}</span>'
                if comp_s:
                    badge_html += f'<span class="q-badge tag" title="{esc(comp)}" style="max-width:260px;overflow:hidden;text-overflow:ellipsis;">{esc(comp_s)}</span>'
                if is_flg:
                    badge_html += '<span class="q-badge flag">🚩 Flagged</span>'
                if is_ans:
                    badge_html += '<span class="q-badge ok">✅</span>'

                st.markdown(
                    f'<div class="{card_cls}" id="{key}_{inum}"><div class="q-meta">{badge_html}</div>',
                    unsafe_allow_html=True
                )

                # ── STIMULUS ──
                if stimulus:
                    stim_clean = str(stimulus)
                    if stim_type == "DATA_TABLE":
                        # Ensure table has proper class
                        stim_clean = re.sub(r'<table[^>]*>', '<table class="sci-tbl">', stim_clean)
                        st.markdown(
                            f'<div class="stim-data"><span class="stim-label d">📊 Data Table</span>{stim_clean}</div>',
                            unsafe_allow_html=True
                        )
                    elif stim_type == "DIAGRAM":
                        st.markdown(
                            f'<div class="stim-diagram"><span class="stim-label g">🔎 Diagram / Figure</span>{esc(stim_clean)}</div>',
                            unsafe_allow_html=True
                        )
                    else:  # TEXT_PASSAGE
                        st.markdown(
                            f'<div class="stim-passage"><span class="stim-label p">📄 Read carefully before answering</span>{stim_clean}</div>',
                            unsafe_allow_html=True
                        )

                # ── CHART ──
                if chart_d and isinstance(chart_d, dict):
                    try:
                        svg = build_svg_from_data(chart_d)
                        if svg:
                            st.markdown(f'<div class="chart-wrap">{svg}</div>', unsafe_allow_html=True)
                    except Exception:
                        pass

                # ── QUESTION TEXT — native Streamlit markdown for math ──
                st.markdown(safe_md(qtext))
                st.markdown('</div>', unsafe_allow_html=True)

                # ── OPTIONS — use st.radio, pass option text as plain string ──
                opts = q.get('options', {})
                choices =[
                    f"A)  {safe_md(opts.get('A',''))}",
                    f"B)  {safe_md(opts.get('B',''))}",
                    f"C)  {safe_md(opts.get('C',''))}",
                    f"D)  {safe_md(opts.get('D',''))}",
                ]
                choice = st.radio(
                    f"Q{key}{inum}",
                    choices,
                    key=f"{key}_r_{inum}",
                    index=None,
                    label_visibility="collapsed"
                )
                if choice:
                    # Extract the letter — always first char
                    st.session_state[ans_key][inum] = choice.strip()[0].upper()

                # ── FLAG BUTTON ──
                if enable_flag:
                    fkey = f"{key}_{inum}"
                    flbl = "🚩 Unflag" if fkey in flagged else "🚩 Flag for Review"
                    if st.button(flbl, key=f"fl_{key}_{inum}"):
                        if fkey in flagged: flagged.discard(fkey)
                        else: flagged.add(fkey)
                        st.session_state['flagged_items'] = flagged
                        st.rerun()

                st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:10px 0 14px;'>", unsafe_allow_html=True)

    for tab, key, items in render_pairs:
        render_subtest(tab, key, items)

    # ── SUBMIT ROW ──
    blank_cnt  = tot_all - tot_ans
    flagged_cnt= len(flagged)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill"><div class="sp-n" style="color:var(--green);">{tot_ans}</div><div class="sp-l">Answered</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--amber);">{flagged_cnt}</div><div class="sp-l">Flagged</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{blank_cnt}</div><div class="sp-l">Blank (0 pts)</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--blue);">{tot_all}</div><div class="sp-l">Total Items</div></div>
    </div>""", unsafe_allow_html=True)

    s1, s2, s3 = st.columns([1,2,1])
    with s2:
        if blank_cnt > 0:
            st.warning(f"⚠️ {blank_cnt} unanswered — scored 0. Guess only if you can eliminate ≥2 options.")
        if flagged_cnt > 0:
            st.info(f"🚩 {flagged_cnt} flagged for review.")
        if st.button("📥 Submit & View Full UPG Report", type="primary", use_container_width=True):
            st.session_state['submitted'] = True
            if st.session_state.get('math_start_time'):
                st.session_state['elapsed_math'] = time.time() - st.session_state['math_start_time']
            if st.session_state.get('sci_start_time'):
                st.session_state['elapsed_sci']  = time.time() - st.session_state['sci_start_time']
            st.rerun()

# ==========================================
# RESULTS ENGINE
# ==========================================
if st.session_state.get('submitted') and st.session_state.get('test_data'):
    st.balloons()
    test_data    = st.session_state['test_data']
    u_math       = st.session_state.get('user_answers_math', {})
    u_sci        = st.session_state.get('user_answers_sci',  {})
    elapsed_math = st.session_state.get('elapsed_math', 0)
    elapsed_sci  = st.session_state.get('elapsed_sci',  0)
    math_data    = test_data.get('math',{}).get('items',[])
    sci_data     = test_data.get('sci', {}).get('items',[])

    def score(items, user_ans):
        total   = len(items)
        correct = sum(1 for q in items if user_ans.get(q['item_number']) == q.get('correct_answer'))
        answered= sum(1 for v in user_ans.values() if v)
        wrong   = answered - correct
        blank   = total - answered
        raw     = max(0.0, correct - 0.25 * wrong)
        pct     = raw / max(1, total)
        return total, correct, wrong, blank, raw, pct

    if math_data: m_tot,m_cor,m_wro,m_bla,m_raw,m_pct = score(math_data, u_math)
    else:         m_tot,m_cor,m_wro,m_bla,m_raw,m_pct = 0,0,0,0,0.0,0.0
    if sci_data:  s_tot,s_cor,s_wro,s_bla,s_raw,s_pct = score(sci_data,  u_sci)
    else:         s_tot,s_cor,s_wro,s_bla,s_raw,s_pct = 0,0,0,0,0.0,0.0

    math_grades = [g8_math, g9_math, g10_math, g11_precalc, g11_calc, g11_stats, g11_genmath]
    sci_grades  = [g8_sci,  g9_sci,  g10_sci,  g11_bio1,    g11_bio2, g11_earth]
    m_gav = float(np.mean(math_grades))
    s_gav = float(np.mean(sci_grades))
    a_gav = float(np.mean(math_grades + sci_grades))
    avg_mod = (jhs_mod + shs_mod) / 2

    def g2upg(avg, mod):
        return max(1.0, min(5.0, 5.0 - ((avg - 75) / 25) * 4.0 - mod))

    mg_upg = g2upg(m_gav, avg_mod)
    sg_upg = g2upg(s_gav, avg_mod)
    ag_upg = g2upg(a_gav, avg_mod)

    def upcat2upg(pct):
        z = (pct - MEAN_BASELINE) / SIGMA
        return max(1.0, min(5.0, 2.75 - z * 0.55)), z

    if math_data: mu_upg, mz = upcat2upg(m_pct)
    else:         mu_upg, mz = ag_upg, 0.0
    if sci_data:  su_upg, sz = upcat2upg(s_pct)
    else:         su_upg, sz = ag_upg, 0.0

    mf_upg = 0.40 * mg_upg + 0.60 * mu_upg
    sf_upg = 0.40 * sg_upg + 0.60 * su_upg

    if math_data and sci_data:
        comb_pct = (m_pct + s_pct) / 2
        ou_upg, cz = upcat2upg(comb_pct)
        final_upg  = 0.40 * ag_upg + 0.60 * ou_upg
    elif math_data:
        comb_pct, ou_upg, cz, final_upg = m_pct, mu_upg, mz, mf_upg
    else:
        comb_pct, ou_upg, cz, final_upg = s_pct, su_upg, sz, sf_upg

    op = max(0.001, min(0.9999, 0.5 * (1 + math.erf(cz / math.sqrt(2)))))
    sim_rank = int(135000 - 135000 * op)

    if   final_upg <= 1.50: verdict = "🏆 Elite — Top tier across all UP campuses."
    elif final_upg <= 2.00: verdict = "✅ Very Strong — Likely qualifies for multiple programs."
    elif final_upg <= 2.30: verdict = "📘 Competitive — Within range for several programs."
    elif final_upg <= 2.60: verdict = "🟡 Borderline — May qualify at less competitive campuses."
    elif final_upg <= 3.00: verdict = "🟠 Below Threshold — Focused improvement needed."
    else:                    verdict = "🔴 Not Yet Ready — Focus on fundamentals first."

    def analyze_topics(items, user_ans):
        td = {}
        for q in items:
            key = q.get('competency', q.get('topic','Unknown'))
            key = (key[:38]+'…') if len(key) > 38 else key
            inum= q.get('item_number')
            ok  = user_ans.get(inum) == q.get('correct_answer')
            if key not in td: td[key] = {'correct':0,'total':0}
            td[key]['total'] += 1
            if ok: td[key]['correct'] += 1
        return td

    mt = analyze_topics(math_data, u_math) if math_data else {}
    st_ = analyze_topics(sci_data,  u_sci)  if sci_data  else {}

    # Results hero
    upg_color = "#4d9fff" if final_upg <= 2.3 else ("#fbbf24" if final_upg <= 2.8 else "#f87171")
    st.markdown(f"""
    <div class="res-hero">
      <div class="res-hero-glow"></div>
      <div class="upg-label">University Predicted Grade (UPG) · {difficulty} Difficulty</div>
      <div class="upg-val" style="color:{upg_color};">{final_upg:.3f}</div>
      <div class="upg-verdict">{verdict}</div>
      <div style="color:rgba(255,255,255,0.25);font-family:var(--font-mono);font-size:0.58rem;margin-top:12px;letter-spacing:0.1em;position:relative;z-index:1;">
        Scale: 1.000 (highest) → 5.000 (lowest) · Simulated rank #{sim_rank:,} of 135,000 · Top {100*(1-op):.1f}th percentile
      </div>
    </div>""", unsafe_allow_html=True)

    # Subject UPG Cards
    st.markdown('<div class="sec-title">📊 Subject UPG Breakdown</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="upg-cards">
      <div class="upg-card m">
        <div class="upg-card-title">🔢 Mathematics UPG</div>
        <div class="upg-card-val">{mf_upg:.3f}</div>
        <div class="upg-card-sub">{"✅ Strong" if mf_upg<=2.3 else "⚠️ Needs improvement" if mf_upg<=2.8 else "❌ Significant gaps"}</div>
        <div class="upg-br">
          <div class="upg-br-row"><span class="upg-br-lbl">Math Grade Avg</span><span class="upg-br-val" style="color:var(--blue);">{m_gav:.1f}/100</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Grade UPG (40%)</span><span class="upg-br-val">{mg_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT RMW Score</span><span class="upg-br-val" style="color:var(--blue);">{m_pct*100:.1f}%</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT UPG (60%)</span><span class="upg-br-val">{mu_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Z-score</span><span class="upg-br-val">{mz:+.2f}σ</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">C / W / B</span><span class="upg-br-val">{m_cor}C · {m_wro}W · {m_bla}B</span></div>
        </div>
      </div>
      <div class="upg-card s">
        <div class="upg-card-title">🔬 Science UPG</div>
        <div class="upg-card-val">{sf_upg:.3f}</div>
        <div class="upg-card-sub">{"✅ Strong" if sf_upg<=2.3 else "⚠️ Needs improvement" if sf_upg<=2.8 else "❌ Significant gaps"}</div>
        <div class="upg-br">
          <div class="upg-br-row"><span class="upg-br-lbl">Science Grade Avg</span><span class="upg-br-val" style="color:var(--teal);">{s_gav:.1f}/100</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Grade UPG (40%)</span><span class="upg-br-val">{sg_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT RMW Score</span><span class="upg-br-val" style="color:var(--teal);">{s_pct*100:.1f}%</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT UPG (60%)</span><span class="upg-br-val">{su_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Z-score</span><span class="upg-br-val">{sz:+.2f}σ</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">C / W / B</span><span class="upg-br-val">{s_cor}C · {s_wro}W · {s_bla}B</span></div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Metric tiles
    penalty = (m_wro + s_wro) * 0.25
    metrics = [
        (f"{final_upg:.3f}", upg_color, "Overall UPG", "Lower = Better"),
        (f"#{sim_rank:,}", "var(--teal)", "Sim. Rank", f"Top {100*(1-op):.1f}%"),
        (f"{ag_upg:.3f}", "var(--green)", "Grades UPG", f"Avg: {a_gav:.1f}/100"),
        (f"{ou_upg:.3f}", "var(--amber)" if ou_upg > 2.5 else "var(--green)", "UPCAT UPG", f"Z: {cz:+.2f}"),
    ]
    if math_data: metrics.append((f"{m_pct*100:.1f}%", "var(--blue)", "Math Score", f"RMW: {m_raw:.2f}/{m_tot}"))
    if sci_data:  metrics.append((f"{s_pct*100:.1f}%", "var(--teal)", "Sci. Score", f"RMW: {s_raw:.2f}/{s_tot}"))
    cols_m = st.columns(min(len(metrics), 4))
    for i,(val,clr,lbl,sub) in enumerate(metrics):
        with cols_m[i % 4]:
            st.metric(label=lbl, value=val, delta=sub)

    # Score panels
    st.markdown("<br>", unsafe_allow_html=True)
    panel_keys = [k for k in ['math','sci'] if (math_data if k=='math' else sci_data)]
    pcols = st.columns(len(panel_keys)) if panel_keys else []
    for ci, pk in enumerate(panel_keys):
        with pcols[ci]:
            if pk == 'math':
                em,ems = int(elapsed_math//60),int(elapsed_math%60)
                bud = 72 * m_tot
                st.markdown(f"""
                <div class="score-panel"><h4>🔢 Mathematics</h4>
                  <div class="s-row"><span class="s-lbl">Correct</span><span class="s-val c">{m_cor}/{m_tot}</span></div>
                  <div class="s-row"><span class="s-lbl">Wrong (−0.25 each)</span><span class="s-val w">{m_wro} · −{m_wro*0.25:.2f} pts</span></div>
                  <div class="s-row"><span class="s-lbl">Blank (0 pts)</span><span class="s-val">{m_bla}</span></div>
                  <div class="s-row"><span class="s-lbl">RMW Score</span><span class="s-val g">{m_raw:.2f}/{m_tot}</span></div>
                  <div class="s-row"><span class="s-lbl">Percentage</span><span class="s-val g">{m_pct*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Accuracy on Attempted</span><span class="s-val">{m_cor/max(1,m_cor+m_wro)*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Time Used</span><span class="s-val">{em}m {ems}s · {elapsed_math/max(1,m_tot):.0f}s/item</span></div>
                  <div class="s-row"><span class="s-lbl">Budget Status</span><span class="s-val {"c" if elapsed_math<=bud else "w"}">{"✅ On budget" if elapsed_math<=bud else "⚠️ Over budget"}</span></div>
                </div>""", unsafe_allow_html=True)
            else:
                es,ess = int(elapsed_sci//60),int(elapsed_sci%60)
                bud = 60 * s_tot
                st.markdown(f"""
                <div class="score-panel"><h4>🔬 Science</h4>
                  <div class="s-row"><span class="s-lbl">Correct</span><span class="s-val c">{s_cor}/{s_tot}</span></div>
                  <div class="s-row"><span class="s-lbl">Wrong (−0.25 each)</span><span class="s-val w">{s_wro} · −{s_wro*0.25:.2f} pts</span></div>
                  <div class="s-row"><span class="s-lbl">Blank (0 pts)</span><span class="s-val">{s_bla}</span></div>
                  <div class="s-row"><span class="s-lbl">RMW Score</span><span class="s-val g">{s_raw:.2f}/{s_tot}</span></div>
                  <div class="s-row"><span class="s-lbl">Percentage</span><span class="s-val g">{s_pct*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Accuracy on Attempted</span><span class="s-val">{s_cor/max(1,s_cor+s_wro)*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Time Used</span><span class="s-val">{es}m {ess}s · {elapsed_sci/max(1,s_tot):.0f}s/item</span></div>
                  <div class="s-row"><span class="s-lbl">Budget Status</span><span class="s-val {"c" if elapsed_sci<=bud else "w"}">{"✅ On budget" if elapsed_sci<=bud else "⚠️ Over budget"}</span></div>
                </div>""", unsafe_allow_html=True)

    # Heatmaps
    heat_pairs = [(k, mt if k=='math' else st_) for k in ['math','sci'] if (mt if k=='math' else st_)]
    if heat_pairs:
        st.markdown('<div class="sec-title">🔥 Competency Mastery Heatmap</div>', unsafe_allow_html=True)
        hcols = st.columns(len(heat_pairs))
        for hi,(hk,td) in enumerate(heat_pairs):
            clr = "var(--blue)" if hk=='math' else "var(--teal)"
            with hcols[hi]:
                st.markdown(f"<h4 style='font-family:var(--font-display);font-size:0.9rem;color:{clr};margin-bottom:10px;'>{'🔢 Math' if hk=='math' else '🔬 Science'} Mastery</h4>", unsafe_allow_html=True)
                rows = sorted(td.items(), key=lambda x: x[1]['correct']/max(1,x[1]['total']))
                html = "<div class='heat-grid'>"
                for sk,d in rows:
                    p    = d['correct']/max(1,d['total'])*100
                    bc   = "hi" if p>=70 else ("mid" if p>=40 else "lo")
                    pc   = "var(--green)" if bc=="hi" else ("var(--amber)" if bc=="mid" else "var(--red)")
                    sk_s = (sk[:32]+'…') if len(sk)>32 else sk
                    html += f'<div class="heat-row" title="{sk}"><span style="flex:1;color:var(--fg1);font-size:0.73rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{sk_s}</span><div class="heat-bar-out"><div class="heat-bar-in {bc}" style="width:{p:.0f}%;"></div></div><span class="heat-pct" style="color:{pc};">{p:.0f}%</span></div>'
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)

    # Admission engine
    st.markdown('<div class="sec-title">🏛️ UP Admission Decision Engine</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="notice">
      <span class="ni">📊</span>
      <div><strong>UPCAT 2025:</strong> 17,996 of 135,236 applicants qualified (13.3% total).
      Your simulated UPG <strong>{final_upg:.3f}</strong> → rank <strong>#{sim_rank:,}</strong>.
      Admission: campus-qualified first, then program-specific slots within campus.</div>
    </div>""", unsafe_allow_html=True)

    def eval_prog(campus, prog, cutoff, upg):
        tier = get_program_tier(campus, prog)
        adj  = {"Triple Quota":-0.40,"Double Quota":-0.22,"Single Quota":-0.06,"Less Popular":+0.08}.get(tier,0)
        req  = max(1.1, cutoff + adj)
        if   upg <= req:       return "<span class='badge pass'>✅ PASSED</span>", req, tier
        elif upg <= req + 0.14:return "<span class='badge risk'>🟡 DPWAS RISK</span>", req, tier
        else:                  return "<span class='badge fail'>❌ BELOW CUTOFF</span>", req, tier

    ac1, ac2 = st.columns(2)
    for acol, campus, progs, cn in [(ac1,campus_1,[c1_p1,c1_p2,c1_p3],"1st"),(ac2,campus_2,[c2_p1,c2_p2,c2_p3],"2nd")]:
        cutoff = CAMPUS_DATA[campus]["cutoff"]
        q      = final_upg <= cutoff
        with acol:
            st.markdown(f"""
            <div class="campus-card">
              <div class="campus-hdr {"" if q else "fail"}">
                <h4>{cn} — {campus}</h4>
                <p>Cutoff: {cutoff:.3f} · Your UPG: {final_upg:.3f} · {"✅ QUALIFIED" if q else "❌ NOT QUALIFIED"} · {CAMPUS_DATA[campus]["note"]}</p>
              </div>
              <div class="campus-body">""", unsafe_allow_html=True)
            if campus==campus_2 and final_upg<=CAMPUS_DATA[campus_1]["cutoff"]:
                st.info("📌 Qualified at 1st campus — 2nd is void in cascading system.")
            if q:
                for i, prog in enumerate(progs,1):
                    badge,req,tier = eval_prog(campus, prog, cutoff, final_upg)
                    st.markdown(f'<div class="prog-row"><div><div class="prog-name">P{i}: {prog}</div><div class="prog-sub">{tier} · eff. cutoff ~{req:.3f}</div></div><div>{badge}</div></div>', unsafe_allow_html=True)
            else:
                recon = CAMPUS_DATA[campus]["recon"]
                rok   = recon > 0 and final_upg <= recon
                st.markdown(f'<div style="padding:14px;text-align:center;font-family:var(--font-body);font-size:0.85rem;color:var(--fg1);">UPG {final_upg:.3f} exceeds cutoff {cutoff:.3f}.<br><br>Recon window: <strong>{f"{recon:.3f}" if recon>0 else "None"}</strong><br>{"✅ Recon-eligible" if rok else ("❌ Beyond recon range" if recon>0 else "🚫 No appeals policy")}</div>', unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

    # Deep review tabs
    st.markdown('<div class="sec-title">🔬 Detailed Review & Analytics</div>', unsafe_allow_html=True)

    tab_lbls = ["📊 Overview", "🧮 UPG Formula"]
    if math_data: tab_lbls.append("🔢 Math Review")
    if sci_data:  tab_lbls.append("🔬 Science Review")
    tab_lbls.append("⚖️ Recon & DPWAS")
    tabs_r = st.tabs(tab_lbls)
    ti = 0

    # Overview
    with tabs_r[ti]:
        gr = (m_wro+s_wro)/max(1,m_cor+m_wro+s_cor+s_wro)
        me = {k:(1-v['correct']/max(1,v['total']))*100 for k,v in mt.items()}
        se = {k:(1-v['correct']/max(1,v['total']))*100 for k,v in st_.items()}
        top_m = sorted(me.items(),key=lambda x:-x[1])[:5]
        top_s = sorted(se.items(),key=lambda x:-x[1])[:5]
        st.markdown(f"""
        <div class="notice green">
          <span class="ni">📊</span>
          <div>
            <strong>Performance Summary — {difficulty}</strong><br>
            Rank <strong>#{sim_rank:,}</strong> of 135,000 · {op*100:.1f}th percentile ·
            Combined UPCAT: <strong>{comb_pct*100:.1f}%</strong> (mean {MEAN_BASELINE*100:.0f}%, σ={SIGMA:.2f}) ·
            Z: <strong>{cz:+.2f}</strong> · Total penalty: <strong>−{penalty:.2f} pts</strong>
            {" · ✅ Efficient guessing." if gr<0.22 else " · ⚠️ Moderate over-guessing." if gr<0.38 else " · 🔴 Aggressive guessing hurting score."}
          </div>
        </div>""", unsafe_allow_html=True)
        if top_m:
            st.markdown('<div class="notice warn"><span class="ni">🔢</span><div><strong>Math Weak Areas:</strong><br>' + "<br>".join(f"• {k} — {e:.0f}% error" for k,e in top_m) + '</div></div>', unsafe_allow_html=True)
        if top_s:
            st.markdown('<div class="notice sci"><span class="ni">🔬</span><div><strong>Science Weak Areas:</strong><br>' + "<br>".join(f"• {k} — {e:.0f}% error" for k,e in top_s) + '</div></div>', unsafe_allow_html=True)
    ti += 1

    # UPG Formula
    with tabs_r[ti]:
        st.markdown("#### 🧮 UPG Derivation")
        if math_data:
            with st.expander("📐 Math UPG — Full Derivation"):
                st.latex(f"\\text{{RMW}}_{{\\text{{Math}}}} = {m_cor} - \\tfrac{{1}}{{4}} \\times {m_wro} = {m_raw:.2f}")
                st.latex(f"Z_{{\\text{{Math}}}} = \\frac{{{m_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {mz:.4f}")
                st.latex(f"UPG_{{\\text{{UPCAT,Math}}}} = 2.75 - ({mz:.4f} \\times 0.55) = {mu_upg:.3f}")
                st.latex(f"UPG_{{\\text{{Math}}}} = 0.40 \\times {mg_upg:.3f} + 0.60 \\times {mu_upg:.3f} = {mf_upg:.3f}")
        if sci_data:
            with st.expander("📐 Science UPG — Full Derivation"):
                st.latex(f"\\text{{RMW}}_{{\\text{{Sci}}}} = {s_cor} - \\tfrac{{1}}{{4}} \\times {s_wro} = {s_raw:.2f}")
                st.latex(f"Z_{{\\text{{Sci}}}} = \\frac{{{s_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {sz:.4f}")
                st.latex(f"UPG_{{\\text{{Sci}}}} = 0.40 \\times {sg_upg:.3f} + 0.60 \\times {su_upg:.3f} = {sf_upg:.3f}")
        with st.expander("📐 Overall UPG"):
            st.latex(f"\\text{{Final UPG}} = 0.40 \\times {ag_upg:.3f} + 0.60 \\times {ou_upg:.3f} = {final_upg:.3f}")
        with st.expander("📐 Grade UPG Formula"):
            st.latex(r"UPG_{\text{grade}} = 5.0 - \left(\frac{\bar{G} - 75}{25}\right) \times 4.0 - \Delta_{\text{school}}")
            st.markdown(f"Combined avg: **{a_gav:.2f}** · School modifier: **{avg_mod:+.3f}** · Palugit: **{'Active' if palugit_active else 'Not Active'}**")
    ti += 1

    # Math Review
    if math_data:
        with tabs_r[ti]:
            st.markdown("### 🔢 Math — Item-by-Item Review")
            mw = [q for q in math_data if u_math.get(q['item_number']) not in [None,''] and u_math.get(q['item_number']) != q.get('correct_answer')]
            mc_ = [q for q in math_data if u_math.get(q['item_number']) == q.get('correct_answer')]
            mb  = [q for q in math_data if not u_math.get(q['item_number'])]
            st.markdown(f'<div class="stat-row"><div class="stat-pill"><div class="sp-n" style="color:var(--red);">{len(mw)}</div><div class="sp-l">Wrong</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--green);">{len(mc_)}</div><div class="sp-l">Correct</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{len(mb)}</div><div class="sp-l">Blank</div></div></div>', unsafe_allow_html=True)
            for lbl, subset, show_sol in [
                (f"❌ Wrong ({len(mw)}) — Priority Review", mw, True),
                (f"✅ Correct ({len(mc_)})", mc_, False),
                (f"⚪ Skipped ({len(mb)})", mb, True),
            ]:
                if not subset: continue
                st.markdown(f"#### {lbl}")
                for q in subset:
                    inum = q['item_number']
                    u    = u_math.get(inum)
                    c    = q.get('correct_answer')
                    comp = q.get('competency', q.get('topic',''))[:55]
                    ss   = f"Chose {u} → Correct: {c}" if u and u!=c else ("✅ Correct" if u==c else "⚪ Skipped")
                    with st.expander(f"MTH {inum:02d} · {comp} · {ss}"):
                      # Question with native LaTeX
                        st.markdown(f"**Question:**\n\n{safe_md(q.get('question_text',''))}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {safe_md(opts.get(lt,''))}"
                            if lt == c:
                                st.markdown(f'<div class="ir-c">{txt}</div>', unsafe_allow_html=True)
                            elif lt == u:
                                st.markdown(f'<div class="ir-w">{txt} ← Your answer</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="ir-o">{txt}</div>', unsafe_allow_html=True)
                        da = q.get('distractor_analysis', {})
                        if da and u and u in da and u != c:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Error type ({err.get('type','')}):** {err.get('error','')}")
                            else:
                                st.warning(str(err))
                        if show_sol or u == c:
                            sol = q.get('solution','')
                            if sol: st.info(f"**📐 Solution:**\n\n{safe_md(sol)}")
                            kc = q.get('key_concept','')
                            if kc: st.caption(f"💡 {kc}")
                            cm = q.get('common_mistake','')
                            if cm: st.caption(f"⚠️ Common mistake: {cm}")
        ti += 1

    # Science Review
    if sci_data:
        with tabs_r[ti]:
            st.markdown("### 🔬 Science — Item-by-Item Review")
            sw = [q for q in sci_data if u_sci.get(q['item_number']) not in [None,''] and u_sci.get(q['item_number']) != q.get('correct_answer')]
            sc_ = [q for q in sci_data if u_sci.get(q['item_number']) == q.get('correct_answer')]
            sb  = [q for q in sci_data if not u_sci.get(q['item_number'])]
            st.markdown(f'<div class="stat-row"><div class="stat-pill"><div class="sp-n" style="color:var(--red);">{len(sw)}</div><div class="sp-l">Wrong</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--green);">{len(sc_)}</div><div class="sp-l">Correct</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{len(sb)}</div><div class="sp-l">Blank</div></div></div>', unsafe_allow_html=True)
            for lbl, subset, show_sol in [
                (f"❌ Wrong ({len(sw)}) — Priority Review", sw, True),
                (f"✅ Correct ({len(sc_)})", sc_, False),
                (f"⚪ Skipped ({len(sb)})", sb, True),
            ]:
                if not subset: continue
                st.markdown(f"#### {lbl}")
                for q in subset:
                    inum = q['item_number']
                    u    = u_sci.get(inum)
                    c    = q.get('correct_answer')
                    comp = q.get('competency', q.get('topic',''))[:50]
                    disc = q.get('science_discipline','')
                    ss   = f"Chose {u} → Correct: {c}" if u and u!=c else ("✅ Correct" if u==c else "⚪ Skipped")
                    with st.expander(f"SCI {inum:02d} · {comp} [{disc}] · {ss}"):
                        stim = q.get('stimulus','')
                        if stim:
                            st_type = q.get('stimulus_type','')
                            if st_type == "DATA_TABLE":
                                clean_tbl = re.sub(r'<table[^>]*>','<table class="sci-tbl">',str(stim))
                                st.markdown(f'<div class="stim-data">{clean_tbl}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="stim-passage">{stim}</div>', unsafe_allow_html=True)
                        cd = q.get('chart')
                        if cd and isinstance(cd, dict):
                            try:
                                svg = build_svg_from_data(cd)
                                if svg: st.markdown(f'<div class="chart-wrap">{svg}</div>', unsafe_allow_html=True)
                            except Exception: pass
                       st.markdown(f"**Question:**\n\n{safe_md(q.get('question_text',''))}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {safe_md(opts.get(lt,''))}"
                            if lt == c:
                                st.markdown(f'<div class="ir-c">{txt}</div>', unsafe_allow_html=True)
                            elif lt == u:
                                st.markdown(f'<div class="ir-w">{txt} ← Your answer</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="ir-o">{txt}</div>', unsafe_allow_html=True)
                        da = q.get('distractor_analysis', {})
                        if da and u and u in da and u != c:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Why {u} is wrong ({err.get('type','')}):** {err.get('error','')}")
                        if show_sol or u == c:
                            sol = q.get('solution','')
                            if sol: st.info(f"**🔬 Explanation:**\n\n{safe_md(sol)}")
                            pr = q.get('passage_reference','')
                            if pr: st.caption(f"📍 Key evidence: {pr}")
                            kc = q.get('key_concept','')
                            if kc: st.caption(f"💡 {kc}")
        ti += 1

    # Recon
    with tabs_r[ti]:
        st.markdown("### ⚖️ DPWAS, Reconsideration & Cascading Admission")
        st.markdown(f"""
        <div class="notice">
          <span class="ni">📋</span>
          <div>
            <strong>UPCAT 2025:</strong> 17,996 of 135,236 applicants received admission notices (13.3%).
            ~10,600 were direct program-qualifiers (~7.8%). ~7,400 were DPWAS waitlisted.
            DPWAS is <em>not</em> rejection — slots open as accepted students decline, shift, or fail to enroll.
            Your rank <strong>#{sim_rank:,}</strong>.
          </div>
        </div>""", unsafe_allow_html=True)
        for campus in [campus_1, campus_2]:
            recon  = CAMPUS_DATA[campus]["recon"]
            cutoff = CAMPUS_DATA[campus]["cutoff"]
            st.markdown(f"**{campus}** — Cutoff: `{cutoff:.3f}` · Recon ceiling: `{f'{recon:.3f}' if recon > 0 else 'N/A'}`")
            if recon == 0.0:
                st.error(f"🚫 {campus}: Absolute no-appeal policy.")
            elif final_upg <= cutoff:
                st.success(f"✅ Already qualified ({final_upg:.3f} ≤ {cutoff:.3f}).")
            elif final_upg <= recon:
                st.warning(f"📋 Recon-eligible: UPG {final_upg:.3f} within window ({cutoff:.3f}–{recon:.3f}). Not guaranteed.")
            else:
                st.error(f"❌ UPG {final_upg:.3f} exceeds recon ceiling {recon:.3f}.")

    # Reset
    st.markdown("<br><br>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns([1,2,1])
    with r2:
        st.markdown('<div style="text-align:center;font-family:var(--font-body);font-size:0.8rem;color:var(--fg2);margin-bottom:10px;">Generate a fresh set — competencies and settings preserved.</div>', unsafe_allow_html=True)
        if st.button("🔄 Generate Fresh Items & Reset", use_container_width=True, type="secondary"):
            for k in ['user_answers_math','user_answers_sci','submitted','test_data','flagged_items','math_start_time','sci_start_time','elapsed_math','elapsed_sci']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
