#This file implment the rules to applyu to an Android project to know its state
#•	If it’s an Eclipse legacy project (files are not in the same structure)
# •	If it’s a git project (contains a .git folder)
# •	If it’s a module of a bigger project (an error I created when I had migrated my projects for the first time from Eclipse to AndroidStudio’s structure)
# •	Where is the root of the project (contains .gradle folder and build.gradle file)

from os import path
from os import scandir
import platform
global SPLIT_CHARACTER
if platform.system() == "Windows":
    SPLIT_CHARACTER = '\\'
else:
    SPLIT_CHARACTER = '/'
#To be a root Directory
#You contain:
# a .gradle folder and build.gradle file
# gradle.properties => root project
# To be a module directory (containing the source and the real build.gradle) AS compliant
#You contain
# a src folder, a build folder and a build.gradle file
#You are a module project Eclipse style
#You contain src res and AndroidManifest file
def isRootDirectory(directory):
    # list of names
    hasGradle=path.isdir(directory+SPLIT_CHARACTER+'.gradle')
    hasBuildGradle=path.isfile(directory+SPLIT_CHARACTER+'build.gradle')
    isRootProject= hasBuildGradle and hasGradle
    # if isRootProject:
    #     print(directory+'\n\t is a root project')
    return isRootProject

#Detect if you have a git init in your project
def isGitDirectory(directory):
    hasGit=path.isdir(directory+SPLIT_CHARACTER+'.git')
    return hasGit

#Detect if you have a ReadMe in your project
def isReadMeInTheProject(directory):
    hasReadMe=path.isfile(directory+SPLIT_CHARACTER+'README.md')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'readme.md')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'readMe.md')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'ReadMe.md')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'README.MD')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'readme.txt')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'readMe.txt')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'ReadMe.txt')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'README.TXT')
    hasReadMe=hasReadMe or path.isfile(directory+SPLIT_CHARACTER+'README.txt')
    return hasReadMe
#Detect if you have a license.txt in your project
def isLicenseSetOnTheProject(directory):
    hasLicenseSet=path.isfile(directory+SPLIT_CHARACTER+'LICENSE.txt')
    hasLicenseSet=hasLicenseSet or path.isfile(directory+SPLIT_CHARACTER+'LICENSE.TXT')
    hasLicenseSet=hasLicenseSet or path.isfile(directory+SPLIT_CHARACTER+'licence.txt')
    return hasLicenseSet

#Detect if you have a licenses.yml in your project
def isOSLicensesManagedByTheProject(directory):
    hasOSLicenseManaged=path.isfile(directory+SPLIT_CHARACTER+'app'+SPLIT_CHARACTER+'licenses.yml')
    return hasOSLicenseManaged

#Detect if you have a specific JKS in your project
def isJksInTheProject(directory):
    hasJKS=False 
    for file in scandir(directory):
        # print("Browsing "+file.name)
        if file.is_dir():
            hasJKS=hasJKS or isJksInTheProject(file)
        else:
            if '.jks' in file.name:
                hasJKS=True
                print("JKS file is here:"+file.path+"/"+file.name)
                break
    return hasJKS

#Detect if your project is AndroidStudio compliant
def isAndroidStudioCompliant(directory):
    hasApp=path.isdir(directory+SPLIT_CHARACTER+'app')
    hasSrc=False
    if hasApp:
        hasSrc=path.isdir(directory+SPLIT_CHARACTER+'app'+SPLIT_CHARACTER+'src')
    hasBuildGradle=path.isfile(directory+SPLIT_CHARACTER+'build.gradle')
    hasBuildApp=False
    if hasBuildGradle:
        hasBuildApp=path.isfile(directory+SPLIT_CHARACTER+'app'+SPLIT_CHARACTER+'build.gradle')

    #Legacy code
    # hasBuildFolder=path.isdir(directory+SPLIT_CHARACTER+'build')
    # hasApp=path.isdir(directory+SPLIT_CHARACTER+'app')
    # hasBuildGradle=path.isfile(directory+SPLIT_CHARACTER+'build.gradle')
    # if hasBuildGradle and hasApp and hasBuildFolder:
    #     print(directory+'\n\t isAndroidStudioCompliant, hasApp'+directory+SPLIT_CHARACTER+'app')
    return hasBuildGradle and hasApp  and hasSrc and hasBuildApp

#Detect if your project is in an Eclipse structure
def isEclipseLegacy(directory):
    hasRes=path.isdir(directory+SPLIT_CHARACTER+'res')
    hasSrc=path.isdir(directory+SPLIT_CHARACTER+'src')
    hasManifest=path.isfile(directory+SPLIT_CHARACTER+'AndroidManifest.xml')
    hasBuildGradle=path.isfile(directory+SPLIT_CHARACTER+'build.gradle')
    # if hasBuildGradle and hasSrc and hasRes and hasManifest:
    #     print(directory+'\n\t isEclipseLegacy')
    return hasBuildGradle and hasSrc and hasRes and hasManifest

#Detect if your project is a module of a bigger project
def isModulesCollection(directory):
    filePath=directory+SPLIT_CHARACTER+'settings.gradle'
    hasSetting=path.isfile(filePath)
    isModulesCollection=False
    if hasSetting:
        #read the file and list the modules in it
        settingContent= open(filePath,"r")
        for line in settingContent:
            cleanedLine=line.replace(" ","").replace("'","").replace(":app,","").replace("include","").replace(":","").replace("\n","")
            print(directory+'\n\t cleaned line ='+cleanedLine)
            isModulesCollection=isModulesCollection or len(cleanedLine.split(',')) > 1
        settingContent.close
    print(directory+'\n\t isModulesCollection ='+str(isModulesCollection))
    return isModulesCollection