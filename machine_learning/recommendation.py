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