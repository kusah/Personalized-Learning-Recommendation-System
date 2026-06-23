import pandas as pd
df=pd.read_csv("data/course.csv")
career_skills = {
    "Data Analyst": ["SQL", "Power BI", "Excel", "Statistics", "Python"],
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "Deep Learning"],
    "Software Developer": ["Java", "DSA", "OOP", "Web Development"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "MLOps", "Docker"],
    "Business Analyst": ["Business Analysis", "Agile"]
}
level_order = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3
}
def find_skill_gaps(career_goal, known_skills):
    required_skills = career_skills[career_goal]
    missing_skills = []
    for skill in required_skills:
        if skill not in known_skills:
            missing_skills.append(skill)
    return missing_skills

def recommend_by_skill_gap(career_goal, known_skills):
    gaps = find_skill_gaps(career_goal, known_skills)
    recommendations = df[
        (df["career_path"] == career_goal) &
        (df["skill"].isin(gaps))
    ]
    return recommendations[
        ["course_name", "skill", "level"]
    ]

def generate_roadmap(career_goal, known_skills):
    recommendations = recommend_by_skill_gap(
        career_goal,
        known_skills
    ).copy()
    recommendations["level_rank"] = recommendations["level"].map(level_order)
    roadmap = recommendations.sort_values("level_rank")
    return roadmap[["course_name", "skill", "level"]]


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

career_profiles = {
    "Data Analyst":
        "Python SQL Excel Power BI Statistics Tableau Data Cleaning Data Visualization",

    "Data Scientist":
        "Python Statistics Machine Learning Deep Learning Pandas NumPy Scikit-learn",

    "Software Developer":
        "Java Python DSA OOP Web Development React Flask Git GitHub",

    "Machine Learning Engineer":
        "Python Machine Learning Deep Learning TensorFlow PyTorch Docker MLOps",

    "Business Analyst":
        "Excel SQL Power BI Tableau Business Analysis Agile Requirements Gathering"
}

def predict_career_match(resume_text):

    documents = [resume_text]

    for profile in career_profiles.values():
        documents.append(profile)

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    results = {}

    for career, score in zip(
        career_profiles.keys(),
        similarities
    ):
        results[career] = min(round(score * 300, 2),100)
    return sorted(
        results.items(),
        key=lambda x: x[1],
        reverse=True
    )
