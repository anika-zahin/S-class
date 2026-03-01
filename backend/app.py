import streamlit as st
from streamlit_drawable_canvas import st_canvas
import easyocr
from groq import Groq
from fpdf import FPDF
import numpy as np
import cv2

# --- 1. GLOBAL UI CONFIGURATION (Professional Theme) ---
st.set_page_config(page_title="Smart Class Notes AI | Your Lecture, Transformed", layout="wide", initial_sidebar_state="collapsed")

# Advanced CSS Overhaul for a Premium and Harmonious User Experience
st.markdown("""
    <style>
    /* Force high-quality light theme aesthetic */
    .stApp { background-color: #F8FAFC; color: #1E293B !important; font-family: 'Inter', -apple-system, sans-serif !important; }
    
    /* Hide default Streamlit noise (header, footer) for full focus */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Force all non-button text to be dark gray or black */
    h1, h2, h3, h4, p, span, label { color: #0F172A !important; }

    /* --- App Header Styling --- */
    .app-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 1rem 2rem; background: white; border-radius: 12px;
        margin-bottom: 2rem; border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
    }
    .header-left { display: flex; align-items: center; gap: 1rem; }
    
    /* --- Main Content Area (Cards) --- */
    .main-card {
        background: white; padding: 2.5rem; border-radius: 20px;
        border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05);
    }
    
    /* --- Unified Pen Toolbar --- */
    .toolbar-container {
        background: #F1F5F9; padding: 1rem 1.5rem; border-radius: 10px;
        margin-bottom: 2rem; border: 1px solid #E2E8F0;
        display: flex; gap: 1.5rem; align-items: center;
    }
    
    /* Color Circle Styling */
    .color-option { width: 30px; height: 30px; border-radius: 50%; border: 2px solid #E2E8F0; cursor: pointer; }
    .color-label { font-size: 0.9rem; font-weight: 500; color: #475569 !important; margin-right: 0.5rem; }

    /* --- Action Button Colors --- */
    /* Primary Action (Generate) */
    div[data-testid="stTopBar"] .stButton > button { background-color: #A78BFA !important; color: white !important; border: none !important; padding: 10px 20px !important; }
    /* Secondary Action (Convert Text) */
    .stButton>button { border-radius: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; transition: all 0.2s ease; }
    div[data-testid="stVerticalBlock"] > div:nth-child(4) button { background-color: #3B82F6 !important; color: white !important; border: none !important; height: 3rem !important; }
    /* Danger Action (Clear) */
    .clear-btn > div > button { background-color: #EF4444 !important; color: white !important; border: none !important; }

    /* Fix the legend label color in select_slider */
    [data-testid="stSelectSlider"] span { color: #64748B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND & SESSION INITIALIZATION ---

client = Groq(api_key="GROQ_API_KEY") #type: ignore 

@st.cache_resource
def load_ocr():
    # Load EasyOCR once and cache it to keep the drawing canvas responsive
    return easyocr.Reader(['en'])

reader = load_ocr()

# Data persistence between page syncs
if 'lecture_text' not in st.session_state:
    st.session_state.lecture_text = ""

# --- 3. THE APP HEADER (Branding & Generate) ---
st.markdown('<div class="app-header">', unsafe_allow_html=True)
col_header_left, col_header_right = st.columns([4, 1])

with col_header_left:
    st.markdown("""
        <div class="header-left">
            <img src="https://cdn-icons-png.flaticon.com/512/3429/3429149.png" width="50"/>
            <div>
                <h2 style='margin:0; font-size:2.2rem; font-weight:800; color:#3B82F6 !important;'>Smart Class Notes AI</h2>
                <p style='margin:0; font-size:1.1rem; color:#64748B !important; font-weight:500;'>AI-powered handwriting recognition & study tools</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_header_right:
    generate_all = st.button("Download All PDFs", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. THE NAVIGATION TABS (UI Simulation of future sections) ---
tab_cols = st.columns([1, 1, 1.2, 1])
active_tab_style = "background-color: #3B82F6; color: white !important; border-radius: 10px;"
inactive_tab_style = "color: #475569 !important;"

# This forces the app to only show the 'Write' tab logic below, matching the reference state
tab_cols[0].markdown(f'<div style="{active_tab_style} text-align:center; padding:12px; font-weight:600;">🖊️ Write</div>', unsafe_allow_html=True)
tab_cols[1].markdown(f'<div style="{inactive_tab_style} text-align:center; padding:12px; font-weight:600;">📄 Notes</div>', unsafe_allow_html=True)
tab_cols[2].markdown(f'<div style="{inactive_tab_style} text-align:center; padding:12px; font-weight:600;">📖 Cheat Sheet</div>', unsafe_allow_html=True)
tab_cols[3].markdown(f'<div style="{inactive_tab_style} text-align:center; padding:12px; font-weight:600;">❓ Quiz</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- 5. THE MAIN CONTENT AREA (The 'Write' tab logic) ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# 🎨 THE UNIFIED TOOLBAR (Simulating the cohesive controls in image_3.png)
st.markdown('<div class="toolbar-container">', unsafe_allow_html=True)
t_pen_tools, t_colors, t_size, t_clear = st.columns([1.5, 3, 2, 1])

with t_pen_tools:
    # A segmented control is modern, high-contrast, and professional
    drawing_mode = st.segmented_control("Tools", options=["freedraw", "eraser"], default="freedraw", label_visibility="collapsed")

with t_colors:
    st.markdown('<span class="color-label">Color:</span>', unsafe_allow_html=True)
    # The reference uses a series of simple color circles, simulated by a streamlined color picker for now
    stroke_color = st.color_picker("Pen Color", "#1E293B", label_visibility="collapsed")
    # You can add the specific color circles (Blue, Red, Green, etc.) by creating HTML/CSS circles here in a future update

with t_size:
    # select_slider is much cleaner and has fixed contrast labels compared to the regular slider
    stroke_width = st.select_slider("Thickness", options=[1, 2, 3, 5, 8], value=3, label_visibility="visible")

with t_clear:
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.lecture_text = ""
        # streamlit-drawable-canvas currently requires a page rerun to force a clear of the drawing layer
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 🖊️ THE CLEAN DRAWING CANVAS
canvas_result = st_canvas(
    fill_color="rgba(59, 130, 246, 0.05)",  # Very subtle blue fill for selected areas
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",  # Pure white canvas for high contrast
    height=550,
    drawing_mode=drawing_mode,
    key="pro_full_canvas",
    update_streamlit=True
)

st.markdown("<br>", unsafe_allow_html=True)

# 🚀 THE PRIMARY ACTION BUTTONS
b_sync, b_gen = st.columns([2, 1])

with b_sync:
    # Using toast notifications is less disruptive than a new status box, perfect for a pro UI
    if st.button("🔄 Sync Section to AI", use_container_width=True):
        if canvas_result.image_data is not None:
            with st.spinner("AI Reading board..."):
                # Convert canvas data to OCR-ready format
                img = cv2.cvtColor(canvas_result.image_data.astype(np.uint8), cv2.COLOR_RGBA2BGR)
                results = reader.readtext(img)
                new_text = " ".join([res[1] for res in results])
                
                if new_text.strip():
                    st.session_state.lecture_text += " " + new_text
                    st.toast(f"Captured: {new_text[:30]}...", icon="🎯")
                else:
                    st.toast("Write something first!", icon="⚠️")

# This is the "primary action" for the lecture, placed prominently at the end of the drawing section
with b_gen:
    generate_btn = st.button("Generate Detailed Notes PDF", use_container_width=True)

# Closing the main content card
st.markdown('</div>', unsafe_allow_html=True)


# --- 6. DOCUMENT GENERATION LOGIC (Placeholder for now) ---
# A professional app will show the results only after generation is complete
if generate_btn or generate_all:
    if not st.session_state.lecture_text:
        st.error("There is nothing to process! Please write on the board and 'Sync' first.")
    else:
        with st.spinner("Analyzing lecture data and creating professional PDFs..."):
            # Llama 3.1 is tasked with synthesis and structuring
            prompt = f"""
            You are an expert professor. Given these class notes (brief keywords/fragments): "{st.session_state.lecture_text}"
            
            Please create a detailed student study guide containing:
            1. FULL LECTURE NOTES: Detailed definitions and paragraphs on each topic.
            2. CHEAT SHEET: A highly concise, bulleted list of essential formulas and keywords.
            3. A 5-question multiple choice QUIZ with an Answer Key.
            """
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            data_content = chat_completion.choices[0].message.content

            # PDF GENERATION FUNCTION (Simple simulation of detailed notes)
            def create_pdf(text, title):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(0, 20, txt=title, ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", size=12)
                # Clean text for PDF encoding
                clean_text = text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, txt=clean_text)
                return bytes(pdf.output())

            # Generate the combined byte data
            notes_pdf_bytes = create_pdf(data_content, "Official Study Notes")

            # In a pro UI, we don't dump all the text to the screen; we just show download cards
            st.markdown("<br>", unsafe_allow_html=True)
            col_results1, col_results2 = st.columns(2)
            
            with col_results1:
                st.markdown('<div class="main-card"><h3>📄 Lecture Study Bundle</h3><p>Your full study guide, cheat sheet, and quiz are ready in a single high-quality PDF.</p></div>', unsafe_allow_html=True)
                st.download_button("📥 Download Combined PDF Bundle", data=notes_pdf_bytes, file_name="Class_Study_Bundle.pdf", mime="application/pdf", use_container_width=True)
            
            # This logic will need to be refined to generate separate PDFs when you add the specific content tabs
            with col_results2:

                 st.info("The individual Cheat Sheet and Quiz tabs are currently a simulated view. This 'Bundle' includes all three sections.")
