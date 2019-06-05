#https://python-jenkins.readthedocs.io/en/latest/examples.html#example-3-working-with-jenkins-jobs
import jenkins
import xml.etree.ElementTree as ET
from os import path
from sys import path as syspath
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
#Root variables
server=None
ROOT_PYTHON_PATH=path.dirname(path.abspath(__file__))
JENKINS_TEMPLATE_PATH=ROOT_PYTHON_PATH+"\\templates\\"

#Managing private account : the file jenkins_private_account.py is not in git
if path.isfile(ROOT_PYTHON_PATH+'\\jenkins_private_account.py'):
    import jenkins_private_account
    print(GREEN+" Private accounts for jenkins have been found. Using them.")
    GIT_ROOT_URL=jenkins_private_account.GIT_ROOT_URL
    jenkinsUrl = jenkins_private_account.jenkinsUrl
    jenkinsUserName = jenkins_private_account.jenkinsUserName
    jenkinsUserPassword = jenkins_private_account.jenkinsUserPassword
else:
    import getpass
    print(RED+" /!\\________Warning________/!\\")
    print(RED+" You have to create your accounts file:")
    print(RED+" ?\\MigrationProjectA2ee\\jenkins_management\\jenkins_private_account.py")
    GIT_ROOT_URL=input("What is the github root of the project. Ex: https://github.com/MyGithubName/ (don't include ProjectName, just parent directory.)\n")
    jenkinsUrl =input('What is the URL of your Jenkins server (Ex:myJenkinsUrl:8080)\n')
    jenkinsUserName = input('What is the JenkinsUserName to use?\n')
    jenkinsUserPassword = getpass.getpass(prompt='What is the JenkinsUserPassword associated with this account?\n')


def doaJenkinsStuff():
    global server
    if server==None:
        server = jenkins.Jenkins(jenkinsUrl, username=jenkinsUserName, password=jenkinsUserPassword)
    user = server.get_whoami()
    version = server.get_version()
    print('Hello %s from Jenkins %s' % (user['fullName'], version))

def launchAJob(jobName):
    global server
    if server==None:
        server = jenkins.Jenkins(jenkinsUrl, username=jenkinsUserName, password=jenkinsUserPassword)
    server.build_job(jobName)

def listJobs():
    global server
    if server==None:
        server = jenkins.Jenkins(jenkinsUrl, username=jenkinsUserName, password=jenkinsUserPassword)
    jobs = server.get_jobs()
    for job in jobs:
        job_name = job['name']
        job_config = server.get_job_config(job_name)
        job_file = open("D:\\Git\\Temp\\"+job_name + '.xml', 'w+')
        job_file.write(job_config)
        job_file.close()

#Convert xml file to string
def convert_xml_file_to_str(xmlPath):
    tree = ET.parse(xmlPath)
    root = tree.getroot()
    return ET.tostring(root, encoding='utf8', method='xml').decode()
#Create a job based on generic Jenkins file
#name:Amber
#branch:master
#tasks: clean build
#It will create a job linked to this github repo:
#gitUrl:https://github.com/MathiasSeguy-Android2EE/name/ (GIT_ROOT_URL+name+"/")
def createJob(name,branch,tasks):
    global server
    if server==None:
        server = jenkins.Jenkins(jenkinsUrl, username=jenkinsUserName, password=jenkinsUserPassword)
    # Create your xml file
    xmlConfig=convert_xml_file_to_str(JENKINS_TEMPLATE_PATH+"generic_jenkins_job.xml")
    xmlConfig=xmlConfig.replace("#Description_A2ee","This job is the job which ensures the project "+name+" is building")
    xmlConfig=xmlConfig.replace("#GitHubUrl_A2ee",GIT_ROOT_URL+name+"/")
    xmlConfig=xmlConfig.replace("#Name_A2ee",name)
    xmlConfig=xmlConfig.replace("#BRANCH_NAME",branch)
    xmlConfig=xmlConfig.replace("#TASKS",tasks)
    if server.job_exists(name):
        server.reconfig_job(name, xmlConfig)
    else:
        server.create_job(name, xmlConfig)

def createLinkedJob(currentJob,parentJob,childJob):
    #according to the context find the good template
    if parentJob == None:
        xmlConfig=convert_xml_file_to_str(JENKINS_TEMPLATE_PATH+"generic_jenkins_job_with_child.xml")
    elif childJob == None:
        xmlConfig=convert_xml_file_to_str(JENKINS_TEMPLATE_PATH+"generic_jenkins_job_withparent.xml")
    else:
        xmlConfig=convert_xml_file_to_str(JENKINS_TEMPLATE_PATH+"generic_jenkins_job_with_child_and_parent.xml")
    #Inject the variable into the generic script        
    xmlConfig=xmlConfig.replace("#Description_A2ee","This job is the job which ensures the project "+currentJob.name+" is building")
    xmlConfig=xmlConfig.replace("#GitHubUrl_A2ee",GIT_ROOT_URL+currentJob.name+"/")
    xmlConfig=xmlConfig.replace("#Name_A2ee",currentJob.name)
    xmlConfig=xmlConfig.replace("#BRANCH_NAME",currentJob.branch)
    xmlConfig=xmlConfig.replace("#TASKS",currentJob.tasks)
    if childJob != None:
        xmlConfig=xmlConfig.replace("#ChildName",childJob.name)
    if parentJob != None:
        xmlConfig=xmlConfig.replace("#ParentName",parentJob.name)
    #Create the job on the server    
    global server
    if server==None:
        server = jenkins.Jenkins(jenkinsUrl, username=jenkinsUserName, password=jenkinsUserPassword)
    # Create your xml file
    if server.job_exists(currentJob.name):
        server.reconfig_job(currentJob.name, xmlConfig)
    else:
        server.create_job(currentJob.name, xmlConfig)
    print(GREEN+"Job "+currentJob.name+" created")


def createLinkedJobs(jenkinsJobs):
    global server
    if server==None:
        server = jenkins.Jenkins(jenkinsUrl, username=jenkinsUserName, password=jenkinsUserPassword)
    # 
    i=0
    parentJob=None
    childJob=None
    print(BLUE+"Starting Jenkins job creation")
    while i < len(jenkinsJobs):
        currentJob=jenkinsJobs[i]
        if i == 0:
            parentJob=None
        else:
            parentJob=jenkinsJobs[i-1]
        if i < len(jenkinsJobs)-1:
            childJob=jenkinsJobs[i+1]
        else:
            childJob=None
        createLinkedJob(currentJob,parentJob,childJob)
        i=i+1
    # print("Jenkins jobs creation is done")
    # print("Launching first job of the chain")
    launchAJob(jenkinsJobs[0].name)
    print(GREEN+"All jobs has been created. Chain of build has been launched.")


# createJob("MultiplicationBasile","master","clean build")
# listJobs()
print("Test")