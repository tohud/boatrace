DROP TABLE IF EXISTS racemember;

CREATE TABLE racemember (
    raceId CHAR(14),
    rmLane TINYINT,
    rmToban CHAR(4),
    rmRank CHAR(2),
    PRIMARY KEY (raceId,rmLane)
);
  