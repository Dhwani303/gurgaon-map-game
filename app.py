import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import time

# --- CONFIGURATION ---
BLANK_MAP_PATH = 'blank_gurgaon_map.png' 
ORIGINAL_MAP_PATH = 'gurgaon-map-watermark.jpg' # The one with labels
DATA_FILE = 'sector_logic.csv'
# ---------------------

st.set_page_config(layout="wide", page_title="Gurgaon Real Estate Game")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df.columns = [str(c).lower().strip() for c in df.columns]
    return df

# Initialize Session States
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'correct_sectors' not in st.session_state:
    st.session_state.correct_sectors = []
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

df = load_data()

# Logic to pick next target
remaining_df = df[~df['sector'].astype(str).isin([str(s['sector']) for s in st.session_state.correct_sectors])]

if not remaining_df.empty and not st.session_state.game_over:
    # Always pick the first one from the remaining to stay consistent
    target = remaining_df.iloc[0]
else:
    st.session_state.game_over = True

# --- SIDEBAR UI ---
with st.sidebar:
    st.title("📊 Progress")
    
    # 3. Guess Tracker
    total = len(df)
    guessed = len(st.session_state.correct_sectors)
    st.metric("Sectors Mastered", f"{guessed} / {total}")
    st.progress(guessed / total)

    # 2. Timer
    if not st.session_state.game_over:
        elapsed = int(time.time() - st.session_state.start_time)
        st.write(f"⏱️ Time Elapsed: {elapsed // 60}m {elapsed % 60}s")
    
    st.divider()

    if not st.session_state.game_over:
        st.header("Identify Target")
        if 'landmark' in target and pd.notna(target['landmark']):
            st.info(f"Clue: Near {target['landmark']}")
        
        guess = st.text_input("Enter Sector Number:", key="guess")
        if st.button("Submit Answer"):
            if guess.strip().lower() == str(target['sector']).lower():
                st.session_state.correct_sectors.append(target.to_dict())
                st.rerun()
            else:
                st.error("Incorrect. Try again!")
    
    # 1. End Game / Reveal Solution
    if st.button("End Game & Reveal Map"):
        st.session_state.game_over = True
        st.rerun()

    if st.button("Restart Training"):
        st.session_state.clear()
        st.rerun()

# --- MAIN MAP DISPLAY ---
# Switch image based on game state
current_map = ORIGINAL_MAP_PATH if st.session_state.game_over else BLANK_MAP_PATH
img = Image.open(current_map).convert("RGB")
draw = ImageDraw.Draw(img)
w, h = img.size

# Draw revealed sectors
for s in st.session_state.correct_sectors:
    x, y = s['x_pct'] * w, s['y_pct'] * h
    draw.ellipse([x-15, y-15, x+15, y+15], fill="#2ecc71", outline="white")

# Draw current target if game is active
if not st.session_state.game_over:
    tx, ty = target['x_pct'] * w, target['y_pct'] * h
    draw.ellipse([tx-25, ty-25, tx+25, ty+25], outline="#e74c3c", width=8)

st.image(img, use_container_width=True)

if st.session_state.game_over:
    st.balloons()
    st.success(f"Final Score: {guessed}/{total}! Full map revealed below.")