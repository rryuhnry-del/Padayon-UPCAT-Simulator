import streamlit as st
import google.generativeai as genai
import json
import time
import math
import numpy as np
import random

# ==========================================
# 🛡️ SESSION STATE INIT
# ==========================================
defaults = {
    'user_answers_math': {}, 'user_answers_sci': {},
    'submitted': False, 'test_data': None,
    'start_time': None, 'time_limit_math': 0, 'time_limit_sci': 0,
    'elapsed_math': 0, 'elapsed_sci': 0,
    'generation_error': None,
    'flagged_items': set(),
    'font_size': 'medium', 'high_contrast': False,
    'active_subtest': 'math',
    'math_started': False, 'sci_started': False,
    'math_submitted': False, 'sci_submitted': False,
    'math_start_time': None, 'sci_start_time': None,
    'custom_competencies_math': '', 'custom_competencies_sci': '',
    'use_custom_math': False, 'use_custom_sci': False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==========================================
# 🏛️ PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Padayon! Agham at Matematika — UPCAT Elite Simulator",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

FONT_SIZES = {'small': '0.875rem', 'medium': '1.0rem', 'large': '1.125rem', 'x-large': '1.25rem'}
fs = FONT_SIZES.get(st.session_state.get('font_size', 'medium'), '1.0rem')
hc = st.session_state.get('high_contrast', False)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=DM+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&display=swap');

:root {{
    --navy: #0a1628;
    --navy-mid: #132040;
    --navy-light: #1e3260;
    --blue: #1a56db;
    --blue-pale: #eef2ff;
    --teal: #0e7490;
    --teal-pale: #ecfeff;
    --green: #065f46;
    --green-pale: #ecfdf5;
    --green-mid: #047857;
    --amber: #92400e;
    --amber-pale: #fffbeb;
    --red: #991b1b;
    --red-pale: #fef2f2;
    --purple: #5b21b6;
    --purple-pale: #f5f3ff;
    --gold: #b45309;
    --gold-pale: #fef3c7;
    --bg: #f0f4f8;
    --bg-card: #ffffff;
    --bg-card2: #f8fafc;
    --fg: #0f172a;
    --fg-mid: #334155;
    --fg-mute: #64748b;
    --border: #e2e8f0;
    --border-light: #f1f5f9;
    --shadow-xs: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-sm: 0 4px 6px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.04);
    --shadow-md: 0 10px 15px rgba(0,0,0,0.07), 0 4px 6px rgba(0,0,0,0.05);
    --shadow-lg: 0 20px 25px rgba(0,0,0,0.08), 0 10px 10px rgba(0,0,0,0.04);
    --r: 10px; --r-lg: 16px; --r-xl: 20px;
    --font-display: 'Crimson Pro', Georgia, serif;
    --font-body: 'Source Serif 4', Georgia, serif;
    --font-ui: 'DM Sans', sans-serif;
    --font-mono: 'IBM Plex Mono', monospace;
    --base-font-size: {fs};
    --transition: 0.16s cubic-bezier(0.4,0,0.2,1);
}}
{'body {{ filter: contrast(1.22); }}' if hc else ''}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

.stApp {{
    background: var(--bg) !important;
    font-family: var(--font-body) !important;
    color: var(--fg) !important;
    font-size: var(--base-font-size) !important;
}}

.skip-link {{
    position: absolute; top: -120px; left: 12px; z-index: 99999;
    background: var(--navy); color: #fff; padding: 10px 18px;
    border-radius: 0 0 8px 8px; font-family: var(--font-ui);
    font-weight: 600; font-size: 0.875rem; text-decoration: none;
    transition: top 0.2s;
}}
.skip-link:focus {{ top: 0; outline: 3px solid var(--gold); }}

*:focus-visible {{
    outline: 3px solid var(--blue) !important;
    outline-offset: 2px !important;
    border-radius: 4px !important;
}}

#MainMenu, footer {{ visibility: hidden; }}
.block-container {{
    padding-top: 1.25rem !important;
    padding-bottom: 4rem !important;
    max-width: 1340px !important;
}}

h1,h2,h3,h4,h5,h6 {{
    font-family: var(--font-display) !important;
    color: var(--fg) !important; font-weight: 700 !important;
}}
p, li, span {{ font-family: var(--font-body); line-height: 1.75; }}
.stMarkdown, .stText {{ color: var(--fg) !important; }}

/* ═══════════ HERO ═══════════ */
.hero-wrap {{
    position: relative; border-radius: var(--r-xl);
    overflow: hidden; margin-bottom: 18px; box-shadow: var(--shadow-lg);
}}
.hero-bg {{
    position: absolute; inset: 0;
    background: linear-gradient(135deg, #050d1c 0%, #0a1e3d 40%, #0d2d5e 70%, #0e3a6b 100%);
}}
.hero-accent {{
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 50% 60% at 90% 10%, rgba(29,78,216,0.25) 0%, transparent 55%),
        radial-gradient(ellipse 40% 50% at 5% 90%, rgba(16,185,129,0.15) 0%, transparent 50%);
}}
.hero-grid {{
    position: absolute; inset: 0; opacity: 0.04;
    background-image:
        linear-gradient(rgba(255,255,255,1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px);
    background-size: 40px 40px;
}}
.hero-inner {{
    position: relative; z-index: 2;
    padding: 40px 52px;
}}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(59,130,246,0.18); border: 1px solid rgba(59,130,246,0.35);
    color: #93c5fd !important; font-family: var(--font-mono);
    font-size: 0.66rem; font-weight: 600; letter-spacing: 0.16em;
    text-transform: uppercase; padding: 5px 14px; border-radius: 20px; margin-bottom: 14px;
}}
.hero-title {{
    font-family: var(--font-display) !important;
    font-size: clamp(1.75rem, 3.2vw, 2.8rem) !important;
    font-weight: 900 !important; color: #fff !important;
    line-height: 1.1 !important; margin-bottom: 10px !important;
    letter-spacing: -0.02em;
}}
.hero-title em {{ font-style: italic; color: #60a5fa !important; }}
.hero-sub {{
    font-family: var(--font-ui); font-size: 0.9rem;
    color: rgba(255,255,255,0.6); line-height: 1.65; max-width: 580px;
}}
.hero-stats-row {{
    display: flex; gap: 24px; margin-top: 26px;
    padding-top: 22px; border-top: 1px solid rgba(255,255,255,0.1);
    flex-wrap: wrap;
}}
.hero-stat {{ text-align: left; }}
.hero-stat-num {{
    font-family: var(--font-display); font-size: 1.6rem;
    font-weight: 900; color: #60a5fa !important; line-height: 1;
}}
.hero-stat-label {{
    font-family: var(--font-ui); font-size: 0.68rem;
    color: rgba(255,255,255,0.45); text-transform: uppercase;
    letter-spacing: 0.1em; margin-top: 3px;
}}

/* ═══════════ SIDEBAR ═══════════ */
section[data-testid="stSidebar"] {{
    background: var(--navy) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}}
section[data-testid="stSidebar"] > div {{ padding: 0 !important; }}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.8) !important; }}
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] strong {{ color: #fff !important; }}
section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.09) !important; }}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] textarea {{
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.15) !important;
    color: #fff !important; border-radius: 7px !important;
}}
section[data-testid="stSidebar"] *:focus-visible {{
    outline: 3px solid #60a5fa !important;
}}
.sb-logo {{
    background: rgba(0,0,0,0.3); padding: 22px 18px 16px;
    text-align: center; border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 4px;
}}
.sb-heading {{
    font-family: var(--font-mono) !important; font-size: 0.60rem !important;
    letter-spacing: 0.2em !important; text-transform: uppercase !important;
    color: rgba(255,255,255,0.3) !important; margin: 16px 0 8px !important;
    display: block; padding: 0 18px;
}}

/* ═══════════ DISCLAIMER / NOTICE ═══════════ */
.notice {{
    background: var(--blue-pale); border: 1px solid rgba(29,78,216,0.2);
    border-left: 4px solid var(--blue); border-radius: var(--r);
    padding: 12px 18px; font-family: var(--font-ui); font-size: 0.82rem;
    color: var(--fg-mid); line-height: 1.65; margin-bottom: 18px;
}}
.notice-warn {{
    background: var(--amber-pale); border: 1px solid rgba(180,83,9,0.2);
    border-left: 4px solid var(--gold);
}}
.notice-rmw {{
    background: var(--red-pale); border: 1px solid rgba(153,27,27,0.2);
    border-left: 4px solid var(--red);
}}

/* ═══════════ SUBTEST SELECTOR CARDS ═══════════ */
.subtest-cards {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px;
}}
.subtest-card {{
    background: var(--bg-card); border: 2px solid var(--border);
    border-radius: var(--r-lg); padding: 22px 24px;
    cursor: pointer; transition: all var(--transition);
    box-shadow: var(--shadow-xs);
}}
.subtest-card:hover {{ border-color: var(--blue); box-shadow: var(--shadow-md); transform: translateY(-2px); }}
.subtest-card.active {{ border-color: var(--blue); background: var(--blue-pale); box-shadow: var(--shadow-sm); }}
.subtest-card.math-card.active {{ border-color: #1a56db; background: #eff6ff; }}
.subtest-card.sci-card.active {{ border-color: #0e7490; background: #ecfeff; }}
.subtest-card-icon {{ font-size: 1.8rem; margin-bottom: 8px; }}
.subtest-card-title {{
    font-family: var(--font-display); font-size: 1.15rem;
    font-weight: 700; color: var(--fg); margin-bottom: 4px;
}}
.subtest-card-meta {{
    font-family: var(--font-mono); font-size: 0.62rem;
    color: var(--fg-mute); letter-spacing: 0.08em; text-transform: uppercase;
}}
.subtest-card-detail {{
    font-family: var(--font-ui); font-size: 0.78rem;
    color: var(--fg-mid); margin-top: 8px; line-height: 1.55;
}}

/* ═══════════ STAT PILL ═══════════ */
.stat-pill {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 12px 16px;
    text-align: center; box-shadow: var(--shadow-xs);
}}
.stat-pill-num {{ font-family: var(--font-display); font-size: 1.4rem; font-weight: 900; line-height: 1; }}
.stat-pill-label {{ font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg-mute); margin-top: 3px; }}

/* ═══════════ PROGRESS ═══════════ */
.prog-outer {{ margin: 12px 0 18px; }}
.prog-meta {{
    display: flex; justify-content: space-between;
    font-family: var(--font-mono); font-size: 0.66rem;
    color: var(--fg-mute); letter-spacing: 0.05em; margin-bottom: 5px;
}}
.prog-track {{ height: 6px; background: var(--border); border-radius: 4px; overflow: hidden; }}
.prog-math {{ height: 100%; border-radius: 4px; background: linear-gradient(90deg, #1d4ed8, #3b82f6); transition: width 0.5s ease; }}
.prog-sci {{ height: 100%; border-radius: 4px; background: linear-gradient(90deg, #0e7490, #06b6d4); transition: width 0.5s ease; }}
.legend-dot {{ width: 9px; height: 9px; border-radius: 2px; display: inline-block; margin-right: 4px; }}
.status-legend {{ display: flex; gap: 14px; align-items: center; font-family: var(--font-mono); font-size: 0.60rem; color: var(--fg-mute); letter-spacing: 0.06em; text-transform: uppercase; padding: 6px 0; flex-wrap: wrap; }}

/* ═══════════ QUESTION CARDS ═══════════ */
.q-card {{
    background: var(--bg-card); border: 1.5px solid var(--border);
    border-left: 4px solid #3b82f6; border-radius: var(--r);
    padding: 20px 24px; margin-bottom: 10px; box-shadow: var(--shadow-xs);
    transition: border-left-color var(--transition), box-shadow var(--transition), transform var(--transition);
    position: relative;
}}
.q-card:hover {{ box-shadow: var(--shadow-sm); transform: translateY(-1px); }}
.q-card.answered {{ border-left-color: var(--green-mid); }}
.q-card.flagged {{ border-left-color: #f59e0b; border-left-width: 4px; }}
.q-card.sci-card {{ border-left-color: #0e7490; }}
.q-card.sci-card.answered {{ border-left-color: var(--green-mid); }}

.q-meta {{ display: flex; align-items: center; gap: 7px; margin-bottom: 10px; flex-wrap: wrap; }}
.q-num {{ font-family: var(--font-mono); font-size: 0.60rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #1d4ed8; }}
.q-num.sci {{ color: #0e7490; }}
.q-tag {{
    display: inline-block; font-family: var(--font-mono); font-size: 0.56rem;
    font-weight: 600; letter-spacing: 0.07em; padding: 2px 8px; border-radius: 10px;
}}
.q-tag-topic {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }}
.q-tag-topic-sci {{ background: #ecfeff; color: #0e7490; border: 1px solid #a5f3fc; }}
.q-tag-grade {{ background: #f0fdf4; color: var(--green); border: 1px solid #bbf7d0; }}
.q-tag-type {{ background: #f5f3ff; color: var(--purple); border: 1px solid #ddd6fe; }}
.q-stem {{
    font-family: var(--font-body); font-size: var(--base-font-size);
    line-height: 1.85; color: var(--fg); margin-bottom: 12px;
}}
/* Math rendering — clean, no artifacts */
.q-stem .katex {{ font-size: 1.05em !important; }}
.math-display {{
    background: var(--bg-card2); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px 20px; margin: 10px 0;
    text-align: center; font-size: 1.1rem; overflow-x: auto;
}}
/* Science data box */
.sci-data-box {{
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 1.5px solid #7dd3fc; border-radius: 10px;
    padding: 14px 18px; margin: 10px 0;
    font-family: var(--font-mono); font-size: 0.82rem; line-height: 1.7;
    color: var(--fg-mid); overflow-x: auto;
}}
.sci-table {{
    width: 100%; border-collapse: collapse; font-family: var(--font-ui);
    font-size: 0.82rem; margin: 8px 0;
}}
.sci-table th {{
    background: #1e3a5f; color: #fff; padding: 8px 12px;
    font-weight: 600; text-align: left; font-size: 0.75rem;
    letter-spacing: 0.04em;
}}
.sci-table td {{
    padding: 7px 12px; border-bottom: 1px solid var(--border);
    color: var(--fg-mid);
}}
.sci-table tr:nth-child(even) td {{ background: var(--bg-card2); }}
.sci-passage {{
    background: var(--bg-card2); border: 1px solid var(--border);
    border-left: 3px solid #0e7490; border-radius: 8px;
    padding: 16px 20px; margin: 10px 0;
    font-family: var(--font-body); font-size: 0.92rem; line-height: 1.9;
    color: var(--fg-mid); max-height: 280px; overflow-y: auto;
}}

/* ═══════════ RADIO ═══════════ */
.stRadio > label {{ display: none !important; }}
.stRadio [data-testid="stWidgetLabel"] {{ display: none !important; }}
.stRadio > div {{ display: flex !important; flex-direction: column !important; gap: 5px !important; }}
.stRadio > div > label {{
    background: var(--bg-card2) !important; border: 1.5px solid var(--border) !important;
    border-radius: 8px !important; padding: 10px 15px !important;
    cursor: pointer !important; transition: all var(--transition) !important;
    font-family: var(--font-body) !important; font-size: var(--base-font-size) !important;
    line-height: 1.6 !important; color: var(--fg) !important;
}}
.stRadio > div > label:hover {{
    border-color: #3b82f6 !important; background: #eff6ff !important;
    transform: translateX(2px) !important;
}}
.stRadio > div > label[data-checked="true"] {{
    border-color: var(--green-mid) !important;
    background: var(--green-pale) !important; color: var(--green) !important;
}}

/* ═══════════ ITEM NAVIGATOR ═══════════ */
.item-nav {{
    position: sticky; top: 10px; z-index: 100;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 12px 16px;
    box-shadow: var(--shadow-sm); margin-bottom: 16px;
}}
.item-nav-title {{
    font-family: var(--font-mono); font-size: 0.60rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--fg-mute); margin-bottom: 9px;
}}
.item-nav-grid {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.nav-dot {{
    min-width: 34px; height: 28px; border-radius: 5px; display: inline-flex;
    align-items: center; justify-content: center;
    font-family: var(--font-mono); font-size: 0.58rem; font-weight: 700;
    cursor: pointer; border: 1.5px solid var(--border);
    background: var(--bg-card2); color: var(--fg-mute);
    transition: all var(--transition);
}}
.nav-dot:hover {{ border-color: #3b82f6; color: #1d4ed8; transform: scale(1.1); }}
.nav-dot.answered {{ background: var(--green-mid); color: #fff; border-color: var(--green-mid); }}
.nav-dot.flagged {{ background: #f59e0b; color: #fff; border-color: #f59e0b; }}
.nav-dot.sci-answered {{ background: #0e7490; color: #fff; border-color: #0e7490; }}

/* ═══════════ TIMER ═══════════ */
#upcat-timer {{
    position: fixed; top: 18px; right: 22px; z-index: 99999;
    background: #1d4ed8; color: #fff;
    font-family: var(--font-mono); font-size: 0.95rem; font-weight: 700;
    padding: 8px 18px; border-radius: 28px;
    box-shadow: 0 4px 16px rgba(29,78,216,0.4);
    letter-spacing: 0.05em; border: 2px solid rgba(255,255,255,0.18);
    transition: background 0.3s;
}}
#upcat-timer.sci {{ background: #0e7490; box-shadow: 0 4px 16px rgba(14,116,144,0.4); }}
#upcat-timer.warn {{ background: #d97706; }}
#upcat-timer.danger {{ background: #dc2626; }}

/* ═══════════ BUTTONS ═══════════ */
.stButton > button {{
    font-family: var(--font-ui) !important; font-weight: 600 !important;
    border-radius: 8px !important; transition: all var(--transition) !important;
    letter-spacing: 0.02em !important; min-height: 44px !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    border: none !important; color: #fff !important;
    box-shadow: 0 4px 14px rgba(29,78,216,0.35) !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(29,78,216,0.45) !important;
}}
.stButton > button[kind="secondary"] {{
    border: 2px solid #1d4ed8 !important; color: #1d4ed8 !important;
    background: transparent !important;
}}
.stButton > button[kind="secondary"]:hover {{ background: #eff6ff !important; }}

/* ═══════════ TABS ═══════════ */
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px; background: var(--border-light);
    border-radius: 10px; padding: 3px; border: none !important; flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: var(--font-ui) !important; font-size: 0.79rem !important;
    font-weight: 600 !important; padding: 9px 15px !important;
    border-radius: 7px !important; background: transparent !important;
    color: var(--fg-mute) !important; border: none !important;
    transition: all var(--transition) !important; min-height: 38px !important;
}}
.stTabs [aria-selected="true"] {{
    background: var(--bg-card) !important; color: #1d4ed8 !important;
    box-shadow: var(--shadow-xs) !important;
}}

/* ═══════════ RESULTS ═══════════ */
.results-hero {{
    background: linear-gradient(135deg, #0a1628 0%, #1e3a5f 50%, #0d3b60 100%);
    border-radius: var(--r-xl); padding: 44px; text-align: center;
    margin-bottom: 22px; position: relative; overflow: hidden;
    box-shadow: var(--shadow-lg);
}}
.results-hero::before {{
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at center, rgba(59,130,246,0.12) 0%, transparent 70%);
}}
.upg-display {{
    font-family: var(--font-display); font-size: clamp(3rem, 7vw, 5.5rem);
    font-weight: 900; color: #fff; line-height: 1; position: relative; z-index: 1;
}}
.upg-label {{
    font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: rgba(255,255,255,0.5);
    margin-bottom: 10px; position: relative; z-index: 1;
}}
.upg-verdict {{ font-family: var(--font-ui); font-size: 1.05rem; color: #93c5fd; margin-top: 10px; position: relative; z-index: 1; }}

.metrics-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 18px; }}
.metric-tile {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 18px 14px; text-align: center;
    box-shadow: var(--shadow-xs); transition: transform var(--transition), box-shadow var(--transition);
}}
.metric-tile:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-sm); }}
.metric-val {{ font-family: var(--font-display); font-size: 1.75rem; font-weight: 900; color: #1d4ed8; line-height: 1; margin-bottom: 4px; }}
.metric-val.green {{ color: var(--green-mid); }}
.metric-val.teal {{ color: var(--teal); }}
.metric-val.amber {{ color: var(--gold); }}
.metric-val.red {{ color: var(--red); }}
.metric-label {{ font-family: var(--font-mono); font-size: 0.56rem; letter-spacing: 0.11em; text-transform: uppercase; color: var(--fg-mute); }}
.metric-sub {{ font-family: var(--font-ui); font-size: 0.71rem; color: var(--fg-mute); margin-top: 3px; }}

.score-panel {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 20px 24px; box-shadow: var(--shadow-xs);
}}
.score-panel h4 {{ font-family: var(--font-display) !important; font-size: 1.05rem !important; margin-bottom: 12px !important; padding-bottom: 10px !important; border-bottom: 1px solid var(--border-light) !important; }}
.score-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-light); font-family: var(--font-ui); font-size: 0.85rem; }}
.score-row:last-child {{ border-bottom: none; }}
.score-lbl {{ color: var(--fg-mid); }}
.score-val {{ font-family: var(--font-mono); font-weight: 700; font-size: 0.85rem; }}
.score-val.c {{ color: var(--green-mid); }}
.score-val.w {{ color: var(--red); }}
.score-val.g {{ color: var(--gold); }}

/* ═══════════ SKILL HEATMAP ═══════════ */
.skill-heatmap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-top: 10px; }}
.skill-row {{
    display: flex; align-items: center; gap: 8px;
    font-family: var(--font-ui); font-size: 0.78rem; padding: 7px 11px;
    border-radius: 7px; border: 1px solid var(--border-light);
    background: var(--bg-card2);
}}
.skill-bar-outer {{ flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }}
.skill-bar-inner {{ height: 100%; border-radius: 3px; transition: width 0.7s ease; }}
.skill-bar-inner.strong {{ background: var(--green-mid); }}
.skill-bar-inner.mid {{ background: #d97706; }}
.skill-bar-inner.weak {{ background: #dc2626; }}
.skill-pct {{ font-family: var(--font-mono); font-size: 0.60rem; font-weight: 700; min-width: 30px; text-align: right; }}

/* ═══════════ ADMISSION CARDS ═══════════ */
.campus-shell {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-lg); overflow: hidden;
    box-shadow: var(--shadow-sm); margin-bottom: 16px;
}}
.campus-header {{ padding: 16px 22px; background: linear-gradient(135deg, #065f46, #047857); }}
.campus-header.rejected {{ background: linear-gradient(135deg, #7f1d1d, #991b1b); }}
.campus-header h4 {{ color: #fff !important; font-size: 1.0rem !important; margin-bottom: 3px !important; }}
.campus-header p {{ color: rgba(255,255,255,0.65); font-family: var(--font-mono); font-size: 0.68rem; }}
.campus-body {{ padding: 14px 22px; }}
.prog-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border-light); font-family: var(--font-ui); font-size: 0.85rem; }}
.prog-row:last-child {{ border-bottom: none; }}
.prog-name {{ font-weight: 600; color: var(--fg); }}
.prog-meta-txt {{ font-family: var(--font-mono); font-size: 0.61rem; color: var(--fg-mute); margin-top: 2px; }}
.badge-pass {{ color: var(--green-mid); font-weight: 700; background: var(--green-pale); padding: 2px 10px; border-radius: 5px; border: 1px solid #bbf7d0; font-family: var(--font-mono); font-size: 0.68rem; }}
.badge-wait {{ color: #92400e; font-weight: 700; background: var(--amber-pale); padding: 2px 10px; border-radius: 5px; border: 1px solid #fde68a; font-family: var(--font-mono); font-size: 0.68rem; }}
.badge-fail {{ color: var(--red); font-weight: 700; background: var(--red-pale); padding: 2px 10px; border-radius: 5px; border: 1px solid #fecaca; font-family: var(--font-mono); font-size: 0.68rem; }}

/* ═══════════ SECTION DIVIDER ═══════════ */
.sec-div {{ display: flex; align-items: center; gap: 12px; margin: 28px 0 16px; }}
.sec-div h3 {{ font-family: var(--font-display) !important; font-size: 1.35rem !important; white-space: nowrap; margin: 0 !important; color: var(--fg) !important; }}
.sec-line {{ flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }}

/* ═══════════ FEEDBACK BOX ═══════════ */
.feedback-box {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 20px 24px; margin-bottom: 14px;
    line-height: 1.85; font-family: var(--font-body); font-size: var(--base-font-size);
}}
.feedback-box.blue-accent {{ border-left: 4px solid #1d4ed8; }}
.feedback-box.teal-accent {{ border-left: 4px solid #0e7490; }}
.feedback-box.green-accent {{ border-left: 4px solid var(--green-mid); }}
.feedback-box.amber-accent {{ border-left: 4px solid #d97706; }}

/* ═══════════ DEEP FEEDBACK ═══════════ */
.deep-box {{
    background: linear-gradient(135deg, var(--bg-card), var(--bg-card2));
    border: 1px solid var(--border); border-radius: var(--r-lg);
    padding: 24px 28px; margin-top: 12px;
}}
.deep-box h5 {{ font-family: var(--font-display) !important; font-size: 1.0rem !important; color: #1d4ed8 !important; margin-bottom: 10px !important; }}
.feedback-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }}
.feedback-card {{ background: var(--bg); border: 1px solid var(--border); border-radius: var(--r); padding: 13px 16px; }}
.feedback-card-title {{ font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-mute); margin-bottom: 6px; }}
.feedback-card-body {{ font-family: var(--font-ui); font-size: 0.82rem; line-height: 1.62; color: var(--fg-mid); }}

/* ═══════════ COMPETENCY INPUT ═══════════ */
.competency-box {{
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 1.5px solid #7dd3fc; border-radius: var(--r);
    padding: 14px 18px; margin: 10px 0;
}}
.competency-box-title {{
    font-family: var(--font-mono); font-size: 0.62rem;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: #0369a1; margin-bottom: 8px; font-weight: 700;
}}

/* ═══════════ EXPANDER ═══════════ */
.streamlit-expanderHeader {{
    font-family: var(--font-ui) !important; font-size: 0.85rem !important;
    font-weight: 600 !important; background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    color: var(--fg) !important; min-height: 44px !important;
}}

/* ═══════════ RESPONSIVE ═══════════ */
@media (max-width: 768px) {{
    .hero-inner {{ padding: 24px 20px; }}
    .metrics-row {{ grid-template-columns: repeat(2,1fr); }}
    .feedback-grid {{ grid-template-columns: 1fr; }}
    .skill-heatmap {{ grid-template-columns: 1fr; }}
    .subtest-cards {{ grid-template-columns: 1fr; }}
}}

@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }}
}}

@media print {{
    section[data-testid="stSidebar"], #upcat-timer, .stButton {{ display: none !important; }}
}}

.stSelectbox > div > div, .stNumberInput > div > div > input,
.stTextInput > div > div > input {{ border-radius: 8px !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<a href="#main-content" class="skip-link">Skip to main content</a>', unsafe_allow_html=True)

# ==========================================
# 🏫 DATA
# ==========================================
SCHOOL_TIERS = {
    "PSHS (Philippine Science High School)": {"modifier": 0.30, "label": "Elite National Science School", "palugit": True},
    "DepEd Specialized Science & Math (PSHS-Affiliate)": {"modifier": 0.22, "label": "Regional Specialized", "palugit": True},
    "DepEd Laboratory School (UP, PNU, etc.)": {"modifier": 0.18, "label": "University Laboratory", "palugit": True},
    "DepEd Legislated Special School (CLSU, MSU, etc.)": {"modifier": 0.14, "label": "Legislated Special", "palugit": True},
    "Public — Special Program (STEM, TVL, ABM)": {"modifier": 0.07, "label": "Public SHS Special Track", "palugit": True},
    "Public — Regular National High School": {"modifier": 0.04, "label": "Public Regular", "palugit": True},
    "Public — Barangay / Community High School": {"modifier": 0.08, "label": "Barangay NHS (+bonus)", "palugit": True},
    "Public — Vocational / Technical": {"modifier": 0.06, "label": "Vocational Tech", "palugit": True},
    "Private — International School (IB, AP, Cambridge)": {"modifier": 0.08, "label": "International Private", "palugit": False},
    "Private — University Affiliated / Sectarian Elite": {"modifier": -0.04, "label": "Sectarian Elite", "palugit": False},
    "Private — Regular Sectarian": {"modifier": -0.08, "label": "Private Sectarian", "palugit": False},
    "Private — Non-Sectarian": {"modifier": -0.12, "label": "Private Non-Sectarian", "palugit": False},
}

CAMPUS_DATA = {
    "UP Diliman":           {"cutoff": 2.20, "recon": 0.0,   "note": "Strictest. No appeals."},
    "UP Manila":            {"cutoff": 2.10, "recon": 2.580, "note": "Health sciences hub."},
    "UP Los Baños":         {"cutoff": 2.30, "recon": 2.800, "note": "Recon possible for 1st choice."},
    "UP Baguio":            {"cutoff": 2.50, "recon": 2.700, "note": "Strong arts & sciences."},
    "UP Cebu":              {"cutoff": 2.60, "recon": 2.800, "note": "Growing campus."},
    "UP Mindanao":          {"cutoff": 2.60, "recon": 2.800, "note": "Priority for Mindanaoan applicants."},
    "UP Visayas (Iloilo)":  {"cutoff": 2.70, "recon": 2.700, "note": "Marine & fisheries focus."},
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
        "Double Quota": ["BS Computer Science","D Dental Medicine","BS Occupational Therapy","BS Physical Therapy","BS Speech Pathology","BS Pharmaceutical Sciences"],
        "Single Quota": ["BS Applied Physics","BA Behavioral Sciences","BA Political Science","BA Social Sciences"],
        "Less Popular": ["BA Development Studies","BA Philippine Arts","BA Social Work"]
    },
    "UP Los Baños": {
        "Triple Quota": ["BS Biology","BS Chemical Engineering","BS Civil Engineering","BS Computer Science","D Veterinary Medicine"],
        "Double Quota": ["BS Accountancy","BS Economics","BS Electrical Engineering","BS Industrial Engineering","BS Mechanical Engineering","BS Applied Mathematics"],
        "Single Quota": ["BS Agribusiness Management","BS Agricultural Chemistry","BS Food Technology","BS Mathematics","BS Statistics","BS Applied Physics"],
        "Less Popular": ["BS Agriculture","BS Forestry","BS Human Ecology","BS Nutrition","BS Environmental Science"]
    },
    "UP Baguio": {
        "Triple Quota": ["BS Computer Science","BS Biology","BS Mathematics"],
        "Double Quota": ["BA Communication","BS Physics","BS Management Economics","B Fine Arts"],
        "Single Quota": ["BA Languages & Literature","BS Statistics"],
        "Less Popular": ["BA Social Sciences (Economics)","BA Social Sciences (History)"]
    },
    "UP Cebu": {
        "Triple Quota": ["BS Accountancy","BS Biology","BS Computer Science","BS Management","BA Psychology"],
        "Double Quota": ["BA Political Science","BS Mathematics","B Fine Arts","BS Statistics"],
        "Single Quota": ["BA Communication"],
        "Less Popular": ["B Physical Education","BA Arts & Humanities"]
    },
    "UP Mindanao": {
        "Triple Quota": ["BS Architecture","BS Biology","BS Computer Science","BS Data Science"],
        "Double Quota": ["BS Agribusiness Economics","BS Applied Mathematics","BA Communication and Media Arts","BS Food Technology"],
        "Single Quota": ["BA English (Creative Writing)","BS Environmental Science"],
        "Less Popular": ["BA Anthropology","BA Mindanao Studies"]
    },
    "UP Visayas (Iloilo)": {
        "Triple Quota": ["BS Accountancy","BS Biology","BS Business Administration","BS Chemical Engineering","BS Computer Science","BS Economics","BS Fisheries","BS Management","BA Political Science","BA Psychology","BS Public Health"],
        "Double Quota": ["BS Chemistry","BS Food Technology","BS Statistics","BS Marine Biology"],
        "Single Quota": ["BS Applied Mathematics","BS Fisheries Engineering"],
        "Less Popular": ["BS Community Development","BA History","BA Literature","BA Sociology"]
    },
    "UP Open University": {
        "Triple Quota": [],
        "Double Quota": [],
        "Single Quota": ["BA Multi Media Studies","B Education Studies"],
        "Less Popular": ["BA Social Sciences","BA Journalism","B Public Management"]
    }
}

def get_all_programs(campus):
    progs = []
    for tier, plist in PROGRAM_TIERS.get(campus, {}).items():
        progs.extend(plist)
    return sorted(progs)

def get_program_tier(campus, program):
    for tier, plist in PROGRAM_TIERS.get(campus, {}).items():
        if program in plist: return tier
    return "Less Popular"

# ==========================================
# ⚙️ SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class='sb-logo'>
        <img src='https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/University_of_the_Philippines_seal.svg/1200px-University_of_the_Philippines_seal.svg.png'
             width='60' style='filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5));'
             alt='UP seal'/>
        <div style='color:rgba(255,255,255,0.3); font-family: var(--font-mono); font-size:0.56rem; letter-spacing:0.18em; margin-top:9px; text-transform:uppercase;'>
            Padayon! Agham at Math · v1.0
        </div>
        <div style='color:rgba(255,255,255,0.6); font-family: var(--font-display); font-size:0.82rem; font-style:italic; margin-top:5px;'>
            UPCAT Science & Math Simulator
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sb-heading">♿ Accessibility</span>', unsafe_allow_html=True)
    font_size = st.select_slider("Text Size", options=["small","medium","large","x-large"],
        value=st.session_state.get('font_size','medium'), help="Adjust all text size")
    if font_size != st.session_state.get('font_size'):
        st.session_state['font_size'] = font_size; st.rerun()
    high_contrast = st.checkbox("High Contrast Mode", value=st.session_state.get('high_contrast', False))
    if high_contrast != st.session_state.get('high_contrast'):
        st.session_state['high_contrast'] = high_contrast; st.rerun()
    show_timer = st.checkbox("Show Countdown Timer", value=True)
    show_nav = st.checkbox("Show Item Navigator", value=True)
    enable_flag = st.checkbox("Enable Item Flagging 🚩", value=True)

    st.divider()
    st.markdown('<span class="sb-heading">🔑 API Configuration</span>', unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...",
        help="aistudio.google.com — free API key")
    gemini_model = st.selectbox("Gemini Model", [
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-pro-latest",
    ], index=0, help="2.5 Pro produces deepest, most accurate items")

    st.divider()
    st.markdown('<span class="sb-heading">🏫 School Type</span>', unsafe_allow_html=True)
    jhs_type = st.selectbox("JHS School Type", list(SCHOOL_TIERS.keys()), index=5)
    shs_type = st.selectbox("SHS School Type", list(SCHOOL_TIERS.keys()), index=5)
    jhs_mod = SCHOOL_TIERS[jhs_type]["modifier"]
    shs_mod = SCHOOL_TIERS[shs_type]["modifier"]
    if SCHOOL_TIERS[jhs_type]["palugit"] or SCHOOL_TIERS[shs_type]["palugit"]:
        st.caption(f"✅ Palugit: JHS +{jhs_mod:.2f} / SHS +{shs_mod:.2f}")

    st.divider()
    st.markdown('<span class="sb-heading">📐 Science & Math Grades (G8–G11)</span>', unsafe_allow_html=True)
    st.caption("DepEd Final Grade scale (60–100). UPCAT uses G8–G11 only.")
    
    st.markdown("**Mathematics**")
    c1, c2 = st.columns(2)
    with c1:
        g8_math  = st.number_input("G8 Math",      60.0, 100.0, 87.0, 0.5)
        g9_math  = st.number_input("G9 Math",      60.0, 100.0, 87.0, 0.5)
        g10_math = st.number_input("G10 Math",     60.0, 100.0, 88.0, 0.5)
        g11_precalc = st.number_input("Pre-Calculus", 60.0, 100.0, 88.0, 0.5)
    with c2:
        g11_calc  = st.number_input("Basic Calculus", 60.0, 100.0, 87.0, 0.5)
        g11_stats = st.number_input("Stats & Prob",  60.0, 100.0, 88.0, 0.5)
        g11_genmath = st.number_input("Gen. Math",   60.0, 100.0, 88.0, 0.5)

    st.markdown("**Science**")
    c3, c4 = st.columns(2)
    with c3:
        g8_sci  = st.number_input("G8 Science",   60.0, 100.0, 87.0, 0.5)
        g9_sci  = st.number_input("G9 Science",   60.0, 100.0, 87.0, 0.5)
        g10_sci = st.number_input("G10 Science",  60.0, 100.0, 88.0, 0.5)
        g11_bio1 = st.number_input("Gen Bio 1",   60.0, 100.0, 88.0, 0.5)
    with c4:
        g11_bio2 = st.number_input("Gen Bio 2",   60.0, 100.0, 88.0, 0.5)
        g11_earth = st.number_input("Earth Sci",  60.0, 100.0, 87.0, 0.5)

    st.divider()
    st.markdown('<span class="sb-heading">🎯 Campus & Program</span>', unsafe_allow_html=True)
    campus_1 = st.selectbox("1st Campus", list(CAMPUS_DATA.keys()), index=0)
    c1_p1 = st.selectbox("Priority 1", get_all_programs(campus_1), key="c1p1")
    c1_p2 = st.selectbox("Priority 2", get_all_programs(campus_1), key="c1p2")
    c1_p3 = st.selectbox("Priority 3", get_all_programs(campus_1), key="c1p3")
    campus_2 = st.selectbox("2nd Campus", list(CAMPUS_DATA.keys()), index=2)
    c2_p1 = st.selectbox("Priority 1", get_all_programs(campus_2), key="c2p1")
    c2_p2 = st.selectbox("Priority 2", get_all_programs(campus_2), key="c2p2")
    c2_p3 = st.selectbox("Priority 3", get_all_programs(campus_2), key="c2p3")

    st.divider()
    st.markdown('<span class="sb-heading">⚙️ Simulation Parameters</span>', unsafe_allow_html=True)
    math_items = st.slider("Math Items", 10, 50, 25, 5,
        help="Actual UPCAT Math = 50 items / 60 minutes. No calculator.")
    sci_items = st.slider("Science Items", 10, 45, 20, 5,
        help="Actual UPCAT Science = 45 items / 45 minutes.")
    difficulty = st.select_slider("Difficulty",
        options=["Standard", "Competitive", "Brutal", "Massacre"],
        value="Competitive",
        help="Massacre = top ~3% ceiling, reflecting the true competition among 140,000 applicants.")

# ==========================================
# 🧠 PROMPT CONFIGURATION
# ==========================================
DIFF_MAP = {
    "Standard":    ("Standard: JHS-level items dominate. Problems solvable in under 60 seconds each by an average reviewer. Distractors are common errors. Science items: stock knowledge with clear factual basis.", 0.50, 0.16),
    "Competitive": ("Competitive: ~top 20% ceiling. Algebra/geometry/statistics items require 2-3 step solutions. Science items mix recall with data analysis from brief tables or diagrams. Average solver takes 60-90 seconds per item.", 0.44, 0.15),
    "Brutal":      ("Brutal: ~top 8% ceiling. Items test conceptual depth — not solvable by formula memorization alone. Science items include passage-based data analysis. Math involves multi-step problem solving without calculator.", 0.38, 0.14),
    "Massacre":    ("Massacre: ~top 2-3% ceiling (UP Diliman Engineering/MBB/CS tier). Math items are elegant traps that look simple but require precise conceptual reasoning. Distractors are the results of common procedural errors. Science items have dense experimental data or multi-variable scenarios. No item is solvable by rote recall alone.", 0.33, 0.13),
}
diff_instruction, MEAN_BASELINE, SIGMA = DIFF_MAP[difficulty]

# UPCAT Math topic distribution (research-based)
MATH_TOPIC_WEIGHTS = {
    "Algebra — JHS Core (Linear equations, inequalities, systems, factoring, polynomials, rational expressions, word problems)": 28,
    "Algebra — Functions and Graphs (Domain/range, evaluating functions, linear/quadratic graphs, transformations)": 10,
    "Number Sense and Arithmetic (Fractions, decimals, ratios, percentages, number theory, LCM/GCF, PEMDAS)": 12,
    "Quadratic Equations and Formula (Discriminant, nature of roots, sum/product of roots, applications)": 8,
    "Geometry — Plane (Angles, triangles, congruence, similarity, quadrilaterals, polygons, circles, area, perimeter)": 10,
    "Geometry — Solid (Surface area, volume of prisms, cylinders, cones, spheres, pyramids)": 5,
    "Statistics and Probability (Mean, median, mode, range, basic probability, counting, permutations, combinations)": 8,
    "Sequences and Series (Arithmetic, geometric sequences; nth term; sum of finite series)": 5,
    "Exponents and Logarithms (Laws, simplification, basic equations with logs and exponents)": 6,
    "Trigonometry (SOH-CAH-TOA, special angles, basic identities — RARE in UPCAT, max 1-2 items)": 3,
    "Pre-Calculus/SHS (Conic sections, polynomial functions, logarithmic models — RARE, max 1-2 items)": 3,
    "Radicals and Complex Numbers (Simplification, rationalizing, operations)": 2,
}

MATH_CRITICAL_RULES = """
UPCAT MATH PSYCHOMETRIC RULES (NON-NEGOTIABLE):
1. NO CALCULATOR — all numerical answers must be obtainable by mental math or hand calculation in under 90 seconds by a prepared student. No item should require a calculator.
2. NO HINT ABOUT DIFFICULTY — do not label any item as easy, medium, or hard in the question or options. The distribution should be roughly: 40% easy (p>0.55), 40% medium (p=0.35-0.55), 20% hard (p<0.35).
3. DISTRIBUTION: ~60-65% JHS algebra/geometry/number sense; ~20-25% statistics/sequences/exponents; ~10-15% trigonometry/SHS topics combined.
4. WORD PROBLEMS must use realistic Filipino contexts (jeepney fares, rice prices, geometry of bahay kubo, etc.) where appropriate.
5. NO OVERLY LONG PROBLEMS — the maximum mathematical complexity per item is 3-4 computational steps. UPCAT Math tests quick conceptual reasoning, NOT marathon computation.
6. DISTRACTORS: Each wrong option must be the result of a specific, common student error (e.g., sign error, wrong formula, forgetting to square root, dividing instead of multiplying).
7. LaTeX FORMAT: Express all mathematical expressions using proper LaTeX between $ signs for inline math or $$ for display math. Example: $x^2 + 3x - 4 = 0$. Every fraction, exponent, radical, inequality must be LaTeX.
8. ZERO AMBIGUITY: Every item must have exactly ONE defensible correct answer.
9. NO TRICKS: No items that are only 'hard' because of ambiguous wording or unconventional notation.
10. NO CALCULUS-HEAVY ITEMS — if a Pre-Calc/Calculus topic appears, it must be accessible to a student who only took the basic version of the subject.
"""

SCI_TOPIC_WEIGHTS = {
    "Biology — Cell Biology (Cell structure/organelles, cell division mitosis/meiosis, cell processes, membrane transport)": 10,
    "Biology — Genetics and Heredity (Mendelian genetics, Punnett squares, inheritance patterns, DNA structure, protein synthesis basics)": 8,
    "Biology — Ecosystems and Environment (Food chains/webs, biogeochemical cycles, ecological relationships, biodiversity, conservation)": 8,
    "Biology — Classification and Evolution (Taxonomy, kingdoms, natural selection, evidence of evolution, comparative anatomy)": 6,
    "Biology — Human Anatomy and Physiology (Organ systems, circulation, respiration, digestion, nervous system basics)": 7,
    "Biology — Plants (Photosynthesis, transpiration, plant tissues, reproductive structures)": 5,
    "Earth Science — Geology (Rock types and rock cycle, soil, layers of earth, plate tectonics, mountain formation)": 8,
    "Earth Science — Atmosphere and Climate (Weather vs climate, atmospheric layers, pressure systems, fronts, climate change)": 6,
    "Earth Science — Astronomy (Solar system, celestial bodies, tides, seasons, galaxies, life cycle of stars)": 5,
    "Earth Science — Hydrosphere (Water cycle, ocean currents, watersheds, groundwater)": 4,
    "Chemistry — Matter and Measurement (States of matter, properties, physical vs chemical changes, measurement, sig figs)": 6,
    "Chemistry — Atomic Structure and Periodic Table (Atomic models, subatomic particles, periodic trends, electron configuration)": 7,
    "Chemistry — Chemical Bonding and Reactions (Types of bonding, balancing equations, reaction types, acid-base, pH basics)": 7,
    "Physics — Mechanics (Force, Newton's laws, motion, speed/velocity/acceleration, momentum, work/energy/power)": 6,
    "Physics — Waves and Sound/Light (Wave properties, reflection, refraction, electromagnetic spectrum, sound)": 4,
    "Physics — Electricity (Basic circuits, voltage/current/resistance, Ohm's law)": 3,
}

SCI_CRITICAL_RULES = """
UPCAT SCIENCE PSYCHOMETRIC RULES (NON-NEGOTIABLE):
1. SCIENCE IS HYBRID — approximately 60% of items are PASSAGE-BASED or DATA-BASED (brief experimental scenarios, tables, graphs described in text, diagrams described in words). The other 40% are direct knowledge/application questions.
2. PASSAGE/DATA FORMAT: When using a passage or data table, present it as a structured text block in the "stimulus" field. Items that reference it must cite which part of the data they use.
3. NO PURELY MEMORIZATION QUESTIONS — even factual items should require understanding, not just recall. E.g., not "What is the powerhouse of the cell?" but "A cell deprived of its mitochondria would most directly lose its ability to..."
4. DISTRIBUTION BY SUBJECT (approximate): Biology ~35-38%, Earth Science ~25-28%, Chemistry ~20-22%, Physics ~15-18%.
5. JHS TOPICS DOMINATE — approximately 70% of items test G8-G10 science concepts. SHS (Gen Bio, Earth Sci) topics comprise ~30% but often appear in the passage-based items.
6. DIFFICULTY: Mix of 40% recall+application, 35% analysis, 25% evaluation/synthesis.
7. NO CHEMISTRY CALCULATION-HEAVY ITEMS — Science is not a math test. Avoid items requiring stoichiometric calculations, molarity formulas, or significant figure arithmetic. The UPCAT Science tests conceptual chemistry.
8. DIAGRAMS AND TABLES: Since we cannot render actual images, describe them PRECISELY in text using ASCII or structured HTML table format within the stimulus field. Label all data columns clearly.
9. DISTRACTORS: Each wrong option must represent a specific scientific misconception, not just a made-up wrong answer.
10. LaTeX for science: Use LaTeX for any chemical formulas (e.g., $H_2O$, $CO_2$) and equations.
"""

MATH_PROMPT_TEMPLATE = """
You are the chief item writer for the UPCAT Mathematics subtest at the University of the Philippines Office of Admissions. You are constructing a psychometrically valid practice test for {num_items} items under 60 minutes (no calculator).

{diff_instruction}

{custom_section}

TOPIC DISTRIBUTION GUIDANCE:
{topic_weights}

{critical_rules}

DISTRACTOR FRAMEWORK — every wrong option must be labeled:
- "SIGN_ERROR": Student made a sign error (most common in algebra)
- "FORMULA_CONFUSION": Used wrong formula or wrong variable
- "ARITHMETIC_ERROR": Correct approach, made computational mistake
- "CONCEPTUAL_ERROR": Fundamentally misunderstood the concept
- "INCOMPLETE_SOLUTION": Stopped one step short (forgot final operation)
- "WRONG_OPERATION": Used the inverse or incorrect operation

OUTPUT — STRICT JSON ONLY, no fences, no commentary:
{{
  "exam_metadata": {{
    "subtest": "Mathematics",
    "total_items": {num_items},
    "time_minutes": 60,
    "calculator_allowed": false,
    "difficulty": "{difficulty}",
    "distribution_note": "~60% JHS topics, ~20-25% statistics/sequences/exponents, ~10-15% SHS+trig combined"
  }},
  "items": [
    {{
      "item_number": 1,
      "topic": "Algebra — JHS Core",
      "subtopic": "Linear equations with fractions",
      "grade_level_origin": "Grade 8",
      "question_text": "Full question text. ALL MATH must use LaTeX: inline as $...$ and display as $$...$$. Word problems use Filipino context where natural.",
      "stimulus": null,
      "options": {{
        "A": "Option A with LaTeX where needed",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "B",
      "distractor_analysis": {{
        "A": {{"type": "SIGN_ERROR", "error": "Student forgot to change sign when moving term to other side"}},
        "C": {{"type": "ARITHMETIC_ERROR", "error": "Computed 3 × 4 = 16 instead of 12"}},
        "D": {{"type": "INCOMPLETE_SOLUTION", "error": "Solved for 2x instead of x, forgot to divide by 2"}}
      }},
      "solution": "FULL STEP-BY-STEP SOLUTION minimum 4 steps. Use LaTeX for all math expressions. Label each step clearly: Step 1: [action], Step 2: [action], etc. Show the exact reasoning. Final answer must match correct_answer.",
      "key_concept": "One sentence: the core mathematical concept being tested.",
      "common_mistake_warning": "One sentence: the single most common error students make on this type of item."
    }}
  ]
}}

ABSOLUTE RULES: Valid JSON only. No markdown. No truncation. Every item must have a complete solution. All math in LaTeX. Exactly {num_items} items.
"""

SCI_PROMPT_TEMPLATE = """
You are the chief item writer for the UPCAT Science subtest at the University of the Philippines Office of Admissions. You are constructing a psychometrically valid practice test for {num_items} items under 45 minutes.

{diff_instruction}

{custom_section}

TOPIC DISTRIBUTION GUIDANCE:
{topic_weights}

{critical_rules}

STIMULUS TYPES for passage/data items:
- "TEXT_PASSAGE": A 60-120 word scientific scenario or experimental description
- "DATA_TABLE": An HTML table with experimental data (use proper <table><tr><th><td> tags)
- "DIAGRAM_TEXT": A clearly labeled text-based description of a biological, geological, or physical diagram
- null: Direct knowledge question with no stimulus

OUTPUT — STRICT JSON ONLY, no fences, no commentary:
{{
  "exam_metadata": {{
    "subtest": "Science",
    "total_items": {num_items},
    "time_minutes": 45,
    "difficulty": "{difficulty}",
    "distribution_note": "Biology ~36%, Earth Science ~26%, Chemistry ~21%, Physics ~17%"
  }},
  "items": [
    {{
      "item_number": 1,
      "topic": "Biology — Cell Biology",
      "subtopic": "Mitochondria and cellular respiration",
      "grade_level_origin": "Grade 9",
      "stimulus_type": "TEXT_PASSAGE",
      "stimulus": "A researcher cultured two groups of liver cells. Group A received normal nutrients and oxygen. Group B was placed in a nitrogen-rich, oxygen-deprived environment for 24 hours. After the experiment, Group B cells showed significantly lower ATP concentrations and increased lactic acid production compared to Group A.",
      "question_text": "Based on the experimental data, which conclusion is most directly supported?",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "C",
      "distractor_analysis": {{
        "A": {{"type": "MAGNIFIED_DETAIL", "error": "Focuses on lactic acid but reverses the cause-effect relationship"}},
        "B": {{"type": "EXTERNAL_INTRUSION", "error": "Correct biology fact but not supported by this specific experiment"}},
        "D": {{"type": "PARTIAL_TRUTH", "error": "True statement about nitrogen but irrelevant to what was measured"}}
      }},
      "solution": "FULL EXPLANATION minimum 4 sentences: (1) Identify the key variable(s) in the stimulus. (2) Apply the relevant scientific principle. (3) Explain why the correct answer is correct. (4) Explain why each distractor fails. Reference stimulus data specifically.",
      "key_concept": "One sentence: the core scientific concept being tested.",
      "science_discipline": "Biology",
      "passage_reference": "Stimulus data: ATP levels and lactic acid production in Group B"
    }}
  ]
}}

ABSOLUTE RULES: Valid JSON only. No markdown. No truncation. Every item must have a complete solution. Chemical formulas use LaTeX ($H_2O$). Exactly {num_items} items.
"""

def build_custom_section(use_custom, custom_text, subtest):
    if use_custom and custom_text.strip():
        return f"""
CUSTOM COMPETENCIES PROVIDED BY USER — PRIORITIZE THESE:
The following are specific learning competencies the user wants tested. Generate items that closely align to these competencies. These competencies override the default topic distribution to the extent possible.

```
{custom_text.strip()}
```

Generate as many items as possible from these competencies, cycling through them. Any remaining items should follow standard UPCAT {subtest} coverage.
"""
    return ""

def build_topic_weights_str(weights):
    return "\n".join([f"  - {topic}: ~{w}% of items" for topic, w in weights.items()])

def clean_json(raw):
    s = raw.strip()
    for fence in ["```json", "```"]:
        if s.startswith(fence): s = s[len(fence):]
    if s.endswith("```"): s = s[:-3]
    last = s.rfind("}")
    if last != -1: s = s[:last+1]
    return s.strip()

# ==========================================
# 🚀 HERO
# ==========================================
st.markdown('<div id="main-content"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class='hero-wrap' role="banner">
    <div class='hero-bg'></div>
    <div class='hero-accent'></div>
    <div class='hero-grid' aria-hidden="true"></div>
    <div class='hero-inner'>
        <div class='hero-badge'>🧮 UPCAT SCIENCE & MATH ELITE SIMULATOR · v1.0</div>
        <h1 class='hero-title'><em>Padayon!</em> Agham at Matematika</h1>
        <p class='hero-sub'>
            Research-based psychometric simulation of the UPCAT Mathematics (50 items · 60 min · no calculator)
            and Science (45 items · 45 min · passage-based) subtests.
            Only ~10–13% of 140,000+ applicants pass their first-choice campus and degree.
            Train at the level that separates Iskos and Iskas from the rest.
        </p>
        <div class='hero-stats-row' role="list">
            <div class='hero-stat' role="listitem"><div class='hero-stat-num'>140k+</div><div class='hero-stat-label'>UPCAT Applicants / Year</div></div>
            <div class='hero-stat' role="listitem"><div class='hero-stat-num'>10–13%</div><div class='hero-stat-label'>Pass Rate (1st Choice)</div></div>
            <div class='hero-stat' role="listitem"><div class='hero-stat-num'>50+45</div><div class='hero-stat-label'>Math + Science Items</div></div>
            <div class='hero-stat' role="listitem"><div class='hero-stat-num'>−0.25</div><div class='hero-stat-label'>Wrong Answer Penalty</div></div>
            <div class='hero-stat' role="listitem"><div class='hero-stat-num'>0</div><div class='hero-stat-label'>Calculators Allowed</div></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='notice' role="note">
    ⚠️ <strong>Disclaimer:</strong> All items are AI-generated for practice only. UPG formulas use independent research modeling, not official UP methodology.
    This simulator focuses on <strong>Mathematics and Science</strong> exclusively.
    Item distribution reflects research into actual UPCAT coverage — JHS topics dominate Math; Science is heavily passage/data-based.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📋 CUSTOM COMPETENCY INPUT
# ==========================================
st.markdown("""
<div class='sec-div'><h3>📋 Custom Competency Input (Optional)</h3><div class='sec-line'></div></div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='notice'>
    💡 <strong>How to use:</strong> Find specific DepEd learning competencies (MELCs) you want to practice from 
    <em>curriculum.deped.gov.ph</em> or your textbook, paste them below, and the simulator will generate items targeting those exact competencies.
    Leave blank to use the default UPCAT coverage distribution.
</div>
""", unsafe_allow_html=True)

col_comp1, col_comp2 = st.columns(2)
with col_comp1:
    st.markdown("""
    <div class='competency-box'>
        <div class='competency-box-title'>🔢 Mathematics Custom Competencies</div>
    </div>
    """, unsafe_allow_html=True)
    use_custom_math = st.checkbox("Use custom Math competencies", key="use_custom_math_cb")
    custom_math = st.text_area(
        "Paste Math competencies here",
        height=150,
        placeholder="""Example (paste your own from DepEd MELCs):
• Factors completely different types of polynomials (M8AL-Ia-b-1)
• Solves problems involving factors of polynomials (M8AL-Ia-b-2)
• Illustrates rational algebraic expressions (M8AL-Ic-1)
• Simplifies rational algebraic expressions (M8AL-Ic-2)""",
        label_visibility="collapsed",
        key="custom_math_input"
    )
    st.session_state['use_custom_math'] = use_custom_math
    st.session_state['custom_competencies_math'] = custom_math

with col_comp2:
    st.markdown("""
    <div class='competency-box' style='background:linear-gradient(135deg,#ecfeff,#cffafe); border-color:#67e8f9;'>
        <div class='competency-box-title' style='color:#0369a1;'>🔬 Science Custom Competencies</div>
    </div>
    """, unsafe_allow_html=True)
    use_custom_sci = st.checkbox("Use custom Science competencies", key="use_custom_sci_cb")
    custom_sci = st.text_area(
        "Paste Science competencies here",
        height=150,
        placeholder="""Example (paste your own from DepEd MELCs):
• Describe the different levels of biological organization from cell to biosphere (S8LT-Ia-1)
• Identify the parts of the cell and their functions (S8LT-Ia-2)
• Explain how energy is transformed in photosynthesis and cellular respiration (S8LT-Ib-c-3)
• Describe the process of mitosis and its role in growth and repair (S8LT-Id-4)""",
        label_visibility="collapsed",
        key="custom_sci_input"
    )
    st.session_state['use_custom_sci'] = use_custom_sci
    st.session_state['custom_competencies_sci'] = custom_sci

# ==========================================
# ⚙️ GENERATE BUTTONS
# ==========================================
st.markdown("""
<div class='sec-div'><h3>🚀 Generate Simulation</h3><div class='sec-line'></div></div>
""", unsafe_allow_html=True)

# Subtest info cards
st.markdown(f"""
<div class='subtest-cards'>
    <div class='subtest-card math-card'>
        <div class='subtest-card-icon'>🔢</div>
        <div class='subtest-card-title'>Mathematics</div>
        <div class='subtest-card-meta'>{math_items} items · 60 minutes · No calculator</div>
        <div class='subtest-card-detail'>
            ~60% JHS Algebra & Geometry · ~20% Stats/Sequences/Exponents · ~15% Trig/SHS topics<br>
            <strong>No calculus-heavy items.</strong> All answers reachable by mental math or hand computation in under 90 seconds.
        </div>
    </div>
    <div class='subtest-card sci-card'>
        <div class='subtest-card-icon'>🔬</div>
        <div class='subtest-card-title'>Science</div>
        <div class='subtest-card-meta'>{sci_items} items · 45 minutes · Passage-based</div>
        <div class='subtest-card-detail'>
            Biology ~36% · Earth Sci ~26% · Chemistry ~21% · Physics ~17%<br>
            <strong>~60% passage/data-based.</strong> Tests conceptual understanding and data analysis, not just memorization.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_g1, col_g2, col_g3 = st.columns([1, 1, 1])
with col_g1:
    gen_both = st.button(f"🚀 Generate BOTH — {math_items + sci_items} Items Total",
        type="primary", use_container_width=True,
        help="Generates Math and Science simultaneously")
with col_g2:
    gen_math = st.button(f"🔢 Math Only — {math_items} Items",
        use_container_width=True)
with col_g3:
    gen_sci = st.button(f"🔬 Science Only — {sci_items} Items",
        use_container_width=True)

# ==========================================
# ⚙️ GENERATION ENGINE
# ==========================================
def generate_subtest(model, prompt, subtest_name):
    response = model.generate_content(prompt)
    raw = clean_json(response.text)
    data = json.loads(raw)
    if "items" not in data or len(data["items"]) == 0:
        raise ValueError(f"No items generated for {subtest_name}")
    return data

def run_generation(generate_math_flag, generate_sci_flag):
    if not api_key:
        st.error("❌ Enter your Gemini API Key in the sidebar (aistudio.google.com).")
        return

    prog = st.progress(0)
    status = st.empty()

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            gemini_model,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.85,
                "top_p": 0.95,
                "max_output_tokens": 32000,
            }
        )

        new_data = dict(st.session_state.get('test_data') or {})

        if generate_math_flag:
            steps_math = [
                "📐 Calibrating UPCAT Math difficulty ceiling and topic distribution...",
                "🔢 Constructing JHS algebra, geometry, and number sense items...",
                "📊 Adding statistics, sequences, and exponents items...",
                "⚡ Writing trigonometry and SHS-track items (rare, high-difficulty)...",
                "✅ Validating LaTeX, answer keys, and solution completeness..."
            ]
            for i, step in enumerate(steps_math):
                status.info(step); prog.progress(int((i+1)*8)); time.sleep(0.2)

            custom_section_math = build_custom_section(
                st.session_state.get('use_custom_math', False),
                st.session_state.get('custom_competencies_math', ''),
                "Mathematics"
            )
            math_prompt = MATH_PROMPT_TEMPLATE.format(
                num_items=math_items,
                diff_instruction=diff_instruction,
                custom_section=custom_section_math,
                topic_weights=build_topic_weights_str(MATH_TOPIC_WEIGHTS),
                critical_rules=MATH_CRITICAL_RULES,
                difficulty=difficulty,
            )
            status.info("🧠 Generating Math items — this may take 45-90 seconds...")
            math_data = generate_subtest(model, math_prompt, "Mathematics")
            prog.progress(50)
            new_data['math'] = math_data
            status.success(f"✅ Math: {len(math_data['items'])} items generated!")

        if generate_sci_flag:
            steps_sci = [
                "🔬 Calibrating UPCAT Science distribution (Biology/Earth Sci/Chem/Physics)...",
                "🌿 Writing Biology items — cell biology, genetics, ecology...",
                "🌍 Writing Earth Science items — geology, atmosphere, astronomy...",
                "⚗️ Writing Chemistry & Physics items — conceptual focus, no heavy calculation...",
                "📊 Constructing passage-based and data-table items (~60% of test)...",
                "✅ Validating stimuli, HTML tables, and solution completeness..."
            ]
            for i, step in enumerate(steps_sci):
                status.info(step); prog.progress(50 + int((i+1)*6)); time.sleep(0.2)

            custom_section_sci = build_custom_section(
                st.session_state.get('use_custom_sci', False),
                st.session_state.get('custom_competencies_sci', ''),
                "Science"
            )
            sci_prompt = SCI_PROMPT_TEMPLATE.format(
                num_items=sci_items,
                diff_instruction=diff_instruction,
                custom_section=custom_section_sci,
                topic_weights=build_topic_weights_str(SCI_TOPIC_WEIGHTS),
                critical_rules=SCI_CRITICAL_RULES,
                difficulty=difficulty,
            )
            status.info("🧠 Generating Science items with passages and data tables — 45-90 seconds...")
            sci_data = generate_subtest(model, sci_prompt, "Science")
            prog.progress(96)
            new_data['sci'] = sci_data
            status.success(f"✅ Science: {len(sci_data['items'])} items generated!")

        prog.progress(100)
        math_count = len(new_data.get('math', {}).get('items', []))
        sci_count = len(new_data.get('sci', {}).get('items', []))
        status.success(f"🎉 Ready! Math: {math_count} items · Science: {sci_count} items · Difficulty: {difficulty}")

        st.session_state.update({
            'test_data': new_data,
            'user_answers_math': {},
            'user_answers_sci': {},
            'flagged_items': set(),
            'submitted': False,
            'math_submitted': False,
            'sci_submitted': False,
            'math_started': False,
            'sci_started': False,
            'math_start_time': None,
            'sci_start_time': None,
            'elapsed_math': 0,
            'elapsed_sci': 0,
        })
        time.sleep(1.0)
        st.rerun()

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON Parse Error — try Gemini 2.5 Pro for better JSON compliance. Detail: {str(e)[:200]}")
        if 'response' in dir():
            with st.expander("🔍 Raw response (debug)"):
                st.code(response.text[:3000], language="text")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

if gen_both: run_generation(True, True)
elif gen_math: run_generation(True, False)
elif gen_sci: run_generation(False, True)

# ==========================================
# 📝 EXAM INTERFACE
# ==========================================
if st.session_state.get('test_data') and not st.session_state.get('submitted'):
    test_data = st.session_state['test_data']
    math_items_data = test_data.get('math', {}).get('items', [])
    sci_items_data = test_data.get('sci', {}).get('items', [])
    flagged = st.session_state.get('flagged_items', set())

    # Timer logic
    if show_timer:
        active = st.session_state.get('active_subtest', 'math')
        if active == 'math' and st.session_state.get('math_start_time'):
            elapsed_so_far = int(time.time() - st.session_state['math_start_time'])
            remaining = max(0, 3600 - elapsed_so_far)  # 60 min
        elif active == 'sci' and st.session_state.get('sci_start_time'):
            elapsed_so_far = int(time.time() - st.session_state['sci_start_time'])
            remaining = max(0, 2700 - elapsed_so_far)  # 45 min
        else:
            remaining = 3600 if active == 'math' else 2700
        timer_cls = "sci" if active == 'sci' else ""

        st.components.v1.html(f"""
        <div id="upcat-timer" class="{timer_cls}" role="timer" aria-live="polite" aria-atomic="true">
            {"🔬" if active == "sci" else "🔢"} <span id="t-val">--:--</span>
        </div>
        <script>
        (function() {{
            var tl = {remaining};
            function tick() {{
                if(tl < 0) tl = 0;
                var m = Math.floor(tl/60), s = tl%60;
                var el = document.getElementById('t-val');
                var box = document.getElementById('upcat-timer');
                if(el) {{
                    el.textContent = (m<10?'0':'')+m+':'+(s<10?'0':'')+s;
                    if(tl<=300 && tl>60) box.className='{timer_cls} warn';
                    if(tl<=60) {{ box.className='{timer_cls} danger'; }}
                    if(tl<=0) el.textContent='00:00 · TIME UP';
                }}
                if(tl>0) {{ tl--; setTimeout(tick,1000); }}
            }}
            setTimeout(tick,300);
        }})();
        </script>
        """, height=0)

    # Progress summary
    answered_math = len(st.session_state['user_answers_math'])
    answered_sci = len(st.session_state['user_answers_sci'])
    total_math = len(math_items_data)
    total_sci = len(sci_items_data)
    total_ans = answered_math + answered_sci
    total_items_all = total_math + total_sci

    pct_math = (answered_math / max(1, total_math)) * 100
    pct_sci = (answered_sci / max(1, total_sci)) * 100

    if total_math > 0 and total_sci > 0:
        col_pm, col_ps = st.columns(2)
        with col_pm:
            st.markdown(f"""
            <div class='prog-outer'>
                <div class='prog-meta'>
                    <span>🔢 MATH: {answered_math}/{total_math}</span>
                    <span>{pct_math:.0f}%</span>
                </div>
                <div class='prog-track' role="progressbar" aria-valuenow="{int(pct_math)}" aria-valuemin="0" aria-valuemax="100">
                    <div class='prog-math' style='width:{pct_math:.1f}%'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_ps:
            st.markdown(f"""
            <div class='prog-outer'>
                <div class='prog-meta'>
                    <span>🔬 SCIENCE: {answered_sci}/{total_sci}</span>
                    <span>{pct_sci:.0f}%</span>
                </div>
                <div class='prog-track' role="progressbar" aria-valuenow="{int(pct_sci)}" aria-valuemin="0" aria-valuemax="100">
                    <div class='prog-sci' style='width:{pct_sci:.1f}%'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='notice notice-rmw' role="alert">
        ⚠️ <strong>RMW ACTIVE:</strong> +1.0 correct · −0.25 wrong · 0 blank.
        <strong>Math:</strong> No calculator. All items solvable by hand/mental math.
        <strong>Science:</strong> Read the stimulus carefully before answering. The answer is often IN the data.
        Only guess if you can confidently eliminate 2+ options.
    </div>
    """, unsafe_allow_html=True)

    # Determine which tabs to show
    tabs_labels = []
    if math_items_data: tabs_labels.append(f"🔢 Mathematics ({total_math} items · {answered_math} answered)")
    if sci_items_data: tabs_labels.append(f"🔬 Science ({total_sci} items · {answered_sci} answered)")

    if len(tabs_labels) == 2:
        tab_math, tab_sci = st.tabs(tabs_labels)
        active_tabs = [(tab_math, 'math', math_items_data), (tab_sci, 'sci', sci_items_data)]
    elif len(tabs_labels) == 1:
        if math_items_data:
            tab_only = st.tabs(tabs_labels)[0]
            active_tabs = [(tab_only, 'math', math_items_data)]
        else:
            tab_only = st.tabs(tabs_labels)[0]
            active_tabs = [(tab_only, 'sci', sci_items_data)]
    else:
        active_tabs = []

    def render_items(tab, subtest_key, items_list):
        with tab:
            if not items_list: return

            is_math = subtest_key == 'math'
            answers_key = f'user_answers_{subtest_key}'
            color = "#1d4ed8" if is_math else "#0e7490"
            q_num_cls = "q-num" if is_math else "q-num sci"
            topic_tag_cls = "q-tag-topic" if is_math else "q-tag-topic-sci"
            dot_ans_cls = "answered" if is_math else "sci-answered"

            # Navigator
            if show_nav:
                nav_html = f"<div class='item-nav' aria-label='{('Math' if is_math else 'Science')} Item Navigator'>"
                nav_html += f"<div class='item-nav-title'>{'Math' if is_math else 'Science'} navigator — click to jump</div>"
                nav_html += "<div class='item-nav-grid'>"
                for q in items_list:
                    inum = q.get('item_number')
                    key = f"{subtest_key}_{inum}"
                    is_ans = inum in st.session_state[answers_key]
                    is_flg = key in flagged
                    dot_cls = "flagged" if is_flg else (dot_ans_cls if is_ans else "")
                    nav_html += f"<div class='nav-dot {dot_cls}' onclick=\"document.getElementById('{subtest_key}_{inum}').scrollIntoView({{behavior:'smooth'}})\" role='button' tabindex='0' aria-label='Go to item {inum}'>{inum}</div>"
                nav_html += "</div></div>"
                st.markdown(nav_html, unsafe_allow_html=True)

            # Start timer on first answer
            if not st.session_state.get(f'{subtest_key}_start_time'):
                st.session_state[f'{subtest_key}_start_time'] = time.time()
                st.session_state['active_subtest'] = subtest_key

            for q in items_list:
                inum = q.get('item_number')
                topic = q.get('topic', '')
                subtopic = q.get('subtopic', '')
                grade_orig = q.get('grade_level_origin', '')
                qtext = q.get('question_text', '')
                stimulus = q.get('stimulus', None)
                stimulus_type = q.get('stimulus_type', None)
                is_ans = inum in st.session_state[answers_key]
                is_flg = f"{subtest_key}_{inum}" in flagged

                card_cls = f"q-card {'answered' if is_ans else ''} {'flagged' if is_flg else ''} {'' if is_math else 'sci-card'}"

                # Topic tag (truncated)
                short_topic = topic.split(' — ')[0] if ' — ' in topic else topic
                short_topic = short_topic[:25] + ('...' if len(short_topic) > 25 else '')

                st.markdown(f"""
                <div class='{card_cls}' id='{subtest_key}_{inum}' role="article" aria-label="Item {inum}">
                    <div class='q-meta'>
                        <span class='{q_num_cls}'>{'MATH' if is_math else 'SCI'} {inum}</span>
                        <span class='q-tag {topic_tag_cls}' title='{topic}'>{short_topic}</span>
                        {f"<span class='q-tag q-tag-grade' title='{subtopic}'>{grade_orig}</span>" if grade_orig else ""}
                        {f"<span class='q-tag q-tag-type'>{'Data/Passage' if stimulus else 'Knowledge'}</span>" if not is_math else ""}
                        {"<span style='font-size:0.8rem; margin-left:auto;'>🚩</span>" if is_flg else ""}
                        {"<span style='font-size:0.8rem; margin-left:4px;'>✅</span>" if is_ans else ""}
                    </div>
                """, unsafe_allow_html=True)

                # Render stimulus
                if stimulus:
                    if stimulus_type == "DATA_TABLE":
                        st.markdown(f"""
                        <div style='margin-bottom:10px; overflow-x:auto;'>
                            <div style='font-family:var(--font-mono); font-size:0.60rem; letter-spacing:0.1em; text-transform:uppercase; color:#0369a1; margin-bottom:6px;'>📊 EXPERIMENTAL DATA</div>
                            {stimulus}
                        </div>
                        """, unsafe_allow_html=True)
                    elif stimulus_type == "DIAGRAM_TEXT":
                        st.markdown(f"""
                        <div class='sci-data-box'>
                            <div style='font-weight:700; margin-bottom:6px; color:#0369a1;'>🔎 DIAGRAM / FIGURE</div>
                            {stimulus}
                        </div>
                        """, unsafe_allow_html=True)
                    else:  # TEXT_PASSAGE
                        st.markdown(f"""
                        <div class='sci-passage'>
                            <div style='font-family:var(--font-mono); font-size:0.60rem; letter-spacing:0.1em; text-transform:uppercase; color:#0e7490; margin-bottom:8px; font-weight:700;'>📄 READ THE FOLLOWING BEFORE ANSWERING</div>
                            {stimulus}
                        </div>
                        """, unsafe_allow_html=True)

                # Question text (LaTeX rendering via st.markdown)
                st.markdown(f"<div class='q-stem'>{qtext}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                opts = q.get('options', {})
                choices = [f"A) {opts.get('A','')}", f"B) {opts.get('B','')}", f"C) {opts.get('C','')}", f"D) {opts.get('D','')}"]
                choice = st.radio(
                    f"Answer for {'Math' if is_math else 'Science'} Item {inum}",
                    choices, key=f"{subtest_key}_r_{inum}", index=None, label_visibility="collapsed"
                )
                if choice:
                    st.session_state[answers_key][inum] = choice[0]
                    if not st.session_state.get(f'{subtest_key}_start_time'):
                        st.session_state[f'{subtest_key}_start_time'] = time.time()

                # Flag button
                if enable_flag:
                    flag_key = f"{subtest_key}_{inum}"
                    flbl = "🚩 Unflag" if flag_key in flagged else "🚩 Flag"
                    if st.button(flbl, key=f"flag_{subtest_key}_{inum}", help="Mark for review"):
                        if flag_key in flagged: flagged.discard(flag_key)
                        else: flagged.add(flag_key)
                        st.session_state['flagged_items'] = flagged
                        st.rerun()

                st.markdown("<hr style='border:none; border-top:1px solid var(--border-light); margin:10px 0 14px;'>", unsafe_allow_html=True)

    for tab, key, items in active_tabs:
        render_items(tab, key, items)

    # SUBMIT
    st.markdown("<br>", unsafe_allow_html=True)
    total_flagged = len(flagged)
    total_blank = total_items_all - total_ans

    s_cols = st.columns(4)
    for idx, (lbl, val, clr) in enumerate([
        ("Answered", total_ans, "#065f46"),
        ("Flagged", total_flagged, "#d97706"),
        ("Blank (0 pts)", total_blank, "#64748b"),
        ("Total Items", total_items_all, "#1d4ed8"),
    ]):
        with s_cols[idx]:
            st.markdown(f"<div class='stat-pill'><div class='stat-pill-num' style='color:{clr};'>{val}</div><div class='stat-pill-label'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c_sub1, c_sub2, c_sub3 = st.columns([1,2,1])
    with c_sub2:
        if total_blank > 0:
            st.warning(f"⚠️ {total_blank} item(s) unanswered — scored 0 (no penalty). Only guess if you can eliminate 2+ options.")
        if total_flagged > 0:
            st.info(f"🚩 {total_flagged} item(s) flagged — review before submitting.")
        if st.button("📥 Submit & Generate Full UPG Report + Deep Feedback",
                     type="primary", use_container_width=True,
                     help="Computes your UPG, admission chances, topic heatmap, and step-by-step solutions"):
            st.session_state['submitted'] = True
            if st.session_state.get('math_start_time'):
                st.session_state['elapsed_math'] = time.time() - st.session_state['math_start_time']
            if st.session_state.get('sci_start_time'):
                st.session_state['elapsed_sci'] = time.time() - st.session_state['sci_start_time']
            st.rerun()

# ==========================================
# 📊 RESULTS ENGINE
# ==========================================
if st.session_state.get('submitted') and st.session_state.get('test_data'):
    st.balloons()
    test_data = st.session_state['test_data']
    u_math = st.session_state.get('user_answers_math', {})
    u_sci = st.session_state.get('user_answers_sci', {})
    elapsed_math = st.session_state.get('elapsed_math', 0)
    elapsed_sci = st.session_state.get('elapsed_sci', 0)

    math_items_data = test_data.get('math', {}).get('items', [])
    sci_items_data = test_data.get('sci', {}).get('items', [])

    # ── SCORING ──
    def score_subtest(items, user_ans):
        total = len(items)
        correct = sum(1 for q in items if user_ans.get(q.get('item_number')) == q.get('correct_answer'))
        answered = sum(1 for v in user_ans.values() if v)
        wrong = answered - correct
        blank = total - answered
        raw = max(0.0, correct - 0.25 * wrong)
        pct = raw / max(1, total)
        return total, correct, wrong, blank, raw, pct

    if math_items_data:
        m_total, m_correct, m_wrong, m_blank, m_raw, m_pct = score_subtest(math_items_data, u_math)
    else:
        m_total, m_correct, m_wrong, m_blank, m_raw, m_pct = 0, 0, 0, 0, 0.0, 0.0

    if sci_items_data:
        s_total, s_correct, s_wrong, s_blank, s_raw, s_pct = score_subtest(sci_items_data, u_sci)
    else:
        s_total, s_correct, s_wrong, s_blank, s_raw, s_pct = 0, 0, 0, 0, 0.0, 0.0

    # Combined (only what was tested)
    tested_subtests = sum([1 if math_items_data else 0, 1 if sci_items_data else 0])
    if tested_subtests == 2:
        combined_pct = (m_pct + s_pct) / 2
    elif math_items_data:
        combined_pct = m_pct
    else:
        combined_pct = s_pct

    # ── GRADE UPG (40%) — Science & Math grades ──
    math_grades = [g8_math, g9_math, g10_math, g11_precalc, g11_calc, g11_stats, g11_genmath]
    sci_grades = [g8_sci, g9_sci, g10_sci, g11_bio1, g11_bio2, g11_earth]
    all_grades = math_grades + sci_grades
    raw_avg = float(np.mean(all_grades))
    avg_mod = (jhs_mod + shs_mod) / 2
    grade_upg_raw = 5.0 - ((raw_avg - 75) / 25) * 4.0
    grade_upg_final = max(1.0, min(5.0, grade_upg_raw - avg_mod))

    # ── UPCAT UPG (60%) — calibrated to 140k applicant pool ──
    upcat_z = (combined_pct - MEAN_BASELINE) / SIGMA
    upcat_upg = max(1.0, min(5.0, 2.75 - (upcat_z * 0.55)))
    overall_pct = 0.5 * (1 + math.erf(upcat_z / math.sqrt(2)))
    overall_pct = max(0.001, min(0.9999, overall_pct))
    final_upg = (0.40 * grade_upg_final) + (0.60 * upcat_upg)
    sim_rank = int(140000 - (140000 * overall_pct))

    # Pass rate context: ~10-13% pass their 1st choice, ~18-22% pass any campus
    PASS_RATE_1ST = 0.115  # ~11.5% first-choice pass rate
    PASS_RATE_ANY = 0.20   # ~20% any campus pass rate

    if final_upg <= 1.5:
        verdict = "🏆 Elite — Top tier. Strong contender for any program at any campus."
    elif final_upg <= 2.0:
        verdict = "✅ Very Strong — Likely qualified for multiple programs."
    elif final_upg <= 2.3:
        verdict = "📘 Competitive — Within range for several programs. Keep drilling."
    elif final_upg <= 2.6:
        verdict = "🟡 Borderline — May qualify at less competitive campuses."
    elif final_upg <= 3.0:
        verdict = "🟠 Below Threshold — Needs significant improvement in both UPCAT and grades."
    else:
        verdict = "🔴 Not Yet Ready — Focus on fundamentals. Retake with lower difficulty first."

    # ── TOPIC ANALYSIS ──
    def analyze_topics(items, user_ans):
        topic_results = {}
        for q in items:
            topic = q.get('topic', 'Unknown')
            short = topic.split(' — ')[0] if ' — ' in topic else topic
            inum = q.get('item_number')
            correct = user_ans.get(inum) == q.get('correct_answer')
            if short not in topic_results:
                topic_results[short] = {'correct': 0, 'total': 0}
            topic_results[short]['total'] += 1
            if correct: topic_results[short]['correct'] += 1
        return topic_results

    math_topics = analyze_topics(math_items_data, u_math) if math_items_data else {}
    sci_topics = analyze_topics(sci_items_data, u_sci) if sci_items_data else {}

    # ── RESULTS HERO ──
    st.markdown(f"""
    <div class='results-hero' role="main" aria-label="Your UPG Result">
        <div class='upg-label'>YOUR UNIVERSITY PREDICTED GRADE (UPG)</div>
        <div class='upg-display' aria-label="UPG: {final_upg:.3f}">{final_upg:.3f}</div>
        <div class='upg-verdict'>{verdict}</div>
        <div style='color:rgba(255,255,255,0.4); font-family:var(--font-mono); font-size:0.64rem; margin-top:10px; letter-spacing:0.1em; position:relative; z-index:1;'>
            1.000 (HIGHEST) → 5.000 (LOWEST) · Simulated rank #{sim_rank:,} / 140,000 applicants
        </div>
        <div style='color:rgba(255,255,255,0.5); font-family:var(--font-ui); font-size:0.82rem; margin-top:8px; position:relative; z-index:1;'>
            ~{100*(1-overall_pct):.1f}th percentile · {"✅ LIKELY QUALIFIED for at least one campus" if final_upg <= 2.8 else "❌ Below typical campus cutoffs — keep training"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRIC TILES ──
    metrics = []
    metrics.append((f"{final_upg:.3f}", "", "Final UPG", "Lower is better"))
    metrics.append((f"#{sim_rank:,}", "teal", "Simulated Rank", f"Top {100*(1-overall_pct):.1f}%"))
    metrics.append((f"{grade_upg_final:.3f}", "green", "Grades UPG (40%)", f"Avg: {raw_avg:.1f}/100"))
    metrics.append((f"{upcat_upg:.3f}", "amber" if upcat_upg > 2.5 else "green", "UPCAT UPG (60%)", f"Z: {upcat_z:+.2f}"))
    if math_items_data:
        metrics.append((f"{m_pct*100:.1f}%", "green" if m_pct >= 0.5 else "red", "Math Score %", f"{m_correct}C · {m_wrong}W · {m_blank}B"))
    if sci_items_data:
        metrics.append((f"{s_pct*100:.1f}%", "teal" if s_pct >= 0.5 else "red", "Science Score %", f"{s_correct}C · {s_wrong}W · {s_blank}B"))

    cols_m = st.columns(min(len(metrics), 4))
    for i, (val, cls, lbl, sub) in enumerate(metrics):
        with cols_m[i % 4]:
            st.markdown(f"""
            <div class='metric-tile' role="figure" aria-label="{lbl}: {val}">
                <div class='metric-val {cls}'>{val}</div>
                <div class='metric-label'>{lbl}</div>
                <div class='metric-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── SCORE PANELS ──
    st.markdown("<br>", unsafe_allow_html=True)
    panels_cols = st.columns(sum([1 if math_items_data else 0, 1 if sci_items_data else 0]))
    pi = 0
    if math_items_data:
        e_m, e_ms = int(elapsed_math // 60), int(elapsed_math % 60)
        with panels_cols[pi]:
            penalty_m = m_wrong * 0.25
            st.markdown(f"""
            <div class='score-panel' role="region" aria-label="Math breakdown">
                <h4>🔢 Mathematics Breakdown</h4>
                <div class='score-row'><span class='score-lbl'>Correct</span><span class='score-val c'>{m_correct} / {m_total}</span></div>
                <div class='score-row'><span class='score-lbl'>Wrong</span><span class='score-val w'>{m_wrong} (−{penalty_m:.2f} pts)</span></div>
                <div class='score-row'><span class='score-lbl'>Blank</span><span class='score-val'>{m_blank}</span></div>
                <div class='score-row'><span class='score-lbl'>Raw Score (RMW)</span><span class='score-val g'>{m_raw:.2f} / {m_total}</span></div>
                <div class='score-row'><span class='score-lbl'>Percentage</span><span class='score-val g'>{m_pct*100:.1f}%</span></div>
                <div class='score-row'><span class='score-lbl'>Accuracy on Attempted</span><span class='score-val'>{(m_correct/max(1,m_correct+m_wrong)*100):.1f}%</span></div>
                <div class='score-row'><span class='score-lbl'>Time Spent</span><span class='score-val'>{e_m}m {e_ms}s ({elapsed_math/max(1,m_total):.0f}s/item)</span></div>
                <div class='score-row'><span class='score-lbl'>UPCAT Budget</span><span class='score-val'>72s/item (60min÷50items)</span></div>
            </div>
            """, unsafe_allow_html=True)
        pi += 1

    if sci_items_data:
        e_s, e_ss = int(elapsed_sci // 60), int(elapsed_sci % 60)
        with panels_cols[pi]:
            penalty_s = s_wrong * 0.25
            st.markdown(f"""
            <div class='score-panel' role="region" aria-label="Science breakdown">
                <h4>🔬 Science Breakdown</h4>
                <div class='score-row'><span class='score-lbl'>Correct</span><span class='score-val c'>{s_correct} / {s_total}</span></div>
                <div class='score-row'><span class='score-lbl'>Wrong</span><span class='score-val w'>{s_wrong} (−{penalty_s:.2f} pts)</span></div>
                <div class='score-row'><span class='score-lbl'>Blank</span><span class='score-val'>{s_blank}</span></div>
                <div class='score-row'><span class='score-lbl'>Raw Score (RMW)</span><span class='score-val g'>{s_raw:.2f} / {s_total}</span></div>
                <div class='score-row'><span class='score-lbl'>Percentage</span><span class='score-val g'>{s_pct*100:.1f}%</span></div>
                <div class='score-row'><span class='score-lbl'>Accuracy on Attempted</span><span class='score-val'>{(s_correct/max(1,s_correct+s_wrong)*100):.1f}%</span></div>
                <div class='score-row'><span class='score-lbl'>Time Spent</span><span class='score-val'>{e_s}m {e_ss}s ({elapsed_sci/max(1,s_total):.0f}s/item)</span></div>
                <div class='score-row'><span class='score-lbl'>UPCAT Budget</span><span class='score-val'>60s/item (45min÷45items)</span></div>
            </div>
            """, unsafe_allow_html=True)

    # ── TOPIC HEATMAPS ──
    if math_topics or sci_topics:
        st.markdown("""
        <div class='sec-div'><h3>🔥 Topic Mastery Heatmap</h3><div class='sec-line'></div></div>
        """, unsafe_allow_html=True)

        h_cols = st.columns(sum([1 if math_topics else 0, 1 if sci_topics else 0]))
        hi = 0
        for topics_dict, title, clr in [(math_topics, "🔢 Math Topics", "#1d4ed8"), (sci_topics, "🔬 Science Topics", "#0e7490")]:
            if not topics_dict: continue
            with h_cols[hi]:
                st.markdown(f"<h4 style='font-family:var(--font-display); font-size:1.0rem; margin-bottom:12px; color:{clr};'>{title}</h4>", unsafe_allow_html=True)
                skill_html = "<div class='skill-heatmap'>"
                for sk, data in sorted(topics_dict.items(), key=lambda x: x[1]['correct']/max(1,x[1]['total'])):
                    pct_sk = data['correct'] / max(1, data['total']) * 100
                    bar_cls = "strong" if pct_sk >= 70 else ("mid" if pct_sk >= 40 else "weak")
                    pct_color = "#065f46" if bar_cls == "strong" else ("#d97706" if bar_cls == "mid" else "#dc2626")
                    skill_html += f"""
                    <div class='skill-row' role='listitem' aria-label='{sk}: {pct_sk:.0f}%'>
                        <span style='font-family:var(--font-ui); font-size:0.73rem; flex:1; color:var(--fg-mid); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;' title='{sk}'>{sk[:28]}{"…" if len(sk)>28 else ""}</span>
                        <div class='skill-bar-outer'><div class='skill-bar-inner {bar_cls}' style='width:{pct_sk:.0f}%;'></div></div>
                        <span class='skill-pct' style='color:{pct_color};'>{pct_sk:.0f}%</span>
                        <span style='font-family:var(--font-mono); font-size:0.56rem; color:var(--fg-mute);'>{data["correct"]}/{data["total"]}</span>
                    </div>"""
                skill_html += "</div>"
                st.markdown(skill_html, unsafe_allow_html=True)
            hi += 1

    # ── ADMISSION ENGINE ──
    st.markdown("""
    <div class='sec-div'><h3>🏛️ Cascading Admission Decision Engine</h3><div class='sec-line'></div></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='notice'>
        📊 <strong>Reality check:</strong> Only ~10–13% of ~140,000 UPCAT applicants earn their 1st-choice campus AND 1st-choice program.
        About 18–22% qualify for at least one campus. Your simulated UPG of <strong>{final_upg:.3f}</strong> places you
        at rank <strong>#{sim_rank:,}</strong>. This simulation uses research-based modeling — not official UP formulas.
    </div>
    """, unsafe_allow_html=True)

    def evaluate_program(campus, program, cutoff, upg):
        tier = get_program_tier(campus, program)
        adj = {"Triple Quota": -0.40, "Double Quota": -0.22, "Single Quota": -0.06, "Less Popular": +0.08}.get(tier, 0.0)
        req = max(1.100, cutoff + adj)
        if upg <= req:
            badge = "<span class='badge-pass'>✅ PASSED</span>"
            note = "Within quota band"
        elif upg <= req + 0.15:
            badge = "<span class='badge-wait'>🟡 DPWAS RISK</span>"
            note = "Borderline — may compete for waitlisted slots"
        else:
            badge = "<span class='badge-fail'>❌ BELOW CUTOFF</span>"
            note = "Exceeds slot ceiling for this program"
        return badge, req, note, tier

    a_col1, a_col2 = st.columns(2)
    for acol, campus, progs, cn in [
        (a_col1, campus_1, [c1_p1, c1_p2, c1_p3], "1st"),
        (a_col2, campus_2, [c2_p1, c2_p2, c2_p3], "2nd")
    ]:
        cutoff = CAMPUS_DATA[campus]["cutoff"]
        recon = CAMPUS_DATA[campus]["recon"]
        qualified = final_upg <= cutoff
        hdr_cls = "" if qualified else "rejected"
        stat = "✅ QUALIFIED" if qualified else "❌ NOT QUALIFIED"

        with acol:
            st.markdown(f"""
            <div class='campus-shell' role="region" aria-label="{cn} campus: {campus}">
                <div class='campus-header {hdr_cls}'>
                    <h4>{cn} Choice — {campus}</h4>
                    <p>Cutoff: {cutoff:.3f} · Your UPG: {final_upg:.3f} · {stat} · {CAMPUS_DATA[campus]["note"]}</p>
                </div>
                <div class='campus-body'>
            """, unsafe_allow_html=True)

            if campus == campus_2 and final_upg <= CAMPUS_DATA[campus_1]["cutoff"]:
                st.info("📌 Qualified at Campus 1 — Campus 2 is nullified in cascading UP system.")

            if qualified:
                for i, prog in enumerate(progs, 1):
                    badge, req, note, tier = evaluate_program(campus, prog, cutoff, final_upg)
                    st.markdown(f"""
                    <div class='prog-row'>
                        <div>
                            <div class='prog-name'>P{i}: {prog}</div>
                            <div class='prog-meta-txt'>{tier} · Eff. cutoff ~{req:.3f} · {note}</div>
                        </div>
                        <div>{badge}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                recon_ok = recon > 0 and final_upg <= recon
                st.markdown(f"""
                <div style='padding:16px; text-align:center; font-family:var(--font-ui); font-size:0.86rem; color:var(--fg-mid);'>
                    UPG {final_upg:.3f} exceeds cutoff {cutoff:.3f}.<br><br>
                    Recon threshold: <strong>{f"{recon:.3f}" if recon > 0 else "None"}</strong><br>
                    {"✅ Recon-eligible" if recon_ok else ("❌ Beyond recon range" if recon > 0 else "🚫 No appeals policy")}
                </div>""", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ── DEEP ANALYTICS TABS ──
    st.markdown("""
    <div class='sec-div'><h3>🔬 Deep Analytics & Personalized Feedback</h3><div class='sec-line'></div></div>
    """, unsafe_allow_html=True)

    tab_labels = ["📊 Overview", "📐 Grade & UPG Math", "🧮 UPCAT Math Deep Dive", "⚖️ Recon & DPWAS"]
    if math_items_data: tab_labels.append("🔢 Math Item Review")
    if sci_items_data: tab_labels.append("🔬 Science Item Review")
    tabs_result = st.tabs(tab_labels)
    ti = 0

    # ── OVERVIEW ──
    with tabs_result[ti]:
        ti_math_pct = m_pct * 100 if math_items_data else None
        ti_sci_pct = s_pct * 100 if sci_items_data else None
        penalty_total = (m_wrong + s_wrong) * 0.25
        guess_rate = (m_wrong + s_wrong) / max(1, (m_correct + m_wrong + s_correct + s_wrong))

        # Math topic gaps
        math_errors = {sk: (1 - data['correct']/max(1,data['total']))*100
                      for sk, data in math_topics.items() if data['total'] > 0}
        top_math_gaps = sorted(math_errors.items(), key=lambda x: -x[1])[:4]

        sci_errors = {sk: (1 - data['correct']/max(1,data['total']))*100
                     for sk, data in sci_topics.items() if data['total'] > 0}
        top_sci_gaps = sorted(sci_errors.items(), key=lambda x: -x[1])[:4]

        # Time analysis
        math_time_ratio = (elapsed_math / max(1, m_total)) / 72 if m_total > 0 else None  # 72s budget
        sci_time_ratio = (elapsed_sci / max(1, s_total)) / 60 if s_total > 0 else None   # 60s budget

        st.markdown(f"""
        <div class='deep-box' role="region" aria-label="Overview">
            <h5>📊 Performance Overview — {difficulty} Simulation · {sim_rank:,} Simulated Rank / 140,000</h5>
            <p style='font-family:var(--font-body); font-size:0.91rem; line-height:1.90; color:var(--fg-mid); margin-bottom:14px;'>
                You completed this <strong>{difficulty}</strong>-difficulty simulation placing in the 
                <strong>{overall_pct*100:.1f}th percentile</strong> of a simulated 140,000-applicant cohort.
                Combined score: <strong>{combined_pct*100:.1f}%</strong> vs. competitive mean <strong>{MEAN_BASELINE*100:.0f}%</strong> (Z={upcat_z:+.2f}).
                Total penalty incurred: <strong>−{penalty_total:.2f} pts</strong> from {m_wrong+s_wrong} wrong answers.
                {"✅ Efficient penalty profile." if guess_rate < 0.22 else "⚠️ Moderate penalty load — be more selective with guesses." if guess_rate < 0.38 else "🔴 High penalty load — aggressive guessing cost you significantly."}
            </p>
            <div class='feedback-grid'>
                {f"""<div class='feedback-card'>
                    <div class='feedback-card-title'>🔢 Math Performance ({m_correct}/{m_total})</div>
                    <div class='feedback-card-body'>
                        <strong>{m_pct*100:.0f}% accuracy</strong><br>
                        {"✅ Strong mathematical foundation." if m_pct >= 0.65 else
                        "📘 Moderate — focus on JHS algebra fundamentals and practice computation speed." if m_pct >= 0.45 else
                        "📖 Needs significant work — drill basic algebra (linear equations, factoring, word problems) daily. These dominate ~60% of UPCAT Math."}
                    </div>
                </div>""" if math_items_data else ""}
                {f"""<div class='feedback-card'>
                    <div class='feedback-card-title'>🔬 Science Performance ({s_correct}/{s_total})</div>
                    <div class='feedback-card-body'>
                        <strong>{s_pct*100:.0f}% accuracy</strong><br>
                        {"✅ Strong conceptual science understanding." if s_pct >= 0.65 else
                        "📘 Moderate — practice reading data tables and experimental passages quickly." if s_pct >= 0.45 else
                        "📖 Needs work — UPCAT Science is ~60% passage/data-based. Practice extracting information from experimental scenarios, not just memorizing facts."}
                    </div>
                </div>""" if sci_items_data else ""}
                {f"""<div class='feedback-card'>
                    <div class='feedback-card-title'>⏱️ Math Time Management</div>
                    <div class='feedback-card-body'>
                        <strong>{int(elapsed_math//60)}m {int(elapsed_math%60)}s</strong> · {elapsed_math/max(1,m_total):.0f}s/item<br>
                        UPCAT budget: ~72s/item (60min÷50 items)<br>
                        {"✅ On pace." if math_time_ratio and 0.6 <= math_time_ratio <= 1.3 else
                        "⚡ Rushed — accuracy may have suffered." if math_time_ratio and math_time_ratio < 0.6 else
                        "⏰ Over budget — practice faster computation. Learn mental math shortcuts for fractions, percentages, and factoring."}
                    </div>
                </div>""" if math_items_data else ""}
                {f"""<div class='feedback-card'>
                    <div class='feedback-card-title'>⏱️ Science Time Management</div>
                    <div class='feedback-card-body'>
                        <strong>{int(elapsed_sci//60)}m {int(elapsed_sci%60)}s</strong> · {elapsed_sci/max(1,s_total):.0f}s/item<br>
                        UPCAT budget: ~60s/item (45min÷45 items)<br>
                        {"✅ On pace." if sci_time_ratio and 0.6 <= sci_time_ratio <= 1.3 else
                        "⚡ Rushed — don't skip reading the stimulus." if sci_time_ratio and sci_time_ratio < 0.6 else
                        "⏰ Over budget — for passage items: read the QUESTION first, then scan the stimulus for the relevant data point."}
                    </div>
                </div>""" if sci_items_data else ""}
                <div class='feedback-card'>
                    <div class='feedback-card-title'>⚡ RMW Strategy Analysis</div>
                    <div class='feedback-card-body'>
                        Penalty: <strong>−{penalty_total:.2f} pts</strong><br>
                        Wrong: {m_wrong+s_wrong} of {m_correct+m_wrong+s_correct+s_wrong} attempted<br>
                        {"✅ Excellent — answered only when confident." if guess_rate < 0.20 else
                        "Good — slightly aggressive but manageable." if guess_rate < 0.30 else
                        "⚠️ Too many wrong guesses. Rule: leave blank unless you can eliminate ≥2 options."}
                    </div>
                </div>
                <div class='feedback-card'>
                    <div class='feedback-card-title'>🎯 Priority Study Plan</div>
                    <div class='feedback-card-body'>
                        {"Math: Drill algebra basics daily · Science: Practice reading experimental data · Increase difficulty level on next attempt · Target 70%+ on current difficulty first" if combined_pct < 0.55 else
                        "Math: Focus on identified weak topics below · Science: Practice passage items for speed · Move to Brutal difficulty · Target 0 wrong-guess penalty"}
                    </div>
                </div>
            </div>
            {f"<div style='margin-top:14px; padding:13px 17px; background:var(--blue-pale); border-radius:8px; border:1px solid #bfdbfe;'><strong style='color:#1d4ed8; font-family:var(--font-ui);'>🔢 Math Weak Areas:</strong><ul style='margin:6px 0 0 16px; font-family:var(--font-mono); font-size:0.76rem;'>" + "".join([f"<li>{sk} — {e:.0f}% error rate</li>" for sk, e in top_math_gaps]) + "</ul></div>" if top_math_gaps else ""}
            {f"<div style='margin-top:10px; padding:13px 17px; background:var(--teal-pale); border-radius:8px; border:1px solid #a5f3fc;'><strong style='color:#0e7490; font-family:var(--font-ui);'>🔬 Science Weak Areas:</strong><ul style='margin:6px 0 0 16px; font-family:var(--font-mono); font-size:0.76rem;'>" + "".join([f"<li>{sk} — {e:.0f}% error rate</li>" for sk, e in top_sci_gaps]) + "</ul></div>" if top_sci_gaps else ""}
        </div>
        """, unsafe_allow_html=True)
    ti += 1

    # ── GRADES MATH ──
    with tabs_result[ti]:
        st.markdown("<div class='feedback-box blue-accent'>", unsafe_allow_html=True)
        st.markdown("### 📐 Grade Standardization — Science & Math Subjects (40% UPG Weight)")
        g_cols = st.columns(4)
        all_grade_inputs = [
            ("G8 Math", g8_math), ("G9 Math", g9_math), ("G10 Math", g10_math),
            ("Pre-Calculus", g11_precalc), ("Basic Calc", g11_calc), ("Stats & Prob", g11_stats),
            ("Gen Math", g11_genmath), ("G8 Science", g8_sci), ("G9 Science", g9_sci),
            ("G10 Science", g10_sci), ("Gen Bio 1", g11_bio1), ("Gen Bio 2", g11_bio2),
            ("Earth Science", g11_earth)
        ]
        for i, (lbl, val) in enumerate(all_grade_inputs):
            g_cols[i % 4].metric(lbl, f"{val:.1f}")

        math_avg = float(np.mean(math_grades))
        sci_avg = float(np.mean(sci_grades))
        st.markdown(f"""
        **Math Grade Average:** {math_avg:.2f} / 100  
        **Science Grade Average:** {sci_avg:.2f} / 100  
        **Overall Sci+Math Average:** {raw_avg:.2f} / 100  
        **School Modifier (JHS+SHS avg):** {avg_mod:+.3f} ({SCHOOL_TIERS[jhs_type]['label']} / {SCHOOL_TIERS[shs_type]['label']})  
        **Grade UPG (raw → adjusted):** {grade_upg_raw:.3f} → **{grade_upg_final:.3f}**
        """)
        if avg_mod > 0:
            st.success(f"✅ **Palugit active:** School rigor protection improves your Grade UPG by {avg_mod:.3f} pts ({grade_upg_raw:.3f} → {grade_upg_final:.3f}).")
        elif avg_mod < 0:
            st.warning(f"⚠️ **Pabigat applied:** Private school grade inflation adjustment worsens Grade UPG by {abs(avg_mod):.3f} pts.")
        with st.expander("📐 Full Grade UPG Formula"):
            st.latex(r"UPG_{\text{grade, raw}} = 5.0 - \left(\frac{\bar{G} - 75}{25}\right) \times 4.0")
            st.latex(f"= 5.0 - \\left(\\frac{{{raw_avg:.2f} - 75}}{{25}}\\right) \\times 4.0 = {grade_upg_raw:.3f}")
            st.latex(r"UPG_{\text{final}} = \text{clamp}\left(UPG_{\text{raw}} - \Delta_{\text{school}},\;1.0,\;5.0\right)")
            st.latex(f"= {grade_upg_raw:.3f} - ({avg_mod:+.3f}) = {grade_upg_final:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

    # ── UPCAT MATH ──
    with tabs_result[ti]:
        st.markdown("<div class='feedback-box teal-accent'>", unsafe_allow_html=True)
        st.markdown("### 🧮 UPCAT Math Deep Dive (RMW Forensics · 60% UPG Weight)")
        st.markdown(f"""
        Combined RMW score: {combined_pct*100:.1f}% vs. competitive mean {MEAN_BASELINE*100:.0f}% (σ={SIGMA:.2f}).
        Z = {upcat_z:+.2f} → **UPCAT UPG: {upcat_upg:.3f}** → simulated rank **#{sim_rank:,}** (top {100*(1-overall_pct):.1f}%).
        """)
        with st.expander("📐 Full UPCAT UPG Derivation"):
            st.latex(r"\text{RMW} = \text{Correct} - \frac{1}{4}\text{Wrong}")
            st.latex(r"Z = \frac{\bar{P} - \mu}{\sigma} = " + f"\\frac{{{combined_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {upcat_z:.4f}")
            st.latex(r"UPG_{\text{UPCAT}} = \text{clamp}(2.75 - Z \times 0.55) = " + f"{upcat_upg:.3f}")
            st.latex(r"\text{Final UPG} = 0.40 \times UPG_{\text{grades}} + 0.60 \times UPG_{\text{UPCAT}}")
            st.latex(f"= 0.40 \\times {grade_upg_final:.3f} + 0.60 \\times {upcat_upg:.3f} = {final_upg:.3f}")
        with st.expander("📐 UPCAT Math: What the Exam Tests and Why"):
            st.markdown(f"""
            **UPCAT Math is NOT a calculus test.** Research and insider accounts consistently confirm:
            
            - ~**60-65% JHS topics**: Linear algebra, factoring, word problems, geometry, number sense — topics every Filipino student studies in Grades 7-10. Most applicants (STEM and non-STEM alike) have studied these.
            - ~**20-25% intermediate topics**: Statistics, sequences/series, exponents/logarithms — tested at a moderate level.
            - ~**10-15% SHS/trig**: Pre-Calculus, Calculus basics, Trigonometry — appears rarely, usually 2-5 items max. Even STEM students should not bank on these.

            **Why no calculator?** The UPCAT tests *mathematical reasoning*, not *computation speed*. Items are designed so a prepared student can solve them mentally or with simple hand computation in under 90 seconds. If an item seems to require a calculator, either there is a smarter approach, or the numbers are chosen to be "friendly" (divisible, perfect squares, simple fractions).

            **The Real Trap in UPCAT Math**: Items look simple but are designed to catch students who memorize formulas without understanding. Distractors are specifically constructed to match the output of common errors (sign mistakes, forgetting to square root, stopping one step early). This is why understanding > memorization.

            **Your penalty this session:** −{(m_wrong+s_wrong)*0.25:.2f} pts total. 
            If you had left all wrong answers blank: Math raw would be {m_correct:.0f} (vs {m_raw:.2f}), Science raw {s_correct:.0f} (vs {s_raw:.2f}).
            Break-even guessing requires ≥25% probability — you need to eliminate **2 options** to make guessing statistically worthwhile.
            """)
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

    # ── RECON ──
    with tabs_result[ti]:
        st.markdown("<div class='feedback-box amber-accent'>", unsafe_allow_html=True)
        st.markdown("### ⚖️ DPWAS, Reconsideration & Strategic Admission Planning")
        st.markdown(f"""
        **The Real Numbers:** Of ~140,000 UPCAT applicants, approximately 16,000–18,000 (11–13%) earn admission
        to their **first-choice campus and first-choice degree program**. About 25,000–30,000 (18–22%) qualify
        for at least one program at any UP campus. Your simulated rank of **#{sim_rank:,}** places you in the
        {"**qualifying zone for most campuses**" if sim_rank <= 28000 else "**competitive zone but below typical cutoffs**" if sim_rank <= 50000 else "**zone requiring significant score improvement**"}.

        **DPWAS (Deferred Placement Waitlisted Admission Status):** You are campus-qualified but no program slot
        is available at time of results. This is NOT rejection. Slots open as accepted students decline, shift,
        or transfer. Programs with "Triple Quota" have more slots and higher DPWAS resolution rates.

        **Reconsideration:** Available at select campuses (see below) for UPGs slightly above the cutoff.
        UPLB reconsideration is most accessible when the campus was your stated 1st choice AND the program was your 1st priority.
        """)
        for campus in [campus_1, campus_2]:
            recon = CAMPUS_DATA[campus]["recon"]
            cutoff = CAMPUS_DATA[campus]["cutoff"]
            st.markdown(f"**{campus}** — Cutoff: {cutoff:.3f}")
            if recon == 0.0:
                st.error(f"🚫 **{campus}: Absolute no-reconsideration policy.** No appeals accepted.")
            elif final_upg <= cutoff:
                st.success(f"✅ Qualified ({final_upg:.3f} ≤ {cutoff:.3f}). Reconsideration not needed.")
            elif final_upg <= recon:
                st.warning(f"📋 **Recon-eligible** — UPG {final_upg:.3f} within recon window ({cutoff:.3f}–{recon:.3f}). Not guaranteed.")
            else:
                st.error(f"❌ UPG {final_upg:.3f} exceeds recon threshold ({recon:.3f}).")
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

    # ── MATH ITEM REVIEW ──
    if math_items_data:
        with tabs_result[ti]:
            st.markdown("### 🔢 Mathematics — Item-by-Item Review with Full Solutions")

            m_wrong_list = [q for q in math_items_data if u_math.get(q.get('item_number')) not in [None, q.get('correct_answer')] and u_math.get(q.get('item_number')) is not None]
            m_correct_list = [q for q in math_items_data if u_math.get(q.get('item_number')) == q.get('correct_answer')]
            m_blank_list = [q for q in math_items_data if u_math.get(q.get('item_number')) is None]

            st.markdown(f"""
            <div style='display:flex; gap:10px; margin-bottom:18px; flex-wrap:wrap;'>
                <div class='stat-pill'><div class='stat-pill-num' style='color:#dc2626;'>{len(m_wrong_list)}</div><div class='stat-pill-label'>Wrong</div></div>
                <div class='stat-pill'><div class='stat-pill-num' style='color:#065f46;'>{len(m_correct_list)}</div><div class='stat-pill-label'>Correct</div></div>
                <div class='stat-pill'><div class='stat-pill-num' style='color:#64748b;'>{len(m_blank_list)}</div><div class='stat-pill-label'>Blank</div></div>
            </div>
            """, unsafe_allow_html=True)

            if m_wrong_list:
                st.markdown(f"#### ❌ Wrong Answers ({len(m_wrong_list)}) — Priority Review:")
                for q in m_wrong_list:
                    inum = q.get('item_number')
                    u = u_math.get(inum, '?')
                    c = q.get('correct_answer')
                    topic = q.get('topic', '')
                    with st.expander(f"❌ Math {inum} | {topic.split(' — ')[0][:35]} | Chose {u} → Correct: {c} | −0.25 pts"):
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                            elif lt == u: st.error(f"❌ **{lt})** {opts.get(lt,'')} ← Your answer")
                            else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                        st.divider()
                        da = q.get('distractor_analysis', {})
                        if da and u in da:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Error you made ({err.get('type','')}):** {err.get('error','')}")
                            else:
                                st.warning(f"**Why {u} is wrong:** {err}")
                        solution = q.get('solution', '')
                        if solution:
                            st.info(f"**📐 Step-by-Step Solution:**\n\n{solution}")
                        kc = q.get('key_concept', '')
                        if kc: st.caption(f"💡 Key concept: {kc}")

            if m_correct_list:
                st.markdown(f"#### ✅ Correct Answers ({len(m_correct_list)}):")
                for q in m_correct_list:
                    inum = q.get('item_number')
                    c = q.get('correct_answer')
                    with st.expander(f"✅ Math {inum} | {q.get('topic','').split(' — ')[0][:35]} | +1.0 pt"):
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                            else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                        with st.expander("Show solution"):
                            st.info(f"**Solution:**\n\n{q.get('solution','')}")

            if m_blank_list:
                st.markdown(f"#### ⚪ Skipped ({len(m_blank_list)}):")
                for q in m_blank_list:
                    inum = q.get('item_number')
                    c = q.get('correct_answer')
                    with st.expander(f"⚪ Math {inum} | {q.get('topic','').split(' — ')[0][:35]} | 0 pts (skipped)"):
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                            else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                        st.info(f"**Solution:**\n\n{q.get('solution','')}")
        ti += 1

    # ── SCIENCE ITEM REVIEW ──
    if sci_items_data:
        with tabs_result[ti]:
            st.markdown("### 🔬 Science — Item-by-Item Review with Full Explanations")

            s_wrong_list = [q for q in sci_items_data if u_sci.get(q.get('item_number')) not in [None, q.get('correct_answer')] and u_sci.get(q.get('item_number')) is not None]
            s_correct_list = [q for q in sci_items_data if u_sci.get(q.get('item_number')) == q.get('correct_answer')]
            s_blank_list = [q for q in sci_items_data if u_sci.get(q.get('item_number')) is None]

            st.markdown(f"""
            <div style='display:flex; gap:10px; margin-bottom:18px; flex-wrap:wrap;'>
                <div class='stat-pill'><div class='stat-pill-num' style='color:#dc2626;'>{len(s_wrong_list)}</div><div class='stat-pill-label'>Wrong</div></div>
                <div class='stat-pill'><div class='stat-pill-num' style='color:#065f46;'>{len(s_correct_list)}</div><div class='stat-pill-label'>Correct</div></div>
                <div class='stat-pill'><div class='stat-pill-num' style='color:#64748b;'>{len(s_blank_list)}</div><div class='stat-pill-label'>Blank</div></div>
            </div>
            """, unsafe_allow_html=True)

            if s_wrong_list:
                st.markdown(f"#### ❌ Wrong Answers ({len(s_wrong_list)}) — Priority Review:")
                for q in s_wrong_list:
                    inum = q.get('item_number')
                    u = u_sci.get(inum, '?')
                    c = q.get('correct_answer')
                    topic = q.get('topic', '')
                    stim_type = q.get('stimulus_type', '')
                    with st.expander(f"❌ Sci {inum} | {topic.split(' — ')[0][:30]} | Chose {u} → Correct: {c} | −0.25 pts"):
                        stim = q.get('stimulus', '')
                        if stim:
                            if stim_type == "DATA_TABLE":
                                st.markdown(f"**Data:**\n{stim}", unsafe_allow_html=True)
                            else:
                                st.markdown(f"""<div class='sci-passage' style='max-height:160px;'>{stim}</div>""", unsafe_allow_html=True)
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                            elif lt == u: st.error(f"❌ **{lt})** {opts.get(lt,'')} ← Your answer")
                            else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                        st.divider()
                        da = q.get('distractor_analysis', {})
                        if da and u in da:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Why you chose {u} ({err.get('type','')}):** {err.get('error','')}")
                        if q.get('solution'): st.info(f"**🔬 Full Explanation:**\n\n{q.get('solution','')}")
                        if q.get('passage_reference'): st.caption(f"📍 Evidence location: {q.get('passage_reference','')}")
                        if q.get('key_concept'): st.caption(f"💡 Core concept: {q.get('key_concept','')}")

            if s_correct_list:
                st.markdown(f"#### ✅ Correct Answers ({len(s_correct_list)}):")
                for q in s_correct_list:
                    inum = q.get('item_number')
                    c = q.get('correct_answer')
                    with st.expander(f"✅ Sci {inum} | {q.get('topic','').split(' — ')[0][:30]} | +1.0 pt"):
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                            else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                        with st.expander("Show explanation"):
                            st.info(f"**Explanation:**\n\n{q.get('solution','')[:400]}...")

            if s_blank_list:
                st.markdown(f"#### ⚪ Skipped ({len(s_blank_list)}):")
                for q in s_blank_list:
                    inum = q.get('item_number')
                    c = q.get('correct_answer')
                    with st.expander(f"⚪ Sci {inum} | {q.get('topic','').split(' — ')[0][:30]} | 0 pts"):
                        stim = q.get('stimulus', '')
                        if stim:
                            st.markdown(f"""<div class='sci-passage' style='max-height:120px;'>{stim}</div>""", unsafe_allow_html=True)
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                            else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                        st.info(f"**Explanation:**\n\n{q.get('solution','')}")

    # ── RESET ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns([1,2,1])
    with r2:
        st.markdown("""<div style='text-align:center; margin-bottom:10px; font-family:var(--font-ui); font-size:0.80rem; color:var(--fg-mute);'>
            Generate a fresh simulation with new items — your selections are preserved.
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Generate Fresh Items & Reset", use_container_width=True, type="secondary",
                     help="Clears all answers and generates brand-new items"):
            for k in ['user_answers_math','user_answers_sci','submitted','test_data',
                      'flagged_items','math_started','sci_started','math_submitted','sci_submitted',
                      'math_start_time','sci_start_time','elapsed_math','elapsed_sci']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
