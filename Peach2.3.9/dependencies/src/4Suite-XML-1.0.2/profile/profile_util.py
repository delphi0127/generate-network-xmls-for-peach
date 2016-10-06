import profile, pstats, os, sha



def run(cmd,g,l):
    tempFileName = 'out.profile'
    prof = profile.Profile()
    prof.runctx(cmd,g,l)

    prof.dump_stats(tempFileName)

    pstat = pstats.Stats(tempFileName)

    print "Sorted by total cumulative time"
    pstat.strip_dirs().sort_stats('time').print_stats(100)
    print "Sorted by number calls time"
    pstat.strip_dirs().sort_stats('calls').print_stats(100)
    print "Sorted by number calls time"
    pstat.strip_dirs().sort_stats('cumulative').print_stats(100)
    print "A Listing of who called who"
    pstat.print_callers()
    print "A Listing of who was called by who"
    pstat.print_callees()
    del pstat
    os.unlink(tempFileName)
    

from Ft.Server.Common import ClAuthenticate
from Ft.Server.Server import SCore
from Ft.Server.Server.Lib import LogUtil
def GetRepo():
    properties = GetProperties()
    return SCore.GetRepository(userName,sha.new(password).hexdigest(),LogUtil.NullLogger(),properties)


userName = 'root'
password = 'root'
from Ft.Server.Server.Commands import Init

from Ft.Rdf import Model

def InitRepo():
    global properties
    properties = GetProperties()
    Init.DoInit(properties, userName, sha.new(password).hexdigest(),
                ['Core'], 1, 0, [(userName, password)], 1)

properties = None
def InitModel():
    global properties
    driver = GetRdfDriverModule()
    if driver.ExistsDb('testModel'):
        driver.DestroyDb('testModel')
    db = driver.CreateDb('testModel')
    db.begin()
    return Model.Model(db)



def GetProperties():
    import sys
    properties = {}
    if "--postgres" in sys.argv:
        print "Using Postgress Driver"
        properties['Driver'] = PostgresDriverProperties()
    else:
        print "Using Flat File Driver"
        properties['Driver'] = FlatFileDriverProperties()

    properties['CoreId'] = 'Core'
    return properties


def GetRdfDriverModule():
    import sys
    properties = {}
    if "--postgres" in sys.argv:
        print "Using Postgres Driver"
        from Ft.Rdf.Drivers import Postgres
        return Postgres
    if "--dbm" in sys.argv:
        print "Using Dbm Driver"
        from Ft.Rdf.Drivers import Dbm
        return Dbm

    print "Memory Driver"
    from Ft.Rdf.Drivers import Memory
    return Memory


def GetRdfDriver():
    mod = GetRdfDriverModule()
    db = mod.GetDb('testModel')
    db.begin()
    return db

def FlatFileDriverProperties():
    return {'TYPE': 'FlatFile', 'Root': 'profileServer'} 


def PostgresDriverProperties():
    return {'TYPE': 'Postgres', 'DbName': 'profileserver','Host':None, 'Port':-1,'User':None, 'Passwd':None} 
