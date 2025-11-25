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

# --- CUSTOM CSS (Mobile-App Style) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    /* Card Style for Menu Items */
    .menu-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border: 1px solid #E0E0E0;
        cursor: pointer;
        transition: transform 0.1s;
    }
    .menu-card:hover {
        transform: scale(1.02);
    }
    .reviewed-tag {
        color: #2e7d32;
        font-weight: bold;
        font-size: 0.9em;
    }
    /* Header Style */
    .app-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 50px;
        font-weight: 600;
    }
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'upload' # upload -> analyzing -> overview -> detail -> report

if 'current_category' not in st.session_state:
    st.session_state.current_category = None

if 'reviewed_categories' not in st.session_state:
    st.session_state.reviewed_categories = set()

# Mock Data Structure
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {
        "Navigation": {
            "issues": [
                {"id": "n1", "text": "Back button placement is inconsistent.", "accepted": True, "comment": ""},
                {"id": "n2", "text": "Menu hierarchy is too deep.", "accepted": True, "comment": ""}
            ]
        },
        "Visual Design": {
            "issues": [
                {"id": "v1", "text": "Primary color contrast is low.", "accepted": True, "comment": ""},
                {"id": "v2", "text": "Font size is too small for mobile.", "accepted": True, "comment": ""}
            ]
        },
        "Consistency": {
            "issues": [
                {"id": "c1", "text": "Button styles vary across screens.", "accepted": True, "comment": ""}
            ]
        }
    }

# --- FUNCTIONS ---
def change_state(new_state):
    st.session_state.app_state = new_state
    st.rerun()

def select_category(category_name):
    st.session_state.current_category = category_name
    change_state('detail')

def mark_category_reviewed():
    if st.session_state.current_category:
        st.session_state.reviewed_categories.add(st.session_state.current_category)
    change_state('overview')

def reset_app():
    st.session_state.app_state = 'upload'
    st.session_state.reviewed_categories = set()
    st.session_state.current_category = None
    st.rerun()

# --- UI SCREENS ---

# SCREEN 1: UPLOAD (Start)
if st.session_state.app_state == 'upload':
    st.markdown("<div class='app-header'><h1>🤖 UI Feedback</h1></div>", unsafe_allow_html=True)
    
    # Robot Illustration Placeholder
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=150)
    st.markdown("<h3 style='text-align: center;'>Hello! Upload your interface.</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=['png', 'jpg'], label_visibility="collapsed")
    
    if uploaded_file:
        st.success("Image Uploaded!")
        if st.button("Analyze Interface", type="primary"):
            change_state('analyzing')

# SCREEN 2: ANALYZING (Robot Thinking)
elif st.session_state.app_state == 'analyzing':
    st.markdown("<div class='app-header'><h1>Analyzing...</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2040/2040946.png", caption="Processing...", width=150)
    
    my_bar = st.progress(0)
    status = st.empty()
    
    steps = ["Scanning Layout...", "Checking Contrast...", "Verifying Consistency...", "Done!"]
    for i, step in enumerate(steps):
        status.text(step)
        my_bar.progress((i + 1) * 25)
        time.sleep(0.7)
    
    change_state('overview')

# SCREEN 3 & 5: FEEDBACK OVERVIEW (The Hub)
elif st.session_state.app_state == 'overview':
    st.markdown("<div class='app-header'><h1>🤖 Feedback</h1></div>", unsafe_allow_html=True)
    
    # Progress Section
    reviewed_count = len(st.session_state.reviewed_categories)
    total_count = len(st.session_state.analysis_data)
    
    if reviewed_count > 0:
        st.markdown(f"**Reviewed: {reviewed_count}/{total_count} Categories**")
        st.progress(reviewed_count / total_count)
    
    st.write("### Categories")

    # Render Category Buttons/Cards
    for category in st.session_state.analysis_data.keys():
        is_reviewed = category in st.session_state.reviewed_categories
        status_icon = "✅" if is_reviewed else "👉"
        status_text = "Reviewed" if is_reviewed else "Pending"
        
        # We use a button to simulate the "Click" arrow flow
        btn_label = f"{status_icon} {category} \n({status_text})"
        if st.button(btn_label, key=f"btn_{category}", use_container_width=True):
            select_category(category)

    st.markdown("---")
    
    # Final Report Button (Active only if at least one reviewed, or always active as per prototype)
    if reviewed_count == total_count:
        if st.button("Create Final Report", type="primary"):
            change_state('report')
    else:
        st.caption("Review all categories to generate the final report.")

# SCREEN 4: DETAIL VIEW (Specific Feedback Interactions)
elif st.session_state.app_state == 'detail':
    cat = st.session_state.current_category
    st.markdown(f"<div class='app-header'><h3>< {cat}</h3></div>", unsafe_allow_html=True)
    
    issues = st.session_state.analysis_data[cat]['issues']
    
    for i, issue in enumerate(issues):
        st.info(f"**Issue {i+1}:** {issue['text']}")
        
        # Interactions: Thumbs Up/Down (Toggle) & Comment
        col1, col2 = st.columns([1, 4])
        with col1:
             # Using a toggle to represent the thumbs up/down decision
            issue['accepted'] = st.toggle("Accept", value=issue['accepted'], key=f"acc_{cat}_{i}")
        with col2:
            issue['comment'] = st.text_input("Add comment", value=issue['comment'], placeholder="Context...", key=f"com_{cat}_{i}")
        
        st.markdown("---")
    
    # Back button that marks as reviewed
    if st.button(f"Done Reviewing {cat}"):
        mark_category_reviewed()

# SCREEN 6: FINAL REPORT
elif st.session_state.app_state == 'report':
    st.markdown("<div class='app-header'><h1>📊 Final Report</h1></div>", unsafe_allow_html=True)
    st.balloons()
    
    st.success("Human-AI Collaborative Audit Complete!")
    
    # Display Summary
    st.subheader("Summary")
    for cat, data in st.session_state.analysis_data.items():
        st.markdown(f"**{cat}**")
        for issue in data['issues']:
            status = "✅ Accepted" if issue['accepted'] else "❌ Rejected"
            st.text(f"- {status}: {issue['text']}")
            if issue['comment']:
                st.caption(f"  Note: {issue['comment']}")
        st.markdown("")

    if st.button("Start New Audit"):
        reset_app()
