import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import time
import os 
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide", page_title="Gurgaon Real Estate Game")
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
# Initialize Session States

if 'current_target_idx' not in st.session_state:
    st.session_state.current_target_idx = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'correct_sectors' not in st.session_state:
    st.session_state.correct_sectors = []
# --- CONFIGURATION ---
BLANK_MAP_PATH = 'blank_gurgaon_map.png' 
ORIGINAL_MAP_PATH = 'gurgaon-map-watermark.jpg' # The one with labels
DATA_FILE = 'sector_logic.csv'
# ---------------------
TIME_LIMIT = 60  # 1 minutes in seconds
if not st.session_state.game_over:
    st_autorefresh(interval=1000, key="countdown_timer")

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['sector', 'x_pct', 'y_pct', 'landmark'])
    df = pd.read_csv(DATA_FILE)
    df.columns = [str(c).lower().strip() for c in df.columns]
    return df

df = load_data()
# Logic to pick next target
remaining_df = df[~df['sector'].astype(str).isin([str(s['sector']) for s in st.session_state.correct_sectors])]

# --- 1. UPDATED GAME LOGIC (RANDOMIZATION) ---
if st.session_state.game_over or remaining_df.empty:
    st.session_state.game_over = True
    st.session_state.current_target_idx = None
else:
    # If no target is set, or the previous one was solved, pick a RANDOM index
    if 'current_target_idx' not in st.session_state or st.session_state.current_target_idx not in remaining_df.index:
        st.session_state.current_target_idx = remaining_df.sample(1).index[0]

# Set the target using the saved index so it stays the same during timer refreshes
if st.session_state.current_target_idx is not None:
    target = df.loc[st.session_state.current_target_idx]
else:
    target = None

# --- 2. SIDEBAR UI ---
# --- MAIN UI (REPLACING SIDEBAR) ---
st.title("📍 Sector Trainer")

# Timer & Stats Row (Visible immediately on phone)
col_a, col_b = st.columns(2)
with col_a:
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, TIME_LIMIT - elapsed)
    if remaining <= 0 and not st.session_state.game_over:
        st.session_state.game_over = True
        st.rerun()
    st.subheader(f"⏳ {remaining // 60}m {remaining % 60}s")
with col_b:
    guessed = len(st.session_state.correct_sectors)
    total = len(df)
    st.subheader(f"🎯 {guessed}/{total}")

st.progress(guessed / total if total > 0 else 0)

# Active Play UI
# --- REFINED CLUE LOGIC ---
# --- ACTION AREA (WITH AUTO-CLEAR) ---
if not st.session_state.game_over and target is not None:
    s_val = str(target['sector']).strip()
    
    # Generic prompt: Forces use of the map
    st.markdown("### Identify the Sector marked in Red 📍")
    
    with st.form("guess_form", clear_on_submit=True):
        guess = st.text_input("Enter Sector Number:", label_visibility="collapsed", placeholder="Type Sector # here...")
        
        # Form submit buttons
        submit_btn = st.form_submit_button("SUBMIT ANSWER", use_container_width=True, type="primary")
        
        c1, c2 = st.columns(2)
        with c1:
            skip_btn = st.form_submit_button("SKIP", use_container_width=True)
        with c2:
            exit_btn = st.form_submit_button("EXIT", use_container_width=True)

    # Logic is processed only after a form button is clicked
    if submit_btn:
        if guess.strip().lower() == s_val.lower():
            st.session_state.correct_sectors.append(target.to_dict())
            st.session_state.current_target_idx = None # Safely empty it, don't delete it
            st.balloons()
            
        else:
            pass
            # Rerun silently on wrong answer; the form will auto-clear
            

    if skip_btn:
        st.session_state.current_target_idx = None # Safely empty it
        

    if exit_btn:
        st.session_state.game_over = True
        st.rerun()

else:
    # Game Over / Success screen
    st.success(f"Final Score: {guessed}/{total}!")
    if st.button("RESTART", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.divider()

# --- MAP RENDERING ---
active_map_file = ORIGINAL_MAP_PATH if st.session_state.game_over else BLANK_MAP_PATH

try:
    img = Image.open(active_map_file).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for s in st.session_state.correct_sectors:
        x, y = s['x_pct'] * w, s['y_pct'] * h
        draw.ellipse([x-15, y-15, x+15, y+15], fill="#2ecc71", outline="white")

    if not st.session_state.game_over and target is not None:
        tx, ty = target['x_pct'] * w, target['y_pct'] * h
        draw.ellipse([tx-25, ty-25, tx+25, ty+25], outline="#e74c3c", width=8)

    st.image(img, use_container_width=True)
except Exception as e:
    st.error(f"Image Error: Ensure map files are in the folder. ({e})")
