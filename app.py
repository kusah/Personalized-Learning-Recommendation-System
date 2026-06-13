from flask import Flask, render_template, request
from sqlalchemy import values
from machine_learning.recommendation import generate_roadmap
from flask import redirect 
import mysql.connector
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sah123",
    database="learning_recommendation_db"
)

cursor = db.cursor()

app = Flask(__name__)
app.secret_key = "learning_recommendation_secret"

@app.route("/", methods=["GET", "POST"])
def home():
    if "student_id" not in session:
        return redirect("/login")
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
                (student_id, course_name)
                VALUES (%s, %s)
            """,
        (
            session["student_id"],
            row["course_name"]
        )
)
        db.commit()
        skills_text = ", ".join(known_skills)

        query = """
            INSERT INTO roadmap_history
            (student_id, career_goal, skills)
            VALUES (%s, %s, %s)
        """

        values = (
            session["student_id"],
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
    if "student_id" not in session:
        return redirect("/login")
    cursor.execute("""
    SELECT *
    FROM roadmap_history
    WHERE student_id = %s
    ORDER BY generated_at DESC
""",
(session["student_id"],))

    rows = cursor.fetchall()

    return render_template(
        "history.html",
        rows=rows
    )
@app.route("/progress")

def progress():
    if "student_id" not in session:
        return redirect("/login")
    cursor.execute("""
        SELECT *
        FROM course_progress
        WHERE student_id = %s
    """, (session["student_id"],))

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
@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect("/login")
    cursor.execute(
    """
    SELECT COUNT(*)
    FROM roadmap_history
    WHERE student_id = %s
    """,
    (session["student_id"],)
)
    total_roadmaps = cursor.fetchone()[0]

    cursor.execute("""
    SELECT career_goal, COUNT(*) as total
    FROM roadmap_history
    WHERE student_id = %s
    GROUP BY career_goal
    ORDER BY total DESC
    LIMIT 1
""",
    (session["student_id"],))

    popular_goal = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*)
        FROM course_progress
        WHERE student_id = %s
AND completed = TRUE
    """, (session["student_id"],))
    completed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM course_progress
        WHERE student_id = %s
AND completed = FALSE
    """, (session["student_id"],))
    pending = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        total_roadmaps=total_roadmaps,
        popular_goal=popular_goal,
        completed=completed,
        pending=pending
    )
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        student_name = request.form["student_name"]
        career_goal = request.form["career_goal"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            """
            INSERT INTO students
            (student_name, career_goal, email, password)
            VALUES (%s, %s, %s, %s)
            """,
            (
                student_name,
                career_goal,
                email,
                password
            )
        )

        db.commit()

        return redirect("/login")

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE email = %s
            AND password = %s
            """,
            (email, password)
        )

        student = cursor.fetchone()

        if student:

            session["student_id"] = student[0]
            session["student_name"] = student[1]

            return redirect("/")

        else:

            return "Invalid Credentials"

    return render_template("login.html")
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
@app.route("/profile")
def profile():

    if "student_id" not in session:
        return redirect("/login")

    student_id = session["student_id"]

    # Student Details
    cursor.execute("""
        SELECT student_name,
               email,
               career_goal
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    # Roadmaps Generated
    cursor.execute("""
        SELECT COUNT(*)
        FROM roadmap_history
        WHERE student_id = %s
    """, (student_id,))

    roadmap_count = cursor.fetchone()[0]

    # Completed Courses
    cursor.execute("""
        SELECT COUNT(*)
        FROM course_progress
        WHERE student_id = %s
        AND completed = TRUE
    """, (student_id,))

    completed_count = cursor.fetchone()[0]

    # Pending Courses
    cursor.execute("""
        SELECT COUNT(*)
        FROM course_progress
        WHERE student_id = %s
        AND completed = FALSE
    """, (student_id,))

    pending_count = cursor.fetchone()[0]

    total_courses = completed_count + pending_count

    progress = 0

    if total_courses > 0:
        progress = round(
        completed_count * 100 / total_courses,
        2
    )

    return render_template(
        "profile.html",
        student=student,
        roadmap_count=roadmap_count,
        completed_count=completed_count,
        pending_count=pending_count,
        progress=progress
    )
if __name__ == "__main__":
    app.run(debug=True)