from sys import path
from AndroidXMigration import androidx_migration

from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
import os
import subprocess
from shutil import copyfile
from shutil import copytree
from shutil import rmtree
from shutil import move
from os import scandir
from os import remove
from os import path

ROOT_PYTHON_PATH=os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH=os.path.dirname(ROOT_PYTHON_PATH+'\\template_gradle\\')
REPO_NAME='not_set'
####################################################
# DEPRECATED CLASS
####################################################


def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
    func(path)

def migrateGradleBuildFile(repository,projectMetaData):
    print(RED+'\n\n\n\nStarting a new Migration\n-------------------------\n')
    print(RED+'Working dir:'+ repository)
    print(RED+'ROOT_PYTHON_PATH:'+ ROOT_PYTHON_PATH)
    #check if it's an Eclipse project
    if not path.isdir(repository+'\\src'):
        print(RED+"Not an eclipse project, returning")
        return
    global REPO_NAME
    REPO_NAME=repository.split('\\')[-1]
    print(RED+'RepoName is the following:'+ REPO_NAME)
    #First open the source gradle file
    buildGradle=repository+"\\app\\build.gradle"
    #Parse it and paste it in a temp file:
    #Need to find the file
    referentGradleBuildFile= open(buildGradle,"r")
    destinationFile=open(buildGradle+'_temp',"w+")
    #and update it according to our generic config file
    
    dependenciesBloc=False
    signingConfigBloc=False
    #the depth when reading dependencies in {}
    dependencyDepth=0
    signingConfigDepth=0
    for line in referentGradleBuildFile:
        #When reaching signing config, keep source
        if(dependenciesBloc):
            #managing depth in {} bloc
            if '{' in line:
                dependencyDepth=dependencyDepth+1
            elif '}' in line:
                dependencyDepth=dependencyDepth-1
            if(dependencyDepth == 0):
                #add the crashlitics and the junit blocs
                dependenciesBloc=False

            #Do the stuff: Log those you don't find in ref
            pass
        if(signingConfigBloc):

            #Probably a more general problem, linked with keystore: As to be handled by ProjMetaData

            #managing depth in {} bloc
            if '{' in line:
                signingConfigDepth=signingConfigDepth+1
            elif '}' in line:
                signingConfigDepth=signingConfigDepth-1
            if(signingConfigDepth == 0):
                signingConfigBloc=False

            #you are in signin in, just copy initial element from your ProjectMetaData
            # You also have this block later to handle :'(
            # buildTypes {
            #     release {
            #         signingConfig signingConfigs.release
            #         minifyEnabled true
            #         shrinkResources true
            #         useProguard true
            #         proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
            #         //add tests coverage using Jacoco
            #         testCoverageEnabled false
            #     }
            #     debug {
            #         // Run code coverage reports by default on debug builds.
            #         // testCoverageEnabled = true
            #         signingConfig signingConfigs.debug
            #         applicationIdSuffix '.debug'
            #         versionNameSuffix '.debug'
            #         //add tests coverage using Jacoco
            #         testCoverageEnabled true
            #         useProguard false
            #     }
            # }

            pass
        else:
            if 'dependencies' in line:
                dependencyDepth=1
                dependenciesBloc=True
            elif 'signingConfigs {' in line:
                signingConfigDepth=1
                signingConfigBloc=True
            #When reaching the dependencies block, use our own line if not already the good format
            #List all the unknown library
            #else copy line
            destinationFile.write(line)
    destinationFile.close
    referentGradleBuildFile.close

    #delete source, rename target as source
