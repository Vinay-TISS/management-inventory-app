# management_style_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import os
import unicodedata

# --- CONFIG ---
st.set_page_config(page_title="Management Style Finder", layout="centered")

# --- BACKGROUND IMAGE ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("Leadership.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- LOAD QUESTIONS ---
@st.cache_data
def load_questions():
    xls = pd.ExcelFile("Book2.xlsx")
    all_parts = []
    for i in range(1, 7):
        sheet = f"PART {i}" if f"PART {i}" in xls.sheet_names else f"PART{i}"
        df = pd.read_excel(xls, sheet_name=sheet)
        df = df.dropna(subset=[df.columns[0], df.columns[1]])
        df.columns = ['Q_No', 'Question'] + list(df.columns[2:])
        df['Part'] = f"PART {i}"
        all_parts.append(df[['Q_No', 'Question', 'Part']])
    return pd.concat(all_parts, ignore_index=True)

# --- STYLES TEXT ---
def get_style_description():
    return {
        "Top Dog": '''This manager prefers to be in control. Communication tends to be one-way. They say what to do and expect team members to do it. It's an autocratic approach to management.

When there's a crisis, or when things need to get done quickly, a take-charge approach to management can be very efficient. Sometimes we need a strong general to get us through the battle, or a decisive coach to dictate the next play. But this can come at the cost of team morale or employee welfare. Often these managers speak in an urgent tone that doesn't feel good to hear. They give feedback without considering the impact of their words. And they may miss others’ good ideas by failing to listen.

Top Dog management is best for urgent, high-stakes situations where a quick result is the biggest priority, provided the manager actually knows what's best and can keep their severity in check.''',

        "Collaborator": '''This manager enjoys give-and-take with team members. Communication is two-way, and all ideas are welcome. This yields more perspectives, information, and choices. Decisions are made collectively, which empowers everyone. People like to have a say, and when they do, they have more ownership in the outcome.

Giving employees a voice will make them happy, but consensus takes time. When things need to be dealt with fast, this approach won’t work. And not all work is suited for groups. Collaborator management is best for brainstorming and making plans for work that’s not time-sensitive or urgent, with employees who have lots of experience.''',

        "Chillaxer": '''Sometimes referred to as a "laissez-faire leader," this manager prefers to hang back ("chill") and let the team do its thing. That doesn’t mean they don’t care. They just don’t want to get in the way. They see their team as smart and capable and want to empower them to take risks and be creative. They are willing to let employees make mistakes.

This style doesn’t work well with unmotivated employees or those lacking proper training, ability, or confidence. Chillaxer management is best for proven, skilled employees who have earned their independence with proven results.''',

        "Visionary": '''Visionary managers are all about the big picture. Everything they do is about the organization’s mission. They inspire their teams by speaking in broader terms, giving purpose to their work.

Visionaries also focus a lot on employee growth and learning. Visionaries have a wonderful larger perspective but often miss the important details of day-to-day work. Visionary management is best when team members need inspiration, purpose, and personal growth.'''
    }

# --- TOP LEFT LOGO ---
st.markdown("""
<div style='position: absolute; top: 10px; left: 10px;'>
    <img src='https://raw.githubusercontent.com/your-repo-path/logo.png' width='60'>
</div>
""", unsafe_allow_html=True)

# --- APP INTRO + USER DETAILS ---
st.image("logo.png", width=150)
st.markdown("<h1 style='text-align: center;'>🎯 Management Style Inventory</h1>", unsafe_allow_html=True)
st.markdown("""
Welcome! This tool helps you discover your natural management style based on your preferences.
After answering a set of questions, you'll receive a detailed report and chart summarizing your management traits.
""")

st.markdown("### 👤 Participant Information")
name = st.text_input("Your Name")
tiss_id = st.text_input("TISS ID")
password = st.text_input("Enter Access Password", type="password")
if password != "Tiss@2025":
    st.warning("Please enter the correct password to continue.")
    st.stop()

# --- ASSESSMENT ---
questions_df = load_questions()
style_descriptions = get_style_description()
st.markdown("---")
st.header("📋 Rate Each Statement (1 = Strongly Disagree, 5 = Strongly Agree)")
responses = []

for index, row in questions_df.iterrows():
    score = st.slider(f"{int(row['Q_No'])}. {row['Question']}", 1, 5, 3)
    responses.append((row['Part'], score))

# --- SUBMIT BUTTON ---
if st.button("✅ Submit Responses"):
    from collections import defaultdict

    # Define question index to style mapping
    position_style_map = {
        0: "Top Dog",
        1: "Collaborator",
        2: "Chillaxer",
        3: "Visionary"
    }

    style_totals = {
        "Top Dog": 0,
        "Collaborator": 0,
        "Chillaxer": 0,
        "Visionary": 0
    }

    part_question_counter = defaultdict(int)

    for index, row in questions_df.iterrows():
        part = row["Part"]
        question_index = part_question_counter[part]
        style = position_style_map.get(question_index % 4)
        part_question_counter[part] += 1

        style_totals[style] += responses[index][1]

    # Get final style
    final_style = max(style_totals.items(), key=lambda x: x[1])[0]
    final_score = style_totals[final_style]

    # Show result
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center; color:green;'>🌟 Your Management Style: {final_style}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background-color:#f0f9ff; padding:20px; border-radius:10px; border-left: 6px solid #4CAF50;'>
    {style_descriptions[final_style]}
    </div>
    """, unsafe_allow_html=True)

    # 📊 Show score table
    score_df = pd.DataFrame(list(style_totals.items()), columns=["Management Style", "Score"])
    st.markdown("### 📊 Style-wise Score Table")
    st.table(score_df)

    # 🕸️ Radar Chart
    fig = px.line_polar(score_df, r="Score", theta="Management Style", line_close=True,
                        title="Your Style Chart", markers=True)
    fig.update_traces(fill='toself', line_color='blue')
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 60])), paper_bgcolor="#f7f7f7")
    st.plotly_chart(fig)
    fig.write_image("radar_chart.png")

    def clean_pdf_text(text):
        replacements = {
            "—": "-", "–": "-", "“": "\"", "”": "\"",
            "‘": "'", "’": "'", "\u00A0": " "
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.add_page()
    pdf.image("logo.png", x=10, y=8, w=40)
    pdf.set_font("Arial", 'B', 16)
    pdf.ln(25)
    pdf.cell(0, 10, "Management Style Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"TISS ID: {tiss_id}", ln=True)
    pdf.cell(0, 10, f"Style: {final_style} ({final_score})", ln=True)
    pdf.ln(8)
    pdf.multi_cell(0, 8, clean_pdf_text(style_descriptions[final_style]))
    if os.path.exists("radar_chart.png"):
        pdf.image("radar_chart.png", w=150)
    pdf.output("management_style_report.pdf")

    with open("management_style_report.pdf", "rb") as f:
        st.download_button("📥 Download Full Report", data=f, file_name="management_style_report.pdf", mime="application/pdf")
