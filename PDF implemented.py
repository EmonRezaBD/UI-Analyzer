import streamlit as st
import pandas as pd
import time
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(
    page_title="UI Analyzer",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT ---
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'upload' 
if 'reviewed_categories' not in st.session_state:
    st.session_state.reviewed_categories = set()
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Initialize Data
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

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("⚙️ Settings")
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode
    
    st.divider()
    st.caption("App Navigation")
    if st.button("🏠 Home / Upload"):
        st.session_state.app_state = 'upload'
        st.rerun()
    if st.button("🔄 Reset Analysis"):
        st.session_state.app_state = 'upload'
        st.session_state.reviewed_categories = set()
        st.rerun()

# --- THEME COLORS ---
if dark_mode:
    bg_color = "#18191a"
    card_bg = "#242526"
    text_color = "#e4e6eb"
    border_color = "#393a3b"
    accent_color = "#2D88FF"
    secondary_text = "#b0b3b8"
    shadow = "rgba(0,0,0,0.5)"
else:
    bg_color = "#f0f2f5"
    card_bg = "#ffffff"
    text_color = "#050505"
    border_color = "#e4e6eb"
    accent_color = "#1b74e4"
    secondary_text = "#65676b"
    shadow = "rgba(0,0,0,0.08)"

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .nav-header {{
        background-color: {card_bg}; padding: 15px 30px; border-bottom: 1px solid {border_color};
        margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 2px 4px {shadow};
    }}
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important; color: {text_color} !important;
        border-radius: 8px; border: 1px solid {border_color}; margin-bottom: 10px;
    }}
    .streamlit-expanderContent {{
        background-color: {card_bg} !important; color: {text_color} !important;
        border: 1px solid {border_color}; border-top: none;
        border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;
        box-shadow: 0 4px 12px {shadow};
    }}
    .custom-card {{
        background-color: {card_bg}; padding: 20px; border-radius: 8px;
        box-shadow: 0 2px 8px {shadow}; border: 1px solid {border_color}; margin-bottom: 20px;
    }}
    h1, h2, h3, h4, p, label, .stMarkdown {{ color: {text_color} !important; }}
    .secondary-text {{ color: {secondary_text} !important; font-size: 0.9rem; }}
    .reviewed-item {{
        padding: 12px; border-bottom: 1px solid {border_color}; display: flex;
        align-items: center; color: #2e7d32; font-weight: 500;
    }}
    .block-container {{ padding-top: 1rem; padding-bottom: 5rem; }}
    .stTextInput input {{ background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; }}
    </style>
""", unsafe_allow_html=True)

# --- PDF GENERATION CLASS ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'UI Analyzer - Audit Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f'{title}', 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body, comment):
        self.set_font('Arial', '', 11)
        # Use latin-1 compatible characters
        clean_body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, f"- {clean_body}")
        
        if comment:
            self.set_font('Arial', 'I', 10)
            self.set_text_color(100, 100, 100) # Grey for comments
            clean_comment = comment.encode('latin-1', 'replace').decode('latin-1')
            self.multi_cell(0, 5, f"  Note: {clean_comment}")
            self.set_text_color(0, 0, 0) # Reset to black
        
        self.ln(3)

def generate_pdf_bytes(data):
    pdf = PDFReport()
    pdf.add_page()
    
    for category, content in data.items():
        # Filter for accepted issues only
        accepted_issues = [i for i in content['issues'] if i['accepted']]
        
        if accepted_issues:
            pdf.chapter_title(category)
            for issue in accepted_issues:
                pdf.chapter_body(issue['text'], issue['comment'])
            pdf.ln(5)
            
    return pdf.output(dest='S').encode('latin-1')

# --- FUNCTIONS ---
def change_state(new_state):
    st.session_state.app_state = new_state
    st.rerun()

def mark_reviewed(category):
    st.session_state.reviewed_categories.add(category)
    st.rerun()

# --- UI RENDERING ---

# GLOBAL NAVBAR
st.markdown(f"""
    <div class="nav-header">
        <h2 style="margin:0; font-size: 24px;">⚡ UI Analyzer Pro</h2>
        <span style="color: {secondary_text};">Dashboard</span>
    </div>
""", unsafe_allow_html=True)

# 1. UPLOAD SCREEN
if st.session_state.app_state == 'upload':
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center; margin-top: 50px;">
            <div style="font-size: 60px; margin-bottom: 20px;">📁</div>
            <h3>Upload Interface Design</h3>
            <p class="secondary-text">Upload a screenshot of your UI to begin the heuristic audit.</p>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=['png', 'jpg'], label_visibility="collapsed")
        if uploaded_file:
            st.success("✅ Image successfully loaded")
            if st.button("Start AI Analysis", type="primary", use_container_width=True):
                change_state('analyzing')

# 2. ANALYZING SCREEN
elif st.session_state.app_state == 'analyzing':
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center; margin-top: 50px;">
            <div style="font-size: 60px; margin-bottom: 20px;">🧠</div>
            <h3>Analyzing Interface...</h3>
        </div>
        """, unsafe_allow_html=True)
        my_bar = st.progress(0)
        status = st.empty()
        steps = ["Detecting UI Elements...", "Applying Heuristics...", "Checking Accessibility...", "Compiling Report..."]
        for i, step in enumerate(steps):
            status.text(step)
            my_bar.progress((i + 1) * 25)
            time.sleep(0.4)
        change_state('feedback_hub')

# 3. FEEDBACK HUB
elif st.session_state.app_state == 'feedback_hub':
    left_col, main_col, right_col = st.columns([1, 2.5, 1.2])
    
    with left_col:
        st.markdown(f"""
        <div class="custom-card">
            <h4>📊 Overview</h4>
            <p class="secondary-text">Review feedback cards. Accept findings to include them in the PDF report.</p>
        </div>
        """, unsafe_allow_html=True)

    with main_col:
        st.markdown("### 📌 Action Items")
        all_cats = list(st.session_state.analysis_data.keys())
        pending_cats = [c for c in all_cats if c not in st.session_state.reviewed_categories]
        
        if pending_cats:
            for cat in pending_cats:
                with st.expander(f"{cat}", expanded=True):
                    with st.container(height=250):
                        issues = st.session_state.analysis_data[cat]['issues']
                        for i, issue in enumerate(issues):
                            st.markdown(f"**Issue {i+1}:** {issue['text']}")
                            ic1, ic2 = st.columns([0.8, 2])
                            with ic1:
                                issue['accepted'] = st.toggle("✅ Accept", value=issue['accepted'], key=f"tg_{cat}_{i}")
                            with ic2:
                                issue['comment'] = st.text_input("Comment", value=issue['comment'], placeholder="Add context...", key=f"txt_{cat}_{i}", label_visibility="collapsed")
                            st.divider()
                    if st.button(f"Mark {cat} as Reviewed", key=f"done_{cat}", use_container_width=True):
                        mark_reviewed(cat)
        else:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; border-color: #2e7d32;">
                <h3 style="color: #2e7d32 !important;">🎉 All Clear!</h3>
                <p>You have reviewed all feedback categories.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate Final Report", type="primary", use_container_width=True):
                change_state('report')

    with right_col:
        st.markdown(f"""<div class="custom-card"><h4>✅ Reviewed</h4>""", unsafe_allow_html=True)
        reviewed_cats = list(st.session_state.reviewed_categories)
        if reviewed_cats:
            for cat in reviewed_cats:
                st.markdown(f"<div class='reviewed-item'>✔ {cat}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='secondary-text' style='padding:10px;'>No categories reviewed yet.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# 4. FINAL REPORT
elif st.session_state.app_state == 'report':
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        st.balloons()
        st.markdown(f"""
        <div class="custom-card">
            <h2 style="text-align: center; margin-bottom: 20px;">📊 Collaborative Audit Report</h2>
            <hr style="border-top: 1px solid {border_color};">
        """, unsafe_allow_html=True)
        
        # Display On-Screen Report
        for cat, data in st.session_state.analysis_data.items():
            accepted_count = sum(1 for i in data['issues'] if i['accepted'])
            if accepted_count > 0:
                st.markdown(f"#### {cat}")
                for issue in data['issues']:
                    if issue['accepted']:
                        st.markdown(f"""
                        <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <div>✅ <b>Accepted:</b> {issue['text']}</div>
                            <div style="font-size: 0.9em; color: {secondary_text}; margin-left: 25px;">
                                <i>Note: {issue['comment'] if issue['comment'] else 'No comments'}</i>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # PDF Download Section
        st.markdown("### 📥 Download")
        
        # Generate PDF Bytes
        try:
            pdf_data = generate_pdf_bytes(st.session_state.analysis_data)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name="ui_audit_report.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            with col_d2:
                 if st.button("Start New Audit", use_container_width=True):
                    st.session_state.app_state = 'upload'
                    st.session_state.reviewed_categories = set()
                    st.rerun()

        except Exception as e:
            st.error(f"Error generating PDF: {e}")