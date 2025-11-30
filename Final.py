import streamlit as st
import pandas as pd
import time
import base64
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURATION ---
st.set_page_config(
    page_title="UI Analyzer Prototype",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    .custom-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        margin-bottom: 15px;
    }
    .secondary-text {
        color: #666;
        font-size: 0.9rem;
    }
    .reviewed-item {
        color: #2e7d32;
        font-size: 1rem;
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
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

# --- PDF GENERATION FUNCTIONS ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'UI Analysis Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def add_section(self, title, issues):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(5)
        
        self.set_font('Arial', '', 10)
        for i, issue in enumerate(issues, 1):
            status = "ACCEPTED" if issue['accepted'] else "REJECTED"
            self.set_font('Arial', 'B', 10)
            self.cell(0, 8, f'Issue {i}: [{status}]', 0, 1)
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 6, issue['text'])
            
            if issue['comment']:
                self.set_font('Arial', 'I', 9)
                self.set_text_color(100, 100, 100)
                self.multi_cell(0, 6, f"Note: {issue['comment']}")
                self.set_text_color(0, 0, 0)
            
            self.ln(3)

def generate_pdf_bytes(analysis_data):
    pdf = PDFReport()
    pdf.add_page()
    
    # Summary statistics
    total_issues = 0
    accepted_issues = 0
    
    for category_data in analysis_data.values():
        total_issues += len(category_data['issues'])
        accepted_issues += sum(1 for issue in category_data['issues'] if issue['accepted'])
    
    # Add summary section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Executive Summary', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f'Total Issues Identified: {total_issues}', 0, 1)
    pdf.cell(0, 6, f'Issues Accepted: {accepted_issues}', 0, 1)
    pdf.cell(0, 6, f'Acceptance Rate: {(accepted_issues/total_issues*100):.1f}%', 0, 1)
    pdf.ln(10)
    
    # Add each category
    for category, data in analysis_data.items():
        accepted_count = sum(1 for issue in data['issues'] if issue['accepted'])
        if accepted_count > 0:  # Only add categories with accepted issues
            pdf.add_section(category, [issue for issue in data['issues'] if issue['accepted']])
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin1')

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

# Colors for styling
bg_color = "#f8f9fa"
border_color = "#dee2e6"
secondary_text = "#6c757d"

# --- UI SCREENS ---

# 1. UPLOAD SCREEN
# if st.session_state.app_state == 'upload':
#     st.markdown("<div class='app-header'><h1>🤖 UI Analyzer</h1></div>", unsafe_allow_html=True)
#     st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=120)
#     st.markdown("<h3 style='text-align: center;'>Upload Interface</h3>", unsafe_allow_html=True)
    
#     uploaded_file = st.file_uploader("", type=['png', 'jpg'], label_visibility="collapsed")
    
#     if uploaded_file:
#         st.success("Image Uploaded!")
#         if st.button("Analyze UI", type="primary"):
#             change_state('analyzing')

# 1. UPLOAD SCREEN
# 1. UPLOAD SCREEN
if st.session_state.app_state == 'upload':
    # Center everything using a single centered column
    centered_col1, centered_col2, centered_col3 = st.columns([1, 3, 1])
    
    with centered_col2:
        st.markdown("<div style='text-align: center;'><h1>🤖 UI Analyzer</h1></div>", unsafe_allow_html=True)
        
        # Center the image
        img_col1, img_col2, img_col3 = st.columns([1, 1, 1])
        with img_col2:
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=120)
        
        st.markdown("<h3 style='text-align: center;'>Upload Interface</h3>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=['png', 'jpg'], label_visibility="collapsed")
        
        if uploaded_file:
            st.success("Image Uploaded!")
            
            # Center the button
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
            with btn_col2:
                st.markdown("""
                            <style>
                            div.stButton > button:first-child {
                                background: linear-gradient(135deg, #28a745, #20c997);
                                color: white;
                                border: none;
                                border-radius: 8px;
                                padding: 12px 24px;
                                font-weight: 600;
                                transition: all 0.3s ease;
                            }

                            div.stButton > button:first-child:hover {
                                background: linear-gradient(135deg, #218838, #1ea085);
                                transform: translateY(-2px);
                                box-shadow: 0 6px 15px rgba(32, 201, 151, 0.3);
                            }
                            </style>
                            """, unsafe_allow_html=True)
                if st.button("Analyze UI", type="primary", use_container_width=True):
                    change_state('analyzing')

# 2. ANALYZING SCREEN
# elif st.session_state.app_state == 'analyzing':
#     st.markdown("<div class='app-header'><h1>Analyzing...</h1></div>", unsafe_allow_html=True)
#     st.image("https://cdn-icons-png.flaticon.com/512/2040/2040946.png", width=120)
    
#     my_bar = st.progress(0)
#     status = st.empty()
#     steps = ["Scanning Layout...", "Checking Contrast...", "Verifying Consistency...", "Generating Feedback..."]
    
#     for i, step in enumerate(steps):
#         status.text(step)
#         my_bar.progress((i + 1) * 25)
#         time.sleep(0.5)
    
#     change_state('feedback_hub')

# 2. ANALYZING SCREEN
elif st.session_state.app_state == 'analyzing':
    st.markdown("""
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    @keyframes dotPulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.2); }
    }
    .dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #28a745;
        margin: 0 5px;
        animation: dotPulse 1.5s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='app-header'><h1>Analyzing Your Design</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <img src="https://cdn-icons-png.flaticon.com/512/2040/2040946.png" width="150" 
                 style="animation: bounce 2s infinite ease-in-out;">
            <div style="margin-top: 20px;">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    my_bar = st.progress(0)
    status = st.empty()
    steps = ["Scanning Layout...", "Checking Contrast...", "Verifying Consistency...", "Generating Feedback..."]
    
    for i, step in enumerate(steps):
        status.text(step)
        my_bar.progress((i + 1) * 25)
        time.sleep(1.2)
    
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
                    file_name="UI_Audit_Report.pdf",
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