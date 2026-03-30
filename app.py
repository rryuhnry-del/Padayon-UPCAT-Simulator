import streamlit as st
import google.generativeai as genai
import json
import time
import math
import numpy as np

# ==========================================
# 🛡️ SESSION STATE INIT
# ==========================================
defaults = {
    'user_answers_math': {}, 'user_answers_sci': {},
    'submitted': False, 'test_data': None,
    'generation_error': None,
    'flagged_items': set(),
    'font_size': 'medium', 'high_contrast': False,
    'active_subtest': 'math',
    'math_started': False, 'sci_started': False,
    'math_submitted': False, 'sci_submitted': False,
    'math_start_time': None, 'sci_start_time': None,
    'elapsed_math': 0, 'elapsed_sci': 0,
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
    page_title="Padayon! UPCAT Agham at Matematika",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

FONT_SIZES = {'small': '0.85rem', 'medium': '1.0rem', 'large': '1.125rem', 'x-large': '1.25rem'}
fs = FONT_SIZES.get(st.session_state.get('font_size', 'medium'), '1.0rem')

# ==========================================
# 🎨 DARK MODE CSS (ONLY)
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;0,700;0,900;1,400;1,600&display=swap');

:root {{
  /* Core Dark Palette */
  --bg-base:      #0d1117;
  --bg-surface:   #161b22;
  --bg-elevated:  #1c2333;
  --bg-overlay:   #21262d;
  --bg-subtle:    #30363d;

  /* Math accent: Indigo/Blue */
  --math-primary: #58a6ff;
  --math-dim:     #1f3352;
  --math-glow:    rgba(88,166,255,0.12);

  /* Science accent: Teal/Cyan */
  --sci-primary:  #39d0c5;
  --sci-dim:      #0d2e2c;
  --sci-glow:     rgba(57,208,197,0.12);

  /* Status */
  --green:        #3fb950;
  --green-dim:    #0d2d1a;
  --red:          #f85149;
  --red-dim:      #2d1b1b;
  --amber:        #d29922;
  --amber-dim:    #2d2209;
  --purple:       #bc8cff;

  /* Typography */
  --fg-primary:   #e6edf3;
  --fg-secondary: #8b949e;
  --fg-muted:     #484f58;
  --fg-on-dark:   #ffffff;

  /* Borders */
  --border:       #30363d;
  --border-mid:   #21262d;
  --border-subtle:#161b22;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.3);
  --shadow-lg: 0 12px 32px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);

  /* Radii */
  --r-sm: 6px;
  --r:    10px;
  --r-lg: 14px;
  --r-xl: 20px;

  /* Fonts */
  --font-display: 'Crimson Pro', Georgia, serif;
  --font-body:    'Inter', -apple-system, sans-serif;
  --font-mono:    'JetBrains Mono', 'Courier New', monospace;
  --base-fs:      {fs};

  --transition: 0.18s cubic-bezier(0.4,0,0.2,1);
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ── Streamlit overrides ── */
.stApp, body {{
  background: var(--bg-base) !important;
  color: var(--fg-primary) !important;
  font-family: var(--font-body) !important;
  font-size: var(--base-fs) !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
  padding-top: 1rem !important;
  padding-bottom: 5rem !important;
  max-width: 1380px !important;
}}

h1,h2,h3,h4,h5,h6 {{
  font-family: var(--font-display) !important;
  color: var(--fg-primary) !important;
  font-weight: 700 !important;
}}
p, li, span {{ font-family: var(--font-body); line-height: 1.7; }}
.stMarkdown, .stText {{ color: var(--fg-primary) !important; }}

*:focus-visible {{
  outline: 2px solid var(--math-primary) !important;
  outline-offset: 2px !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: var(--bg-surface) !important;
  border-right: 1px solid var(--border) !important;
}}
section[data-testid="stSidebar"] > div {{ padding: 0 !important; }}
section[data-testid="stSidebar"] * {{ color: var(--fg-secondary) !important; }}
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] label {{
  color: var(--fg-primary) !important;
}}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] textarea {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  color: var(--fg-primary) !important;
  border-radius: var(--r-sm) !important;
}}
section[data-testid="stSidebar"] hr {{
  border-color: var(--border) !important;
  margin: 14px 0 !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
  background: var(--bg-elevated) !important;
  border-color: var(--border) !important;
  color: var(--fg-primary) !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] * {{
  color: var(--fg-primary) !important;
  background: var(--bg-elevated) !important;
}}

.sb-brand {{
  background: linear-gradient(135deg, var(--bg-elevated), var(--bg-overlay));
  border-bottom: 1px solid var(--border);
  padding: 24px 20px 18px;
  text-align: center;
  margin-bottom: 2px;
}}
.sb-brand img {{ filter: drop-shadow(0 2px 12px rgba(88,166,255,0.35)); }}
.sb-brand .sb-title {{
  font-family: var(--font-display) !important;
  font-size: 0.95rem; font-style: italic;
  color: var(--fg-primary) !important;
  margin-top: 10px; display: block;
}}
.sb-brand .sb-sub {{
  font-family: var(--font-mono);
  font-size: 0.56rem; letter-spacing: 0.18em;
  color: var(--fg-muted) !important;
  text-transform: uppercase; margin-top: 5px;
}}
.sb-section {{
  font-family: var(--font-mono) !important;
  font-size: 0.58rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--fg-muted) !important;
  display: block; padding: 14px 18px 6px;
  border-top: 1px solid var(--border-mid);
  margin-top: 6px;
}}

/* ── Buttons ── */
.stButton > button {{
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  border-radius: var(--r-sm) !important;
  transition: all var(--transition) !important;
  min-height: 40px !important;
  letter-spacing: 0.01em !important;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 0 0 1px rgba(88,166,255,0.2), 0 4px 12px rgba(29,78,216,0.4) !important;
}}
.stButton > button[kind="primary"]:hover {{
  background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
  box-shadow: 0 0 0 1px rgba(88,166,255,0.35), 0 8px 20px rgba(29,78,216,0.5) !important;
  transform: translateY(-1px) !important;
}}
.stButton > button[kind="secondary"] {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  color: var(--fg-primary) !important;
}}
.stButton > button[kind="secondary"]:hover {{
  background: var(--bg-overlay) !important;
  border-color: var(--math-primary) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 2px; background: var(--bg-surface);
  border-radius: var(--r); padding: 3px;
  border: 1px solid var(--border) !important;
  flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
  font-family: var(--font-body) !important;
  font-size: 0.8rem !important; font-weight: 500 !important;
  padding: 8px 14px !important;
  border-radius: var(--r-sm) !important;
  background: transparent !important;
  color: var(--fg-secondary) !important;
  border: none !important;
  transition: all var(--transition) !important;
}}
.stTabs [aria-selected="true"] {{
  background: var(--bg-elevated) !important;
  color: var(--math-primary) !important;
  box-shadow: var(--shadow-sm) !important;
}}

/* ── Radio (answer choices) ── */
.stRadio > label {{ display: none !important; }}
.stRadio [data-testid="stWidgetLabel"] {{ display: none !important; }}
.stRadio > div {{
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
}}
.stRadio > div > label {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  padding: 10px 14px !important;
  cursor: pointer !important;
  transition: all var(--transition) !important;
  font-family: var(--font-body) !important;
  font-size: var(--base-fs) !important;
  line-height: 1.65 !important;
  color: var(--fg-primary) !important;
}}
.stRadio > div > label:hover {{
  border-color: var(--math-primary) !important;
  background: var(--math-glow) !important;
  transform: translateX(3px) !important;
}}
.stRadio > div > label[data-checked="true"] {{
  border-color: var(--green) !important;
  background: var(--green-dim) !important;
  color: #3fb950 !important;
}}

/* ── Expanders ── */
.streamlit-expanderHeader {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--fg-primary) !important;
  font-family: var(--font-body) !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  min-height: 44px !important;
  padding: 0 14px !important;
}}
.streamlit-expanderContent {{
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--r-sm) var(--r-sm) !important;
  padding: 14px !important;
}}

/* ── Alert / info boxes ── */
.stAlert {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--fg-primary) !important;
}}

/* ── Select / Number ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input {{
  background: var(--bg-elevated) !important;
  border-color: var(--border) !important;
  color: var(--fg-primary) !important;
  border-radius: var(--r-sm) !important;
}}
[data-baseweb="popover"] * {{
  background: var(--bg-overlay) !important;
  color: var(--fg-primary) !important;
  border-color: var(--border) !important;
}}

/* ── Metric ── */
[data-testid="metric-container"] {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 14px !important;
}}
[data-testid="metric-container"] label {{
  color: var(--fg-secondary) !important;
  font-size: 0.75rem !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
  color: var(--math-primary) !important;
  font-family: var(--font-display) !important;
}}

/* ── Progress ── */
[data-testid="stProgress"] > div > div {{
  background: var(--bg-subtle) !important;
  border-radius: 4px;
}}
[data-testid="stProgress"] > div > div > div {{
  background: linear-gradient(90deg, var(--math-primary), var(--sci-primary)) !important;
  border-radius: 4px;
}}

/* ==========================================
   CUSTOM COMPONENTS
   ========================================== */

/* ── Hero ── */
.hero-shell {{
  position: relative; border-radius: var(--r-xl);
  overflow: hidden; margin-bottom: 20px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
}}
.hero-bg {{
  position: absolute; inset: 0;
  background: linear-gradient(135deg,
    #060d1a 0%, #0b1829 35%,
    #0a2040 65%, #081e3c 100%);
}}
.hero-grid {{
  position: absolute; inset: 0; opacity: 0.025;
  background-image:
    linear-gradient(rgba(255,255,255,1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px);
  background-size: 36px 36px;
}}
.hero-glow-math {{
  position: absolute; width: 400px; height: 400px;
  border-radius: 50%; top: -100px; right: -50px;
  background: radial-gradient(circle, rgba(88,166,255,0.12) 0%, transparent 70%);
}}
.hero-glow-sci {{
  position: absolute; width: 300px; height: 300px;
  border-radius: 50%; bottom: -80px; left: 10%;
  background: radial-gradient(circle, rgba(57,208,197,0.09) 0%, transparent 70%);
}}
.hero-inner {{
  position: relative; z-index: 2; padding: 42px 56px;
}}
.hero-pill {{
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(88,166,255,0.1);
  border: 1px solid rgba(88,166,255,0.25);
  color: var(--math-primary) !important;
  font-family: var(--font-mono);
  font-size: 0.62rem; font-weight: 600;
  letter-spacing: 0.14em; text-transform: uppercase;
  padding: 4px 12px; border-radius: 20px;
  margin-bottom: 16px; width: fit-content;
}}
.hero-title {{
  font-family: var(--font-display) !important;
  font-size: clamp(1.8rem, 3.5vw, 3rem) !important;
  font-weight: 900 !important;
  color: var(--fg-on-dark) !important;
  line-height: 1.08 !important;
  margin-bottom: 12px !important;
  letter-spacing: -0.025em;
}}
.hero-title em {{ font-style: italic; color: var(--math-primary) !important; }}
.hero-sub {{
  font-family: var(--font-body); font-size: 0.88rem;
  color: rgba(255,255,255,0.5); line-height: 1.75;
  max-width: 600px;
}}
.hero-divider {{
  height: 1px; background: rgba(255,255,255,0.07);
  margin: 22px 0;
}}
.hero-stats {{
  display: flex; gap: 32px; flex-wrap: wrap;
}}
.h-stat-num {{
  font-family: var(--font-display); font-size: 1.65rem;
  font-weight: 900; color: var(--math-primary); line-height: 1;
}}
.h-stat-lbl {{
  font-family: var(--font-mono); font-size: 0.60rem;
  color: rgba(255,255,255,0.35); text-transform: uppercase;
  letter-spacing: 0.1em; margin-top: 3px;
}}

/* ── Notice boxes ── */
.notice {{
  display: flex; gap: 10px; align-items: flex-start;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-left: 3px solid var(--math-primary);
  border-radius: var(--r); padding: 12px 16px;
  font-family: var(--font-body); font-size: 0.83rem;
  color: var(--fg-secondary); line-height: 1.65;
  margin-bottom: 16px;
}}
.notice.warn {{ border-left-color: var(--amber); }}
.notice.danger {{ border-left-color: var(--red); }}
.notice.sci {{ border-left-color: var(--sci-primary); }}
.notice strong {{ color: var(--fg-primary); }}
.notice-icon {{ font-size: 1rem; flex-shrink: 0; margin-top: 1px; }}

/* ── Section header ── */
.sec-hdr {{
  display: flex; align-items: center; gap: 12px;
  margin: 28px 0 16px;
}}
.sec-hdr-text {{
  font-family: var(--font-display) !important;
  font-size: 1.3rem !important; font-weight: 700 !important;
  color: var(--fg-primary) !important; white-space: nowrap;
}}
.sec-hdr-line {{
  flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--border), transparent);
}}

/* ── Subtest info cards ── */
.subtest-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px; }}
.subtest-card {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 20px 22px;
  transition: all var(--transition);
}}
.subtest-card.math {{ border-top: 2px solid var(--math-primary); }}
.subtest-card.sci {{ border-top: 2px solid var(--sci-primary); }}
.subtest-card:hover {{ border-color: var(--bg-subtle); background: var(--bg-overlay); }}
.sc-icon {{ font-size: 1.6rem; margin-bottom: 8px; }}
.sc-title {{
  font-family: var(--font-display); font-size: 1.15rem;
  font-weight: 700; color: var(--fg-primary); margin-bottom: 4px;
}}
.sc-meta {{
  font-family: var(--font-mono); font-size: 0.62rem;
  color: var(--fg-muted); letter-spacing: 0.06em;
  text-transform: uppercase; margin-bottom: 8px;
}}
.sc-detail {{
  font-family: var(--font-body); font-size: 0.78rem;
  color: var(--fg-secondary); line-height: 1.6;
}}

/* ── Competency input ── */
.comp-card {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 14px 18px 10px; margin-bottom: 8px;
}}
.comp-label {{
  font-family: var(--font-mono); font-size: 0.60rem;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--fg-muted); margin-bottom: 6px; display: block;
}}
.comp-label.math {{ color: var(--math-primary); }}
.comp-label.sci {{ color: var(--sci-primary); }}

/* ── Progress bar ── */
.prog-wrap {{ margin: 8px 0 14px; }}
.prog-row {{
  display: flex; justify-content: space-between;
  font-family: var(--font-mono); font-size: 0.62rem;
  color: var(--fg-muted); margin-bottom: 5px;
}}
.prog-track {{
  height: 5px; background: var(--bg-subtle);
  border-radius: 3px; overflow: hidden;
}}
.prog-fill-math {{ height: 100%; border-radius: 3px; background: linear-gradient(90deg, #1d4ed8, var(--math-primary)); transition: width 0.5s ease; }}
.prog-fill-sci {{ height: 100%; border-radius: 3px; background: linear-gradient(90deg, #0d5a55, var(--sci-primary)); transition: width 0.5s ease; }}

/* ── Question cards ── */
.q-card {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-left: 3px solid var(--math-primary);
  border-radius: var(--r);
  padding: 18px 22px;
  margin-bottom: 10px;
  transition: border-color var(--transition), box-shadow var(--transition);
  position: relative;
}}
.q-card.sci {{ border-left-color: var(--sci-primary); }}
.q-card.answered {{ border-left-color: var(--green); }}
.q-card.flagged {{ border-left-color: var(--amber); }}
.q-card:hover {{ box-shadow: var(--shadow-sm); }}

.q-meta {{
  display: flex; align-items: center; gap: 6px;
  margin-bottom: 12px; flex-wrap: wrap;
}}
.q-num {{
  font-family: var(--font-mono); font-size: 0.58rem;
  font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--math-primary);
  background: var(--math-glow);
  padding: 2px 8px; border-radius: 4px;
  border: 1px solid rgba(88,166,255,0.2);
}}
.q-num.sci {{ color: var(--sci-primary); background: var(--sci-glow); border-color: rgba(57,208,197,0.2); }}
.q-tag {{
  font-family: var(--font-mono); font-size: 0.54rem;
  font-weight: 500; letter-spacing: 0.06em;
  padding: 2px 8px; border-radius: 4px;
  border: 1px solid var(--border);
  color: var(--fg-muted);
  background: var(--bg-overlay);
}}
.q-stem {{
  font-family: var(--font-body); font-size: var(--base-fs);
  line-height: 1.85; color: var(--fg-primary);
  margin-bottom: 14px;
}}
/* LaTeX rendering */
.q-stem .katex, .q-stem .katex * {{ color: var(--fg-primary) !important; }}
.q-stem .katex-display {{ overflow-x: auto; overflow-y: hidden; }}

/* Science stimuli */
.sci-passage {{
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--sci-primary);
  border-radius: var(--r-sm);
  padding: 14px 18px; margin-bottom: 12px;
  font-family: var(--font-body); font-size: 0.88rem;
  line-height: 1.85; color: var(--fg-secondary);
  max-height: 260px; overflow-y: auto;
}}
.sci-data-box {{
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--amber);
  border-radius: var(--r-sm);
  padding: 14px 18px; margin-bottom: 12px;
  font-family: var(--font-mono); font-size: 0.80rem;
  line-height: 1.7; color: var(--fg-secondary);
  overflow-x: auto;
}}
.sci-table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
.sci-table th {{
  background: var(--bg-overlay); color: var(--fg-primary);
  padding: 8px 12px; font-size: 0.72rem; text-align: left;
  border-bottom: 1px solid var(--border); font-weight: 600;
  letter-spacing: 0.04em; font-family: var(--font-mono);
}}
.sci-table td {{
  padding: 7px 12px; border-bottom: 1px solid var(--border-mid);
  color: var(--fg-secondary); font-family: var(--font-body);
}}
.sci-table tr:last-child td {{ border-bottom: none; }}
.sci-table tr:hover td {{ background: var(--bg-overlay); }}

.stim-label {{
  font-family: var(--font-mono); font-size: 0.58rem;
  letter-spacing: 0.14em; text-transform: uppercase;
  margin-bottom: 6px; display: flex; align-items: center; gap: 6px;
}}
.stim-label.passage {{ color: var(--sci-primary); }}
.stim-label.data {{ color: var(--amber); }}
.stim-label.diagram {{ color: var(--purple); }}

/* ── Item navigator ── */
.item-nav {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 12px 14px; margin-bottom: 16px;
  position: sticky; top: 10px; z-index: 99;
  box-shadow: var(--shadow-md);
}}
.nav-title {{
  font-family: var(--font-mono); font-size: 0.58rem;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--fg-muted); margin-bottom: 8px;
}}
.nav-grid {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.nav-dot {{
  min-width: 30px; height: 26px;
  border-radius: 5px;
  display: inline-flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-size: 0.58rem; font-weight: 700;
  cursor: pointer;
  background: var(--bg-overlay); color: var(--fg-muted);
  border: 1px solid var(--border);
  transition: all var(--transition);
}}
.nav-dot:hover {{ border-color: var(--math-primary); color: var(--math-primary); transform: scale(1.08); }}
.nav-dot.answered-m {{ background: var(--math-dim); color: var(--math-primary); border-color: var(--math-primary); }}
.nav-dot.answered-s {{ background: var(--sci-dim); color: var(--sci-primary); border-color: var(--sci-primary); }}
.nav-dot.flagged {{ background: var(--amber-dim); color: var(--amber); border-color: var(--amber); }}

/* ── Timer ── */
.timer-chip {{
  position: fixed; top: 16px; right: 20px; z-index: 99999;
  font-family: var(--font-mono); font-size: 0.9rem; font-weight: 700;
  padding: 7px 16px; border-radius: 24px;
  border: 1px solid rgba(88,166,255,0.35);
  background: var(--bg-surface);
  color: var(--math-primary);
  box-shadow: 0 4px 16px rgba(0,0,0,0.5), 0 0 20px rgba(88,166,255,0.08);
  letter-spacing: 0.04em;
  transition: all 0.3s;
}}
.timer-chip.sci {{ color: var(--sci-primary); border-color: rgba(57,208,197,0.35); }}
.timer-chip.warn {{ color: var(--amber); border-color: rgba(210,153,34,0.5); }}
.timer-chip.danger {{ color: var(--red); border-color: rgba(248,81,73,0.5); animation: pulse-red 1s infinite; }}

@keyframes pulse-red {{
  0%,100% {{ opacity: 1; }}
  50% {{ opacity: 0.7; }}
}}

/* ── Stat pills ── */
.stat-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0; }}
.stat-pill {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 10px 16px; flex: 1; min-width: 100px;
  text-align: center;
}}
.sp-num {{ font-family: var(--font-display); font-size: 1.4rem; font-weight: 900; line-height: 1; }}
.sp-lbl {{ font-family: var(--font-mono); font-size: 0.56rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg-muted); margin-top: 3px; }}

/* ── Results hero ── */
.res-hero {{
  background: linear-gradient(135deg, #060d1a 0%, #0b1829 40%, #0a1f3e 100%);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: 48px; text-align: center;
  position: relative; overflow: hidden;
  margin-bottom: 20px;
  box-shadow: var(--shadow-lg);
}}
.res-hero-glow {{
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at center, rgba(88,166,255,0.08) 0%, transparent 65%);
  pointer-events: none;
}}
.upg-label {{
  font-family: var(--font-mono); font-size: 0.62rem;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: rgba(255,255,255,0.35); margin-bottom: 8px;
  position: relative; z-index: 1;
}}
.upg-val {{
  font-family: var(--font-display);
  font-size: clamp(3.5rem, 8vw, 6rem);
  font-weight: 900; line-height: 1;
  position: relative; z-index: 1;
  letter-spacing: -0.03em;
}}
.upg-verdict {{
  font-family: var(--font-body); font-size: 0.95rem;
  color: rgba(255,255,255,0.6); margin-top: 10px;
  position: relative; z-index: 1;
}}

/* ── Sub-UPG cards ── */
.upg-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px; }}
.upg-card {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 20px 24px;
  position: relative; overflow: hidden;
}}
.upg-card.math {{ border-top: 2px solid var(--math-primary); }}
.upg-card.sci {{ border-top: 2px solid var(--sci-primary); }}
.upg-card-shimmer {{
  position: absolute; inset: 0; pointer-events: none;
}}
.upg-card.math .upg-card-shimmer {{
  background: radial-gradient(ellipse at top right, rgba(88,166,255,0.06) 0%, transparent 60%);
}}
.upg-card.sci .upg-card-shimmer {{
  background: radial-gradient(ellipse at top right, rgba(57,208,197,0.06) 0%, transparent 60%);
}}
.upg-card-title {{
  font-family: var(--font-mono); font-size: 0.60rem;
  letter-spacing: 0.16em; text-transform: uppercase;
  margin-bottom: 8px;
}}
.upg-card.math .upg-card-title {{ color: var(--math-primary); }}
.upg-card.sci .upg-card-title {{ color: var(--sci-primary); }}
.upg-card-value {{
  font-family: var(--font-display); font-size: 2.4rem;
  font-weight: 900; line-height: 1; margin-bottom: 4px;
}}
.upg-card.math .upg-card-value {{ color: var(--math-primary); }}
.upg-card.sci .upg-card-value {{ color: var(--sci-primary); }}
.upg-card-sub {{
  font-family: var(--font-body); font-size: 0.78rem;
  color: var(--fg-secondary); line-height: 1.55;
}}
.upg-breakdown {{ margin-top: 12px; }}
.upg-br-row {{
  display: flex; justify-content: space-between;
  padding: 5px 0; border-bottom: 1px solid var(--border-mid);
  font-family: var(--font-body); font-size: 0.78rem;
}}
.upg-br-row:last-child {{ border-bottom: none; }}
.upg-br-lbl {{ color: var(--fg-secondary); }}
.upg-br-val {{ font-family: var(--font-mono); font-weight: 700; font-size: 0.78rem; }}

/* ── Metrics grid ── */
.metrics-grid {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 16px; }}
.metric-card {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 16px 14px; text-align: center;
  transition: transform var(--transition), box-shadow var(--transition);
}}
.metric-card:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-md); }}
.metric-card-val {{
  font-family: var(--font-display); font-size: 1.7rem;
  font-weight: 900; line-height: 1; margin-bottom: 4px;
}}
.metric-card-lbl {{
  font-family: var(--font-mono); font-size: 0.55rem;
  letter-spacing: 0.11em; text-transform: uppercase;
  color: var(--fg-muted);
}}
.metric-card-sub {{
  font-family: var(--font-body); font-size: 0.71rem;
  color: var(--fg-secondary); margin-top: 3px;
}}

/* ── Score panel ── */
.score-panel {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r); padding: 18px 22px;
}}
.score-panel h4 {{
  font-family: var(--font-display) !important;
  font-size: 1.0rem !important; margin-bottom: 12px !important;
  padding-bottom: 10px !important;
  border-bottom: 1px solid var(--border) !important;
  color: var(--fg-primary) !important;
}}
.s-row {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 7px 0; border-bottom: 1px solid var(--border-mid);
  font-family: var(--font-body); font-size: 0.83rem;
}}
.s-row:last-child {{ border-bottom: none; }}
.s-lbl {{ color: var(--fg-secondary); }}
.s-val {{ font-family: var(--font-mono); font-weight: 700; font-size: 0.80rem; }}
.s-val.c {{ color: var(--green); }}
.s-val.w {{ color: var(--red); }}
.s-val.g {{ color: var(--math-primary); }}

/* ── Skill heatmap ── */
.heat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }}
.heat-row {{
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-body); font-size: 0.76rem;
  padding: 7px 10px; border-radius: var(--r-sm);
  border: 1px solid var(--border);
  background: var(--bg-surface);
}}
.heat-bar-out {{ flex: 1; height: 4px; background: var(--bg-subtle); border-radius: 2px; overflow: hidden; }}
.heat-bar-in {{ height: 100%; border-radius: 2px; transition: width 0.7s ease; }}
.heat-bar-in.strong {{ background: var(--green); }}
.heat-bar-in.mid {{ background: var(--amber); }}
.heat-bar-in.weak {{ background: var(--red); }}
.heat-pct {{ font-family: var(--font-mono); font-size: 0.58rem; font-weight: 700; min-width: 30px; text-align: right; }}

/* ── Campus admission cards ── */
.campus-card {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r-lg); overflow: hidden;
  margin-bottom: 14px;
}}
.campus-hdr {{
  padding: 14px 20px;
  background: linear-gradient(135deg, #0d2e1a, #0f3b1e);
  border-bottom: 1px solid var(--border);
}}
.campus-hdr.fail {{
  background: linear-gradient(135deg, #2d1b1b, #3b1f1f);
}}
.campus-hdr h4 {{ color: var(--fg-primary) !important; font-size: 0.95rem !important; margin-bottom: 4px !important; }}
.campus-hdr p {{ color: var(--fg-secondary) !important; font-family: var(--font-mono); font-size: 0.64rem !important; }}
.campus-body {{ padding: 12px 20px; }}
.prog-row {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 9px 0; border-bottom: 1px solid var(--border-mid);
  font-family: var(--font-body); font-size: 0.83rem;
}}
.prog-row:last-child {{ border-bottom: none; }}
.prog-name {{ font-weight: 600; color: var(--fg-primary); }}
.prog-sub {{ font-family: var(--font-mono); font-size: 0.60rem; color: var(--fg-muted); margin-top: 2px; }}
.badge {{
  font-family: var(--font-mono); font-size: 0.62rem; font-weight: 700;
  padding: 3px 10px; border-radius: 5px;
}}
.badge.pass {{ color: var(--green); background: var(--green-dim); border: 1px solid rgba(63,185,80,0.3); }}
.badge.risk {{ color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(210,153,34,0.3); }}
.badge.fail {{ color: var(--red); background: var(--red-dim); border: 1px solid rgba(248,81,73,0.3); }}

/* ── Feedback boxes ── */
.fb-box {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 18px 22px; margin-bottom: 12px;
  font-family: var(--font-body); font-size: var(--base-fs);
  line-height: 1.8; color: var(--fg-secondary);
}}
.fb-box.math {{ border-left: 3px solid var(--math-primary); }}
.fb-box.sci {{ border-left: 3px solid var(--sci-primary); }}
.fb-box.green {{ border-left: 3px solid var(--green); }}
.fb-box.amber {{ border-left: 3px solid var(--amber); }}
.fb-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }}
.fb-mini {{
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--r-sm); padding: 12px 14px;
}}
.fb-mini-title {{
  font-family: var(--font-mono); font-size: 0.57rem;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--fg-muted); margin-bottom: 6px;
}}
.fb-mini-body {{
  font-family: var(--font-body); font-size: 0.80rem;
  color: var(--fg-secondary); line-height: 1.6;
}}

/* ── Item review ── */
.ir-correct {{
  background: var(--green-dim);
  border: 1px solid rgba(63,185,80,0.3);
  border-radius: var(--r-sm); padding: 9px 14px;
  font-family: var(--font-body); font-size: var(--base-fs);
  color: var(--green); margin: 3px 0;
}}
.ir-wrong {{
  background: var(--red-dim);
  border: 1px solid rgba(248,81,73,0.3);
  border-radius: var(--r-sm); padding: 9px 14px;
  font-family: var(--font-body); font-size: var(--base-fs);
  color: var(--red); margin: 3px 0;
}}
.ir-option {{
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--r-sm); padding: 9px 14px;
  font-family: var(--font-body); font-size: var(--base-fs);
  color: var(--fg-secondary); margin: 3px 0;
}}

/* ── Responsive ── */
@media (max-width: 768px) {{
  .hero-inner {{ padding: 24px 22px; }}
  .metrics-grid {{ grid-template-columns: repeat(2,1fr); }}
  .fb-grid {{ grid-template-columns: 1fr; }}
  .heat-grid {{ grid-template-columns: 1fr; }}
  .subtest-grid {{ grid-template-columns: 1fr; }}
  .upg-row {{ grid-template-columns: 1fr; }}
  .hero-stats {{ gap: 20px; }}
}}
@media print {{ section[data-testid="stSidebar"], .timer-chip, .stButton {{ display: none !important; }} }}
@media (prefers-reduced-motion: reduce) {{ *,*::before,*::after {{ animation: none !important; transition-duration: 0.01ms !important; }} }}
</style>
""", unsafe_allow_html=True)

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
    "Public — Barangay / Community High School": {"modifier": 0.09, "label": "Barangay NHS (+bonus)", "palugit": True},
    "Public — Vocational / Technical": {"modifier": 0.06, "label": "Vocational Tech", "palugit": True},
    "Private — International School (IB, AP, Cambridge)": {"modifier": 0.08, "label": "International Private", "palugit": False},
    "Private — University Affiliated / Sectarian Elite": {"modifier": -0.04, "label": "Sectarian Elite", "palugit": False},
    "Private — Regular Sectarian": {"modifier": -0.08, "label": "Private Sectarian", "palugit": False},
    "Private — Non-Sectarian": {"modifier": -0.12, "label": "Private Non-Sectarian", "palugit": False},
}

CAMPUS_DATA = {
    "UP Diliman":           {"cutoff": 2.20, "recon": 0.0,   "note": "Strictest. No appeals. 40,000 applicants."},
    "UP Manila":            {"cutoff": 2.10, "recon": 2.580, "note": "Health sciences hub. Recon available."},
    "UP Los Baños":         {"cutoff": 2.30, "recon": 2.800, "note": "Agri/forestry leader. Recon for 1st choice."},
    "UP Baguio":            {"cutoff": 2.50, "recon": 2.700, "note": "Strong arts & sciences."},
    "UP Cebu":              {"cutoff": 2.60, "recon": 2.800, "note": "Growing campus."},
    "UP Mindanao":          {"cutoff": 2.60, "recon": 2.800, "note": "Priority for Mindanaoan applicants."},
    "UP Visayas (Iloilo)":  {"cutoff": 2.70, "recon": 2.700, "note": "Marine & fisheries focus."},
    "UP Open University":   {"cutoff": 2.80, "recon": 2.800, "note": "Distance learning format."},
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
    <div class='sb-brand'>
        <img src='https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/University_of_the_Philippines_seal.svg/1200px-University_of_the_Philippines_seal.svg.png'
             width='58' alt='UP seal'/>
        <span class='sb-title'>Padayon! Agham at Matematika</span>
        <span class='sb-sub'>UPCAT Elite Simulator · v2.0</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sb-section">♿ Display</span>', unsafe_allow_html=True)
    font_size = st.select_slider("Text Size", options=["small","medium","large","x-large"],
        value=st.session_state.get('font_size','medium'))
    if font_size != st.session_state.get('font_size'):
        st.session_state['font_size'] = font_size; st.rerun()
    show_timer = st.checkbox("Show Countdown Timer", value=True)
    show_nav = st.checkbox("Show Item Navigator", value=True)
    enable_flag = st.checkbox("Enable Item Flagging 🚩", value=True)

    st.markdown('<span class="sb-section">🔑 API Config</span>', unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...",
        help="Get free key at aistudio.google.com")
    gemini_model = st.selectbox("Model", [
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview",
    ], index=0)

    st.markdown('<span class="sb-section">🏫 School Type</span>', unsafe_allow_html=True)
    jhs_type = st.selectbox("JHS School", list(SCHOOL_TIERS.keys()), index=5)
    shs_type = st.selectbox("SHS School", list(SCHOOL_TIERS.keys()), index=5)
    jhs_mod = SCHOOL_TIERS[jhs_type]["modifier"]
    shs_mod = SCHOOL_TIERS[shs_type]["modifier"]
    palugit_jhs = SCHOOL_TIERS[jhs_type]["palugit"]
    palugit_shs = SCHOOL_TIERS[shs_type]["palugit"]
    if palugit_jhs or palugit_shs:
        st.caption(f"✅ Palugit active — JHS {jhs_mod:+.2f} / SHS {shs_mod:+.2f}")

    st.markdown('<span class="sb-section">📐 Math Grades (G8–G11)</span>', unsafe_allow_html=True)
    st.caption("DepEd Final Grade (60–100). UPCAT uses G8–G11.")
    c1, c2 = st.columns(2)
    with c1:
        g8_math     = st.number_input("G8 Math",       60.0, 100.0, 87.0, 0.5)
        g9_math     = st.number_input("G9 Math",       60.0, 100.0, 87.0, 0.5)
        g10_math    = st.number_input("G10 Math",      60.0, 100.0, 88.0, 0.5)
        g11_precalc = st.number_input("Pre-Calculus",  60.0, 100.0, 88.0, 0.5)
    with c2:
        g11_calc    = st.number_input("Basic Calculus",60.0, 100.0, 87.0, 0.5)
        g11_stats   = st.number_input("Stats & Prob",  60.0, 100.0, 88.0, 0.5)
        g11_genmath = st.number_input("Gen. Math",     60.0, 100.0, 88.0, 0.5)

    st.markdown('<span class="sb-section">🔬 Science Grades (G8–G11)</span>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        g8_sci   = st.number_input("G8 Science",  60.0, 100.0, 87.0, 0.5)
        g9_sci   = st.number_input("G9 Science",  60.0, 100.0, 87.0, 0.5)
        g10_sci  = st.number_input("G10 Science", 60.0, 100.0, 88.0, 0.5)
        g11_bio1 = st.number_input("Gen Bio 1",   60.0, 100.0, 88.0, 0.5)
    with c4:
        g11_bio2  = st.number_input("Gen Bio 2",  60.0, 100.0, 88.0, 0.5)
        g11_earth = st.number_input("Earth Sci",  60.0, 100.0, 87.0, 0.5)

    st.markdown('<span class="sb-section">🎯 Campus & Program</span>', unsafe_allow_html=True)
    campus_1 = st.selectbox("1st Choice Campus", list(CAMPUS_DATA.keys()), index=0)
    c1_p1 = st.selectbox("Program Priority 1", get_all_programs(campus_1), key="c1p1")
    c1_p2 = st.selectbox("Program Priority 2", get_all_programs(campus_1), key="c1p2")
    c1_p3 = st.selectbox("Program Priority 3", get_all_programs(campus_1), key="c1p3")
    campus_2 = st.selectbox("2nd Choice Campus", list(CAMPUS_DATA.keys()), index=2)
    c2_p1 = st.selectbox("Program Priority 1", get_all_programs(campus_2), key="c2p1")
    c2_p2 = st.selectbox("Program Priority 2", get_all_programs(campus_2), key="c2p2")
    c2_p3 = st.selectbox("Program Priority 3", get_all_programs(campus_2), key="c2p3")

    st.markdown('<span class="sb-section">⚙️ Sim Parameters</span>', unsafe_allow_html=True)
    math_items = st.slider("Math Items", 10, 50, 25, 5,
        help="Full UPCAT Math = 50 items / 60 min. No calculator.")
    sci_items  = st.slider("Science Items", 10, 45, 20, 5,
        help="Full UPCAT Science = 45 items / 45 min.")
    difficulty = st.select_slider("Difficulty",
        options=["Standard","Competitive","Brutal","Massacre"],
        value="Competitive",
        help="Massacre = top ~3% ceiling. 135,000+ competitors.")

# ==========================================
# 🧠 PROMPT CONFIG
# ==========================================
DIFF_MAP = {
    "Standard":    ("Standard difficulty: JHS-dominant items. Solvable in under 60s each. Distractors are common errors. Science items: stock knowledge, clear factual basis. Roughly 50% of UPCAT-standard applicants should score ≥60%.", 0.52, 0.16),
    "Competitive": ("Competitive difficulty: ~top 20% ceiling. Math requires 2-3 step algebra/geometry. Science mixes recall with data-table analysis. Average prepared student takes 60-90s per item.", 0.44, 0.15),
    "Brutal":      ("Brutal difficulty: ~top 8% ceiling. Items test conceptual depth — not formula memorization. Science includes passage-based data analysis with experimental design questions. Math involves multi-step reasoning without obvious formula entry point.", 0.37, 0.14),
    "Massacre":    ("Massacre difficulty: ~top 2-3% ceiling (UP Diliman Engineering/MBB/CS level). Math items look deceptively simple but require precise conceptual logic. Distractors match common procedural errors exactly. Science has dense experimental data and multi-variable scenarios. Zero items solvable by rote recall alone.", 0.31, 0.13),
}
diff_instruction, MEAN_BASELINE, SIGMA = DIFF_MAP[difficulty]

MATH_TOPIC_WEIGHTS = {
    "Algebra — Linear Equations, Inequalities, Systems": 15,
    "Algebra — Polynomials, Factoring, Rational Expressions": 13,
    "Number Sense — Fractions, Ratios, Percentages, Number Theory": 12,
    "Algebra — Word Problems (Filipino contexts: distance, mixture, work, age)": 10,
    "Geometry — Plane (Triangles, Similarity, Circles, Polygons, Coordinate)": 10,
    "Statistics & Probability (Mean, Median, Mode, Counting, Basic Probability)": 9,
    "Quadratic Equations (Discriminant, Sum/Product of Roots, Applications)": 8,
    "Sequences & Series (Arithmetic, Geometric, nth term, Sum)": 6,
    "Exponents & Logarithms (Laws, Equations, Simplification)": 6,
    "Geometry — Solid (Volume, Surface Area of Common Solids)": 5,
    "Functions & Graphs (Domain/Range, Evaluation, Transformations)": 4,
    "Radicals & Complex Numbers (Simplification, Operations)": 2,
}

SCI_TOPIC_WEIGHTS = {
    "Biology — Cell Biology (Organelles, Cell Division, Membrane Transport)": 10,
    "Biology — Genetics (Mendel, Punnett Squares, Inheritance Patterns, DNA basics)": 8,
    "Biology — Ecology (Food Webs, Biogeochemical Cycles, Ecological Relationships)": 8,
    "Biology — Human Physiology (Organ Systems, Digestion, Circulation, Respiration)": 7,
    "Biology — Evolution & Classification (Natural Selection, Taxonomy, Evidence)": 6,
    "Biology — Plants (Photosynthesis, Transpiration, Plant Tissues)": 5,
    "Earth Science — Geology (Rock Cycle, Plate Tectonics, Geologic Time)": 8,
    "Earth Science — Atmosphere & Weather (Layers, Climate, Pressure, Fronts)": 6,
    "Earth Science — Astronomy (Solar System, Seasons, Stars, Tides)": 5,
    "Earth Science — Hydrosphere (Water Cycle, Oceans, Groundwater)": 4,
    "Chemistry — Atomic Structure & Periodic Table (Trends, Electron Config)": 7,
    "Chemistry — Chemical Bonding & Reactions (Balancing, Reaction Types, pH)": 7,
    "Chemistry — Matter & Properties (States, Physical vs Chemical Changes)": 5,
    "Physics — Mechanics (Newton's Laws, Kinematics, Work-Energy, Momentum)": 6,
    "Physics — Waves, Light & Sound (Wave Properties, Reflection, Refraction)": 4,
    "Physics — Electricity (Circuits, Ohm's Law, Voltage, Current)": 4,
}

MATH_CRITICAL_RULES = """
UPCAT MATH PSYCHOMETRIC RULES — ALL ARE NON-NEGOTIABLE:

1. NO CALCULATOR ALLOWED. Every numerical answer must be reachable via mental math or hand computation in under 90 seconds. If the arithmetic is messy, redesign the numbers.

2. ZERO HINTS ABOUT ANSWER. NEVER label difficulty (easy/medium/hard), NEVER use "clearly", "obviously", "simply", or "just". NEVER phrase options so that one option is obviously longer/more complex (a tell for correct answers). Options must be plausibly similar in length and complexity.

3. NO OBVIOUS CORRECT ANSWER POSITIONING. Vary correct answer keys (A, B, C, D) roughly equally. Do NOT cluster correct answers on B or C.

4. LaTeX MANDATORY. Every mathematical expression, fraction, exponent, radical, inequality, equation MUST be wrapped in LaTeX — inline: $...$, display (standalone equation): $$...$$. Plain text math (like "x^2") is FORBIDDEN. Options must also use LaTeX where needed.

5. DISTRACTOR QUALITY. Each wrong option MUST be the exact numerical/algebraic output of a specific, named error:
   - "SIGN_ERROR" — forgot to flip sign (most common in algebra)
   - "FORMULA_CONFUSION" — used wrong formula
   - "ARITHMETIC_ERROR" — correct method, wrong calculation
   - "CONCEPTUAL_ERROR" — fundamentally wrong approach
   - "INCOMPLETE_SOLUTION" — stopped one step early
   - "WRONG_OPERATION" — divided instead of multiplied, etc.

6. TOPIC DISTRIBUTION (approximate): ~58% JHS algebra/geometry/number sense; ~22% statistics/sequences/exponents/logarithms; ~10% functions/graphing; ~10% trigonometry+SHS combined (rare items, 1-3 max).

7. WORD PROBLEMS: Use realistic Filipino contexts (jeepney/tricycle fares, rice/produce prices, construction dimensions, school settings, Filipino names). Keep setup ≤3 sentences.

8. STEP COUNT: Max 3-4 computational steps per item. UPCAT tests quick reasoning, not marathon computation. If it takes longer than 90 seconds for a prepared student, it is too complex.

9. ANSWER OPTIONS: Must be 4 distinct values/expressions. For numerical answers, options should be in the same order (ascending or descending) so as not to hint at the answer by placement.

10. SOLUTION: Minimum 4 clearly labeled steps. Show every step. Explain WHY each step was taken, not just WHAT was done. Final answer must perfectly match correct_answer field.
"""

SCI_CRITICAL_RULES = """
UPCAT SCIENCE PSYCHOMETRIC RULES — ALL ARE NON-NEGOTIABLE:

1. ~60% PASSAGE OR DATA-BASED. For these items, provide a stimulus (experimental scenario, data table, or diagram-in-text). The stimulus must contain information NECESSARY to answer the question — not mere context. The correct answer must require reading and interpreting the stimulus.

2. NO PURE MEMORIZATION. Even factual items must test APPLICATION. Forbidden: "What organelle is the powerhouse of the cell?" Permitted: "A cell completely deprived of functioning mitochondria would most directly lose its ability to..."

3. DISCIPLINE DISTRIBUTION: Biology ~38%, Earth Science ~26%, Chemistry ~21%, Physics ~15%. For a balanced test, do not write all Biology first.

4. DATA TABLE FORMAT: Use clean HTML table tags (<table><tr><th><td>) within the "stimulus" field. Include 3-5 columns, 4-6 data rows. Column headers must be specific (include units). Data must be internally consistent and scientifically plausible.

5. NO STOICHIOMETRY ARITHMETIC. UPCAT Science tests conceptual chemistry. Do not write items requiring molar mass calculations, molarity formulas, or significant figure arithmetic beyond simple ratios.

6. LaTeX for chemical formulas: $H_2O$, $CO_2$, $O_2$, $C_6H_{12}O_6$, etc. Do NOT write them as plain text.

7. DISTRACTOR QUALITY. Each wrong option must represent a specific scientific misconception or analytical error:
   - "MISCONCEPTION" — common wrong belief about the topic
   - "PARTIAL_TRUTH" — true fact but not supported by THIS stimulus
   - "REVERSED_CAUSATION" — cause/effect switched
   - "SCOPE_ERROR" — correct conclusion but applied to wrong variable
   - "MAGNIFIED_DETAIL" — fixates on minor stimulus detail, misses the main finding

8. ZERO HINTS IN QUESTION TEXT. Do not use "obviously", "clearly", "it is evident". Do not repeat key words from the stimulus in the correct option (makes it guessable).

9. DIAGRAMS: Describe them fully in text within stimulus field with clear labels. Use [DIAGRAM: ...] tag if needed. Make it possible to answer without seeing the actual image.

10. SOLUTION: Minimum 4 sentences: (1) Identify key variable(s) in stimulus. (2) State the relevant scientific principle. (3) Explain why correct answer is correct. (4) Explain why each distractor fails. Reference specific stimulus data.
"""

def build_custom_section(use_custom, custom_text, subtest):
    if use_custom and custom_text.strip():
        return f"""
CUSTOM COMPETENCIES — PRIORITIZE THESE ABOVE DEFAULT DISTRIBUTION:
Generate as many items as possible targeting these specific DepEd MELCs/competencies.
Cycle through them. Remaining items use standard coverage.
```
{custom_text.strip()}
```
"""
    return ""

def build_topic_str(weights):
    return "\n".join([f"  - {t}: ~{w}%" for t, w in weights.items()])

def clean_json(raw):
    s = raw.strip()
    for fence in ["```json", "```"]:
        if s.startswith(fence): s = s[len(fence):]
    if s.endswith("```"): s = s[:-3]
    last = s.rfind("}")
    if last != -1: s = s[:last+1]
    return s.strip()

MATH_PROMPT = """
You are the chief psychometrician and item writer for the UPCAT Mathematics subtest at the University of the Philippines Office of Admissions.
Construct a psychometrically valid {num_items}-item practice test. All items are multiple choice with exactly 4 options (A, B, C, D).

DIFFICULTY LEVEL: {difficulty}
{diff_instruction}

{custom_section}

TOPIC DISTRIBUTION (target percentages):
{topic_weights}

{critical_rules}

OUTPUT FORMAT: Return STRICT, VALID JSON ONLY. No markdown code fences, no preamble, no trailing commentary.
No truncation — all {num_items} items must be complete with full solutions.

{{
  "exam_metadata": {{
    "subtest": "Mathematics",
    "total_items": {num_items},
    "time_minutes": {time_budget},
    "time_per_item_seconds": {spi_math},
    "calculator_allowed": false,
    "difficulty": "{difficulty}",
    "scoring": "+1 correct, -0.25 wrong, 0 blank (RMW)"
  }},
  "items": [
    {{
      "item_number": 1,
      "topic": "Algebra — Linear Equations, Inequalities, Systems",
      "subtopic": "Linear equation with fractional coefficients",
      "grade_level_origin": "Grade 8",
      "question_text": "Full question stem using LaTeX for ALL math. Word problems must use Filipino context. Example: If $\\\\frac{{3x-1}}{{4}} + 2 = \\\\frac{{x+5}}{{3}}$, what is the value of $x$?",
      "stimulus": null,
      "options": {{
        "A": "$x = -7$",
        "B": "$x = 5$",
        "C": "$x = -1$",
        "D": "$x = 11$"
      }},
      "correct_answer": "C",
      "distractor_analysis": {{
        "A": {{"type": "SIGN_ERROR", "error": "Forgot to distribute negative when moving terms; got $3x - 12 = 4x + 5$ instead of correct form"}},
        "B": {{"type": "ARITHMETIC_ERROR", "error": "Made multiplication error: computed $3 \\\\times 4 = 16$ instead of 12 when clearing fractions"}},
        "D": {{"type": "INCOMPLETE_SOLUTION", "error": "Solved for $2x$ but forgot to divide by 2 at the final step"}}
      }},
      "solution": "Step 1: Multiply both sides by LCM(4,3) = 12 to clear fractions: $12 \\\\cdot \\\\frac{{3x-1}}{{4}} + 12 \\\\cdot 2 = 12 \\\\cdot \\\\frac{{x+5}}{{3}}$. Step 2: Simplify: $3(3x-1) + 24 = 4(x+5)$. Step 3: Expand: $9x - 3 + 24 = 4x + 20$, so $9x + 21 = 4x + 20$. Step 4: Isolate $x$: $5x = -1$, therefore $x = -\\\\frac{{1}}{{5}}$. (Adjust numbers in your actual item so answer is clean.)",
      "key_concept": "Solving linear equations with unlike-denominator fractions by multiplying through by the LCM.",
      "common_mistake_warning": "Most students forget to distribute the multiplication through the entire numerator of each fraction."
    }}
  ]
}}

Generate exactly {num_items} items. Every item must have a complete, step-by-step solution. All math in LaTeX. Valid JSON only.
"""

SCI_PROMPT = """
You are the chief psychometrician and item writer for the UPCAT Science subtest at the University of the Philippines Office of Admissions.
Construct a psychometrically valid {num_items}-item practice test. All items are multiple choice with exactly 4 options.

DIFFICULTY LEVEL: {difficulty}
{diff_instruction}

{custom_section}

TOPIC DISTRIBUTION (target percentages):
{topic_weights}

{critical_rules}

STIMULUS TYPES:
- "TEXT_PASSAGE": 60-120 word experimental/scientific scenario. Answer must require reading it.
- "DATA_TABLE": HTML table with ≥4 rows and ≥3 columns of real-looking experimental data.
- "DIAGRAM_TEXT": Clear labeled text description of a diagram/figure.
- null: Direct conceptual application, no stimulus.

OUTPUT FORMAT: Return STRICT, VALID JSON ONLY. No markdown fences, no preamble, no commentary.

{{
  "exam_metadata": {{
    "subtest": "Science",
    "total_items": {num_items},
    "time_minutes": {time_budget},
    "time_per_item_seconds": {spi_sci},
    "difficulty": "{difficulty}",
    "scoring": "+1 correct, -0.25 wrong, 0 blank (RMW)",
    "distribution": "Biology ~38%, Earth Science ~26%, Chemistry ~21%, Physics ~15%"
  }},
  "items": [
    {{
      "item_number": 1,
      "topic": "Biology — Cell Biology",
      "subtopic": "Mitochondria and cellular respiration",
      "grade_level_origin": "Grade 9",
      "science_discipline": "Biology",
      "stimulus_type": "TEXT_PASSAGE",
      "stimulus": "A researcher cultured two groups of liver cells under identical nutrient conditions. Group A was maintained in normal atmospheric oxygen (21% $O_2$). Group B was placed in a sealed chamber with the oxygen gradually depleted to less than 1% over 24 hours. At the end of the experiment, Group A cells showed ATP concentrations of 85 nmol/mg protein, while Group B cells had ATP concentrations of 12 nmol/mg protein. Lactic acid concentrations in Group B were 6.8 times higher than in Group A.",
      "question_text": "Based on the experimental data, which conclusion about Group B cells is most directly supported?",
      "options": {{
        "A": "Group B cells experienced complete necrosis due to the absence of nutrients.",
        "B": "Group B cells shifted primarily to anaerobic respiration to generate ATP.",
        "C": "Group B cells increased mitochondrial biogenesis to compensate for oxygen loss.",
        "D": "Group B cells stopped all metabolic activity after 12 hours of oxygen depletion."
      }},
      "correct_answer": "B",
      "distractor_analysis": {{
        "A": {{"type": "SCOPE_ERROR", "error": "Nutrients were identical between groups; the variable was oxygen, not nutrients. Complete necrosis is not indicated by lactic acid production."}},
        "C": {{"type": "REVERSED_CAUSATION", "error": "Mitochondrial biogenesis requires oxygen; cells deprived of oxygen cannot increase mitochondrial production. This is the opposite of what happens."}},
        "D": {{"type": "PARTIAL_TRUTH", "error": "ATP was not zero — Group B had 12 nmol/mg protein, indicating some metabolic activity continued via anaerobic pathways."}}
      }},
      "solution": "The key variables in the stimulus are: ATP concentration dropped from 85 to 12 nmol/mg protein (86% reduction) and lactic acid increased 6.8x in the oxygen-deprived group. The scientific principle is that lactic acid is the end product of anaerobic glycolysis, which cells switch to when oxygen is unavailable for the electron transport chain. Option B is correct because the dramatic increase in lactic acid directly indicates a shift to anaerobic respiration, while the remaining ATP (12 nmol/mg) confirms some energy production continued through this pathway. Option A is wrong because nutrients were the same and lactic acid production indicates living cells, not necrosis. Option C is wrong because mitochondrial biogenesis requires oxygen — deprived cells downregulate, not upregulate, mitochondria. Option D is wrong because the stimulus explicitly shows non-zero ATP production, proving metabolic activity continued.",
      "key_concept": "When cells are deprived of oxygen, aerobic respiration in the mitochondria halts; cells compensate via anaerobic glycolysis, producing lactic acid as a byproduct.",
      "passage_reference": "ATP: 12 vs 85 nmol/mg protein; lactic acid: 6.8× higher in Group B"
    }}
  ]
}}

Generate exactly {num_items} items. At least 60% must have stimuli (TEXT_PASSAGE, DATA_TABLE, or DIAGRAM_TEXT). Valid JSON only.
"""

def generate_subtest(model, prompt, name):
    response = model.generate_content(prompt)
    raw = clean_json(response.text)
    data = json.loads(raw)
    if "items" not in data or not data["items"]:
        raise ValueError(f"No items in {name} response")
    return data

def run_generation(do_math, do_sci):
    if not api_key:
        st.error("❌ Enter your Gemini API Key in the sidebar.")
        return

    prog = st.progress(0)
    status = st.empty()

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            gemini_model,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.82,
                "top_p": 0.95,
                "max_output_tokens": 32000,
            }
        )
        new_data = dict(st.session_state.get('test_data') or {})

        if do_math:
            # Actual UPCAT: 50 items / 60 min = 72s per item
            time_budget_math = max(10, int((math_items / 50) * 60))
            spi_math = 72  # fixed per UPCAT spec
            status.info("📐 Generating UPCAT Math items — Gemini is writing questions, solutions & distractor analysis…")
            prog.progress(10)
            custom_m = build_custom_section(
                st.session_state.get('use_custom_math', False),
                st.session_state.get('custom_competencies_math', ''),
                "Mathematics"
            )
            math_p = MATH_PROMPT.format(
                num_items=math_items,
                difficulty=difficulty,
                diff_instruction=diff_instruction,
                custom_section=custom_m,
                topic_weights=build_topic_str(MATH_TOPIC_WEIGHTS),
                critical_rules=MATH_CRITICAL_RULES,
                time_budget=time_budget_math,
                spi_math=spi_math,
            )
            math_d = generate_subtest(model, math_p, "Mathematics")
            new_data['math'] = math_d
            prog.progress(50)
            status.success(f"✅ Math: {len(math_d['items'])} items generated!")

        if do_sci:
            # Actual UPCAT: 45 items / 45 min = 60s per item
            time_budget_sci = max(10, int((sci_items / 45) * 45))
            spi_sci = 60  # fixed per UPCAT spec
            status.info("🔬 Generating UPCAT Science items (passage-based, data tables, conceptual)…")
            prog.progress(55 if do_math else 10)
            custom_s = build_custom_section(
                st.session_state.get('use_custom_sci', False),
                st.session_state.get('custom_competencies_sci', ''),
                "Science"
            )
            sci_p = SCI_PROMPT.format(
                num_items=sci_items,
                difficulty=difficulty,
                diff_instruction=diff_instruction,
                custom_section=custom_s,
                topic_weights=build_topic_str(SCI_TOPIC_WEIGHTS),
                critical_rules=SCI_CRITICAL_RULES,
                time_budget=time_budget_sci,
                spi_sci=spi_sci,
            )
            sci_d = generate_subtest(model, sci_p, "Science")
            new_data['sci'] = sci_d
            prog.progress(96)
            status.success(f"✅ Science: {len(sci_d['items'])} items generated!")

        prog.progress(100)
        m_c = len(new_data.get('math', {}).get('items', []))
        s_c = len(new_data.get('sci', {}).get('items', []))
        status.success(f"🎉 Ready — Math: {m_c} items · Science: {s_c} items · {difficulty} difficulty")

        st.session_state.update({
            'test_data': new_data,
            'user_answers_math': {}, 'user_answers_sci': {},
            'flagged_items': set(),
            'submitted': False, 'math_submitted': False, 'sci_submitted': False,
            'math_started': False, 'sci_started': False,
            'math_start_time': None, 'sci_start_time': None,
            'elapsed_math': 0, 'elapsed_sci': 0,
        })
        time.sleep(0.8)
        st.rerun()

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON parse error — try Gemini 2.5 Pro for better compliance. Detail: {str(e)[:200]}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ==========================================
# 🚀 HERO
# ==========================================
st.markdown("""
<div class='hero-shell' role='banner'>
  <div class='hero-bg'></div>
  <div class='hero-grid' aria-hidden='true'></div>
  <div class='hero-glow-math' aria-hidden='true'></div>
  <div class='hero-glow-sci' aria-hidden='true'></div>
  <div class='hero-inner'>
    <div class='hero-pill'>🧮 UPCAT Science &amp; Math Elite Simulator · v2.0</div>
    <h1 class='hero-title'><em>Padayon!</em><br>Agham at Matematika</h1>
    <p class='hero-sub'>
      Research-based psychometric simulation of the UPCAT Mathematics (50 items · 60 min · no calculator)
      and Science (45 items · 45 min · ~60% passage-based) subtests.
      135,000+ applicants compete for ~18,000 admission notices yearly.
      Train at the level that makes Iskos and Iskas.
    </p>
    <div class='hero-divider'></div>
    <div class='hero-stats'>
      <div><div class='h-stat-num'>135k+</div><div class='h-stat-lbl'>Applicants / Year</div></div>
      <div><div class='h-stat-num'>13.3%</div><div class='h-stat-lbl'>Any Qualification Rate</div></div>
      <div><div class='h-stat-num'>&lt;8%</div><div class='h-stat-lbl'>1st Choice Prog Rate</div></div>
      <div><div class='h-stat-num'>50+45</div><div class='h-stat-lbl'>Math + Science Items</div></div>
      <div><div class='h-stat-num'>−0.25</div><div class='h-stat-lbl'>Wrong Answer Penalty</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='notice'>
  <span class='notice-icon'>ℹ️</span>
  <div><strong>Disclaimer:</strong> All items are AI-generated for practice only. UPG formulas use independent research modeling based on published UP admissions data — not official UP methodology. 
  This simulator focuses on <strong>Mathematics and Science only</strong>. The 13.3% passing rate (UPCAT 2025 data) includes waitlisted applicants; 
  <strong>actual first-choice program qualification is significantly lower</strong> (~8% or less).</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📋 CUSTOM COMPETENCY INPUT
# ==========================================
st.markdown("""
<div class='sec-hdr'><span class='sec-hdr-text'>📋 Custom Competency Input</span><div class='sec-hdr-line'></div></div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='notice sci'>
  <span class='notice-icon'>💡</span>
  <div>Paste specific DepEd MELCs (Most Essential Learning Competencies) to target those exact skills. 
  Leave blank to use the default UPCAT topic distribution. Source MELCs from <em>curriculum.deped.gov.ph</em> or your textbook.</div>
</div>
""", unsafe_allow_html=True)

col_c1, col_c2 = st.columns(2)
with col_c1:
    st.markdown('<div class="comp-card"><span class="comp-label math">🔢 Math Competencies</span></div>', unsafe_allow_html=True)
    use_custom_math = st.checkbox("Enable custom Math competencies", key="use_custom_math_cb")
    custom_math = st.text_area("Math competencies",
        height=140, label_visibility="collapsed",
        placeholder="Example:\n• Factors polynomials completely (M8AL-Ia-b-1)\n• Solves problems involving rational algebraic expressions\n• Illustrates quadratic inequalities and their graphs",
        key="custom_math_input")
    st.session_state['use_custom_math'] = use_custom_math
    st.session_state['custom_competencies_math'] = custom_math

with col_c2:
    st.markdown('<div class="comp-card"><span class="comp-label sci">🔬 Science Competencies</span></div>', unsafe_allow_html=True)
    use_custom_sci = st.checkbox("Enable custom Science competencies", key="use_custom_sci_cb")
    custom_sci = st.text_area("Science competencies",
        height=140, label_visibility="collapsed",
        placeholder="Example:\n• Describe the different levels of biological organization\n• Explain how energy is transformed in photosynthesis\n• Describe the process of meiosis and its significance in heredity",
        key="custom_sci_input")
    st.session_state['use_custom_sci'] = use_custom_sci
    st.session_state['custom_competencies_sci'] = custom_sci

# ==========================================
# 🚀 GENERATE
# ==========================================
st.markdown("""
<div class='sec-hdr'><span class='sec-hdr-text'>🚀 Generate Simulation</span><div class='sec-hdr-line'></div></div>
""", unsafe_allow_html=True)

spi_math_display = 72  # UPCAT: 60min / 50 items
spi_sci_display = 60   # UPCAT: 45min / 45 items
time_m = max(10, int((math_items / 50) * 60))
time_s = max(10, int((sci_items / 45) * 45))

st.markdown(f"""
<div class='subtest-grid'>
  <div class='subtest-card math'>
    <div class='sc-icon'>🔢</div>
    <div class='sc-title'>Mathematics</div>
    <div class='sc-meta'>{math_items} items · ~{time_m} min · no calculator · ~{spi_math_display}s/item budget</div>
    <div class='sc-detail'>
      ~58% JHS Algebra/Geometry/Number Sense · ~22% Stats/Sequences/Exponents · ~10% Functions · ~10% Trig/SHS (rare)<br>
      <strong style='color:#58a6ff;'>No calculator. All answers reachable in ≤90 seconds by hand or mental math.</strong>
    </div>
  </div>
  <div class='subtest-card sci'>
    <div class='sc-icon'>🔬</div>
    <div class='sc-title'>Science</div>
    <div class='sc-meta'>{sci_items} items · ~{time_s} min · passage-based · ~{spi_sci_display}s/item budget</div>
    <div class='sc-detail'>
      Bio ~38% · Earth Sci ~26% · Chem ~21% · Physics ~15%<br>
      <strong style='color:#39d0c5;'>~60% stimulus-based (passages, data tables, diagrams). Read the stimulus before the question.</strong>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

g1, g2, g3 = st.columns([2,1,1])
with g1:
    gen_both = st.button(f"🚀 Generate Both — {math_items + sci_items} Items Total",
        type="primary", use_container_width=True)
with g2:
    gen_math = st.button(f"🔢 Math Only", use_container_width=True)
with g3:
    gen_sci = st.button(f"🔬 Science Only", use_container_width=True)

if gen_both: run_generation(True, True)
elif gen_math: run_generation(True, False)
elif gen_sci: run_generation(False, True)

# ==========================================
# 📝 EXAM INTERFACE
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
        p1, p2 = st.columns(2)
        with p1:
            st.markdown(f"""
            <div class='prog-wrap'>
              <div class='prog-row'>
                <span>🔢 MATH — {answered_math}/{total_math}</span>
                <span>{pct_m:.0f}%</span>
              </div>
              <div class='prog-track'><div class='prog-fill-math' style='width:{pct_m:.1f}%'></div></div>
            </div>
            """, unsafe_allow_html=True)
        with p2:
            st.markdown(f"""
            <div class='prog-wrap'>
              <div class='prog-row'>
                <span>🔬 SCIENCE — {answered_sci}/{total_sci}</span>
                <span>{pct_s:.0f}%</span>
              </div>
              <div class='prog-track'><div class='prog-fill-sci' style='width:{pct_s:.1f}%'></div></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class='notice warn'>
      <span class='notice-icon'>⚠️</span>
      <div><strong>RMW Scoring Active:</strong> +1.00 correct · −0.25 wrong · 0.00 blank.
      For Math: no calculator — all arithmetic must be done by hand or mentally.
      For Science: read the stimulus first, then the question.
      Only guess when you can eliminate at least 2 options with confidence.</div>
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
        label = "🔬" if active == "sci" else "🔢"
        tcls = "sci" if active == "sci" else ""

        st.components.v1.html(f"""
        <div id="tc" class="timer-chip {tcls}">{label} <span id="tv">--:--</span></div>
        <script>
        (function(){{
          var tl={remaining};
          function tick(){{
            if(tl<0)tl=0;
            var m=Math.floor(tl/60),s=tl%60;
            var el=document.getElementById('tv');
            var box=document.getElementById('tc');
            if(el){{
              el.textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
              if(tl<=300&&tl>60)box.className='timer-chip {tcls} warn';
              if(tl<=60){{box.className='timer-chip {tcls} danger';}}
              if(tl<=0)el.textContent='00:00 · TIME UP';
            }}
            if(tl>0){{tl--;setTimeout(tick,1000);}}
          }}
          setTimeout(tick,200);
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
            dot_ans_cls = "answered-m" if is_math else "answered-s"

            # Navigator
            if show_nav:
                nav_html = f"""
                <div class='item-nav'>
                  <div class='nav-title'>{'Math' if is_math else 'Science'} Navigator — click to jump to item</div>
                  <div class='nav-grid'>"""
                for q in items_list:
                    inum = q.get('item_number')
                    fkey = f"{subtest_key}_{inum}"
                    is_a = inum in st.session_state[ans_key]
                    is_f = fkey in flagged
                    cls = "flagged" if is_f else (dot_ans_cls if is_a else "")
                    nav_html += f"""<div class='nav-dot {cls}' onclick="document.getElementById('{subtest_key}_{inum}').scrollIntoView({{behavior:'smooth'}})" title='Item {inum}'>{inum}</div>"""
                nav_html += "</div></div>"
                st.markdown(nav_html, unsafe_allow_html=True)

            # Start timer on first render
            if not st.session_state.get(f'{subtest_key}_start_time'):
                st.session_state[f'{subtest_key}_start_time'] = time.time()
                st.session_state['active_subtest'] = subtest_key

            for q in items_list:
                inum       = q.get('item_number')
                topic      = q.get('topic', '')
                subtopic   = q.get('subtopic', '')
                grade_orig = q.get('grade_level_origin', '')
                qtext      = q.get('question_text', '')
                stimulus   = q.get('stimulus', None)
                stim_type  = q.get('stimulus_type', None)
                is_ans     = inum in st.session_state[ans_key]
                is_flg     = f"{subtest_key}_{inum}" in flagged

                # Card class
                card_cls = "q-card"
                if not is_math: card_cls += " sci"
                if is_ans: card_cls += " answered"
                if is_flg: card_cls += " flagged"

                # Short topic label
                short = topic.split(' — ')[0] if ' — ' in topic else topic
                short = short[:28] + ('…' if len(short) > 28 else '')
                sci_disc = q.get('science_discipline', '')

                st.markdown(f"""
                <div class='{card_cls}' id='{subtest_key}_{inum}'>
                  <div class='q-meta'>
                    <span class='q-num {"sci" if not is_math else ""}'>
                      {'MTH' if is_math else 'SCI'} {inum:02d}
                    </span>
                    <span class='q-tag' title='{topic}'>{short}</span>
                    {f"<span class='q-tag'>{grade_orig}</span>" if grade_orig else ""}
                    {f"<span class='q-tag'>{sci_disc}</span>" if sci_disc and not is_math else ""}
                    {f"<span class='q-tag' style='color:var(--amber); border-color:rgba(210,153,34,0.3);'>📊 Data</span>" if stimulus else ""}
                    {"<span style='font-size:0.85rem; margin-left:auto;'>🚩</span>" if is_flg else ""}
                    {"<span style='font-size:0.85rem; margin-left:2px;'>✅</span>" if is_ans else ""}
                  </div>
                """, unsafe_allow_html=True)

                # Render stimulus
                if stimulus:
                    if stim_type == "DATA_TABLE":
                        st.markdown(f"""
                        <div class='sci-data-box'>
                          <div class='stim-label data'>📊 Experimental Data / Table</div>
                          {stimulus}
                        </div>
                        """, unsafe_allow_html=True)
                    elif stim_type == "DIAGRAM_TEXT":
                        st.markdown(f"""
                        <div class='sci-data-box' style='border-left-color: var(--purple);'>
                          <div class='stim-label diagram'>🔎 Figure / Diagram</div>
                          {stimulus}
                        </div>
                        """, unsafe_allow_html=True)
                    else:  # TEXT_PASSAGE
                        st.markdown(f"""
                        <div class='sci-passage'>
                          <div class='stim-label passage'>📄 Read carefully before answering</div>
                          {stimulus}
                        </div>
                        """, unsafe_allow_html=True)

                # Question — use st.markdown for LaTeX rendering
                st.markdown(f"<div class='q-stem'>{qtext}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)  # close q-card

                opts = q.get('options', {})
                choices = [
                    f"A) {opts.get('A','')}",
                    f"B) {opts.get('B','')}",
                    f"C) {opts.get('C','')}",
                    f"D) {opts.get('D','')}",
                ]
                choice = st.radio(
                    f"Answer {subtest_key} {inum}",
                    choices,
                    key=f"{subtest_key}_r_{inum}",
                    index=None,
                    label_visibility="collapsed"
                )
                if choice:
                    st.session_state[ans_key][inum] = choice[0]

                if enable_flag:
                    fkey = f"{subtest_key}_{inum}"
                    flbl = "🚩 Unflag" if fkey in flagged else "🚩 Flag for review"
                    if st.button(flbl, key=f"fl_{subtest_key}_{inum}"):
                        if fkey in flagged: flagged.discard(fkey)
                        else: flagged.add(fkey)
                        st.session_state['flagged_items'] = flagged
                        st.rerun()

                st.markdown("<hr style='border:none;border-top:1px solid var(--border-mid);margin:8px 0 14px;'>",
                    unsafe_allow_html=True)

    for tab, key, items in active_tabs:
        render_subtest(tab, key, items)

    # Submit section
    st.markdown("<br>", unsafe_allow_html=True)
    blank = total_all - total_ans
    flagged_count = len(flagged)

    st.markdown(f"""
    <div class='stat-row'>
      <div class='stat-pill'><div class='sp-num' style='color:var(--green);'>{total_ans}</div><div class='sp-lbl'>Answered</div></div>
      <div class='stat-pill'><div class='sp-num' style='color:var(--amber);'>{flagged_count}</div><div class='sp-lbl'>Flagged</div></div>
      <div class='stat-pill'><div class='sp-num' style='color:var(--fg-muted);'>{blank}</div><div class='sp-lbl'>Blank (0 pts)</div></div>
      <div class='stat-pill'><div class='sp-num' style='color:var(--math-primary);'>{total_all}</div><div class='sp-lbl'>Total Items</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1s, c2s, c3s = st.columns([1,2,1])
    with c2s:
        if blank > 0:
            st.warning(f"⚠️ {blank} item(s) unanswered — scored 0 (no penalty). Only guess if you can eliminate ≥2 options.")
        if flagged_count > 0:
            st.info(f"🚩 {flagged_count} item(s) flagged for review.")
        if st.button("📥 Submit & View Full UPG Report + Deep Feedback",
            type="primary", use_container_width=True):
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
    test_data     = st.session_state['test_data']
    u_math        = st.session_state.get('user_answers_math', {})
    u_sci         = st.session_state.get('user_answers_sci', {})
    elapsed_math  = st.session_state.get('elapsed_math', 0)
    elapsed_sci   = st.session_state.get('elapsed_sci', 0)
    math_items_data = test_data.get('math', {}).get('items', [])
    sci_items_data  = test_data.get('sci', {}).get('items', [])

    def score_subtest(items, user_ans):
        total   = len(items)
        correct = sum(1 for q in items if user_ans.get(q['item_number']) == q['correct_answer'])
        answered= sum(1 for v in user_ans.values() if v)
        wrong   = answered - correct
        blank   = total - answered
        raw     = max(0.0, correct - 0.25 * wrong)
        pct     = raw / max(1, total)
        return total, correct, wrong, blank, raw, pct

    if math_items_data:
        m_total, m_correct, m_wrong, m_blank, m_raw, m_pct = score_subtest(math_items_data, u_math)
    else:
        m_total, m_correct, m_wrong, m_blank, m_raw, m_pct = 0,0,0,0,0.0,0.0

    if sci_items_data:
        s_total, s_correct, s_wrong, s_blank, s_raw, s_pct = score_subtest(sci_items_data, u_sci)
    else:
        s_total, s_correct, s_wrong, s_blank, s_raw, s_pct = 0,0,0,0,0.0,0.0

    # ── SEPARATE MATH vs SCIENCE UPG ──
    # Math grades
    math_grades = [g8_math, g9_math, g10_math, g11_precalc, g11_calc, g11_stats, g11_genmath]
    sci_grades  = [g8_sci, g9_sci, g10_sci, g11_bio1, g11_bio2, g11_earth]

    math_grade_avg = float(np.mean(math_grades))
    sci_grade_avg  = float(np.mean(sci_grades))
    all_grade_avg  = float(np.mean(math_grades + sci_grades))

    # School modifier
    avg_mod = (jhs_mod + shs_mod) / 2

    # Grade UPG per subject (raw: maps 75→3.0, 100→1.0, 60→5.0)
    def grade_to_upg(avg, mod):
        raw = 5.0 - ((avg - 75) / 25) * 4.0
        return max(1.0, min(5.0, raw - mod))

    math_grade_upg = grade_to_upg(math_grade_avg, avg_mod)
    sci_grade_upg  = grade_to_upg(sci_grade_avg, avg_mod)
    overall_grade_upg = grade_to_upg(all_grade_avg, avg_mod)

    # UPCAT UPG per subtest (60% weight)
    # UPCAT Math contributes to UPG based on math score
    # Science also contributes — combined for overall UPG
    # For SEPARATE Math and Science UPG:
    #   Subject UPG = 0.40 * grade_UPG_subject + 0.60 * upcat_UPG_subject

    def upcat_pct_to_upg(pct, mean_b, sigma_v):
        z = (pct - mean_b) / sigma_v
        return max(1.0, min(5.0, 2.75 - z * 0.55)), z

    if math_items_data:
        math_upcat_upg, math_z = upcat_pct_to_upg(m_pct, MEAN_BASELINE, SIGMA)
    else:
        math_upcat_upg, math_z = overall_grade_upg, 0.0

    if sci_items_data:
        sci_upcat_upg, sci_z = upcat_pct_to_upg(s_pct, MEAN_BASELINE, SIGMA)
    else:
        sci_upcat_upg, sci_z = overall_grade_upg, 0.0

    # Final subject UPGs
    math_final_upg = (0.40 * math_grade_upg) + (0.60 * math_upcat_upg)
    sci_final_upg  = (0.40 * sci_grade_upg)  + (0.60 * sci_upcat_upg)

    # Overall UPG (average of what was tested)
    if math_items_data and sci_items_data:
        combined_pct = (m_pct + s_pct) / 2
        overall_upcat_upg, combined_z = upcat_pct_to_upg(combined_pct, MEAN_BASELINE, SIGMA)
        final_upg = (0.40 * overall_grade_upg) + (0.60 * overall_upcat_upg)
    elif math_items_data:
        combined_pct = m_pct
        overall_upcat_upg, combined_z = math_upcat_upg, math_z
        final_upg = math_final_upg
    else:
        combined_pct = s_pct
        overall_upcat_upg, combined_z = sci_upcat_upg, sci_z
        final_upg = sci_final_upg

    overall_pct = max(0.001, min(0.9999,
        0.5 * (1 + math.erf(combined_z / math.sqrt(2)))))
    sim_rank = int(135000 - 135000 * overall_pct)

    if   final_upg <= 1.50: verdict = "🏆 Elite — Top tier across all campuses."
    elif final_upg <= 2.00: verdict = "✅ Very Strong — Likely qualifies for multiple programs."
    elif final_upg <= 2.30: verdict = "📘 Competitive — Within range for several programs."
    elif final_upg <= 2.60: verdict = "🟡 Borderline — May qualify at less competitive campuses."
    elif final_upg <= 3.00: verdict = "🟠 Below Threshold — Significant improvement needed."
    else:                    verdict = "🔴 Not Yet Ready — Focus on fundamentals first."

    # Topic analysis
    def analyze_topics(items, user_ans):
        td = {}
        for q in items:
            topic = q.get('topic','Unknown')
            short = topic.split(' — ')[0] if ' — ' in topic else topic
            inum  = q.get('item_number')
            ok    = user_ans.get(inum) == q.get('correct_answer')
            if short not in td: td[short] = {'correct':0,'total':0}
            td[short]['total'] += 1
            if ok: td[short]['correct'] += 1
        return td

    math_topics = analyze_topics(math_items_data, u_math) if math_items_data else {}
    sci_topics  = analyze_topics(sci_items_data,  u_sci)  if sci_items_data  else {}

    # ── RESULTS HERO ──
    upg_color = "#58a6ff" if final_upg <= 2.3 else ("#d29922" if final_upg <= 2.8 else "#f85149")
    st.markdown(f"""
    <div class='res-hero'>
      <div class='res-hero-glow'></div>
      <div class='upg-label'>University Predicted Grade (UPG)</div>
      <div class='upg-val' style='color:{upg_color};'>{final_upg:.3f}</div>
      <div class='upg-verdict'>{verdict}</div>
      <div style='color:rgba(255,255,255,0.3);font-family:var(--font-mono);font-size:0.62rem;margin-top:10px;letter-spacing:0.1em;position:relative;z-index:1;'>
        Scale: 1.000 (highest) → 5.000 (lowest) · Simulated rank #{sim_rank:,} of 135,000 applicants · Top {100*(1-overall_pct):.1f}th percentile
      </div>
      <div style='color:rgba(255,255,255,0.45);font-family:var(--font-body);font-size:0.82rem;margin-top:8px;position:relative;z-index:1;'>
        {"✅ Within campus qualification range for at least one UP campus" if final_upg <= 2.80 else "❌ Below standard campus cutoffs — consistent practice needed"}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SEPARATE MATH & SCIENCE UPG CARDS ──
    st.markdown("""
    <div class='sec-hdr'><span class='sec-hdr-text'>📊 Subject UPG Breakdown</span><div class='sec-hdr-line'></div></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='upg-row'>
      <div class='upg-card math'>
        <div class='upg-card-shimmer'></div>
        <div class='upg-card-title'>🔢 Mathematics UPG</div>
        <div class='upg-card-value'>{math_final_upg:.3f}</div>
        <div class='upg-card-sub'>
          {"✅ Strong math performance" if math_final_upg <= 2.3 else "⚠️ Needs improvement" if math_final_upg <= 2.8 else "❌ Significant gaps in math"}
        </div>
        <div class='upg-breakdown'>
          <div class='upg-br-row'><span class='upg-br-lbl'>Math Grade Avg</span><span class='upg-br-val' style='color:var(--math-primary);'>{math_grade_avg:.1f}/100</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>Math Grade UPG (40%)</span><span class='upg-br-val'>{math_grade_upg:.3f}</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>UPCAT Math Score</span><span class='upg-br-val' style='color:var(--math-primary);'>{m_pct*100:.1f}% (RMW)</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>UPCAT Math UPG (60%)</span><span class='upg-br-val'>{math_upcat_upg:.3f}</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>Z-score</span><span class='upg-br-val'>{math_z:+.2f}σ</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>Correct / Wrong / Blank</span><span class='upg-br-val'>{m_correct}C · {m_wrong}W · {m_blank}B</span></div>
        </div>
      </div>
      <div class='upg-card sci'>
        <div class='upg-card-shimmer'></div>
        <div class='upg-card-title'>🔬 Science UPG</div>
        <div class='upg-card-value'>{sci_final_upg:.3f}</div>
        <div class='upg-card-sub'>
          {"✅ Strong science performance" if sci_final_upg <= 2.3 else "⚠️ Needs improvement" if sci_final_upg <= 2.8 else "❌ Significant gaps in science"}
        </div>
        <div class='upg-breakdown'>
          <div class='upg-br-row'><span class='upg-br-lbl'>Science Grade Avg</span><span class='upg-br-val' style='color:var(--sci-primary);'>{sci_grade_avg:.1f}/100</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>Science Grade UPG (40%)</span><span class='upg-br-val'>{sci_grade_upg:.3f}</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>UPCAT Science Score</span><span class='upg-br-val' style='color:var(--sci-primary);'>{s_pct*100:.1f}% (RMW)</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>UPCAT Science UPG (60%)</span><span class='upg-br-val'>{sci_upcat_upg:.3f}</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>Z-score</span><span class='upg-br-val'>{sci_z:+.2f}σ</span></div>
          <div class='upg-br-row'><span class='upg-br-lbl'>Correct / Wrong / Blank</span><span class='upg-br-val'>{s_correct}C · {s_wrong}W · {s_blank}B</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRIC TILES ──
    penalty_total = (m_wrong + s_wrong) * 0.25
    metrics = [
        (f"{final_upg:.3f}", upg_color, "Overall UPG", "Lower is better"),
        (f"#{sim_rank:,}", "var(--sci-primary)", "Sim. Rank", f"Top {100*(1-overall_pct):.1f}%"),
        (f"{overall_grade_upg:.3f}", "var(--green)", "Grades UPG", f"Avg: {all_grade_avg:.1f}/100"),
        (f"{overall_upcat_upg:.3f}", "var(--amber)" if overall_upcat_upg > 2.5 else "var(--green)", "UPCAT UPG", f"Z: {combined_z:+.2f}"),
    ]
    if math_items_data:
        metrics.append((f"{m_pct*100:.1f}%", "var(--math-primary)", "Math Score %", f"RMW: {m_raw:.2f}/{m_total}"))
    if sci_items_data:
        metrics.append((f"{s_pct*100:.1f}%", "var(--sci-primary)", "Science Score %", f"RMW: {s_raw:.2f}/{s_total}"))

    cols_m = st.columns(min(len(metrics), 4))
    for i, (val, clr, lbl, sub) in enumerate(metrics):
        with cols_m[i % 4]:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='metric-card-val' style='color:{clr};'>{val}</div>
              <div class='metric-card-lbl'>{lbl}</div>
              <div class='metric-card-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── SCORE PANELS ──
    st.markdown("<br>", unsafe_allow_html=True)
    pcols = []
    if math_items_data: pcols.append('math')
    if sci_items_data: pcols.append('sci')
    sc = st.columns(len(pcols)) if pcols else []

    for ci, subj in enumerate(pcols):
        with sc[ci]:
            if subj == 'math':
                em, ems = int(elapsed_math//60), int(elapsed_math%60)
                budget_s = spi_math_display * m_total
                st.markdown(f"""
                <div class='score-panel'>
                  <h4>🔢 Mathematics</h4>
                  <div class='s-row'><span class='s-lbl'>Correct</span><span class='s-val c'>{m_correct} / {m_total}</span></div>
                  <div class='s-row'><span class='s-lbl'>Wrong (−0.25 each)</span><span class='s-val w'>{m_wrong} · −{m_wrong*0.25:.2f} pts</span></div>
                  <div class='s-row'><span class='s-lbl'>Blank</span><span class='s-val'>{m_blank}</span></div>
                  <div class='s-row'><span class='s-lbl'>RMW Score</span><span class='s-val g'>{m_raw:.2f} / {m_total}</span></div>
                  <div class='s-row'><span class='s-lbl'>Percentage</span><span class='s-val g'>{m_pct*100:.1f}%</span></div>
                  <div class='s-row'><span class='s-lbl'>Accuracy on Attempted</span><span class='s-val'>{m_correct/max(1,m_correct+m_wrong)*100:.1f}%</span></div>
                  <div class='s-row'><span class='s-lbl'>Time Used</span><span class='s-val'>{em}m {ems}s · {elapsed_math/max(1,m_total):.0f}s/item</span></div>
                  <div class='s-row'><span class='s-lbl'>UPCAT Budget</span><span class='s-val'>72s/item · {budget_s//60}min total</span></div>
                  <div class='s-row'><span class='s-lbl'>Time Status</span><span class='s-val {"c" if elapsed_math <= budget_s*1.05 else "w"}'>{"✅ On budget" if elapsed_math <= budget_s else "⚠️ Over budget"}</span></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                es, ess = int(elapsed_sci//60), int(elapsed_sci%60)
                budget_ss = spi_sci_display * s_total
                st.markdown(f"""
                <div class='score-panel'>
                  <h4>🔬 Science</h4>
                  <div class='s-row'><span class='s-lbl'>Correct</span><span class='s-val c'>{s_correct} / {s_total}</span></div>
                  <div class='s-row'><span class='s-lbl'>Wrong (−0.25 each)</span><span class='s-val w'>{s_wrong} · −{s_wrong*0.25:.2f} pts</span></div>
                  <div class='s-row'><span class='s-lbl'>Blank</span><span class='s-val'>{s_blank}</span></div>
                  <div class='s-row'><span class='s-lbl'>RMW Score</span><span class='s-val g'>{s_raw:.2f} / {s_total}</span></div>
                  <div class='s-row'><span class='s-lbl'>Percentage</span><span class='s-val g'>{s_pct*100:.1f}%</span></div>
                  <div class='s-row'><span class='s-lbl'>Accuracy on Attempted</span><span class='s-val'>{s_correct/max(1,s_correct+s_wrong)*100:.1f}%</span></div>
                  <div class='s-row'><span class='s-lbl'>Time Used</span><span class='s-val'>{es}m {ess}s · {elapsed_sci/max(1,s_total):.0f}s/item</span></div>
                  <div class='s-row'><span class='s-lbl'>UPCAT Budget</span><span class='s-val'>60s/item · {budget_ss//60}min total</span></div>
                  <div class='s-row'><span class='s-lbl'>Time Status</span><span class='s-val {"c" if elapsed_sci <= budget_ss*1.05 else "w"}'>{"✅ On budget" if elapsed_sci <= budget_ss else "⚠️ Over budget"}</span></div>
                </div>
                """, unsafe_allow_html=True)

    # ── TOPIC HEATMAPS ──
    if math_topics or sci_topics:
        st.markdown("""
        <div class='sec-hdr'><span class='sec-hdr-text'>🔥 Topic Mastery Heatmap</span><div class='sec-hdr-line'></div></div>
        """, unsafe_allow_html=True)
        hcols = []
        if math_topics: hcols.append('math')
        if sci_topics:  hcols.append('sci')
        hc = st.columns(len(hcols))
        for hi, hs in enumerate(hcols):
            with hc[hi]:
                td = math_topics if hs == 'math' else sci_topics
                color = "var(--math-primary)" if hs == 'math' else "var(--sci-primary)"
                lbl = "🔢 Math Topics" if hs == 'math' else "🔬 Science Topics"
                st.markdown(f"<h4 style='font-family:var(--font-display);font-size:1rem;color:{color};margin-bottom:10px;'>{lbl}</h4>", unsafe_allow_html=True)
                rows = sorted(td.items(), key=lambda x: x[1]['correct']/max(1,x[1]['total']))
                html = "<div class='heat-grid'>"
                for sk, data in rows:
                    pct_sk = data['correct']/max(1,data['total'])*100
                    cls_b = "strong" if pct_sk>=70 else ("mid" if pct_sk>=40 else "weak")
                    pc = "var(--green)" if cls_b=="strong" else ("var(--amber)" if cls_b=="mid" else "var(--red)")
                    label_short = sk[:26]+"…" if len(sk)>26 else sk
                    html += f"""
                    <div class='heat-row' title='{sk}'>
                      <span style='flex:1;color:var(--fg-secondary);font-size:0.74rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{label_short}</span>
                      <div class='heat-bar-out'><div class='heat-bar-in {cls_b}' style='width:{pct_sk:.0f}%;'></div></div>
                      <span class='heat-pct' style='color:{pc};'>{pct_sk:.0f}%</span>
                    </div>"""
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)

    # ── ADMISSION ENGINE ──
    st.markdown("""
    <div class='sec-hdr'><span class='sec-hdr-text'>🏛️ Cascading Admission Decision Engine</span><div class='sec-hdr-line'></div></div>
    """, unsafe_allow_html=True)

    # Actual 2025 data: 17,996 qualifiers out of 135,236 = 13.3% total
    # 10,600 degree-program qualifiers (direct) = 7.8%
    # rest are waitlisted
    st.markdown(f"""
    <div class='notice'>
      <span class='notice-icon'>📊</span>
      <div>
        <strong>UPCAT 2025 Official Data:</strong> 17,996 of 135,236 applicants received admission notices (13.3%),
        including waitlisted applicants. Only ~10,600 received direct program qualifications (~7.8%).
        Your simulated UPG of <strong>{final_upg:.3f}</strong> places you at rank <strong>#{sim_rank:,}</strong>.
        Admission is campus-qualified first, then program-specific within that campus.
      </div>
    </div>
    """, unsafe_allow_html=True)

    def evaluate_program(campus, program, cutoff, upg):
        tier = get_program_tier(campus, program)
        adj = {"Triple Quota": -0.40, "Double Quota": -0.22, "Single Quota": -0.06, "Less Popular": +0.08}.get(tier, 0.0)
        req = max(1.100, cutoff + adj)
        if upg <= req:
            return "<span class='badge pass'>✅ PASSED</span>", req, tier, "Within quota band"
        elif upg <= req + 0.14:
            return "<span class='badge risk'>🟡 DPWAS RISK</span>", req, tier, "Borderline — may waitlist"
        else:
            return "<span class='badge fail'>❌ BELOW CUTOFF</span>", req, tier, "Above program ceiling"

    acol1, acol2 = st.columns(2)
    for acol, campus, progs, cn in [
        (acol1, campus_1, [c1_p1, c1_p2, c1_p3], "1st"),
        (acol2, campus_2, [c2_p1, c2_p2, c2_p3], "2nd"),
    ]:
        cutoff = CAMPUS_DATA[campus]["cutoff"]
        recon  = CAMPUS_DATA[campus]["recon"]
        qualified = final_upg <= cutoff
        hdr_cls = "" if qualified else "fail"
        status_txt = "✅ QUALIFIED" if qualified else "❌ NOT QUALIFIED"
        with acol:
            st.markdown(f"""
            <div class='campus-card'>
              <div class='campus-hdr {hdr_cls}'>
                <h4>{cn} Choice — {campus}</h4>
                <p>Cutoff: {cutoff:.3f} · Your UPG: {final_upg:.3f} · {status_txt} · {CAMPUS_DATA[campus]["note"]}</p>
              </div>
              <div class='campus-body'>
            """, unsafe_allow_html=True)
            if campus == campus_2 and final_upg <= CAMPUS_DATA[campus_1]["cutoff"]:
                st.info("📌 Qualified at 1st campus — 2nd campus becomes null in the cascading UP system.")
            if qualified:
                for i, prog in enumerate(progs, 1):
                    badge, req, tier, note = evaluate_program(campus, prog, cutoff, final_upg)
                    st.markdown(f"""
                    <div class='prog-row'>
                      <div>
                        <div class='prog-name'>P{i}: {prog}</div>
                        <div class='prog-sub'>{tier} · Eff. cutoff ~{req:.3f} · {note}</div>
                      </div>
                      <div>{badge}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                recon_ok = recon > 0 and final_upg <= recon
                st.markdown(f"""
                <div style='padding:16px;text-align:center;font-family:var(--font-body);font-size:0.85rem;color:var(--fg-secondary);'>
                  UPG {final_upg:.3f} exceeds campus cutoff {cutoff:.3f}.<br><br>
                  Reconsideration: <strong>{f"{recon:.3f}" if recon>0 else "None"}</strong><br>
                  {"✅ Recon-eligible" if recon_ok else ("❌ Beyond recon range" if recon>0 else "🚫 No appeals policy")}
                </div>""", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ── DEEP ANALYTICS TABS ──
    st.markdown("""
    <div class='sec-hdr'><span class='sec-hdr-text'>🔬 Deep Analytics & Personalized Feedback</span><div class='sec-hdr-line'></div></div>
    """, unsafe_allow_html=True)

    tab_labels_res = ["📊 Overview", "📐 Grade UPG Math", "📐 Grade UPG Science",
                      "🧮 UPG Formula", "⚖️ Recon & DPWAS"]
    if math_items_data: tab_labels_res.append("🔢 Math Item Review")
    if sci_items_data:  tab_labels_res.append("🔬 Science Item Review")
    tabs_r = st.tabs(tab_labels_res)
    ti = 0

    # ── OVERVIEW ──
    with tabs_r[ti]:
        penalty_total = (m_wrong + s_wrong) * 0.25
        guess_rate = (m_wrong + s_wrong) / max(1, m_correct+m_wrong+s_correct+s_wrong)
        math_err = {sk:(1-d['correct']/max(1,d['total']))*100 for sk,d in math_topics.items()}
        sci_err  = {sk:(1-d['correct']/max(1,d['total']))*100 for sk,d in sci_topics.items()}
        top_math_gaps = sorted(math_err.items(), key=lambda x:-x[1])[:4]
        top_sci_gaps  = sorted(sci_err.items(),  key=lambda x:-x[1])[:4]

        st.markdown(f"""
        <div class='fb-box math'>
          <strong style='font-family:var(--font-display);font-size:1.1rem;'>📊 Performance Overview — {difficulty} Difficulty</strong><br><br>
          You completed this simulation placing at the <strong>{overall_pct*100:.1f}th percentile</strong> of a simulated 135,000-applicant pool
          (Rank #{sim_rank:,}). Combined UPCAT score: <strong>{combined_pct*100:.1f}%</strong> vs competitive mean {MEAN_BASELINE*100:.0f}% (σ = {SIGMA:.2f}).
          Z-score = {combined_z:+.2f}. Total penalty from wrong answers: <strong>−{penalty_total:.2f} pts</strong>.<br><br>
          {"✅ Penalty is well-controlled — you're answering selectively." if guess_rate < 0.22 else
          "⚠️ Moderate penalty — be more conservative; leave items blank if you cannot eliminate 2+ options." if guess_rate < 0.38 else
          "🔴 High penalty burden — aggressive guessing significantly hurt your score. UPCAT Math and Science reward leaving hard items blank."}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="fb-grid">', unsafe_allow_html=True)
        mini_cards = []
        if math_items_data:
            mini_cards.append(("🔢 Math Performance", f"{m_correct}/{m_total} correct · {m_pct*100:.0f}%",
                "✅ Strong math base." if m_pct>=0.65 else
                "📘 Moderate — drill JHS algebra word problems and number sense daily." if m_pct>=0.45 else
                "📖 Needs major work — JHS algebra (linear equations, factoring, ratios) is ~58% of UPCAT Math. Master these first."))
        if sci_items_data:
            mini_cards.append(("🔬 Science Performance", f"{s_correct}/{s_total} correct · {s_pct*100:.0f}%",
                "✅ Strong conceptual science." if s_pct>=0.65 else
                "📘 Moderate — practice reading experimental data under time pressure." if s_pct>=0.45 else
                "📖 Needs work — UPCAT Science is ~60% passage-based. Practice: read question FIRST, then scan stimulus for the relevant data point."))
        if math_items_data:
            m_ratio = elapsed_math / max(1, m_total) / 72
            mini_cards.append(("⏱️ Math Time (72s/item budget)", f"{int(elapsed_math//60)}m {int(elapsed_math%60)}s total · {elapsed_math/max(1,m_total):.0f}s/item",
                "✅ On pace." if 0.6<=m_ratio<=1.2 else
                "⚡ Rushed — may have made careless arithmetic errors. Slow down on multi-step items." if m_ratio<0.6 else
                "⏰ Over budget — practice mental math shortcuts: PEMDAS shortcuts, factor trees, fraction sense, divisibility rules."))
        if sci_items_data:
            s_ratio = elapsed_sci / max(1, s_total) / 60
            mini_cards.append(("⏱️ Science Time (60s/item budget)", f"{int(elapsed_sci//60)}m {int(elapsed_sci%60)}s total · {elapsed_sci/max(1,s_total):.0f}s/item",
                "✅ On pace." if 0.6<=s_ratio<=1.2 else
                "⚡ Rushed — don't skip reading the stimulus. Misreading the stimulus is the #1 source of Science errors." if s_ratio<0.6 else
                "⏰ Over budget — strategy: read the QUESTION first to know what you're looking for, then scan the stimulus for only that information."))
        mini_cards.append(("⚡ RMW Strategy", f"−{penalty_total:.2f} pts from {m_wrong+s_wrong} wrong guesses",
            "✅ Excellent guessing discipline." if guess_rate<0.20 else
            "👍 Acceptable — slightly aggressive but manageable." if guess_rate<0.30 else
            "⚠️ Too many wrong guesses. Rule: blank unless you eliminate ≥2 options. Break-even requires ≥25% confidence."))
        mini_cards.append(("🎯 Priority Study Plan", "Recommended next steps",
            "Drill JHS algebra word problems · Practice passage-based Science items · Increase difficulty next session" if combined_pct<0.55 else
            "Focus on heatmap weak areas · Practice time management · Move up one difficulty level · Target 0 wrong-guess penalties"))

        for mc_title, mc_stat, mc_body in mini_cards:
            st.markdown(f"""
            <div class='fb-mini'>
              <div class='fb-mini-title'>{mc_title}</div>
              <div class='fb-mini-body'>
                <strong style='color:var(--fg-primary);'>{mc_stat}</strong><br>
                {mc_body}
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if top_math_gaps:
            st.markdown(f"""
            <div style='margin-top:14px;padding:12px 16px;background:var(--math-glow);border:1px solid rgba(88,166,255,0.2);border-radius:var(--r-sm);'>
              <strong style='color:var(--math-primary);font-family:var(--font-body);'>🔢 Math Weak Areas (priority review order):</strong>
              <ul style='margin:8px 0 0 16px;font-family:var(--font-mono);font-size:0.74rem;color:var(--fg-secondary);'>
                {"".join(f"<li>{sk} — {e:.0f}% error rate</li>" for sk,e in top_math_gaps)}
              </ul>
            </div>""", unsafe_allow_html=True)
        if top_sci_gaps:
            st.markdown(f"""
            <div style='margin-top:10px;padding:12px 16px;background:var(--sci-glow);border:1px solid rgba(57,208,197,0.2);border-radius:var(--r-sm);'>
              <strong style='color:var(--sci-primary);font-family:var(--font-body);'>🔬 Science Weak Areas (priority review order):</strong>
              <ul style='margin:8px 0 0 16px;font-family:var(--font-mono);font-size:0.74rem;color:var(--fg-secondary);'>
                {"".join(f"<li>{sk} — {e:.0f}% error rate</li>" for sk,e in top_sci_gaps)}
              </ul>
            </div>""", unsafe_allow_html=True)
    ti += 1

    # ── MATH GRADE UPG ──
    with tabs_r[ti]:
        st.markdown('<div class="fb-box math">', unsafe_allow_html=True)
        st.markdown("### 📐 Mathematics Grade UPG (40% Weight)")
        g_cols = st.columns(4)
        for i, (lbl, val) in enumerate([
            ("G8 Math", g8_math),("G9 Math", g9_math),("G10 Math", g10_math),
            ("Pre-Calc", g11_precalc),("Basic Calc", g11_calc),("Stats", g11_stats),("Gen Math", g11_genmath)
        ]):
            g_cols[i%4].metric(lbl, f"{val:.1f}")
        st.markdown(f"""
        **Math Grade Average:** {math_grade_avg:.2f} / 100  
        **School Modifier:** {avg_mod:+.3f} ({SCHOOL_TIERS[jhs_type]['label']} · {SCHOOL_TIERS[shs_type]['label']})  
        **Math Grade UPG:** {grade_to_upg(math_grade_avg, 0):.3f} (raw) → **{math_grade_upg:.3f}** (after school mod)
        """)
        if avg_mod > 0:
            st.success(f"✅ Palugit active: school rigor protection reduces grade UPG by {avg_mod:.3f} pts.")
        elif avg_mod < 0:
            st.warning(f"⚠️ Pabigat: private school grade inflation adjustment increases UPG by {abs(avg_mod):.3f} pts.")
        with st.expander("📐 Formula"):
            st.latex(r"UPG_{\text{Math, grade}} = 5.0 - \left(\frac{\bar{G}_{\text{Math}} - 75}{25}\right) \times 4.0 - \Delta_{\text{school}}")
            st.latex(f"= 5.0 - \\frac{{{math_grade_avg:.2f}-75}}{{25}} \\times 4.0 - ({avg_mod:.3f}) = {math_grade_upg:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

    # ── SCIENCE GRADE UPG ──
    with tabs_r[ti]:
        st.markdown('<div class="fb-box sci">', unsafe_allow_html=True)
        st.markdown("### 📐 Science Grade UPG (40% Weight)")
        sg_cols = st.columns(4)
        for i, (lbl, val) in enumerate([
            ("G8 Sci", g8_sci),("G9 Sci", g9_sci),("G10 Sci", g10_sci),
            ("Gen Bio 1", g11_bio1),("Gen Bio 2", g11_bio2),("Earth Sci", g11_earth)
        ]):
            sg_cols[i%4].metric(lbl, f"{val:.1f}")
        st.markdown(f"""
        **Science Grade Average:** {sci_grade_avg:.2f} / 100  
        **School Modifier:** {avg_mod:+.3f}  
        **Science Grade UPG:** {grade_to_upg(sci_grade_avg, 0):.3f} (raw) → **{sci_grade_upg:.3f}** (after school mod)
        """)
        with st.expander("📐 Formula"):
            st.latex(r"UPG_{\text{Science, grade}} = 5.0 - \left(\frac{\bar{G}_{\text{Sci}} - 75}{25}\right) \times 4.0 - \Delta_{\text{school}}")
            st.latex(f"= 5.0 - \\frac{{{sci_grade_avg:.2f}-75}}{{25}} \\times 4.0 - ({avg_mod:.3f}) = {sci_grade_upg:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

    # ── UPG FORMULA TAB ──
    with tabs_r[ti]:
        st.markdown('<div class="fb-box green">', unsafe_allow_html=True)
        st.markdown("### 🧮 UPG Formula & UPCAT Score Analysis")
        st.markdown(f"""
        The overall UPG is a weighted combination: **40% grades + 60% UPCAT score**.
        For this simulator, Math and Science grades are averaged (the actual UPCAT uses all 4 subtests).
        """)
        with st.expander("📐 Full Math UPG Derivation"):
            st.latex(r"\text{RMW}_{\text{Math}} = \text{Correct} - \frac{1}{4}\text{Wrong}")
            st.latex(f"= {m_correct} - \\frac{{1}}{{4}} \\times {m_wrong} = {m_raw:.2f}")
            st.latex(r"Z_{\text{Math}} = \frac{P_{\text{Math}} - \mu}{\sigma}")
            st.latex(f"= \\frac{{{m_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {math_z:.4f}")
            st.latex(r"UPG_{\text{UPCAT, Math}} = \text{clamp}(2.75 - Z_{\text{Math}} \times 0.55)")
            st.latex(f"= 2.75 - ({math_z:.4f} \\times 0.55) = {math_upcat_upg:.3f}")
            st.latex(r"UPG_{\text{Math}} = 0.40 \times UPG_{\text{grade, Math}} + 0.60 \times UPG_{\text{UPCAT, Math}}")
            st.latex(f"= 0.40 \\times {math_grade_upg:.3f} + 0.60 \\times {math_upcat_upg:.3f} = {math_final_upg:.3f}")
        with st.expander("📐 Full Science UPG Derivation"):
            st.latex(r"\text{RMW}_{\text{Sci}} = \text{Correct} - \frac{1}{4}\text{Wrong}")
            st.latex(f"= {s_correct} - \\frac{{1}}{{4}} \\times {s_wrong} = {s_raw:.2f}")
            st.latex(r"Z_{\text{Sci}} = \frac{P_{\text{Sci}} - \mu}{\sigma}")
            st.latex(f"= \\frac{{{s_pct:.4f} - {MEAN_BASELINE}}}{{{SIGMA}}} = {sci_z:.4f}")
            st.latex(r"UPG_{\text{Sci}} = 0.40 \times UPG_{\text{grade, Sci}} + 0.60 \times UPG_{\text{UPCAT, Sci}}")
            st.latex(f"= 0.40 \\times {sci_grade_upg:.3f} + 0.60 \\times {sci_upcat_upg:.3f} = {sci_final_upg:.3f}")
        with st.expander("📐 Overall UPG"):
            st.latex(r"UPG_{\text{Overall}} = 0.40 \times UPG_{\text{grades}} + 0.60 \times UPG_{\text{UPCAT combined}}")
            st.latex(f"= 0.40 \\times {overall_grade_upg:.3f} + 0.60 \\times {overall_upcat_upg:.3f} = {final_upg:.3f}")
        with st.expander("📐 Real UPCAT Math vs Science (what this sim approximates)"):
            st.markdown("""
            **Actual UPCAT UPG computation** (official methodology, simplified):
            - The UPCAT has 4 subtests: Language, Reading Comprehension, Science, Mathematics.
            - Each subtest is standardized separately then combined.
            - **For STEM programs** (Engineering, CS, Nursing), Math and Science scores are weighted more heavily in the degree-predictor score used for program ranking.
            - **This simulator** approximates by computing separate Math UPG and Science UPG, then averaging them for the overall. Real UP weights may differ.
            - The key takeaway: **strong Math and Science scores are critical** for competitive STEM programs. A weak Science UPG can disqualify you from Biology/Nursing/CS even if your overall UPG is borderline qualifying.
            """)
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

    # ── RECON / DPWAS ──
    with tabs_r[ti]:
        st.markdown('<div class="fb-box amber">', unsafe_allow_html=True)
        st.markdown("### ⚖️ DPWAS, Reconsideration & Cascading Admission")
        st.markdown(f"""
        **Official UPCAT 2025 numbers:** 17,996 admission notices out of 135,236 applicants (13.3%).
        Of these, ~10,600 were direct degree-program qualifiers (~7.8%). 
        The remaining ~7,400 were waitlisted (DPWAS). 
        Being waitlisted is NOT rejection — slots open as accepted students decline, transfer, or fail to enroll.

        **How cascading works:**
        1. You name 2 campuses and up to 3 programs per campus.
        2. If you qualify at Campus 1 → Campus 2 is automatically voided.
        3. Within a campus, program slots are filled by UPG ranking. Triple-quota programs have the most slots.
        4. If you fail all programs at Campus 1, you cascade to Campus 2.

        **EEAS (Excellence-Equity Admissions System):**
        UP allocates ~70% of slots by raw UPG rank. The remaining ~30% is distributed to underrepresented areas and school types. 
        Public school students get Palugit (bonus) which improves your UPG.
        """)
        for campus in [campus_1, campus_2]:
            recon  = CAMPUS_DATA[campus]["recon"]
            cutoff = CAMPUS_DATA[campus]["cutoff"]
            st.markdown(f"**{campus}** — Cutoff: {cutoff:.3f} · Recon: {f'{recon:.3f}' if recon > 0 else 'N/A'}")
            if recon == 0.0:
                st.error(f"🚫 {campus}: Absolute no-reconsideration policy. No appeals.")
            elif final_upg <= cutoff:
                st.success(f"✅ Qualified ({final_upg:.3f} ≤ {cutoff:.3f}). No recon needed.")
            elif final_upg <= recon:
                st.warning(f"📋 Recon-eligible: UPG {final_upg:.3f} within window ({cutoff:.3f}–{recon:.3f}). Not guaranteed.")
            else:
                st.error(f"❌ UPG {final_upg:.3f} exceeds recon limit {recon:.3f}.")
        st.markdown("</div>", unsafe_allow_html=True)
    ti += 1

    # ── MATH ITEM REVIEW ──
    if math_items_data:
        with tabs_r[ti]:
            st.markdown("### 🔢 Mathematics — Item-by-Item Review with Full Solutions")
            m_w = [q for q in math_items_data if u_math.get(q['item_number']) not in [None, q['correct_answer']] and u_math.get(q['item_number'])]
            m_c_list = [q for q in math_items_data if u_math.get(q['item_number']) == q['correct_answer']]
            m_b = [q for q in math_items_data if u_math.get(q['item_number']) is None]

            st.markdown(f"""
            <div class='stat-row'>
              <div class='stat-pill'><div class='sp-num' style='color:var(--red);'>{len(m_w)}</div><div class='sp-lbl'>Wrong −0.25ea</div></div>
              <div class='stat-pill'><div class='sp-num' style='color:var(--green);'>{len(m_c_list)}</div><div class='sp-lbl'>Correct +1ea</div></div>
              <div class='stat-pill'><div class='sp-num' style='color:var(--fg-muted);'>{len(m_b)}</div><div class='sp-lbl'>Blank 0pts</div></div>
            </div>
            """, unsafe_allow_html=True)

            if m_w:
                st.markdown(f"#### ❌ Wrong ({len(m_w)}) — Priority Review:")
                for q in m_w:
                    inum = q['item_number']
                    u    = u_math.get(inum, '?')
                    c    = q['correct_answer']
                    top  = q.get('topic','').split(' — ')[0][:35]
                    with st.expander(f"❌ Math {inum:02d} · {top} · Chose {u} → Correct: {c} · −0.25 pts"):
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {opts.get(lt,'')}"
                            if lt == c:
                                st.markdown(f'<div class="ir-correct">✅ {txt}</div>', unsafe_allow_html=True)
                            elif lt == u:
                                st.markdown(f'<div class="ir-wrong">❌ {txt} ← Your answer</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="ir-option">{txt}</div>', unsafe_allow_html=True)
                        da = q.get('distractor_analysis', {})
                        if da and u in da:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Error type ({err.get('type','')}):** {err.get('error','')}")
                        sol = q.get('solution', '')
                        if sol: st.info(f"**📐 Step-by-Step Solution:**\n\n{sol}")
                        kc = q.get('key_concept', '')
                        if kc: st.caption(f"💡 Core concept: {kc}")
                        cm = q.get('common_mistake_warning', '')
                        if cm: st.caption(f"⚠️ Most common mistake: {cm}")

            if m_c_list:
                st.markdown(f"#### ✅ Correct ({len(m_c_list)}):")
                for q in m_c_list:
                    inum = q['item_number']
                    c    = q['correct_answer']
                    top  = q.get('topic','').split(' — ')[0][:35]
                    with st.expander(f"✅ Math {inum:02d} · {top} · +1.00 pt"):
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {opts.get(lt,'')}"
                            if lt == c: st.markdown(f'<div class="ir-correct">✅ {txt}</div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="ir-option">{txt}</div>', unsafe_allow_html=True)
                        with st.expander("Show solution"):
                            st.info(q.get('solution',''))

            if m_b:
                st.markdown(f"#### ⚪ Skipped ({len(m_b)}):")
                for q in m_b:
                    inum = q['item_number']
                    c    = q['correct_answer']
                    top  = q.get('topic','').split(' — ')[0][:35]
                    with st.expander(f"⚪ Math {inum:02d} · {top} · 0 pts (skipped)"):
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {opts.get(lt,'')}"
                            if lt == c: st.markdown(f'<div class="ir-correct">✅ {txt}</div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="ir-option">{txt}</div>', unsafe_allow_html=True)
                        st.info(f"**Solution:**\n\n{q.get('solution','')}")
        ti += 1

    # ── SCIENCE ITEM REVIEW ──
    if sci_items_data:
        with tabs_r[ti]:
            st.markdown("### 🔬 Science — Item-by-Item Review with Full Explanations")
            s_w = [q for q in sci_items_data if u_sci.get(q['item_number']) not in [None, q['correct_answer']] and u_sci.get(q['item_number'])]
            s_c_list = [q for q in sci_items_data if u_sci.get(q['item_number']) == q['correct_answer']]
            s_b = [q for q in sci_items_data if u_sci.get(q['item_number']) is None]

            st.markdown(f"""
            <div class='stat-row'>
              <div class='stat-pill'><div class='sp-num' style='color:var(--red);'>{len(s_w)}</div><div class='sp-lbl'>Wrong −0.25ea</div></div>
              <div class='stat-pill'><div class='sp-num' style='color:var(--green);'>{len(s_c_list)}</div><div class='sp-lbl'>Correct +1ea</div></div>
              <div class='stat-pill'><div class='sp-num' style='color:var(--fg-muted);'>{len(s_b)}</div><div class='sp-lbl'>Blank 0pts</div></div>
            </div>
            """, unsafe_allow_html=True)

            if s_w:
                st.markdown(f"#### ❌ Wrong ({len(s_w)}) — Priority Review:")
                for q in s_w:
                    inum = q['item_number']
                    u    = u_sci.get(inum, '?')
                    c    = q['correct_answer']
                    top  = q.get('topic','').split(' — ')[0][:30]
                    disc = q.get('science_discipline','')
                    stim_type = q.get('stimulus_type', '')
                    with st.expander(f"❌ Sci {inum:02d} · {top} [{disc}] · Chose {u} → Correct: {c} · −0.25 pts"):
                        stim = q.get('stimulus', '')
                        if stim:
                            if stim_type == "DATA_TABLE":
                                st.markdown(f'<div class="sci-data-box">{stim}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="sci-passage">{stim}</div>', unsafe_allow_html=True)
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {opts.get(lt,'')}"
                            if lt == c: st.markdown(f'<div class="ir-correct">✅ {txt}</div>', unsafe_allow_html=True)
                            elif lt == u: st.markdown(f'<div class="ir-wrong">❌ {txt} ← Your answer</div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="ir-option">{txt}</div>', unsafe_allow_html=True)
                        da = q.get('distractor_analysis', {})
                        if da and u in da:
                            err = da[u]
                            if isinstance(err, dict):
                                st.warning(f"**Why {u} is wrong ({err.get('type','')}):** {err.get('error','')}")
                        sol = q.get('solution','')
                        if sol: st.info(f"**🔬 Full Explanation:**\n\n{sol}")
                        pr = q.get('passage_reference','')
                        if pr: st.caption(f"📍 Key stimulus data: {pr}")
                        kc = q.get('key_concept','')
                        if kc: st.caption(f"💡 Core concept: {kc}")

            if s_c_list:
                st.markdown(f"#### ✅ Correct ({len(s_c_list)}):")
                for q in s_c_list:
                    inum = q['item_number']
                    c    = q['correct_answer']
                    top  = q.get('topic','').split(' — ')[0][:30]
                    with st.expander(f"✅ Sci {inum:02d} · {top} · +1.00 pt"):
                        stim = q.get('stimulus','')
                        if stim:
                            if q.get('stimulus_type') == "DATA_TABLE":
                                st.markdown(f'<div class="sci-data-box" style="max-height:120px;overflow:auto;">{stim}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="sci-passage" style="max-height:100px;">{stim}</div>', unsafe_allow_html=True)
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {opts.get(lt,'')}"
                            if lt == c: st.markdown(f'<div class="ir-correct">✅ {txt}</div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="ir-option">{txt}</div>', unsafe_allow_html=True)
                        with st.expander("Show full explanation"):
                            st.info(q.get('solution',''))

            if s_b:
                st.markdown(f"#### ⚪ Skipped ({len(s_b)}):")
                for q in s_b:
                    inum = q['item_number']
                    c    = q['correct_answer']
                    top  = q.get('topic','').split(' — ')[0][:30]
                    with st.expander(f"⚪ Sci {inum:02d} · {top} · 0 pts"):
                        stim = q.get('stimulus','')
                        if stim:
                            st.markdown(f'<div class="sci-passage" style="max-height:100px;">{stim}</div>', unsafe_allow_html=True)
                        st.markdown(f"**Question:** {q.get('question_text','')}")
                        opts = q.get('options', {})
                        for lt in ['A','B','C','D']:
                            txt = f"**{lt})** {opts.get(lt,'')}"
                            if lt == c: st.markdown(f'<div class="ir-correct">✅ {txt}</div>', unsafe_allow_html=True)
                            else: st.markdown(f'<div class="ir-option">{txt}</div>', unsafe_allow_html=True)
                        st.info(f"**Explanation:**\n\n{q.get('solution','')}")

    # ── RESET ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns([1,2,1])
    with rc2:
        st.markdown("""
        <div style='text-align:center;font-family:var(--font-body);font-size:0.80rem;color:var(--fg-muted);margin-bottom:10px;'>
          Generate a fresh set of items — all sidebar settings are preserved.
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Generate Fresh Items & Reset", use_container_width=True, type="secondary"):
            for k in ['user_answers_math','user_answers_sci','submitted','test_data',
                      'flagged_items','math_started','sci_started','math_submitted','sci_submitted',
                      'math_start_time','sci_start_time','elapsed_math','elapsed_sci']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
