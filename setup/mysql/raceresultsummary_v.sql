CREATE OR REPLACE VIEW raceresultsummary_v AS
select o.raceId ,m.raceDate, m.raceNumber ,m.raceGrade,m.raceplaceId,f.funaken,o.odds,
       bi.raceTemperature,bi.raceWeather,bi.raceWindSpeed,bi.raceSurfaceTemperature,bi.raceWaveHeight     
       from raceodds o , racemanagement m , racebeforeinfo bi ,     
            (select concat(fa.lane,'-',fb.lane,'-',fc.lane) as funaken,fa.raceId from     
                    (select lane,raceId from raceresult where goalRank=1) fa,     
                    (select lane,raceId from raceresult where goalRank=2) fb,     
                    (select lane,raceId from raceresult where goalRank=3) fc      
                     where fa.raceId = fb.raceId     
                       and fb.raceId = fc.raceId ) f     
       where m.raceId = o.raceId     
         and o.raceId = f.raceId     
         and m.raceId = bi.raceId     
         and o.oddsType='3t'      
         and o.funaken = f.funaken
;
