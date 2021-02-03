constl = [
        'SET FOREIGN_KEY_CHECKS=0;',
        'DROP TABLE IF EXISTS user;',
        'DROP TABLE IF EXISTS profile;',
        'DROP TABLE IF EXISTS post;',
        'DROP TABLE IF EXISTS comment;',
        'DROP TABLE IF EXISTS metadata',
        'SET FOREIGN_KEY_CHECKS=1;',
        """
            CREATE TABLE metadata (
                id INT PRIMARY KEY AUTO_INCREMENT,
                entries INT
            );
        """,
        'INSERT INTO metadata (entries) VALUES (0)',
        """
            CREATE TABLE user (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            );
        """,
        """
            CREATE TABLE profile (
                id INT PRIMARY KEY AUTO_INCREMENT,
                birthday DATE,
                bio VARCHAR(300),
                direction VARCHAR(50),
                pfp VARCHAR(80),
                entries INT NOT NULL DEFAULT 0,
                anniversary TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """,
        """
            CREATE TABLE post (
                id INT PRIMARY KEY AUTO_INCREMENT,
                created_by INT NOT NULL,
                last_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(80) NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (created_by) REFERENCES user (id)
            );
        """,
        """
            CREATE TABLE comment (
                id INT PRIMARY KEY AUTO_INCREMENT,
                created_by INT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                commented_to INT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                likes INT NOT NULL DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES profile (id),
                FOREIGN KEY (commented_to) REFERENCES post (id)
            );
        """,
]