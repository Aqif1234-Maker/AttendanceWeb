CREATE TABLE teachers (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    full_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    roll_number VARCHAR(50)  NOT NULL UNIQUE,
    class       VARCHAR(20)  NOT NULL,
    section     VARCHAR(10)  NOT NULL,
    contact     VARCHAR(20),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_accounts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT,
    name        VARCHAR(100) NOT NULL,
    roll_number VARCHAR(50)  NOT NULL UNIQUE,
    class       VARCHAR(20)  NOT NULL,
    section     VARCHAR(10)  NOT NULL,
    contact     VARCHAR(20),
    password    VARCHAR(255) NOT NULL,
    approved    TINYINT(1)   DEFAULT 0,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);

CREATE TABLE attendance (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date       DATE NOT NULL,
    status     ENUM('Present','Absent','Late') NOT NULL,
    marked_by  INT,
    UNIQUE KEY unique_attendance (student_id, date),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by)  REFERENCES teachers(id) ON DELETE SET NULL
);
