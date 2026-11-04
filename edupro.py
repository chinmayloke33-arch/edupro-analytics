import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="EduPro Quality Engine", layout="wide", page_icon="🎓")
st.title("🎓 EduPro Instructor Performance & Course Quality Dashboard")
st.markdown("---")

@st.cache_data
def load_data():
    file_path = "data/dataset.xlsx"
    teachers = pd.read_excel(file_path, sheet_name="Teachers")
    courses = pd.read_excel(file_path, sheet_name="Courses")
    transactions = pd.read_excel(file_path, sheet_name="Transactions")
    master = pd.merge(transactions, courses, on="CourseID", how="left")
    master = pd.merge(master, teachers, on="TeacherID", how="left")
    counts = master.groupby("TeacherID").size().reset_index(name="Enrollments")
    teachers = pd.merge(teachers, counts, on="TeacherID", how="left").fillna(0)
    return teachers, courses, master

try:
    teachers_df, courses_df, master_df = load_data()
    st.sidebar.header("🎛️ Dashboard Controls")
    selected_expertise = st.sidebar.selectbox("Instructor Expertise", ["All"] + list(teachers_df["Expertise"].unique()))
    selected_level = st.sidebar.selectbox("Course Level Tier", ["All"] + list(courses_df["CourseLevel"].unique()))
    
    f_teachers = teachers_df.copy()
    if selected_expertise != "All":
        f_teachers = f_teachers[f_teachers["Expertise"] == selected_expertise]
        
    f_master = master_df.copy()
    if selected_level != "All":
        f_master = f_master[f_master["CourseLevel"] == selected_level]

    col1, col2, col3 = st.columns(3)
    col1.metric("📌 Average Teacher Rating", f"{f_teachers['TeacherRating'].mean():.2f} / 5.0")
    col2.metric("📚 Average Course Rating", f"{f_master['CourseRating'].mean():.2f} / 5.0")
    col3.metric("🎯 Total Active Users", f"{len(f_master['UserID'].unique())}")
    
    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("### 🏆 Performance Leaderboard")
        st.dataframe(f_teachers.sort_values(by="TeacherRating", ascending=False)[["TeacherName", "Expertise", "TeacherRating", "Enrollments"]], use_container_width=True)
    with chart_col2:
        st.markdown("### 📊 Teaching Experience Distribution")
        fig = px.histogram(f_teachers, x="YearsOfExperience", color="Expertise", barmode="overlay")
        st.plotly_chart(fig, use_container_width=True)
        
except Exception as e:
    st.error(f"Waiting for local workbook profile. Place your Excel sheet named 'dataset.xlsx' into the 'data/' folder structure.")
