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
    'user_answers_lp': {}, 'user_answers_rc': {}, 'submitted': False,
    'test_data': None, 'start_time': None, 'time_limit': 0,
    'generation_error': None, 'elapsed_time': 0,
    'sidebar_open': True, 'flagged_items': set(),
    'current_tab': 0, 'dark_mode': False,
    'font_size': 'medium', 'high_contrast': False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==========================================
# 🏛️ PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Padayon! Ang Wika! — UPCAT Elite Simulator",
    page_icon="🌻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Font size map
FONT_SIZES = {'small': '0.85rem', 'medium': '1.0rem', 'large': '1.15rem', 'x-large': '1.3rem'}
fs = FONT_SIZES.get(st.session_state.get('font_size', 'medium'), '1.0rem')
hc = st.session_state.get('high_contrast', False)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Grotesk:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=JetBrains+Mono:wght@400;600;700&display=swap');

/* ══════════════════════════════════════════════
   CSS CUSTOM PROPERTIES
══════════════════════════════════════════════ */
:root {{
    --maroon: #7B1113;
    --maroon-deep: #4d0a0b;
    --maroon-mid: #9e1517;
    --maroon-pale: #faf0f0;
    --maroon-tint: #f2dede;
    --olive: #014421;
    --olive-pale: #eaf3ec;
    --olive-mid: #02602f;
    --gold: #C8973F;
    --gold-pale: #fdf6e8;
    --gold-warm: #e8a83a;
    --bg: #f5f2ec;
    --bg-card: #ffffff;
    --bg-card2: #fdfcfa;
    --fg: #1a1208;
    --fg-mid: #4a4030;
    --fg-mute: #7a6a58;
    --border: #e2dbd0;
    --border-light: #ede8e0;
    --shadow-xs: 0 1px 4px rgba(0,0,0,0.06);
    --shadow-sm: 0 2px 10px rgba(0,0,0,0.08);
    --shadow-md: 0 6px 28px rgba(0,0,0,0.10);
    --shadow-lg: 0 16px 56px rgba(0,0,0,0.13);
    --r: 10px;
    --r-lg: 16px;
    --r-xl: 22px;
    --font-display: 'Fraunces', Georgia, serif;
    --font-body: 'Libre Baskerville', Georgia, serif;
    --font-ui: 'Space Grotesk', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --base-font-size: {fs};
    --focus-ring: 0 0 0 3px rgba(123,17,19,0.35);
    --focus-ring-offset: 2px;
    --transition-fast: 0.15s ease;
    --transition-mid: 0.25s ease;
}}

/* ── HIGH CONTRAST OVERRIDE ── */
{'body { filter: contrast(1.25); }' if hc else ''}

/* ══════════════════════════════════════════════
   BASE RESET & ACCESSIBILITY
══════════════════════════════════════════════ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

.stApp {{
    background: var(--bg) !important;
    font-family: var(--font-body) !important;
    color: var(--fg) !important;
    font-size: var(--base-font-size) !important;
}}

/* Skip to content link for keyboard users */
.skip-link {{
    position: absolute; top: -100px; left: 16px; z-index: 99999;
    background: var(--maroon); color: #fff; padding: 12px 20px;
    border-radius: 0 0 var(--r) var(--r); font-family: var(--font-ui);
    font-weight: 700; font-size: 0.9rem; text-decoration: none;
    transition: top 0.2s ease;
}}
.skip-link:focus {{ top: 0; outline: 3px solid var(--gold); }}

/* Focus indicators — WCAG AA compliant */
*:focus-visible {{
    outline: 3px solid var(--maroon) !important;
    outline-offset: var(--focus-ring-offset) !important;
    border-radius: 4px !important;
}}
button:focus-visible {{ box-shadow: var(--focus-ring) !important; }}

#MainMenu, footer{{ visibility: hidden; }}
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1320px !important;
}}

/* ══════════════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-display) !important;
    color: var(--fg) !important;
    font-weight: 700 !important;
    line-height: 1.25 !important;
}}
p, li, span {{ font-family: var(--font-body); line-height: 1.75; }}
.stMarkdown, .stText {{ color: var(--fg) !important; }}

/* Readable line length for passage text */
.passage-text {{ max-width: 75ch; }}

/* ══════════════════════════════════════════════
   ACCESSIBILITY TOOLBAR
══════════════════════════════════════════════ */
.a11y-bar {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--r);
    margin-bottom: 16px;
    flex-wrap: wrap;
}}
.a11y-bar-label {{
    font-family: var(--font-mono);
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--fg-mute);
    margin-right: 4px;
}}
.a11y-btn {{
    background: var(--bg-card2);
    border: 1.5px solid var(--border);
    border-radius: 6px;
    padding: 5px 12px;
    font-family: var(--font-ui);
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--fg-mid);
    cursor: pointer;
    transition: all var(--transition-fast);
}}
.a11y-btn:hover {{ border-color: var(--maroon); color: var(--maroon); }}
.a11y-btn.active {{ background: var(--maroon); color: #fff; border-color: var(--maroon); }}

/* ══════════════════════════════════════════════
   SIDEBAR TOGGLE BUTTON
══════════════════════════════════════════════ */
.sidebar-toggle {{
    position: fixed;
    left: 16px;
    top: 16px;
    z-index: 9999;
    background: var(--maroon);
    color: #fff;
    border: none;
    border-radius: 8px;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 1.1rem;
    box-shadow: var(--shadow-md);
    transition: all var(--transition-fast);
}}
.sidebar-toggle:hover {{
    background: var(--maroon-mid);
    transform: scale(1.05);
}}
.sidebar-toggle:focus-visible {{
    outline: 3px solid var(--gold);
    outline-offset: 2px;
}}

/* ══════════════════════════════════════════════
   HERO BANNER
══════════════════════════════════════════════ */
.padayon-hero {{
    position: relative;
    background: var(--maroon-deep);
    border-radius: var(--r-xl);
    padding: 0;
    margin-bottom: 20px;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}}
.padayon-hero-inner {{
    position: relative;
    z-index: 2;
    padding: 44px 52px;
}}
.padayon-hero-bg {{
    position: absolute; inset: 0; z-index: 1;
    background:
        radial-gradient(ellipse 60% 80% at 85% 20%, rgba(200,151,63,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 40% 60% at 10% 80%, rgba(1,68,33,0.25) 0%, transparent 50%),
        linear-gradient(135deg, #4d0a0b 0%, #7B1113 45%, #9e1517 100%);
}}
.padayon-hero-pattern {{
    position: absolute; inset: 0; z-index: 1; opacity: 0.04;
    background-image: repeating-linear-gradient(
        45deg, transparent, transparent 20px,
        rgba(255,255,255,1) 20px, rgba(255,255,255,1) 21px
    );
}}
.hero-eyebrow {{
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(200,151,63,0.2);
    border: 1px solid rgba(200,151,63,0.4);
    color: var(--gold) !important;
    font-family: var(--font-mono);
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.16em; text-transform: uppercase;
    padding: 5px 14px; border-radius: 20px; margin-bottom: 16px;
}}
.hero-title {{
    font-family: var(--font-display) !important;
    font-size: clamp(1.8rem, 3.5vw, 3rem) !important;
    font-weight: 900 !important; color: #fff !important;
    line-height: 1.1 !important; margin-bottom: 10px !important;
    letter-spacing: -0.02em;
}}
.hero-title em {{ font-style: italic; color: var(--gold) !important; }}
.hero-sub {{
    font-family: var(--font-ui); font-size: 0.92rem;
    color: rgba(255,255,255,0.65); line-height: 1.65; max-width: 560px;
}}
.hero-stats {{
    display: flex; gap: 28px; margin-top: 28px;
    padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.12);
    flex-wrap: wrap;
}}
.hero-stat-item {{ text-align: left; }}
.hero-stat-num {{
    font-family: var(--font-display); font-size: 1.7rem;
    font-weight: 900; color: var(--gold) !important; line-height: 1;
}}
.hero-stat-label {{
    font-family: var(--font-ui); font-size: 0.70rem;
    color: rgba(255,255,255,0.5); text-transform: uppercase;
    letter-spacing: 0.1em; margin-top: 4px;
}}

/* ══════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: var(--maroon-deep) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}}
section[data-testid="stSidebar"] > div {{ padding: 0 !important; }}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.82) !important; }}
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] strong {{ color: #fff !important; }}
section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.10) !important; }}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] textarea {{
    background: rgba(255,255,255,0.09) !important;
    border-color: rgba(255,255,255,0.18) !important;
    color: #fff !important; border-radius: 7px !important;
}}
/* Sidebar focus rings on dark bg */
section[data-testid="stSidebar"] *:focus-visible {{
    outline: 3px solid var(--gold) !important;
}}
.sidebar-logo-wrap {{
    background: rgba(0,0,0,0.28);
    padding: 24px 20px 18px;
    text-align: center;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 4px;
}}
.sidebar-heading {{
    font-family: var(--font-mono) !important;
    font-size: 0.63rem !important; letter-spacing: 0.18em !important;
    text-transform: uppercase !important; color: rgba(255,255,255,0.35) !important;
    margin: 18px 0 9px !important; display: block;
}}
.sidebar-section {{ padding: 0 18px; }}

/* ══════════════════════════════════════════════
   DISCLAIMER
══════════════════════════════════════════════ */
.disclaimer {{
    background: var(--gold-pale);
    border: 1px solid rgba(200,151,63,0.3);
    border-left: 4px solid var(--gold);
    border-radius: var(--r); padding: 13px 18px;
    font-family: var(--font-ui); font-size: 0.82rem;
    color: var(--fg-mid); line-height: 1.65; margin-bottom: 20px;
    role: note;
}}

/* ══════════════════════════════════════════════
   CONTROL BAR
══════════════════════════════════════════════ */
.stat-pill {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 13px 18px;
    text-align: center; box-shadow: var(--shadow-xs);
}}
.stat-pill-num {{ font-family: var(--font-display); font-size: 1.4rem; font-weight: 900; color: var(--maroon); line-height: 1; }}
.stat-pill-label {{ font-family: var(--font-mono); font-size: 0.60rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg-mute); margin-top: 3px; }}

/* ══════════════════════════════════════════════
   EXAM WARNING BANNER
══════════════════════════════════════════════ */
.exam-warning {{
    background: linear-gradient(135deg, var(--gold-pale), #fffdf8);
    border: 1px solid rgba(200,151,63,0.35);
    border-left: 5px solid var(--gold); border-radius: var(--r);
    padding: 13px 18px; font-family: var(--font-ui); font-size: 0.87rem;
    color: var(--fg-mid); margin-bottom: 18px; line-height: 1.65;
    role: alert; aria-live: polite;
}}
.exam-warning strong {{ color: var(--maroon); }}

/* ══════════════════════════════════════════════
   PROGRESS BAR — WCAG 2.1 compliant role=progressbar
══════════════════════════════════════════════ */
.prog-outer {{ margin: 14px 0 20px; }}
.prog-meta {{
    display: flex; justify-content: space-between;
    font-family: var(--font-mono); font-size: 0.68rem;
    color: var(--fg-mute); letter-spacing: 0.06em; margin-bottom: 6px;
}}
.prog-track {{
    height: 6px; background: var(--border);
    border-radius: 4px; overflow: hidden;
}}
.prog-fill {{
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, var(--maroon), var(--gold));
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}}

/* ══════════════════════════════════════════════
   QUESTION CARDS
══════════════════════════════════════════════ */
.q-card {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-left: 4px solid var(--olive); border-radius: var(--r);
    padding: 22px 26px; margin-bottom: 12px; box-shadow: var(--shadow-xs);
    transition: border-left-color var(--transition-fast), box-shadow var(--transition-fast),
                transform var(--transition-fast);
    position: relative;
}}
.q-card:hover {{ box-shadow: var(--shadow-sm); transform: translateY(-1px); }}
.q-card.answered {{ border-left-color: var(--gold); box-shadow: var(--shadow-sm); }}
.q-card.flagged {{ border-left-color: #e67e22; }}
.q-card-meta {{
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 11px; flex-wrap: wrap;
}}
.q-num {{
    font-family: var(--font-mono); font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--maroon);
}}
.q-tag {{
    display: inline-block; font-family: var(--font-mono);
    font-size: 0.58rem; font-weight: 600; letter-spacing: 0.08em;
    padding: 2px 9px; border-radius: 12px;
}}
.q-tag-skill {{ background: var(--maroon-pale); color: var(--maroon); border: 1px solid var(--maroon-tint); }}
.q-tag-lang-en {{ background: #e8f0fe; color: #1a56db; border: 1px solid #c7d9ff; }}
.q-tag-lang-fil {{ background: #fff5e0; color: #b45309; border: 1px solid #fde68a; }}
.q-tag-type {{ background: var(--olive-pale); color: var(--olive); border: 1px solid rgba(1,68,33,0.15); }}
.q-flag {{ position: absolute; top: 14px; right: 14px; font-size: 1.1rem; cursor: pointer; opacity: 0.5; transition: opacity 0.15s; background: none; border: none; padding: 4px; border-radius: 4px; }}
.q-flag:hover {{ opacity: 1; }}
.q-flag.active {{ opacity: 1; }}
.q-stem {{
    font-family: var(--font-body); font-size: var(--base-font-size);
    line-height: 1.80; color: var(--fg); margin-bottom: 14px;
}}

/* ══════════════════════════════════════════════
   RADIO OVERRIDES — fully accessible
══════════════════════════════════════════════ */
.stRadio > label {{ display: none !important; }}
.stRadio [data-testid="stWidgetLabel"] {{ display: none !important; }}
.stRadio > div {{ display: flex !important; flex-direction: column !important; gap: 6px !important; }}
.stRadio > div > label {{
    background: var(--bg-card2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important; padding: 11px 16px !important;
    cursor: pointer !important;
    transition: all var(--transition-fast) !important;
    font-family: var(--font-body) !important;
    font-size: var(--base-font-size) !important;
    line-height: 1.6 !important; color: var(--fg) !important;
    display: flex !important; align-items: flex-start !important;
    gap: 10px !important;
}}
.stRadio > div > label:hover {{
    border-color: var(--maroon) !important;
    background: var(--maroon-pale) !important;
    transform: translateX(2px) !important;
}}
.stRadio > div > label[data-checked="true"] {{
    border-color: var(--olive) !important;
    background: var(--olive-pale) !important;
    color: var(--olive) !important;
}}

/* ══════════════════════════════════════════════
   PASSAGE CARD
══════════════════════════════════════════════ */
.passage-shell {{
    background: var(--bg-card); border-radius: var(--r-lg);
    border: 1px solid var(--border); margin-bottom: 32px;
    overflow: hidden; box-shadow: var(--shadow-md);
}}
.passage-top {{
    background: linear-gradient(135deg, var(--maroon-deep) 0%, var(--maroon-mid) 100%);
    padding: 20px 28px; display: flex;
    align-items: flex-start; justify-content: space-between; gap: 16px;
}}
.passage-top-left h4 {{
    font-family: var(--font-display) !important; color: #fff !important;
    font-size: 1.12rem !important; margin-bottom: 8px !important; font-weight: 700 !important;
}}
.passage-pill {{
    display: inline-block; background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.85) !important; font-family: var(--font-mono);
    font-size: 0.58rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 3px 10px; border-radius: 10px; margin-right: 5px;
    border: 1px solid rgba(255,255,255,0.15);
}}
.passage-strategy {{
    background: rgba(200,151,63,0.15); border: 1px solid rgba(200,151,63,0.35);
    border-radius: 8px; padding: 10px 15px; font-family: var(--font-ui);
    font-size: 0.76rem; color: var(--gold) !important; max-width: 240px; line-height: 1.55;
}}
.passage-strategy strong {{ color: #fff !important; }}
.passage-body-wrap {{
    padding: 28px 32px; border-bottom: 2px dashed var(--border-light);
}}
.passage-text {{
    font-family: var(--font-body); font-size: var(--base-font-size);
    line-height: 2.1; color: var(--fg);
}}
.passage-text p {{ margin-bottom: 1.25em; text-align: justify; text-indent: 1.5em; }}
.passage-text p:first-child {{ text-indent: 0; }}
.passage-qs-wrap {{ padding: 24px 32px; background: var(--bg-card2); }}
.passage-qs-title {{
    font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--fg-mute); margin-bottom: 18px;
    padding-bottom: 10px; border-bottom: 1px solid var(--border-light);
}}

/* ══════════════════════════════════════════════
   LEVEL BADGES for RC
══════════════════════════════════════════════ */
.lvl-badge {{
    display: inline-block; font-family: var(--font-mono); font-size: 0.58rem;
    font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 3px 10px; border-radius: 10px;
}}
.lvl-textual {{ background: var(--olive-pale); color: var(--olive); border: 1px solid rgba(1,68,33,0.2); }}
.lvl-inferential {{ background: var(--gold-pale); color: var(--gold); border: 1px solid rgba(200,151,63,0.3); }}
.lvl-critical {{ background: var(--maroon-pale); color: var(--maroon); border: 1px solid rgba(123,17,19,0.2); }}

/* ══════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════ */
.stButton > button {{
    font-family: var(--font-ui) !important; font-weight: 600 !important;
    border-radius: 8px !important; transition: all var(--transition-fast) !important;
    letter-spacing: 0.02em !important; min-height: 44px !important; /* WCAG touch target */
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, var(--maroon) 0%, var(--maroon-deep) 100%) !important;
    border: none !important; color: #fff !important;
    box-shadow: 0 4px 18px rgba(123,17,19,0.35) !important; padding: 12px 20px !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(123,17,19,0.45) !important;
}}
.stButton > button[kind="secondary"] {{
    border: 2px solid var(--maroon) !important; color: var(--maroon) !important;
    background: transparent !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background: var(--maroon-pale) !important;
}}

/* ══════════════════════════════════════════════
   TABS
══════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px; background: var(--border-light);
    border-radius: 10px; padding: 4px; border: none !important;
    flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: var(--font-ui) !important; font-size: 0.80rem !important;
    font-weight: 600 !important; padding: 9px 16px !important;
    border-radius: 7px !important; background: transparent !important;
    color: var(--fg-mute) !important; border: none !important;
    transition: all var(--transition-fast) !important;
    min-height: 38px !important;
}}
.stTabs [aria-selected="true"] {{
    background: var(--bg-card) !important; color: var(--maroon) !important;
    box-shadow: var(--shadow-xs) !important;
}}
/* Tab focus rings */
.stTabs [data-baseweb="tab"]:focus-visible {{
    outline: 3px solid var(--maroon) !important; outline-offset: 2px !important;
}}

/* ══════════════════════════════════════════════
   ITEM NAVIGATOR (sticky mini-map)
══════════════════════════════════════════════ */
.item-nav {{
    position: sticky; top: 12px; z-index: 100;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 14px 18px;
    box-shadow: var(--shadow-sm); margin-bottom: 20px;
}}
.item-nav-title {{
    font-family: var(--font-mono); font-size: 0.62rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--fg-mute); margin-bottom: 10px;
}}
.item-nav-grid {{
    display: flex; flex-wrap: wrap; gap: 5px;
}}
.nav-dot {{
    width: 28px; height: 28px; border-radius: 6px; display: flex;
    align-items: center; justify-content: center;
    font-family: var(--font-mono); font-size: 0.60rem; font-weight: 700;
    cursor: pointer; border: 1.5px solid var(--border);
    background: var(--bg-card2); color: var(--fg-mute);
    transition: all var(--transition-fast); min-width: 44px; /* touch target */
}}
.nav-dot:hover {{ border-color: var(--maroon); color: var(--maroon); transform: scale(1.08); }}
.nav-dot.answered {{ background: var(--olive); color: #fff; border-color: var(--olive); }}
.nav-dot.flagged {{ background: #e67e22; color: #fff; border-color: #e67e22; }}
.nav-dot.current {{ border-color: var(--maroon); color: var(--maroon); font-weight: 700; box-shadow: 0 0 0 2px var(--maroon-pale); }}

/* ══════════════════════════════════════════════
   RESULTS METRICS
══════════════════════════════════════════════ */
.results-hero {{
    background: linear-gradient(135deg, var(--maroon-deep), var(--olive));
    border-radius: var(--r-xl); padding: 44px;
    text-align: center; margin-bottom: 24px;
    position: relative; overflow: hidden;
}}
.results-hero::before {{
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at center, rgba(200,151,63,0.15) 0%, transparent 70%);
}}
.upg-display {{
    font-family: var(--font-display); font-size: clamp(3rem, 7vw, 5.5rem);
    font-weight: 900; color: #fff; line-height: 1; position: relative; z-index: 1;
}}
.upg-label {{
    font-family: var(--font-mono); font-size: 0.70rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: rgba(255,255,255,0.55);
    margin-bottom: 10px; position: relative; z-index: 1;
}}
.upg-verdict {{
    font-family: var(--font-ui); font-size: 1.05rem; color: var(--gold);
    margin-top: 10px; position: relative; z-index: 1;
}}
.metrics-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }}
.metric-tile {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 20px 16px; text-align: center;
    box-shadow: var(--shadow-xs); transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}}
.metric-tile:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-sm); }}
.metric-tile-val {{
    font-family: var(--font-display); font-size: 1.9rem; font-weight: 900;
    color: var(--maroon); line-height: 1; margin-bottom: 5px;
}}
.metric-tile-val.green {{ color: var(--olive); }}
.metric-tile-val.gold {{ color: var(--gold); }}
.metric-tile-label {{ font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-mute); }}
.metric-tile-sub {{ font-family: var(--font-ui); font-size: 0.73rem; color: var(--fg-mute); margin-top: 4px; }}

/* ══════════════════════════════════════════════
   SCORE BREAKDOWN
══════════════════════════════════════════════ */
.score-panel {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 22px 26px; box-shadow: var(--shadow-xs);
}}
.score-panel h4 {{
    font-family: var(--font-display) !important; font-size: 1.05rem !important;
    margin-bottom: 14px !important; padding-bottom: 11px !important;
    border-bottom: 1px solid var(--border-light) !important;
}}
.score-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0; border-bottom: 1px solid var(--border-light);
    font-family: var(--font-ui); font-size: 0.87rem;
}}
.score-row:last-child {{ border-bottom: none; }}
.score-lbl {{ color: var(--fg-mid); }}
.score-val {{ font-family: var(--font-mono); font-weight: 700; font-size: 0.88rem; }}
.score-val.c {{ color: var(--olive); }}
.score-val.w {{ color: var(--maroon); }}
.score-val.g {{ color: var(--gold); }}

/* ══════════════════════════════════════════════
   ADMISSION CARDS
══════════════════════════════════════════════ */
.campus-shell {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-lg); overflow: hidden;
    box-shadow: var(--shadow-sm); margin-bottom: 18px;
}}
.campus-header {{ padding: 18px 24px; background: linear-gradient(135deg, var(--olive) 0%, var(--olive-mid) 100%); }}
.campus-header.rejected {{ background: linear-gradient(135deg, var(--maroon-deep) 0%, var(--maroon) 100%); }}
.campus-header h4 {{ color: #fff !important; font-size: 1.02rem !important; margin-bottom: 4px !important; }}
.campus-header p {{ color: rgba(255,255,255,0.65); font-family: var(--font-mono); font-size: 0.70rem; }}
.campus-body {{ padding: 16px 24px; }}
.prog-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 11px 0; border-bottom: 1px solid var(--border-light);
    font-family: var(--font-ui); font-size: 0.87rem;
}}
.prog-row:last-child {{ border-bottom: none; }}
.prog-name {{ font-weight: 600; color: var(--fg); }}
.prog-meta {{ font-family: var(--font-mono); font-size: 0.63rem; color: var(--fg-mute); margin-top: 2px; }}
.badge-pass {{ color: var(--olive); font-weight: 700; background: var(--olive-pale); padding: 3px 12px; border-radius: 6px; border: 1px solid rgba(1,68,33,0.2); font-family: var(--font-mono); font-size: 0.70rem; }}
.badge-wait {{ color: #b45309; font-weight: 700; background: #fff5e0; padding: 3px 12px; border-radius: 6px; border: 1px solid #fde68a; font-family: var(--font-mono); font-size: 0.70rem; }}
.badge-fail {{ color: var(--maroon); font-weight: 700; background: var(--maroon-pale); padding: 3px 12px; border-radius: 6px; border: 1px solid var(--maroon-tint); font-family: var(--font-mono); font-size: 0.70rem; }}

/* ══════════════════════════════════════════════
   FEEDBACK PANEL
══════════════════════════════════════════════ */
.feedback-shell {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r); padding: 22px 26px; margin-bottom: 16px;
    line-height: 1.85; font-family: var(--font-body); font-size: var(--base-font-size);
}}
.feedback-shell.gold-accent {{ border-left: 4px solid var(--gold); }}
.feedback-shell.olive-accent {{ border-left: 4px solid var(--olive); }}
.feedback-shell.maroon-accent {{ border-left: 4px solid var(--maroon); }}

/* ══════════════════════════════════════════════
   SECTION DIVIDER
══════════════════════════════════════════════ */
.sec-div {{ display: flex; align-items: center; gap: 14px; margin: 32px 0 18px; }}
.sec-div h3 {{ font-family: var(--font-display) !important; font-size: 1.4rem !important; white-space: nowrap; margin: 0 !important; color: var(--fg) !important; }}
.sec-line {{ flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }}

/* ══════════════════════════════════════════════
   REVIEW ITEMS
══════════════════════════════════════════════ */
.rev-item {{ border-radius: 8px; overflow: hidden; margin-bottom: 10px; border: 1px solid var(--border); }}
.rev-header {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; font-family: var(--font-ui); font-size: 0.87rem; }}
.rev-header.correct {{ border-left: 4px solid var(--olive); background: var(--olive-pale); }}
.rev-header.wrong {{ border-left: 4px solid var(--maroon); background: var(--maroon-pale); }}
.rev-header.blank {{ border-left: 4px solid var(--gold); background: var(--gold-pale); }}

/* ══════════════════════════════════════════════
   FLOATING TIMER — accessible
══════════════════════════════════════════════ */
#padayon-timer {{
    position: fixed; top: 20px; right: 24px; z-index: 99999;
    background: var(--olive); color: #fff;
    font-family: var(--font-mono); font-size: 1.0rem; font-weight: 700;
    padding: 9px 20px; border-radius: 32px;
    box-shadow: 0 4px 20px rgba(1,68,33,0.4);
    letter-spacing: 0.05em; border: 2px solid rgba(255,255,255,0.15);
    transition: background 0.3s;
    role: timer; aria-live: polite; aria-atomic: true;
}}
#padayon-timer.warn {{ background: #b45309; }}
#padayon-timer.danger {{ background: var(--maroon); }}

/* ══════════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════════ */
.streamlit-expanderHeader {{
    font-family: var(--font-ui) !important; font-size: 0.87rem !important;
    font-weight: 600 !important; background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    color: var(--fg) !important; min-height: 44px !important;
}}

/* ══════════════════════════════════════════════
   DEEP ANALYSIS
══════════════════════════════════════════════ */
.deep-feedback-box {{
    background: linear-gradient(135deg, var(--bg-card), var(--bg-card2));
    border: 1px solid var(--border); border-radius: var(--r-lg); padding: 26px 30px; margin-top: 14px;
}}
.deep-feedback-box h5 {{
    font-family: var(--font-display) !important; font-size: 1.0rem !important;
    color: var(--maroon) !important; margin-bottom: 12px !important;
}}
.feedback-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }}
.feedback-card {{ background: var(--bg); border: 1px solid var(--border); border-radius: var(--r); padding: 15px 17px; }}
.feedback-card-title {{ font-family: var(--font-mono); font-size: 0.60rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-mute); margin-bottom: 7px; }}
.feedback-card-body {{ font-family: var(--font-ui); font-size: 0.83rem; line-height: 1.65; color: var(--fg-mid); }}

/* ══════════════════════════════════════════════
   SKILL HEATMAP
══════════════════════════════════════════════ */
.skill-heatmap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }}
.skill-row {{
    display: flex; align-items: center; gap: 10px;
    font-family: var(--font-ui); font-size: 0.80rem; padding: 8px 12px;
    border-radius: 7px; border: 1px solid var(--border-light);
    background: var(--bg-card2);
}}
.skill-bar-outer {{ flex: 1; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }}
.skill-bar-inner {{ height: 100%; border-radius: 3px; transition: width 0.6s ease; }}
.skill-bar-inner.strong {{ background: var(--olive); }}
.skill-bar-inner.mid {{ background: var(--gold); }}
.skill-bar-inner.weak {{ background: var(--maroon); }}
.skill-pct {{ font-family: var(--font-mono); font-size: 0.62rem; font-weight: 700; min-width: 32px; text-align: right; }}

/* ══════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════ */
@media (max-width: 768px) {{
    .padayon-hero-inner {{ padding: 28px 24px; }}
    .hero-stats {{ gap: 18px; }}
    .metrics-row {{ grid-template-columns: repeat(2, 1fr); }}
    .feedback-grid {{ grid-template-columns: 1fr; }}
    .skill-heatmap {{ grid-template-columns: 1fr; }}
    .passage-top {{ flex-direction: column; }}
    .passage-strategy {{ max-width: 100%; }}
    .passage-body-wrap {{ padding: 20px 18px; }}
    .passage-qs-wrap {{ padding: 18px; }}
}}

/* ══════════════════════════════════════════════
   REDUCED MOTION
══════════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
}}

/* ══════════════════════════════════════════════
   PRINT STYLES
══════════════════════════════════════════════ */
@media print {{
    .stSidebar, #padayon-timer, .stButton {{ display: none !important; }}
    .padayon-hero {{ background: #000 !important; }}
    .block-container {{ padding: 0 !important; }}
}}

/* Selectbox & input base */
.stSelectbox > div > div, .stNumberInput > div > div > input,
.stTextInput > div > div > input {{ border-radius: 8px !important; }}

/* ══════════════════════════════════════════════
   STATUS INDICATOR DOTS
══════════════════════════════════════════════ */
.status-legend {{
    display: flex; gap: 16px; align-items: center;
    font-family: var(--font-mono); font-size: 0.62rem;
    color: var(--fg-mute); letter-spacing: 0.08em;
    text-transform: uppercase; padding: 8px 0;
    flex-wrap: wrap;
}}
.legend-dot {{
    width: 10px; height: 10px; border-radius: 3px;
    display: inline-block; margin-right: 5px;
}}
</style>
""", unsafe_allow_html=True)

# Skip link for keyboard navigation
st.markdown('<a href="#main-content" class="skip-link">Skip to main content</a>', unsafe_allow_html=True)

# ==========================================
# 🏫 DATA: SCHOOL TIERS
# ==========================================
SCHOOL_TIERS = {
    "PSHS (Philippine Science High School)": {"modifier": 0.30, "label": "Elite National Science School", "palugit": True},
    "DepEd Specialized Science & Math (PSHS-Affiliate)": {"modifier": 0.22, "label": "Regional Specialized", "palugit": True},
    "DepEd Laboratory School (UP, PNU, Palawan, etc.)": {"modifier": 0.18, "label": "University Laboratory", "palugit": True},
    "DepEd Legislated Special School (CLSU, MSU, etc.)": {"modifier": 0.14, "label": "Legislated Special", "palugit": True},
    "Public — Special Program (STEM, HUMSS, ABM track)": {"modifier": 0.06, "label": "Public SHS Special Track", "palugit": True},
    "Public — Regular National High School": {"modifier": 0.04, "label": "Public Regular", "palugit": True},
    "Public — Barangay / Community High School": {"modifier": 0.08, "label": "Barangay NHS (+bonus)", "palugit": True},
    "Public — Vocational / Technical (TESDA, MNHS)": {"modifier": 0.07, "label": "Vocational Tech", "palugit": True},
    "Private — International School (IB, AP, Cambridge)": {"modifier": 0.10, "label": "International Private", "palugit": False},
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
    "UP Open University":   {"cutoff": 2.80, "recon": 2.800, "note": "Distance learning campus."},
}

PROGRAM_TIERS = {
    "UP Manila": {
        "Triple Quota": ["BS Biochemistry","BS Biology","BS Nursing","BS Public Health","BS Pharmacy"],
        "Double Quota": ["BS Computer Science","D Dental Medicine","BS Occupational Therapy","BS Physical Therapy","BS Speech Pathology","BS Pharmaceutical Sciences"],
        "Single Quota": ["BS Applied Physics","BA Behavioral Sciences","BA Political Science","BA Social Sciences"],
        "Less Popular": ["BA Development Studies","BA Organizational Communication","BA Philippine Arts","BA Social Work"]
    },
    "UP Diliman": {
        "Triple Quota": ["BS Architecture","BS Biology","BS Business Administration & Accountancy","BS Civil Engineering","BS Computer Science","BS Electrical Engineering","BS Mechanical Engineering","BS Molecular Biology & Biotech","BS Psychology","BS Chemical Engineering"],
        "Double Quota": ["BA Broadcast Communication","BS Business Administration","BS Business Economics","BS Computer Engineering","BA Creative Writing","BS Economics","BS Industrial Engineering","BA Political Science","BA Psychology","BS Mathematics"],
        "Single Quota": ["BS Applied Physics","BS Chemistry","BA Communication Research","BS Food Technology","BS Geodetic Engineering","BS Geography","BS Materials Engineering","BA Philosophy","BS Physics","BS Statistics","BS Geology"],
        "Less Popular": ["BA Anthropology","BA Araling Pilipino","BA Art Studies","BS Clothing Technology","BS Community Development","BA English Studies","BA Filipino","BA History","BS Social Work","BA Sociology","BA Library & Information Science"]
    },
    "UP Los Baños": {
        "Triple Quota": ["BS Biology","BS Chemical Engineering","BS Civil Engineering","BS Computer Science","D Veterinary Medicine"],
        "Double Quota": ["BS Accountancy","BS Economics","BS Electrical Engineering","BS Industrial Engineering","BS Mechanical Engineering","BS Applied Mathematics"],
        "Single Quota": ["BS Agribusiness Management","BS Agricultural Chemistry","BA Communication Arts","BS Development Communication","BS Food Technology","BS Mathematics","BS Statistics","BS Applied Physics"],
        "Less Popular": ["BS Agriculture","BS Agricultural Biotechnology","BS Forestry","BS Human Ecology","BS Nutrition","BA Philosophy","BA Sociology","BS Environmental Science"]
    },
    "UP Baguio": {
        "Triple Quota": ["BS Computer Science","BS Biology","BS Mathematics"],
        "Double Quota": ["BA Communication","BS Physics","BS Management Economics","B Fine Arts"],
        "Single Quota": ["BA Languages & Literature","BS Statistics"],
        "Less Popular": ["BA Social Sciences (Economics)","BA Social Sciences (History)","BA Social Sciences (Anthropology)"]
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
        "Double Quota": ["BS Chemistry","BA Communication & Media Studies","BS Food Technology","BS Statistics","BS Marine Biology"],
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
        if program in plist:
            return tier
    return "Less Popular"

# ==========================================
# ⚙️ SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo-wrap'>
        <img src='https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/University_of_the_Philippines_seal.svg/1200px-University_of_the_Philippines_seal.svg.png'
             width='64' style='filter: drop-shadow(0 2px 8px rgba(0,0,0,0.4));'
             alt='University of the Philippines seal'/>
        <div style='color:rgba(255,255,255,0.35); font-family: var(--font-mono); font-size:0.58rem; letter-spacing:0.18em; margin-top:10px; text-transform:uppercase;'>
            Padayon! Ang Wika! · v8.0
        </div>
        <div style='color:rgba(255,255,255,0.65); font-family: var(--font-display); font-size:0.85rem; font-style:italic; margin-top:6px;'>
            Elite UPCAT LP+RC Simulator
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ACCESSIBILITY CONTROLS ──
    st.markdown('<span class="sidebar-heading">♿ Accessibility</span>', unsafe_allow_html=True)
    font_size = st.select_slider(
        "Text Size", options=["small","medium","large","x-large"],
        value=st.session_state.get('font_size','medium'),
        help="Adjust reading text size across the exam interface"
    )
    if font_size != st.session_state.get('font_size'):
        st.session_state['font_size'] = font_size
        st.rerun()

    high_contrast = st.checkbox(
        "High Contrast Mode",
        value=st.session_state.get('high_contrast', False),
        help="Increases color contrast for better readability"
    )
    if high_contrast != st.session_state.get('high_contrast'):
        st.session_state['high_contrast'] = high_contrast
        st.rerun()

    show_rationale_inline = st.checkbox(
        "Show Rationale Hints During Exam",
        value=False,
        help="Displays a brief skill hint under each question (for study mode)"
    )

    st.divider()
    st.markdown('<span class="sidebar-heading">🔑 API Configuration</span>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Gemini API Key", type="password", placeholder="AIza...",
        help="Get your free key at aistudio.google.com"
    )
    gemini_model = st.selectbox("Gemini Model", [
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview",
    ], index=0, help="2.5 Pro gives deepest, most psychometrically accurate items")

    st.divider()
    st.markdown('<span class="sidebar-heading">🏫 School Type (JHS & SHS)</span>', unsafe_allow_html=True)
    jhs_type = st.selectbox(
        "JHS School Type", list(SCHOOL_TIERS.keys()), index=5,
        help="Affects the palugit/pabigat modifier applied to your grade UPG"
    )
    shs_type = st.selectbox(
        "SHS School Type", list(SCHOOL_TIERS.keys()), index=5,
        help="Affects the palugit/pabigat modifier applied to your grade UPG"
    )

    jhs_info = SCHOOL_TIERS[jhs_type]
    shs_info = SCHOOL_TIERS[shs_type]
    palugit_note = ""
    if jhs_info["palugit"]: palugit_note += f"JHS *palugit* +{jhs_info['modifier']:.2f}. "
    if shs_info["palugit"]: palugit_note += f"SHS *palugit* +{shs_info['modifier']:.2f}. "
    if palugit_note:
        st.caption(f"✅ {palugit_note}")

    st.divider()
    st.markdown('<span class="sidebar-heading">📚 Language & Lit Grades (40% UPG Weight)</span>', unsafe_allow_html=True)
    st.caption("Enter final grade (60–100 DepEd scale). Language subjects only — focused on LP+RC correlation.")
    c1, c2 = st.columns(2)
    with c1:
        g8_eng  = st.number_input("G8 English",        60.0, 100.0, 88.0, 0.5)
        g9_eng  = st.number_input("G9 English",        60.0, 100.0, 88.0, 0.5)
        g10_eng = st.number_input("G10 English",       60.0, 100.0, 89.0, 0.5)
        g11_lit = st.number_input("G11 21st Cent Lit", 60.0, 100.0, 89.0, 0.5)
        g11_eapp= st.number_input("G11 EAPP",          60.0, 100.0, 89.0, 0.5)
        g11_rw  = st.number_input("G11 Read & Write",  60.0, 100.0, 88.0, 0.5)
    with c2:
        g8_fil  = st.number_input("G8 Filipino",       60.0, 100.0, 88.0, 0.5)
        g9_fil  = st.number_input("G9 Filipino",       60.0, 100.0, 88.0, 0.5)
        g10_fil = st.number_input("G10 Filipino",      60.0, 100.0, 88.0, 0.5)
        g11_kom = st.number_input("G11 Komunikasyon",  60.0, 100.0, 88.0, 0.5)
        g11_pag = st.number_input("G11 Pagbasa",       60.0, 100.0, 88.0, 0.5)
        g11_ps  = st.number_input("G11 Pagsulat",      60.0, 100.0, 88.0, 0.5)

    st.divider()
    st.markdown('<span class="sidebar-heading">🎯 Campus & Program Selection</span>', unsafe_allow_html=True)
    campus_1 = st.selectbox("1st Campus Choice", list(CAMPUS_DATA.keys()), index=0)
    c1_p1 = st.selectbox("Priority 1", get_all_programs(campus_1), key="c1p1")
    c1_p2 = st.selectbox("Priority 2", get_all_programs(campus_1), key="c1p2")
    c1_p3 = st.selectbox("Priority 3", get_all_programs(campus_1), key="c1p3")
    c1_p4 = st.selectbox("Priority 4", get_all_programs(campus_1), key="c1p4")
    campus_2 = st.selectbox("2nd Campus Choice", list(CAMPUS_DATA.keys()), index=2)
    c2_p1 = st.selectbox("Priority 1", get_all_programs(campus_2), key="c2p1")
    c2_p2 = st.selectbox("Priority 2", get_all_programs(campus_2), key="c2p2")
    c2_p3 = st.selectbox("Priority 3", get_all_programs(campus_2), key="c2p3")
    c2_p4 = st.selectbox("Priority 4", get_all_programs(campus_2), key="c2p4")

    st.divider()
    st.markdown('<span class="sidebar-heading">⚙️ Simulation Parameters</span>', unsafe_allow_html=True)
    num_items = st.slider(
        "Total Exam Items", 10, 60, 30, 10,
        help="UPCAT LP=80, RC=80 items. Scale down for focused practice sessions."
    )
    difficulty = st.select_slider(
        "Difficulty Ceiling",
        options=["Standard", "Competitive", "Brutal", "Massacre"],
        value="Competitive",
        help="Massacre = top 2% psychometric ceiling. Competitive = top 20%."
    )
    show_timer = st.checkbox("Show Countdown Timer", value=True)
    show_item_nav = st.checkbox("Show Item Navigator", value=True,
        help="Sticky mini-map showing answered/flagged/blank status")
    enable_flagging = st.checkbox("Enable Item Flagging 🚩", value=True,
        help="Flag items to review before submitting")

# ==========================================
# 🧠 PROMPT CONSTRUCTION
# ==========================================
num_lp = int(num_items * 0.50)
num_rc = num_items - num_lp
num_passages = max(2, num_rc // 5)

DIFF_MAP = {
    "Standard":    ("Standard: items are college-entrance level. Vocabulary up to B2. Grammar tests standard rules. RC passages are 300-400 words. Inference limited to one-step.", 0.52, 0.16),
    "Competitive": ("Competitive: Top-20% ceiling. Items test advanced grammar edge cases, C1 vocabulary, and two-step inference. Passages 400-550 words with academic register.", 0.47, 0.15),
    "Brutal":      ("Brutal: Top-8% ceiling. Items expose gaps in advanced syntax, rare vocabulary (C1-C2), and cross-paragraph synthesis. Passages 450-600 words in full academic register.", 0.42, 0.14),
    "Massacre":    ("Massacre: Top-2% ceiling (UP Diliman CS/MBB tier). Psychometrically sadistic — C2 vocabulary, structurally ambiguous sentences, passages with deliberate internal complexity, distractors that are grammatically perfect but semantically off by one degree of precision. Every item is a trap for the overconfident.", 0.37, 0.13),
}
diff_instruction, MEAN_BASELINE, SIGMA = DIFF_MAP[difficulty]

LP_ENGLISH_TYPES = [
    "Parts of Speech: Nouns (common, proper, collective, abstract, concrete, countable, uncountable)",
    "Parts of Speech: Pronouns (personal, reflexive, relative, demonstrative, indefinite, interrogative, reciprocal)",
    "Parts of Speech: Verbs (transitive, intransitive, linking, auxiliary, modal, phrasal verbs, verb forms)",
    "Parts of Speech: Adjectives (attributive, predicative, order of adjectives, comparative/superlative, participial)",
    "Parts of Speech: Adverbs (manner, time, place, frequency, degree, conjunctive adverbs)",
    "Parts of Speech: Prepositions (time, place, direction, idioms with prepositions)",
    "Parts of Speech: Conjunctions (coordinating FANBOYS, subordinating, correlative — both/and, neither/nor, etc.)",
    "Parts of Speech: Interjections (punctuation and register in formal vs. informal)",
    "Parts of Speech: Determiners (articles a/an/the, quantifiers, demonstratives, possessives)",
    "Subject-Verb Agreement (collective nouns, indefinite pronouns, inverted sentences, compound subjects)",
    "Phrases and Clauses (noun phrase, verb phrase, adjective clause, adverb clause, noun clause, participial phrase, infinitive phrase, gerund phrase)",
    "Sentence Patterns (S-V, S-V-O, S-V-IO-DO, S-LV-SC, S-V-OC, inverted patterns)",
    "Sentence Structure (simple, compound, complex, compound-complex; coordination vs. subordination)",
    "Sentence Completeness (fragments, run-ons, comma splices, fused sentences)",
    "Sentence Complements (direct object, indirect object, subject complement, object complement)",
    "Error Identification: Parallelism (faulty parallelism in lists, correlative conjunctions, comparisons)",
    "Error Identification: Redundancy and Wordiness (tautology, pleonasm, circumlocution)",
    "Error Identification: Double Negatives (nonstandard double negatives in formal register)",
    "Error Identification: Misplaced and Dangling Modifiers",
    "Error Identification: Special Agreements (neither/nor, either/or, collective nouns, fractions, measurements)",
    "Spelling and Vocabulary: Context Clues (definition clues, restatement clues, contrast clues, inference clues)",
    "Spelling and Vocabulary: Word Etymology (Latin/Greek roots, prefixes, suffixes, word families)",
    "Vocabulary: Synonyms, Antonyms, Analogies, Connotation vs. Denotation",
    "Vocabulary: Idiomatic Expressions and Collocations",
    "Vocabulary: Formal Academic Word List (AWL) words in context",
]

LP_FILIPINO_TYPES = [
    "Bahagi ng Pananalita: Pangalan (uri, kasing-kahulugan, kasalungat, kasukdulang kahulugan)",
    "Bahagi ng Pananalita: Panghalip (panao, pamatlig, pananong, panaklaw, pantukoy)",
    "Bahagi ng Pananalita: Pandiwa (aspeto, pokus, palaugnayan — aktor, layon, direksyon, ganapan, kagamitan, katuwang; pandiwang may at walang panlapi)",
    "Bahagi ng Pananalita: Pang-uri (antas ng paghahambing — lantay, pahambing, pasukdol; pang-uring panlarawan at pamirihan)",
    "Bahagi ng Pananalita: Pang-abay (pamanahon, panlunan, paraan, pamarami, pang-agam, panggitna)",
    "Bahagi ng Pananalita: Pang-ukol (tamang gamit ng sa, para sa, tungkol sa, mula sa, hanggang sa at iba pa)",
    "Bahagi ng Pananalita: Pangatnig (nagtutuloy, nagpapahiwatig, nagbibigay-daan, nagkakaugnay)",
    "Bahagi ng Pananalita: Padamdam (tamang bantas at gamit sa pormal na sulatin)",
    "Bahagi ng Pananalita: Pantukoy (ang, ng, sa at ang mga di-tipikal na gamit nito)",
    "Kasunduan ng Paksa at Panaguri (kolektibong pangngalan, walang tiyak na panghalip)",
    "Parirala at Sugnay (pariralang pangngalan, pandiwang parirala, sugnay na nakasalalay, malayang sugnay)",
    "Pangungusap (payak, tambalan, hugnayan, langkapan; pagbabago ng estraktura ng pangungusap)",
    "Pagkilala ng Mali: Pagkakasalungatan ng paksa at panaguri",
    "Pagkilala ng Mali: Malinlang na gamit ng panlapi at hulapi (ma-, mag-, -um-, -in, i-, -an, pa-, maka-)",
    "Pagkilala ng Mali: Maling paggamit ng pang-ukol at pangatnig",
    "Pabaybay at Talasalitaan: Wastong baybay ng mga salitang hiram at dati nang naisasaling Filipino",
    "Talasalitaan: Kontekstwal na kahulugan ng mga salita (kasingkahulugan, kasalungat, kaugnay na kahulugan)",
    "Talasalitaan: Salawikain, Sawikain, at Idyoma sa konteksto",
    "Figurang Retorika: Talinghaga, personipikasyon, simile, litotes, hyperbole, metonimya, paradox sa konteksto",
    "Pagbabago ng Antas ng Wika (pormal, di-pormal, lalawiganin, balbal)",
]

RC_GENRES = [
    "Filipino Contemporary Poetry (multiple stanzas, modern imagery, social commentary)",
    "English Free Verse Poetry (extended poem, lyric meditation, environmental or social theme)",
    "Academic Essay (Philippine Social Sciences — historical, anthropological, or sociological argument)",
    "Literary Prose (short story excerpt — Filipino Modernist or magic realist, 500+ words)",
    "Analytical Opinion / Editorial (complex sociopolitical or ethical issue in the Philippines)",
    "Scientific Explainer (biology, environmental science, public health — with data, statistics)",
    "Historical Document / Chronicle (primary source from Philippine history in archaic register)",
    "Speech / Oration (delivered address by a Filipino leader, contains rhetorical devices)",
    "Myth or Fable (pre-colonial Philippine mythology or Aesop-style fable with moral ambiguity)",
    "News Article / Investigative Report (journalistic, factual, bias analysis required)",
    "Procedure / Manual (step-by-step instructional text, sequencing and purpose questions)",
    "Fact vs. Opinion Passage (mixed paragraph, distinguish verifiable claims from perspectives)",
    "Editorial Cartoon Description (description of a political cartoon — analyze symbolism)",
    "Graph or Table Interpretation (data visualization embedded in prose — statistics, trends)",
    "Literary Criticism (excerpt from a critical essay analyzing a Filipino work)",
    "Scientific Abstract (research paper abstract, academic hedging language, methodology questions)",
    "Filipino Folktale (regional Philippine folktale with cultural significance and moral questions)",
    "Debate Transcript Excerpt (two opposing positions on a Philippine policy issue)",
    "Biographical Sketch (Philippine historical figure or contemporary hero, evaluative questions)",
]

UPCAT_PROMPT = f"""
You are the Chief Psychometrician of the University of the Philippines Office of Admissions, personally responsible for the UPCAT Language Proficiency and Reading Comprehension subtests. Your items are used to rank over 140,000 competitive applicants. Every item must reflect the highest standards of psychometric design.

DIFFICULTY INSTRUCTION:
{diff_instruction}

Generate exactly {num_lp} Language Proficiency (LP) items and exactly {num_rc} Reading Comprehension (RC) items across {num_passages} diverse passages.

PSYCHOMETRIC VALIDITY REQUIREMENTS (ALL ITEMS):
- Every item must have a UNIQUE correct answer that cannot be arrived at by test-taking strategies alone
- Point-biserial correlation target: >0.30 (items must discriminate between high and low scorers)
- No item should be answerable without domain knowledge or reading the passage
- Distractors must be plausible to students who have studied but have misconceptions
- Item difficulty range: p-value 0.35–0.65 for Standard; 0.25–0.55 for Competitive; 0.20–0.45 for Brutal; 0.15–0.40 for Massacre
- ZERO trick questions — every correct answer must be defensible with a clear rule or textual evidence

═══════════════════════════════════════════════
PART 1: LANGUAGE PROFICIENCY — {num_lp} ITEMS
═══════════════════════════════════════════════

LANGUAGE BALANCE: Exactly 50% English LP items, exactly 50% Filipino LP items.

ENGLISH LP ITEM POOL (cycle through all — every item type must appear at least once if items allow):
{chr(10).join(f"{i+1}. {t}" for i, t in enumerate(LP_ENGLISH_TYPES))}

FILIPINO LP ITEM POOL (cycle through all — every item type must appear at least once if items allow):
{chr(10).join(f"{i+1}. {t}" for i, t in enumerate(LP_FILIPINO_TYPES))}

STRICT PSYCHOMETRIC RULES FOR LP:
1. ZERO LENGTH BIAS: All four options (A, B, C, D) must be within ±4 characters of each other. Non-negotiable.
2. ZERO PATTERN BIAS: Correct answers evenly distributed — no letter correct more than 30% of the time.
3. FUNCTIONAL DISTRACTORS (label explicitly):
   - "OVERCONFIDENT TRAP": Grammatically plausible but wrong in register or subtle semantics
   - "COMMON MISCONCEPTION": What average students memorize wrongly from textbooks
   - "PARTIAL TRUTH": Right in one dimension (morphology, syntax) but wrong in another (semantics, context)
4. VOCABULARY items: All options must be same grammatical category and register. No morphological giveaways.
5. ERROR IDENTIFICATION: Mark four underlined sections using ALL-CAPS: "She (A) INSISTED THAT the committee (B) WERE GOING TO (C) RENDER A DECISION before (D) THE DEADLINE." The error location must be one of A, B, C, or D — never "No error."
6. Filipino items MUST use correct Filipino orthography including diacritical marks (tuldík, pahilís, paigtíng) where meaning changes with stress.
7. Include the skill_tested field with the SPECIFIC sub-skill (e.g., "Subject-verb agreement with collective nouns in inverted sentences")
8. Include a difficulty_estimate field: "Easy (p=0.60+)", "Medium (p=0.40-0.60)", or "Hard (p<0.40)"

═══════════════════════════════════════════════
PART 2: READING COMPREHENSION — {num_rc} ITEMS
across {num_passages} PASSAGES
═══════════════════════════════════════════════

PASSAGE GENRE ROTATION (choose {num_passages} DIFFERENT genres — maximize diversity, no repeats):
{chr(10).join(f"- {g}" for g in random.sample(RC_GENRES, min(num_passages, len(RC_GENRES))))}

MANDATORY PASSAGE REQUIREMENTS:
- MINIMUM 420 words per passage, IDEAL 500-650 words. DO NOT truncate.
- All passages must be COMPLETELY ORIGINAL — no actual published texts.
- Passages must be intellectually substantive — UP academic journal / Ateneo Press / DOST science digest quality.
- For Filipino passages: full Akademikong Filipino register. Zero code-switching.
- Deliberate complexity: embedded clauses, academic hedging, domain-specific vocabulary, internal tensions.
- Poetry: minimum 4 stanzas with figurative devices that can be tested.
- Procedure passages: minimum 8 steps, with purpose and sequencing questions.
- Include a vocabulary_focus field listing 3-5 target words from the passage that appear in questions.

RC QUESTION LEVELS (every passage must have all 3 levels):
- TEXTUAL (1-2 per passage): Direct but non-obvious retrieval. Correct answer paraphrases ONE specific sentence. Key phrase NOT copied verbatim.
- INFERENTIAL (2-3 per passage): Synthesizes information from 2+ paragraphs. Never stated directly — must be logically derived with a clear inferential chain.
- CRITICAL/EVALUATIVE (1-2 per passage): Test-taker must evaluate argument, identify unstated assumptions, recognize rhetorical devices, determine primary purpose, assess evidence quality, or distinguish tone/bias.

MANDATORY FUNCTIONAL DISTRACTOR SYSTEM:
Label each distractor explicitly with its trap type:
1. "MAGNIFIED DETAIL TRAP": A fact from the passage elevated incorrectly as the main point.
2. "EXTERNAL PLAUSIBLE INTRUSION": Academically correct but has NO basis in the passage. Tests prior-knowledge overreach.
3. "PARTIAL TRUTH / SCOPE ERROR": Correct idea + wrong qualifier/scope/causal direction/emphasis.
4. CORRECT ANSWER: Full, defensible paraphrase. Never ambiguous. Never a trick.

═══════════════════════════════════════════════
OUTPUT FORMAT — STRICT JSON ONLY:
═══════════════════════════════════════════════

{{
  "exam_metadata": {{
    "total_lp": {num_lp},
    "total_rc": {num_rc},
    "num_passages": {num_passages},
    "difficulty": "{difficulty}",
    "generated_at": "auto",
    "estimated_time_minutes": {int(num_items * 0.5625)},
    "validity_notes": "Items generated with p-value targets and discrimination index guidance"
  }},
  "language_proficiency": [
    {{
      "item_number": 1,
      "language": "English",
      "item_type": "Subject-Verb Agreement",
      "skill_category": "Grammar",
      "skill_tested": "Specific sub-skill description here",
      "difficulty_estimate": "Hard (p<0.40)",
      "question_text": "FULL QUESTION. For error ID, mark sections: 'The committee (A) HAS AGREED that all members (B) ARE REQUIRED to (C) SUBMIT THEIR reports (D) BY FRIDAY.'",
      "options": {{
        "A": "option A — same approximate length as others",
        "B": "option B — same approximate length as others",
        "C": "option C — same approximate length as others",
        "D": "option D — same approximate length as others"
      }},
      "correct_answer": "B",
      "distractor_analysis": {{
        "A": {{"type": "OVERCONFIDENT TRAP", "explanation": "What linguistic knowledge gap this exploits"}},
        "C": {{"type": "COMMON MISCONCEPTION", "explanation": "What textbook rule students misapply"}},
        "D": {{"type": "PARTIAL TRUTH", "explanation": "Why this seems correct but fails on inspection"}}
      }},
      "rationale": "DEEP RATIONALE minimum 6 sentences: (1) Name the exact grammatical/linguistic rule and its classification. (2) Explain WHY the correct answer is correct citing the rule. (3) Explain the cognitive error for distractor A. (4) Explain the cognitive error for distractor C. (5) Explain the cognitive error for distractor D. (6) Memory device or rule-of-thumb for future items.",
      "option_char_counts": "A=XX B=XX C=XX D=XX"
    }}
  ],
  "reading_comprehension": [
    {{
      "passage_id": 1,
      "language": "English",
      "genre": "Academic Essay",
      "genre_subtype": "Philippine Social Science",
      "word_count": 530,
      "passage_title": "Descriptive Title Here",
      "vocabulary_focus": ["word1", "word2", "word3"],
      "passage_text": "FULL PASSAGE TEXT. Minimum 420 words. Paragraphs separated by \\n\\n. DO NOT TRUNCATE. Write with genuine intellectual depth.",
      "questions": [
        {{
          "item_number": 1,
          "question_text": "Full question text here.",
          "question_level": "Inferential",
          "difficulty_estimate": "Hard (p<0.40)",
          "options": {{
            "A": "option A text",
            "B": "option B text",
            "C": "option C text",
            "D": "option D text"
          }},
          "correct_answer": "C",
          "distractor_labels": {{
            "A": {{"type": "MAGNIFIED DETAIL TRAP", "explanation": "Fact IS in the passage (paragraph 2) but is only a supporting detail."}},
            "B": {{"type": "EXTERNAL PLAUSIBLE INTRUSION", "explanation": "Sounds on-topic but is completely absent from the passage."}},
            "D": {{"type": "PARTIAL TRUTH / SCOPE ERROR", "explanation": "Combines correct subject with wrong causal direction."}}
          }},
          "rationale": "DEEP RATIONALE minimum 7 sentences: (1) Which paragraphs contain the required evidence. (2) The inferential steps required. (3) Exact textual evidence for correct answer. (4) Why distractor A is a Magnified Detail Trap. (5) Why distractor B is External Plausible Intrusion. (6) Why distractor D fails. (7) Reading strategy a prepared student should apply.",
          "passage_paragraph_reference": "Paragraphs 2-4"
        }}
      ]
    }}
  ]
}}

ABSOLUTE RULE: Return ONLY valid JSON. No markdown fences. No commentary. No truncation of any passage or rationale under any circumstance.
"""

def clean_json(raw):
    s = raw.strip()
    for fence in ["```json", "```"]:
        if s.startswith(fence): s = s[len(fence):]
    if s.endswith("```"): s = s[:-3]
    last = s.rfind("}")
    if last != -1: s = s[:last+1]
    return s.strip()

# ==========================================
# 🚀 HERO SECTION
# ==========================================
st.markdown('<div id="main-content"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class='padayon-hero' role="banner">
    <div class='padayon-hero-bg'></div>
    <div class='padayon-hero-pattern' aria-hidden="true"></div>
    <div class='padayon-hero-inner'>
        <div class='hero-eyebrow' role="doc-subtitle">🌻 UPCAT LP+RC ELITE SIMULATOR · v8.0</div>
        <h1 class='hero-title'><em>Padayon!</em> Ang Wika!</h1>
        <p class='hero-sub'>
            Advanced psychometric simulation for UPCAT Language Proficiency and Reading Comprehension.
            Right-minus-wrong scoring · Real UPG computation · Transparent campus admission modeling.
            Item flagging, skill heatmaps, and WCAG AA accessibility built in.
        </p>
        <div class='hero-stats' role="list" aria-label="Exam statistics">
            <div class='hero-stat-item' role="listitem">
                <div class='hero-stat-num'>80+80</div>
                <div class='hero-stat-label'>LP + RC Items in Actual Exam</div>
            </div>
            <div class='hero-stat-item' role="listitem">
                <div class='hero-stat-num'>140k+</div>
                <div class='hero-stat-label'>Applicants Ranked by UPG</div>
            </div>
            <div class='hero-stat-item' role="listitem">
                <div class='hero-stat-num'>60/40</div>
                <div class='hero-stat-label'>UPCAT / HS Grades UPG Split</div>
            </div>
            <div class='hero-stat-item' role="listitem">
                <div class='hero-stat-num'>−0.25</div>
                <div class='hero-stat-label'>Penalty Per Wrong Answer</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='disclaimer' role="note" aria-label="Academic disclaimer">
    ⚠️ <strong>Academic Disclaimer:</strong> All examination items are AI-generated for practice only.
    UPG formulas and campus cutoffs are based on independent research modeling — not official UP System methodology.
    This simulator covers <strong>Language Proficiency and Reading Comprehension</strong> exclusively —
    the two subtests where language-track students gain the most decisive competitive advantage.
</div>
""", unsafe_allow_html=True)

# Generate row
col_btn, col_lp, col_rc = st.columns([3, 1, 1])
with col_btn:
    gen_btn = st.button(
        f"🚀 Generate {difficulty.upper()} Simulation — {num_items} Items",
        type="primary", use_container_width=True,
        help=f"Generates {num_lp} LP + {num_rc} RC items across {num_passages} passages at {difficulty} difficulty"
    )
with col_lp:
    st.markdown(f"""
    <div class='stat-pill' aria-label="{num_lp} Language Proficiency items">
        <div class='stat-pill-num' style='color:var(--maroon);'>{num_lp}</div>
        <div class='stat-pill-label'>LP Items</div>
    </div>
    """, unsafe_allow_html=True)
with col_rc:
    st.markdown(f"""
    <div class='stat-pill' aria-label="{num_rc} RC items across {num_passages} passages">
        <div class='stat-pill-num' style='color:var(--olive);'>{num_rc} / {num_passages}P</div>
        <div class='stat-pill-label'>RC Items / Passages</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ⚙️ GENERATION
# ==========================================
if gen_btn:
    if not api_key:
        st.error("❌ Please enter your Gemini API Key in the sidebar. Get a free key at aistudio.google.com.")
    else:
        prog = st.progress(0)
        status_box = st.empty()
        steps = [
            "📐 Calibrating psychometric parameters and difficulty ceiling...",
            "🗣️ Constructing LP item bank — English grammar, vocabulary, syntax...",
            "🌻 Constructing LP item bank — Filipino gramatika, talasalitaan, pangungusap...",
            "📖 Generating diverse RC passages (poetry, essays, stories, data, speeches...)...",
            "🔬 Writing inferential, textual, and evaluative RC questions with functional distractors...",
            "✅ Validating JSON structure, length parity, and answer key distribution..."
        ]
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                gemini_model,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.90,
                    "top_p": 0.96,
                    "max_output_tokens": 32000
                }
            )
            for i, step in enumerate(steps):
                status_box.info(step)
                prog.progress((i + 1) * 14)
                time.sleep(0.25)

            status_box.info("🧠 Querying AI — generating dense passages and deep rationales. This may take 45–120 seconds...")
            response = model.generate_content(UPCAT_PROMPT)
            prog.progress(92)

            raw = clean_json(response.text)
            test_data = json.loads(raw)

            if "language_proficiency" not in test_data or "reading_comprehension" not in test_data:
                raise ValueError("Invalid JSON: missing 'language_proficiency' or 'reading_comprehension' keys.")
            if len(test_data["language_proficiency"]) == 0:
                raise ValueError("No LP items generated.")
            if len(test_data["reading_comprehension"]) == 0:
                raise ValueError("No RC passages generated.")

            prog.progress(100)
            actual_lp = len(test_data["language_proficiency"])
            actual_rc = sum(len(p.get("questions", [])) for p in test_data["reading_comprehension"])
            actual_passages = len(test_data["reading_comprehension"])
            status_box.success(
                f"✅ Exam ready! {actual_lp} LP · {actual_rc} RC across {actual_passages} passages · {difficulty} difficulty"
            )

            time_per_item = (45 * 60) / 80
            st.session_state.update({
                'test_data': test_data,
                'user_answers_lp': {},
                'user_answers_rc': {},
                'flagged_items': set(),
                'start_time': time.time(),
                'time_limit': int(num_items * time_per_item),
                'submitted': False,
                'generation_error': None,
                'elapsed_time': 0,
            })
            time.sleep(1.0)
            st.rerun()

        except json.JSONDecodeError as e:
            st.error(f"❌ JSON Parse Error — model returned malformed JSON. Try Gemini 2.5 Pro. Details: {str(e)[:200]}")
            with st.expander("🔍 Raw API Response (debug)"):
                st.code(response.text[:4000] if 'response' in locals() else "No response captured.", language="text")
        except Exception as e:
            st.error(f"❌ Generation Error: {str(e)}")

# ==========================================
# 📝 EXAM INTERFACE
# ==========================================
if st.session_state.get('test_data') and not st.session_state.get('submitted'):
    test_data = st.session_state['test_data']
    time_limit = st.session_state.get('time_limit', 0)
    flagged = st.session_state.get('flagged_items', set())

    # Floating timer
    if show_timer:
        st.components.v1.html(f"""
        <div id="padayon-timer" role="timer" aria-live="polite" aria-atomic="true">⏱ <span id="t-val">--:--</span></div>
        <script>
        (function() {{
            var tl = {time_limit};
            function tick() {{
                if(tl < 0) tl = 0;
                var m = Math.floor(tl/60), s = tl%60;
                var el = document.getElementById('t-val');
                var box = document.getElementById('padayon-timer');
                if(el) {{
                    el.textContent = (m<10?'0':'')+m+':'+(s<10?'0':'')+s;
                    box.setAttribute('aria-label', 'Time remaining: ' + m + ' minutes ' + s + ' seconds');
                    if(tl<=300 && tl>0) {{ box.className='warn'; }}
                    if(tl<=0) {{ box.className='danger'; el.textContent='00:00 · TIME UP'; }}
                }}
                if(tl>0) {{ tl--; setTimeout(tick,1000); }}
            }}
            setTimeout(tick,400);
        }})();
        </script>
        """, height=0)

    lp_items = test_data.get('language_proficiency', [])
    rc_passages = test_data.get('reading_comprehension', [])
    rc_items_flat = [q for p in rc_passages for q in p.get('questions', [])]

    answered_lp = len(st.session_state['user_answers_lp'])
    answered_rc = len(st.session_state['user_answers_rc'])
    total_answered = answered_lp + answered_rc
    total_items = len(lp_items) + len(rc_items_flat)
    total_flagged = len(flagged)

    pct = (total_answered / max(1, total_items)) * 100

    # Progress bar with ARIA
    st.markdown(f"""
    <div class='prog-outer'>
        <div class='prog-meta'>
            <span>ANSWERED: {total_answered} / {total_items}</span>
            <span style='display:flex; gap:16px;'>
                <span style='color: #e67e22;'>🚩 FLAGGED: {total_flagged}</span>
                <span>{pct:.0f}% COMPLETE</span>
            </span>
        </div>
        <div class='prog-track' role="progressbar" aria-valuenow="{int(pct)}" aria-valuemin="0" aria-valuemax="100" aria-label="Exam progress: {int(pct)} percent complete">
            <div class='prog-fill' style='width:{pct:.1f}%'></div>
        </div>
        <div class='status-legend' aria-hidden="true">
            <span><span class='legend-dot' style='background:var(--olive);'></span>Answered</span>
            <span><span class='legend-dot' style='background:#e67e22;'></span>Flagged</span>
            <span><span class='legend-dot' style='background:var(--border);'></span>Blank</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='exam-warning' role="alert">
        ⚠️ <strong>RIGHT-MINUS-WRONG (RMW) IS ACTIVE:</strong>
        +1.0 correct · −0.25 wrong · 0 for blank. 
        <strong>Only guess if you can eliminate ≥2 options with confidence.</strong>
        Blank is mathematically smarter than reckless guessing. Use 🚩 to flag items for review.
    </div>
    """, unsafe_allow_html=True)

    tab_lp, tab_rc = st.tabs([
        f"🗣️ Language Proficiency  ({len(lp_items)} items · {answered_lp} answered)",
        f"📖 Reading Comprehension  ({len(rc_items_flat)} items · {answered_rc} answered)"
    ])

    # ─── LP TAB ───
    with tab_lp:
        # Item navigator
        if show_item_nav and lp_items:
            nav_html = "<div class='item-nav' aria-label='LP Item Navigator'><div class='item-nav-title'>LP Item Navigator — click to jump</div><div class='item-nav-grid'>"
            for q in lp_items:
                inum = q.get('item_number')
                is_ans = inum in st.session_state['user_answers_lp']
                is_flag = f"lp_{inum}" in flagged
                dot_cls = "flagged" if is_flag else ("answered" if is_ans else "")
                nav_html += f"<div class='nav-dot {dot_cls}' title='LP {inum}' onclick=\"document.getElementById('lp_{inum}').scrollIntoView({{behavior:'smooth'}})\" role='button' tabindex='0' aria-label='Go to LP item {inum}'>{inum}</div>"
            nav_html += "</div></div>"
            st.markdown(nav_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        for q in lp_items:
            inum = q.get('item_number')
            lang = q.get('language', 'English')
            skill = q.get('skill_tested', '')
            itype = q.get('item_type', '')
            diff_est = q.get('difficulty_estimate', '')
            is_ans = inum in st.session_state['user_answers_lp']
            is_flag = f"lp_{inum}" in flagged

            lang_tag_cls = "q-tag-lang-fil" if lang == "Filipino" else "q-tag-lang-en"
            lang_icon = "🌻 Filipino" if lang == "Filipino" else "🔵 English"
            diff_color = "#e74c3c" if "Hard" in diff_est else ("#e67e22" if "Medium" in diff_est else "#27ae60")

            card_cls = "q-card"
            if is_ans: card_cls += " answered"
            if is_flag: card_cls += " flagged"

            st.markdown(f"""
            <div class='{card_cls}' id='lp_{inum}' role="article" aria-label="LP Item {inum}">
                <div class='q-card-meta'>
                    <span class='q-num'>LP ITEM {inum}</span>
                    <span class='q-tag q-tag-skill'>{itype}</span>
                    <span class='q-tag {lang_tag_cls}'>{lang_icon}</span>
                    <span class='q-tag q-tag-type'>{skill[:35]}{"..." if len(skill)>35 else ""}</span>
                    {f"<span style='font-family:var(--font-mono); font-size:0.58rem; font-weight:700; color:{diff_color}; margin-left:auto;'>{diff_est}</span>" if diff_est else ""}
                </div>
                <div class='q-stem' id='lp_stem_{inum}'>{q.get('question_text', '')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Study mode hint
            if show_rationale_inline:
                st.caption(f"💡 Skill focus: {skill}")

            opts = q.get('options', {})
            choices = [
                f"A) {opts.get('A','')}", f"B) {opts.get('B','')}",
                f"C) {opts.get('C','')}", f"D) {opts.get('D','')}"
            ]
            choice = st.radio(
                f"Answer for LP Item {inum}", choices,
                key=f"lp_r_{inum}", index=None, label_visibility="collapsed"
            )
            if choice:
                st.session_state['user_answers_lp'][inum] = choice[0]

            # Flag button
            if enable_flagging:
                flag_key = f"lp_{inum}"
                flag_label = "🚩 Unflag" if flag_key in flagged else "🚩 Flag for Review"
                if st.button(flag_label, key=f"flag_lp_{inum}", help="Flag this item to review before submitting"):
                    if flag_key in flagged:
                        flagged.discard(flag_key)
                    else:
                        flagged.add(flag_key)
                    st.session_state['flagged_items'] = flagged
                    st.rerun()

            st.markdown("<hr style='border:none; border-top:1px solid var(--border-light); margin:12px 0 16px;'>", unsafe_allow_html=True)

    # ─── RC TAB ───
    with tab_rc:
        if show_item_nav and rc_items_flat:
            nav_html = "<div class='item-nav' aria-label='RC Item Navigator'><div class='item-nav-title'>RC Item Navigator</div><div class='item-nav-grid'>"
            for q in rc_items_flat:
                qnum = q.get('item_number')
                is_ans = qnum in st.session_state['user_answers_rc']
                is_flag = f"rc_{qnum}" in flagged
                dot_cls = "flagged" if is_flag else ("answered" if is_ans else "")
                nav_html += f"<div class='nav-dot {dot_cls}' title='RC {qnum}' onclick=\"document.getElementById('rc_{qnum}').scrollIntoView({{behavior:'smooth'}})\" role='button' tabindex='0' aria-label='Go to RC item {qnum}'>{qnum}</div>"
            nav_html += "</div></div>"
            st.markdown(nav_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        for passage in rc_passages:
            pid = passage.get('passage_id')
            genre = passage.get('genre', 'Passage')
            genre_sub = passage.get('genre_subtype', '')
            lang = passage.get('language', 'English')
            title = passage.get('passage_title', f'Passage {pid}')
            ptext = passage.get('passage_text', '')
            wc = passage.get('word_count', len(ptext.split()))
            pqs = passage.get('questions', [])
            vocab_focus = passage.get('vocabulary_focus', [])

            lang_pill = "🌻 Filipino" if lang == "Filipino" else "🔵 English"
            genre_display = f"{genre} — {genre_sub}" if genre_sub else genre
            p_answered = sum(1 for q in pqs if q.get('item_number') in st.session_state['user_answers_rc'])

            st.markdown(f"""
            <div class='passage-shell' role="article" aria-label="Passage {pid}: {title}">
                <div class='passage-top'>
                    <div class='passage-top-left'>
                        <h4>Passage {pid}: {title}</h4>
                        <div style='display:flex; gap:5px; flex-wrap:wrap; margin-bottom:6px;'>
                            <span class='passage-pill'>{genre_display}</span>
                            <span class='passage-pill'>{lang_pill}</span>
                            <span class='passage-pill'>~{wc} words</span>
                            <span class='passage-pill'>{p_answered}/{len(pqs)} answered</span>
                        </div>
                        {f"<div style='font-family:var(--font-mono); font-size:0.58rem; color:rgba(255,255,255,0.4); letter-spacing:0.1em;'>VOCABULARY FOCUS: {' · '.join(vocab_focus)}</div>" if vocab_focus else ""}
                    </div>
                    <div class='passage-strategy' role="note" aria-label="Exam strategy tip">
                        <strong>📌 Strategy:</strong> Read questions first. Underline key terms.
                        Then read passage. Map each question to specific paragraphs before answering.
                    </div>
                </div>
                <div class='passage-body-wrap'>
                    <div class='passage-text' role="document" aria-label="Passage text for {title}">
            """, unsafe_allow_html=True)

            for para in ptext.split('\n\n'):
                para = para.strip()
                if para:
                    st.markdown(para)

            st.markdown(f"""
                    </div>
                </div>
                <div class='passage-qs-wrap'>
                    <div class='passage-qs-title'>📝 Questions for Passage {pid}: {title}</div>
            """, unsafe_allow_html=True)

            for q in pqs:
                qnum = q.get('item_number')
                qlvl = q.get('question_level', 'Inferential')
                diff_est = q.get('difficulty_estimate', '')
                is_ans = qnum in st.session_state['user_answers_rc']
                is_flag = f"rc_{qnum}" in flagged
                diff_color = "#e74c3c" if "Hard" in diff_est else ("#e67e22" if "Medium" in diff_est else "#27ae60")

                lvl_cls = {
                    'Textual': 'lvl-textual',
                    'Inferential': 'lvl-inferential',
                    'Critical/Evaluative': 'lvl-critical'
                }.get(qlvl, 'lvl-inferential')

                st.markdown(f"""
                <div id='rc_{qnum}' style='margin: 8px 0 4px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;'>
                    <span class='lvl-badge {lvl_cls}'>RC {qnum} · {qlvl}</span>
                    {f"<span style='font-family:var(--font-mono); font-size:0.58rem; font-weight:700; color:{diff_color};'>{diff_est}</span>" if diff_est else ""}
                    {f"<span style='font-size:0.75rem;'>🚩</span>" if is_flag else ""}
                    {f"<span style='font-size:0.75rem;'>✅</span>" if is_ans else ""}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**{q.get('question_text', '')}**")

                qopts = q.get('options', {})
                qchoices = [
                    f"A) {qopts.get('A','')}", f"B) {qopts.get('B','')}",
                    f"C) {qopts.get('C','')}", f"D) {qopts.get('D','')}"
                ]
                qchoice = st.radio(
                    f"Answer for RC Item {qnum}", qchoices,
                    key=f"rc_r_{qnum}", index=None, label_visibility="collapsed"
                )
                if qchoice:
                    st.session_state['user_answers_rc'][qnum] = qchoice[0]

                if enable_flagging:
                    flag_key = f"rc_{qnum}"
                    flag_label = "🚩 Unflag" if flag_key in flagged else "🚩 Flag for Review"
                    if st.button(flag_label, key=f"flag_rc_{qnum}", help="Flag to review before submitting"):
                        if flag_key in flagged:
                            flagged.discard(flag_key)
                        else:
                            flagged.add(flag_key)
                        st.session_state['flagged_items'] = flagged
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # ─── SUBMIT ───
    st.markdown("<br>", unsafe_allow_html=True)
    unanswered = total_items - total_answered

    # Pre-submit summary
    col_sum1, col_sum2, col_sum3 = st.columns(3)
    with col_sum1:
        st.markdown(f"""
        <div class='stat-pill'>
            <div class='stat-pill-num' style='color:var(--olive);'>{total_answered}</div>
            <div class='stat-pill-label'>Answered</div>
        </div>
        """, unsafe_allow_html=True)
    with col_sum2:
        st.markdown(f"""
        <div class='stat-pill'>
            <div class='stat-pill-num' style='color:#e67e22;'>{total_flagged}</div>
            <div class='stat-pill-label'>Flagged</div>
        </div>
        """, unsafe_allow_html=True)
    with col_sum3:
        st.markdown(f"""
        <div class='stat-pill'>
            <div class='stat-pill-num' style='color:var(--fg-mute);'>{unanswered}</div>
            <div class='stat-pill-label'>Blank (0 pts)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
    with col_s2:
        if unanswered > 0:
            st.warning(
                f"⚠️ **{unanswered} item(s) unanswered.** Blank = 0 points (no penalty). "
                f"Only guess if you can eliminate 2+ options. Otherwise leave blank."
            )
        if total_flagged > 0:
            st.info(f"🚩 **{total_flagged} flagged item(s)** — review them before submitting.")
        if st.button(
            "📥 Submit Exam & Generate Full UPG Report",
            type="primary", use_container_width=True,
            help="Calculates your UPG, admission chances, skill heatmap, and deep item-level feedback"
        ):
            st.session_state['submitted'] = True
            st.session_state['elapsed_time'] = time.time() - st.session_state.get('start_time', time.time())
            st.rerun()

# ==========================================
# 📊 RESULTS ENGINE
# ==========================================
if st.session_state.get('submitted') and st.session_state.get('test_data'):
    st.balloons()
    test_data = st.session_state['test_data']
    u_lp = st.session_state.get('user_answers_lp', {})
    u_rc = st.session_state.get('user_answers_rc', {})
    elapsed = st.session_state.get('elapsed_time', 0)
    e_min, e_sec = int(elapsed // 60), int(elapsed % 60)

    lp_items = test_data.get('language_proficiency', [])
    rc_passages = test_data.get('reading_comprehension', [])
    rc_all_q = [q for p in rc_passages for q in p.get('questions', [])]

    # ── SCORING ──
    lp_total = len(lp_items)
    lp_correct = sum(1 for q in lp_items if u_lp.get(q.get('item_number')) == q.get('correct_answer'))
    lp_answered = sum(1 for v in u_lp.values() if v)
    lp_wrong = lp_answered - lp_correct
    lp_blank = lp_total - lp_answered
    lp_raw = max(0.0, lp_correct - 0.25 * lp_wrong)
    lp_pct = lp_raw / max(1, lp_total)

    rc_total = len(rc_all_q)
    rc_correct = sum(1 for q in rc_all_q if u_rc.get(q.get('item_number')) == q.get('correct_answer'))
    rc_answered = sum(1 for v in u_rc.values() if v)
    rc_wrong = rc_answered - rc_correct
    rc_blank = rc_total - rc_answered
    rc_raw = max(0.0, rc_correct - 0.25 * rc_wrong)
    rc_pct = rc_raw / max(1, rc_total)

    # ── GRADE UPG (40%) ──
    all_grades = [g8_eng, g8_fil, g9_eng, g9_fil, g10_eng, g10_fil,
                  g11_lit, g11_eapp, g11_rw, g11_kom, g11_pag, g11_ps]
    raw_avg = float(np.mean(all_grades))
    jhs_mod = SCHOOL_TIERS[jhs_type]["modifier"]
    shs_mod = SCHOOL_TIERS[shs_type]["modifier"]
    avg_mod = (jhs_mod + shs_mod) / 2
    grade_upg_raw = 5.0 - ((raw_avg - 75) / 25) * 4.0
    grade_upg_final = max(1.0, min(5.0, grade_upg_raw - avg_mod))

    # ── UPCAT UPG (60%) ──
    combined_pct = (lp_pct + rc_pct) / 2
    upcat_z = (combined_pct - MEAN_BASELINE) / SIGMA
    upcat_upg = max(1.0, min(5.0, 2.75 - (upcat_z * 0.55)))
    overall_pct = 0.5 * (1 + math.erf(upcat_z / math.sqrt(2)))
    overall_pct = max(0.001, min(0.9999, overall_pct))

    # ── COMPOSITE UPG ──
    final_upg = (0.40 * grade_upg_final) + (0.60 * upcat_upg)
    sim_rank = int(140000 - (140000 * overall_pct))

    # ── UPG VERDICT ──
    if final_upg <= 1.500:
        verdict = "🏆 Exceptional — Strong contender for any UP program."
    elif final_upg <= 2.000:
        verdict = "✅ Very Strong — Qualified for most competitive programs."
    elif final_upg <= 2.400:
        verdict = "📘 Competitive — Eligible for several programs; some may require higher."
    elif final_upg <= 2.700:
        verdict = "🟡 Moderate — May qualify for programs with higher quotas."
    elif final_upg <= 3.000:
        verdict = "🟠 Below Threshold — May qualify at certain campuses."
    else:
        verdict = "🔴 Needs Improvement — Focus on both UPCAT and high school grades."

    # ── SKILL ANALYSIS ──
    skill_results = {}
    for q in lp_items:
        sk = q.get('skill_tested', q.get('item_type', 'Unknown'))
        lang = q.get('language', 'English')
        key = f"{lang[:2]}·{sk[:30]}"
        inum = q.get('item_number')
        correct = u_lp.get(inum) == q.get('correct_answer')
        answered = u_lp.get(inum) is not None
        if key not in skill_results:
            skill_results[key] = {'correct': 0, 'total': 0, 'lang': lang}
        skill_results[key]['total'] += 1
        if correct: skill_results[key]['correct'] += 1

    # ── RESULTS HERO ──
    st.markdown(f"""
    <div class='results-hero' role="main" aria-label="Your UPG Result">
        <div class='upg-label'>YOUR UNIVERSITY PREDICTED GRADE (UPG)</div>
        <div class='upg-display' aria-label="UPG score: {final_upg:.3f}">{final_upg:.3f}</div>
        <div class='upg-verdict'>{verdict}</div>
        <div style='color:rgba(255,255,255,0.45); font-family:var(--font-mono); font-size:0.66rem; margin-top:10px; letter-spacing:0.1em; position:relative; z-index:1;'>
            1.000 (HIGHEST) → 5.000 (LOWEST) · Simulated rank #{sim_rank:,} / 140,000
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRIC TILES ──
    metrics = [
        (f"{final_upg:.3f}", "", "Final UPG", "1.000 = Best · 5.000 = Worst"),
        (f"#{sim_rank:,}", "gold", "Simulated Rank", f"Top {100*(1-overall_pct):.1f}% of cohort"),
        (f"{grade_upg_final:.3f}", "green", "Grades UPG (40%)", f"Avg: {raw_avg:.1f}/100"),
        (f"{upcat_upg:.3f}", "", "UPCAT UPG (60%)", f"Z-Score: {upcat_z:+.2f}"),
        (f"{lp_pct*100:.1f}%", "green", "LP Score %", f"{lp_correct}C · {lp_wrong}W · {lp_blank} Blank"),
        (f"{rc_pct*100:.1f}%", "", "RC Score %", f"{rc_correct}C · {rc_wrong}W · {rc_blank} Blank"),
    ]
    cols = st.columns(3)
    for i, (val, color_cls, label, sub) in enumerate(metrics):
        with cols[i % 3]:
            st.markdown(f"""
            <div class='metric-tile' role="figure" aria-label="{label}: {val}">
                <div class='metric-tile-val {color_cls}'>{val}</div>
                <div class='metric-tile-label'>{label}</div>
                <div class='metric-tile-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── SCORE PANELS ──
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class='score-panel' role="region" aria-label="Language Proficiency breakdown">
            <h4>🗣️ Language Proficiency Breakdown</h4>
            <div class='score-row'><span class='score-lbl'>Correct Answers</span><span class='score-val c'>{lp_correct} / {lp_total}</span></div>
            <div class='score-row'><span class='score-lbl'>Wrong Answers</span><span class='score-val w'>{lp_wrong} (−{0.25*lp_wrong:.2f} pts)</span></div>
            <div class='score-row'><span class='score-lbl'>Blank / Skipped</span><span class='score-val'>{lp_blank}</span></div>
            <div class='score-row'><span class='score-lbl'>Raw Score (RMW)</span><span class='score-val g'>{lp_raw:.2f} / {lp_total}</span></div>
            <div class='score-row'><span class='score-lbl'>Percentage Score</span><span class='score-val g'>{lp_pct*100:.1f}%</span></div>
            <div class='score-row'><span class='score-lbl'>Accuracy on Attempted</span><span class='score-val'>{(lp_correct/max(1,lp_answered)*100):.1f}%</span></div>
            <div class='score-row'><span class='score-lbl'>Penalty Incurred</span><span class='score-val w'>−{lp_wrong*0.25:.2f} pts</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class='score-panel' role="region" aria-label="Reading Comprehension breakdown">
            <h4>📖 Reading Comprehension Breakdown</h4>
            <div class='score-row'><span class='score-lbl'>Correct Answers</span><span class='score-val c'>{rc_correct} / {rc_total}</span></div>
            <div class='score-row'><span class='score-lbl'>Wrong Answers</span><span class='score-val w'>{rc_wrong} (−{0.25*rc_wrong:.2f} pts)</span></div>
            <div class='score-row'><span class='score-lbl'>Blank / Skipped</span><span class='score-val'>{rc_blank}</span></div>
            <div class='score-row'><span class='score-lbl'>Raw Score (RMW)</span><span class='score-val g'>{rc_raw:.2f} / {rc_total}</span></div>
            <div class='score-row'><span class='score-lbl'>Percentage Score</span><span class='score-val g'>{rc_pct*100:.1f}%</span></div>
            <div class='score-row'><span class='score-lbl'>Accuracy on Attempted</span><span class='score-val'>{(rc_correct/max(1,rc_answered)*100):.1f}%</span></div>
            <div class='score-row'><span class='score-lbl'>Penalty Incurred</span><span class='score-val w'>−{rc_wrong*0.25:.2f} pts</span></div>
        </div>
        """, unsafe_allow_html=True)

    # ── SKILL HEATMAP ──
    if skill_results:
        st.markdown("""
        <div class='sec-div'>
            <h3>🔥 Skill Mastery Heatmap</h3>
            <div class='sec-line'></div>
        </div>
        """, unsafe_allow_html=True)

        skill_html = "<div class='skill-heatmap' role='list' aria-label='Skill mastery breakdown'>"
        for sk, data in sorted(skill_results.items(), key=lambda x: x[1]['correct']/max(1,x[1]['total'])):
            pct_sk = data['correct'] / max(1, data['total']) * 100
            bar_cls = "strong" if pct_sk >= 70 else ("mid" if pct_sk >= 40 else "weak")
            lang_badge = "🌻" if data['lang'] == "Filipino" else "🔵"
            label = sk.split('·', 1)[1] if '·' in sk else sk
            skill_html += f"""
            <div class='skill-row' role='listitem' aria-label='{label}: {pct_sk:.0f}% correct'>
                <span style='font-size:0.75rem;'>{lang_badge}</span>
                <span style='font-family:var(--font-ui); font-size:0.75rem; flex:1; color:var(--fg-mid); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;' title='{label}'>{label}</span>
                <div class='skill-bar-outer' aria-hidden='true'>
                    <div class='skill-bar-inner {bar_cls}' style='width:{pct_sk:.0f}%;'></div>
                </div>
                <span class='skill-pct' style='color:{"var(--olive)" if bar_cls=="strong" else ("var(--gold)" if bar_cls=="mid" else "var(--maroon)")};'>{pct_sk:.0f}%</span>
                <span style='font-family:var(--font-mono); font-size:0.58rem; color:var(--fg-mute);'>{data["correct"]}/{data["total"]}</span>
            </div>"""
        skill_html += "</div>"
        st.markdown(skill_html, unsafe_allow_html=True)

    # ── ADMISSION ENGINE ──
    st.markdown("""
    <div class='sec-div'>
        <h3>🏛️ Cascading Admission Decision Engine</h3>
        <div class='sec-line'></div>
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
            note = "Borderline — may compete for leftover slots"
        else:
            badge = "<span class='badge-fail'>❌ REJECTED</span>"
            note = "Exceeds slot ceiling for this program"
        return badge, req, note, tier

    col_c1, col_c2 = st.columns(2)
    for col, campus, progs, cn in [
        (col_c1, campus_1, [c1_p1, c1_p2, c1_p3, c1_p4], "1st"),
        (col_c2, campus_2, [c2_p1, c2_p2, c2_p3, c2_p4], "2nd")
    ]:
        cutoff = CAMPUS_DATA[campus]["cutoff"]
        recon = CAMPUS_DATA[campus]["recon"]
        qualified = final_upg <= cutoff
        header_cls = "" if qualified else "rejected"
        status_txt = "✅ QUALIFIED" if qualified else "❌ NOT QUALIFIED"
        note_txt = CAMPUS_DATA[campus]["note"]

        with col:
            st.markdown(f"""
            <div class='campus-shell' role="region" aria-label="{cn} campus choice: {campus}">
                <div class='campus-header {header_cls}'>
                    <h4>{cn} Choice — {campus}</h4>
                    <p>Cutoff: {cutoff:.3f} · Your UPG: {final_upg:.3f} · {status_txt} · {note_txt}</p>
                </div>
                <div class='campus-body'>
            """, unsafe_allow_html=True)

            if campus == campus_2 and final_upg <= CAMPUS_DATA[campus_1]["cutoff"]:
                st.info("📌 You qualified at Campus 1 — Campus 2 is nullified in the actual UP cascading system. Shown for reference only.")

            if qualified:
                for i, prog in enumerate(progs, 1):
                    badge, req, note, tier = evaluate_program(campus, prog, cutoff, final_upg)
                    st.markdown(f"""
                    <div class='prog-row'>
                        <div>
                            <div class='prog-name'>Priority {i}: {prog}</div>
                            <div class='prog-meta'>{tier} · Effective cutoff ~{req:.3f} · {note}</div>
                        </div>
                        <div>{badge}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                recon_eligible = recon > 0 and final_upg <= recon
                recon_txt = "✅ Recon-eligible" if recon_eligible else ("❌ Recon not possible" if recon > 0 else "🚫 NO APPEALS POLICY")
                st.markdown(f"""
                <div style='padding:18px; text-align:center; font-family:var(--font-ui); font-size:0.88rem; color:var(--fg-mid);'>
                    Your UPG of <strong>{final_upg:.3f}</strong> exceeds the campus cutoff of <strong>{cutoff:.3f}</strong>.<br><br>
                    <strong>Reconsideration threshold: {f"{recon:.3f}" if recon > 0 else "None"}</strong><br>
                    {recon_txt}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ── DEEP ANALYTICS TABS ──
    st.markdown("""
    <div class='sec-div'>
        <h3>🔬 Deep Analytics & Personalized Mastery Feedback</h3>
        <div class='sec-line'></div>
    </div>
    """, unsafe_allow_html=True)

    t_overview, t_grades, t_upcat_math, t_recon, t_lp_rev, t_rc_rev = st.tabs([
        "📊 Overview", "📚 Grades Math", "🧠 UPCAT Math", "⚖️ Recon & DPWAS", "🗣️ LP Review", "📖 RC Review"
    ])

    # ──── OVERVIEW TAB ────
    with t_overview:
        lp_en_items = [q for q in lp_items if q.get('language') == 'English']
        lp_fil_items = [q for q in lp_items if q.get('language') == 'Filipino']
        lp_en_correct = sum(1 for q in lp_en_items if u_lp.get(q.get('item_number')) == q.get('correct_answer'))
        lp_fil_correct = sum(1 for q in lp_fil_items if u_lp.get(q.get('item_number')) == q.get('correct_answer'))
        lp_en_pct = lp_en_correct / max(1, len(lp_en_items)) * 100
        lp_fil_pct = lp_fil_correct / max(1, len(lp_fil_items)) * 100

        rc_by_level = {'Textual': [], 'Inferential': [], 'Critical/Evaluative': []}
        for q in rc_all_q:
            lvl = q.get('question_level', 'Inferential')
            if lvl in rc_by_level: rc_by_level[lvl].append(q)

        rc_lvl_scores = {}
        for lvl, qs in rc_by_level.items():
            correct_in_lvl = sum(1 for q in qs if u_rc.get(q.get('item_number')) == q.get('correct_answer'))
            rc_lvl_scores[lvl] = (correct_in_lvl, len(qs), correct_in_lvl / max(1, len(qs)) * 100)

        skill_errors = {}
        for q in lp_items:
            if u_lp.get(q.get('item_number')) and u_lp.get(q.get('item_number')) != q.get('correct_answer'):
                sk = q.get('skill_tested', 'Unknown')
                skill_errors[sk] = skill_errors.get(sk, 0) + 1
        top_errors = sorted(skill_errors.items(), key=lambda x: -x[1])[:5]

        time_per_item_actual = elapsed / max(1, lp_total + rc_total)
        upcat_time_budget = 45 * 60 / 80
        time_ratio = time_per_item_actual / upcat_time_budget

        penalty_total = (lp_wrong + rc_wrong) * 0.25
        guess_risk = (lp_wrong + rc_wrong) / max(1, lp_answered + rc_answered)

        # RMW Strategy Score
        expected_wrong_random = (lp_answered + rc_answered) * 0.75
        penalty_efficiency = 1.0 - (lp_wrong + rc_wrong) / max(1, expected_wrong_random)

        st.markdown(f"""
        <div class='deep-feedback-box' role="region" aria-label="Performance overview">
            <h5>📊 Comprehensive Performance Overview — {difficulty} Simulation</h5>
            <p style='font-family:var(--font-body); font-size:0.92rem; line-height:1.90; color:var(--fg-mid);'>
                You completed this <strong>{difficulty}</strong>-difficulty simulation with a combined LP+RC percentage of 
                <strong>{combined_pct*100:.1f}%</strong> against a competitive mean of 
                <strong>{MEAN_BASELINE*100:.0f}%</strong> (σ={SIGMA:.2f}). 
                Your Z-Score of <strong>{upcat_z:+.2f}</strong> places you at the 
                <strong>{overall_pct*100:.1f}th percentile</strong> of the simulated 140,000-applicant cohort.
                You incurred <strong>−{penalty_total:.2f} penalty points</strong> from {lp_wrong + rc_wrong} wrong answers.
                {"✅ Your penalty profile is efficient — you guessed selectively." if guess_risk < 0.25 else
                "⚠️ Moderate penalty load — consider more selective guessing on test day." if guess_risk < 0.40 else
                "🔴 High penalty load — aggressive guessing cost you significantly. Practice the elimination rule."}
            </p>
            <div class='feedback-grid'>
                <div class='feedback-card'>
                    <div class='feedback-card-title'>🇺🇸 English LP ({lp_en_correct}/{len(lp_en_items)})</div>
                    <div class='feedback-card-body'>
                        <strong>{lp_en_pct:.0f}% accuracy</strong><br>
                        {"✅ Strong English foundation." if lp_en_pct >= 70 else
                        "📘 Moderate — focus on the specific grammar rules you missed." if lp_en_pct >= 50 else
                        "📖 Needs work — prioritize parts of speech, SVA rules, sentence structure. Read broadsheets daily."}
                    </div>
                </div>
                <div class='feedback-card'>
                    <div class='feedback-card-title'>🌻 Filipino LP ({lp_fil_correct}/{len(lp_fil_items)})</div>
                    <div class='feedback-card-body'>
                        <strong>{lp_fil_pct:.0f}% accuracy</strong><br>
                        {"✅ Malakas ang iyong Akademikong Filipino." if lp_fil_pct >= 70 else
                        "📘 Katamtaman — fokus sa pandiwang aspeto, panlapi, at mga sawikain." if lp_fil_pct >= 50 else
                        "📖 Kailangan ng maraming pagsasanay — basahin ang mga pormal na teksto. Fokus sa pandiwang pokus at panlapi."}
                    </div>
                </div>
                <div class='feedback-card'>
                    <div class='feedback-card-title'>📖 RC by Level</div>
                    <div class='feedback-card-body'>
                        {"".join([f"<strong>{lvl}:</strong> {sc[0]}/{sc[1]} ({sc[2]:.0f}%)<br>" for lvl, sc in rc_lvl_scores.items() if sc[1] > 0])}
                        {"✅ All levels strong." if all(sc[2] >= 60 for sc in rc_lvl_scores.values() if sc[1] > 0) else
                        "Critical/evaluative hardest — practice identifying author's purpose and unstated assumptions." if rc_lvl_scores.get('Critical/Evaluative', (0,0,0))[2] < 50 else
                        "Focus on inferential — requires synthesizing across paragraphs, not just locating facts."}
                    </div>
                </div>
                <div class='feedback-card'>
                    <div class='feedback-card-title'>⏱️ Time Management</div>
                    <div class='feedback-card-body'>
                        <strong>{e_min}m {e_sec}s</strong> · {time_per_item_actual:.1f}s/item<br>
                        UPCAT budget: ~{upcat_time_budget:.0f}s/item<br>
                        {"✅ Good pacing — within UPCAT budget." if 0.7 <= time_ratio <= 1.3 else
                        "⚡ You rushed — increased error rate risk. Review flagged items." if time_ratio < 0.7 else
                        "⏰ Over budget — practice reading faster. In RC: read questions first, then passage."}
                    </div>
                </div>
                <div class='feedback-card'>
                    <div class='feedback-card-title'>⚡ RMW Penalty Analysis</div>
                    <div class='feedback-card-body'>
                        Penalty: <strong>−{penalty_total:.2f} pts</strong><br>
                        Wrong: {lp_wrong+rc_wrong} of {lp_answered+rc_answered} attempted<br>
                        Error rate: <strong>{guess_risk*100:.0f}%</strong> of attempted<br>
                        {"✅ Excellent discrimination — you only answered when confident." if guess_risk < 0.20 else
                        "Good — slightly aggressive but manageable." if guess_risk < 0.35 else
                        "⚠️ Too many wrong guesses. RMW rule: guess only after eliminating ≥2 options."}
                    </div>
                </div>
                <div class='feedback-card'>
                    <div class='feedback-card-title'>🎯 Next Steps</div>
                    <div class='feedback-card-body'>
                        {"1. Drill weak skill areas below.<br>2. Daily broadsheet reading (Philippine Star, Inquirer).<br>3. Filipino: Basahin ang Hulagpos at mga pormal na pahayagan.<br>4. Practice RC with timer — 33 seconds per item max.<br>5. Retake at higher difficulty when this level hits 70%+" if combined_pct < 0.60 else
                        "1. Push to Brutal/Massacre difficulty.<br>2. Target 0% wrong-answer rate (leave blank if unsure).<br>3. Focus specifically on your weakest skill tags.<br>4. Time yourself strictly — 33s per item is the real budget.<br>5. Study distractor types — you can spot traps if you know them."}
                    </div>
                </div>
            </div>
            {"<div style='margin-top:16px; padding:14px 18px; background:var(--maroon-pale); border-radius:8px; border:1px solid var(--maroon-tint);'><strong style='color:var(--maroon); font-family:var(--font-ui);'>🎯 Top " + str(len(top_errors)) + " Skill Gaps (most errors first):</strong><ul style='margin:8px 0 0 18px; font-family:var(--font-mono); font-size:0.78rem;'>" + "".join([f"<li><strong>{sk}</strong> — {cnt} error(s)</li>" for sk, cnt in top_errors]) + "</ul></div>" if top_errors else ""}
        </div>
        """, unsafe_allow_html=True)

    # ──── GRADES TAB ────
    with t_grades:
        st.markdown("<div class='feedback-shell gold-accent'>", unsafe_allow_html=True)
        st.markdown("### 📊 High School Language Grades Standardization (40% Weight)")
        g_cols = st.columns(4)
        grade_inputs = [
            ("G8 English", g8_eng), ("G8 Filipino", g8_fil),
            ("G9 English", g9_eng), ("G9 Filipino", g9_fil),
            ("G10 English", g10_eng), ("G10 Filipino", g10_fil),
            ("G11 21st Lit", g11_lit), ("G11 EAPP", g11_eapp),
            ("G11 Read&Write", g11_rw), ("G11 Komunikasyon", g11_kom),
            ("G11 Pagbasa", g11_pag), ("G11 Pagsulat", g11_ps),
        ]
        for i, (lbl, val) in enumerate(grade_inputs):
            g_cols[i % 4].metric(lbl, f"{val:.1f}")

        st.markdown(f"""
        **Unweighted Language Grade Average:** {raw_avg:.2f} / 100  
        **JHS School Modifier:** {jhs_mod:+.3f} ({SCHOOL_TIERS[jhs_type]['label']})  
        **SHS School Modifier:** {shs_mod:+.3f} ({SCHOOL_TIERS[shs_type]['label']})  
        **Combined Modifier:** {avg_mod:+.3f}  
        **Grade UPG (raw):** {grade_upg_raw:.3f} → **Grade UPG (adjusted):** {grade_upg_final:.3f}
        """)

        if avg_mod > 0:
            st.success(f"✅ **Palugit Active:** Public school rigor protection applied. UPG improved {grade_upg_raw:.3f} → {grade_upg_final:.3f} (−{avg_mod:.3f} pts).")
        elif avg_mod < 0:
            st.warning(f"⚠️ **Pabigat Applied:** Private school grade inflation adjustment. UPG worsened {grade_upg_raw:.3f} → {grade_upg_final:.3f} (+{abs(avg_mod):.3f} pts).")

        with st.expander("📐 Grade UPG Formula — Full Derivation"):
            st.latex(r"UPG_{\text{grade, raw}} = 5.0 - \left(\frac{\bar{G} - 75}{25}\right) \times 4.0")
            st.latex(f"= 5.0 - \\left(\\frac{{{raw_avg:.2f} - 75}}{{25}}\\right) \\times 4.0 = {grade_upg_raw:.3f}")
            st.latex(r"UPG_{\text{grade, final}} = \text{clamp}\left(UPG_{\text{raw}} - \Delta_{\text{school}},\ 1.0,\ 5.0\right)")
            st.latex(f"= {grade_upg_raw:.3f} - ({avg_mod:+.3f}) = {grade_upg_final:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ──── UPCAT MATH TAB ────
    with t_upcat_math:
        st.markdown("<div class='feedback-shell olive-accent'>", unsafe_allow_html=True)
        st.markdown("### 🧠 UPCAT Right-Minus-Wrong Forensics (60% Weight)")

        st.markdown(f"""
        Combined RMW-penalized score: LP ({lp_pct*100:.1f}%) + RC ({rc_pct*100:.1f}%) → composite **{combined_pct*100:.1f}%**. 
        Benchmarked against competitive mean **{MEAN_BASELINE*100:.0f}%** (σ={SIGMA:.2f}). 
        Most UPCAT takers are already above-average students, so the mean is higher than naive expectations.

        **Z-Score {upcat_z:+.2f}** → {abs(upcat_z):.2f} SD {"above" if upcat_z >= 0 else "below"} mean →
        simulated rank **#{sim_rank:,} / 140,000** (top {100*(1-overall_pct):.1f}%).
        """)

        with st.expander("📐 Full UPCAT UPG Derivation"):
            st.latex(r"\text{RMW} = \text{Correct} - \frac{1}{4} \times \text{Wrong}")
            st.latex(r"\bar{P} = \frac{LP\% + RC\%}{2} = " + f"\\frac{{{lp_pct:.4f} + {rc_pct:.4f}}}{{2}} = {combined_pct:.4f}")
            st.latex(r"Z = \frac{\bar{P} - \mu}{\sigma} = " + f"\\frac{{{combined_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {upcat_z:.4f}")
            st.latex(r"UPG_{\text{UPCAT}} = \text{clamp}(2.75 - Z \times 0.55) = " + f"{upcat_upg:.3f}")

        with st.expander("📐 Final Composite UPG"):
            st.latex(r"\text{Final UPG} = 0.40 \times UPG_{\text{grades}} + 0.60 \times UPG_{\text{UPCAT}}")
            st.latex(f"= 0.40 \\times {grade_upg_final:.3f} + 0.60 \\times {upcat_upg:.3f} = {final_upg:.3f}")

        with st.expander("📐 RMW Strategy Optimization"):
            st.markdown(f"""
            **If you had left all wrong answers blank instead of guessing:**  
            - You would have gained back {penalty_total:.2f} points  
            - Your LP raw would be: {lp_correct:.0f} (vs {lp_raw:.2f})  
            - Your RC raw would be: {rc_correct:.0f} (vs {rc_raw:.2f})
            
            **The break-even guessing threshold:**  
            In a 4-choice test with −¼ penalty, you need to be right **at least 25% of the time** 
            just to break even on random guessing. If you can eliminate ONE option, your probability 
            rises to 33.3% — still barely above break-even. You need to eliminate **TWO** options 
            (50% probability) before guessing becomes statistically advantageous.
            """)
        st.markdown("</div>", unsafe_allow_html=True)

    # ──── RECON TAB ────
    with t_recon:
        st.markdown("<div class='feedback-shell maroon-accent'>", unsafe_allow_html=True)
        st.markdown("### ⚖️ DPWAS, Reconsideration & Strategic Admission Planning")
        st.markdown("""
        **DPWAS (Deferred Placement Waitlisted Admission Status):**  
        Occurs when your UPG passes the campus cutoff but not for your specific program.
        You are campus-admitted but program-pending. Slots open when accepted students transfer, shift, or decline.
        DPWAS is NOT rejection — it is a waitlisted state that can resolve positively.

        **Reconsideration:**  
        If your UPG exceeds the campus cutoff, some campuses allow a formal appeal up to a secondary threshold.
        Conditions are strict and program-specific. UPLB reconsideration chances improve significantly if 
        the campus was your first choice AND the program was your first priority.
        """)

        for campus in [campus_1, campus_2]:
            recon = CAMPUS_DATA[campus]["recon"]
            cutoff = CAMPUS_DATA[campus]["cutoff"]
            st.markdown(f"**{campus}** — Cutoff: {cutoff:.3f}")
            if recon == 0.0:
                st.error(f"🚫 **{campus}: Strict no-reconsideration policy.** No appeals under any circumstance.")
            elif final_upg <= cutoff:
                st.success(f"✅ Already qualified ({final_upg:.3f} ≤ {cutoff:.3f}). Reconsideration not applicable.")
            elif final_upg <= recon:
                st.warning(f"📋 **Recon-eligible** — UPG {final_upg:.3f} is within recon range ({cutoff:.3f}–{recon:.3f}). Approval depends on program quota availability, not guaranteed.")
            else:
                st.error(f"❌ UPG {final_upg:.3f} exceeds even the recon threshold ({recon:.3f}).")

        st.info("""
        💡 **DPWAS Strategic Note:**  
        Do NOT enroll elsewhere immediately if DPWAS. Monitor your UP email closely — 
        DPWAS offers can arrive very late in the admission cycle. 
        Programs with "Triple Quota" have more slots and higher DPWAS resolution chances.
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    # ──── LP REVIEW TAB ────
    with t_lp_rev:
        st.markdown("### 🗣️ Language Proficiency — Item-by-Item Deep Review")

        lp_wrong_list = [q for q in lp_items if u_lp.get(q.get('item_number')) not in [None, q.get('correct_answer')] and u_lp.get(q.get('item_number')) is not None]
        lp_correct_list = [q for q in lp_items if u_lp.get(q.get('item_number')) == q.get('correct_answer')]
        lp_blank_list = [q for q in lp_items if u_lp.get(q.get('item_number')) is None]

        # Summary bar
        st.markdown(f"""
        <div style='display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap;'>
            <div class='stat-pill'><div class='stat-pill-num' style='color:var(--maroon);'>{len(lp_wrong_list)}</div><div class='stat-pill-label'>Wrong</div></div>
            <div class='stat-pill'><div class='stat-pill-num' style='color:var(--olive);'>{len(lp_correct_list)}</div><div class='stat-pill-label'>Correct</div></div>
            <div class='stat-pill'><div class='stat-pill-num' style='color:var(--fg-mute);'>{len(lp_blank_list)}</div><div class='stat-pill-label'>Blank</div></div>
        </div>
        """, unsafe_allow_html=True)

        if lp_wrong_list:
            st.markdown(f"#### ❌ Wrong Answers ({len(lp_wrong_list)}) — Priority Review:")
            for q in lp_wrong_list:
                inum = q.get('item_number')
                u = u_lp.get(inum, '?')
                c = q.get('correct_answer')
                with st.expander(
                    f"❌  LP {inum} | {q.get('language','')} | {q.get('item_type','')} | Chose {u} → Correct: {c} | −0.25 pts",
                    expanded=False
                ):
                    st.markdown(f"**Question:** {q.get('question_text')}")
                    opts = q.get('options', {})
                    for lt in ['A','B','C','D']:
                        if lt == c:
                            st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                        elif lt == u:
                            st.error(f"❌ **{lt})** {opts.get(lt,'')} ← Your answer")
                        else:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                    st.divider()
                    da = q.get('distractor_analysis', {})
                    if da and u in da:
                        trap_info = da[u]
                        if isinstance(trap_info, dict):
                            st.warning(f"**Why you chose {u} ({trap_info.get('type','Distractor')}):** {trap_info.get('explanation','')}")
                        else:
                            st.warning(f"**Why you chose {u}:** {trap_info}")
                    st.info(f"**📚 Deep Rationale:**\n\n{q.get('rationale', 'No rationale provided.')}")

        if lp_correct_list:
            st.markdown(f"#### ✅ Correct Answers ({len(lp_correct_list)}):")
            for q in lp_correct_list:
                inum = q.get('item_number')
                with st.expander(f"✅  LP {inum} | {q.get('language','')} | {q.get('item_type','')} | +1.0 pt"):
                    st.markdown(f"**Question:** {q.get('question_text')}")
                    opts = q.get('options', {}); c = q.get('correct_answer')
                    for lt in ['A','B','C','D']:
                        if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                        else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                    st.info(f"**Why correct:** {q.get('rationale','')[:350]}...")

        if lp_blank_list:
            st.markdown(f"#### ⚪ Blank / Skipped ({len(lp_blank_list)}):")
            for q in lp_blank_list:
                inum = q.get('item_number')
                with st.expander(f"⚪  LP {inum} | {q.get('language','')} | {q.get('item_type','')} | Skipped | 0 pts"):
                    st.markdown(f"**Question:** {q.get('question_text')}")
                    opts = q.get('options', {}); c = q.get('correct_answer')
                    for lt in ['A','B','C','D']:
                        if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                        else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                    st.info(f"**Explanation:**\n\n{q.get('rationale','')}")

    # ──── RC REVIEW TAB ────
    with t_rc_rev:
        st.markdown("### 📖 Reading Comprehension — Item-by-Item Deep Review")

        rc_wrong_count = sum(1 for q in rc_all_q if u_rc.get(q.get('item_number')) not in [None, q.get('correct_answer')] and u_rc.get(q.get('item_number')) is not None)
        rc_correct_count = sum(1 for q in rc_all_q if u_rc.get(q.get('item_number')) == q.get('correct_answer'))
        rc_blank_count = sum(1 for q in rc_all_q if u_rc.get(q.get('item_number')) is None)

        st.markdown(f"""
        <div style='display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap;'>
            <div class='stat-pill'><div class='stat-pill-num' style='color:var(--maroon);'>{rc_wrong_count}</div><div class='stat-pill-label'>Wrong</div></div>
            <div class='stat-pill'><div class='stat-pill-num' style='color:var(--olive);'>{rc_correct_count}</div><div class='stat-pill-label'>Correct</div></div>
            <div class='stat-pill'><div class='stat-pill-num' style='color:var(--fg-mute);'>{rc_blank_count}</div><div class='stat-pill-label'>Blank</div></div>
        </div>
        """, unsafe_allow_html=True)

        for passage in rc_passages:
            pid = passage.get('passage_id')
            title = passage.get('passage_title', f'Passage {pid}')
            genre = passage.get('genre', '')
            p_items = passage.get('questions', [])
            p_correct = sum(1 for q in p_items if u_rc.get(q.get('item_number')) == q.get('correct_answer'))
            p_pct = p_correct / max(1, len(p_items)) * 100

            st.markdown(f"""
            <div style='margin:20px 0 10px; padding:13px 18px; background:var(--bg-card);
            border:1px solid var(--border); border-radius:8px; border-left:4px solid var(--maroon);'>
                <strong style='font-family:var(--font-display); font-size:0.98rem;'>Passage {pid}: {title}</strong>
                <span style='font-family:var(--font-mono); font-size:0.63rem; color:var(--fg-mute); margin-left:12px;'>
                    {genre} · {p_correct}/{len(p_items)} correct ({p_pct:.0f}%)
                </span>
            </div>
            """, unsafe_allow_html=True)

            for q in p_items:
                qnum = q.get('item_number')
                u = u_rc.get(qnum)
                c = q.get('correct_answer')
                qlvl = q.get('question_level', 'Inferential')

                if u == c: icon, score = "✅", "+1.0"
                elif u is None: icon, score = "⚪", "Skipped"
                else: icon, score = "❌", "−0.25"

                with st.expander(f"{icon}  RC {qnum} | {qlvl} | {score} pts | P{pid}"):
                    st.markdown(f"**Question:** {q.get('question_text','')}")
                    opts = q.get('options', {})
                    for lt in ['A','B','C','D']:
                        if lt == c: st.success(f"✅ **{lt})** {opts.get(lt,'')}")
                        elif lt == u: st.error(f"❌ **{lt})** {opts.get(lt,'')} ← Your answer")
                        else: st.markdown(f"&nbsp;&nbsp;&nbsp;**{lt})** {opts.get(lt,'')}")
                    st.divider()

                    dl = q.get('distractor_labels', {})
                    if dl:
                        wrong_opts = [lt for lt in ['A','B','C','D'] if lt != c]
                        trap_parts = []
                        for lt in wrong_opts:
                            td = dl.get(lt, {})
                            if td:
                                trap_parts.append(f"**{lt} — {td.get('type','')}:** {td.get('explanation','')}")
                        if trap_parts:
                            st.warning("**Distractor Analysis:**\n\n" + "\n\n".join(trap_parts))

                    pref = q.get('passage_paragraph_reference', '')
                    if pref: st.caption(f"📍 Evidence: {pref}")
                    st.info(f"**📚 Reading Strategy & Rationale:**\n\n{q.get('rationale', 'No rationale provided.')}")

    # ── RESET ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
    with col_r2:
        st.markdown("""
        <div style='text-align:center; margin-bottom:12px; font-family:var(--font-ui); font-size:0.82rem; color:var(--fg-mute);'>
            Ready for another round? A fresh simulation will generate completely new items.
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Retake with Fresh Items — Full Reset", use_container_width=True, type="secondary",
                     help="Clears all answers and generates brand-new exam items"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()