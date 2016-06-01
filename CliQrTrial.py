import requests
import json
import os
import threading

requests.packages.urllib3.disable_warnings()
user = "cliqradmin"

username = "YourUser@cliqrtech.com,1"
passwd = "YourPassWord"

baseURL = "https://<your URL/IP here>/v1"
userid = "100000"

baseHeaders = {"Accept": "application/json",
               "Content-Type": "application/json"}



def newAPIkey(userid):
    global key
    keyURL = "/users/%s/keys" % userid
    keyHeaders = {"Content-Type": "application/json"}

    keyData = json.dumps({"apiKey": {"generate": True}})

    print baseURL + keyURL

    errorReq = requests.Request('POST', baseURL + keyURL,
                                headers=keyHeaders,
                                data=keyData,
                                auth=(username, passwd))

    prepared = errorReq.prepare()

    print prepared.method +' ' + prepared.url
    print prepared.headers
    print prepared.body

    keyReq = requests.post(baseURL + keyURL,
                           headers=keyHeaders,
                           data=keyData,
                           auth=(username, passwd),
                           verify=False)

    keyJson = keyReq.json()
    key = keyJson["apiKey"]["key"]

    print key
    print keyReq.content


def getAllJobs():
    jobsURL = "/jobs"
    jobReq = requests.get(baseURL + jobsURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    jobResp = jobReq.json()

    jobId = {}

    info = jobReq.json()

    for i in range(0, len(jobResp["jobs"])):
        jobId[jobResp["jobs"][i]["id"]] = jobResp["jobs"][i]["appName"] + ', ' + jobResp["jobs"][i]["name"]

    return jobId

def getJobDet(id):
    jobURL = "/jobs/%s" % id
    jobReq = requests.get(baseURL + jobURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    return jobReq.content

def getSSHsession():
    sshURL = "https://64.103.26.61:10000/job/service/webssh/803/cqjw-0591984a8"

    sshReq = requests.get(sshURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    return sshReq.content


#https://64.103.26.61:10000/job/service/webssh/803/cqjw-0591984a8


def deleteAllJobs():
    allJobs = getAllJobs()
    allIds = allJobs.keys()

    for i in allIds:
        id = i
        deletejobURL = "/jobs/%s" % id
        print baseURL + deletejobURL
        deleteReq = requests.delete(baseURL + deletejobURL,
                                    headers=baseHeaders,
                                    auth=(user, key),
                                    verify=False)
        print deleteReq


def delete1Lab(id):
    deletejobURL = "/jobs/%s" % id
    deleteReq = requests.delete(baseURL + deletejobURL,
                                headers=baseHeaders,
                                auth=(user, key),
                                verify=False)

    return deleteReq


def create1Lab(x_lab):
    createURL = "/jobs"
    direct = os.path.dirname(__file__)
    labfile = open(direct + "/cliqr_submitjob/devnet_n9kv_leaf_spine.json", "r")
    labJson = json.loads(labfile.read())

    labJson["name"] = "TopOTheMorning%d" % x_lab
    labJson['{{network}}'] = "ABC10-vlan100"

    labJson = json.dumps(labJson)

    createReq = requests.post(baseURL + createURL,
                              headers=baseHeaders,
                              data=labJson,
                              auth=(user, key),
                              verify=False)
    return createReq


class newLabThread(threading.Thread):
    def __init__(self, xlab):
        threading.Thread.__init__(self)
        self.xlab = xlab

    def run(self):
        #respCode = create1Lab(self.xlab)
        respCode = getAllJobs()
        print respCode
        print self.xlab


def create100LabsAll():
    threads = []
    for i in range(0, 100):
        create = newLabThread(i)
        create.setDaemon(True)
        threads.append(create)
        create.start()

    for thread in threads:
        thread.join()

def create100Labs():
    for i in range(0, 100):
        create1Lab(i)


def main():
    # create100Labs()
    # deleteAllJobs()
    # print getAllJobs()
    # print delete1Lab(797)

    # create1Lab(101)

    # print getJobDet(802)

    # print getSSHsession()

    newAPIkey(2)

    #create100LabsAll()


if __name__ == '__main__':
    main()



