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
SHOW tables;
DESC recommendations;
SELECT * FROM recommendations;

CREATE TABLE roadmap_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_goal VARCHAR(100),
    skills TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
SELECT * from roadmap_history;

CREATE TABLE course_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(200),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;

SELECT * from course_progress;
DESC course_progress;
DESC students;
ALTER TABLE students
ADD email VARCHAR(100) UNIQUE,
ADD password VARCHAR(255);

SELECT * from roadmap_history;
ALTER TABLE roadmap_history ADD student_id INT;
ALTER TABLE course_progress ADD student_id INT;
DELETE FROM students WHERE email='kunalsah3108@gmail.com';

ALTER TABLE students AUTO_INCREMENT = 1;
TRUNCATE TABLE course_progress;
SELECT * FROM students;
SELECT * 
FROM course_progress
WHERE student_id = 1;


CREATE TABLE resume_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    career_goal VARCHAR(100),
    resume_score INT,
    found_skills TEXT,
    missing_skills TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM resume_history;

CREATE TABLE student_skills(
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    skill_name VARCHAR(100)
);