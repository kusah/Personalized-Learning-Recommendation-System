# 🚀 Personalized Learning Recommendation System

A Flask-based web application that helps students build personalized learning roadmaps based on their career goals and current skills.

## 🌐 Live Demo

https://personalized-learning-recommendation-gncz.onrender.com/

---

## ✨ Features

### 🎯 Career-Based Roadmap Generation

* Select a target career role.
* Choose your existing skills.
* Generate a personalized learning roadmap.

### 📄 Resume Analyzer

* Upload a PDF resume.
* Extract skills automatically.
* Identify missing skills for the chosen career path.
* Generate a resume score.

### 📚 Course Recommendations

* Recommends courses based on skill gaps.
* Allows users to add recommended courses to their roadmap.

### 📈 Progress Tracking

* Mark courses as completed.
* View learning progress percentage.
* Track completed and pending courses.

### 📊 Analytics Dashboard

* Total roadmaps generated.
* Most popular career goal.
* Latest resume score.
* Course completion analytics.

### 👤 User Profile

* Personalized student profile.
* Learning statistics.
* Progress overview.

### 📝 History Tracking

* Resume analysis history.
* Roadmap generation history.

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask

### Database

* MySQL
* Railway Cloud Database

### Frontend

* HTML
* CSS
* Jinja2 Templates

### Libraries

* Pandas
* PDFPlumber
* MySQL Connector
* Werkzeug

### Deployment

* Render
* Railway

---

## 🗄️ Database Tables

* students
* student_skills
* course_progress
* roadmap_history
* resume_history
* courses
* recommendations

---

## 📸 Screenshots

Add screenshots of:

* Home Page
* Dashboard
* Resume Analyzer
* Progress Tracker
* Profile Page

---

## 🚀 Installation

```bash
git clone <repository-url>
cd Personalized-Learning-Recommendation-System

pip install -r requirements.txt

python app.py
```

Create a `.env` file:

```env
DB_HOST=your_host
DB_PORT=your_port
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
SECRET_KEY=your_secret_key
```

---

## Future Improvements

* AI-powered course recommendations
* Learning streak tracking
* Email notifications
* Mobile responsive UI
* Advanced analytics dashboard

---

## Author

Kunal Sah

B.Tech Student | Aspiring Data Analyst & Software Developer
