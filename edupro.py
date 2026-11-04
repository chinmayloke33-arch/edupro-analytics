import streamlit as st
import pandas as pd
import plotly.express as px

from analytical_pipeline import run_analytical_pipeline

# ============================================================

# PAGE CONFIGURATION

# ============================================================

st.set_page_config(
page_title="EduPro Quality Engine",
page_icon="🎓",
layout="wide"
)

# ============================================================

# DASHBOARD HEADER

# ============================================================

st.title("🎓 EduPro Quality Engine")

st.subheader(
"Instructor Performance & Course Quality Analytics"
)

st.markdown(
"An integrated analytical platform for monitoring "
"instructor performance, course quality and student enrollment."
)

st.markdown("---")

# ============================================================

# DATA LOADING

# ============================================================

@st.cache_data
def load_data():


return run_analytical_pipeline(
    "data/dataset.xlsx"
)


try:


teachers_df, courses_df, master_df = load_data()

# ========================================================
# SIDEBAR FILTERS
# ========================================================

st.sidebar.title("🎛️ Dashboard Controls")

expertise_options = ["All"] + sorted(
    teachers_df["Expertise"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

level_options = ["All"] + sorted(
    courses_df["CourseLevel"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_expertise = st.sidebar.selectbox(
    "Instructor Expertise",
    expertise_options
)

selected_level = st.sidebar.selectbox(
    "Course Level",
    level_options
)

# ========================================================
# FILTERING
# ========================================================

f_teachers = teachers_df.copy()

f_master = master_df.copy()

if selected_expertise != "All":

    f_teachers = f_teachers[
        f_teachers["Expertise"] == selected_expertise
    ]

    f_master = f_master[
        f_master["Expertise"] == selected_expertise
    ]

if selected_level != "All":

    f_master = f_master[
        f_master["CourseLevel"] == selected_level
    ]

# ========================================================
# KPI SECTION
# ========================================================

st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

average_teacher_rating = (
    f_teachers["TeacherRating"].mean()
    if not f_teachers.empty else 0
)

average_course_rating = (
    f_master["CourseRating"].mean()
    if not f_master.empty else 0
)

total_users = f_master["UserID"].nunique()

total_enrollments = len(f_master)

col1.metric(
    "⭐ Average Teacher Rating",
    f"{average_teacher_rating:.2f}/5"
)

col2.metric(
    "📚 Average Course Rating",
    f"{average_course_rating:.2f}/5"
)

col3.metric(
    "👥 Active Students",
    f"{total_users:,}"
)

col4.metric(
    "🎯 Total Enrollments",
    f"{total_enrollments:,}"
)

st.markdown("---")

# ========================================================
# INSTRUCTOR PERFORMANCE
# ========================================================

st.markdown("## 🏆 Instructor Performance Analysis")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    st.markdown("### Instructor Leaderboard")

    leaderboard = f_teachers.sort_values(
        by="TeacherRating",
        ascending=False
    )

    st.dataframe(
        leaderboard[
            [
                "TeacherName",
                "Expertise",
                "TeacherRating",
                "YearsOfExperience",
                "Enrollments"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

with chart_col2:

    st.markdown("### Teaching Experience Distribution")

    if not f_teachers.empty:

        fig = px.histogram(
            f_teachers,
            x="YearsOfExperience",
            color="Expertise",
            barmode="overlay",
            title="Instructor Experience Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No instructor data available.")

st.markdown("---")

# ========================================================
# COURSE QUALITY ANALYSIS
# ========================================================

st.markdown("## 📚 Course Quality Analysis")

course_col1, course_col2 = st.columns(2)

with course_col1:

    st.markdown("### Course Rating Distribution")

    if not f_master.empty:

        fig = px.histogram(
            f_master,
            x="CourseRating",
            color="CourseLevel",
            title="Distribution of Course Ratings"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No course data available.")

with course_col2:

    st.markdown("### Average Rating by Course Level")

    if not f_master.empty:

        level_rating = (
            f_master.groupby("CourseLevel")["CourseRating"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            level_rating,
            x="CourseLevel",
            y="CourseRating",
            text_auto=".2f",
            title="Average Course Rating"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No course data available.")

st.markdown("---")

# ========================================================
# ENROLLMENT ANALYTICS
# ========================================================

st.markdown("## 👥 Student Enrollment Analytics")

if not f_master.empty:

    enrollment_data = (
        f_master.groupby("TeacherName")
        .size()
        .reset_index(name="Enrollments")
        .sort_values(
            by="Enrollments",
            ascending=False
        )
    )

    fig = px.bar(
        enrollment_data,
        x="TeacherName",
        y="Enrollments",
        color="Enrollments",
        title="Instructor-wise Student Enrollments",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("No enrollment data available.")

# ========================================================
# DATA TABLE
# ========================================================

with st.expander("🔍 View Integrated Analytical Dataset"):

    st.dataframe(
        f_master,
        use_container_width=True,
        hide_index=True
    )

# ========================================================
# DOWNLOAD REPORTS
# ========================================================

st.markdown("---")

st.markdown("## 📥 Download Analytical Reports")

download_col1, download_col2 = st.columns(2)

with download_col1:

    st.download_button(
        "Download Instructor Report",
        data=f_teachers.to_csv(index=False).encode("utf-8"),
        file_name="instructor_report.csv",
        mime="text/csv"
    )

with download_col2:

    st.download_button(
        "Download Integrated Dataset",
        data=f_master.to_csv(index=False).encode("utf-8"),
        file_name="master_analytics.csv",
        mime="text/csv"
    )


except FileNotFoundError:


st.error(
    "Dataset not found. Please place dataset.xlsx "
    "inside the data folder."
)


except Exception as e:


st.error(f"Dashboard Error: {e}")


# ============================================================

# FOOTER

# ============================================================

st.markdown("---")

st.caption(
"EduPro Quality Engine | Instructor Performance "
"& Course Quality Analytics"
)
