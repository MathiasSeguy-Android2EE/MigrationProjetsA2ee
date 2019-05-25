#This file generates reports on the states of your projects.
#You can generates two types of reports : Global (generateGlobalState()) or ProjectByProject (listFileAndGenerate)
#If your run the script, both are generated

import platform
from os import path
from os import scandir
import sys 
sys.path.insert(0, './projectsRulesChecker')
import projectsRulesChecker as rules
sys.path.insert(0, './git_management/')
from git_management import git_init
sys.path.insert(0, './gradle_management/')
from gradle_management import manageSigninAndJks
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
global SPLIT_CHARACTER

if platform.system() == "Windows":
    SPLIT_CHARACTER = '\\'
else:
    SPLIT_CHARACTER = '/'

# Root directory of all your projects
PROJECT_DIR = "../../"

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
    "release"
]
#Elements used for Reporting
AndroidStudioCompliant=['']
EclipseLegacy=['']
NotRootProject=['']
GitNotSet=['']
MissingReadMe=['']
MissingLicenceTxt=['']
MissingOSLicensesManagement=['']
SpecificJks=['']
numberOfProject=0

#Sort my project according to the folowing elements:
#Skipped: This project has not to be maintained
#AndroidStudioCompliant projects : This project has to be maintained, AndroidStudio migrated
#EclipseLegacy project: This project has to be maintained, EclipseLegacy state
#GitNotSet: This project has not git
#ProjectsCollection: This projects contains sub project
def analyseProjectsRecurse(directory,fh):
    # if isRootDirectory(directory.path):
    #     print(directory.name+' is a root directory '+str(isRootDirectory(directory.path)))
    # print(directory.name+' is a final AndroidStudio module '+str(isAndroidStudioCompliant(directory.path)))
    # print(directory.name+' is a need to migrate Eclipse module running with gradle '+ str(isEclipseLegacy(directory.path)))
    # print(directory.name+' is a git directory '+str(isGitDirectory(directory.path)))
    global AndroidStudioCompliant
    global EclipseLegacy
    global NotRootProject
    global GitNotSet
    global MissingReadMe
    global MissingLicenceTxt
    global MissingOSLicensesManagement
    global SpecificJks
    global numberOfProject
    if not(rules.isAndroidStudioCompliant(directory.path) or rules.isEclipseLegacy(directory.path)) or rules.isModulesCollection(directory.path):
        #si ce n'est ni un As ni un Ec alors recurse
        for file in scandir(directory):
            if not any(substring in file.path for substring in exclude_package_list):
                if file.is_dir():
                    analyseProjectsRecurse(file,fh)
    else :
        global numberOfProject
        numberOfProject=numberOfProject+1
        fh.write(directory.path)
        if rules.isAndroidStudioCompliant(directory.path):
            # fh.write('\t isAndroidStudioCompliant\n')
            AndroidStudioCompliant.append(directory.path)
        if rules.isEclipseLegacy(directory.path):
            fh.write('\t isEclipseLegacy')
            EclipseLegacy.append(directory.path)
        if not rules.isGitDirectory(directory.path):
            fh.write('\t is not Git Repo')
            GitNotSet.append(directory.path)
        if not rules.isRootDirectory(directory.path):
            fh.write('\t is NOT RootDir')
            NotRootProject.append(directory.path)
        if not rules.isReadMeInTheProject(directory.path):
            fh.write('\t has NOT ReadMe')
            MissingReadMe.append(directory.path)
        if not rules.isLicenseSetOnTheProject(directory.path):
            fh.write('\t has NOT LICENSE.txt')
            MissingLicenceTxt.append(directory.path)
        if not rules.isOSLicensesManagedByTheProject(directory.path):
            fh.write('\t has NOT O.S. Licenses management')
            MissingOSLicensesManagement.append(directory.path)
        if rules.isJksInTheProject(directory.path):
            fh.write('\t has Specific JKS already defined')
            SpecificJks.append(directory.path)
            # manageSigninAndJks.manageSpecificJKS(directory.path)
        fh.write('\n')

#Detect if you have a specific JKS in your project
def getJksInTheProject(directory):
    for file in scandir(directory):
        # print("Browsing "+file.name)
        if file.is_dir():
            fileFound=getJksInTheProject(file)
            if fileFound != None:
                return fileFound
        else:
            if '.jks' in file.name:
                print("JKS file is here:"+file.path+"/"+file.name)
                return file
    return None

def analyseProjectsForGlobalState(directory,fh):    
    global AndroidStudioCompliant
    global EclipseLegacy
    global NotRootProject
    global GitNotSet
    global numberOfProject
    global MissingReadMe
    global MissingLicenceTxt
    global MissingOSLicensesManagement
    global SpecificJks
    AndroidStudioCompliant=['']
    EclipseLegacy=['']
    NotRootProject=['']
    GitNotSet=['']
    MissingReadMe=['']
    MissingLicenceTxt=['']
    MissingOSLicensesManagement=['']
    SpecificJks=['']
    numberOfProject=0
    fh.write('\n\nList of projects \n****************************\n')
    # print("Browsing "+directory)
    for file in scandir(directory):
        # print("Browsing "+file.name)
        if file.is_dir():
            # print("Recursing "+file.name)
            # isRootDirectory(file.path)
            # isPythonNC(file.path)
            analyseProjectsRecurse(file,fh)

    fh.write('\n\nReport \n****************************\n')
    fh.write('\nNumber of Projects='+str(numberOfProject))
    fh.write('\nNumber of Projects AndroidStudio Compliant with Git='+str(len(AndroidStudioCompliant)))
    fh.write('\nNumber of Projects EclipseLegacy                   ='+str(len(EclipseLegacy)))
    fh.write('\nNumber of Projects Without Git                     ='+str(len(GitNotSet)))
    fh.write('\nNumber of Projects in MultiModule                  ='+str(len(NotRootProject)))
    fh.write('\nNumber of Projects without ReadMe                  ='+str(len(MissingReadMe)))
    fh.write('\nNumber of Projects without Licenses.txt            ='+str(len(MissingLicenceTxt)))
    fh.write('\nNumber of Projects without OS Licenses Management  ='+str(len(MissingOSLicensesManagement)))
    fh.write('\nNumber of Projects with specific JKS               ='+str(len(SpecificJks)))

    fh.write('\n\nAndroidStudio projects\n****************************\n')
    for file in AndroidStudioCompliant:
        fh.write(file+'\n')
    fh.write('\n\nEclipseLegacy projects\n****************************\n')
    for file1 in EclipseLegacy:
        fh.write(file1+'\n')
    fh.write('\n\nGitNotSet projects\n****************************\n')
    for file in GitNotSet:
        fh.write(file+'\n')
    fh.write('\n\nNotRootProject projects\n****************************\n')
    for file in NotRootProject:
        fh.write(file+'\n')
    fh.write('\n\nMissing ReadMe projects\n****************************\n')
    for file in MissingReadMe:
        fh.write(file+'\n')
    fh.write('\n\nMissing LicenceTxt projects\n****************************\n')
    for file in MissingLicenceTxt:
        fh.write(file+'\n')
    fh.write('\n\nMissing OSLicenses Management projects\n****************************\n')
    for file in MissingOSLicensesManagement:
        fh.write(file+'\n')
    fh.write('\n\nWith Specific Jks projects\n****************************\n')
    for file in SpecificJks:
        fh.write(file+'\n')
        # manageSigninAndJks.logSigninConfig(file,fh)


# Get the state of the Projects in the following way:
# It generates a global vision of your workspace, sorted and clear with the following chapter:
# 1)The list of all project, with for each its state like this:
#    ../../FormationAndroid2ee\FormationInitiale_InitGui_AS\ActivityWithListMenuDialog	 isEclipseLegacy	 is not Git Repo	 is NOT RootDir
# 2)The report files
#    Report file
#    ****************************
#     Number of Projects=127
#     Number of Projects AndroidStudio Compliant with Git=43
#     Number of Projects EclipseLegacy                   =86
#     Number of Projects Without Git                     =109
#     Number of Projects in MultiModule                  =43
# 3)The list of AndroidStudio projects
# 4)The list of EclipseLegacy projects
# 5)The list of GitNotSet projects
# 6)The list of NotRootProject projects
def generateGlobalState():
    fh = open("GlobalProjectsStates.txt", "w+")
    analyseProjectsForGlobalState(PROJECT_DIR,fh)
    fh.close


# Get the state of the projects in the following way
# It lists all the projects, project by project. For each, provides the status
# Example1 for a normal project, lists its attributes:
# =>../../FormationAndroid2ee\FormationInitiale_InitGui_AS\CircleBar
#           has a problem with git
#           has a problem with the structure AS NOT COMPLICANT, eclipse project
# Example2 for a project containing modules, lists its modules:
# =>../../FormationAndroid2ee\FormationInitiale_InitGui_AS
# 			ActivityWithListMenuDialog
# 			AnalogicAndDigitalClock
# 			AppWidgetTuto
# 			CalendarViewTuto
def listFileAndGenerate(directory,fh):
    # print(BLUE+"Generating State Reports on "+directory)
    hasGradle=False
    hasGit=False
    hasBuildGradle=False
    hasSrc=False
    hasApp=False
    isRootProject=False    
    hasReadMe=False    
    hasLicense=False
    hasOSLicensesManagement=False
    hasJKS=False
    for f in scandir(directory):
        # fh.write("toto\n")
        if not any(substring in f.path for substring in exclude_package_list):
            # fh.write("john bob\n")
            if f.is_dir():
                # fh.write("john bobby\n")
                #recurse
                #check if the directory contains .gradle and .git and build.gradle
                for subFiles  in scandir(f):
                    if subFiles.name in ".gradle":
                        hasGradle=True
                    if subFiles.name in ".git":
                        hasGit=True
                    if subFiles.name in "build.gradle":
                        hasBuildGradle=True
                    if subFiles.name in "src":
                        hasSrc=True
                    if subFiles.name in "README.md":
                        hasReadMe=True
                    if subFiles.name in "LICENSE.txt":
                        hasLicense=True
                    if subFiles.name in "licenses.yml":
                        hasOSLicensesManagement=True
                    if ".jks" in subFiles.name:
                        hasJKS=True
                    if subFiles.name in "app":
                        hasApp=True
                    isRootProject= hasBuildGradle and hasGradle
                    if isRootProject and (hasSrc or hasApp):
                        break

                # fh.write("ahahah\n")
                # fh.write ('IsRoot project : '+str(isRootProject)+' hasGit'+str(hasGit)+' hasGradle'+str(hasGradle)+' hasBuildGradle'+str(hasBuildGradle)+'\n')
                if not isRootProject:
                    # print("listFileAndGenerate called with "+f.path+ "::" +f.name)
                    listFileAndGenerate(f.path,fh)
                else:
                    fh.write('=>'+f.path+'\n')
                    # fh.write('=>'+f.path+'--->'+f.name+'\n')
                    # print(BLUE+"\t"+f.path)

                    if(not hasGit):
                        # print(RED+"\tDamned It git not at the same level or no git defined")
                        fh.write('\t\t\t has a problem with git\n')
                    if(not hasReadMe):
                        # print(RED+"\tDamned It git not at the same level or no git defined")
                        fh.write('\t\t\t has a problem, missing ReadMe.md file\n')
                            
                    if(not hasLicense):
                        # print(RED+"\tDamned It git not at the same level or no git defined")
                        fh.write('\t\t\t has a problem, missing License.txt file\n')
                            
                    if(not hasOSLicensesManagement):
                        # print(RED+"\tDamned It git not at the same level or no git defined")
                        fh.write('\t\t\t has a problem with O.S. Licenses management\n')
                            
                    if(not hasJKS):
                        # print(RED+"\tDamned It git not at the same level or no git defined")
                        fh.write('\t\t\t has a speicifc JKS\n')

                    if(not hasApp):
                        # print(RED+"\tNo app folder, this is strange")
                        # fh.write('\t has a problem with the app folder not found => not A.S. compliant\n')
                        if(not hasSrc):
                            # print(RED+"\tNo src folder, this is strange")
                            fh.write('\t\t\t has a problem with the structure NO CODE\n')
                            #seems top directory
                            listFileAndGenerate(f.path,fh)
                        else:
                            # print(RED+"\tNo src folder, this is strange")
                            fh.write('\t\t\t has a problem with the structure AS NOT COMPLICANT, eclipse project\n')

                    for subFiles  in scandir(f):
                        if "settings.gradle" in subFiles.name :
                            settingContent= open(subFiles,"r")
                            for line in settingContent:
                                cleanedLine=line.replace(" ","").replace("'","").replace(":app,","").replace("include","").replace(":","").replace("\n","")
                                # print("\tcleanedLine "+cleanedLine)
                                for module in cleanedLine.split(','):
                                    fh.write("\t\t\t")
                                    fh.write(module)
                                    fh.write("\n")
                                if len(cleanedLine.split(',')) > 1:
                                    path=subFiles.path[0:(-1*len(subFiles.name))]
                                    listFileAndGenerate(path,fh)
                                    # for file in cleanedLine.split(','):
                                    #     fh.write("recursing call of "+file+" for path "+path)
                                    #     print("recursing call of "+path+file)
                                    #     listFileAndGenerate(path+file,fh)

                            settingContent.close
                        isRootProject= hasBuildGradle and hasGradle
                        # if isRootProject and (hasSrc or hasApp):
                        #     break

                hasGit=0
                hasBuildGradle=0
                hasGradle=0
                hasApp=0
                hasSrc=0


#Launching the script to test it
generateGlobalState()
fh = open("StatePerProject.txt", "w+")
listFileAndGenerate(PROJECT_DIR,fh)