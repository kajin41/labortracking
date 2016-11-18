

currentJobs = []
employees = []
activeWorkstations = []

conn = []

cursor = []

ipaddrs = {'10.1.1.34': 'FAB010',
           '10.1.1.91': 'FAB020',
           '10.1.1.92': 'FAB080',
           '10.1.1.94': 'FAB060',
           '10.1.1.79': 'gmercado'}

SQLQueries = {
    'station-manhours': "SELECT [WipMaster].Job, [Station], sum(datediff(minute,Datestart,DateFinish)) as manMinutes\
                          FROM [SysproCompanyC].[dbo].[TrackLaborEmployee]\
                          left join WipMaster\
                          on WipMaster.Job LIKE '%'+ TrackLaborEmployee.Job",
    'station-totaltime': "SELECT\
                              [WipMaster].Job\
	                          ,[MasterJob]\
                              ,[Station]\
                              ,sum(datediff(minute,Datestart,DateFinish)) as totaltime\
                              ,min(Datestart) as starttime\
                              ,max(DateFinish) as endtime\
                            FROM [SysproCompanyC].[dbo].[TrackLaborJob]\
                            left join WipMaster\
                            on WipMaster.Job LIKE '%'+ TrackLaborJob.Job",
    'station-group': "GROUP BY MasterJob,WipMaster.Job,Station",
    'subJob-manhours': "SELECT [WipMaster].Job, sum(datediff(minute,Datestart,DateFinish)) as manMinutes\
                          FROM [SysproCompanyC].[dbo].[TrackLaborEmployee]\
                          left join WipMaster\
                          on WipMaster.Job LIKE '%'+ TrackLaborEmployee.Job",
    'subJob-totaltime': "SELECT\
                              [WipMaster].Job\
	                          [MasterJob]\
                              ,sum(datediff(minute,Datestart,DateFinish)) as totaltime\
                              ,min(Datestart) as starttime\
                              ,max(DateFinish) as endtime\
                            FROM [SysproCompanyC].[dbo].[TrackLaborJob]\
                            left join WipMaster\
                            on WipMaster.Job LIKE '%'+ TrackLaborJob.Job",
    'subJob-group': "GROUP BY MasterJob, WipMaster.Job",
    'masterJob-manhours': "SELECT [MasterJob], sum(datediff(minute,Datestart,DateFinish)) as manMinutes\
                          FROM [SysproCompanyC].[dbo].[TrackLaborEmployee]\
                          left join WipMaster\
                          on WipMaster.Job LIKE '%'+ TrackLaborEmployee.Job",
    'masterJob-totaltime': "SELECT\
	                          [MasterJob]\
                              ,sum(datediff(minute,Datestart,DateFinish)) as totaltime\
                              ,min(Datestart) as starttime\
                              ,max(DateFinish) as endtime\
                            FROM [SysproCompanyC].[dbo].[TrackLaborJob]\
                            left join WipMaster\
                            on WipMaster.Job LIKE '%'+ TrackLaborJob.Job",
    'masterJob-group': "GROUP BY MasterJob",
}