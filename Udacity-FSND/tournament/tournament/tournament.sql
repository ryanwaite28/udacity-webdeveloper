-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;


CREATE TABLE players (
  name TEXT,
  id SERIAL PRIMARY KEY
);



CREATE TABLE games (
  round SERIAL,
  winner INTEGER REFERENCES players (id),
  loser INTEGER REFERENCES players (id),
  PRIMARY KEY (round)
);



CREATE VIEW standings as
  SELECT players.id,
  players.name,
  COUNT (nullif(games.loser , players.id)) AS wins,
  COUNT (games) AS matches
  FROM players LEFT JOIN games ON (players.id = games.winner) OR (players.id = games.loser)
  GROUP BY players.id ORDER BY wins DESC;
