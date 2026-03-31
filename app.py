import streamlit as st
import google.generativeai as genai
import json
import time
import math
import numpy as np
import re
import base64
import io

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
    'generation_log': [],
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
# CSS — March 2026 Edition
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;0,700;1,400;1,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

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
  --fg3: #2e3d50;

  --border: rgba(255,255,255,0.06);
  --border2: rgba(255,255,255,0.12);

  --r: 8px;
  --r2: 12px;
  --r3: 16px;

  --font-display: 'Syne', sans-serif;
  --font-body:    'Source Serif 4', Georgia, serif;
  --font-mono:    'IBM Plex Mono', monospace;
  --fs: {fs};

  --shadow: 0 4px 24px rgba(0,0,0,0.5);
  --shadow2: 0 8px 40px rgba(0,0,0,0.7);
  --t: 0.2s cubic-bezier(0.4,0,0.2,1);
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
  max-width: 1400px !important;
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
section[data-testid="stSidebar"] label {{
  color: var(--fg0) !important;
  font-family: var(--font-display) !important;
}}
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
  background: var(--bg2) !important;
  border-color: var(--border2) !important;
  color: var(--fg0) !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] * {{
  color: var(--fg0) !important;
  background: var(--bg2) !important;
}}
[data-baseweb="popover"] * {{
  background: var(--bg3) !important;
  color: var(--fg0) !important;
  border-color: var(--border2) !important;
}}

/* ── Buttons ── */
.stButton > button {{
  font-family: var(--font-display) !important;
  font-weight: 700 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
  border-radius: var(--r) !important;
  transition: all var(--t) !important;
  min-height: 42px !important;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, #1a56db 0%, var(--blue) 100%) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 0 0 1px rgba(77,159,255,0.3), 0 4px 16px rgba(26,86,219,0.5) !important;
}}
.stButton > button[kind="primary"]:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 0 0 1px rgba(77,159,255,0.5), 0 8px 24px rgba(26,86,219,0.6) !important;
}}
.stButton > button[kind="secondary"] {{
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--fg1) !important;
}}
.stButton > button[kind="secondary"]:hover {{
  background: var(--bg3) !important;
  border-color: var(--blue) !important;
  color: var(--fg0) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 2px;
  background: var(--bg1);
  border: 1px solid var(--border) !important;
  border-radius: var(--r2);
  padding: 4px;
  flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
  font-family: var(--font-display) !important;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  padding: 7px 14px !important;
  border-radius: var(--r) !important;
  background: transparent !important;
  color: var(--fg2) !important;
  border: none !important;
  transition: all var(--t) !important;
}}
.stTabs [aria-selected="true"] {{
  background: var(--bg3) !important;
  color: var(--blue) !important;
}}

/* ── Radio (answer choices) ── */
.stRadio > label {{ display: none !important; }}
.stRadio [data-testid="stWidgetLabel"] {{ display: none !important; }}
.stRadio > div {{
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
}}
.stRadio > div > label {{
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important;
  padding: 12px 16px !important;
  cursor: pointer !important;
  transition: all var(--t) !important;
  font-family: var(--font-body) !important;
  font-size: var(--fs) !important;
  line-height: 1.7 !important;
  color: var(--fg0) !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
}}
.stRadio > div > label:hover {{
  border-color: var(--blue) !important;
  background: var(--blue-dim) !important;
  transform: translateX(4px) !important;
}}
.stRadio > div > label[data-checked="true"] {{
  border-color: var(--blue) !important;
  background: var(--blue-dim) !important;
}}

/* ── Expanders ── */
.streamlit-expanderHeader {{
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important;
  color: var(--fg0) !important;
  font-family: var(--font-display) !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
  min-height: 44px !important;
  padding: 0 14px !important;
}}
.streamlit-expanderContent {{
  background: var(--bg1) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--r) var(--r) !important;
  padding: 16px !important;
}}

/* ── Alerts ── */
.stAlert {{
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  color: var(--fg0) !important;
  font-family: var(--font-body) !important;
}}

/* ── Select / Number ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input {{
  background: var(--bg2) !important;
  border-color: var(--border2) !important;
  color: var(--fg0) !important;
  border-radius: var(--r) !important;
  font-family: var(--font-mono) !important;
}}

/* ── Metric ── */
[data-testid="metric-container"] {{
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important;
  padding: 16px !important;
}}
[data-testid="metric-container"] label {{
  color: var(--fg2) !important;
  font-size: 0.72rem !important;
  font-family: var(--font-display) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
  color: var(--blue) !important;
  font-family: var(--font-display) !important;
  font-size: 1.6rem !important;
}}

/* ── Progress ── */
[data-testid="stProgress"] > div > div {{
  background: var(--bg3) !important;
  border-radius: 4px;
}}
[data-testid="stProgress"] > div > div > div {{
  background: linear-gradient(90deg, var(--blue), var(--teal)) !important;
  border-radius: 4px;
}}

/* ── Textarea ── */
.stTextArea textarea {{
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--fg0) !important;
  border-radius: var(--r) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.82rem !important;
  line-height: 1.7 !important;
}}
.stTextArea textarea:focus {{
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 2px rgba(77,159,255,0.2) !important;
}}

/* ── Checkbox ── */
.stCheckbox label span {{
  color: var(--fg1) !important;
  font-family: var(--font-display) !important;
  font-size: 0.82rem !important;
}}

/* ==========================================
   CUSTOM COMPONENTS
   ========================================== */

.hero {{
  position: relative;
  background: linear-gradient(145deg, #070b12 0%, #0c1628 50%, #071420 100%);
  border: 1px solid var(--border2);
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: var(--shadow2);
}}
.hero-noise {{
  position: absolute; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.025'/%3E%3C/svg%3E");
  opacity: 0.4;
}}
.hero-glow-l {{
  position: absolute; width: 500px; height: 500px;
  border-radius: 50%; top: -150px; left: -100px;
  background: radial-gradient(circle, rgba(77,159,255,0.08) 0%, transparent 70%);
  pointer-events: none;
}}
.hero-glow-r {{
  position: absolute; width: 400px; height: 400px;
  border-radius: 50%; bottom: -100px; right: -50px;
  background: radial-gradient(circle, rgba(45,212,191,0.07) 0%, transparent 70%);
  pointer-events: none;
}}
.hero-inner {{
  position: relative; z-index: 2;
  padding: 48px 56px 40px;
}}
.hero-eyebrow {{
  font-family: var(--font-mono);
  font-size: 0.6rem; font-weight: 600;
  letter-spacing: 0.25em; text-transform: uppercase;
  color: var(--blue);
  background: rgba(77,159,255,0.1);
  border: 1px solid rgba(77,159,255,0.2);
  padding: 4px 12px; border-radius: 20px;
  display: inline-block; margin-bottom: 20px;
}}
.hero-title {{
  font-family: var(--font-display) !important;
  font-size: clamp(2rem, 4vw, 3.4rem) !important;
  font-weight: 800 !important;
  line-height: 1.05 !important;
  letter-spacing: -0.03em !important;
  color: #fff !important;
  margin-bottom: 16px !important;
}}
.hero-title .accent {{ color: var(--blue); }}
.hero-title .accent2 {{ color: var(--teal); }}
.hero-sub {{
  font-family: var(--font-body);
  font-size: 0.9rem; line-height: 1.8;
  color: rgba(255,255,255,0.45);
  max-width: 640px; margin-bottom: 28px;
}}
.hero-rule {{
  height: 1px;
  background: linear-gradient(90deg, rgba(77,159,255,0.3), transparent);
  margin-bottom: 24px;
}}
.hero-stats {{
  display: flex; gap: 36px; flex-wrap: wrap;
}}
.hs-num {{
  font-family: var(--font-display); font-size: 1.8rem;
  font-weight: 800; color: var(--blue); line-height: 1;
}}
.hs-lbl {{
  font-family: var(--font-mono); font-size: 0.58rem;
  color: rgba(255,255,255,0.3); text-transform: uppercase;
  letter-spacing: 0.12em; margin-top: 4px;
}}

.sec-title {{
  font-family: var(--font-display) !important;
  font-size: 0.72rem !important; font-weight: 700 !important;
  letter-spacing: 0.2em !important; text-transform: uppercase !important;
  color: var(--fg2) !important;
  display: flex; align-items: center; gap: 10px;
  margin: 28px 0 14px;
}}
.sec-title::after {{
  content: ''; flex: 1; height: 1px;
  background: var(--border);
}}

.notice {{
  display: flex; gap: 12px;
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--blue);
  border-radius: var(--r); padding: 12px 16px;
  font-family: var(--font-body); font-size: 0.84rem;
  color: var(--fg1); line-height: 1.7;
  margin-bottom: 14px;
}}
.notice.warn {{ border-left-color: var(--amber); }}
.notice.sci  {{ border-left-color: var(--teal); }}
.notice.red  {{ border-left-color: var(--red); }}
.notice.green{{ border-left-color: var(--green); }}
.notice strong {{ color: var(--fg0); }}
.ni {{ font-size: 1rem; flex-shrink: 0; margin-top: 1px; }}

.comp-wrap {{
  background: var(--bg1);
  border: 1px solid var(--border2);
  border-radius: var(--r2);
  padding: 16px 20px; margin-bottom: 12px;
}}
.comp-wrap.math {{ border-top: 2px solid var(--blue); }}
.comp-wrap.sci  {{ border-top: 2px solid var(--teal); }}
.comp-head {{
  font-family: var(--font-display); font-size: 0.85rem;
  font-weight: 700; color: var(--fg0); margin-bottom: 4px;
}}
.comp-sub {{
  font-family: var(--font-mono); font-size: 0.62rem;
  color: var(--fg2); letter-spacing: 0.08em;
  text-transform: uppercase; margin-bottom: 10px;
}}

/* ── Question card ── */
.q-card {{
  background: var(--bg1);
  border: 1px solid var(--border);
  border-left: 3px solid var(--blue);
  border-radius: var(--r2);
  padding: 20px 24px;
  margin-bottom: 14px;
  transition: box-shadow var(--t), border-color var(--t);
  scroll-margin-top: 80px;
}}
.q-card.sci {{ border-left-color: var(--teal); }}
.q-card.answered {{ border-left-color: var(--green); }}
.q-card.flagged {{ border-left-color: var(--amber); }}
.q-card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}

.q-meta {{
  display: flex; align-items: center; gap: 7px;
  flex-wrap: wrap; margin-bottom: 14px;
}}
.q-badge {{
  font-family: var(--font-mono); font-size: 0.58rem;
  font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
  padding: 3px 10px; border-radius: 4px;
}}
.q-badge.math {{ color: var(--blue); background: var(--blue-dim); border: 1px solid rgba(77,159,255,0.2); }}
.q-badge.sci  {{ color: var(--teal); background: var(--teal-dim); border: 1px solid rgba(45,212,191,0.2); }}
.q-badge.tag  {{
  color: var(--fg2); background: var(--bg3);
  border: 1px solid var(--border2);
}}
.q-badge.flag {{ color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(251,191,36,0.2); }}
.q-badge.ok   {{ color: var(--green); background: var(--green-dim); border: 1px solid rgba(52,211,153,0.2); }}

.q-stem {{
  font-family: var(--font-body); font-size: var(--fs);
  line-height: 1.9; color: var(--fg0);
  margin-bottom: 16px;
}}
/* KaTeX rendering */
.q-stem .katex, .q-stem .katex * {{ color: var(--fg0) !important; }}
.q-stem .katex-display {{
  background: var(--bg3); border-radius: var(--r);
  padding: 12px 16px; margin: 10px 0;
  overflow-x: auto; overflow-y: hidden;
  border: 1px solid var(--border);
}}

/* Science stimuli */
.stim-passage {{
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--teal);
  border-radius: var(--r); padding: 14px 18px;
  margin-bottom: 14px;
  font-family: var(--font-body); font-size: 0.875rem;
  line-height: 1.85; color: var(--fg1);
}}
.stim-data {{
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--amber);
  border-radius: var(--r); padding: 14px 18px;
  margin-bottom: 14px;
  font-family: var(--font-mono); font-size: 0.78rem;
  line-height: 1.7; color: var(--fg1);
  overflow-x: auto;
}}
.stim-label {{
  font-family: var(--font-mono); font-size: 0.58rem;
  letter-spacing: 0.14em; text-transform: uppercase;
  margin-bottom: 8px; display: block;
}}
.stim-label.p {{ color: var(--teal); }}
.stim-label.d {{ color: var(--amber); }}
.stim-label.g {{ color: var(--purple); }}

/* Tables inside stimuli */
.sci-tbl {{ width: 100%; border-collapse: collapse; margin-top: 6px; }}
.sci-tbl th {{
  background: var(--bg3); color: var(--fg0);
  padding: 8px 12px; text-align: left;
  border-bottom: 1px solid var(--border2);
  font-size: 0.72rem; letter-spacing: 0.04em;
}}
.sci-tbl td {{
  padding: 7px 12px; border-bottom: 1px solid var(--border);
  color: var(--fg1); font-size: 0.82rem;
}}
.sci-tbl tr:last-child td {{ border-bottom: none; }}
.sci-tbl tr:hover td {{ background: var(--bg3); }}

/* Navigator */
.nav-box {{
  background: var(--bg1);
  border: 1px solid var(--border2);
  border-radius: var(--r2); padding: 14px 18px;
  margin-bottom: 18px; position: sticky; top: 10px; z-index: 99;
  box-shadow: var(--shadow);
}}
.nav-title {{
  font-family: var(--font-mono); font-size: 0.58rem;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--fg2); margin-bottom: 10px;
}}
.nav-grid {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.nav-dot {{
  min-width: 32px; height: 28px;
  border-radius: 5px; display: inline-flex;
  align-items: center; justify-content: center;
  font-family: var(--font-mono); font-size: 0.6rem; font-weight: 600;
  cursor: pointer;
  background: var(--bg3); color: var(--fg2);
  border: 1px solid var(--border);
  transition: all var(--t);
}}
.nav-dot:hover {{ border-color: var(--blue); color: var(--blue); transform: scale(1.1); }}
.nav-dot.am {{ background: var(--blue-dim); color: var(--blue); border-color: rgba(77,159,255,0.3); }}
.nav-dot.as {{ background: var(--teal-dim); color: var(--teal); border-color: rgba(45,212,191,0.3); }}
.nav-dot.fl {{ background: var(--amber-dim); color: var(--amber); border-color: rgba(251,191,36,0.3); }}

/* Progress bar */
.pbar-wrap {{ margin-bottom: 12px; }}
.pbar-row {{
  display: flex; justify-content: space-between;
  font-family: var(--font-mono); font-size: 0.6rem;
  color: var(--fg2); margin-bottom: 5px;
}}
.pbar-track {{
  height: 4px; background: var(--bg3);
  border-radius: 2px; overflow: hidden;
}}
.pbar-fill-m {{ height: 100%; border-radius: 2px; background: linear-gradient(90deg, #1a56db, var(--blue)); transition: width 0.5s ease; }}
.pbar-fill-s {{ height: 100%; border-radius: 2px; background: linear-gradient(90deg, #0d6b63, var(--teal)); transition: width 0.5s ease; }}

/* Timer */
.timer {{
  position: fixed; top: 16px; right: 20px; z-index: 99999;
  font-family: var(--font-mono); font-size: 0.95rem; font-weight: 600;
  padding: 8px 18px; border-radius: 24px;
  border: 1px solid rgba(77,159,255,0.3);
  background: var(--bg1);
  color: var(--blue);
  box-shadow: var(--shadow);
  letter-spacing: 0.06em;
}}
.timer.s {{ color: var(--teal); border-color: rgba(45,212,191,0.3); }}
.timer.w {{ color: var(--amber); border-color: rgba(251,191,36,0.4); }}
.timer.d {{ color: var(--red); border-color: rgba(248,113,113,0.4); animation: pulse 1s infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.6; }} }}

/* Stat row */
.stat-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 12px 0; }}
.stat-pill {{
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: var(--r); padding: 12px 18px; flex: 1; min-width: 90px; text-align: center;
}}
.sp-n {{ font-family: var(--font-display); font-size: 1.6rem; font-weight: 800; line-height: 1; }}
.sp-l {{ font-family: var(--font-mono); font-size: 0.55rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg2); margin-top: 4px; }}

/* Results */
.res-hero {{
  background: linear-gradient(145deg, #070b12, #0c1628, #071420);
  border: 1px solid var(--border2);
  border-radius: 20px; padding: 52px 48px;
  text-align: center; position: relative; overflow: hidden;
  margin-bottom: 24px; box-shadow: var(--shadow2);
}}
.res-hero-glow {{
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at center, rgba(77,159,255,0.07) 0%, transparent 65%);
  pointer-events: none;
}}
.upg-label {{
  font-family: var(--font-mono); font-size: 0.6rem;
  letter-spacing: 0.25em; text-transform: uppercase;
  color: rgba(255,255,255,0.3); margin-bottom: 10px;
  position: relative; z-index: 1;
}}
.upg-val {{
  font-family: var(--font-display);
  font-size: clamp(4rem, 9vw, 7rem);
  font-weight: 800; line-height: 1;
  position: relative; z-index: 1;
  letter-spacing: -0.04em;
}}
.upg-verdict {{
  font-family: var(--font-body); font-size: 1rem;
  color: rgba(255,255,255,0.5); margin-top: 12px;
  position: relative; z-index: 1;
}}

.upg-cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }}
.upg-card {{
  background: var(--bg1); border: 1px solid var(--border2);
  border-radius: var(--r2); padding: 22px 26px;
  position: relative; overflow: hidden;
}}
.upg-card.m {{ border-top: 2px solid var(--blue); }}
.upg-card.s {{ border-top: 2px solid var(--teal); }}
.upg-card-title {{
  font-family: var(--font-mono); font-size: 0.6rem;
  letter-spacing: 0.16em; text-transform: uppercase;
  margin-bottom: 10px;
}}
.upg-card.m .upg-card-title {{ color: var(--blue); }}
.upg-card.s .upg-card-title {{ color: var(--teal); }}
.upg-card-val {{
  font-family: var(--font-display); font-size: 2.8rem;
  font-weight: 800; line-height: 1; margin-bottom: 6px;
}}
.upg-card.m .upg-card-val {{ color: var(--blue); }}
.upg-card.s .upg-card-val {{ color: var(--teal); }}
.upg-card-sub {{ font-family: var(--font-body); font-size: 0.8rem; color: var(--fg1); }}
.upg-br {{ margin-top: 14px; }}
.upg-br-row {{
  display: flex; justify-content: space-between;
  padding: 6px 0; border-bottom: 1px solid var(--border);
  font-family: var(--font-body); font-size: 0.8rem;
}}
.upg-br-row:last-child {{ border-bottom: none; }}
.upg-br-lbl {{ color: var(--fg1); }}
.upg-br-val {{ font-family: var(--font-mono); font-weight: 600; font-size: 0.78rem; }}

.score-panel {{
  background: var(--bg1); border: 1px solid var(--border2);
  border-radius: var(--r2); padding: 20px 24px;
}}
.score-panel h4 {{
  font-family: var(--font-display) !important;
  font-size: 0.85rem !important; font-weight: 700 !important;
  letter-spacing: 0.08em !important; text-transform: uppercase !important;
  margin-bottom: 14px !important; padding-bottom: 12px !important;
  border-bottom: 1px solid var(--border) !important;
}}
.s-row {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 7px 0; border-bottom: 1px solid var(--border);
  font-family: var(--font-body); font-size: 0.84rem;
}}
.s-row:last-child {{ border-bottom: none; }}
.s-lbl {{ color: var(--fg1); }}
.s-val {{ font-family: var(--font-mono); font-weight: 600; font-size: 0.8rem; }}
.s-val.c {{ color: var(--green); }}
.s-val.w {{ color: var(--red); }}
.s-val.g {{ color: var(--blue); }}

.heat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }}
.heat-row {{
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-body); font-size: 0.75rem;
  padding: 7px 10px; border-radius: var(--r);
  border: 1px solid var(--border); background: var(--bg2);
}}
.heat-bar-out {{ flex: 1; height: 4px; background: var(--bg3); border-radius: 2px; overflow: hidden; }}
.heat-bar-in {{ height: 100%; border-radius: 2px; transition: width 0.8s ease; }}
.heat-bar-in.hi {{ background: var(--green); }}
.heat-bar-in.mid {{ background: var(--amber); }}
.heat-bar-in.lo {{ background: var(--red); }}
.heat-pct {{ font-family: var(--font-mono); font-size: 0.58rem; font-weight: 700; min-width: 32px; text-align: right; }}

.ir-c {{ background: var(--green-dim); border: 1px solid rgba(52,211,153,0.25); border-radius: var(--r); padding: 9px 14px; font-family: var(--font-body); color: var(--green); margin: 4px 0; font-size: var(--fs); }}
.ir-w {{ background: var(--red-dim);   border: 1px solid rgba(248,113,113,0.25); border-radius: var(--r); padding: 9px 14px; font-family: var(--font-body); color: var(--red);   margin: 4px 0; font-size: var(--fs); }}
.ir-o {{ background: var(--bg2);       border: 1px solid var(--border);         border-radius: var(--r); padding: 9px 14px; font-family: var(--font-body); color: var(--fg1);  margin: 4px 0; font-size: var(--fs); }}

/* Graph canvas container */
.graph-container {{
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: var(--r); padding: 8px; margin-bottom: 14px;
  overflow: hidden;
}}

/* Campus cards */
.campus-card {{ background: var(--bg1); border: 1px solid var(--border2); border-radius: var(--r2); overflow: hidden; margin-bottom: 14px; }}
.campus-hdr {{ padding: 14px 20px; background: linear-gradient(135deg, #0a2a16, #0d3820); border-bottom: 1px solid var(--border2); }}
.campus-hdr.fail {{ background: linear-gradient(135deg, #2a0a0a, #3a1010); }}
.campus-hdr h4 {{ color: var(--fg0) !important; font-size: 0.95rem !important; margin-bottom: 3px !important; }}
.campus-hdr p {{ color: var(--fg1) !important; font-family: var(--font-mono); font-size: 0.62rem !important; }}
.campus-body {{ padding: 14px 20px; }}
.prog-row {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 9px 0; border-bottom: 1px solid var(--border);
  font-family: var(--font-body); font-size: 0.84rem;
}}
.prog-row:last-child {{ border-bottom: none; }}
.prog-name {{ font-weight: 600; color: var(--fg0); font-family: var(--font-display); }}
.prog-sub {{ font-family: var(--font-mono); font-size: 0.58rem; color: var(--fg2); margin-top: 2px; }}
.badge {{ font-family: var(--font-mono); font-size: 0.6rem; font-weight: 700; padding: 3px 10px; border-radius: 4px; }}
.badge.pass {{ color: var(--green); background: var(--green-dim); border: 1px solid rgba(52,211,153,0.25); }}
.badge.risk {{ color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(251,191,36,0.25); }}
.badge.fail {{ color: var(--red);   background: var(--red-dim);   border: 1px solid rgba(248,113,113,0.25); }}

/* KaTeX load helper */
.katex-render {{ display: none; }}

/* Graph SVG */
.chart-wrap {{
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: var(--r2); padding: 20px; margin: 12px 0;
  overflow: visible;
}}

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

# Load KaTeX for proper math rendering
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {
    delimiters: [
      {left:'$$',right:'$$',display:true},
      {left:'$',right:'$',display:false},
      {left:'\\\\(',right:'\\\\)',display:false},
      {left:'\\\\[',right:'\\\\]',display:true}
    ],
    throwOnError: false,
    strict: false
  });"></script>
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
    "UP Diliman":           {"cutoff": 2.20, "recon": 0.0,   "note": "Strictest. No appeals. ~40k applicants."},
    "UP Manila":            {"cutoff": 2.10, "recon": 2.580, "note": "Health sciences hub."},
    "UP Los Baños":         {"cutoff": 2.30, "recon": 2.800, "note": "Agri/forestry flagship."},
    "UP Baguio":            {"cutoff": 2.50, "recon": 2.700, "note": "Arts & sciences."},
    "UP Cebu":              {"cutoff": 2.60, "recon": 2.800, "note": "Growing campus."},
    "UP Mindanao":          {"cutoff": 2.60, "recon": 2.800, "note": "Priority for Mindanaoan applicants."},
    "UP Visayas (Iloilo)":  {"cutoff": 2.70, "recon": 2.700, "note": "Marine & fisheries."},
    "UP Open University":   {"cutoff": 2.80, "recon": 2.800, "note": "Distance learning."},
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
    <div style='background: linear-gradient(135deg, var(--bg1), var(--bg2)); border-bottom: 1px solid var(--border); padding: 24px 20px 20px; text-align: center;'>
      <div style='font-family: var(--font-display); font-size: 1.15rem; font-weight: 800; color: var(--fg0); letter-spacing: -0.02em; margin-bottom: 4px;'>PADAYON!</div>
      <div style='font-family: var(--font-mono); font-size: 0.55rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--fg2);'>UPCAT Agham + Matematika · 2026</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-title" style="margin: 18px 0 10px; padding-left: 12px; font-size: 0.6rem;">🔑 API Config</div>', unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", help="Get free key at aistudio.google.com")
    gemini_model = st.selectbox("Model", ["gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-pro"], index=0)

    st.markdown('<div class="sec-title" style="margin: 14px 0 10px; padding-left: 12px; font-size: 0.6rem;">♿ Display</div>', unsafe_allow_html=True)
    font_size = st.select_slider("Text Size", options=["small","medium","large","x-large"], value=st.session_state.get('font_size','medium'))
    if font_size != st.session_state.get('font_size'):
        st.session_state['font_size'] = font_size; st.rerun()
    show_timer = st.checkbox("Show Countdown Timer", value=True)
    show_nav = st.checkbox("Show Item Navigator", value=True)
    enable_flag = st.checkbox("Enable Item Flagging 🚩", value=True)

    st.markdown('<div class="sec-title" style="margin: 14px 0 10px; padding-left: 12px; font-size: 0.6rem;">🏫 School Type</div>', unsafe_allow_html=True)
    jhs_type = st.selectbox("JHS School Type", list(SCHOOL_TIERS.keys()), index=5)
    shs_type = st.selectbox("SHS School Type", list(SCHOOL_TIERS.keys()), index=5)
    jhs_mod = SCHOOL_TIERS[jhs_type]["modifier"]
    shs_mod = SCHOOL_TIERS[shs_type]["modifier"]
    palugit_active = SCHOOL_TIERS[jhs_type]["palugit"] or SCHOOL_TIERS[shs_type]["palugit"]
    if palugit_active:
        st.caption(f"✅ Palugit: JHS {jhs_mod:+.2f} / SHS {shs_mod:+.2f}")

    st.markdown('<div class="sec-title" style="margin: 14px 0 10px; padding-left: 12px; font-size: 0.6rem;">📐 Math Grades G8–G11</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        g8_math     = st.number_input("G8 Math",      60.0, 100.0, 87.0, 0.5)
        g9_math     = st.number_input("G9 Math",      60.0, 100.0, 87.0, 0.5)
        g10_math    = st.number_input("G10 Math",     60.0, 100.0, 88.0, 0.5)
        g11_precalc = st.number_input("Pre-Calculus", 60.0, 100.0, 88.0, 0.5)
    with c2:
        g11_calc    = st.number_input("Basic Calculus",60.0, 100.0, 87.0, 0.5)
        g11_stats   = st.number_input("Stats & Prob",  60.0, 100.0, 88.0, 0.5)
        g11_genmath = st.number_input("Gen. Math",     60.0, 100.0, 88.0, 0.5)

    st.markdown('<div class="sec-title" style="margin: 14px 0 10px; padding-left: 12px; font-size: 0.6rem;">🔬 Science Grades G8–G11</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        g8_sci   = st.number_input("G8 Science",  60.0, 100.0, 87.0, 0.5)
        g9_sci   = st.number_input("G9 Science",  60.0, 100.0, 87.0, 0.5)
        g10_sci  = st.number_input("G10 Science", 60.0, 100.0, 88.0, 0.5)
        g11_bio1 = st.number_input("Gen Bio 1",   60.0, 100.0, 88.0, 0.5)
    with c4:
        g11_bio2  = st.number_input("Gen Bio 2",  60.0, 100.0, 88.0, 0.5)
        g11_earth = st.number_input("Earth Sci",  60.0, 100.0, 87.0, 0.5)

    st.markdown('<div class="sec-title" style="margin: 14px 0 10px; padding-left: 12px; font-size: 0.6rem;">🎯 Campus & Program Choices</div>', unsafe_allow_html=True)
    campus_1 = st.selectbox("1st Choice Campus", list(CAMPUS_DATA.keys()), index=0)
    c1_p1 = st.selectbox("Priority 1", get_all_programs(campus_1), key="c1p1")
    c1_p2 = st.selectbox("Priority 2", get_all_programs(campus_1), key="c1p2")
    c1_p3 = st.selectbox("Priority 3", get_all_programs(campus_1), key="c1p3")
    campus_2 = st.selectbox("2nd Choice Campus", list(CAMPUS_DATA.keys()), index=2)
    c2_p1 = st.selectbox("Priority 1", get_all_programs(campus_2), key="c2p1")
    c2_p2 = st.selectbox("Priority 2", get_all_programs(campus_2), key="c2p2")
    c2_p3 = st.selectbox("Priority 3", get_all_programs(campus_2), key="c2p3")

    st.markdown('<div class="sec-title" style="margin: 14px 0 10px; padding-left: 12px; font-size: 0.6rem;">⚙️ Simulation Parameters</div>', unsafe_allow_html=True)
    math_items = st.slider("Math Items", 10, 50, 25, 5)
    sci_items  = st.slider("Science Items", 10, 45, 20, 5)
    difficulty = st.select_slider("Difficulty",
        options=["Standard", "Competitive", "Brutal", "Massacre"],
        value="Competitive")

# ==========================================
# DIFFICULTY CONFIG
# ==========================================
DIFF_MAP = {
    "Standard":    ("Items should be solvable in under 60s. Test basic recall and single-step reasoning. ~50% of prepared applicants should score above 60%.", 0.52, 0.16),
    "Competitive": ("Items require 2-4 steps. Test conceptual understanding, not just formulas. ~Top 20% ceiling. Distractors are common procedural errors.", 0.44, 0.15),
    "Brutal":      ("Items test deep conceptual knowledge. Multi-step reasoning with non-obvious entry points. ~Top 8% ceiling. Science items use dense experimental data.", 0.37, 0.14),
    "Massacre":    ("Items appear simple but require precise logical reasoning. ~Top 2-3% ceiling. Zero items solvable by rote recall. Every distractor matches a specific conceptual error.", 0.31, 0.13),
}
diff_instruction, MEAN_BASELINE, SIGMA = DIFF_MAP[difficulty]

# ==========================================
# GRAPH GENERATION HELPERS
# ==========================================
def generate_bar_chart_svg(labels, values, title="", color="#4d9fff", width=500, height=280):
    """Generate an SVG bar chart for embedding in science stimuli."""
    if not labels or not values:
        return ""
    max_v = max(values) if max(values) > 0 else 1
    margin = {"top": 40, "right": 20, "bottom": 60, "left": 55}
    chart_w = width - margin["left"] - margin["right"]
    chart_h = height - margin["top"] - margin["bottom"]
    bar_w = chart_w / len(values) * 0.7
    bar_gap = chart_w / len(values)
    
    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#141d2e;border-radius:8px;font-family:IBM Plex Mono,monospace;">',
        f'<rect width="{width}" height="{height}" fill="#141d2e" rx="8"/>',
    ]
    if title:
        svg_parts.append(f'<text x="{width//2}" y="22" text-anchor="middle" fill="#9aaabb" font-size="11" font-weight="600" letter-spacing="0.05em">{title}</text>')
    
    # Y-axis grid lines and labels
    for i in range(5):
        y_val = max_v * i / 4
        y_pos = margin["top"] + chart_h - (y_val / max_v * chart_h)
        svg_parts.append(f'<line x1="{margin["left"]}" y1="{y_pos:.1f}" x2="{margin["left"]+chart_w}" y2="{y_pos:.1f}" stroke="#1a2540" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin["left"]-6}" y="{y_pos+4:.1f}" text-anchor="end" fill="#5a6a7a" font-size="9">{y_val:.1f}</text>')
    
    # Bars
    for i, (lbl, val) in enumerate(zip(labels, values)):
        bar_h = (val / max_v) * chart_h
        x = margin["left"] + i * bar_gap + (bar_gap - bar_w) / 2
        y = margin["top"] + chart_h - bar_h
        svg_parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" opacity="0.85" rx="2"/>')
        svg_parts.append(f'<text x="{x+bar_w/2:.1f}" y="{y-4:.1f}" text-anchor="middle" fill="#f0f4f8" font-size="9" font-weight="600">{val:.1f}</text>')
        # X label
        lbl_short = str(lbl)[:12]
        svg_parts.append(f'<text x="{x+bar_w/2:.1f}" y="{margin["top"]+chart_h+16:.1f}" text-anchor="middle" fill="#9aaabb" font-size="9" transform="rotate(-30 {x+bar_w/2:.1f} {margin["top"]+chart_h+16:.1f})">{lbl_short}</text>')
    
    svg_parts.append('</svg>')
    return "".join(svg_parts)

def generate_line_chart_svg(x_vals, y_series, title="", width=500, height=280):
    """Generate SVG line chart."""
    if not x_vals or not y_series:
        return ""
    colors = ["#4d9fff", "#2dd4bf", "#fbbf24", "#f87171", "#a78bfa"]
    all_y = [v for series in y_series.values() for v in series]
    min_y = min(all_y) if all_y else 0
    max_y = max(all_y) if all_y else 1
    if max_y == min_y: max_y = min_y + 1
    margin = {"top": 40, "right": 100, "bottom": 50, "left": 55}
    chart_w = width - margin["left"] - margin["right"]
    chart_h = height - margin["top"] - margin["bottom"]
    n = len(x_vals)
    
    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#141d2e;border-radius:8px;font-family:IBM Plex Mono,monospace;">',
        f'<rect width="{width}" height="{height}" fill="#141d2e" rx="8"/>',
    ]
    if title:
        svg_parts.append(f'<text x="{(width-margin["right"])//2}" y="22" text-anchor="middle" fill="#9aaabb" font-size="11" font-weight="600">{title}</text>')
    
    # Grid
    for i in range(5):
        y_v = min_y + (max_y - min_y) * i / 4
        y_p = margin["top"] + chart_h - ((y_v - min_y) / (max_y - min_y) * chart_h)
        svg_parts.append(f'<line x1="{margin["left"]}" y1="{y_p:.1f}" x2="{margin["left"]+chart_w}" y2="{y_p:.1f}" stroke="#1a2540" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin["left"]-6}" y="{y_p+4:.1f}" text-anchor="end" fill="#5a6a7a" font-size="9">{y_v:.2g}</text>')
    
    # X axis labels
    for i, xv in enumerate(x_vals):
        x = margin["left"] + i * chart_w / max(1, n-1)
        svg_parts.append(f'<text x="{x:.1f}" y="{margin["top"]+chart_h+14:.1f}" text-anchor="middle" fill="#9aaabb" font-size="9">{xv}</text>')
    
    # Lines and legend
    for ci, (name, y_vals) in enumerate(y_series.items()):
        color = colors[ci % len(colors)]
        if len(y_vals) < 1: continue
        pts = []
        for i, yv in enumerate(y_vals):
            x = margin["left"] + i * chart_w / max(1, n-1)
            y = margin["top"] + chart_h - ((yv - min_y) / (max_y - min_y) * chart_h)
            pts.append(f"{x:.1f},{y:.1f}")
        polyline = " ".join(pts)
        svg_parts.append(f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        # Dots
        for i, yv in enumerate(y_vals):
            x = margin["left"] + i * chart_w / max(1, n-1)
            y = margin["top"] + chart_h - ((yv - min_y) / (max_y - min_y) * chart_h)
            svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>')
        # Legend
        ly = margin["top"] + ci * 18
        svg_parts.append(f'<rect x="{width-margin["right"]+6}" y="{ly}" width="10" height="10" fill="{color}" rx="2"/>')
        svg_parts.append(f'<text x="{width-margin["right"]+20}" y="{ly+9:.1f}" fill="#9aaabb" font-size="9">{name[:14]}</text>')
    
    svg_parts.append('</svg>')
    return "".join(svg_parts)

# ==========================================
# JSON & LATEX HELPERS
# ==========================================
def clean_json(raw: str) -> str:
    """Robustly extract and clean JSON from model output."""
    s = raw.strip()
    # Remove code fences
    for fence in ["```json", "```JSON", "```"]:
        if s.startswith(fence):
            s = s[len(fence):]
    if s.endswith("```"):
        s = s[:-3]
    # Find outermost braces
    start = s.find("{")
    if start == -1:
        return s.strip()
    # Find matching closing brace
    depth = 0
    end = start
    for i, c in enumerate(s[start:], start):
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    return s[start:end+1].strip()

def render_math_text(text: str) -> str:
    """Ensure math text renders properly — strip erroneous markdown bold from options."""
    if not text:
        return ""
    # Remove **X)** patterns that were appearing in options (markdown artifacts)
    text = re.sub(r'\*\*([A-D])\)\*\*\s*', r'\1) ', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return text

def build_svg_from_data(chart_data: dict) -> str:
    """Build SVG chart from parsed chart data embedded in items."""
    chart_type = chart_data.get("type", "bar")
    title = chart_data.get("title", "")
    
    if chart_type == "bar":
        labels = chart_data.get("labels", [])
        values = chart_data.get("values", [])
        x_label = chart_data.get("x_label", "")
        color = chart_data.get("color", "#4d9fff")
        return generate_bar_chart_svg(labels, values, title, color)
    elif chart_type == "line":
        x_vals = chart_data.get("x_values", [])
        y_series = chart_data.get("y_series", {})
        return generate_line_chart_svg(x_vals, y_series, title)
    return ""

# ==========================================
# PROMPT SYSTEM
# ==========================================

MATH_SYSTEM_PROMPT = """You are the chief psychometrician for the UPCAT Mathematics subtest at UP Office of Admissions.
Your ONLY job is to generate items that EXACTLY match the provided competencies. You must NOT generate items outside those competencies.

IRONCLAD LATEX RULES — ZERO EXCEPTIONS:
1. Every mathematical expression, variable, number in an equation, fraction, exponent, radical, symbol MUST use LaTeX.
2. Inline: $...$. Display (standalone): $$...$$
3. Options must use LaTeX. Example: "$x = \\frac{3}{4}$" not "x = 3/4"
4. NEVER use plain text math: no "x^2", no "sqrt(x)", no "3/4" inside option text.
5. Fractions: $\\frac{a}{b}$. Square roots: $\\sqrt{x}$. Exponents: $x^{2}$. Subscripts: $x_{1}$.

PSYCHOMETRIC RULES:
- No calculator. All arithmetic done by hand in ≤90s.
- 4 options: A, B, C, D. Correct key distributed roughly equal A/B/C/D.
- Each wrong option = specific named error type (SIGN_ERROR, ARITHMETIC_ERROR, FORMULA_CONFUSION, CONCEPTUAL_ERROR, INCOMPLETE_SOLUTION).
- Options must be plausible and similar in length/complexity.
- Word problems: use Filipino contexts (jeepney, tricycle, rice, market, school).
- Max 3-4 steps per item.
- Solution: minimum 4 clearly labeled steps.

OUTPUT: Return STRICT VALID JSON ONLY. No markdown fences. No preamble. No commentary."""

SCI_SYSTEM_PROMPT = """You are the chief psychometrician for the UPCAT Science subtest at UP Office of Admissions.
Your ONLY job is to generate items that EXACTLY match the provided competencies. Do NOT generate items outside those competencies.

STIMULUS & GRAPH RULES:
- At least 60% of items must have a stimulus (TEXT_PASSAGE, DATA_TABLE, or DIAGRAM).
- DATA_TABLE stimuli: use clean HTML <table> tags with class="sci-tbl". Include units in headers.
- For items with quantitative data, you may optionally include a "chart" field with chart specification.
- Chart spec format: {"type":"bar","title":"...","labels":[...],"values":[...],"color":"#4d9fff"} for bar charts
  OR {"type":"line","title":"...","x_values":[...],"y_series":{"SeriesName":[...]}} for line charts.

PSYCHOMETRIC RULES:
- NO pure memorization — test APPLICATION and ANALYSIS.
- Correct answer must require reading the stimulus. Not guessable without it.
- 4 options: A, B, C, D.
- Each wrong option = specific misconception (MISCONCEPTION, PARTIAL_TRUTH, REVERSED_CAUSATION, SCOPE_ERROR, MAGNIFIED_DETAIL).
- NEVER repeat key words from stimulus in correct option.
- Solution: 4 sentences minimum: (1) key stimulus variable, (2) scientific principle, (3) why correct, (4) why each distractor fails.
- LaTeX for chemical formulas: $H_2O$, $CO_2$, $O_2$.

OUTPUT: Return STRICT VALID JSON ONLY. No markdown fences. No preamble. No commentary."""


def build_math_prompt(competencies: str, num_items: int, difficulty: str, diff_instr: str) -> str:
    # Parse competency list for better enforcement
    comp_lines = [l.strip() for l in competencies.strip().split('\n') if l.strip()]
    comp_count = len(comp_lines)
    
    # Determine how many items per competency
    items_per_comp = max(1, num_items // max(1, comp_count))
    remainder = num_items - items_per_comp * comp_count
    
    comp_assignment = []
    for i, comp in enumerate(comp_lines):
        count = items_per_comp + (1 if i < remainder else 0)
        comp_assignment.append(f"  - [{count} item(s)] {comp}")
    
    return f"""Generate exactly {num_items} UPCAT Mathematics items.

DIFFICULTY: {difficulty}
{diff_instr}

MANDATORY COMPETENCY ASSIGNMENT — YOU MUST FOLLOW THIS EXACTLY:
Each item must map to one of the competencies below. Generate the specified number of items per competency.
{chr(10).join(comp_assignment)}

TOTAL ITEMS REQUIRED: {num_items}

Return this exact JSON structure with exactly {num_items} items in the array:
{{
  "exam_metadata": {{
    "subtest": "Mathematics",
    "total_items": {num_items},
    "difficulty": "{difficulty}",
    "calculator_allowed": false,
    "scoring": "+1 correct, -0.25 wrong, 0 blank"
  }},
  "items": [
    {{
      "item_number": 1,
      "competency": "EXACT text of the competency this item addresses",
      "topic": "Brief topic label",
      "subtopic": "Specific concept tested",
      "grade_level_origin": "Grade 8/9/10/11",
      "question_text": "Full question using $LaTeX$ for ALL math expressions. Filipino context for word problems.",
      "stimulus": null,
      "options": {{
        "A": "$option text with LaTeX$",
        "B": "$option text with LaTeX$",
        "C": "$option text with LaTeX$",
        "D": "$option text with LaTeX$"
      }},
      "correct_answer": "C",
      "distractor_analysis": {{
        "A": {{"type": "SIGN_ERROR", "error": "Description of specific error"}},
        "B": {{"type": "ARITHMETIC_ERROR", "error": "Description of specific error"}},
        "D": {{"type": "INCOMPLETE_SOLUTION", "error": "Description of specific error"}}
      }},
      "solution": "Step 1: ... Step 2: ... Step 3: ... Step 4: ... Final answer: ...",
      "key_concept": "Core concept tested",
      "common_mistake": "Most common student error on this item type"
    }}
  ]
}}"""


def build_sci_prompt(competencies: str, num_items: int, difficulty: str, diff_instr: str) -> str:
    comp_lines = [l.strip() for l in competencies.strip().split('\n') if l.strip()]
    comp_count = len(comp_lines)
    items_per_comp = max(1, num_items // max(1, comp_count))
    remainder = num_items - items_per_comp * comp_count
    
    comp_assignment = []
    for i, comp in enumerate(comp_lines):
        count = items_per_comp + (1 if i < remainder else 0)
        comp_assignment.append(f"  - [{count} item(s)] {comp}")
    
    return f"""Generate exactly {num_items} UPCAT Science items.

DIFFICULTY: {difficulty}
{diff_instr}

MANDATORY COMPETENCY ASSIGNMENT — YOU MUST FOLLOW THIS EXACTLY:
{chr(10).join(comp_assignment)}

TOTAL ITEMS REQUIRED: {num_items}

Return this exact JSON structure:
{{
  "exam_metadata": {{
    "subtest": "Science",
    "total_items": {num_items},
    "difficulty": "{difficulty}",
    "scoring": "+1 correct, -0.25 wrong, 0 blank"
  }},
  "items": [
    {{
      "item_number": 1,
      "competency": "EXACT competency text",
      "topic": "Brief topic",
      "subtopic": "Specific concept",
      "grade_level_origin": "Grade 8/9/10",
      "science_discipline": "Biology|Chemistry|Physics|Earth Science",
      "stimulus_type": "TEXT_PASSAGE|DATA_TABLE|DIAGRAM|null",
      "stimulus": "Passage text OR HTML table with class=sci-tbl OR null",
      "chart": null,
      "question_text": "Full question. Reference specific stimulus data.",
      "options": {{
        "A": "Option text",
        "B": "Option text",
        "C": "Option text",
        "D": "Option text"
      }},
      "correct_answer": "B",
      "distractor_analysis": {{
        "A": {{"type": "MISCONCEPTION", "error": "Specific misconception"}},
        "C": {{"type": "PARTIAL_TRUTH", "error": "True but not supported by stimulus"}},
        "D": {{"type": "REVERSED_CAUSATION", "error": "Cause/effect inverted"}}
      }},
      "solution": "1. Key stimulus variable. 2. Scientific principle. 3. Why correct. 4. Why distractors fail.",
      "key_concept": "Core concept",
      "passage_reference": "Key data point from stimulus that proves the answer"
    }}
  ]
}}"""


def generate_subtest(model, system_prompt: str, user_prompt: str, name: str):
    """Generate a subtest with robust error handling."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    response = model.generate_content(full_prompt)
    raw = clean_json(response.text)
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        # Attempt to fix common issues
        # Fix trailing commas
        raw_fixed = re.sub(r',\s*([}\]])', r'\1', raw)
        # Fix single quotes
        raw_fixed = raw_fixed.replace("'", '"')
        data = json.loads(raw_fixed)
    
    if "items" not in data or not data["items"]:
        raise ValueError(f"No items in {name} response")
    
    # Post-process items to fix formatting issues
    for item in data["items"]:
        # Fix options: remove markdown bold artifacts like **A)**
        for key in ['A','B','C','D']:
            if key in item.get("options", {}):
                opt = item["options"][key]
                opt = re.sub(r'\*\*([A-D])\)\*\*\s*', '', opt)
                opt = opt.strip()
                item["options"][key] = opt
        # Ensure correct_answer is uppercase single letter
        ca = str(item.get("correct_answer", "")).strip().upper()
        if ca and ca[0] in "ABCD":
            item["correct_answer"] = ca[0]
    
    return data


def run_generation(do_math: bool, do_sci: bool):
    if not api_key:
        st.error("❌ Enter your Gemini API Key in the sidebar.")
        return
    
    math_comp = st.session_state.get('competencies_math', '').strip()
    sci_comp  = st.session_state.get('competencies_sci', '').strip()
    
    if do_math and not math_comp:
        st.error("❌ Please enter Math competencies before generating. This simulator requires you to provide DepEd MELCs/competencies.")
        return
    if do_sci and not sci_comp:
        st.error("❌ Please enter Science competencies before generating.")
        return
    
    prog = st.progress(0)
    status = st.empty()
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            gemini_model,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.75,
                "top_p": 0.92,
                "max_output_tokens": 32000,
            }
        )
        new_data = dict(st.session_state.get('test_data') or {})
        
        if do_math:
            status.info("📐 Generating Mathematics items from your competencies...")
            prog.progress(8)
            math_prompt = build_math_prompt(math_comp, math_items, difficulty, diff_instruction)
            math_d = generate_subtest(model, MATH_SYSTEM_PROMPT, math_prompt, "Mathematics")
            new_data['math'] = math_d
            prog.progress(50)
            status.success(f"✅ Math: {len(math_d['items'])} items generated!")
        
        if do_sci:
            status.info("🔬 Generating Science items from your competencies...")
            prog.progress(55 if do_math else 8)
            sci_prompt = build_sci_prompt(sci_comp, sci_items, difficulty, diff_instruction)
            sci_d = generate_subtest(model, SCI_SYSTEM_PROMPT, sci_prompt, "Science")
            new_data['sci'] = sci_d
            prog.progress(96)
            status.success(f"✅ Science: {len(sci_d['items'])} items generated!")
        
        prog.progress(100)
        m_c = len(new_data.get('math', {}).get('items', []))
        s_c = len(new_data.get('sci', {}).get('items', []))
        status.success(f"🎉 Ready — Math: {m_c} items · Science: {s_c} items · {difficulty}")
        
        st.session_state.update({
            'test_data': new_data,
            'user_answers_math': {}, 'user_answers_sci': {},
            'flagged_items': set(),
            'submitted': False,
            'math_start_time': None, 'sci_start_time': None,
            'elapsed_math': 0, 'elapsed_sci': 0,
        })
        time.sleep(0.6)
        st.rerun()
    
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON parse error — model returned malformed JSON. Try Gemini 2.5 Pro. Detail: {str(e)[:300]}")
    except Exception as e:
        st.error(f"❌ Generation error: {str(e)[:500]}")

# ==========================================
# HERO
# ==========================================
st.markdown("""
<div class="hero" role="banner">
  <div class="hero-noise"></div>
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
      135,000+ applicants. ~7.8% first-choice qualification rate. Train smarter.
    </p>
    <div class="hero-rule"></div>
    <div class="hero-stats">
      <div><div class="hs-num">135k+</div><div class="hs-lbl">Applicants / Year</div></div>
      <div><div class="hs-num">7.8%</div><div class="hs-lbl">1st Choice Rate</div></div>
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
  <div><strong>March 2026 Edition:</strong> Competency-locked generation — items are generated <em>exclusively</em> from your provided DepEd MELCs. 
  LaTeX renders properly via KaTeX. Graphs and data visualizations are auto-generated for applicable Science items. 
  UPG is a research model — not official UP methodology.</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# COMPETENCY INPUT — THE MAIN SECTION
# ==========================================
st.markdown('<div class="sec-title">📋 Competency Input (Required)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="notice sci">
  <span class="ni">🔑</span>
  <div><strong>This simulator ONLY generates questions from competencies you provide.</strong> 
  Paste DepEd MELCs (Most Essential Learning Competencies) below — one per line. 
  The AI will generate items exclusively targeting these competencies, cycling through them evenly.
  Source MELCs from <em>curriculum.deped.gov.ph</em>, your textbook table of contents, or teacher's guide.</div>
</div>
""", unsafe_allow_html=True)

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("""
    <div class="comp-wrap math">
      <div class="comp-head">🔢 Mathematics Competencies</div>
      <div class="comp-sub">One competency per line · MELCs format recommended</div>
    </div>
    """, unsafe_allow_html=True)
    math_comp_input = st.text_area(
        "Math competencies",
        value=st.session_state.get('competencies_math', ''),
        height=200,
        label_visibility="collapsed",
        placeholder="Paste your competencies here, one per line. Examples:\n\nFactors completely different types of polynomials (M8AL-Ia-b-1)\nSolves problems involving rational algebraic expressions\nIllustrates quadratic inequalities\nSolves quadratic equations by factoring\nGraphs a quadratic function with different values of a, h, and k\nSolves problems involving quadratic functions",
        key="math_comp_input_field"
    )
    st.session_state['competencies_math'] = math_comp_input
    comp_count_m = len([l for l in math_comp_input.strip().split('\n') if l.strip()])
    if comp_count_m > 0:
        st.caption(f"✅ {comp_count_m} competencies · ~{math_items} items → ~{max(1, math_items//comp_count_m)} items/competency")
    else:
        st.caption("⚠️ Enter at least 1 competency to generate Math items.")

with col_c2:
    st.markdown("""
    <div class="comp-wrap sci">
      <div class="comp-head">🔬 Science Competencies</div>
      <div class="comp-sub">One competency per line · include discipline (Bio/Chem/Physics/ES)</div>
    </div>
    """, unsafe_allow_html=True)
    sci_comp_input = st.text_area(
        "Science competencies",
        value=st.session_state.get('competencies_sci', ''),
        height=200,
        label_visibility="collapsed",
        placeholder="Paste your competencies here, one per line. Examples:\n\n[Biology] Describe the structure and functions of cell organelles\n[Biology] Explain the process of mitosis and meiosis\n[Chemistry] Balance chemical equations\n[Physics] Apply Newton's Laws to solve problems\n[Earth Science] Describe the layers of the Earth\n[Biology] Explain how photosynthesis produces glucose",
        key="sci_comp_input_field"
    )
    st.session_state['competencies_sci'] = sci_comp_input
    comp_count_s = len([l for l in sci_comp_input.strip().split('\n') if l.strip()])
    if comp_count_s > 0:
        st.caption(f"✅ {comp_count_s} competencies · ~{sci_items} items → ~{max(1, sci_items//comp_count_s)} items/competency")
    else:
        st.caption("⚠️ Enter at least 1 competency to generate Science items.")

# ==========================================
# GENERATE SECTION
# ==========================================
st.markdown('<div class="sec-title">🚀 Generate Simulation</div>', unsafe_allow_html=True)

time_m = max(10, int((math_items / 50) * 60))
time_s = max(10, int((sci_items / 45) * 45))

info_col1, info_col2 = st.columns(2)
with info_col1:
    st.markdown(f"""
    <div style='background:var(--bg1);border:1px solid var(--border2);border-top:2px solid var(--blue);border-radius:var(--r2);padding:16px 20px;'>
      <div style='font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--blue);margin-bottom:8px;'>🔢 Mathematics</div>
      <div style='font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--fg0);margin-bottom:6px;'>{math_items} Items · ~{time_m} min · No Calculator</div>
      <div style='font-family:var(--font-body);font-size:0.8rem;color:var(--fg1);line-height:1.7;'>
        72 sec/item budget · Filipino contexts · Full LaTeX rendering ·
        <strong style="color:var(--blue);">Items locked to your competencies only.</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

with info_col2:
    st.markdown(f"""
    <div style='background:var(--bg1);border:1px solid var(--border2);border-top:2px solid var(--teal);border-radius:var(--r2);padding:16px 20px;'>
      <div style='font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--teal);margin-bottom:8px;'>🔬 Science</div>
      <div style='font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--fg0);margin-bottom:6px;'>{sci_items} Items · ~{time_s} min · 60% Passage-Based</div>
      <div style='font-family:var(--font-body);font-size:0.8rem;color:var(--fg1);line-height:1.7;'>
        60 sec/item budget · Data tables · Auto-generated graphs ·
        <strong style="color:var(--teal);">Items locked to your competencies only.</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
g1, g2, g3 = st.columns([2,1,1])
with g1:
    gen_both = st.button(f"🚀 Generate Both ({math_items + sci_items} Items Total)", type="primary", use_container_width=True)
with g2:
    gen_math = st.button(f"🔢 Math Only ({math_items} items)", use_container_width=True)
with g3:
    gen_sci = st.button(f"🔬 Science Only ({sci_items} items)", use_container_width=True)

if gen_both: run_generation(True, True)
elif gen_math: run_generation(True, False)
elif gen_sci: run_generation(False, True)

# ==========================================
# EXAM INTERFACE
# ==========================================
if st.session_state.get('test_data') and not st.session_state.get('submitted'):
    test_data = st.session_state['test_data']
    math_items_data = test_data.get('math', {}).get('items', [])
    sci_items_data  = test_data.get('sci', {}).get('items', [])
    flagged = st.session_state.get('flagged_items', set())

    answered_math = len(st.session_state['user_answers_math'])
    answered_sci  = len(st.session_state['user_answers_sci'])
    total_math = len(math_items_data)
    total_sci  = len(sci_items_data)
    total_all  = total_math + total_sci
    total_ans  = answered_math + answered_sci
    pct_m = (answered_math / max(1, total_math)) * 100
    pct_s = (answered_sci  / max(1, total_sci)) * 100

    # Progress bars
    if total_math > 0 and total_sci > 0:
        pb1, pb2 = st.columns(2)
        with pb1:
            st.markdown(f"""
            <div class="pbar-wrap">
              <div class="pbar-row"><span>🔢 MATH — {answered_math}/{total_math}</span><span>{pct_m:.0f}%</span></div>
              <div class="pbar-track"><div class="pbar-fill-m" style="width:{pct_m:.1f}%"></div></div>
            </div>""", unsafe_allow_html=True)
        with pb2:
            st.markdown(f"""
            <div class="pbar-wrap">
              <div class="pbar-row"><span>🔬 SCIENCE — {answered_sci}/{total_sci}</span><span>{pct_s:.0f}%</span></div>
              <div class="pbar-track"><div class="pbar-fill-s" style="width:{pct_s:.1f}%"></div></div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="notice warn">
      <span class="ni">⚠️</span>
      <div><strong>RMW Scoring:</strong> +1.00 correct · −0.25 wrong · 0.00 blank.
      Only guess when you can eliminate ≥2 options. For Math: show work mentally — no calculator.
      For Science: read the stimulus <em>before</em> the question.</div>
    </div>
    """, unsafe_allow_html=True)

    # Timer
    if show_timer:
        active = st.session_state.get('active_subtest', 'math')
        if active == 'math' and st.session_state.get('math_start_time'):
            remaining = max(0, 3600 - int(time.time() - st.session_state['math_start_time']))
        elif active == 'sci' and st.session_state.get('sci_start_time'):
            remaining = max(0, 2700 - int(time.time() - st.session_state['sci_start_time']))
        else:
            remaining = 3600 if active == 'math' else 2700
        lbl = "🔬" if active == "sci" else "🔢"
        tcls = "s" if active == "sci" else ""
        st.components.v1.html(f"""
        <div id="tc" class="timer {tcls}">{lbl} <span id="tv">--:--</span></div>
        <style>
        .timer{{position:fixed;top:16px;right:20px;z-index:99999;font-family:'IBM Plex Mono',monospace;font-size:.9rem;font-weight:600;padding:8px 18px;border-radius:24px;border:1px solid rgba(77,159,255,.3);background:#0e1520;color:#4d9fff;box-shadow:0 4px 16px rgba(0,0,0,.5);letter-spacing:.06em;}}
        .timer.s{{color:#2dd4bf;border-color:rgba(45,212,191,.3);}}
        .timer.w{{color:#fbbf24;border-color:rgba(251,191,36,.4);}}
        .timer.d{{color:#f87171;border-color:rgba(248,113,113,.4);animation:pulse 1s infinite;}}
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

    # Tabs
    tab_labels = []
    if math_items_data: tab_labels.append(f"🔢 Math ({total_math} items · {answered_math} answered)")
    if sci_items_data:  tab_labels.append(f"🔬 Science ({total_sci} items · {answered_sci} answered)")

    if len(tab_labels) == 2:
        tab_m, tab_s = st.tabs(tab_labels)
        active_tabs = [(tab_m, 'math', math_items_data), (tab_s, 'sci', sci_items_data)]
    elif len(tab_labels) == 1:
        only = st.tabs(tab_labels)[0]
        active_tabs = [(only, 'math' if math_items_data else 'sci', math_items_data or sci_items_data)]
    else:
        active_tabs = []

    def render_subtest(tab, subtest_key, items_list):
        with tab:
            if not items_list: return
            is_math = subtest_key == 'math'
            ans_key = f'user_answers_{subtest_key}'
            dot_cls = "am" if is_math else "as"

            # Start timer
            if not st.session_state.get(f'{subtest_key}_start_time'):
                st.session_state[f'{subtest_key}_start_time'] = time.time()
                st.session_state['active_subtest'] = subtest_key

            # Navigator
            if show_nav:
                nav_html = f'<div class="nav-box"><div class="nav-title">{"Math" if is_math else "Science"} Navigator — click to scroll to item</div><div class="nav-grid">'
                for q in items_list:
                    inum = q.get('item_number')
                    fkey = f"{subtest_key}_{inum}"
                    is_a = inum in st.session_state[ans_key]
                    is_f = fkey in flagged
                    cls = "fl" if is_f else (dot_cls if is_a else "")
                    nav_html += f'<div class="nav-dot {cls}" onclick="document.getElementById(\'{subtest_key}_{inum}\').scrollIntoView({{behavior:\'smooth\'}})" title="Item {inum}">{inum}</div>'
                nav_html += '</div></div>'
                st.markdown(nav_html, unsafe_allow_html=True)

            for q in items_list:
                inum      = q.get('item_number')
                topic     = q.get('topic', '')
                subtopic  = q.get('subtopic', '')
                grade_o   = q.get('grade_level_origin', '')
                qtext     = q.get('question_text', '')
                stimulus  = q.get('stimulus', None)
                stim_type = q.get('stimulus_type', None)
                chart_data= q.get('chart', None)
                comp      = q.get('competency', '')
                is_ans    = inum in st.session_state[ans_key]
                is_flg    = f"{subtest_key}_{inum}" in flagged
                sci_disc  = q.get('science_discipline', '')

                # Card classes
                card_cls = "q-card"
                if not is_math: card_cls += " sci"
                if is_ans: card_cls += " answered"
                if is_flg: card_cls += " flagged"

                short_topic = topic[:32] + ('…' if len(topic) > 32 else '')
                short_comp  = comp[:50] + ('…' if len(comp) > 50 else '') if comp else ''

                st.markdown(f"""
                <div class="{card_cls}" id="{subtest_key}_{inum}">
                  <div class="q-meta">
                    <span class="q-badge {"math" if is_math else "sci"}">{"MTH" if is_math else "SCI"} {inum:02d}</span>
                    <span class="q-badge tag" title="{topic}">{short_topic}</span>
                    {f'<span class="q-badge tag">{grade_o}</span>' if grade_o else ''}
                    {f'<span class="q-badge tag">{sci_disc}</span>' if sci_disc and not is_math else ''}
                    {f'<span class="q-badge tag" title="{comp}">📍 {short_comp}</span>' if short_comp else ''}
                    {"<span class='q-badge flag'>🚩 Flagged</span>" if is_flg else ""}
                    {"<span class='q-badge ok'>✅ Answered</span>" if is_ans else ""}
                  </div>
                """, unsafe_allow_html=True)

                # Render stimulus
                if stimulus:
                    if stim_type == "DATA_TABLE":
                        # Ensure table has proper class
                        tbl_html = stimulus.replace('<table', '<table class="sci-tbl"')
                        st.markdown(f"""
                        <div class="stim-data">
                          <span class="stim-label d">📊 Experimental Data Table</span>
                          {tbl_html}
                        </div>
                        """, unsafe_allow_html=True)
                    elif stim_type == "DIAGRAM":
                        st.markdown(f"""
                        <div class="stim-data" style="border-left-color:var(--purple);">
                          <span class="stim-label g">🔎 Figure / Diagram</span>
                          {stimulus}
                        </div>
                        """, unsafe_allow_html=True)
                    else:  # TEXT_PASSAGE
                        st.markdown(f"""
                        <div class="stim-passage">
                          <span class="stim-label p">📄 Read carefully before answering</span>
                          {stimulus}
                        </div>
                        """, unsafe_allow_html=True)

                # Render chart if present
                if chart_data and isinstance(chart_data, dict):
                    try:
                        svg = build_svg_from_data(chart_data)
                        if svg:
                            st.markdown(f'<div class="chart-wrap">{svg}</div>', unsafe_allow_html=True)
                    except Exception:
                        pass

                # Question text — use st.markdown for KaTeX
                st.markdown(f"<div class='q-stem'>{qtext}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Answer options
                opts = q.get('options', {})
                choices = [
                    f"A)  {render_math_text(opts.get('A',''))}",
                    f"B)  {render_math_text(opts.get('B',''))}",
                    f"C)  {render_math_text(opts.get('C',''))}",
                    f"D)  {render_math_text(opts.get('D',''))}",
                ]
                choice = st.radio(
                    f"Answer {subtest_key} {inum}",
                    choices,
                    key=f"{subtest_key}_r_{inum}",
                    index=None,
                    label_visibility="collapsed"
                )
                if choice:
                    st.session_state[ans_key][inum] = choice[0].upper()

                # Flag button
                if enable_flag:
                    fkey = f"{subtest_key}_{inum}"
                    flbl = "🚩 Unflag item" if fkey in flagged else "🚩 Flag for review"
                    if st.button(flbl, key=f"fl_{subtest_key}_{inum}"):
                        if fkey in flagged: flagged.discard(fkey)
                        else: flagged.add(fkey)
                        st.session_state['flagged_items'] = flagged
                        st.rerun()

                st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:10px 0 14px;'>", unsafe_allow_html=True)

    for tab, key, items in active_tabs:
        render_subtest(tab, key, items)

    # Submit
    st.markdown("<br>", unsafe_allow_html=True)
    blank = total_all - total_ans
    flagged_count = len(flagged)
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill"><div class="sp-n" style="color:var(--green);">{total_ans}</div><div class="sp-l">Answered</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--amber);">{flagged_count}</div><div class="sp-l">Flagged</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{blank}</div><div class="sp-l">Blank (0 pts)</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--blue);">{total_all}</div><div class="sp-l">Total Items</div></div>
    </div>""", unsafe_allow_html=True)

    c1s, c2s, c3s = st.columns([1,2,1])
    with c2s:
        if blank > 0:
            st.warning(f"⚠️ {blank} unanswered — scored 0. Only guess if you can eliminate ≥2 options.")
        if flagged_count > 0:
            st.info(f"🚩 {flagged_count} flagged for review.")
        if st.button("📥 Submit & View Full UPG Report", type="primary", use_container_width=True):
            st.session_state['submitted'] = True
            if st.session_state.get('math_start_time'):
                st.session_state['elapsed_math'] = time.time() - st.session_state['math_start_time']
            if st.session_state.get('sci_start_time'):
                st.session_state['elapsed_sci'] = time.time() - st.session_state['sci_start_time']
            st.rerun()

# ==========================================
# RESULTS ENGINE
# ==========================================
if st.session_state.get('submitted') and st.session_state.get('test_data'):
    st.balloons()
    test_data     = st.session_state['test_data']
    u_math        = st.session_state.get('user_answers_math', {})
    u_sci         = st.session_state.get('user_answers_sci', {})
    elapsed_math  = st.session_state.get('elapsed_math', 0)
    elapsed_sci   = st.session_state.get('elapsed_sci', 0)
    math_items_data = test_data.get('math', {}).get('items', [])
    sci_items_data  = test_data.get('sci', {}).get('items', [])

    def score_subtest(items, user_ans):
        total    = len(items)
        correct  = sum(1 for q in items if user_ans.get(q['item_number']) == q.get('correct_answer'))
        answered = sum(1 for v in user_ans.values() if v)
        wrong    = answered - correct
        blank    = total - answered
        raw      = max(0.0, correct - 0.25 * wrong)
        pct      = raw / max(1, total)
        return total, correct, wrong, blank, raw, pct

    if math_items_data:
        m_total, m_correct, m_wrong, m_blank, m_raw, m_pct = score_subtest(math_items_data, u_math)
    else:
        m_total, m_correct, m_wrong, m_blank, m_raw, m_pct = 0,0,0,0,0.0,0.0

    if sci_items_data:
        s_total, s_correct, s_wrong, s_blank, s_raw, s_pct = score_subtest(sci_items_data, u_sci)
    else:
        s_total, s_correct, s_wrong, s_blank, s_raw, s_pct = 0,0,0,0,0.0,0.0

    # Grades
    math_grades   = [g8_math, g9_math, g10_math, g11_precalc, g11_calc, g11_stats, g11_genmath]
    sci_grades    = [g8_sci, g9_sci, g10_sci, g11_bio1, g11_bio2, g11_earth]
    math_grade_avg= float(np.mean(math_grades))
    sci_grade_avg = float(np.mean(sci_grades))
    all_grade_avg = float(np.mean(math_grades + sci_grades))
    avg_mod       = (jhs_mod + shs_mod) / 2

    def grade_to_upg(avg, mod):
        raw = 5.0 - ((avg - 75) / 25) * 4.0
        return max(1.0, min(5.0, raw - mod))

    math_grade_upg    = grade_to_upg(math_grade_avg, avg_mod)
    sci_grade_upg     = grade_to_upg(sci_grade_avg, avg_mod)
    overall_grade_upg = grade_to_upg(all_grade_avg, avg_mod)

    def upcat_to_upg(pct, mean_b, sigma_v):
        z = (pct - mean_b) / sigma_v
        return max(1.0, min(5.0, 2.75 - z * 0.55)), z

    if math_items_data:
        math_upcat_upg, math_z = upcat_to_upg(m_pct, MEAN_BASELINE, SIGMA)
    else:
        math_upcat_upg, math_z = overall_grade_upg, 0.0

    if sci_items_data:
        sci_upcat_upg, sci_z = upcat_to_upg(s_pct, MEAN_BASELINE, SIGMA)
    else:
        sci_upcat_upg, sci_z = overall_grade_upg, 0.0

    math_final_upg = (0.40 * math_grade_upg) + (0.60 * math_upcat_upg)
    sci_final_upg  = (0.40 * sci_grade_upg)  + (0.60 * sci_upcat_upg)

    if math_items_data and sci_items_data:
        combined_pct = (m_pct + s_pct) / 2
        overall_upcat_upg, combined_z = upcat_to_upg(combined_pct, MEAN_BASELINE, SIGMA)
        final_upg = (0.40 * overall_grade_upg) + (0.60 * overall_upcat_upg)
    elif math_items_data:
        combined_pct, overall_upcat_upg, combined_z = m_pct, math_upcat_upg, math_z
        final_upg = math_final_upg
    else:
        combined_pct, overall_upcat_upg, combined_z = s_pct, sci_upcat_upg, sci_z
        final_upg = sci_final_upg

    overall_pct = max(0.001, min(0.9999, 0.5 * (1 + math.erf(combined_z / math.sqrt(2)))))
    sim_rank    = int(135000 - 135000 * overall_pct)

    if   final_upg <= 1.50: verdict = "🏆 Elite — Top tier across all UP campuses."
    elif final_upg <= 2.00: verdict = "✅ Very Strong — Likely qualifies for multiple programs."
    elif final_upg <= 2.30: verdict = "📘 Competitive — Within range for several programs."
    elif final_upg <= 2.60: verdict = "🟡 Borderline — May qualify at less competitive campuses."
    elif final_upg <= 3.00: verdict = "🟠 Below Threshold — Focused improvement needed."
    else:                    verdict = "🔴 Not Yet Ready — Focus on fundamentals first."

    def analyze_topics(items, user_ans):
        td = {}
        for q in items:
            comp  = q.get('competency', q.get('topic', 'Unknown'))
            short = comp[:40] + ('…' if len(comp) > 40 else '')
            inum  = q.get('item_number')
            ok    = user_ans.get(inum) == q.get('correct_answer')
            if short not in td: td[short] = {'correct': 0, 'total': 0}
            td[short]['total'] += 1
            if ok: td[short]['correct'] += 1
        return td

    math_topics = analyze_topics(math_items_data, u_math) if math_items_data else {}
    sci_topics  = analyze_topics(sci_items_data,  u_sci)  if sci_items_data  else {}

    # ── RESULTS HERO ──
    upg_color = "#4d9fff" if final_upg <= 2.3 else ("#fbbf24" if final_upg <= 2.8 else "#f87171")
    st.markdown(f"""
    <div class="res-hero">
      <div class="res-hero-glow"></div>
      <div class="upg-label">University Predicted Grade (UPG) · {difficulty} Difficulty</div>
      <div class="upg-val" style="color:{upg_color};">{final_upg:.3f}</div>
      <div class="upg-verdict">{verdict}</div>
      <div style="color:rgba(255,255,255,0.25);font-family:var(--font-mono);font-size:0.58rem;margin-top:12px;letter-spacing:0.1em;position:relative;z-index:1;">
        Scale: 1.000 (highest) → 5.000 (lowest) · Simulated rank #{sim_rank:,} of 135,000 · Top {100*(1-overall_pct):.1f}th percentile
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SUBJECT UPG CARDS ──
    st.markdown('<div class="sec-title">📊 Subject UPG Breakdown</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="upg-cards">
      <div class="upg-card m">
        <div class="upg-card-title">🔢 Mathematics UPG</div>
        <div class="upg-card-val">{math_final_upg:.3f}</div>
        <div class="upg-card-sub">{"✅ Strong math performance" if math_final_upg<=2.3 else "⚠️ Needs improvement" if math_final_upg<=2.8 else "❌ Significant gaps"}</div>
        <div class="upg-br">
          <div class="upg-br-row"><span class="upg-br-lbl">Math Grade Avg</span><span class="upg-br-val" style="color:var(--blue);">{math_grade_avg:.1f}/100</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Grade UPG (40%)</span><span class="upg-br-val">{math_grade_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT Score (RMW)</span><span class="upg-br-val" style="color:var(--blue);">{m_pct*100:.1f}%</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT UPG (60%)</span><span class="upg-br-val">{math_upcat_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Z-score</span><span class="upg-br-val">{math_z:+.2f}σ</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Correct / Wrong / Blank</span><span class="upg-br-val">{m_correct}C · {m_wrong}W · {m_blank}B</span></div>
        </div>
      </div>
      <div class="upg-card s">
        <div class="upg-card-title">🔬 Science UPG</div>
        <div class="upg-card-val">{sci_final_upg:.3f}</div>
        <div class="upg-card-sub">{"✅ Strong science performance" if sci_final_upg<=2.3 else "⚠️ Needs improvement" if sci_final_upg<=2.8 else "❌ Significant gaps"}</div>
        <div class="upg-br">
          <div class="upg-br-row"><span class="upg-br-lbl">Science Grade Avg</span><span class="upg-br-val" style="color:var(--teal);">{sci_grade_avg:.1f}/100</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Grade UPG (40%)</span><span class="upg-br-val">{sci_grade_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT Score (RMW)</span><span class="upg-br-val" style="color:var(--teal);">{s_pct*100:.1f}%</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT UPG (60%)</span><span class="upg-br-val">{sci_upcat_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Z-score</span><span class="upg-br-val">{sci_z:+.2f}σ</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Correct / Wrong / Blank</span><span class="upg-br-val">{s_correct}C · {s_wrong}W · {s_blank}B</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRICS ──
    penalty_total = (m_wrong + s_wrong) * 0.25
    metrics = [
        (f"{final_upg:.3f}", upg_color, "Overall UPG", "Lower is better"),
        (f"#{sim_rank:,}", "var(--teal)", "Sim. Rank", f"Top {100*(1-overall_pct):.1f}%"),
        (f"{overall_grade_upg:.3f}", "var(--green)", "Grades UPG", f"Avg: {all_grade_avg:.1f}/100"),
        (f"{overall_upcat_upg:.3f}", "var(--amber)" if overall_upcat_upg > 2.5 else "var(--green)", "UPCAT UPG", f"Z: {combined_z:+.2f}"),
    ]
    if math_items_data:
        metrics.append((f"{m_pct*100:.1f}%", "var(--blue)", "Math Score", f"RMW: {m_raw:.2f}/{m_total}"))
    if sci_items_data:
        metrics.append((f"{s_pct*100:.1f}%", "var(--teal)", "Science Score", f"RMW: {s_raw:.2f}/{s_total}"))

    cols_m = st.columns(min(len(metrics), 4))
    for i, (val, clr, lbl, sub) in enumerate(metrics):
        with cols_m[i % 4]:
            st.metric(label=lbl, value=val, delta=sub)

    # ── SCORE PANELS ──
    st.markdown("<br>", unsafe_allow_html=True)
    pcols = []
    if math_items_data: pcols.append('math')
    if sci_items_data:  pcols.append('sci')
    sc = st.columns(len(pcols)) if pcols else []

    for ci, subj in enumerate(pcols):
        with sc[ci]:
            if subj == 'math':
                em, ems = int(elapsed_math//60), int(elapsed_math%60)
                budget_s = 72 * m_total
                st.markdown(f"""
                <div class="score-panel">
                  <h4>🔢 Mathematics</h4>
                  <div class="s-row"><span class="s-lbl">Correct</span><span class="s-val c">{m_correct} / {m_total}</span></div>
                  <div class="s-row"><span class="s-lbl">Wrong (−0.25 each)</span><span class="s-val w">{m_wrong} · −{m_wrong*0.25:.2f} pts</span></div>
                  <div class="s-row"><span class="s-lbl">Blank (0 pts)</span><span class="s-val">{m_blank}</span></div>
                  <div class="s-row"><span class="s-lbl">RMW Score</span><span class="s-val g">{m_raw:.2f} / {m_total}</span></div>
                  <div class="s-row"><span class="s-lbl">Percentage</span><span class="s-val g">{m_pct*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Accuracy on Attempted</span><span class="s-val">{m_correct/max(1,m_correct+m_wrong)*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Time Used</span><span class="s-val">{em}m {ems}s · {elapsed_math/max(1,m_total):.0f}s/item</span></div>
                  <div class="s-row"><span class="s-lbl">Time Status</span><span class="s-val {"c" if elapsed_math<=budget_s else "w"}">{"✅ On budget" if elapsed_math<=budget_s else "⚠️ Over budget"}</span></div>
                </div>""", unsafe_allow_html=True)
            else:
                es, ess = int(elapsed_sci//60), int(elapsed_sci%60)
                budget_ss = 60 * s_total
                st.markdown(f"""
                <div class="score-panel">
                  <h4>🔬 Science</h4>
                  <div class="s-row"><span class="s-lbl">Correct</span><span class="s-val c">{s_correct} / {s_total}</span></div>
                  <div class="s-row"><span class="s-lbl">Wrong (−0.25 each)</span><span class="s-val w">{s_wrong} · −{s_wrong*0.25:.2f} pts</span></div>
                  <div class="s-row"><span class="s-lbl">Blank (0 pts)</span><span class="s-val">{s_blank}</span></div>
                  <div class="s-row"><span class="s-lbl">RMW Score</span><span class="s-val g">{s_raw:.2f} / {s_total}</span></div>
                  <div class="s-row"><span class="s-lbl">Percentage</span><span class="s-val g">{s_pct*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Accuracy on Attempted</span><span class="s-val">{s_correct/max(1,s_correct+s_wrong)*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Time Used</span><span class="s-val">{es}m {ess}s · {elapsed_sci/max(1,s_total):.0f}s/item</span></div>
                  <div class="s-row"><span class="s-lbl">Time Status</span><span class="s-val {"c" if elapsed_sci<=budget_ss else "w"}">{"✅ On budget" if elapsed_sci<=budget_ss else "⚠️ Over budget"}</span></div>
                </div>""", unsafe_allow_html=True)

    # ── COMPETENCY HEATMAPS ──
    if math_topics or sci_topics:
        st.markdown('<div class="sec-title">🔥 Competency Mastery Heatmap</div>', unsafe_allow_html=True)
        hcols_list = [k for k in ['math', 'sci'] if (math_topics if k=='math' else sci_topics)]
        hc = st.columns(len(hcols_list))
        for hi, hs in enumerate(hcols_list):
            with hc[hi]:
                td = math_topics if hs == 'math' else sci_topics
                color = "var(--blue)" if hs == 'math' else "var(--teal)"
                lbl_h = "🔢 Math Competency Mastery" if hs == 'math' else "🔬 Science Competency Mastery"
                st.markdown(f"<h4 style='font-family:var(--font-display);font-size:0.9rem;color:{color};margin-bottom:10px;'>{lbl_h}</h4>", unsafe_allow_html=True)
                rows = sorted(td.items(), key=lambda x: x[1]['correct']/max(1,x[1]['total']))
                html = "<div class='heat-grid'>"
                for sk, data in rows:
                    pct_sk = data['correct']/max(1,data['total'])*100
                    cls_b = "hi" if pct_sk>=70 else ("mid" if pct_sk>=40 else "lo")
                    pc = "var(--green)" if cls_b=="hi" else ("var(--amber)" if cls_b=="mid" else "var(--red)")
                    sk_s = sk[:34]+'…' if len(sk)>34 else sk
                    html += f"""
                    <div class="heat-row" title="{sk}">
                      <span style="flex:1;color:var(--fg1);font-size:0.73rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{sk_s}</span>
                      <div class="heat-bar-out"><div class="heat-bar-in {cls_b}" style="width:{pct_sk:.0f}%;"></div></div>
                      <span class="heat-pct" style="color:{pc};">{pct_sk:.0f}%</span>
                    </div>"""
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)

    # ── ADMISSION ENGINE ──
    st.markdown('<div class="sec-title">🏛️ UP Admission Decision Engine</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="notice">
      <span class="ni">📊</span>
      <div><strong>UPCAT 2025 Data:</strong> 17,996 of 135,236 applicants qualified (13.3% total, ~7.8% direct program).
      Your simulated UPG of <strong>{final_upg:.3f}</strong> → rank <strong>#{sim_rank:,}</strong>.
      Admission is campus-first, then program-specific within campus.</div>
    </div>""", unsafe_allow_html=True)

    def evaluate_program(campus, program, cutoff, upg):
        tier = get_program_tier(campus, program)
        adj = {"Triple Quota": -0.40, "Double Quota": -0.22, "Single Quota": -0.06, "Less Popular": +0.08}.get(tier, 0.0)
        req = max(1.100, cutoff + adj)
        if upg <= req:
            return "<span class='badge pass'>✅ PASSED</span>", req, tier
        elif upg <= req + 0.14:
            return "<span class='badge risk'>🟡 DPWAS RISK</span>", req, tier
        else:
            return "<span class='badge fail'>❌ BELOW CUTOFF</span>", req, tier

    acol1, acol2 = st.columns(2)
    for acol, campus, progs, cn in [
        (acol1, campus_1, [c1_p1, c1_p2, c1_p3], "1st"),
        (acol2, campus_2, [c2_p1, c2_p2, c2_p3], "2nd"),
    ]:
        cutoff = CAMPUS_DATA[campus]["cutoff"]
        qualified = final_upg <= cutoff
        with acol:
            st.markdown(f"""
            <div class="campus-card">
              <div class="campus-hdr {"" if qualified else "fail"}">
                <h4>{cn} Choice — {campus}</h4>
                <p>Cutoff: {cutoff:.3f} · Your UPG: {final_upg:.3f} · {"✅ QUALIFIED" if qualified else "❌ NOT QUALIFIED"} · {CAMPUS_DATA[campus]["note"]}</p>
              </div>
              <div class="campus-body">""", unsafe_allow_html=True)
            if campus == campus_2 and final_upg <= CAMPUS_DATA[campus_1]["cutoff"]:
                st.info("📌 Already qualified at 1st campus — 2nd is null in cascading system.")
            if qualified:
                for i, prog in enumerate(progs, 1):
                    badge, req, tier = evaluate_program(campus, prog, cutoff, final_upg)
                    st.markdown(f"""
                    <div class="prog-row">
                      <div>
                        <div class="prog-name">P{i}: {prog}</div>
                        <div class="prog-sub">{tier} · Eff. cutoff ~{req:.3f}</div>
                      </div>
                      <div>{badge}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                recon = CAMPUS_DATA[campus]["recon"]
                recon_ok = recon > 0 and final_upg <= recon
                st.markdown(f"""
                <div style="padding:14px;text-align:center;font-family:var(--font-body);font-size:0.85rem;color:var(--fg1);">
                  UPG {final_upg:.3f} exceeds cutoff {cutoff:.3f}.<br><br>
                  Recon window: <strong>{f"{recon:.3f}" if recon > 0 else "None"}</strong><br>
                  {"✅ Recon-eligible" if recon_ok else ("❌ Beyond recon range" if recon > 0 else "🚫 No appeals policy")}
                </div>""", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ── ITEM REVIEW TABS ──
    st.markdown('<div class="sec-title">🔬 Detailed Item Review & Feedback</div>', unsafe_allow_html=True)

    tab_res_labels = ["📊 Performance Overview", "🧮 UPG Formula"]
    if math_items_data: tab_res_labels.append("🔢 Math Review")
    if sci_items_data:  tab_res_labels.append("🔬 Science Review")
    tab_res_labels.append("⚖️ Recon & DPWAS")
    tabs_r = st.tabs(tab_res_labels)
    ti = 0

    # Overview
    with tabs_r[ti]:
        guess_rate = (m_wrong + s_wrong) / max(1, m_correct+m_wrong+s_correct+s_wrong)
        math_err = {k: (1-v['correct']/max(1,v['total']))*100 for k,v in math_topics.items()}
        sci_err  = {k: (1-v['correct']/max(1,v['total']))*100 for k,v in sci_topics.items()}
        top_m_gaps = sorted(math_err.items(), key=lambda x:-x[1])[:5]
        top_s_gaps = sorted(sci_err.items(), key=lambda x:-x[1])[:5]

        st.markdown(f"""
        <div class="notice green">
          <span class="ni">📊</span>
          <div>
            <strong>Performance Summary — {difficulty} Difficulty</strong><br>
            You placed at the <strong>{overall_pct*100:.1f}th percentile</strong> (Rank #{sim_rank:,} of 135,000).
            Combined UPCAT score: <strong>{combined_pct*100:.1f}%</strong> vs competitive mean {MEAN_BASELINE*100:.0f}% (σ={SIGMA:.2f}).
            Z-score: <strong>{combined_z:+.2f}</strong>.
            Total penalty from wrong guesses: <strong>−{penalty_total:.2f} pts</strong>
            ({f"✅ Well-controlled guessing." if guess_rate<0.22 else "⚠️ Moderate over-guessing." if guess_rate<0.38 else "🔴 Aggressive guessing hurting score."})
          </div>
        </div>""", unsafe_allow_html=True)

        if top_m_gaps:
            st.markdown("""<div class="notice warn"><span class="ni">🔢</span><div><strong>Math Competency Gaps (highest error rate first):</strong><br>""" +
                "<br>".join(f"• {k} — {e:.0f}% error rate" for k,e in top_m_gaps) +
                "</div></div>", unsafe_allow_html=True)
        if top_s_gaps:
            st.markdown("""<div class="notice sci"><span class="ni">🔬</span><div><strong>Science Competency Gaps (highest error rate first):</strong><br>""" +
                "<br>".join(f"• {k} — {e:.0f}% error rate" for k,e in top_s_gaps) +
                "</div></div>", unsafe_allow_html=True)
    ti += 1

    # UPG Formula
    with tabs_r[ti]:
        st.markdown("#### 🧮 UPG Derivation")
        with st.expander("Full Math UPG Derivation"):
            st.latex(f"\\text{{RMW}}_{{\\text{{Math}}}} = {m_correct} - \\frac{{1}}{{4}} \\times {m_wrong} = {m_raw:.2f}")
            st.latex(f"Z_{{\\text{{Math}}}} = \\frac{{{m_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {math_z:.4f}")
            st.latex(f"UPG_{{\\text{{UPCAT,Math}}}} = 2.75 - ({math_z:.4f} \\times 0.55) = {math_upcat_upg:.3f}")
            st.latex(f"UPG_{{\\text{{Math}}}} = 0.40 \\times {math_grade_upg:.3f} + 0.60 \\times {math_upcat_upg:.3f} = {math_final_upg:.3f}")
        with st.expander("Full Science UPG Derivation"):
            st.latex(f"\\text{{RMW}}_{{\\text{{Sci}}}} = {s_correct} - \\frac{{1}}{{4}} \\times {s_wrong} = {s_raw:.2f}")
            st.latex(f"Z_{{\\text{{Sci}}}} = \\frac{{{s_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {sci_z:.4f}")
            st.latex(f"UPG_{{\\text{{Sci}}}} = 0.40 \\times {sci_grade_upg:.3f} + 0.60 \\times {sci_upcat_upg:.3f} = {sci_final_upg:.3f}")
        with st.expander("Overall UPG"):
            st.latex(f"UPG_{{\\text{{Overall}}}} = 0.40 \\times {overall_grade_upg:.3f} + 0.60 \\times {overall_upcat_upg:.3f} = {final_upg:.3f}")
        with st.expander("Grade UPG Formula"):
            st.latex(r"UPG_{\text{grade}} = 5.0 - \left(\frac{\bar{G} - 75}{25}\right) \times 4.0 - \Delta_{\text{school}}")
            st.markdown(f"Math grade avg: **{math_grade_avg:.2f}** · School modifier: **{avg_mod:+.3f}** · Palugit: **{'Active' if palugit_active else 'Not Active'}**")
    ti += 1

    # Math Item Review
    if math_items_data:
        with tabs_r[ti]:
            st.markdown("### 🔢 Mathematics — Item-by-Item Review")
            m_w = [q for q in math_items_data if u_math.get(q['item_number']) not in [None,''] and u_math.get(q['item_number']) != q.get('correct_answer')]
            m_c_list = [q for q in math_items_data if u_math.get(q['item_number']) == q.get('correct_answer')]
            m_b = [q for q in math_items_data if not u_math.get(q['item_number'])]
            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-pill"><div class="sp-n" style="color:var(--red);">{len(m_w)}</div><div class="sp-l">Wrong −0.25ea</div></div>
              <div class="stat-pill"><div class="sp-n" style="color:var(--green);">{len(m_c_list)}</div><div class="sp-l">Correct +1ea</div></div>
              <div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{len(m_b)}</div><div class="sp-l">Blank 0pts</div></div>
            </div>""", unsafe_allow_html=True)

            for label, items_subset, show_sol in [
                (f"❌ Wrong ({len(m_w)}) — Priority Review", m_w, True),
                (f"✅ Correct ({len(m_c_list)})", m_c_list, False),
                (f"⚪ Skipped ({len(m_b)})", m_b, True),
            ]:
                if not items_subset: continue
                st.markdown(f"#### {label}")
                for q in items_subset:
                    inum = q['item_number']
                    u    = u_math.get(inum)
                    c    = q.get('correct_answer')
                    comp = q.get('competency', q.get('topic', ''))[:60]
                    status_str = f"Chose {u} → Correct: {c}" if u and u != c else ("✅ Correct" if u == c else "⚪ Skipped")
                    with st.expander(f"MTH {inum:02d} · {comp} · {status_str}"):
                        st.markdown(f"<div class='q-stem'>{q.get('question_text','')}</div>", unsafe_allow_html=True)
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {render_math_text(opts.get(lt,''))}"
                            if lt == c:
                                st.markdown(f'<div class="ir-c">✅ {txt}</div>', unsafe_allow_html=True)
                            elif lt == u:
                                st.markdown(f'<div class="ir-w">❌ {txt} ← Your answer</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="ir-o">{txt}</div>', unsafe_allow_html=True)
                        da = q.get('distractor_analysis', {})
                        if da and u and u in da and u != c:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Error ({err.get('type','')}):** {err.get('error','')}")
                        if show_sol or u == c:
                            sol = q.get('solution','')
                            if sol:
                                st.info(f"**📐 Solution:**\n\n{sol}")
                            kc = q.get('key_concept','')
                            if kc: st.caption(f"💡 Core concept: {kc}")
                            cm = q.get('common_mistake','')
                            if cm: st.caption(f"⚠️ Common mistake: {cm}")
        ti += 1

    # Science Item Review
    if sci_items_data:
        with tabs_r[ti]:
            st.markdown("### 🔬 Science — Item-by-Item Review")
            s_w = [q for q in sci_items_data if u_sci.get(q['item_number']) not in [None,''] and u_sci.get(q['item_number']) != q.get('correct_answer')]
            s_c_list = [q for q in sci_items_data if u_sci.get(q['item_number']) == q.get('correct_answer')]
            s_b = [q for q in sci_items_data if not u_sci.get(q['item_number'])]
            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-pill"><div class="sp-n" style="color:var(--red);">{len(s_w)}</div><div class="sp-l">Wrong −0.25ea</div></div>
              <div class="stat-pill"><div class="sp-n" style="color:var(--green);">{len(s_c_list)}</div><div class="sp-l">Correct +1ea</div></div>
              <div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{len(s_b)}</div><div class="sp-l">Blank 0pts</div></div>
            </div>""", unsafe_allow_html=True)

            for label, items_subset, show_sol in [
                (f"❌ Wrong ({len(s_w)}) — Priority Review", s_w, True),
                (f"✅ Correct ({len(s_c_list)})", s_c_list, False),
                (f"⚪ Skipped ({len(s_b)})", s_b, True),
            ]:
                if not items_subset: continue
                st.markdown(f"#### {label}")
                for q in items_subset:
                    inum = q['item_number']
                    u    = u_sci.get(inum)
                    c    = q.get('correct_answer')
                    comp = q.get('competency', q.get('topic', ''))[:55]
                    disc = q.get('science_discipline', '')
                    status_str = f"Chose {u} → Correct: {c}" if u and u != c else ("✅ Correct" if u == c else "⚪ Skipped")
                    with st.expander(f"SCI {inum:02d} · {comp} [{disc}] · {status_str}"):
                        stim = q.get('stimulus','')
                        if stim:
                            stim_t = q.get('stimulus_type','')
                            if stim_t == "DATA_TABLE":
                                tbl = stim.replace('<table', '<table class="sci-tbl"')
                                st.markdown(f'<div class="stim-data">{tbl}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="stim-passage">{stim}</div>', unsafe_allow_html=True)
                        chart_data = q.get('chart', None)
                        if chart_data and isinstance(chart_data, dict):
                            try:
                                svg = build_svg_from_data(chart_data)
                                if svg:
                                    st.markdown(f'<div class="chart-wrap">{svg}</div>', unsafe_allow_html=True)
                            except Exception:
                                pass
                        st.markdown(f"<div class='q-stem'>{q.get('question_text','')}</div>", unsafe_allow_html=True)
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {opts.get(lt,'')}"
                            if lt == c:
                                st.markdown(f'<div class="ir-c">✅ {txt}</div>', unsafe_allow_html=True)
                            elif lt == u:
                                st.markdown(f'<div class="ir-w">❌ {txt} ← Your answer</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="ir-o">{txt}</div>', unsafe_allow_html=True)
                        da = q.get('distractor_analysis', {})
                        if da and u and u in da and u != c:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Why {u} is wrong ({err.get('type','')}):** {err.get('error','')}")
                        if show_sol or u == c:
                            sol = q.get('solution','')
                            if sol: st.info(f"**🔬 Explanation:**\n\n{sol}")
                            pr = q.get('passage_reference','')
                            if pr: st.caption(f"📍 Key stimulus data: {pr}")
                            kc = q.get('key_concept','')
                            if kc: st.caption(f"💡 Core concept: {kc}")
        ti += 1

    # Recon & DPWAS
    with tabs_r[ti]:
        st.markdown("### ⚖️ DPWAS, Reconsideration & Cascading Admission")
        st.markdown(f"""
        <div class="notice">
          <span class="ni">📋</span>
          <div>
            <strong>UPCAT 2025:</strong> 17,996 admission notices of 135,236 applicants (13.3%).
            ~10,600 were direct degree-program qualifiers (~7.8%). ~7,400 were DPWAS (waitlisted).
            Being waitlisted is NOT rejection — slots open as accepted students decline or fail to enroll.<br><br>
            <strong>Cascading:</strong> If qualified at Campus 1 → Campus 2 is void.
            If failed all programs at Campus 1 → cascade to Campus 2.
            Program slots filled by UPG rank within each campus.
          </div>
        </div>""", unsafe_allow_html=True)
        for campus in [campus_1, campus_2]:
            recon  = CAMPUS_DATA[campus]["recon"]
            cutoff = CAMPUS_DATA[campus]["cutoff"]
            st.markdown(f"**{campus}** — Cutoff: `{cutoff:.3f}` · Recon ceiling: `{f'{recon:.3f}' if recon > 0 else 'N/A'}`")
            if recon == 0.0:
                st.error(f"🚫 {campus}: Absolute no-appeal policy. No reconsideration.")
            elif final_upg <= cutoff:
                st.success(f"✅ Qualified ({final_upg:.3f} ≤ {cutoff:.3f}). No recon needed.")
            elif final_upg <= recon:
                st.warning(f"📋 Recon-eligible: UPG {final_upg:.3f} within window ({cutoff:.3f}–{recon:.3f}). Not guaranteed — subject to slot availability.")
            else:
                st.error(f"❌ UPG {final_upg:.3f} exceeds recon ceiling {recon:.3f}.")

    # ── RESET ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns([1,2,1])
    with rc2:
        st.markdown("""<div style='text-align:center;font-family:var(--font-body);font-size:0.8rem;color:var(--fg2);margin-bottom:10px;'>
          Generate a fresh set of items — competencies and sidebar settings preserved.
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Generate Fresh Items & Reset", use_container_width=True, type="secondary"):
            for k in ['user_answers_math','user_answers_sci','submitted','test_data','flagged_items',
                      'math_start_time','sci_start_time','elapsed_math','elapsed_sci']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
