import pandas as pd
import numpy as np

def run_analytical_pipeline(file_path):
    print("🔄 Ingesting high-dimensional data sheets...")
    teachers = pd.read_excel(file_path, sheet_name="Teachers")
    courses = pd.read_excel(file_path, sheet_name="Courses")
    transactions = pd.read_excel(file_path, sheet_name="Transactions")
    
    tx_with_courses = pd.merge(transactions, courses, on="CourseID", how="left")
    master_df = pd.merge(tx_with_courses, teachers, on="TeacherID", how="left")
    
    enrollments = master_df.groupby("TeacherID").size().reset_index(name="Enrollments")
    teachers_enriched = pd.merge(teachers, enrollments, on="TeacherID", how="left").fillna(0)
    
    print(f"✔ Pipeline complete! Linked transactions: {len(master_df)}")
    return teachers_enriched, courses, master_df

if __name__ == "__main__":
    teachers_df, courses_df, master_df = run_analytical_pipeline("data/dataset.xlsx")
