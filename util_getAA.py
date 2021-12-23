'''
- 2021. 04. 06 : fix Infinity value error : conversion infinity to nan
- 2020. 12. 02 : check PV has been archived
- 2020. 11. 16 : python version 2 library error
- 2020. 09. 21 : check number of sample, default process to lastFill, improve getAAPVList
                 change function name : getAAPVList --> getAllPVs
- 2019. 12. 04 : use numpy
- 2018. 05 .02 : Initial release

- reference
  https://slacmshankar.github.io/epicsarchiver_docs/api/mgmt_scriptables.html
  https://github.com/slacmshankar/epicsarchiverap/tree/master/src/main/org/epics/archiverappliance/mgmt/bpl
'''

import sys
import time
from datetime import datetime, timedelta

import json

if sys.version_info[0] > 2:
    from urllib.request import urlopen
    from urllib.parse import urlencode
else:
    from urllib2 import urlopen
    from urllib import urlencode

import numpy as np


serverAddress = "http://xfel-archive.postech.ac.kr"


def processOperators():
    processList = ('', 'firstSample','lastSample', 'firstFill', 'lastFill',
                    'mean', 'min', 'max', 'count', 'ncount', 'nth',
                    'median', 'std', 'jitter', 'ignoreflyers', 'flyers',
                    'variance', 'popvariance', 'kurtosis', 'skewness')
    
    return processList


def getAllPVs(regex, limit=500):
    '''
    https://slacmshankar.github.io/epicsarchiver_docs/details.html
    https://slacmshankar.github.io/epicsarchiver_docs/api/org/epics/archiverappliance/mgmt/bpl/GetAllPVs.html
    
    usage :
      pvlist = getAllPVs('*BPM*CHARGE')
    '''
    params = {'pv':regex, 'limit':limit}
    query = urlencode(params)
    url = "{}:17665/mgmt/bpl/getAllPVs?{}".format(serverAddress, query)
    # print(url)
    
    try:
        req = urlopen(url)
    except:
        raise Exception("Fail to access to the web address")
    
    try:
        page = req.read()
        pvlist = json.loads(page)
    except:
        print("Fail to get pv list")
        return None
    
    return pvlist


def getPVStatus(pvlist):
    ''' Check PV is being archived
    https://slacmshankar.github.io/epicsarchiver_docs/api/org/epics/archiverappliance/mgmt/bpl/GetPVStatusAction.html
    usage :
      status = getPVStatus('XX:XX')
      status = getPVStatus(['AA:BB:CC','AA:BB:DD'])
    '''
    if isinstance(pvlist, str):
        pvlist = [pvlist]
    
    status = [False] * len(pvlist)
    
    params = {'pv': ','.join(pvlist)}
    query = urlencode(params)
    url = "{}:17665/mgmt/bpl/getPVStatus?{}".format(serverAddress, query)
    
    try:
        req = urlopen(url)
    except:
        raise Exception("Fail to access to the web address")
    
    try:
        page = req.read()
        data = json.loads(page)
    except:
        print("Fail to parse data")
        return status
    
    for i, stat in enumerate(data):
        status[i] = stat['status'] == 'Being archived'
    
    return status


def getUrl(pvname, process='lastFill', secs=None, timelimit=None, maxBuffer=10000, **kwargs):
    '''
    https://slacmshankar.github.io/epicsarchiver_docs/userguide.html
    
    pvname = 'HL1:BCM:M01:BeamCharge'
    
    **Optional arguments example
        process : Data processing function name
        secs : process interval second (1,2,3,4,...)
               default is 15 min (900 secs)
        timelimit = [datetime(2018,3,25,9,0,0), datetime(2018,3,26,2,0,0)]
        egu : Engineering Unit
        maxBuffer : Max. request data size
    
    kwargs : ...
    '''
    processList = ('', 'firstSample','lastSample', 'firstFill', 'lastFill',
                    'mean', 'min', 'max', 'count', 'ncount', 'nth',
                    'median', 'std', 'jitter', 'ignoreflyers', 'flyers',
                    'variance', 'popvariance', 'kurtosis', 'skewness')
    
    if pvname is None:
        raise Exception("pv name is not defined!!")
    
    if secs and secs < 0.1:
        secs = None
    
    if process in ('', 'raw'):
        processname = pvname
    else:
        if process in processList:
            if secs:
                processname = "{}_{:d}({})".format(process, secs, pvname)
            else:
                processname = "{}({})".format(process, pvname)
        else:
            print("Error : {} is not in operation function!!".format(process))
            return None
    
    ## Make query for archive appliance
    params = dict()
    params['pv'] = processname
    
    if timelimit:
        startTime, endTime = timelimit
        
        ## check time range
        if endTime < startTime:
            raise Exception("Request time range error : {} {}".format(startTime, endTime))
        
        if endTime - startTime < timedelta(seconds=1):
            params['pv'] = pvname
            startTime -= timedelta(seconds=1)
            endTime += timedelta(seconds=1)
        
        if sys.version_info[0] > 2:
            params['from'] = startTime.astimezone().isoformat(timespec='seconds')
            params['to']   = endTime.astimezone().isoformat(timespec='seconds')
        else:
            params['from'] = "{}+09:00".format(startTime.isoformat()[:19])
            params['to']   = "{}+09:00".format(endTime.isoformat()[:19])
        
        ## check number of samples
        dt = (endTime - startTime).total_seconds()
        if secs:
            nSamples = int(dt/secs)
        else:
            nSamples = int(dt)
        
        if nSamples > maxBuffer:
            print("Check your time range {} ~ {}".format(params['from'], params['to']))
            raise Exception("Requested sample {:d} is over the Max. sample : {:d}".format(nSamples, maxBuffer))
    
    query = urlencode(params)
    url = "{}:17668/retrieval/data/getData.json?{}".format(serverAddress, query)
    # print(params)
    return url


def getData(pvname, process='lastFill', secs=None, timelimit=None, egu=None, **kwargs):
    '''
    https://slacmshankar.github.io/epicsarchiver_docs/userguide.html#post_processing
    
    pvname = 'HL1:BCM:M01:BeamCharge'
    
    **Optional arguments example
        process : Data processing function name
        secs : process interval second (1,2,3,4,...)
               default is 15 min (900 secs)
        timelimit = [datetime(2018,3,25,9,0,0), datetime(2018,3,26,2,0,0)]
        egu : Engineering Unit
    
    kwargs : ...
    
    **After get data ==> inf value conversion to nan
    '''
    INF = float('inf')
    NAN = float('nan')
    x2val = lambda x: NAN if abs(x['val']) == INF else x['val']
    x2ts  = lambda x: datetime.fromtimestamp(x['secs'] + x['nanos']*1e-9)

    time.sleep(0.01)
    url = getUrl(pvname, process, secs, timelimit, **kwargs)
    
    try:
        req = urlopen(url)
    except:
        print("Can't access web server >> {} from\n  {}".format(pvname, url))
        return None
    
    try:
        page = req.read()
        d = json.loads(page)[0]
    except:
        print("Fail to load archive data >> {} from\n  {}".format(pvname, url))
        return None
    
    if not egu:
        egu = d['meta'].get('EGU')
    
    if not d['data']:
        print("No data >> {}".format(pvname))
        return None
    
    data_ts  = np.asarray([x2ts(x) for x in d['data']])
    data_val = np.asarray([x2val(x) for x in d['data']])
    
    if timelimit and (timelimit[0] == timelimit[1]):
        # Request specific time value
        tsDiff = data_ts - timelimit[0]
        filter = np.asarray([x.total_seconds() for x in tsDiff]) <= 0
        data_ts  = [ data_ts[filter][-1] ]
        data_val = [ data_val[filter][-1] ]
    elif len(data_ts) > 1 and data_ts[0] < timelimit[0]:
        # Remove 1st data point
        data_ts  = data_ts[1:]
        data_val = data_val[1:]
    
    return {'name': d['meta']['name'],
            'process': process,
            'egu': egu,
            'ts': data_ts,
            'val': data_val }


def getAAdata(pvlist, process='lastFill', secs=None, timelimit=None, egu=None, **kwargs):
    '''
    pvlist = ['INJ:SBPM:IN01:TMIT_CHARGE', 'HL1:BCM:M01:BeamCharge']
    
    **Optional arguments example
        process : Data processing function name
        secs : process interval second (1,2,3,4,...)
               default is 15 min (900 secs)
        timelimit = [datetime(2018,3,25,9,0,0), datetime(2018,3,26,2,0,0)]
        egu : Engineering Unit
    
    kwargs : ...
    '''
    printMode = ('quiet' not in kwargs) or not kwargs['quiet']
    
    if isinstance(pvlist, str):
        pvlist = [pvlist]
    
    if not pvlist:
        raise Exception("PV list is empty!")
        
    if isinstance(process, str):
        process = [process] * len(pvlist)
    
    if not isinstance(egu, list):
        egu = [egu] * len(pvlist)
    
    pvStatus = getPVStatus(pvlist)
    
    data = [];
    for pvname, status, proc, unit in zip(pvlist, pvStatus, process, egu):
        if status:
            d = getData(pvname, proc, secs, timelimit, unit)
            
            if d:
                ts0 = d['ts'][0].strftime("%Y-%m-%dT%H:%M:%S")
                ts1 = d['ts'][-1].strftime("%Y-%m-%dT%H:%M:%S")
                
                if printMode:
                    if len(d['ts']) == 1:
                        # print("Load PV Data >> {} ... {}".format(pvname, ts0))
                        pass
                    else:
                        # print("Load PV Data >> {} ... {} ~ {}".format(pvname, ts0, ts1))
                        pass
            else:
                pass
                # Print Error message
                # print("Fail to Load PV Data >> {}".format(pvname))            
        else:
            pass
            # print('Error >> {} is not being archived'.format(pvname))
        
        if d and status:
            data.append(d)
        else:
            data.append({'name':pvname, 'process':proc, 'egu': egu,'ts':None, 'val':None})
    
    if len(pvlist) == 1:
        data = data[0]
    
    # print("Load PV Data Finished : {} ea!".format(len(pvlist)))
    
    return data

