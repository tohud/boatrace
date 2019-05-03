DROP TABLE IF EXISTS racemember;

CREATE TABLE racemember (
    raceId CHAR(14),
    rmLane TINYINT,
    rmToban CHAR(4),
    rmRank CHAR(2),
    Fcnt TINYINT,
    Lcnt TINYINT,
    avgStart FLOAT(3,2),
    motor2r FLOAT(5,2),
    motor3r FLOAT(5,2),
    boat2r FLOAT(5,2),
    boat3r FLOAT(5,2),
    PRIMARY KEY (raceId,rmLane)
);
  
