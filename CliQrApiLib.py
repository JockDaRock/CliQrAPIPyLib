import requests
import json
import os

requests.packages.urllib3.disable_warnings()

baseURL = "https://<your URL / IP here >/v1"

baseHeaders = {"Accept": "application/json",
               "Content-Type": "application/json"}


#Drives the creation of a new API key. Once this is successfully called,
#the previous API key is revoked.
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


#Used to get the Job Detail of a Lab Environment or the Job a specific VM.
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


#Used to retrieve the Web SSH session URL to login to SSH through any browser window, if
#VM has SSH access enabled.
def getSSHsession(user, key, reqURL):
    sshURL = reqURL

    sshReq = requests.get(sshURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    sshResp = sshReq.json()
    ssh = sshResp["serverUrl"] + "/ssh.html?session=" + sshResp["sessionId"]

    return ssh


#Used to retrieve the Web VNC/RDP session URL to login to VNC/RDP through any browser window, if
#VM has VNC/RDP access enabled.
def getVNCsession(user, key, reqURL):
    vncURL = reqURL

    vncReq = requests.get(vncURL,
                          headers=baseHeaders,
                          auth=(user, key),
                          verify=False)

    vncResp = vncReq.json()
    vnc = vncResp["serverUrl"] + "/vnc.html?session=" + sshResp["sessionId"]

    return vnc


#Terminates all current running Jobs
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


#Deletes a specific Lab Environment by JobID
def deleteLab(user, key, id):
    deletejobURL = "/jobs/%s" % id
    deleteReq = requests.delete(baseURL + deletejobURL,
                                headers=baseHeaders,
                                auth=(user, key),
                                verify=False)

    return deleteReq


#Creation of Lab environment function using Pre-made json Response File
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


#Demo of functionality ran in main function
def main():
#The following credentials either have to be obtained through the Web GUI for CliQr or by providing
#Admin creds (also obtained through the GUI) and then using Admin creds to obtain individual creds.
    user = "YourUser"

    userid = "10000000"

    username = "YourUser@cliqrtech.com,1"

    passwd = "yourPassWord"

#API Key to be used for the duration of the program
    key = newAPIkey(username, passwd, userid)

#Lab creation using the createLab function
    labID = createLab("AdminTest1", user, key)

#Job detail of the newly created lab
    jsonResp = getJobDet(user, key, labID)

    numVMs = len(jsonResp["jobs"])
    jobIDs = []
    run = True

#populating jobIDs array with jobIDs representing each individual VM
    for i in range(0, numVMs):
        jobIDs.append(jsonResp["jobs"][i]["id"])

#for loop used to continually check whether individual VMs in Lab Environment are spun up
#and the once a VM is running the SSH web session URL is put together and printed to console.
#This will take some time and could be spun up on a separate thread if additional functionality
#to the main needs to be added.
    for i in jobIDs:
        vmStatus = isVMRunning(user, key, i)
        if vmStatus == "JobRunning":
            vmHostName = getJobDet(user, key, i)
            sshReq = "https://64.103.26.61:10000/job/service/webssh/%s/%s" % (i, vmHostName["virtualMachines"][0]["hostName"])
            guacSSH = getSSHsession(user, key, sshReq)
            print guacSSH
        else:
            jobIDs.append(i)

#Commented out delete section to terminate Lab Environment
    #print deleteLab(user, key, "1107")


if __name__ == '__main__':
    main()



