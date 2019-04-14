DROP TABLE IF EXISTS racemanagement;

CREATE TABLE racemanagement (
    raceId CHAR(14),
    raceDate DATE,
    raceNumber TINYINT,
    raceName VARCHAR(80),
    raceGrade VARCHAR(5),
    racePlaceId CHAR(2),
    racebeforeinfo_flg BOOLEAN,
    racemember_flg BOOLEAN,
    raceodds_flg BOOLEAN,
    PRIMARY KEY (raceId),
    INDEX raceinfo_date_idx (raceDate)
);