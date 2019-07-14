CREATE OR REPLACE VIEW raceabst_forml_rentai_v
as
select g.raceId,g.raceDate,
       m1.rmRank as l1rank, m1.Fcnt as l1Fcnt,m1.motor2r/100.0 as l1motor2r,m1.motor3r/100.0 as l1motor3r,m1.boat2r/100.0 as l1boat2r,m1.boat3r/100.0 as l1boat3r,1000/o1.avgo as l1score,
       m2.rmRank as l2rank, m2.Fcnt as l2Fcnt,m2.motor2r/100.0 as l2motor2r,m2.motor3r/100.0 as l2motor3r,m2.boat2r/100.0 as l2boat2r,m2.boat3r/100.0 as l2boat3r,1000/o2.avgo as l2score,
       m3.rmRank as l3rank, m3.Fcnt as l3Fcnt,m3.motor2r/100.0 as l3motor2r,m3.motor3r/100.0 as l3motor3r,m3.boat2r/100.0 as l3boat2r,m3.boat3r/100.0 as l3boat3r,1000/o3.avgo as l3score,
       m4.rmRank as l4rank, m4.Fcnt as l4Fcnt,m4.motor2r/100.0 as l4motor2r,m4.motor3r/100.0 as l4motor3r,m4.boat2r/100.0 as l4boat2r,m4.boat3r/100.0 as l4boat3r,1000/o4.avgo as l4score,
       m5.rmRank as l5rank, m5.Fcnt as l5Fcnt,m5.motor2r/100.0 as l5motor2r,m5.motor3r/100.0 as l5motor3r,m5.boat2r/100.0 as l5boat2r,m5.boat3r/100.0 as l5boat3r,1000/o5.avgo as l5score,
       m6.rmRank as l6rank, m6.Fcnt as l6Fcnt,m6.motor2r/100.0 as l6motor2r,m6.motor3r/100.0 as l6motor3r,m6.boat2r/100.0 as l6boat2r,m6.boat3r/100.0 as l6boat3r,1000/o6.avgo as l6score,
       old.l1oldrank1 as l1oldrank1,old.l1oldrank2 as l1oldrank2,old.l1oldrank3 as l1oldrank3,old.l1oldrank4 as l1oldrank4,old.l1oldrank5 as l1oldrank5,old.l1oldrank6 as l1oldrank6,old.l1oldavgstdev as l1oldavgstdev,old.l1oldavgsttime as l1oldavgsttime,
       old.l2oldrank1 as l2oldrank1,old.l2oldrank2 as l2oldrank2,old.l2oldrank3 as l2oldrank3,old.l2oldrank4 as l2oldrank4,old.l2oldrank5 as l2oldrank5,old.l2oldrank6 as l2oldrank6,old.l2oldavgstdev as l2oldavgstdev,old.l2oldavgsttime as l2oldavgsttime,
       old.l3oldrank1 as l3oldrank1,old.l3oldrank2 as l3oldrank2,old.l3oldrank3 as l3oldrank3,old.l3oldrank4 as l3oldrank4,old.l3oldrank5 as l3oldrank5,old.l3oldrank6 as l3oldrank6,old.l3oldavgstdev as l3oldavgstdev,old.l3oldavgsttime as l3oldavgsttime,
       old.l4oldrank1 as l4oldrank1,old.l4oldrank2 as l4oldrank2,old.l4oldrank3 as l4oldrank3,old.l4oldrank4 as l4oldrank4,old.l4oldrank5 as l4oldrank5,old.l4oldrank6 as l4oldrank6,old.l4oldavgstdev as l4oldavgstdev,old.l4oldavgsttime as l4oldavgsttime,
       old.l5oldrank1 as l5oldrank1,old.l5oldrank2 as l5oldrank2,old.l5oldrank3 as l5oldrank3,old.l5oldrank4 as l5oldrank4,old.l5oldrank5 as l5oldrank5,old.l5oldrank6 as l5oldrank6,old.l5oldavgstdev as l5oldavgstdev,old.l5oldavgsttime as l5oldavgsttime,
       old.l6oldrank1 as l6oldrank1,old.l6oldrank2 as l6oldrank2,old.l6oldrank3 as l6oldrank3,old.l6oldrank4 as l6oldrank4,old.l6oldrank5 as l6oldrank5,old.l6oldrank6 as l6oldrank6,old.l6oldavgstdev as l6oldavgstdev,old.l6oldavgsttime as l6oldavgsttime,
       b.raceWindSpeed,b.raceWaveHeight,
       s.funaken,s.odds
from 
 racemanagement g,
 racebeforeinfo b,
 raceresultsummary_v s,
 ( select raceId,rmToban,rmRank,Fcnt,motor2r,motor3r,boat2r,boat3r from racemember
   where rmLane = 1 ) m1,
 ( select raceId,rmToban,rmRank,Fcnt,motor2r,motor3r,boat2r,boat3r from racemember
   where rmLane = 2 ) m2,
 ( select raceId,rmToban,rmRank,Fcnt,motor2r,motor3r,boat2r,boat3r from racemember
   where rmLane = 3 ) m3,
 ( select raceId,rmToban,rmRank,Fcnt,motor2r,motor3r,boat2r,boat3r from racemember
   where rmLane = 4 ) m4,
 ( select raceId,rmToban,rmRank,Fcnt,motor2r,motor3r,boat2r,boat3r from racemember
   where rmLane = 5 ) m5,
 ( select raceId,rmToban,rmRank,Fcnt,motor2r,motor3r,boat2r,boat3r from racemember
   where rmLane = 6 ) m6,
 ( select raceId,avg(odds) as avgo from raceodds
   where oddsType='3t'
     and funaken like '1-%'
   group by raceId) o1,
 ( select raceId,avg(odds) as avgo from raceodds
   where oddsType='3t'
     and funaken like '2-%'
   group by raceId) o2,
 ( select raceId,avg(odds) as avgo from raceodds
   where oddsType='3t'
     and funaken like '3-%'
   group by raceId) o3,
 ( select raceId,avg(odds) as avgo from raceodds
   where oddsType='3t'
     and funaken like '4-%'
   group by raceId) o4,
 ( select raceId,avg(odds) as avgo from raceodds
   where oddsType='3t'
     and funaken like '5-%'
   group by raceId) o5,
 ( select raceId,avg(odds) as avgo from raceodds
   where oddsType='3t'
     and funaken like '6-%'
   group by raceId) o6,
 ( select raceId,
     max(CASE WHEN lane=1 THEN oldRank1 ELSE null END ) as l1oldrank1,
     max(CASE WHEN lane=1 THEN oldRank2 ELSE null END ) as l1oldrank2,
     max(CASE WHEN lane=1 THEN oldRank3 ELSE null END ) as l1oldrank3,
     max(CASE WHEN lane=1 THEN oldRank4 ELSE null END ) as l1oldrank4,
     max(CASE WHEN lane=1 THEN oldRank5 ELSE null END ) as l1oldrank5,
     max(CASE WHEN lane=1 THEN oldRank6 ELSE null END ) as l1oldrank6,
     max(CASE WHEN lane=1 THEN avgStartDev ELSE null END ) as l1oldavgstdev,
     max(CASE WHEN lane=1 THEN avgStartTime ELSE null END ) as l1oldavgsttime,
     max(CASE WHEN lane=2 THEN oldRank1 ELSE null END ) as l2oldrank1,
     max(CASE WHEN lane=2 THEN oldRank2 ELSE null END ) as l2oldrank2,
     max(CASE WHEN lane=2 THEN oldRank3 ELSE null END ) as l2oldrank3,
     max(CASE WHEN lane=2 THEN oldRank4 ELSE null END ) as l2oldrank4,
     max(CASE WHEN lane=2 THEN oldRank5 ELSE null END ) as l2oldrank5,
     max(CASE WHEN lane=2 THEN oldRank6 ELSE null END ) as l2oldrank6,
     max(CASE WHEN lane=2 THEN avgStartDev ELSE null END ) as l2oldavgstdev,
     max(CASE WHEN lane=2 THEN avgStartTime ELSE null END ) as l2oldavgsttime,
     max(CASE WHEN lane=3 THEN oldRank1 ELSE null END ) as l3oldrank1,
     max(CASE WHEN lane=3 THEN oldRank2 ELSE null END ) as l3oldrank2,
     max(CASE WHEN lane=3 THEN oldRank3 ELSE null END ) as l3oldrank3,
     max(CASE WHEN lane=3 THEN oldRank4 ELSE null END ) as l3oldrank4,
     max(CASE WHEN lane=3 THEN oldRank5 ELSE null END ) as l3oldrank5,
     max(CASE WHEN lane=3 THEN oldRank6 ELSE null END ) as l3oldrank6,
     max(CASE WHEN lane=3 THEN avgStartDev ELSE null END ) as l3oldavgstdev,
     max(CASE WHEN lane=3 THEN avgStartTime ELSE null END ) as l3oldavgsttime,
     max(CASE WHEN lane=4 THEN oldRank1 ELSE null END ) as l4oldrank1,
     max(CASE WHEN lane=4 THEN oldRank2 ELSE null END ) as l4oldrank2,
     max(CASE WHEN lane=4 THEN oldRank3 ELSE null END ) as l4oldrank3,
     max(CASE WHEN lane=4 THEN oldRank4 ELSE null END ) as l4oldrank4,
     max(CASE WHEN lane=4 THEN oldRank5 ELSE null END ) as l4oldrank5,
     max(CASE WHEN lane=4 THEN oldRank6 ELSE null END ) as l4oldrank6,
     max(CASE WHEN lane=4 THEN avgStartDev ELSE null END ) as l4oldavgstdev,
     max(CASE WHEN lane=4 THEN avgStartTime ELSE null END ) as l4oldavgsttime,
     max(CASE WHEN lane=5 THEN oldRank1 ELSE null END ) as l5oldrank1,
     max(CASE WHEN lane=5 THEN oldRank2 ELSE null END ) as l5oldrank2,
     max(CASE WHEN lane=5 THEN oldRank3 ELSE null END ) as l5oldrank3,
     max(CASE WHEN lane=5 THEN oldRank4 ELSE null END ) as l5oldrank4,
     max(CASE WHEN lane=5 THEN oldRank5 ELSE null END ) as l5oldrank5,
     max(CASE WHEN lane=5 THEN oldRank6 ELSE null END ) as l5oldrank6,
     max(CASE WHEN lane=5 THEN avgStartDev ELSE null END ) as l5oldavgstdev,
     max(CASE WHEN lane=5 THEN avgStartTime ELSE null END ) as l5oldavgsttime,
     max(CASE WHEN lane=6 THEN oldRank1 ELSE null END ) as l6oldrank1,
     max(CASE WHEN lane=6 THEN oldRank2 ELSE null END ) as l6oldrank2,
     max(CASE WHEN lane=6 THEN oldRank3 ELSE null END ) as l6oldrank3,
     max(CASE WHEN lane=6 THEN oldRank4 ELSE null END ) as l6oldrank4,
     max(CASE WHEN lane=6 THEN oldRank5 ELSE null END ) as l6oldrank5,
     max(CASE WHEN lane=6 THEN oldRank6 ELSE null END ) as l6oldrank6,
     max(CASE WHEN lane=6 THEN avgStartDev ELSE null END ) as l6oldavgstdev,
     max(CASE WHEN lane=6 THEN avgStartTime ELSE null END ) as l6oldavgsttime
   from oldResultByToban
   group by raceId
   ) old
where o1.raceId = o2.raceId
  and o1.raceId = o3.raceId
  and o1.raceId = o4.raceId
  and o1.raceId = o5.raceId
  and o1.raceId = o6.raceId
  and g.raceId = o1.raceId
  and g.raceId = b.raceId
  and g.raceId = s.raceId
  and g.raceId = m1.raceId
  and g.raceId = m2.raceId
  and g.raceId = m3.raceId
  and g.raceId = m4.raceId
  and g.raceId = m5.raceId
  and g.raceId = m6.raceId
  and g.raceId = old.raceId
order by g.raceId

