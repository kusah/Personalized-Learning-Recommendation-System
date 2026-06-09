use learning_recommendation_db;
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100),
    career_goal VARCHAR(100)
);
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255),
    skill VARCHAR(100),
    level VARCHAR(50)
);

CREATE TABLE recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);