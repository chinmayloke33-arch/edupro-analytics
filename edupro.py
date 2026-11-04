import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

from process_data import run_analytical_pipeline


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EduPro | Instructor Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATASET LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "EduPro Online Platform.xlsx"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #1E3A5F;
    }

    .sub-title {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background-color: #f1f5f9;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">EduPro Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Instructor Performance and Course Quality Analysis'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    return run_analytical_pipeline(DATASET_PATH)


try:

    with st.spinner("Loading EduPro dataset..."):

        teachers_df, courses_df, master_df = load_data()

except Exception as error:

    st.error("Unable to load the EduPro dataset.")

    st.code(str(error))

    st.info(
        "Check that 'EduPro Online Platform.xlsx' "
        "is uploaded in the main GitHub repository folder "
        "and contains the sheets Teachers, Courses, and Transactions."
    )

    st.stop()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("Dashboard Filters")

st.sidebar.markdown("Filter the analytics below.")

# Expertise filter

expertise_options = sorted(
    teachers_df["Expertise"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_expertise = st.sidebar.multiselect(
    "Select Teacher Expertise",
    options=expertise_options,
    default=expertise_options
)


# Course level filter

course_level_options = sorted(
    courses_df["CourseLevel"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_course_levels = st.sidebar.multiselect(
    "Select Course Level",
    options=course_level_options,
    default=course_level_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_teachers = teachers_df[
    teachers_df["Expertise"]
    .astype(str)
    .isin(selected_expertise)
].copy()

filtered_courses = courses_df[
    courses_df["CourseLevel"]
    .astype(str)
    .isin(selected_course_levels)
].copy()

filtered_master = master_df[
    master_df["Expertise"]
    .astype(str)
    .isin(selected_expertise)
    &
    master_df["CourseLevel"]
    .astype(str)
    .isin(selected_course_levels)
].copy()


# ============================================================
# KPI METRICS
# ============================================================

st.subheader("Platform Overview")

col1, col2, col3, col4 = st.columns(4)

average_teacher_rating = (
    filtered_teachers["TeacherRating"].mean()
)

average_course_rating = (
    filtered_courses["CourseRating"].mean()
)

unique_users = filtered_master["UserID"].nunique()

total_enrollments = len(filtered_master)


col1.metric(
    "Average Teacher Rating",
    f"{average_teacher_rating:.2f}"
    if pd.notna(average_teacher_rating)
    else "N/A"
)

col2.metric(
    "Average Course Rating",
    f"{average_course_rating:.2f}"
    if pd.notna(average_course_rating)
    else "N/A"
)

col3.metric(
    "Unique Users",
    f"{unique_users:,}"
)

col4.metric(
    "Total Enrollments",
    f"{total_enrollments:,}"
)


st.divider()


# ============================================================
# TEACHER PERFORMANCE
# ============================================================

st.subheader("Instructor Performance Analysis")

col1, col2 = st.columns(2)


# Teacher leaderboard

with col1:

    st.markdown("#### Top Instructors")

    leaderboard = (
        filtered_teachers
        .sort_values(
            by="TeacherRating",
            ascending=False
        )
        .head(10)
    )

    if not leaderboard.empty:

        fig = px.bar(
            leaderboard,
            x="TeacherRating",
            y="TeacherName",
            orientation="h",
            color="TeacherRating",
            title="Top 10 Teachers by Rating",
            labels={
                "TeacherRating": "Teacher Rating",
                "TeacherName": "Teacher"
            }
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No teacher data available for these filters.")


# Teacher experience

with col2:

    st.markdown("#### Teaching Experience Distribution")

    experience_data = filtered_teachers.dropna(
        subset=["YearsOfExperience"]
    )

    if not experience_data.empty:

        fig = px.histogram(
            experience_data,
            x="YearsOfExperience",
            nbins=10,
            title="Teacher Experience Distribution",
            labels={
                "YearsOfExperience": "Years of Experience"
            }
        )

        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No experience data available.")


st.divider()


# ============================================================
# COURSE QUALITY ANALYSIS
# ============================================================

st.subheader("Course Quality Analysis")

col1, col2 = st.columns(2)


# Course rating distribution

with col1:

    st.markdown("#### Course Rating Distribution")

    rating_data = filtered_courses.dropna(
        subset=["CourseRating"]
    )

    if not rating_data.empty:

        fig = px.histogram(
            rating_data,
            x="CourseRating",
            nbins=10,
            title="Distribution of Course Ratings",
            labels={
                "CourseRating": "Course Rating"
            }
        )

        fig.update_layout(height=420)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No course rating data available.")


# Average rating by course level

with col2:

    st.markdown("#### Average Rating by Course Level")

    level_rating = (
        filtered_courses
        .groupby("CourseLevel", as_index=False)
        ["CourseRating"]
        .mean()
    )

    if not level_rating.empty:

        fig = px.bar(
            level_rating,
            x="CourseLevel",
            y="CourseRating",
            color="CourseRating",
            title="Course Level vs Average Rating",
            labels={
                "CourseLevel": "Course Level",
                "CourseRating": "Average Rating"
            }
        )

        fig.update_layout(height=420)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No course-level data available.")


st.divider()


# ============================================================
# ENROLLMENT ANALYSIS
# ============================================================

st.subheader("Instructor Enrollment Analysis")

enrollment_data = (
    filtered_teachers
    .sort_values(
        by="Enrollments",
        ascending=False
    )
    .head(15)
)

if not enrollment_data.empty:

    fig = px.bar(
        enrollment_data,
        x="TeacherName",
        y="Enrollments",
        color="Enrollments",
        title="Top 15 Instructors by Enrollments",
        labels={
            "TeacherName": "Instructor",
            "Enrollments": "Total Enrollments"
        }
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("No enrollment data available.")


st.divider()


# ============================================================
# INTEGRATED DATA TABLE
# ============================================================

st.subheader("Integrated Analytics Dataset")

st.write(
    "The following table displays the integrated "
    "teacher, course, and transaction records."
)

st.dataframe(
    filtered_master,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD REPORTS
# ============================================================

st.divider()

st.subheader("Download Analytical Reports")

col1, col2, col3 = st.columns(3)


with col1:

    teachers_csv = filtered_teachers.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Teacher Report",
        data=teachers_csv,
        file_name="teachers_enriched.csv",
        mime="text/csv"
    )


with col2:

    courses_csv = filtered_courses.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Course Report",
        data=courses_csv,
        file_name="courses_report.csv",
        mime="text/csv"
    )


with col3:

    master_csv = filtered_master.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Integrated Report",
        data=master_csv,
        file_name="master_analytics.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:gray;">
        EduPro Analytics Dashboard |
        Instructor Performance & Course Quality
    </div>
    """,
    unsafe_allow_html=True
)
