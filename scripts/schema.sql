-- Run this in Supabase SQL Editor first
CREATE TABLE IF NOT EXISTS member (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    nickname VARCHAR NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    email VARCHAR,
    phone VARCHAR,
    instagram VARCHAR,
    github VARCHAR,
    linkedin VARCHAR,
    portfolio_url VARCHAR,
    date_of_birth VARCHAR,
    current_city VARCHAR,
    gender VARCHAR,
    blood_group VARCHAR,
    relationship_status VARCHAR,
    occupation VARCHAR,
    current_company VARCHAR,
    current_status VARCHAR,
    tag VARCHAR,
    quote VARCHAR,
    bio VARCHAR,
    fun_fact VARCHAR,
    photo_url VARCHAR,
    image1 VARCHAR,
    image2 VARCHAR,
    resume_url VARCHAR
);

CREATE TABLE IF NOT EXISTS globalquestion (
    id SERIAL PRIMARY KEY,
    question VARCHAR NOT NULL,
    option_a VARCHAR NOT NULL,
    option_b VARCHAR NOT NULL,
    option_c VARCHAR NOT NULL,
    option_d VARCHAR NOT NULL,
    correct_answer VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS timelineevent (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    description VARCHAR,
    photo_urls VARCHAR
);

CREATE TABLE IF NOT EXISTS updatepost (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    content VARCHAR NOT NULL,
    excerpt VARCHAR,
    author VARCHAR NOT NULL,
    posted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    permanently_hidden BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS updateimage (
    id SERIAL PRIMARY KEY,
    update_id INTEGER NOT NULL REFERENCES updatepost(id),
    file_url VARCHAR NOT NULL,
    alt_text VARCHAR,
    order_index INTEGER NOT NULL DEFAULT 0,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS galleryitem (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    file_url VARCHAR NOT NULL,
    uploaded_by VARCHAR NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    source_update_id INTEGER REFERENCES updatepost(id),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    permanently_hidden BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS event (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    description VARCHAR,
    is_upcoming BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS guestbookentry (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    message VARCHAR NOT NULL,
    posted_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS privateupload (
    id SERIAL PRIMARY KEY,
    file_url VARCHAR NOT NULL,
    uploaded_by VARCHAR NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS internalnote (
    id SERIAL PRIMARY KEY,
    author VARCHAR NOT NULL,
    message VARCHAR NOT NULL,
    posted_at TIMESTAMP NOT NULL DEFAULT NOW()
);
