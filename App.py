import streamlit as st
import pandas as pd
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="UI Analyzer Prototype",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (Matching the Screenshots) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    /* Style for the Expanders to look like Cards */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .streamlit-expanderContent {
        background-color: white;
        border-left: 1px solid #E0E0E0;
        border-right: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        margin-top: -5px; /* Connect header to content */
    }
    /* Section Headers */
    .section-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    /* Reviewed Item Style */
    .reviewed-item {
        color: #2e7d32;
        font-size: 1rem;
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
    .app-header {
        text-align: center;
        margin-bottom: 20px;
    }
    /* Buttons */
    .stButton>button {
        border-radius: 20px;
        font-weight: 600;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'upload' 

if 'reviewed_categories' not in st.session_state:
    st.session_state.reviewed_categories = set()

# Initialize Data if not present
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {
        "Visual Design": {
            "issues": [
                {"id": "v1", "text": "Primary button contrast is too low (3.5:1).", "accepted": True, "comment": ""},
                {"id": "v2", "text": "Font hierarchy is unclear in the header.", "accepted": True, "comment": ""},
                {"id": "v3", "text": "Icon stroke weights are inconsistent.", "accepted": True, "comment": ""}
            ]
        },
        "Consistency": {
            "issues": [
                {"id": "c1", "text": "Card padding varies (16px vs 24px).", "accepted": True, "comment": ""},
                {"id": "c2", "text": "Submit button style differs on Page 2.", "accepted": True, "comment": ""}
            ]
        },
        "Navigation": {
            "issues": [
                {"id": "n1", "text": "Back button missing on detail screen.", "accepted": True, "comment": ""}
            ]
        }
    }

# --- FUNCTIONS ---
def change_state(new_state):
    st.session_state.app_state = new_state
    st.rerun()

def mark_reviewed(category):
    st.session_state.reviewed_categories.add(category)
    st.rerun()

def reset_app():
    st.session_state.app_state = 'upload'
    st.session_state.reviewed_categories = set()
    st.rerun()

# --- UI SCREENS ---

# 1. UPLOAD SCREEN
if st.session_state.app_state == 'upload':
    st.markdown("<div class='app-header'><h1>🤖 UI Analyzer</h1></div>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=120)
    st.markdown("<h3 style='text-align: center;'>Upload Interface</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=['png', 'jpg'], label_visibility="collapsed")
    
    if uploaded_file:
        st.success("Image Uploaded!")
        if st.button("Analyze UI", type="primary"):
            change_state('analyzing')

# 2. ANALYZING SCREEN
elif st.session_state.app_state == 'analyzing':
    st.markdown("<div class='app-header'><h1>Analyzing...</h1></div>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040946.png", width=120)
    
    my_bar = st.progress(0)
    status = st.empty()
    steps = ["Scanning Layout...", "Checking Contrast...", "Verifying Consistency...", "Generating Feedback..."]
    
    for i, step in enumerate(steps):
        status.text(step)
        my_bar.progress((i + 1) * 25)
        time.sleep(0.5)
    
    change_state('feedback_hub')

# 3. FEEDBACK HUB (Main Interaction Screen)
elif st.session_state.app_state == 'feedback_hub':
    st.markdown("<div class='app-header'><h1>🤖 Feedback</h1></div>", unsafe_allow_html=True)
    
    # Separation of Pending vs Reviewed
    all_cats = list(st.session_state.analysis_data.keys())
    pending_cats = [c for c in all_cats if c not in st.session_state.reviewed_categories]
    reviewed_cats = list(st.session_state.reviewed_categories)

    # --- PENDING CARDS (With Scrollers) ---
    if pending_cats:
        for cat in pending_cats:
            # Using Expander as the "Card" container
            with st.expander(f"📌 {cat}", expanded=True):
                
                # THE SCROLLER: Container with fixed height
                with st.container(height=200):
                    issues = st.session_state.analysis_data[cat]['issues']
                    for i, issue in enumerate(issues):
                        st.markdown(f"**Issue {i+1}:** {issue['text']}")
                        
                        # In-place interactions
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            issue['accepted'] = st.toggle("Accept", value=issue['accepted'], key=f"tg_{cat}_{i}")
                        with c2:
                            issue['comment'] = st.text_input("Comment", value=issue['comment'], placeholder="Add context...", key=f"txt_{cat}_{i}", label_visibility="collapsed")
                        
                        st.divider()
                
                # "Done" button footer for the card
                if st.button(f"Mark {cat} as Reviewed", key=f"done_{cat}"):
                    mark_reviewed(cat)
    else:
        st.info("All categories reviewed! You can now generate the report.")
        if st.button("Create Final Report", type="primary"):
            change_state('report')

    # --- REVIEWED SECTION (Bottom List) ---
    if reviewed_cats:
        st.markdown("<div class='section-header'>Reviewed</div>", unsafe_allow_html=True)
        for cat in reviewed_cats:
            st.markdown(f"<div class='reviewed-item'>✅ {cat}</div>", unsafe_allow_html=True)

# 4. FINAL REPORT
elif st.session_state.app_state == 'report':
    st.markdown("<div class='app-header'><h1>📊 Final Report</h1></div>", unsafe_allow_html=True)
    st.balloons()
    
    st.subheader("Audit Summary")
    
    for cat, data in st.session_state.analysis_data.items():
        st.markdown(f"### {cat}")
        for issue in data['issues']:
            status = "✅ Accepted" if issue['accepted'] else "❌ Rejected"
            st.markdown(f"- {status}: {issue['text']}")
            if issue['comment']:
                st.info(f"  📝 Note: {issue['comment']}")
        st.markdown("---")

    if st.button("Start New Audit"):
        reset_app()