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


