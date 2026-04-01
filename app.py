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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root {{
  --bg0:#070b12;--bg1:#0e1520;--bg2:#141d2e;--bg3:#1a2540;
  --blue:#4d9fff;--teal:#2dd4bf;--green:#34d399;--amber:#fbbf24;--red:#f87171;--purple:#a78bfa;
  --blue-dim:rgba(77,159,255,0.10);--teal-dim:rgba(45,212,191,0.10);
  --green-dim:rgba(52,211,153,0.10);--amber-dim:rgba(251,191,36,0.10);--red-dim:rgba(248,113,113,0.10);
  --fg0:#f0f4f8;--fg1:#9aaabb;--fg2:#5a6a7a;
  --border:rgba(255,255,255,0.06);--border2:rgba(255,255,255,0.12);
  --r:8px;--r2:12px;--r3:16px;
  --font-display:'Syne',sans-serif;--font-body:'Source Serif 4',Georgia,serif;--font-mono:'IBM Plex Mono',monospace;
  --fs:{fs};--shadow:0 4px 24px rgba(0,0,0,0.5);--shadow2:0 8px 40px rgba(0,0,0,0.7);
  --t:0.18s cubic-bezier(0.4,0,0.2,1);
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
.stApp,body{{background:var(--bg0)!important;color:var(--fg0)!important;font-family:var(--font-body)!important;font-size:var(--fs)!important;}}
#MainMenu,footer,header{{visibility:hidden;}}
.block-container{{padding-top:1.5rem!important;padding-bottom:6rem!important;max-width:1380px!important;}}
h1,h2,h3,h4,h5,h6{{font-family:var(--font-display)!important;color:var(--fg0)!important;letter-spacing:-0.02em!important;}}

/* Sidebar */
section[data-testid="stSidebar"]{{background:var(--bg1)!important;border-right:1px solid var(--border)!important;}}
section[data-testid="stSidebar"] *{{color:var(--fg1)!important;}}
section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] h4,section[data-testid="stSidebar"] strong,section[data-testid="stSidebar"] label{{color:var(--fg0)!important;font-family:var(--font-display)!important;}}
section[data-testid="stSidebar"] input,section[data-testid="stSidebar"] select,section[data-testid="stSidebar"] textarea{{background:var(--bg2)!important;border:1px solid var(--border2)!important;color:var(--fg0)!important;border-radius:var(--r)!important;font-family:var(--font-mono)!important;font-size:0.82rem!important;}}
section[data-testid="stSidebar"] [data-baseweb="select"]>div{{background:var(--bg2)!important;border-color:var(--border2)!important;color:var(--fg0)!important;}}
section[data-testid="stSidebar"] [data-baseweb="select"] *{{color:var(--fg0)!important;background:var(--bg2)!important;}}
[data-baseweb="popover"] *{{background:var(--bg3)!important;color:var(--fg0)!important;border-color:var(--border2)!important;}}

/* Buttons */
.stButton>button{{font-family:var(--font-display)!important;font-weight:700!important;font-size:0.82rem!important;letter-spacing:0.04em!important;text-transform:uppercase!important;border-radius:var(--r)!important;transition:all var(--t)!important;min-height:42px!important;}}
.stButton>button[kind="primary"]{{background:linear-gradient(135deg,#1a56db 0%,var(--blue) 100%)!important;border:none!important;color:#fff!important;box-shadow:0 0 0 1px rgba(77,159,255,0.3),0 4px 16px rgba(26,86,219,0.5)!important;}}
.stButton>button[kind="primary"]:hover{{transform:translateY(-2px)!important;box-shadow:0 0 0 1px rgba(77,159,255,0.5),0 8px 24px rgba(26,86,219,0.6)!important;}}
.stButton>button[kind="secondary"]{{background:var(--bg2)!important;border:1px solid var(--border2)!important;color:var(--fg1)!important;}}
.stButton>button[kind="secondary"]:hover{{background:var(--bg3)!important;border-color:var(--blue)!important;color:var(--fg0)!important;}}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{{gap:2px;background:var(--bg1);border:1px solid var(--border)!important;border-radius:var(--r2);padding:4px;flex-wrap:wrap;}}
.stTabs [data-baseweb="tab"]{{font-family:var(--font-display)!important;font-size:0.75rem!important;font-weight:700!important;letter-spacing:0.05em!important;text-transform:uppercase!important;padding:7px 14px!important;border-radius:var(--r)!important;background:transparent!important;color:var(--fg2)!important;border:none!important;transition:all var(--t)!important;}}
.stTabs [aria-selected="true"]{{background:var(--bg3)!important;color:var(--blue)!important;}}

/* Radio — CRITICAL: must be clean for KaTeX to render */
.stRadio>label{{display:none!important;}}
.stRadio [data-testid="stWidgetLabel"]{{display:none!important;}}
.stRadio>div{{display:flex!important;flex-direction:column!important;gap:6px!important;}}
.stRadio>div>label{{
  background:var(--bg2)!important;border:1.5px solid var(--border2)!important;
  border-radius:var(--r)!important;padding:12px 16px!important;
  cursor:pointer!important;transition:all var(--t)!important;
  font-family:var(--font-body)!important;font-size:var(--fs)!important;
  line-height:1.7!important;color:var(--fg0)!important;
  display:flex!important;align-items:flex-start!important;gap:8px!important;
}}
.stRadio>div>label:hover{{border-color:var(--blue)!important;background:var(--blue-dim)!important;transform:translateX(3px)!important;}}
.stRadio>div>label[data-checked="true"]{{border-color:var(--blue)!important;background:var(--blue-dim)!important;}}
/* KaTeX in radio options */
.stRadio>div>label .katex,.stRadio>div>label .katex *{{color:var(--fg0)!important;}}
.stRadio>div>label .katex-display{{display:inline!important;}}

/* Expanders */
.streamlit-expanderHeader{{background:var(--bg2)!important;border:1px solid var(--border2)!important;border-radius:var(--r)!important;color:var(--fg0)!important;font-family:var(--font-display)!important;font-size:0.82rem!important;font-weight:700!important;letter-spacing:0.04em!important;text-transform:uppercase!important;min-height:44px!important;padding:0 14px!important;}}
.streamlit-expanderContent{{background:var(--bg1)!important;border:1px solid var(--border)!important;border-top:none!important;border-radius:0 0 var(--r) var(--r)!important;padding:16px!important;}}

/* Textarea */
.stTextArea textarea{{background:var(--bg2)!important;border:1px solid var(--border2)!important;color:var(--fg0)!important;border-radius:var(--r)!important;font-family:var(--font-mono)!important;font-size:0.82rem!important;line-height:1.7!important;}}
.stTextArea textarea:focus{{border-color:var(--blue)!important;box-shadow:0 0 0 2px rgba(77,159,255,0.2)!important;}}

/* Alerts / Metrics / Select */
.stAlert{{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;color:var(--fg0)!important;}}
.stSelectbox>div>div,.stNumberInput>div>div>input{{background:var(--bg2)!important;border-color:var(--border2)!important;color:var(--fg0)!important;border-radius:var(--r)!important;font-family:var(--font-mono)!important;}}
[data-testid="metric-container"]{{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;padding:16px!important;}}
[data-testid="metric-container"] label{{color:var(--fg2)!important;font-size:0.72rem!important;font-family:var(--font-display)!important;text-transform:uppercase!important;letter-spacing:0.08em!important;}}
[data-testid="metric-container"] [data-testid="stMetricValue"]{{color:var(--blue)!important;font-family:var(--font-display)!important;font-size:1.6rem!important;}}
.stCheckbox label span{{color:var(--fg1)!important;font-family:var(--font-display)!important;font-size:0.82rem!important;}}

/* ── Custom Components ── */
.hero{{position:relative;background:linear-gradient(145deg,#070b12 0%,#0c1628 50%,#071420 100%);border:1px solid var(--border2);border-radius:20px;overflow:hidden;margin-bottom:24px;box-shadow:var(--shadow2);}}
.hero-glow-l{{position:absolute;width:500px;height:500px;border-radius:50%;top:-150px;left:-100px;background:radial-gradient(circle,rgba(77,159,255,0.08) 0%,transparent 70%);pointer-events:none;}}
.hero-glow-r{{position:absolute;width:400px;height:400px;border-radius:50%;bottom:-100px;right:-50px;background:radial-gradient(circle,rgba(45,212,191,0.07) 0%,transparent 70%);pointer-events:none;}}
.hero-inner{{position:relative;z-index:2;padding:48px 56px 40px;}}
.hero-eyebrow{{font-family:var(--font-mono);font-size:0.6rem;font-weight:600;letter-spacing:0.25em;text-transform:uppercase;color:var(--blue);background:rgba(77,159,255,0.1);border:1px solid rgba(77,159,255,0.2);padding:4px 12px;border-radius:20px;display:inline-block;margin-bottom:20px;}}
.hero-title{{font-family:var(--font-display)!important;font-size:clamp(2rem,4vw,3.4rem)!important;font-weight:800!important;line-height:1.05!important;letter-spacing:-0.03em!important;color:#fff!important;margin-bottom:16px!important;}}
.hero-title .accent{{color:var(--blue);}} .hero-title .accent2{{color:var(--teal);}}
.hero-sub{{font-family:var(--font-body);font-size:0.9rem;line-height:1.8;color:rgba(255,255,255,0.45);max-width:640px;margin-bottom:28px;}}
.hero-rule{{height:1px;background:linear-gradient(90deg,rgba(77,159,255,0.3),transparent);margin-bottom:24px;}}
.hero-stats{{display:flex;gap:36px;flex-wrap:wrap;}}
.hs-num{{font-family:var(--font-display);font-size:1.8rem;font-weight:800;color:var(--blue);line-height:1;}}
.hs-lbl{{font-family:var(--font-mono);font-size:0.58rem;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.12em;margin-top:4px;}}

.sec-title{{font-family:var(--font-display)!important;font-size:0.72rem!important;font-weight:700!important;letter-spacing:0.2em!important;text-transform:uppercase!important;color:var(--fg2)!important;display:flex;align-items:center;gap:10px;margin:28px 0 14px;}}
.sec-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
.notice{{display:flex;gap:12px;background:var(--bg2);border:1px solid var(--border2);border-left:3px solid var(--blue);border-radius:var(--r);padding:12px 16px;font-family:var(--font-body);font-size:0.84rem;color:var(--fg1);line-height:1.7;margin-bottom:14px;}}
.notice.warn{{border-left-color:var(--amber);}} .notice.sci{{border-left-color:var(--teal);}}
.notice.red{{border-left-color:var(--red);}} .notice.green{{border-left-color:var(--green);}}
.notice strong{{color:var(--fg0);}} .ni{{font-size:1rem;flex-shrink:0;margin-top:1px;}}

.comp-wrap{{background:var(--bg1);border:1px solid var(--border2);border-radius:var(--r2);padding:16px 20px;margin-bottom:12px;}}
.comp-wrap.math{{border-top:2px solid var(--blue);}} .comp-wrap.sci{{border-top:2px solid var(--teal);}}
.comp-head{{font-family:var(--font-display);font-size:0.85rem;font-weight:700;color:var(--fg0);margin-bottom:4px;}}
.comp-sub{{font-family:var(--font-mono);font-size:0.62rem;color:var(--fg2);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;}}

/* Question card */
.q-card{{background:var(--bg1);border:1px solid var(--border);border-left:3px solid var(--blue);border-radius:var(--r2);padding:20px 24px 10px;margin-bottom:14px;transition:box-shadow var(--t);scroll-margin-top:80px;}}
.q-card.sci{{border-left-color:var(--teal);}} .q-card.answered{{border-left-color:var(--green);}} .q-card.flagged{{border-left-color:var(--amber);}}
.q-card:hover{{box-shadow:0 4px 20px rgba(0,0,0,0.4);}}
.q-meta{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:14px;}}
.q-badge{{font-family:var(--font-mono);font-size:0.58rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;padding:3px 9px;border-radius:4px;display:inline-block;white-space:nowrap;}}
.q-badge.math{{color:var(--blue);background:var(--blue-dim);border:1px solid rgba(77,159,255,0.2);}}
.q-badge.sci{{color:var(--teal);background:var(--teal-dim);border:1px solid rgba(45,212,191,0.2);}}
.q-badge.tag{{color:var(--fg2);background:var(--bg3);border:1px solid var(--border2);}}
.q-badge.flag{{color:var(--amber);background:var(--amber-dim);border:1px solid rgba(251,191,36,0.2);}}
.q-badge.ok{{color:var(--green);background:var(--green-dim);border:1px solid rgba(52,211,153,0.2);}}

/* Science stimuli */
.stim-passage{{background:var(--bg2);border:1px solid var(--border2);border-left:3px solid var(--teal);border-radius:var(--r);padding:14px 18px;margin-bottom:14px;font-family:var(--font-body);font-size:0.875rem;line-height:1.85;color:var(--fg1);}}
.stim-data{{background:var(--bg2);border:1px solid var(--border2);border-left:3px solid var(--amber);border-radius:var(--r);padding:14px 18px;margin-bottom:14px;font-size:0.78rem;line-height:1.7;color:var(--fg1);overflow-x:auto;}}
.stim-diagram{{background:var(--bg2);border:1px solid var(--border2);border-left:3px solid var(--purple);border-radius:var(--r);padding:14px 18px;margin-bottom:14px;font-family:var(--font-mono);font-size:0.78rem;line-height:1.7;color:var(--fg1);overflow-x:auto;}}
.stim-label{{font-family:var(--font-mono);font-size:0.58rem;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:8px;display:block;font-weight:600;}}
.stim-label.p{{color:var(--teal);}} .stim-label.d{{color:var(--amber);}} .stim-label.g{{color:var(--purple);}}
.sci-tbl{{width:100%;border-collapse:collapse;margin-top:6px;font-size:0.82rem;}}
.sci-tbl th{{background:var(--bg3);color:var(--fg0);padding:8px 12px;text-align:left;border-bottom:1px solid var(--border2);font-size:0.72rem;font-family:var(--font-display);}}
.sci-tbl td{{padding:7px 12px;border-bottom:1px solid var(--border);color:var(--fg1);}}
.sci-tbl tr:last-child td{{border-bottom:none;}} .sci-tbl tr:hover td{{background:var(--bg3);}}

/* Navigator */
.nav-box{{background:var(--bg1);border:1px solid var(--border2);border-radius:var(--r2);padding:14px 18px;margin-bottom:18px;position:sticky;top:10px;z-index:99;box-shadow:var(--shadow);}}
.nav-title{{font-family:var(--font-mono);font-size:0.58rem;letter-spacing:0.14em;text-transform:uppercase;color:var(--fg2);margin-bottom:10px;}}
.nav-grid{{display:flex;flex-wrap:wrap;gap:4px;}}
.nav-dot{{min-width:32px;height:28px;border-radius:5px;display:inline-flex;align-items:center;justify-content:center;font-family:var(--font-mono);font-size:0.6rem;font-weight:600;cursor:pointer;background:var(--bg3);color:var(--fg2);border:1px solid var(--border);transition:all var(--t);}}
.nav-dot:hover{{border-color:var(--blue);color:var(--blue);transform:scale(1.1);}}
.nav-dot.am{{background:var(--blue-dim);color:var(--blue);border-color:rgba(77,159,255,0.3);}}
.nav-dot.as{{background:var(--teal-dim);color:var(--teal);border-color:rgba(45,212,191,0.3);}}
.nav-dot.fl{{background:var(--amber-dim);color:var(--amber);border-color:rgba(251,191,36,0.3);}}

/* Progress */
.pbar-wrap{{margin-bottom:12px;}}
.pbar-row{{display:flex;justify-content:space-between;font-family:var(--font-mono);font-size:0.6rem;color:var(--fg2);margin-bottom:5px;}}
.pbar-track{{height:4px;background:var(--bg3);border-radius:2px;overflow:hidden;}}
.pbar-fill-m{{height:100%;border-radius:2px;background:linear-gradient(90deg,#1a56db,var(--blue));transition:width 0.5s ease;}}
.pbar-fill-s{{height:100%;border-radius:2px;background:linear-gradient(90deg,#0d6b63,var(--teal));transition:width 0.5s ease;}}

/* Timer */
.timer{{position:fixed;top:16px;right:20px;z-index:99999;font-family:var(--font-mono);font-size:0.95rem;font-weight:600;padding:8px 18px;border-radius:24px;border:1px solid rgba(77,159,255,0.3);background:var(--bg1);color:var(--blue);box-shadow:var(--shadow);letter-spacing:0.06em;}}
.timer.s{{color:var(--teal);border-color:rgba(45,212,191,0.3);}} .timer.w{{color:var(--amber);}} .timer.d{{color:var(--red);animation:pulse 1s infinite;}}
@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:0.6;}}}}

/* Stat row */
.stat-row{{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0;}}
.stat-pill{{background:var(--bg2);border:1px solid var(--border2);border-radius:var(--r);padding:12px 18px;flex:1;min-width:90px;text-align:center;}}
.sp-n{{font-family:var(--font-display);font-size:1.6rem;font-weight:800;line-height:1;}}
.sp-l{{font-family:var(--font-mono);font-size:0.55rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--fg2);margin-top:4px;}}

/* Results */
.res-hero{{background:linear-gradient(145deg,#070b12,#0c1628,#071420);border:1px solid var(--border2);border-radius:20px;padding:52px 48px;text-align:center;position:relative;overflow:hidden;margin-bottom:24px;box-shadow:var(--shadow2);}}
.res-hero-glow{{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(77,159,255,0.07) 0%,transparent 65%);pointer-events:none;}}
.upg-label{{font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.25em;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:10px;position:relative;z-index:1;}}
.upg-val{{font-family:var(--font-display);font-size:clamp(4rem,9vw,7rem);font-weight:800;line-height:1;position:relative;z-index:1;letter-spacing:-0.04em;}}
.upg-verdict{{font-family:var(--font-body);font-size:1rem;color:rgba(255,255,255,0.5);margin-top:12px;position:relative;z-index:1;}}
.upg-cards{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px;}}
.upg-card{{background:var(--bg1);border:1px solid var(--border2);border-radius:var(--r2);padding:22px 26px;}}
.upg-card.m{{border-top:2px solid var(--blue);}} .upg-card.s{{border-top:2px solid var(--teal);}}
.upg-card-title{{font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.16em;text-transform:uppercase;margin-bottom:10px;}}
.upg-card.m .upg-card-title{{color:var(--blue);}} .upg-card.s .upg-card-title{{color:var(--teal);}}
.upg-card-val{{font-family:var(--font-display);font-size:2.8rem;font-weight:800;line-height:1;margin-bottom:6px;}}
.upg-card.m .upg-card-val{{color:var(--blue);}} .upg-card.s .upg-card-val{{color:var(--teal);}}
.upg-card-sub{{font-family:var(--font-body);font-size:0.8rem;color:var(--fg1);}}
.upg-br{{margin-top:14px;}}
.upg-br-row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-family:var(--font-body);font-size:0.8rem;}}
.upg-br-row:last-child{{border-bottom:none;}} .upg-br-lbl{{color:var(--fg1);}} .upg-br-val{{font-family:var(--font-mono);font-weight:600;font-size:0.78rem;}}
.score-panel{{background:var(--bg1);border:1px solid var(--border2);border-radius:var(--r2);padding:20px 24px;}}
.score-panel h4{{font-family:var(--font-display)!important;font-size:0.85rem!important;font-weight:700!important;letter-spacing:0.08em!important;text-transform:uppercase!important;margin-bottom:14px!important;padding-bottom:12px!important;border-bottom:1px solid var(--border)!important;}}
.s-row{{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border);font-family:var(--font-body);font-size:0.84rem;}}
.s-row:last-child{{border-bottom:none;}} .s-lbl{{color:var(--fg1);}} .s-val{{font-family:var(--font-mono);font-weight:600;font-size:0.8rem;}}
.s-val.c{{color:var(--green);}} .s-val.w{{color:var(--red);}} .s-val.g{{color:var(--blue);}}
.heat-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px;}}
.heat-row{{display:flex;align-items:center;gap:8px;font-family:var(--font-body);font-size:0.75rem;padding:7px 10px;border-radius:var(--r);border:1px solid var(--border);background:var(--bg2);}}
.heat-bar-out{{flex:1;height:4px;background:var(--bg3);border-radius:2px;overflow:hidden;}}
.heat-bar-in{{height:100%;border-radius:2px;transition:width 0.8s ease;}}
.heat-bar-in.hi{{background:var(--green);}} .heat-bar-in.mid{{background:var(--amber);}} .heat-bar-in.lo{{background:var(--red);}}
.heat-pct{{font-family:var(--font-mono);font-size:0.58rem;font-weight:700;min-width:32px;text-align:right;}}
.ir-c{{background:var(--green-dim);border:1px solid rgba(52,211,153,0.25);border-radius:var(--r);padding:10px 14px;margin:4px 0;font-size:var(--fs);color:var(--green);}}
.ir-w{{background:var(--red-dim);border:1px solid rgba(248,113,113,0.25);border-radius:var(--r);padding:10px 14px;margin:4px 0;font-size:var(--fs);color:var(--red);}}
.ir-o{{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);padding:10px 14px;margin:4px 0;font-size:var(--fs);color:var(--fg1);}}
.campus-card{{background:var(--bg1);border:1px solid var(--border2);border-radius:var(--r2);overflow:hidden;margin-bottom:14px;}}
.campus-hdr{{padding:14px 20px;background:linear-gradient(135deg,#0a2a16,#0d3820);border-bottom:1px solid var(--border2);}}
.campus-hdr.fail{{background:linear-gradient(135deg,#2a0a0a,#3a1010);}}
.campus-hdr h4{{color:var(--fg0)!important;font-size:0.95rem!important;margin-bottom:3px!important;}}
.campus-hdr p{{color:var(--fg1)!important;font-family:var(--font-mono);font-size:0.62rem!important;}}
.campus-body{{padding:14px 20px;}}
.prog-row{{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--border);font-family:var(--font-body);font-size:0.84rem;}}
.prog-row:last-child{{border-bottom:none;}}
.prog-name{{font-weight:600;color:var(--fg0);font-family:var(--font-display);}}
.prog-sub{{font-family:var(--font-mono);font-size:0.58rem;color:var(--fg2);margin-top:2px;}}
.badge{{font-family:var(--font-mono);font-size:0.6rem;font-weight:700;padding:3px 10px;border-radius:4px;}}
.badge.pass{{color:var(--green);background:var(--green-dim);border:1px solid rgba(52,211,153,0.25);}}
.badge.risk{{color:var(--amber);background:var(--amber-dim);border:1px solid rgba(251,191,36,0.25);}}
.badge.fail{{color:var(--red);background:var(--red-dim);border:1px solid rgba(248,113,113,0.25);}}
.chart-wrap{{background:var(--bg2);border:1px solid var(--border2);border-radius:var(--r2);padding:8px;margin:12px 0;}}
@media(max-width:768px){{.hero-inner{{padding:28px 24px;}}.upg-cards{{grid-template-columns:1fr;}}.heat-grid{{grid-template-columns:1fr;}}}}
@media print{{section[data-testid="stSidebar"],.timer,.stButton{{display:none!important;}}}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition-duration:0.01ms!important;}}}}
</style>
""", unsafe_allow_html=True)

# ── KaTeX: robust loader with MutationObserver re-render ──
st.components.v1.html("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<script>
(function(){
  var OPTS={
    delimiters:[
      {left:'$$',right:'$$',display:true},
      {left:'$',right:'$',display:false}
    ],
    throwOnError:false,
    strict:false,
    trust:true,
    fleqn:false
  };
  function renderAll(){
    try{if(window.renderMathInElement&&document.body)renderMathInElement(document.body,OPTS);}
    catch(e){}
  }
  // First render
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(renderAll,300);});
  else setTimeout(renderAll,300);
  // Re-render on Streamlit DOM updates
  var last=0;
  var obs=new MutationObserver(function(muts){
    var now=Date.now();
    if(now-last<150)return;
    var changed=muts.some(function(m){return m.addedNodes.length>0;});
    if(changed){last=now;setTimeout(renderAll,100);}
  });
  obs.observe(document.body,{childList:true,subtree:true});
  window.reRenderKaTeX=renderAll;
})();
</script>
""", height=0)

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
        "Single Quota": ["BA Communication"], "Less Popular": ["BA Arts & Humanities"]
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
        "Triple Quota": [], "Double Quota": [],
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
        if program in plist: return tier
    return "Less Popular"

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style='background:linear-gradient(135deg,var(--bg1),var(--bg2));border-bottom:1px solid var(--border);padding:24px 20px 20px;text-align:center;'>
      <div style='font-family:var(--font-display);font-size:1.15rem;font-weight:800;color:var(--fg0);letter-spacing:-0.02em;margin-bottom:4px;'>PADAYON!</div>
      <div style='font-family:var(--font-mono);font-size:0.55rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--fg2);'>UPCAT Sci + Math · 2026</div>
    </div>""", unsafe_allow_html=True)

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
        g8_math=st.number_input("G8 Math",60.0,100.0,87.0,0.5); g9_math=st.number_input("G9 Math",60.0,100.0,87.0,0.5)
        g10_math=st.number_input("G10 Math",60.0,100.0,88.0,0.5); g11_precalc=st.number_input("Pre-Calculus",60.0,100.0,88.0,0.5)
    with c2:
        g11_calc=st.number_input("Basic Calculus",60.0,100.0,87.0,0.5); g11_stats=st.number_input("Stats & Prob",60.0,100.0,88.0,0.5)
        g11_genmath=st.number_input("Gen. Math",60.0,100.0,88.0,0.5)

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">🔬 Science Grades G8–G11</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        g8_sci=st.number_input("G8 Science",60.0,100.0,87.0,0.5); g9_sci=st.number_input("G9 Science",60.0,100.0,87.0,0.5)
        g10_sci=st.number_input("G10 Science",60.0,100.0,88.0,0.5); g11_bio1=st.number_input("Gen Bio 1",60.0,100.0,88.0,0.5)
    with c4:
        g11_bio2=st.number_input("Gen Bio 2",60.0,100.0,88.0,0.5); g11_earth=st.number_input("Earth Sci",60.0,100.0,87.0,0.5)

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">🎯 Campus & Programs</div>', unsafe_allow_html=True)
    campus_1 = st.selectbox("1st Choice Campus", list(CAMPUS_DATA.keys()), index=0)
    c1_p1=st.selectbox("Priority 1", get_all_programs(campus_1), key="c1p1")
    c1_p2=st.selectbox("Priority 2", get_all_programs(campus_1), key="c1p2")
    c1_p3=st.selectbox("Priority 3", get_all_programs(campus_1), key="c1p3")
    campus_2 = st.selectbox("2nd Choice Campus", list(CAMPUS_DATA.keys()), index=2)
    c2_p1=st.selectbox("Priority 1", get_all_programs(campus_2), key="c2p1")
    c2_p2=st.selectbox("Priority 2", get_all_programs(campus_2), key="c2p2")
    c2_p3=st.selectbox("Priority 3", get_all_programs(campus_2), key="c2p3")

    st.markdown('<div class="sec-title" style="margin:14px 0 10px;padding-left:12px;font-size:0.6rem;">⚙️ Parameters</div>', unsafe_allow_html=True)
    math_items = st.slider("Math Items", 10, 50, 20, 5)
    sci_items  = st.slider("Science Items", 10, 45, 15, 5)
    difficulty = st.select_slider("Difficulty", options=["Standard","Competitive","Brutal","Massacre"], value="Competitive")

# ==========================================
# DIFFICULTY
# ==========================================
DIFF_MAP = {
    "Standard":    ("Standard difficulty. Items are solvable in under 60 seconds with basic high school knowledge. No multi-step algebra traps.", 0.52, 0.16),
    "Competitive": ("Competitive difficulty (~top 20%). Items require 2–3 clear reasoning steps. Distractors are common student errors.", 0.44, 0.15),
    "Brutal":      ("Brutal difficulty (~top 8%). Items are conceptually deep. Non-obvious approach required. Strong distractors.", 0.37, 0.14),
    "Massacre":    ("Massacre difficulty (~top 2–3%). Items appear simple but require precise reasoning. Zero solvable by rote recall alone.", 0.31, 0.13),
}
diff_instruction, MEAN_BASELINE, SIGMA = DIFF_MAP[difficulty]

# ==========================================
# SVG CHARTS
# ==========================================
def generate_bar_svg(labels, values, title="", color="#4d9fff", width=480, height=250):
    if not labels or not values: return ""
    max_v = max(values) if max(values) > 0 else 1
    ml,mr,mt,mb = 52,18,36,55
    cw=width-ml-mr; ch=height-mt-mb
    bw=cw/len(values)*0.62; bg=cw/len(values)
    p=[f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#141d2e;border-radius:8px;">',
       f'<rect width="{width}" height="{height}" fill="#141d2e" rx="8"/>']
    if title: p.append(f'<text x="{(width-mr)//2}" y="20" text-anchor="middle" fill="#9aaabb" font-size="11" font-family="IBM Plex Mono,monospace" font-weight="600">{title[:55]}</text>')
    for i in range(5):
        yv=max_v*i/4; yp=mt+ch-(yv/max_v*ch)
        p.append(f'<line x1="{ml}" y1="{yp:.1f}" x2="{ml+cw}" y2="{yp:.1f}" stroke="#1a2540" stroke-width="1"/>')
        p.append(f'<text x="{ml-4}" y="{yp+4:.1f}" text-anchor="end" fill="#5a6a7a" font-size="9" font-family="IBM Plex Mono,monospace">{yv:.2g}</text>')
    for i,(lbl,val) in enumerate(zip(labels,values)):
        bh=(val/max_v)*ch; x=ml+i*bg+(bg-bw)/2; y=mt+ch-bh
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" opacity="0.85" rx="2"/>')
        p.append(f'<text x="{x+bw/2:.1f}" y="{y-4:.1f}" text-anchor="middle" fill="#f0f4f8" font-size="9" font-family="IBM Plex Mono,monospace" font-weight="600">{val:.2g}</text>')
        lbl_s=str(lbl)[:9]
        p.append(f'<text x="{x+bw/2:.1f}" y="{mt+ch+13:.1f}" text-anchor="middle" fill="#9aaabb" font-size="9" font-family="IBM Plex Mono,monospace" transform="rotate(-22,{x+bw/2:.1f},{mt+ch+13:.1f})">{lbl_s}</text>')
    p.append('</svg>'); return "".join(p)

def build_chart(cd):
    if not cd or not isinstance(cd,dict): return ""
    try:
        t=cd.get("type","bar")
        if t=="bar": return generate_bar_svg(cd.get("labels",[]),cd.get("values",[]),cd.get("title",""),cd.get("color","#4d9fff"))
    except Exception: pass
    return ""

# ==========================================
# JSON CLEANER — never touch backslashes
# ==========================================
# ==========================================
# JSON CLEANER — THE MATH VACCINE
# ==========================================
# ==========================================
# JSON CLEANER & MARKDOWN SAFEGUARD
# ==========================================
def safe_md(text):
    """Protects Math/LaTeX backslashes from being eaten by Streamlit"""
    if not text: return ""
    return str(text).replace('\\', '\\\\')

def clean_json(raw: str) -> str:
    """High-Precision JSON Extractor for LaTeX and Math Symbols"""
    import re
    s = raw.strip()
    # 1. Remove Markdown fences
    s = re.sub(r'^```(?:json)?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*```$', '', s)
    
    # 2. Extract outermost { }
    start = s.find('{')
    end = s.rfind('}')
    if start != -1 and end != -1:
        s = s[start:end+1]
        
    # 3. CRITICAL: Protect backslashes for Math/LaTeX
    # This prevents the parser from eating the '\' in \frac
    s = s.replace('\\', '\\\\')
    # Restore standard JSON escapes that we accidentally doubled
    s = s.replace('\\\\"', '\\"')
    s = s.replace('\\\\n', '\\n')
    return s.strip()

def esc_html(s: str) -> str:
    """HTML-escape user strings to prevent injection."""
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def post_process(items):
    for q in items:
        # Correct answer: single uppercase letter
        ca = str(q.get('correct_answer','')).strip().upper()
        q['correct_answer'] = ca[0] if ca and ca[0] in 'ABCD' else 'A'
        # Options: strip accidental "A) " prefixes the AI sometimes adds
        for k in ['A','B','C','D']:
            opt = str(q.get('options',{}).get(k,''))
            opt = re.sub(r'^[A-D][)\.\:]\s*', '', opt.strip())
            q.setdefault('options',{})[k] = opt
        # question_text must be str
        if not isinstance(q.get('question_text'), str):
            q['question_text'] = str(q.get('question_text',''))
    return items

# ==========================================
# PROMPTS
# ==========================================
MATH_SYSTEM = """You are a senior UPCAT Mathematics item writer for the University of the Philippines Office of Admissions.

LANGUAGE: ALL questions and options MUST be written in ENGLISH. No Filipino/Tagalog in question stems or options.

LATEX RULES — ABSOLUTE:
- Wrap ALL math in dollar signs. Inline: $...$  Display (centered): $$...$$
- Fractions: $\\frac{a}{b}$ — NEVER write "a/b" for fractions in math context
- Square roots: $\\sqrt{x}$, $\\sqrt[3]{x}$ — NEVER write "sqrt(x)"
- Exponents: $x^{2}$, $2^{10}$
- Absolute value: $|x|$
- Repeating decimal: $0.\\overline{36}$
- Set notation: $\\mathbb{Z}$, $\\mathbb{R}$, $\\mathbb{Q}$, $\\mathbb{N}$
- Greek: $\\pi$, $\\theta$, $\\alpha$, $\\beta$, $\\Delta$
- Special: $\\leq$, $\\geq$, $\\neq$, $\\approx$, $\\infty$, $\\pm$
- Every option that contains a number or expression MUST use LaTeX: "$15$" not "15"
- NEVER mix plain text math with LaTeX in the same expression

UPCAT MATH STYLE:
- Items must be solvable in 60-90 seconds WITHOUT a calculator
- No multi-page computations. Max 3-4 arithmetic steps.
- JHS algebra dominates: linear equations, factoring, quadratics, geometry, word problems
- Word problems should use realistic Philippine contexts (jeepney fares, land areas, age problems)
- Distractors must be the result of specific named errors (SIGN_ERROR, ARITHMETIC_ERROR, FORMULA_CONFUSION, CONCEPTUAL_ERROR, INCOMPLETE_SOLUTION)
- Options must be parallel in form and similar in length — no obvious outliers
- Correct answer must be defensible from the question alone

THE "ALIEN ITEM" ILLUSION PROTOCOL (30% of questions):
- Inject "Alien Items": These are questions masked in highly intimidating, seemingly out-of-coverage, or bizarre scenarios. 
- Use intimidating numbers (e.g., $2026^2 - 2025^2$, $10^{99} - 1$, nested infinite radicals, fractional exponents of massive bases).
- Use distinct, wide-ranging contexts (e.g., cryptography algorithms, orbital mechanics, abstract economics).
- THE CATCH: The mathematical complexity MUST be an illusion. The item must collapse into a beautifully simple K-12 concept (like difference of two squares, exponent rules, similar triangles, or factoring) that can be solved mentally in under 90 seconds.
- DO NOT make it overly absurd or unsolvable. It must strictly map to the given competencies.

STRICT PSYCHOMETRIC TRIFECTA STANDARDS:
1. VALIDITY: The item must measure EXACTLY the mathematical competency required, not the student's reading comprehension or patience for long division.
2. RELIABILITY: The difficulty must be consistent. A student with strong algebraic foundations will instantly see the "shortcut" trick, while an unprepared student will try to calculate it manually and fail/run out of time.
3. OBJECTIVITY: There is only ONE mathematically undeniable correct answer. Distractors must be the exact values obtained if a student falls for the illusion (e.g., computing normally and making an arithmetic error, or applying the wrong shortcut).


OUTPUT: Return ONLY valid JSON. No markdown fences. No text before or after."""

SCI_SYSTEM = """You are a senior UPCAT Science item writer for the University of the Philippines Office of Admissions.

LANGUAGE: ALL questions, stimuli, and options MUST be written in ENGLISH. No Filipino/Tagalog.

STIMULUS RULES:
- 60%+ of items must have a stimulus (TEXT_PASSAGE, DATA_TABLE, or DIAGRAM)
- DATA_TABLE: use ONLY this exact HTML format (no extra attributes):
  <table class="sci-tbl"><thead><tr><th>Col1 (unit)</th><th>Col2 (unit)</th></tr></thead><tbody><tr><td>val</td><td>val</td></tr></tbody></table>
- TEXT_PASSAGE: 60-120 words, scientific scenario or experimental setup
- DIAGRAM: clear ASCII or labeled text diagram

UPCAT SCIENCE STYLE:
- Test APPLICATION and ANALYSIS, not pure memorization
- Passage-based items: the answer must require reading the stimulus, not just recall
- Distractors represent real student misconceptions (MISCONCEPTION, PARTIAL_TRUTH, REVERSED_CAUSATION, SCOPE_ERROR, MAGNIFIED_DETAIL)
- Chemical formulas in LaTeX: $H_2O$, $CO_2$, $O_2$, $NaCl$
- No heavy stoichiometry calculations — conceptual chemistry only
- Disciplines: Biology ~35%, Earth Science ~25%, Chemistry ~22%, Physics ~18%
- JHS topics (~70%) dominate; SHS topics (~30%) appear mainly in passages

- CRITICAL: Never omit curly braces in LaTeX. Always write \frac{a}{b}, never \fracab.
- Always put a space after a LaTeX command if it's followed by a variable. 
- Example: \cos (5x) is better than \cos(5x).

THE "ALIEN ITEM" ILLUSION PROTOCOL (30% of questions):
- Inject "Alien Items": Wrap basic K-12 science competencies in highly intimidating, alien, or niche scientific contexts.
- Wide Contexts & Vocabulary: Use deep-sea hydrothermal vents, exoplanet atmospheric spectra, rare genetic mutations (like *Xeroderma pigmentosum*), or terrifying chemical nomenclature (e.g., *dichloro-diphenyl-trichloroethane*).
- THE CATCH: The core science required to solve it MUST be standard K-12 curriculum. The alien vocabulary is just a wrapper to test "Panic Control" and "Data Extraction." For example, a terrifying organic chemistry compound question should simply require identifying the number of covalent bonds or electronegativity trends.
- The item must be fully solvable within the 60-second time budget. If the student understands the basic principle, the alien context shouldn't slow them down.
- Zero repeating contexts. Ensure massive diversity in species, ecosystems, chemical reactions, and physical setups.

STRICT PSYCHOMETRIC TRIFECTA STANDARDS:
1. VALIDITY: The item must test the exact target MELC (competency). The alien context must NOT interfere with the scientific truth being measured.
2. RELIABILITY: A well-prepared student will pierce through the jargon and identify the basic principle (e.g., osmosis, Newton's 3rd Law, periodic trends). An unprepared student will guess blindly out of intimidation.
3. OBJECTIVITY: There must be ONE scientifically absolute correct answer. Distractors must target students who misinterpret the alien data or panic and choose a "smart-sounding" but factually wrong scientific term.



OUTPUT: Return ONLY valid JSON. No markdown fences. No text before or after."""

def build_math_prompt(comps: str, n: int, diff: str, dinstr: str) -> str:
    lines = [l.strip() for l in comps.strip().split('\n') if l.strip()]
    nc = len(lines)
    base = max(1, n // max(1, nc))
    rem  = n - base * nc
    assign = "\n".join(f"  [{base + (1 if i < rem else 0)} item(s)] {c}" for i,c in enumerate(lines))
    return f"""Generate exactly {n} UPCAT Mathematics items IN ENGLISH.

DIFFICULTY: {diff}
{dinstr}

MANDATORY COMPETENCY ASSIGNMENT:
{assign}

JSON schema — return exactly {n} items:
{{
  "exam_metadata": {{"subtest":"Mathematics","total_items":{n},"difficulty":"{diff}","calculator_allowed":false}},
  "items": [
    {{
      "item_number": 1,
      "competency": "exact competency text from the list above",
      "topic": "short topic (e.g. Quadratic Equations)",
      "subtopic": "specific concept tested",
      "grade_level_origin": "Grade 8",
      "question_text": "Full question in ENGLISH. ALL math MUST use LaTeX $...$ or $$...$$. Example: Find the roots of $x^2 - 5x + 6 = 0$.",
      "stimulus": null,
      "options": {{
        "A": "$2$ and $3$",
        "B": "$-2$ and $-3$",
        "C": "$1$ and $6$",
        "D": "$2$ and $-3$"
      }},
      "correct_answer": "A",
      "distractor_analysis": {{
        "B": {{"type": "SIGN_ERROR", "error": "Student negated both roots incorrectly"}},
        "C": {{"type": "ARITHMETIC_ERROR", "error": "Found factors of 6 but wrong pair"}},
        "D": {{"type": "CONCEPTUAL_ERROR", "error": "Mixed positive and negative roots incorrectly"}}
      }},
      "solution": "Step 1: Factor $x^2 - 5x + 6 = (x-2)(x-3) = 0$. Step 2: Set each factor to zero: $x-2=0$ gives $x=2$; $x-3=0$ gives $x=3$. Final answer: $x = 2$ and $x = 3$.",
      "key_concept": "Factoring trinomials to find roots of a quadratic equation.",
      "common_mistake": "Students often negate both roots when the constant term is positive."
    }}
  ]
}}"""

def build_sci_prompt(comps: str, n: int, diff: str, dinstr: str) -> str:
    lines = [l.strip() for l in comps.strip().split('\n') if l.strip()]
    nc = len(lines)
    base = max(1, n // max(1, nc))
    rem  = n - base * nc
    assign = "\n".join(f"  [{base + (1 if i < rem else 0)} item(s)] {c}" for i,c in enumerate(lines))
    return f"""Generate exactly {n} UPCAT Science items IN ENGLISH.

DIFFICULTY: {diff}
{dinstr}

MANDATORY COMPETENCY ASSIGNMENT:
{assign}

JSON schema — return exactly {n} items:
{{
  "exam_metadata": {{"subtest":"Science","total_items":{n},"difficulty":"{diff}"}},
  "items": [
    {{
      "item_number": 1,
      "competency": "exact competency text",
      "topic": "short topic (e.g. Cell Biology)",
      "subtopic": "specific concept",
      "grade_level_origin": "Grade 9",
      "science_discipline": "Biology",
      "stimulus_type": "TEXT_PASSAGE",
      "stimulus": "A researcher placed two groups of onion root tip cells under different glucose concentrations. Group A received 0.9% glucose solution (isotonic) while Group B received 3.0% glucose solution (hypertonic). After 30 minutes, Group B cells showed plasmolysis while Group A cells remained turgid.",
      "chart": null,
      "question_text": "Based on the experimental data, which process most directly explains the change observed in Group B cells?",
      "options": {{
        "A": "Active transport moving water against its concentration gradient",
        "B": "Osmosis causing water to move out of the cells into the surrounding solution",
        "C": "Diffusion of glucose molecules into the cell cytoplasm",
        "D": "Endocytosis bringing the hypertonic solution inside the cell membrane"
      }},
      "correct_answer": "B",
      "distractor_analysis": {{
        "A": {{"type": "MISCONCEPTION", "error": "Active transport moves solutes not water, and requires ATP"}},
        "C": {{"type": "PARTIAL_TRUTH", "error": "Diffusion is real but glucose moves into not out of cells here"}},
        "D": {{"type": "CONCEPTUAL_ERROR", "error": "Endocytosis is for large particles, not osmotic response"}}
      }},
      "solution": "1. The stimulus shows Group B cells in a hypertonic solution (3.0% glucose > cell interior concentration). 2. Osmosis moves water from high to low water potential — from inside the cell to the hypertonic solution outside. 3. This water loss causes the cell membrane to pull away from the cell wall, producing plasmolysis, which is directly caused by osmosis. 4. Active transport (A) moves solutes; diffusion of glucose (C) is not the primary change observed; endocytosis (D) is irrelevant to osmotic response.",
      "key_concept": "Osmosis is the passive movement of water across a selectively permeable membrane from a region of high water potential to low water potential.",
      "passage_reference": "Group B cells showed plasmolysis in 3.0% hypertonic solution"
    }}
  ]
}}"""

def generate_subtest(model, system: str, user: str, name: str):
    response = model.generate_content(f"{system}\n\n{user}")
    raw = clean_json(response.text)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        fixed = re.sub(r',\s*([}\]])', r'\1', raw)
        try: data = json.loads(fixed)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parse failed for {name}: {str(e)[:200]}")
    if 'items' not in data or not data['items']:
        raise ValueError(f"No items in {name} response")
    data['items'] = post_process(data['items'])
    return data

def run_generation(do_math: bool, do_sci: bool):
    if not api_key:
        st.error("❌ Enter your Gemini API Key in the sidebar."); return
    mc = st.session_state.get('competencies_math','').strip()
    sc = st.session_state.get('competencies_sci','').strip()
    if do_math and not mc:
        st.error("❌ Enter Math competencies first."); return
    if do_sci and not sc:
        st.error("❌ Enter Science competencies first."); return
    prog = st.progress(0); status = st.empty()
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            gemini_model,
            generation_config={"response_mime_type":"application/json","temperature":0.72,"top_p":0.92,"max_output_tokens":32000}
        )
        new_data = dict(st.session_state.get('test_data') or {})
        if do_math:
            status.info("📐 Generating Math items from your competencies…")
            prog.progress(10)
            md = generate_subtest(model, MATH_SYSTEM, build_math_prompt(mc, math_items, difficulty, diff_instruction), "Math")
            new_data['math'] = md; prog.progress(50)
            status.success(f"✅ Math: {len(md['items'])} items ready!")
        if do_sci:
            status.info("🔬 Generating Science items…")
            prog.progress(55 if do_math else 10)
            sd = generate_subtest(model, SCI_SYSTEM, build_sci_prompt(sc, sci_items, difficulty, diff_instruction), "Science")
            new_data['sci'] = sd; prog.progress(96)
            status.success(f"✅ Science: {len(sd['items'])} items ready!")
        prog.progress(100)
        mc_=len(new_data.get('math',{}).get('items',[])); sc_=len(new_data.get('sci',{}).get('items',[]))
        status.success(f"🎉 Ready — Math: {mc_} · Science: {sc_} · {difficulty}")
        st.session_state.update({
            'test_data': new_data, 'user_answers_math': {}, 'user_answers_sci': {},
            'flagged_items': set(), 'submitted': False,
            'math_start_time': None, 'sci_start_time': None, 'elapsed_math': 0, 'elapsed_sci': 0,
        })
        time.sleep(0.6); st.rerun()
    except Exception as e:
        st.error(f"❌ {str(e)[:500]}")

# ==========================================
# HERO
# ==========================================
st.markdown("""
<div class="hero" role="banner">
  <div class="hero-glow-l"></div><div class="hero-glow-r"></div>
  <div class="hero-inner">
    <div class="hero-eyebrow">🎓 UPCAT Elite Simulator · 2026 Edition</div>
    <h1 class="hero-title"><span class="accent">Padayon!</span><br><span class="accent2">Science</span> & Mathematics</h1>
    <p class="hero-sub">
      Research-grade UPCAT simulation. Math (50 items · 60 min · no calculator) and
      Science (45 items · 45 min · 60% passage-based). All questions in <strong>English</strong>.
      Competency-locked — every item maps to your DepEd MELCs.
      135,000+ applicants. ~7.8% first-choice rate.
    </p>
    <div class="hero-rule"></div>
    <div class="hero-stats">
      <div><div class="hs-num">135k+</div><div class="hs-lbl">Applicants / Year</div></div>
      <div><div class="hs-num">7.8%</div><div class="hs-lbl">1st-Choice Rate</div></div>
      <div><div class="hs-num">50+45</div><div class="hs-lbl">Full UPCAT Items</div></div>
      <div><div class="hs-num">−0.25</div><div class="hs-lbl">Wrong Penalty</div></div>
      <div><div class="hs-num">0</div><div class="hs-lbl">Calculators Allowed</div></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
  <span class="ni">ℹ️</span>
  <div><strong>2026 Edition:</strong> All questions in English. LaTeX renders via KaTeX.
  Competency-locked: items generated <em>only</em> from your provided DepEd MELCs.
  Science items are 60% passage/data-based. UPG uses research-based modeling.</div>
</div>""", unsafe_allow_html=True)

# ==========================================
# COMPETENCY INPUT
# ==========================================
st.markdown('<div class="sec-title">📋 Competency Input (Required)</div>', unsafe_allow_html=True)
st.markdown("""
<div class="notice sci">
  <span class="ni">🔑</span>
  <div><strong>Items are generated ONLY from competencies you enter.</strong>
  Paste DepEd MELCs one per line. Source from <em>curriculum.deped.gov.ph</em> or your textbook.
  Items are distributed evenly across all listed competencies.</div>
</div>""", unsafe_allow_html=True)

cc1, cc2 = st.columns(2)
with cc1:
    st.markdown('<div class="comp-wrap math"><div class="comp-head">🔢 Mathematics Competencies</div><div class="comp-sub">One per line · MELCs format recommended</div></div>', unsafe_allow_html=True)
    math_cv = st.text_area("Math comp", value=st.session_state.get('competencies_math',''), height=200,
        label_visibility="collapsed",
        placeholder="One competency per line, e.g.:\n\nFactors polynomials completely (M8AL-Ia-b-1)\nSolves quadratic equations by factoring\nIllustrates quadratic inequalities\nDetermines the standard form of a circle equation\nSolves problems involving geometric sequences",
        key="math_ci")
    st.session_state['competencies_math'] = math_cv
    mc_n = len([l for l in math_cv.strip().split('\n') if l.strip()])
    st.caption(f"✅ {mc_n} competencies · {math_items} items → ~{max(1,math_items//max(1,mc_n))} per comp" if mc_n>0 else "⚠️ Enter at least 1 Math competency.")

with cc2:
    st.markdown('<div class="comp-wrap sci"><div class="comp-head">🔬 Science Competencies</div><div class="comp-sub">One per line · include discipline for clarity</div></div>', unsafe_allow_html=True)
    sci_cv = st.text_area("Sci comp", value=st.session_state.get('competencies_sci',''), height=200,
        label_visibility="collapsed",
        placeholder="One competency per line, e.g.:\n\n[Biology] Describe structure and function of cell organelles\n[Biology] Explain the stages and significance of mitosis\n[Chemistry] Balance chemical equations using conservation of mass\n[Physics] Apply Newton's second law F=ma to solve problems\n[Earth Science] Explain plate tectonics and its effects",
        key="sci_ci")
    st.session_state['competencies_sci'] = sci_cv
    sc_n = len([l for l in sci_cv.strip().split('\n') if l.strip()])
    st.caption(f"✅ {sc_n} competencies · {sci_items} items → ~{max(1,sci_items//max(1,sc_n))} per comp" if sc_n>0 else "⚠️ Enter at least 1 Science competency.")

# ==========================================
# GENERATE
# ==========================================
st.markdown('<div class="sec-title">🚀 Generate Simulation</div>', unsafe_allow_html=True)
tm = max(10,int((math_items/50)*60)); ts = max(10,int((sci_items/45)*45))
gi1, gi2 = st.columns(2)
with gi1:
    st.markdown(f"""<div style='background:var(--bg1);border:1px solid var(--border2);border-top:2px solid var(--blue);border-radius:var(--r2);padding:16px 20px;'>
      <div style='font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--blue);margin-bottom:8px;'>🔢 Mathematics</div>
      <div style='font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--fg0);margin-bottom:6px;'>{math_items} Items · ~{tm} min · No Calculator</div>
      <div style='font-family:var(--font-body);font-size:0.8rem;color:var(--fg1);line-height:1.7;'>English only · KaTeX rendering · 72s/item budget · JHS-dominant topics · Locked to your competencies.</div>
    </div>""", unsafe_allow_html=True)
with gi2:
    st.markdown(f"""<div style='background:var(--bg1);border:1px solid var(--border2);border-top:2px solid var(--teal);border-radius:var(--r2);padding:16px 20px;'>
      <div style='font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--teal);margin-bottom:8px;'>🔬 Science</div>
      <div style='font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--fg0);margin-bottom:6px;'>{sci_items} Items · ~{ts} min · Passage-Based</div>
      <div style='font-family:var(--font-body);font-size:0.8rem;color:var(--fg1);line-height:1.7;'>English only · Data tables & charts · 60s/item budget · ~60% passage items · Locked to your competencies.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
g1,g2,g3 = st.columns([2,1,1])
with g1: gen_both=st.button(f"🚀 Generate Both ({math_items+sci_items} Items)",type="primary",use_container_width=True)
with g2: gen_math=st.button(f"🔢 Math Only ({math_items})",use_container_width=True)
with g3: gen_sci=st.button(f"🔬 Science Only ({sci_items})",use_container_width=True)
if gen_both: run_generation(True,True)
elif gen_math: run_generation(True,False)
elif gen_sci: run_generation(False,True)

# ==========================================
# EXAM INTERFACE
# ==========================================
if st.session_state.get('test_data') and not st.session_state.get('submitted'):
    td = st.session_state['test_data']
    math_data = td.get('math',{}).get('items',[])
    sci_data  = td.get('sci',{}).get('items',[])
    flagged   = st.session_state.get('flagged_items', set())

    am=len(st.session_state['user_answers_math']); as_=len(st.session_state['user_answers_sci'])
    tot_m=len(math_data); tot_s=len(sci_data); tot_all=tot_m+tot_s; tot_ans=am+as_
    pm=(am/max(1,tot_m))*100; ps=(as_/max(1,tot_s))*100

    if tot_m>0 and tot_s>0:
        pb1,pb2=st.columns(2)
        with pb1: st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔢 MATH — {am}/{tot_m}</span><span>{pm:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-m" style="width:{pm:.1f}%"></div></div></div>',unsafe_allow_html=True)
        with pb2: st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔬 SCIENCE — {as_}/{tot_s}</span><span>{ps:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-s" style="width:{ps:.1f}%"></div></div></div>',unsafe_allow_html=True)
    elif tot_m>0:
        st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔢 MATH — {am}/{tot_m}</span><span>{pm:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-m" style="width:{pm:.1f}%"></div></div></div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="pbar-wrap"><div class="pbar-row"><span>🔬 SCIENCE — {as_}/{tot_s}</span><span>{ps:.0f}%</span></div><div class="pbar-track"><div class="pbar-fill-s" style="width:{ps:.1f}%"></div></div></div>',unsafe_allow_html=True)

    st.markdown("""<div class="notice warn"><span class="ni">⚠️</span><div><strong>RMW Scoring Active:</strong> +1.00 correct · −0.25 wrong · 0.00 blank. Only guess when you can eliminate ≥2 options. Math: no calculator — all items solvable by hand. Science: read the stimulus <em>before</em> the question.</div></div>""",unsafe_allow_html=True)

    if show_timer:
        active=st.session_state.get('active_subtest','math')
        if active=='math' and st.session_state.get('math_start_time'):
            remaining=max(0,3600-int(time.time()-st.session_state['math_start_time']))
        elif active=='sci' and st.session_state.get('sci_start_time'):
            remaining=max(0,2700-int(time.time()-st.session_state['sci_start_time']))
        else: remaining=3600 if active=='math' else 2700
        lbl="🔬" if active=="sci" else "🔢"; tcls="s" if active=="sci" else ""
        st.components.v1.html(f"""
        <div id="tc" class="timer {tcls}">{lbl} <span id="tv">--:--</span></div>
        <style>.timer{{position:fixed;top:16px;right:20px;z-index:99999;font-family:'IBM Plex Mono',monospace;font-size:.9rem;font-weight:600;padding:8px 18px;border-radius:24px;border:1px solid rgba(77,159,255,.3);background:#0e1520;color:#4d9fff;letter-spacing:.06em;box-shadow:0 4px 16px rgba(0,0,0,.5);}}.timer.s{{color:#2dd4bf;border-color:rgba(45,212,191,.3);}}.timer.w{{color:#fbbf24;}}.timer.d{{color:#f87171;animation:pulse 1s infinite;}}@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.6;}}}}</style>
        <script>(function(){{var tl={remaining};function tick(){{if(tl<0)tl=0;var m=Math.floor(tl/60),s=tl%60;var el=document.getElementById('tv'),box=document.getElementById('tc');if(el){{el.textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;if(tl<=300&&tl>60)box.className='timer {tcls} w';if(tl<=60)box.className='timer {tcls} d';if(tl<=0)el.textContent='TIME UP';}}if(tl>0){{tl--;setTimeout(tick,1000);}}}}setTimeout(tick,300);}})()</script>""",height=0)

    tab_labels=[]
    if math_data: tab_labels.append(f"🔢 Math ({tot_m} items · {am} answered)")
    if sci_data:  tab_labels.append(f"🔬 Science ({tot_s} items · {as_} answered)")
    if len(tab_labels)==2:
        tm_tab,ts_tab=st.tabs(tab_labels); render_pairs=[(tm_tab,'math',math_data),(ts_tab,'sci',sci_data)]
    elif len(tab_labels)==1:
        only=st.tabs(tab_labels)[0]; render_pairs=[(only,'math' if math_data else 'sci',math_data or sci_data)]
    else: render_pairs=[]

    def render_subtest(tab, key, items):
        with tab:
            if not items: return
            is_math=(key=='math'); ans_key=f'user_answers_{key}'
            dot_cls='am' if is_math else 'as'; badge_cls='math' if is_math else 'sci'
            if not st.session_state.get(f'{key}_start_time'):
                st.session_state[f'{key}_start_time']=time.time()
                st.session_state['active_subtest']=key

            if show_nav:
                nav=f'<div class="nav-box"><div class="nav-title">{"Math" if is_math else "Science"} navigator</div><div class="nav-grid">'
                for q in items:
                    inum=q.get('item_number'); fkey=f"{key}_{inum}"
                    cls='fl' if fkey in flagged else (dot_cls if inum in st.session_state[ans_key] else '')
                    nav+=f'<div class="nav-dot {cls}" onclick="document.getElementById(\'{key}_{inum}\').scrollIntoView({{behavior:\'smooth\'}})">{inum}</div>'
                nav+='</div></div>'
                st.markdown(nav, unsafe_allow_html=True)

            for q in items:
                inum=q.get('item_number'); topic=q.get('topic',''); grade_o=q.get('grade_level_origin','')
                qtext=q.get('question_text',''); stimulus=q.get('stimulus'); stim_type=q.get('stimulus_type')
                chart_d=q.get('chart'); comp=q.get('competency',''); disc=q.get('science_discipline','')
                is_ans=(inum in st.session_state[ans_key]); is_flg=(f"{key}_{inum}" in flagged)
                card_cls=f"q-card{' sci' if not is_math else ''}{' answered' if is_ans else ''}{' flagged' if is_flg else ''}"

                # Build badge HTML with proper HTML escaping
                topic_s=esc_html(topic[:26]+('…' if len(topic)>26 else ''))
                comp_s=esc_html(comp[:42]+('…' if len(comp)>42 else ''))
                comp_full=esc_html(comp)

                badge_html=(f'<span class="q-badge {badge_cls}">{"MTH" if is_math else "SCI"} {inum:02d}</span>'
                           +f'<span class="q-badge tag" title="{esc_html(topic)}">{topic_s}</span>')
                if grade_o: badge_html+=f'<span class="q-badge tag">{esc_html(grade_o)}</span>'
                if disc and not is_math: badge_html+=f'<span class="q-badge tag">{esc_html(disc)}</span>'
                if comp_s: badge_html+=f'<span class="q-badge tag" title="{comp_full}" style="max-width:240px;overflow:hidden;text-overflow:ellipsis;">{comp_s}</span>'
                if is_flg: badge_html+='<span class="q-badge flag">🚩 Flagged</span>'
                if is_ans: badge_html+='<span class="q-badge ok">✅</span>'

                st.markdown(f'<div class="{card_cls}" id="{key}_{inum}"><div class="q-meta">{badge_html}</div>', unsafe_allow_html=True)

               # ── 1. STIMULUS (Native Markdown for Tables & Math) ──
                if stimulus:
                    stim_str = str(stimulus)
                    if stim_type == "DATA_TABLE":
                        st.markdown('<div class="stim-label d">📊 Experimental Data / Table</div>', unsafe_allow_html=True)
                        st.markdown(stim_str, unsafe_allow_html=True)
                    elif stim_type == "DIAGRAM":
                        st.markdown('<div class="stim-label g">🔎 Diagram / Figure</div>', unsafe_allow_html=True)
                        st.info(safe_md(stim_str))
                    else:
                        st.markdown('<div class="stim-label p">📄 Read the passage carefully before answering:</div>', unsafe_allow_html=True)
                        st.info(safe_md(stim_str))

                # ── 2. CHART ──
                if chart_d and isinstance(chart_d, dict):
                    try:
                        svg = build_chart(chart_d)
                        if svg: st.markdown(f'<div class="chart-wrap">{svg}</div>', unsafe_allow_html=True)
                    except Exception: pass

                # ── 3. QUESTION TEXT ──
                st.markdown(f"**{safe_md(qtext)}**")

                # ── 4. OPTIONS (With Math Protection) ──
                opts = q.get('options', {})
                choices =[
                    f"A)  {safe_md(opts.get('A',''))}",
                    f"B)  {safe_md(opts.get('B',''))}",
                    f"C)  {safe_md(opts.get('C',''))}",
                    f"D)  {safe_md(opts.get('D',''))}",
                ]
                choice = st.radio(f"Q{key}{inum}", choices, key=f"{key}_r_{inum}", index=None, label_visibility="collapsed")
                if choice:
                    st.session_state[ans_key][inum] = choice.strip()[0].upper()

                if enable_flag:
                    fkey=f"{key}_{inum}"
                    if st.button("🚩 Unflag" if fkey in flagged else "🚩 Flag",key=f"fl_{key}_{inum}"):
                        if fkey in flagged: flagged.discard(fkey)
                        else: flagged.add(fkey)
                        st.session_state['flagged_items']=flagged; st.rerun()

                st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:10px 0 14px;'>",unsafe_allow_html=True)

    for tab,key,items in render_pairs:
        render_subtest(tab,key,items)

    blank_cnt=tot_all-tot_ans; flag_cnt=len(flagged)
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown(f"""<div class="stat-row">
      <div class="stat-pill"><div class="sp-n" style="color:var(--green);">{tot_ans}</div><div class="sp-l">Answered</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--amber);">{flag_cnt}</div><div class="sp-l">Flagged</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{blank_cnt}</div><div class="sp-l">Blank (0 pts)</div></div>
      <div class="stat-pill"><div class="sp-n" style="color:var(--blue);">{tot_all}</div><div class="sp-l">Total Items</div></div>
    </div>""",unsafe_allow_html=True)
    s1,s2,s3=st.columns([1,2,1])
    with s2:
        if blank_cnt>0: st.warning(f"⚠️ {blank_cnt} unanswered — scored 0. Guess only if you can eliminate ≥2 options.")
        if flag_cnt>0: st.info(f"🚩 {flag_cnt} item(s) flagged — review before submitting.")
        if st.button("📥 Submit & View Full UPG Report",type="primary",use_container_width=True):
            st.session_state['submitted']=True
            if st.session_state.get('math_start_time'): st.session_state['elapsed_math']=time.time()-st.session_state['math_start_time']
            if st.session_state.get('sci_start_time'):  st.session_state['elapsed_sci']=time.time()-st.session_state['sci_start_time']
            st.rerun()

# ==========================================
# RESULTS
# ==========================================
if st.session_state.get('submitted') and st.session_state.get('test_data'):
    st.balloons()
    td=st.session_state['test_data']; u_math=st.session_state.get('user_answers_math',{}); u_sci=st.session_state.get('user_answers_sci',{})
    em=st.session_state.get('elapsed_math',0); es=st.session_state.get('elapsed_sci',0)
    math_data=td.get('math',{}).get('items',[]); sci_data=td.get('sci',{}).get('items',[])

    def score(items, ua):
        total=len(items); correct=sum(1 for q in items if ua.get(q['item_number'])==q.get('correct_answer'))
        answered=sum(1 for v in ua.values() if v); wrong=answered-correct; blank=total-answered
        raw=max(0.0,correct-0.25*wrong); pct=raw/max(1,total)
        return total,correct,wrong,blank,raw,pct

    if math_data: mt,mc,mw,mb,mr,mp=score(math_data,u_math)
    else: mt,mc,mw,mb,mr,mp=0,0,0,0,0.0,0.0
    if sci_data: st2,sc2,sw,sb,sr,sp=score(sci_data,u_sci)
    else: st2,sc2,sw,sb,sr,sp=0,0,0,0,0.0,0.0

    math_grades=[g8_math,g9_math,g10_math,g11_precalc,g11_calc,g11_stats,g11_genmath]
    sci_grades=[g8_sci,g9_sci,g10_sci,g11_bio1,g11_bio2,g11_earth]
    mgav=float(np.mean(math_grades)); sgav=float(np.mean(sci_grades)); agav=float(np.mean(math_grades+sci_grades))
    amod=(jhs_mod+shs_mod)/2

    def g2upg(avg,mod): return max(1.0,min(5.0,5.0-((avg-75)/25)*4.0-mod))
    mg_upg=g2upg(mgav,amod); sg_upg=g2upg(sgav,amod); ag_upg=g2upg(agav,amod)

    def upcat2upg(pct):
        z=(pct-MEAN_BASELINE)/SIGMA; return max(1.0,min(5.0,2.75-z*0.55)),z
    mu_upg,mz=(upcat2upg(mp) if math_data else (ag_upg,0.0))
    su_upg,sz=(upcat2upg(sp) if sci_data else (ag_upg,0.0))
    mf_upg=0.40*mg_upg+0.60*mu_upg; sf_upg=0.40*sg_upg+0.60*su_upg

    if math_data and sci_data:
        cp=(mp+sp)/2; ou_upg,cz=upcat2upg(cp); final_upg=0.40*ag_upg+0.60*ou_upg
    elif math_data: cp,ou_upg,cz,final_upg=mp,mu_upg,mz,mf_upg
    else: cp,ou_upg,cz,final_upg=sp,su_upg,sz,sf_upg

    op=max(0.001,min(0.9999,0.5*(1+math.erf(cz/math.sqrt(2)))))
    sim_rank=int(135000-135000*op)

    if   final_upg<=1.50: verdict="🏆 Elite — Top tier across all UP campuses."
    elif final_upg<=2.00: verdict="✅ Very Strong — Likely qualifies for multiple programs."
    elif final_upg<=2.30: verdict="📘 Competitive — Within range for several programs."
    elif final_upg<=2.60: verdict="🟡 Borderline — May qualify at less competitive campuses."
    elif final_upg<=3.00: verdict="🟠 Below Threshold — Focused improvement needed."
    else:                  verdict="🔴 Not Yet Ready — Focus on fundamentals first."

    def atopics(items,ua):
        td={}
        for q in items:
            k=q.get('competency',q.get('topic','Unknown')); k=(k[:36]+'…') if len(k)>36 else k
            inum=q.get('item_number'); ok=ua.get(inum)==q.get('correct_answer')
            if k not in td: td[k]={'correct':0,'total':0}
            td[k]['total']+=1
            if ok: td[k]['correct']+=1
        return td
    mt_=atopics(math_data,u_math) if math_data else {}
    st_=atopics(sci_data,u_sci) if sci_data else {}

    upg_color="#4d9fff" if final_upg<=2.3 else ("#fbbf24" if final_upg<=2.8 else "#f87171")
    st.markdown(f"""<div class="res-hero"><div class="res-hero-glow"></div>
      <div class="upg-label">University Predicted Grade (UPG) · {difficulty} Difficulty</div>
      <div class="upg-val" style="color:{upg_color};">{final_upg:.3f}</div>
      <div class="upg-verdict">{verdict}</div>
      <div style="color:rgba(255,255,255,0.25);font-family:var(--font-mono);font-size:0.58rem;margin-top:12px;letter-spacing:0.1em;position:relative;z-index:1;">
        Scale: 1.000 (highest) → 5.000 (lowest) · Rank #{sim_rank:,} of 135,000 · Top {100*(1-op):.1f}th percentile
      </div></div>""",unsafe_allow_html=True)

    st.markdown('<div class="sec-title">📊 Subject UPG Breakdown</div>',unsafe_allow_html=True)
    st.markdown(f"""<div class="upg-cards">
      <div class="upg-card m"><div class="upg-card-title">🔢 Mathematics UPG</div>
        <div class="upg-card-val">{mf_upg:.3f}</div>
        <div class="upg-card-sub">{"✅ Strong" if mf_upg<=2.3 else "⚠️ Needs work" if mf_upg<=2.8 else "❌ Significant gaps"}</div>
        <div class="upg-br">
          <div class="upg-br-row"><span class="upg-br-lbl">Grade Avg</span><span class="upg-br-val" style="color:var(--blue);">{mgav:.1f}/100</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Grade UPG (40%)</span><span class="upg-br-val">{mg_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT Score</span><span class="upg-br-val" style="color:var(--blue);">{mp*100:.1f}%</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT UPG (60%)</span><span class="upg-br-val">{mu_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Z-score</span><span class="upg-br-val">{mz:+.2f}σ</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">C / W / B</span><span class="upg-br-val">{mc}C · {mw}W · {mb}B</span></div>
        </div></div>
      <div class="upg-card s"><div class="upg-card-title">🔬 Science UPG</div>
        <div class="upg-card-val">{sf_upg:.3f}</div>
        <div class="upg-card-sub">{"✅ Strong" if sf_upg<=2.3 else "⚠️ Needs work" if sf_upg<=2.8 else "❌ Significant gaps"}</div>
        <div class="upg-br">
          <div class="upg-br-row"><span class="upg-br-lbl">Grade Avg</span><span class="upg-br-val" style="color:var(--teal);">{sgav:.1f}/100</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Grade UPG (40%)</span><span class="upg-br-val">{sg_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT Score</span><span class="upg-br-val" style="color:var(--teal);">{sp*100:.1f}%</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">UPCAT UPG (60%)</span><span class="upg-br-val">{su_upg:.3f}</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">Z-score</span><span class="upg-br-val">{sz:+.2f}σ</span></div>
          <div class="upg-br-row"><span class="upg-br-lbl">C / W / B</span><span class="upg-br-val">{sc2}C · {sw}W · {sb}B</span></div>
        </div></div>
    </div>""",unsafe_allow_html=True)

    metrics=[(f"{final_upg:.3f}",upg_color,"Overall UPG","Lower = Better"),(f"#{sim_rank:,}","var(--teal)","Sim. Rank",f"Top {100*(1-op):.1f}%"),(f"{ag_upg:.3f}","var(--green)","Grades UPG",f"Avg: {agav:.1f}/100"),(f"{ou_upg:.3f}","var(--amber)" if ou_upg>2.5 else "var(--green)","UPCAT UPG",f"Z: {cz:+.2f}")]
    if math_data: metrics.append((f"{mp*100:.1f}%","var(--blue)","Math Score",f"RMW: {mr:.2f}/{mt}"))
    if sci_data:  metrics.append((f"{sp*100:.1f}%","var(--teal)","Sci. Score",f"RMW: {sr:.2f}/{st2}"))
    cols_m=st.columns(min(len(metrics),4))
    for i,(val,clr,lbl,sub) in enumerate(metrics):
        with cols_m[i%4]: st.metric(label=lbl,value=val,delta=sub)

    st.markdown("<br>",unsafe_allow_html=True)
    pkeys=[k for k in ['math','sci'] if (math_data if k=='math' else sci_data)]
    pc=st.columns(len(pkeys)) if pkeys else []
    for ci,pk in enumerate(pkeys):
        with pc[ci]:
            if pk=='math':
                em_m,em_s=int(em//60),int(em%60); bud=72*mt
                st.markdown(f"""<div class="score-panel"><h4>🔢 Mathematics</h4>
                  <div class="s-row"><span class="s-lbl">Correct</span><span class="s-val c">{mc}/{mt}</span></div>
                  <div class="s-row"><span class="s-lbl">Wrong (−0.25 each)</span><span class="s-val w">{mw} · −{mw*0.25:.2f} pts</span></div>
                  <div class="s-row"><span class="s-lbl">Blank</span><span class="s-val">{mb}</span></div>
                  <div class="s-row"><span class="s-lbl">RMW Score</span><span class="s-val g">{mr:.2f}/{mt}</span></div>
                  <div class="s-row"><span class="s-lbl">Percentage</span><span class="s-val g">{mp*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Accuracy on Attempted</span><span class="s-val">{mc/max(1,mc+mw)*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Time</span><span class="s-val">{em_m}m {em_s}s · {em/max(1,mt):.0f}s/item</span></div>
                  <div class="s-row"><span class="s-lbl">Budget</span><span class="s-val {"c" if em<=bud else "w"}">{"✅ On budget" if em<=bud else "⚠️ Over budget"}</span></div>
                </div>""",unsafe_allow_html=True)
            else:
                es_m,es_s=int(es//60),int(es%60); bud=60*st2
                st.markdown(f"""<div class="score-panel"><h4>🔬 Science</h4>
                  <div class="s-row"><span class="s-lbl">Correct</span><span class="s-val c">{sc2}/{st2}</span></div>
                  <div class="s-row"><span class="s-lbl">Wrong (−0.25 each)</span><span class="s-val w">{sw} · −{sw*0.25:.2f} pts</span></div>
                  <div class="s-row"><span class="s-lbl">Blank</span><span class="s-val">{sb}</span></div>
                  <div class="s-row"><span class="s-lbl">RMW Score</span><span class="s-val g">{sr:.2f}/{st2}</span></div>
                  <div class="s-row"><span class="s-lbl">Percentage</span><span class="s-val g">{sp*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Accuracy on Attempted</span><span class="s-val">{sc2/max(1,sc2+sw)*100:.1f}%</span></div>
                  <div class="s-row"><span class="s-lbl">Time</span><span class="s-val">{es_m}m {es_s}s · {es/max(1,st2):.0f}s/item</span></div>
                  <div class="s-row"><span class="s-lbl">Budget</span><span class="s-val {"c" if es<=bud else "w"}">{"✅ On budget" if es<=bud else "⚠️ Over budget"}</span></div>
                </div>""",unsafe_allow_html=True)

    # Heatmap
    hp=[(k,mt_ if k=='math' else st_) for k in ['math','sci'] if (mt_ if k=='math' else st_)]
    if hp:
        st.markdown('<div class="sec-title">🔥 Competency Mastery Heatmap</div>',unsafe_allow_html=True)
        hc=st.columns(len(hp))
        for hi,(hk,htd) in enumerate(hp):
            clr="var(--blue)" if hk=='math' else "var(--teal)"
            with hc[hi]:
                st.markdown(f"<h4 style='font-family:var(--font-display);font-size:0.9rem;color:{clr};margin-bottom:10px;'>{'🔢 Math' if hk=='math' else '🔬 Science'} Mastery</h4>",unsafe_allow_html=True)
                rows=sorted(htd.items(),key=lambda x:x[1]['correct']/max(1,x[1]['total']))
                html="<div class='heat-grid'>"
                for sk,d in rows:
                    p=d['correct']/max(1,d['total'])*100; bc="hi" if p>=70 else ("mid" if p>=40 else "lo")
                    pc="var(--green)" if bc=="hi" else ("var(--amber)" if bc=="mid" else "var(--red)")
                    sk_s=(sk[:30]+'…') if len(sk)>30 else sk
                    html+=f'<div class="heat-row" title="{esc_html(sk)}"><span style="flex:1;color:var(--fg1);font-size:0.73rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{esc_html(sk_s)}</span><div class="heat-bar-out"><div class="heat-bar-in {bc}" style="width:{p:.0f}%;"></div></div><span class="heat-pct" style="color:{pc};">{p:.0f}%</span></div>'
                html+="</div>"
                st.markdown(html,unsafe_allow_html=True)

    # Admission
    st.markdown('<div class="sec-title">🏛️ UP Admission Decision Engine</div>',unsafe_allow_html=True)
    st.markdown(f"""<div class="notice"><span class="ni">📊</span><div><strong>UPCAT 2025:</strong> 17,996 of 135,236 applicants qualified (13.3%). Your UPG <strong>{final_upg:.3f}</strong> → rank <strong>#{sim_rank:,}</strong>.</div></div>""",unsafe_allow_html=True)

    def ep(campus,prog,cutoff,upg):
        tier=get_program_tier(campus,prog); adj={"Triple Quota":-0.40,"Double Quota":-0.22,"Single Quota":-0.06,"Less Popular":+0.08}.get(tier,0)
        req=max(1.1,cutoff+adj)
        if upg<=req: return "<span class='badge pass'>✅ PASSED</span>",req,tier
        elif upg<=req+0.14: return "<span class='badge risk'>🟡 DPWAS RISK</span>",req,tier
        else: return "<span class='badge fail'>❌ BELOW CUTOFF</span>",req,tier

    ac1,ac2=st.columns(2)
    for acol,campus,progs,cn in [(ac1,campus_1,[c1_p1,c1_p2,c1_p3],"1st"),(ac2,campus_2,[c2_p1,c2_p2,c2_p3],"2nd")]:
        cutoff=CAMPUS_DATA[campus]["cutoff"]; q=final_upg<=cutoff
        with acol:
            st.markdown(f"""<div class="campus-card"><div class="campus-hdr {"" if q else "fail"}"><h4>{cn} — {campus}</h4><p>Cutoff: {cutoff:.3f} · Your UPG: {final_upg:.3f} · {"✅ QUALIFIED" if q else "❌ NOT QUALIFIED"} · {CAMPUS_DATA[campus]["note"]}</p></div><div class="campus-body">""",unsafe_allow_html=True)
            if campus==campus_2 and final_upg<=CAMPUS_DATA[campus_1]["cutoff"]: st.info("📌 Qualified at 1st campus — 2nd is void in cascading system.")
            if q:
                for i,prog in enumerate(progs,1):
                    badge,req,tier=ep(campus,prog,cutoff,final_upg)
                    st.markdown(f'<div class="prog-row"><div><div class="prog-name">P{i}: {prog}</div><div class="prog-sub">{tier} · eff. cutoff ~{req:.3f}</div></div><div>{badge}</div></div>',unsafe_allow_html=True)
            else:
                recon=CAMPUS_DATA[campus]["recon"]; rok=recon>0 and final_upg<=recon
                st.markdown(f'<div style="padding:14px;text-align:center;font-family:var(--font-body);font-size:0.85rem;color:var(--fg1);">UPG {final_upg:.3f} exceeds cutoff {cutoff:.3f}.<br><br>Recon: <strong>{f"{recon:.3f}" if recon>0 else "None"}</strong><br>{"✅ Recon-eligible" if rok else ("❌ Beyond recon range" if recon>0 else "🚫 No appeals")}</div>',unsafe_allow_html=True)
            st.markdown("</div></div>",unsafe_allow_html=True)

    # Review tabs
    st.markdown('<div class="sec-title">🔬 Detailed Review & Analytics</div>',unsafe_allow_html=True)
    tab_lbls=["📊 Overview","🧮 UPG Formula"]
    if math_data: tab_lbls.append("🔢 Math Review")
    if sci_data:  tab_lbls.append("🔬 Science Review")
    tab_lbls.append("⚖️ Recon & DPWAS")
    tabs_r=st.tabs(tab_lbls); ti=0

    with tabs_r[ti]:
        gr=(mw+sw)/max(1,mc+mw+sc2+sw)
        me={k:(1-v['correct']/max(1,v['total']))*100 for k,v in mt_.items()}
        se={k:(1-v['correct']/max(1,v['total']))*100 for k,v in st_.items()}
        top_m=sorted(me.items(),key=lambda x:-x[1])[:5]; top_s=sorted(se.items(),key=lambda x:-x[1])[:5]
        penalty=(mw+sw)*0.25
        st.markdown(f"""<div class="notice green"><span class="ni">📊</span><div>
          <strong>Summary — {difficulty}</strong><br>
          Rank <strong>#{sim_rank:,}</strong> of 135,000 · {op*100:.1f}th percentile ·
          Combined: <strong>{cp*100:.1f}%</strong> (mean {MEAN_BASELINE*100:.0f}%, σ={SIGMA:.2f}) · Z: <strong>{cz:+.2f}</strong> ·
          Penalty: <strong>−{penalty:.2f} pts</strong>
          {" · ✅ Efficient guessing." if gr<0.22 else " · ⚠️ Over-guessing." if gr<0.38 else " · 🔴 Aggressive guessing."}
        </div></div>""",unsafe_allow_html=True)
        if top_m: st.markdown('<div class="notice warn"><span class="ni">🔢</span><div><strong>Math Weak Areas:</strong><br>'+"<br>".join(f"• {esc_html(k)} — {e:.0f}% error" for k,e in top_m)+'</div></div>',unsafe_allow_html=True)
        if top_s: st.markdown('<div class="notice sci"><span class="ni">🔬</span><div><strong>Science Weak Areas:</strong><br>'+"<br>".join(f"• {esc_html(k)} — {e:.0f}% error" for k,e in top_s)+'</div></div>',unsafe_allow_html=True)
    ti+=1

    with tabs_r[ti]:
        st.markdown("#### 🧮 UPG Formula Derivation")
        if math_data:
            with st.expander("📐 Math UPG"):
                st.latex(f"\\text{{RMW}}_{{\\text{{Math}}}} = {mc} - \\tfrac{{1}}{{4}} \\times {mw} = {mr:.2f}")
                st.latex(f"Z_{{\\text{{Math}}}} = \\frac{{{mp:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {mz:.4f}")
                st.latex(f"UPG_{{\\text{{Math}}}} = 0.40 \\times {mg_upg:.3f} + 0.60 \\times {mu_upg:.3f} = {mf_upg:.3f}")
        if sci_data:
            with st.expander("📐 Science UPG"):
                st.latex(f"\\text{{RMW}}_{{\\text{{Sci}}}} = {sc2} - \\tfrac{{1}}{{4}} \\times {sw} = {sr:.2f}")
                st.latex(f"Z_{{\\text{{Sci}}}} = \\frac{{{sp:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {sz:.4f}")
                st.latex(f"UPG_{{\\text{{Sci}}}} = 0.40 \\times {sg_upg:.3f} + 0.60 \\times {su_upg:.3f} = {sf_upg:.3f}")
        with st.expander("📐 Final UPG"):
            st.latex(f"\\text{{Final UPG}} = 0.40 \\times {ag_upg:.3f} + 0.60 \\times {ou_upg:.3f} = {final_upg:.3f}")
        with st.expander("📐 Grade UPG"):
            st.latex(r"UPG_{\text{grade}} = 5.0 - \left(\frac{\bar{G} - 75}{25}\right) \times 4.0 - \Delta_{\text{school}}")
            st.markdown(f"Combined avg: **{agav:.2f}** · School modifier: **{amod:+.3f}** · Palugit: **{'Active' if palugit_active else 'Not Active'}**")
    ti+=1

    # ── MATH REVIEW ──
    if math_data:
        with tabs_r[ti]:
            st.markdown("### 🔢 Mathematics — Item Review")
            mw_l=[q for q in math_data if u_math.get(q['item_number']) not in [None,''] and u_math.get(q['item_number'])!=q.get('correct_answer')]
            mc_l=[q for q in math_data if u_math.get(q['item_number'])==q.get('correct_answer')]
            mb_l=[q for q in math_data if not u_math.get(q['item_number'])]
            st.markdown(f'<div class="stat-row"><div class="stat-pill"><div class="sp-n" style="color:var(--red);">{len(mw_l)}</div><div class="sp-l">Wrong</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--green);">{len(mc_l)}</div><div class="sp-l">Correct</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{len(mb_l)}</div><div class="sp-l">Blank</div></div></div>',unsafe_allow_html=True)
            for lbl,subset,show_sol in [(f"❌ Wrong ({len(mw_l)}) — Priority Review",mw_l,True),(f"✅ Correct ({len(mc_l)})",mc_l,False),(f"⚪ Skipped ({len(mb_l)})",mb_l,True)]:
                if not subset: continue
                st.markdown(f"#### {lbl}")
                for q in subset:
                    inum=q['item_number']; u=u_math.get(inum); c=q.get('correct_answer')
                    comp=q.get('competency',q.get('topic',''))[:55]
                    ss=f"Chose {u} → Correct: {c}" if u and u!=c else ("✅ Correct" if u==c else "⚪ Skipped")
                    with st.expander(f"MTH {inum:02d} · {comp} · {ss}"):
                       # Native Question and Options rendering for Math
                        st.markdown(f"**Question:**\n\n{safe_md(q.get('question_text',''))}")
                        opts = q.get('options',{})
                        for lt in['A','B','C','D']:
                            txt = f"**{lt})** {safe_md(opts.get(lt,''))}"
                            if lt == c: st.markdown(f'<div class="ir-c">✅ {txt}</div>', unsafe_allow_html=True)
                            elif lt == u: st.markdown(f'<div class="ir-w">❌ {txt} ← Your answer</div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="ir-o">{txt}</div>', unsafe_allow_html=True)
                        da = q.get('distractor_analysis',{})
                        if da and u and u in da and u != c:
                            err = da[u]
                            if isinstance(err, dict): st.warning(f"**Error ({err.get('type','')}):** {err.get('error','')}")
                            else: st.warning(str(err))
                        if show_sol or u == c:
                            sol = q.get('solution','')
                            if sol: st.info(f"**📐 Solution:**\n\n{safe_md(sol)}")
                            kc = q.get('key_concept','')
                            if kc: st.caption(f"💡 {kc}")
                            cm = q.get('common_mistake','')
                            if cm: st.caption(f"⚠️ Common mistake: {cm}")
        ti+=1

    # ── SCIENCE REVIEW ──
    if sci_data:
        with tabs_r[ti]:
            st.markdown("### 🔬 Science — Item Review")
            sw_l=[q for q in sci_data if u_sci.get(q['item_number']) not in [None,''] and u_sci.get(q['item_number'])!=q.get('correct_answer')]
            sc_l=[q for q in sci_data if u_sci.get(q['item_number'])==q.get('correct_answer')]
            sb_l=[q for q in sci_data if not u_sci.get(q['item_number'])]
            st.markdown(f'<div class="stat-row"><div class="stat-pill"><div class="sp-n" style="color:var(--red);">{len(sw_l)}</div><div class="sp-l">Wrong</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--green);">{len(sc_l)}</div><div class="sp-l">Correct</div></div><div class="stat-pill"><div class="sp-n" style="color:var(--fg2);">{len(sb_l)}</div><div class="sp-l">Blank</div></div></div>',unsafe_allow_html=True)
            for lbl,subset,show_sol in [(f"❌ Wrong ({len(sw_l)}) — Priority",sw_l,True),(f"✅ Correct ({len(sc_l)})",sc_l,False),(f"⚪ Skipped ({len(sb_l)})",sb_l,True)]:
                if not subset: continue
                st.markdown(f"#### {lbl}")
                for q in subset:
                    inum=q['item_number']; u=u_sci.get(inum); c=q.get('correct_answer')
                    comp=q.get('competency',q.get('topic',''))[:50]; disc=q.get('science_discipline','')
                    ss=f"Chose {u} → Correct: {c}" if u and u!=c else ("✅ Correct" if u==c else "⚪ Skipped")
                    with st.expander(f"SCI {inum:02d} · {comp} [{disc}] · {ss}"):
                       stim = q.get('stimulus','')
                        if stim:
                            st_type = q.get('stimulus_type','')
                            if st_type == "DATA_TABLE":
                                st.markdown('<div class="stim-label d">📊 Data Table</div>', unsafe_allow_html=True)
                                st.markdown(str(stim), unsafe_allow_html=True)
                            else:
                                st.info(safe_md(str(stim)))
                        
                        cd = q.get('chart')
                        if cd and isinstance(cd, dict):
                            try:
                                svg = build_chart(cd)
                                if svg: st.markdown(f'<div class="chart-wrap">{svg}</div>', unsafe_allow_html=True)
                            except Exception: pass
                            
                        st.markdown(f"**Question:**\n\n{safe_md(q.get('question_text',''))}")
                        opts = q.get('options',{})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {safe_md(opts.get(lt,''))}"
                            if lt == c: st.markdown(f'<div class="ir-c">✅ {txt}</div>', unsafe_allow_html=True)
                            elif lt == u: st.markdown(f'<div class="ir-w">❌ {txt} ← Your answer</div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="ir-o">{txt}</div>', unsafe_allow_html=True)
                            
                        da = q.get('distractor_analysis',{})
                        if da and u and u in da and u != c:
                            err = da[u]
                            if isinstance(err, dict): st.warning(f"**Why {u} is wrong ({err.get('type','')}):** {err.get('error','')}")
                            
                        if show_sol or u == c:
                            sol = q.get('solution','')
                            if sol: st.info(f"**🔬 Explanation:**\n\n{safe_md(sol)}")
                            pr = q.get('passage_reference','')
                            if pr: st.caption(f"📍 Key evidence: {pr}")
                            kc = q.get('key_concept','')
                            if kc: st.caption(f"💡 {kc}")
        ti+=1

    with tabs_r[ti]:
        st.markdown("### ⚖️ DPWAS, Reconsideration & Cascading Admission")
        st.markdown(f"""<div class="notice"><span class="ni">📋</span><div>
          <strong>UPCAT 2025:</strong> 17,996 of 135,236 qualified (13.3%). ~10,600 direct qualifiers (~7.8%). ~7,400 DPWAS waitlisted.
          DPWAS is <em>not</em> rejection — slots open as accepted students decline or shift. Your rank: <strong>#{sim_rank:,}</strong>.
        </div></div>""",unsafe_allow_html=True)
        for campus in [campus_1,campus_2]:
            recon=CAMPUS_DATA[campus]["recon"]; cutoff=CAMPUS_DATA[campus]["cutoff"]
            st.markdown(f"**{campus}** — Cutoff: `{cutoff:.3f}` · Recon ceiling: `{f'{recon:.3f}' if recon>0 else 'N/A'}`")
            if recon==0.0: st.error(f"🚫 {campus}: Absolute no-appeal policy.")
            elif final_upg<=cutoff: st.success(f"✅ Qualified ({final_upg:.3f} ≤ {cutoff:.3f}).")
            elif final_upg<=recon: st.warning(f"📋 Recon-eligible: UPG {final_upg:.3f} within window ({cutoff:.3f}–{recon:.3f}). Not guaranteed.")
            else: st.error(f"❌ UPG {final_upg:.3f} exceeds recon ceiling {recon:.3f}.")

    st.markdown("<br><br>",unsafe_allow_html=True)
    r1,r2,r3=st.columns([1,2,1])
    with r2:
        st.markdown('<div style="text-align:center;font-family:var(--font-body);font-size:0.8rem;color:var(--fg2);margin-bottom:10px;">Generate a fresh set — competencies and settings preserved.</div>',unsafe_allow_html=True)
        if st.button("🔄 Generate Fresh Items & Reset",use_container_width=True,type="secondary"):
            for k in ['user_answers_math','user_answers_sci','submitted','test_data','flagged_items','math_start_time','sci_start_time','elapsed_math','elapsed_sci']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
