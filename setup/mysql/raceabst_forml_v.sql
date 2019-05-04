CREATE OR REPLACE VIEW raceabst_forml_v
as
select g.raceId,g.raceDate,
       m1.Fcnt as l1Fcnt,m1.motor2r as l1motor2r,m1.motor3r as l1motor3r,m1.boat2r as l1boat2r,m1.boat3r as l1boat3r,1000/o1.avgo as l1score,
       m2.Fcnt as l2Fcnt,m2.motor2r as l2motor2r,m2.motor3r as l2motor3r,m2.boat2r as l2boat2r,m2.boat3r as l2boat3r,1000/o2.avgo as l2score,
       m3.Fcnt as l3Fcnt,m3.motor2r as l3motor2r,m3.motor3r as l3motor3r,m3.boat2r as l3boat2r,m3.boat3r as l3boat3r,1000/o3.avgo as l3score,
       m4.Fcnt as l4Fcnt,m4.motor2r as l4motor2r,m4.motor3r as l4motor3r,m4.boat2r as l4boat2r,m4.boat3r as l4boat3r,1000/o4.avgo as l4score,
       m5.Fcnt as l5Fcnt,m5.motor2r as l5motor2r,m5.motor3r as l5motor3r,m5.boat2r as l5boat2r,m5.boat3r as l5boat3r,1000/o5.avgo as l5score,
       m6.Fcnt as l6Fcnt,m6.motor2r as l6motor2r,m6.motor3r as l6motor3r,m6.boat2r as l6boat2r,m6.boat3r as l6boat3r,1000/o6.avgo as l6score,
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
   group by raceId) o6
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
order by g.raceId

