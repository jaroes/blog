constl = [
        'SET FOREIGN_KEY_CHECKS=0;',
        'DROP TABLE IF EXISTS user;',
        'DROP TABLE IF EXISTS profile;',
        'DROP TABLE IF EXISTS post;',
        'DROP TABLE IF EXISTS comment;',
        'SET FOREIGN_KEY_CHECKS=1;',
        """
            CREATE TABLE user (
                id INT PRIMARY KEY AUTO_INCREMENT,
                email VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        """,
        """
            CREATE TABLE profile (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                birthday TIMESTAMP,
                bio VARCHAR(300),
                direction VARCHAR(50),
                owner INT UNIQUE NOT NULL,
                pfp VARCHAR(50),
                anniversary TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner) REFERENCES user (id)
            );
        """,
        """
            CREATE TABLE post (
                id INT PRIMARY KEY AUTO_INCREMENT,
                created_by INT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(80) NOT NULL,
                content TEXT NOT NULL,
                likes INT NOT NULL DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES profile (id)
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
        """
]