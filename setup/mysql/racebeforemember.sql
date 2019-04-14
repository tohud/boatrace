DROP TABLE IF EXISTS racebeforemember;

CREATE TABLE racebeforemember (
    raceId CHAR(14),
    rmLane TINYINT,
    rmToban CHAR(4),
    rmWeight FLOAT(4,1),
    rmChoseiWeight FLOAT(4,1),
    rmTilt FLOAT(3,1),
    rmPropeller CHAR(2),
    rmTenjiTime FLOAT(3,2),
    rmStartTenjiTime FLOAT(3,2),
    PRIMARY KEY (raceId,rmLane)
);
  