from matplotlib import text
from machine_learning.recommendation import recommend_by_skill_gap, career_skills
from machine_learning.recommendation import generate_roadmap
from flask import redirect 
import mysql.connector
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv
import pdfplumber

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/home", methods=["GET", "POST"])
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

        # Add courses only if they don't already exist
        for _, row in roadmap.iterrows():

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM course_progress
                WHERE student_id = %s
                AND course_name = %s
                """,
                (
                    session["student_id"],
                    row["course_name"]
                )
            )

            count = cursor.fetchone()[0]

            if count == 0:

                cursor.execute(
                    """
                    INSERT INTO course_progress
                    (student_id, course_name)
                    VALUES (%s, %s)
                    """,
                    (
                        session["student_id"],
                        row["course_name"]
                    )
                )

        skills_text = ", ".join(known_skills)

        cursor.execute(
            """
            INSERT INTO roadmap_history
            (student_id, career_goal, skills)
            VALUES (%s, %s, %s)
            """,
            (
                session["student_id"],
                career_goal,
                skills_text
            )
        )

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
        """, 
    (session["student_id"],))

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

    if "student_id" not in session:
        return redirect("/login")

    cursor.execute(
        """
        UPDATE course_progress
        SET completed = TRUE
        WHERE id = %s
        AND student_id = %s
        """,
        (
            id,
            session["student_id"]
        )
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
    if not popular_goal:
        popular_goal = ("No Roadmaps Yet", 0)

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
    cursor.execute("""
        SELECT resume_score
        FROM resume_history
        WHERE student_id = %s
        ORDER BY analyzed_at DESC
        LIMIT 1
        """,
    (session["student_id"],))

    latest_resume = cursor.fetchone()

    if latest_resume:
        latest_resume_score = latest_resume[0]
    else:
        latest_resume_score = 0

    return render_template(
    "dashboard.html",
    total_roadmaps=total_roadmaps,
    popular_goal=popular_goal,
    completed=completed,
    pending=pending,
    latest_resume_score=latest_resume_score,
    chart_labels=["Completed", "Pending"],
    chart_values=[completed, pending]
)
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        student_name = request.form["student_name"]
        career_goal = request.form["career_goal"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        cursor.execute(
                """
                SELECT *
                FROM students
                WHERE email = %s
                """,
                (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return render_template(
                "register.html",
                error="Email already exists"
            )
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
        hashed_password
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
            """,
            (email,)
        )

        student = cursor.fetchone()

        if student and check_password_hash(
            student[4],
            password
        ):

            session["student_id"] = student[0]
            session["student_name"] = student[1]

            return redirect("/home")

        return render_template(
            "login.html",
            error="Invalid Email or Password"
        )
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
    if not student:
        return redirect("/login")

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
@app.route("/resume", methods=["GET", "POST"])
def resume():
    found_skills = []
    missing_skills = []
    resume_score = None
    recommendations = None
    career_goal = ""
    if "student_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        career_goal = request.form["career_goal"]
        session["resume_career_goal"] = career_goal

        resume_file = request.files["resume"]

        text = ""

        with pdfplumber.open(resume_file) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text

        skills_db = [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Statistics",
            "Machine Learning",
            "Deep Learning",
            "Pandas",
            "NumPy",
            "Scikit-learn",
            "TensorFlow",
            "PyTorch",
            "Java",
            "C++",
            "React",
            "FastAPI",
            "Flask",
            "Git",
            "GitHub",
            "Tableau"
        ]

        found_skills = []

        for skill in skills_db:

            if skill.lower() in text.lower():
                found_skills.append(skill)
        for skill in found_skills:
            try:
                cursor.execute(
                    """
                    INSERT INTO student_skills
                    (student_id, skill_name)
                    VALUES (%s, %s)
                    """,
                (
                    session["student_id"],
                    skill
                )
            )

            except Exception as e:
                print(e)

        db.commit()

        required_skills = career_skills[career_goal]

        missing_skills = []

        for skill in required_skills:

            if skill not in found_skills:
                missing_skills.append(skill)

        matched_skills = len(required_skills) - len(missing_skills)

        resume_score = int(
            (matched_skills / len(required_skills)) * 100
        )
        cursor.execute(
            """
            INSERT INTO resume_history
            (
                student_id,
                career_goal,
                resume_score,
                found_skills,
                missing_skills
            )
            VALUES (%s,%s,%s,%s,%s)
            """,
            (
                session["student_id"],
                career_goal,
                resume_score,
                ", ".join(found_skills),
                ", ".join(missing_skills)
            )
        )
        

        db.commit()
        recommendations = recommend_by_skill_gap(
                career_goal,
                found_skills
            )
        session["recommended_courses"] = (
            recommendations["course_name"]
            .drop_duplicates()
            .tolist()
        )
        # print("Found Skills:", found_skills)
        # print("Missing Skills:", missing_skills)
        # print("Score:", resume_score)

        return render_template(
            "resume.html",
            found_skills=found_skills,
            missing_skills=missing_skills,
            resume_score=resume_score,
            career_goal=career_goal,
            recommendations=recommendations
        )

    return render_template("resume.html")
@app.route("/add_resume_roadmap", methods=["POST"])
def add_resume_roadmap():

    if "student_id" not in session:
        return redirect("/login")

    courses = list(set(
        session.get("recommended_courses", [])
    ))

    for course in courses:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM course_progress
            WHERE student_id = %s
            AND course_name = %s
            """,
            (
                session["student_id"],
                course
            )
        )

        count = cursor.fetchone()[0]

        if count == 0:

            cursor.execute(
                """
                INSERT INTO course_progress
                (student_id, course_name)
                VALUES (%s, %s)
                """,
                (
                    session["student_id"],
                    course
                )
            )
    cursor.execute(
    """
    INSERT INTO roadmap_history
    (student_id, career_goal, skills)
    VALUES (%s, %s, %s)
    """,
    (
        session["student_id"],
        session.get("resume_career_goal", ""),
        "Resume Generated"
    )
)
    db.commit()

    return redirect("/progress")

@app.route("/resume_history")
def resume_history():

    if "student_id" not in session:
        return redirect("/login")

    cursor.execute(
        """
        SELECT *
        FROM resume_history
        WHERE student_id = %s
        ORDER BY analyzed_at DESC
        """,
        (session["student_id"],)
    )

    history = cursor.fetchall()

    return render_template(
        "resume_history.html",
        history=history
    )

if __name__ == "__main__":
    app.run(debug=True)