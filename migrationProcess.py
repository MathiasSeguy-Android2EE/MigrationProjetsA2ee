#/***********************************************************
# Input, you should update the following attributes of this file :
# exclude_package_list : The directory to exclude from the process
# PROJECT_DIR : The directory to scan and migrate
# PROJECT_TARGET : The target directory for the migrated projects destination
# 
# This file is the Migration full process, so it will:
# Generate StateReports
# Browse each project in the root directory, for each it will
# 0 Move it to its target
# 0.1 Clean the source
# 0.2 Delete the target
# 0.3 Copy the source to the target
# 
# 1 Git
# 1.1 init and set the git.ignore
# 1.1 Git Add all
# 1.2 Git commit
# 
# 2 Migrate the project
# 2.1   Initialize Errors
# 2.2.	Manage Eclipse project
# 2.3.	Migrate the project to AndroidX (first migration, only the classes are migrated)
# 2.4.	Parse intial gradle file to extract information (ApplicationId, Dependencies and SigningConfig) and generate “projectMetaData”
# 2.5.	write this “projectMetaData” information in a file called “project_reference.gradle”
# 2.6.	Paste in the project the generic gradles files
# 2.7.	Migrate to AndroidX again (in fact only the build.gradle file will be impacted)
# 2.8.	Update your build with the specific dependencies you have found for this project
# 2.9.	Check for the open source licences
# 2.10.	Gradlew cleanBuildCache (to clear the previous script)
# 2.11.	Gradlew build to know if the project compile
# 2.12. Gradlew clean on the target
# 
# 3 Git again
# 3.1 Git add
# 3.2 Git commit
# 3.3 git push to github (todo public or private)
# 
# 4 Jenkins 
# 4.1 Push to Jenkins (create the job)
# 4.2 Launch the build
# Display the migration report
# Run the Generate StateReports script on the target
#********************************************************/
import platform
from os import path,makedirs,scandir
import sys 
import projectsRulesChecker as rules
from git_management import git_init
import migration
from sys import path as syspath
syspath.insert(0, './jenkins_management')
from jenkins_management import jenkinsTools
import generatesStateReports
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
from jenkins_management import JenkinsJob


global SPLIT_CHARACTER

if platform.system() == "Windows":
    SPLIT_CHARACTER = '\\'
else:
    SPLIT_CHARACTER = '/'

# Root directory of all your projects
# PROJECT_DIR = "D:\Git\Temp\Res"
# PROJECT_TARGET = "D:\Git\Temp\R"
PROJECT_DIR = "D:\Git"
PROJECT_TARGET = "D:\GitM"

# Packages to exclude in the PROJECT_DIR
exclude_package_list = [
    "ACMS",
    "ProjetsExternes",
    "OthersSamples",
    "ToNotUse_A2EE_FInit_AS_fullprojects",
    "Android2EE_FInit_Eclipse",
    ".git",
    "build",
    "generated",
    "release",
    "migrationLogFile.txt"
]
#Elements used for Reporting
AndroidStudioCompliant=['']
EclipseLegacy=['']
NotRootProject=['']
GitNotSet=['']
jenkinsJobs=[]
numberOfProject=0

killer=0

def migrationRecurse(sourceDirectory,targetDirectory):
    # if isRootDirectory(directory.path):
    #     print(directory.name+' is a root directory '+str(isRootDirectory(directory.path)))
    # print(directory.name+' is a final AndroidStudio module '+str(isAndroidStudioCompliant(directory.path)))
    # print(directory.name+' is a need to migrate Eclipse module running with gradle '+ str(isEclipseLegacy(directory.path)))
    # print(directory.name+' is a git directory '+str(isGitDirectory(directory.path)))
    global killer
    if killer==2:
        return
    if not(rules.isAndroidStudioCompliant(sourceDirectory) or rules.isEclipseLegacy(sourceDirectory)) or rules.isModulesCollection(sourceDirectory):
        #si ce n'est ni un As ni un Ec alors recurse
        for file in scandir(sourceDirectory):
            if not any(substring in file.path for substring in exclude_package_list):
                if file.is_dir():
                    targetProjectPath=file.path.replace(sourceDirectory,targetDirectory)
                    migrationRecurse(file.path,targetProjectPath)
    else :
        killer=killer+1
        #This is an android project
        REPO_NAME = targetDirectory.split('\\')[-1]
        print(BLUE + "Starting the process of migration with: ")
        print("\tSource : "+sourceDirectory)
        print("\tTarget : "+targetDirectory)
        print("\tREPO_NAME : "+REPO_NAME)
        #0. Copy source to target
        migration.moveSourceToTarget(sourceDirectory,targetDirectory)
        # #1. Git
        git_init.gitInit(targetDirectory)
        # #2. Migrate the project
        migration.migrateTarget(targetDirectory)
        # #3. Git commit and Git push
        git_init.commitAll(targetDirectory,"First commit after migration of may 2019")
        git_init.gitCreateAndPush(targetDirectory,"This is the repository for the Android2ee's project "+REPO_NAME)
        #4. Jenkins
        global jenkinsJobs
        job=JenkinsJob.JenkinsJob(REPO_NAME,'master','clean build')
        jenkinsJobs.append(job)

logToFile=False
def launchMigrationProcess(sourceDirectory,targetDirectory):    
    if not path.exists(targetDirectory):
        makedirs(targetDirectory, mode=0o777)
    if(logToFile):
        original = sys.stdout
        sys.stdout = open(targetDirectory+'/migrationLogFile.txt', 'w+')

    #Take your start picture
    # fileStates = open(targetDirectory+"/InitialStatePerProject.txt", "w+")
    # generatesStateReports.listFileAndGenerate(sourceDirectory,fileStates)   
    # fileStates.close()
    # fileGlobalState = open(targetDirectory+"/InitialGlobalState.txt", "w+") 
    # generatesStateReports.analyseProjectsForGlobalState(sourceDirectory,fileGlobalState)
    # fileGlobalState.close()

    #Browse the source directory
    for f in scandir(sourceDirectory):
        # fh.write("toto\n")
        if not any(substring in f.path for substring in exclude_package_list) and path.isdir(f):
           targetProjectPath=f.path.replace(sourceDirectory,targetDirectory)
           migrationRecurse(f.path, targetProjectPath)
    #Create your linked JenkinsJobs
    print(BLUE + "Starting creating Jenkins Jobs: ")
    createJenkinsJobs()
    #Take your final picture
    fileStates = open(targetDirectory+"/FinalStatePerProject.txt", "w+")
    generatesStateReports.listFileAndGenerate(targetDirectory,fileStates)   
    fileStates.close()
    fileGlobalState = open(targetDirectory+"/FinalGlobalState.txt", "w+") 
    generatesStateReports.analyseProjectsForGlobalState(targetDirectory,fileGlobalState)
    fileGlobalState.close()    
    if(logToFile):
        sys.stdout = original

def createJenkinsJobs():
    global jenkinsJobs
    try:
        jenkinsTools.createLinkedJobs(jenkinsJobs)
    except Exception as e: print(e)

launchMigrationProcess(PROJECT_DIR,PROJECT_TARGET)