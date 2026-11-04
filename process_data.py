import pandas as pd


def run_analytical_pipeline(file_path):

    print("Starting EduPro Analytical Pipeline...")

    # 1. Load Excel sheets
    teachers = pd.read_excel(file_path, sheet_name="Teachers")
    courses = pd.read_excel(file_path, sheet_name="Courses")
    transactions = pd.read_excel(file_path, sheet_name="Transactions")

    # 2. Validate columns
    required = {
        "Teachers": [
            "TeacherID", "TeacherName", "Expertise",
            "TeacherRating", "YearsOfExperience"
        ],
        "Courses": [
            "CourseID", "CourseLevel", "CourseRating"
        ],
        "Transactions": [
            "CourseID", "TeacherID", "UserID"
        ]
    }

    datasets = {
        "Teachers": teachers,
        "Courses": courses,
        "Transactions": transactions
    }

    for sheet, columns in required.items():
        missing = set(columns) - set(datasets[sheet].columns)

        if missing:
            raise ValueError(
                f"Missing columns in {sheet}: {missing}"
            )

    # 3. Merge datasets
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

    # 4. Calculate enrollments
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

    # 5. Data quality summary
    print("Teachers:", len(teachers))
    print("Courses:", len(courses))
    print("Transactions:", len(transactions))
    print("Integrated records:", len(master_df))

    print("EduPro Pipeline Completed Successfully!")

    return teachers_enriched, courses, master_df


# Main execution
if __name__ == "__main__":

    file_path = "data/dataset.xlsx"

    teachers_df, courses_df, master_df = (
        run_analytical_pipeline(file_path)
    )

    teachers_df.to_csv(
        "teachers_enriched.csv",
        index=False
    )

    master_df.to_csv(
        "master_analytics.csv",
        index=False
    )

    print("CSV reports exported successfully.")
