DROP TABLE IF EXISTS exercise_sets        CASCADE;
DROP TABLE IF EXISTS performed_exercises  CASCADE;
DROP TABLE IF EXISTS workout_sessions     CASCADE;
DROP TABLE IF EXISTS workout_plans        CASCADE;
DROP TABLE IF EXISTS exercises            CASCADE;
DROP TABLE IF EXISTS users                CASCADE;

CREATE TABLE users (
    user_id       SERIAL       PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE exercises (
    exercise_id   SERIAL       PRIMARY KEY,
    exercise_name VARCHAR(100) NOT NULL,
    muscle_group  VARCHAR(50)
);

CREATE TABLE workout_plans (
    plan_id   SERIAL       PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    user_id   INTEGER      NOT NULL
        REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE workout_sessions (
    session_id SERIAL  PRIMARY KEY,
    plan_id    INTEGER NOT NULL
        REFERENCES workout_plans (plan_id) ON DELETE CASCADE,
    date       DATE    NOT NULL
);

CREATE TABLE performed_exercises (
    performed_id SERIAL  PRIMARY KEY,
    session_id   INTEGER NOT NULL
        REFERENCES workout_sessions (session_id) ON DELETE CASCADE,
    exercise_id  INTEGER NOT NULL
        REFERENCES exercises (exercise_id) ON DELETE RESTRICT
);

CREATE TABLE exercise_sets (
    set_id       SERIAL       PRIMARY KEY,
    performed_id INTEGER      NOT NULL
        REFERENCES performed_exercises (performed_id) ON DELETE CASCADE,
    set_number   INTEGER      NOT NULL CHECK (set_number > 0),
    weight       NUMERIC(6,2) CHECK (weight  >= 0),
    reps         INTEGER      CHECK (reps     >= 0),
    time         INTEGER      CHECK (time      >= 0)
);

CREATE INDEX idx_workout_plans_user_id           ON workout_plans       (user_id);
CREATE INDEX idx_workout_sessions_plan_id        ON workout_sessions    (plan_id);
CREATE INDEX idx_performed_exercises_session_id  ON performed_exercises (session_id);
CREATE INDEX idx_performed_exercises_exercise_id ON performed_exercises (exercise_id);
CREATE INDEX idx_exercise_sets_performed_id      ON exercise_sets       (performed_id);

INSERT INTO users (username, email, password_hash) VALUES
    ('jdoe',    'jdoe@example.com',    'pbkdf2:sha256:1000000$gT71qqJwqwO4fTu9$fcfd596ca3ec5c2786cde7fb9008372343bc574a5292891e7b8cd0658d41d2ab'),
    ('asmith',  'asmith@example.com',  'pbkdf2:sha256:1000000$lndHZPccQnj99urs$53501a69296ce0cfc690d6a94babf592437cb68b05b98faae67b6eb6408776e6'),
    ('mgarcia', 'mgarcia@example.com', 'pbkdf2:sha256:1000000$AxMl0YO5pAinoIpY$2058aff77cff45c8ad5d5e32e822a52b5ad5288f8017e34679def70156cffdcb'),
    ('kpatel',  'kpatel@example.com',  'pbkdf2:sha256:1000000$LEP6eCdabFIWUqMC$c14ad8c1d8c058ac95f7b5fd5d5330dd53ae25512d3f4bfc76c285ae219a0dac'),
    ('lnguyen', 'lnguyen@example.com', 'pbkdf2:sha256:1000000$L6ewkpAy7KCPXxcW$6ef297ff28f525963f4dd8f0d18ec8a34f561f5ddba473ebb7ef3850c9f4569f'),
    ('owilson', 'owilson@example.com', 'pbkdf2:sha256:1000000$pHhjA4cGUZsaxIsN$0213fb2bf884f87f154fad04de0cea76d5bef9b59d7af227062546632de2bbd3'),
    ('rkovac',  'rkovac@example.com',  'pbkdf2:sha256:1000000$TJJjg5fwHHPihqyg$0e8a010109e0c686060a4c79f8a2dcff50a57e127364ab1b58a9dc9e582665b0');

INSERT INTO exercises (exercise_name, muscle_group) VALUES
    ('Barbell Bench Press', 'Chest'),
    ('Back Squat',          'Legs'),
    ('Deadlift',            'Back'),
    ('Overhead Press',      'Shoulders'),
    ('Pull-Up',             'Back'),
    ('Barbell Row',         'Back'),
    ('Plank',               'Core'),
    ('Bicep Curl',          'Arms'),
    ('Leg Press',           'Legs'),
    ('Lat Pulldown',        'Back');

INSERT INTO workout_plans (plan_name, user_id) VALUES
    ('Push Pull Legs',      1),
    ('Upper / Lower',       1),
    ('Full Body 3x',        2),
    ('Strength Block',      3),
    ('Beginner Routine',    4),
    ('Hypertrophy Phase',   5),
    ('Powerlifting Prep',   6);

INSERT INTO workout_sessions (plan_id, date) VALUES
    (1, '2025-05-05'),
    (1, '2025-05-07'),
    (1, '2025-05-09'),
    (2, '2025-05-06'),
    (3, '2025-05-08'),
    (4, '2025-05-10'),
    (5, '2025-05-11'),
    (6, '2025-05-12'),
    (7, '2025-05-13');

INSERT INTO performed_exercises (session_id, exercise_id) VALUES
    (1, 1),
    (1, 4),
    (2, 2),
    (2, 9),
    (3, 3),
    (4, 1),
    (5, 5),
    (6, 2),
    (7, 7),
    (8, 6);

INSERT INTO exercise_sets (performed_id, set_number, weight, reps, time) VALUES
    (1, 1,  60.00, 10, NULL),
    (1, 2,  70.00,  8, NULL),
    (1, 3,  80.00,  6, NULL),
    (2, 1,  40.00, 10, NULL),
    (2, 2,  45.00,  8, NULL),
    (3, 1, 100.00,  5, NULL),
    (3, 2, 110.00,  5, NULL),
    (4, 1, 120.00,  8, NULL),
    (5, 1, 140.00,  5, NULL),
    (9, 1,   NULL, NULL, 60),
    (9, 2,   NULL, NULL, 75),
    (10, 1,  70.00, 10, NULL);

SELECT setval('users_user_id_seq',                      (SELECT MAX(user_id)      FROM users));
SELECT setval('exercises_exercise_id_seq',              (SELECT MAX(exercise_id)  FROM exercises));
SELECT setval('workout_plans_plan_id_seq',              (SELECT MAX(plan_id)      FROM workout_plans));
SELECT setval('workout_sessions_session_id_seq',        (SELECT MAX(session_id)   FROM workout_sessions));
SELECT setval('performed_exercises_performed_id_seq',   (SELECT MAX(performed_id) FROM performed_exercises));
SELECT setval('exercise_sets_set_id_seq',               (SELECT MAX(set_id)       FROM exercise_sets));
