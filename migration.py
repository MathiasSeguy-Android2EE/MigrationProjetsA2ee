from sys import path, stdout
path.insert(0, './git_management')
path.insert(0, './gradle_management')
from git_management import git_init
from gradle_management import migrateFromEclipseToAS
import errno, os, stat, shutil
import subprocess
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
from shutil import copytree, ignore_patterns
from colorama import init,deinit
init()
#Tracking the process behavior

#This is the process for migrating properly an Eclipse project to an Android Studio Project
#GradleManagemnt
def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
    func(path)

errorFound=['']
successFound=['']
#This method migrate any AndroidProject to the last up to date Android Project structure
# gradle.clean the sourceDirectory
# Delete previous target directory if it exists
# Create the target project directory and paste the initial project in it
# Migrate the target project to the new structure (the core of the work is done here)
# gradle.CleanBuildCache the tagrget directory to be sure it's up to date
# gradle.build on the target directory to be sure migration is ok
def migrate(sourceDirectopy,targetDirectory):
    global errorFound
    global successFound
    print(GREEN+"#############################################")
    print(GREEN+"Start migrating the following project:"+sourceDirectopy)
    print(BLUE+"#############################################")
    print(GREEN+"#############################################")
    moveSourceToTarget(sourceDirectopy,targetDirectory)
    #run migration on the copy
    return migrateTarget(targetDirectory)

#This method migrate any AndroidProject to the last up to date Android Project structure
# Migrate the target project to the new structure (the core of the work is done here)
# gradle.CleanBuildCache the tagrget directory to be sure it's up to date
# gradle.build on the target directory to be sure migration is ok
def migrateTarget(targetDirectory):
    global errorFound
    global successFound
    #run migration on the copy
    try:
        print(BLUE+"Start migrating the target directory("+targetDirectory+") to our new shape ")
        migrateFromEclipseToAS.migrateProject(targetDirectory)
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, migrateProject failed")
        errorFound.append(targetDirectory)
        return [successFound,errorFound]
    else:
        print(GREEN+"MigrateProject is done with success")
    
    #CleanBuildCache before building
    try:           
        print(BLUE+"Runnning CleanCache on "+targetDirectory)
        cleanBuildCache=subprocess.check_output([targetDirectory+"\\gradlew.bat", "cleanBuildCache"], cwd=targetDirectory,
        stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        print(RED+"CleanBuildCache has failed with "+str(exc))
        elementsAsList=exc.output.split('\n')
        print("The stacktrace has "+str(len(elementsAsList))+" elements")
        for line in elementsAsList:
            print(line)
    else:
        print(GREEN+"CleanBuildCache is done with success")
    
    #Run a build on the project
    try:
        print(BLUE+"Runnning build on "+targetDirectory)
        buildTask=subprocess.check_output([targetDirectory+"\\gradlew.bat", "build"], cwd=targetDirectory,
            stderr=subprocess.STDOUT, shell=True, universal_newlines=True)    
        #proc = subprocess.run([targetDirectory+"\\gradlew.bat", "build"], cwd=targetDirectory)
        #0 worked fine
        #not 0 had a problem
        #print('The Build result is the following '+str(proc.returncode)+'\n')
    except subprocess.CalledProcessError as exc:
        errorFound.append(targetDirectory)     
        print(RED+"BuildTask has failed with "+str(exc))
        elementsAsList=exc.output.split('\n')
        print("The stacktrace has "+str(len(elementsAsList))+" elements")
        printIt=False
        for line in elementsAsList:
            printIt=True
            if 'FAILED' in line:
                printIt=True
            if printIt:
                print(RED+line)   
    else:            
        print(GREEN+"BuildTask is a SUCCESS")
        stdout.write(RESET)
        successFound.append(targetDirectory)
    finally:
        return [successFound,errorFound]


#Move the source directory to its target
#Clean=>Delete=>Copy
def moveSourceToTarget(sourceDirectopy,targetDirectory):
    global errorFound
    global successFound
    #clean source
    if os.path.isfile(sourceDirectopy+"\\gradlew.bat"):
        print(BLUE+"Runnning clean on "+sourceDirectopy+"\\gradlew")
        # cleanTaks = subprocess.run([sourceDirectopy+"\\gradlew.bat", "clean"], cwd=sourceDirectopy) 
        try:           
            cleanTaks=subprocess.check_output([sourceDirectopy+"\\gradlew.bat", "clean"], cwd=sourceDirectopy,
                stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            print(RED+"Clean has failed with "+str(exc))
            errorFound.append(targetDirectory)
            #Don't return keep going
        else:
            print(GREEN+"Clean is done with success")

    #delete previous copy if exists
    if os.path.isdir(targetDirectory):
        try:
            print(BLUE+"Deleting the target directory: "+targetDirectory)
            shutil.rmtree(targetDirectory, ignore_errors=False, onerror=handleRemoveReadonly)
        except Exception as e: 
            print(e)
            print(RED+"Houston, we have a problem, RmTree failed on "+targetDirectory)
            errorFound.append(targetDirectory)
            return [successFound,errorFound]
        else:
            print(GREEN+"RmTree is done with success on "+targetDirectory)
    # else:
    #     os.makedirs(targetDirectory,0o777)

    #copy target
    try:        
        print(BLUE+"Creating the target directory "+targetDirectory)
        shutil.copytree(sourceDirectopy, targetDirectory,ignore=ignore_patterns('release/**.*', '*.html','build/**.*','delivery/**.*','SnapshotDB/**.*','doc'))
    except Exception as e: 
        print(e)
        print(RED+"Houston, we have a BIG problem, copyTree failed with "+targetDirectory)
        errorFound.append(targetDirectory)
        return [successFound,errorFound]
    else:
        print(GREEN+"CopyTree is done with success "+targetDirectory)
    