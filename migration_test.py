from sys import path, stdout
path.insert(0, './git_management')
path.insert(0, './gradle_management')
from git_management import git_init
from gradle_management import migrateFromEclipseToAS
from os import path
from os import scandir
from os import remove
import migration
import errno, os, stat, shutil
import subprocess
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
from shutil import copytree, ignore_patterns
from colorama import init,deinit


def cleanAmberProject(sourceDirectory):    
    for file in scandir(sourceDirectory):
        if path.isdir(file):
            cleanAmberProject(file)
        else:
            if "AmberProblem.txt" in file.name:
                os.remove(file)



#Code of the class
init()

#Constants: Application under test
ActionBarCompatSampleDir='D:\\Git\\FormationAndroid2ee\\Formation_ICS_AS\\ActionBarCompatSample'
AmberDir='D:\\Git\\MyProjets\\AmberTeam'
ChronoDir='D:\\Git\\FormationAndroid2ee\\FormationInitiale_InitGui_AS\\ChronoTuto'
ForecastDir='D:\\Git\\MyProjets\\ForecastYahooRest\\ForecastRestWithLibs'
MyLightDir='D:\\Git\\MyProjets\\MyLight'
FtagDir='D:\\Git\\ProjetsExternes\\Tag\\ft_ag_app'
    
ActionBarCompatSampleTarget='D:\\Git\\Temp\\Res\\ActionBarCompatSample'
AmberTarget='D:\\Git\\Temp\\Res\\AmberTeam'
ChronoTarget='D:\\Git\\Temp\\Res\\ChronoTuto'
ForecastTarget='D:\\Git\\Temp\\Res\\ForecastRestWithLibs'
MyLightTarget='D:\\Git\\Temp\\Res\\MyLight'
FtagTarget='D:\\Git\\Temp\\Res\\ft_ag_app'


#Launch your test on your targets
print(BLUE+"#############################################")
print(GREEN+"#############################################")
print(RED+"#############################################")
print(CYAN+"#############################################")
print(BOLD+"Starting the migration of the elements")
print(BLUE+"#############################################")
print(GREEN+"#############################################")
print(RED+"#############################################")
print(CYAN+"#############################################\n\n")
errorFound=['list of errors']
successFound=['list of working project']

# cleanAmberProject(AmberDir)
# launchTest(FtagDir,FtagTarget)

result=migration.migrate(ActionBarCompatSampleDir,ActionBarCompatSampleTarget)#Works fine
successFound=successFound+result[0]
errorFound=errorFound+result[1]

result=migration.migrate(AmberDir,AmberTarget)#Failed: AndoidxMigration failed with android.support.design and projectName and myGradleGroupd are Res :(
successFound=successFound+result[0]
errorFound=errorFound+result[1]

result=migration.migrate(ChronoDir,ChronoTarget)#Fine
successFound=successFound+result[0]
errorFound=errorFound+result[1]

result=migration.migrate(ForecastDir,ForecastTarget)#Could not find unknown properties versionCode
successFound=successFound+result[0]
errorFound=errorFound+result[1]

result=migration.migrate(MyLightDir,MyLightTarget)#Fine
successFound=successFound+result[0]
errorFound=errorFound+result[1]
print(BLUE+'final result :')
#https://stackoverflow.com/questions/37340049/how-do-i-print-colored-output-to-the-terminal-in-python/37340245
for elem in successFound:
    print(GREEN+elem)
for elem in errorFound:
    print(RED+elem)
print(RESET)

deinit()
#This is the step2:Pushing every one in GitHub
# git_init.gitInit(targetDir)
