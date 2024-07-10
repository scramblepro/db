INSERT INTO genre (name) VALUES 
('Rock'),
('Pop'),
('Jazz');

INSERT INTO artist (name) VALUES 
('The Beatles'),
('Elvis Presley'),
('Miles Davis'),
('Madonna');

INSERT INTO album (title, release_date) VALUES 
('Abbey Road', '1969-09-26'),
('Blue Hawaii', '1961-10-20'),
('Kind of Blue', '1959-08-17');

INSERT INTO track (title, album_id, duration) VALUES 
('Come Together', 4, '249'),
('Something', 4, '167'),
('Can not Help Falling in Love', 2, '154'),
('хе-хе Baby', 2, '121'),
('So What', 3, '578'),
('Freddie Freeloader', 3, '666');

INSERT INTO collection (title, release_date) VALUES 
('Best of 60s', '2000-01-01'),
('Greatest Hits', '1990-05-20'),
('Classic Jazz', '1980-12-05'),
('Pop Legends', '2010-06-15');

INSERT INTO artist_genre (artist_id, genre_id) VALUES 
(1, 1),
(2, 1),
(3, 3),
(4, 2);

INSERT INTO collection_track (collection_id, track_id) VALUES 
(1, 1),
(1, 2),
(2, 3), 
(2, 4),
(3, 5),
(3, 6),
(4, 1),
(4, 3);

INSERT INTO artist_alb (artist_id, album_id) VALUES 
(1, 1),
(2, 2),
(3, 3);
