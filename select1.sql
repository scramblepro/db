SELECT title, duration
FROM track
ORDER BY duration DESC
LIMIT 1;

SELECT title
FROM track
WHERE duration >= '190';

SELECT title
FROM collection
WHERE release_date BETWEEN '2018-01-01' AND '2020-12-31';

SELECT name
FROM artist
WHERE name NOT LIKE '% %';

SELECT title
FROM track
WHERE title ILIKE '%мой%' OR title ILIKE '%my%';

SELECT g.name AS genre, COUNT(ag.artist_id) AS artist_count
FROM genre g
JOIN artist_genre ag ON g.id = ag.genre_id
GROUP BY g.name;

SELECT a.title AS album, COUNT(t.id) AS track_count
FROM album a
JOIN track t ON a.id = t.album_id
WHERE a.release_date BETWEEN '2019-01-01' AND '2020-12-31'
GROUP BY a.title;

SELECT a.title AS album, AVG(t.duration) AS average_duration
FROM album a
JOIN track t ON a.id = t.album_id
GROUP BY a.title;

SELECT ar.name AS artist
FROM artist ar
WHERE ar.id NOT IN (
    SELECT aa.artist_id
    FROM artist_alb aa
    JOIN album a ON aa.album_id = a.id
    WHERE a.release_date BETWEEN '2020-01-01' AND '2020-12-31'
);

SELECT c.title AS collection
FROM collection c
JOIN collection_track ct ON c.id = ct.collection_id
JOIN track t ON ct.track_id = t.id
JOIN album a ON t.album_id = a.id
JOIN artist_alb aa ON a.id = aa.album_id
WHERE aa.artist_id = 1;
