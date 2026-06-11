from flask import Flask, render_template, request
from sqlalchemy import values
from machine_learning.recommendation import generate_roadmap
from flask import redirect 
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sah123",
    database="learning_recommendation_db"
)

cursor = db.cursor()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    roadmap = None
    career_goal = ""
    known_skills = []

    if request.method == "POST":

        career_goal = request.form["career_goal"]

        known_skills = request.form.getlist("skills")

        roadmap = generate_roadmap(
            career_goal,
            known_skills
        )
        for _, row in roadmap.iterrows():

            cursor.execute("""
                INSERT INTO course_progress
                (course_name)
                VALUES (%s)
            """,
            (row["course_name"],)
        )
        db.commit()
        skills_text = ", ".join(known_skills)

        query = """
            INSERT INTO roadmap_history
            (career_goal, skills)
            VALUES (%s, %s)
        """

        values = (
            career_goal,
            skills_text
        )

        cursor.execute(query, values)
        db.commit()

    return render_template(
        "index.html",
        roadmap=roadmap,
        career_goal=career_goal,
        selected_skills=known_skills
    )

@app.route("/history")
def history():

    cursor.execute("""
        SELECT *
        FROM roadmap_history
        ORDER BY generated_at DESC
    """)

    rows = cursor.fetchall()

    return render_template(
        "history.html",
        rows=rows
    )
@app.route("/progress")
def progress():

    cursor.execute("""
        SELECT *
        FROM course_progress
    """)

    courses = cursor.fetchall()

    total_courses = len(courses)

    completed_courses = sum(
        1 for course in courses if course[2]
    )

    progress_percent = 0

    if total_courses > 0:
        progress_percent = round(
            (completed_courses / total_courses) * 100,
            2
        )

    return render_template(
        "progress.html",
        courses=courses,
        completed_courses=completed_courses,
        total_courses=total_courses,
        progress_percent=progress_percent
    )
@app.route("/complete/<int:id>")
def complete(id):

    cursor.execute(
        """
        UPDATE course_progress
        SET completed = TRUE
        WHERE id = %s
        """,
        (id,)
    )

    db.commit()

    return redirect("/progress")
if __name__ == "__main__":
    app.run(debug=True)