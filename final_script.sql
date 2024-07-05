-- Таблица ЖАНРЫ
CREATE TABLE IF NOT EXISTS genre (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

-- Таблица ИСПОЛНИТЕЛИ
CREATE TABLE IF NOT EXISTS artist (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

-- Таблица АЛЬБОМЫ
CREATE TABLE IF NOT EXISTS album (
    id SERIAL PRIMARY KEY,
    title VARCHAR(111) NOT NULL,
    release_date DATE
);

-- Таблица ТРЕКИ
CREATE TABLE IF NOT EXISTS track (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    album_id INT REFERENCES album(id),
    duration INT NOT NULL CHECK (duration > 0)
);

-- Таблица СБОРНИКИ
CREATE TABLE IF NOT EXISTS collection (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_date DATE
);

-- Связующая таблица ИСПОЛНИТЕЛИ И ЖАНРЫ
CREATE TABLE IF NOT EXISTS artist_genre (
    artist_id INT REFERENCES artist(id),
    genre_id INT REFERENCES genre(id),
    PRIMARY KEY (artist_id, genre_id)
);

-- СВЯЗУЮЩАЯ ТАБ АЛЬБ-ИСП
CREATE TABLE IF NOT EXISTS artist_alb (
    artist_id INT REFERENCES artist(id),
    album_id INT REFERENCES album(id),
    PRIMARY KEY (artist_id, album_id)
);

CREATE TABLE IF NOT EXISTS collection_track (
    collection_id INT REFERENCES collection(id),
    track_id INT REFERENCES track(id),
    PRIMARY KEY (collection_id, track_id)
);
