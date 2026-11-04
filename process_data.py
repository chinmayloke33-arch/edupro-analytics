import pandas as pd
import numpy as np

# ============================================================

# DATA ANALYTICAL PIPELINE

# ============================================================

def run_analytical_pipeline(file_path):

```
print("Starting EduPro Analytical Pipeline...")

# --------------------------------------------------------
# 1. DATA INGESTION
# --------------------------------------------------------

print("Loading Excel datasets...")

teachers = pd.read_excel(
    file_path,
    sheet_name="Teachers"
)

courses = pd.read_excel(
    file_path,
    sheet_name="Courses"
)

transactions = pd.read_excel(
    file_path,
    sheet_name="Transactions"
)

# --------------------------------------------------------
# 2. DATA VALIDATION
# --------------------------------------------------------

required_columns = {

    "Teachers": [
        "TeacherID",
        "TeacherName",
        "Expertise",
        "TeacherRating",
        "YearsOfExperience"
    ],

    "Courses": [
        "CourseID",
        "CourseLevel",
        "CourseRating"
    ],

    "Transactions": [
        "CourseID",
        "TeacherID",
        "UserID"
    ]
}

datasets = {
    "Teachers": teachers,
    "Courses": courses,
    "Transactions": transactions
}

for sheet, columns in required_columns.items():

    missing = set(columns) - set(datasets[sheet].columns)

    if missing:
        raise ValueError(
            f"Missing columns in {sheet}: {missing}"
        )

# --------------------------------------------------------
# 3. DATA INTEGRATION
# --------------------------------------------------------

print("Integrating datasets...")

tx_with_courses = pd.merge(
    transactions,
    courses,
    on="CourseID",
    how="left"
)

master_df = pd.merge(
    tx_with_courses,
    teachers,
    on="TeacherID",
    how="left"
)

# --------------------------------------------------------
# 4. INSTRUCTOR ENROLLMENT ANALYSIS
# --------------------------------------------------------

enrollments = (
    master_df.groupby("TeacherID")
    .size()
    .reset_index(name="Enrollments")
)

teachers_enriched = pd.merge(
    teachers,
    enrollments,
    on="TeacherID",
    how="left"
)

teachers_enriched["Enrollments"] = (
    teachers_enriched["Enrollments"]
    .fillna(0)
    .astype(int)
)

# --------------------------------------------------------
# 5. DATA QUALITY CHECKS
# --------------------------------------------------------

print("Checking data quality...")

print("Teacher records:", len(teachers))
print("Course records:", len(courses))
print("Transaction records:", len(transactions))

unmatched_courses = master_df["CourseRating"].isna().sum()

unmatched_teachers = master_df["TeacherName"].isna().sum()

print("Unmatched course records:", unmatched_courses)
print("Unmatched teacher records:", unmatched_teachers)

# --------------------------------------------------------
# 6. FINAL OUTPUT
# --------------------------------------------------------

print("-----------------------------------")
print("EDUPRO ANALYTICAL PIPELINE COMPLETE")
print("-----------------------------------")

print("Integrated records:", len(master_df))

return teachers_enriched, courses, master_df
```

# ============================================================

# MAIN EXECUTION

# ============================================================

if **name** == "**main**":

```
FILE_PATH = "data/dataset.xlsx"

teachers_df, courses_df, master_df = (
    run_analytical_pipeline(FILE_PATH)
)

print("\nInstructor Performance Preview:")

print(
    teachers_df[
        [
            "TeacherName",
            "Expertise",
            "TeacherRating",
            "Enrollments"
        ]
    ].head()
)

# --------------------------------------------------------
# EXPORT PROCESSED DATASETS
# --------------------------------------------------------

teachers_df.to_csv(
    "teachers_enriched.csv",
    index=False
)

master_df.to_csv(
    "master_analytics.csv",
    index=False
)

print("\nProcessed datasets exported successfully.")

