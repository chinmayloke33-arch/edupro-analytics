import pandas as pd
from pathlib import Path


# ============================================================
# DATASET LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "EduPro Online Platform.xlsx"


# ============================================================
# ANALYTICAL PIPELINE
# ============================================================

def run_analytical_pipeline(file_path=DATASET_PATH):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    print("Starting EduPro Analytical Pipeline...")

    # --------------------------------------------------------
    # 1. LOAD EXCEL SHEETS
    # --------------------------------------------------------

    try:
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

    except ValueError as error:
        raise ValueError(
            "The Excel file must contain three sheets: "
            "Teachers, Courses, and Transactions. "
            f"Details: {error}"
        )

    # --------------------------------------------------------
    # 2. VALIDATE REQUIRED COLUMNS
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

    for sheet_name, required in required_columns.items():

        missing = [
            column
            for column in required
            if column not in datasets[sheet_name].columns
        ]

        if missing:
            raise ValueError(
                f"Missing columns in {sheet_name}: {missing}"
            )

    # --------------------------------------------------------
    # 3. MERGE DATASETS
    # --------------------------------------------------------

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
    # 4. CALCULATE TEACHER ENROLLMENTS
    # --------------------------------------------------------

    enrollments = (
        master_df
        .groupby("TeacherID")
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
    # 5. DATA CLEANING
    # --------------------------------------------------------

    teachers_enriched["TeacherRating"] = pd.to_numeric(
        teachers_enriched["TeacherRating"],
        errors="coerce"
    )

    teachers_enriched["YearsOfExperience"] = pd.to_numeric(
        teachers_enriched["YearsOfExperience"],
        errors="coerce"
    )

    courses["CourseRating"] = pd.to_numeric(
        courses["CourseRating"],
        errors="coerce"
    )

    master_df["TeacherRating"] = pd.to_numeric(
        master_df["TeacherRating"],
        errors="coerce"
    )

    master_df["CourseRating"] = pd.to_numeric(
        master_df["CourseRating"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 6. PIPELINE SUMMARY
    # --------------------------------------------------------

    print("Teachers:", len(teachers))
    print("Courses:", len(courses))
    print("Transactions:", len(transactions))
    print("Integrated records:", len(master_df))

    print("EduPro Pipeline Completed Successfully!")

    return teachers_enriched, courses, master_df


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    teachers_df, courses_df, master_df = (
        run_analytical_pipeline()
    )

    teachers_df.to_csv(
        BASE_DIR / "teachers_enriched.csv",
        index=False
    )

    master_df.to_csv(
        BASE_DIR / "master_analytics.csv",
        index=False
    )

    print("CSV reports exported successfully.")
