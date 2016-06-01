import requests
import json
import os

requests.packages.urllib3.disable_warnings()

baseURL = "https://64.103.26.61:10000/v1"

baseHeaders = {"Accept": "application/json",
               "Content-Type": "application/json"}


def newAPIkey(un, pw, userid):

    keyURL = "/users/%s/keys" % userid
    keyHeaders = {"Content-Type": "application/json"}

    keyData = json.dumps({"apiKey": {"generate": True}})

    keyReq = requests.post(baseURL + keyURL,
                           headers=keyHeaders,
                           data=keyData,
                           auth=(un, pw),
                           verify=False)

    keyJson = keyReq.json()
    key = keyJson["apiKey"]["key"]

    return key


def getJobDet(user, key, id):
    jobURL = "/jobs/%s" % id
    jobReq = requests.get(baseURL + jobURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    return jobReq.json()


#This is only to be used when getting the status of a singular VM by the singlular VMs Job ID
def isVMRunning(user, key, id):
    toDeployOrNotToDeploy = getJobDet(user, key, id)

    return toDeployOrNotToDeploy["status"]


def getSSHsession(user, key, reqURL):
    sshURL = reqURL

    sshReq = requests.get(sshURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    sshResp = sshReq.json()
    ssh = sshResp["serverUrl"] + "/ssh.html?session=" + sshResp["sessionId"]

    return ssh


def getVNCsession(user, key, reqURL):
    vncURL = reqURL

    vncReq = requests.get(vncURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    vncResp = vncReq.json()
    vnc = vncResp["serverUrl"] + "/vnc.html?session=" + sshResp["sessionId"]

    return vnc


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


def deleteLab(user, key, id):
    deletejobURL = "/jobs/%s" % id
    deleteReq = requests.delete(baseURL + deletejobURL,
                                headers=baseHeaders,
                                auth=(user, key),
                                verify=False)

    return deleteReq


def createLab(LabName, user, key):
    createURL = "/jobs"

    direct = os.path.dirname(__file__)

    labfile = open(direct + "/cliqr_submitjob/devnet_n9kv_leaf_spine.json", "r")
    labJson = json.loads(labfile.read())

    labJson["name"] = LabName
    labJson['{{network}}'] = "ABC10-vlan100"

    labJson = json.dumps(labJson)

    createReq = requests.post(baseURL + createURL,
                              headers=baseHeaders,
                              data=labJson,
                              auth=(user, key),
                              verify=False)

    createResp = createReq.content
    print createResp

    createResp = createReq.json()
    labID = createResp["id"]

    return labID


def create10Labs():
    for i in range(0, 10):
        createLab(i)


def main():
    user = "cliqradmin"

    userid = "2"

    username = "admin@cliqrtech.com,1"

    passwd = "cliqr"

    key = newAPIkey(username, passwd, userid)

    """labID = createLab("AdminTest1", user, key)

    jsonResp = getJobDet(user, key, labID)

    numVMs = len(jsonResp["jobs"])
    jobIDs = []
    run = True

    for i in range(0, numVMs):
        jobIDs.append(jsonResp["jobs"][i]["id"])

    while run == True:
        for i in jobIDs:
            vmStatus = isVMRunning(user, key, i)
            if vmStatus == "JobRunning":
                vmHostName = getJobDet(user, key, i)
                sshReq = "https://64.103.26.61:10000/job/service/webssh/%s/%s" % (i, vmHostName["virtualMachines"][0]["hostName"])
                guacSSH = getSSHsession(user, key, sshReq)
                print guacSSH
            else:
                jobIDs.append(i)
        run = False"""

    print deleteLab(user, key, "1107")


if __name__ == '__main__':
    main()



