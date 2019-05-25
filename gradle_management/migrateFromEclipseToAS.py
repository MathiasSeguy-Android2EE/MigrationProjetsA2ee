import sys
import migrateBuildGradle
from AndroidXMigration import androidx_migration

import os
import subprocess
from shutil import copyfile
from shutil import rmtree
from shutil import move
from os import scandir
from os import remove
from os import path
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN

ROOT_PYTHON_PATH=os.path.dirname(os.path.abspath(__file__))

TEMPLATE_PATH=os.path.dirname(ROOT_PYTHON_PATH+'\\template_gradle\\')
REPO_NAME='not_set'

def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
    func(path)

def migrateProject(repository):
    print(BLUE+'Starting the migration of the project\n-------------------------')
    print(BLUE+'Working dir:'+ repository)
    print(BLUE+'ROOT_PYTHON_PATH:'+ ROOT_PYTHON_PATH)
    global REPO_NAME
    REPO_NAME=repository.split('\\')[-1]
    print(BLUE+'RepoName is the following:'+ REPO_NAME)
    #manage Eclipse project
    if path.isdir(repository+'\\src'):        
        try:
            # create the folders app//src/java and mv src/res and Manifest
            print(BLUE+'Reshaping Project from Eclipse to A.S. files structure '+REPO_NAME)
            reshapeProject(repository)
            #Delete empty folders at root level and display a warning when one is not empty expect gradle and app
            print(BLUE+'Cleaning the repo by removing the empty folder (or build,...) '+REPO_NAME)
            cleanRootRepository(repository)    
        except Exception as e:
            print(e)
            print(RED+"Houston, we have a BIG problem, migrateProject->reshapeProject failed")
            return
        else:
            print(GREEN+"\t migrateProject>reshapeProject success")

    #migrate the project to androidX
    try:
        print(BLUE+'Migrate Build.gradle to AndroidX before analyzing them '+REPO_NAME)
        androidx_migration.migrateGradle(repository)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject->androidx_migration of build.gradle failed")
        return
    else:
        print(GREEN+"\t migrateProject>androidx_migration of build.gradle success")


    # Parse initial gradle to grab :Version and AppId and dependencies
    try:
        #This should generate the signin block and the dependency one.
        print(BLUE+'Parse initial gradle files of the project to extract the Project Information (dependencies, version, appId...) ')
        projectMetaData=parseOldGradleBuild(repository)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject->parseOldGradleBuild failed")
        return
    else:
        print(GREEN+"\t migrateProject>parseOldGradleBuild success. The reference of the project is in ram and its dependencies blocks is generated on disk")

    #create the project_referential.gradle and fill it
    try:
        print(BLUE+'Create the Project Referent File  '+REPO_NAME)
        createProjectRef(repository,projectMetaData)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject->createProjectRef failed")
        return
    else:
        print(GREEN+"\t migrateProject>createProjectRef success. The file project_reference.gradle is in the project")
    
    #CopyPaste all the gradle referents files
    try:
        print(BLUE+'Inject Gradle Template Files in the project '+REPO_NAME)
        injectGradleScript(repository)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject->injectGradleScript failed")
        return
    else:
        print(GREEN+"\t migrateProject>injectGradleScript success. Now your project has all the gradle files needed to be a killing project in terms of tooling")

    #migrate the project to androidX
    try:
        print(BLUE+'Start the AndroidX migration on the full project now '+REPO_NAME)
        androidx_migration.migrate(repository)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject->androidx_migration failed")
        return
    else:
        print(GREEN+"\t migrateProject>androidx_migration success. You know use the AndroidX libraries")
    
    #update build.gradle with dependencies of the project
    try:
        print(BLUE+'Update the build.gradle file of the project to inject the dependencies block (using the elements genrated before) '+REPO_NAME)
        migrateBuildGradle.updateGradleBuild(repository)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject->updateGradleBuild failed")
        return
    else:
        print(GREEN+"\t migrateProject>updateGradleBuild success. You are now able to compile your project")

    #check the licences
    try:
        print(BLUE+"Insure Licences are ok by running it and read the output to fix the package in live")
        migrateBuildGradle.insureLicencesYmlCompliant(repository)
        #delete temp file or rename them:build_gradle_eclipse_initial.legacy (else new change won't be token into account)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject->insureLicencesYmlCompliant failed")
        return
    else:
        print(GREEN+"\t migrateProject>insureLicencesYmlCompliant success. You are now able to build your project and check the licences")

#Move Src and Res folder in their AS location
#Move Manifest as well
def reshapeProject(repository):
    print(CYAN+'\nReshaping the project from Eclipse to A.S. structure')
    #Need to find the file
    if path.isdir(repository+'\\src'):
        move(repository+'\\src',repository+'\\app\\src\\main\\java')

    if path.isdir(repository+'\\res'):
        move(repository+'\\res',repository+'\\app\\src\\main\\res')

    if path.isfile(repository+'\\AndroidManifest.xml'):
        copyfile(repository+'\\AndroidManifest.xml',repository+'\\app\\src\\main\\AndroidManifest.xml')

#Delete the repository if it's empty one
def deleteIfEmpty(repository):
    dir_contents = [x for x in os.listdir(repository) if not x.startswith('.')]
    if len(dir_contents) == 0:
        rmtree(repository, ignore_errors=False, onerror=handleRemoveReadonly)

def isModuleBuildGradle(file):
    #Open and read the file
    fileInputStream = open(file, "r")
    for line in fileInputStream:
        if "buildScript {" in line:
            return False
        if "apply plugin: \'com.android.application\'" in line:
            return True



#Clean the root project
def cleanRootRepository(repository):
    print(CYAN+'\nCleaning Root repo from old eclipse folders')
    for file in scandir(repository):
        if file.is_dir():
            if file.name in 'bin' or file.name in 'gen'or file.name in 'libs' or file.name in 'build' or file.name in 'release' or file.name in 'delivery':
                rmtree(file, ignore_errors=False, onerror=handleRemoveReadonly)
            if file.name in 'assets':
                deleteIfEmpty(file)
        else:
            if file.name in '.classpath'or file.name in '.project' or file.name in 'AndroidManifest.xml':
                remove(file)

            if file.name in 'project.properties' or 'iml' in file.name :
                remove(file)
    if path.isfile(repository+'\\build.gradle'):
        #check if it's the gradle of the project or of the module
        if isModuleBuildGradle(repository+'\\build.gradle'):
            move(repository+'\\build.gradle',repository+'\\build_gradle_eclipse_initial.legacy')

#Parse the previous gradle.build and return associated MetaData using ProjectMeta object
def parseOldGradleBuild(repository):
    file=None
    needToRenameWhenOver =False
    if path.isfile(repository+'\\build_gradle_eclipse_initial.legacy'):
        file=(repository+'\\build_gradle_eclipse_initial.legacy')
        needToRenameWhenOver =False
    elif path.isfile(repository+'\\app\\build_gradle_eclipse_initial.legacy'):
        file=(repository+'\\app\\build_gradle_eclipse_initial.legacy')
        needToRenameWhenOver =False
    elif path.isfile(repository+'\\app\\build.gradle'):
        file=(repository+'\\app\\build.gradle')
    elif path.isfile(repository+'\\build.gradle'):
        file=(repository+'\\build.gradle')
    print(BLUE+'\nParsing the following Gradle file to extract meta data :'+str(file))
    if file != None:
        return migrateBuildGradle.migrateBuildGradle(file,repository,needToRenameWhenOver)
    else:
        return None

#Create the file project_reference.gradle below
#This is the Main information for the projectActionBarCompatSample2
# project.ext {
# 	 applicationId = "com.android2ee.formation.librairies.actionbar.compat"
# 	 versionCode = 1
# 	 versionName = "1.0"
# }
def createProjectRef(repository,projectMetaData):
    print(CYAN+'\nGenerating project_reference.gradle file')
    # git_init.listGitHubRepo()
    #Skip it if the file exist
    PathToPrjectReferenceFile = "\\app\\project_reference.gradle"
    if(path.isfile(repository+PathToPrjectReferenceFile)):
        print(RED+'.........................................Skiped, project already have this file')
        # File already exitst
        return
    #else   
    fh = open(repository+PathToPrjectReferenceFile, "w+")
    fh.write("/**This is the Main information for the project"+projectMetaData.projectName+'*/\n')
    fh.write("project.ext {"+"\n")

    fh.write("\t //The Id of the application\n")
    fh.write("\t applicationId = "+projectMetaData.applicationId+"\n")

    fh.write("\t //The version code, integer, can not decrease\n")
    fh.write("\t versionCode = "+str(projectMetaData.versionCode)+"\n")

    if(projectMetaData.versionName != None and len(projectMetaData.versionName.split('.'))>3):
        versionNameSet=projectMetaData.versionName.split('.')
        fh.write("\t //The majorVersion, To be increased for every major Release\n")
        fh.write("\t majorVersion = \""+versionNameSet[0]+"\"\n")

        fh.write("\t //The minorVersion,to be increased for every minor release\n")
        fh.write("\t minorVersion = \""+versionNameSet[1]+"\"\n")

        fh.write("\t //The buildNumber to increased for every build generation\n")
        fh.write("\t buildNumber = \""+versionNameSet[2]+"\"\n")

        fh.write("\t //The version name, can be anything, but will be generated\n")
        fh.write("\t versionName = majorVersion + '.' + minorVersion + '.' + buildNumber \n")
    elif projectMetaData.versionName == None :
        fh.write("\t //The majorVersion, To be increased for every major Release\n")
        fh.write('\t majorVersion = \"0\"\n')

        fh.write("\t //The minorVersion,to be increased for every minor release\n")
        fh.write("\t minorVersion = \"0\"\n")

        fh.write("\t //The buildNumber to increased for every build generation\n")
        fh.write("\t buildNumber = \"0\"\n")

        fh.write("\t //The version name, can be anything, but will be generated\n")
        fh.write("\t versionName = majorVersion + '.' + minorVersion + '.' + buildNumber\n")
    else:
        fh.write("\t //The majorVersion, To be increased for every major Release\n")
        fh.write('\t majorVersion = \"0\"\n')

        fh.write("\t //The minorVersion,to be increased for every minor release\n")
        fh.write("\t minorVersion = \"0\"\n")

        fh.write("\t //The buildNumber to increased for every build generation\n")
        fh.write("\t buildNumber = \""+projectMetaData.versionName.replace('\"','')+"\"\n")

        fh.write("\t //The version name, can be anything, but will be generated\n")
        fh.write("\t versionName = majorVersion + '.' + minorVersion + '.' + buildNumber\n")


    fh.write("\t//The gradle name to gather gradle task into the same sub folder\n")
    fh.write("\t myGradleGroup = \""+projectMetaData.projectName +"\"\n")
    
    fh.write("\t//The Name of the Project\n")
    fh.write("\t projectName = \""+projectMetaData.projectName +"\"\n")
    
    fh.write("}"+"\n")
    fh.close

#Copy the Gradle files from the the template to the project under migration
def injectGradleScript(repository):   
    print(CYAN+'\nCopying Gradle files to '+repository)
    forceCopyRecurse(TEMPLATE_PATH,repository)
#Recurse Copy the Gradle files from the the template to the project under migration
def forceCopyRecurse(src,dest):
    # print('Copying '+src+' to dest='+dest) 
    for file in scandir(src):
        if(os.path.isdir(file)):
            #check if exist at destination, else create
            if not path.isdir(dest+"\\"+str(file.name)):
                os.mkdir(dest+"\\"+str(file.name))
            #recurse
            forceCopyRecurse(src+"\\"+file.name,dest+"\\"+str(file.name))
            pass
        else:
            #copy the file
            copyfile(src+"\\"+file.name,dest+"\\"+str(file.name))
