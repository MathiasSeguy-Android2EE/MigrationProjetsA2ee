"""" The class that represents the meta data of projects"""
import platform
from os import path
import sys
sys.path.insert(0, './ProjectDependencies')
import ProjectDependencies
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
NOT_DEFINED='NOT_DEFINED'
global SPLIT_CHARACTER

if platform.system() == "Windows":
    SPLIT_CHARACTER = '\\'
else:
    SPLIT_CHARACTER = '/'

class ProjectMeta:

    projectName="\"NOT_DEFINED\""
    projectPath="\"NOT_DEFINED\""
    applicationId="\"NOT_DEFINED\""
    versionCode=0
    versionName="\"NOT_DEFINED\""
    minSdkVersion="\"NOT_DEFINED\""
    dependencies=[]

    def __init__(self,directory):
        #https://stackoverflow.com/questions/10085590/how-to-make-empty-list-in-initial-attr-of-class
        self.dependencies=[]
        self.extractMeta(directory) 

    def __str__(self):
        name=self.projectName+', applicationId ='+self.applicationId+', versionCode='+str(self.versionCode)+", versionName="+self.versionName+", minSdkVersion="+str(self.minSdkVersion)
        # for dep in self.dependencies:
        #     name=name+'\n '+dep.type+', and raw:'+dep.rawValue
        return name

    def extractMeta(self,directory):        
        #open the file
        #read it line by line
        #when you find a key word, grab the value
        temp=path.split(path.abspath(directory))
        print(CYAN+"\t"+str(temp))
        if "\\app" in temp[0]:
            #you are inside the ProjectName\\app\\build.gradle
            #temp=('D:\\Git\\FormationAndroid2ee\\Formation_ICS_AS_2019\\ActionBarCompatSample2\\app', 'build.gradle')
            #find the subdir:
            subDir=temp[0].split('\\')[-1]
            self.projectPath=temp[0].replace('\\'+subDir,'')
            self.projectName=self.projectPath.split('\\')[-1]
            # print("Extracting1 name from "+directory+" => ["+str(temp)+"], SubDir="+subDir+", Path="+self.projectPath+", Name:"+self.projectName) #=>
            #Extracting1 name from D:\Git\Temp\Res\AmberTeam\app\build.gradle => [('D:\\Git\\Temp\\Res\\AmberTeam\\app', 'build.gradle')], SubDir=app, Path=D:\Git\Temp\Res\AmberTeam, Name:AmberTeam
        else:
            #you are inside the ProjectName
            #temp=('D:\\Git\\FormationAndroid2ee\\Formation_ICS_AS_2019\\ActionBarCompatSample2', 'build_gradle_eclipse_initial.legacy')
            self.projectPath=temp[0]
            self.projectName=self.projectPath.split('\\')[-1]
            # print("Extracting2 name from "+directory+" => ["+str(temp)+"], SubDir="+subDir+", Path="+self.projectPath+", Name:"+self.projectName)
        print(CYAN+"\tName: "+ self.projectName+", path="+self.projectPath)
        #open the build.gradle file
        build_gradle=open(directory)
        #and extract meta datav
        dependenciesBloc=False
        #the depth when reading dependencies in {}
        dependencyDepth=0
        #Now read the file and extract information
        for line in build_gradle:
            if(dependenciesBloc):
                #managing depth in {} bloc
                if '{' in line:
                    dependencyDepth=dependencyDepth+1
                elif '}' in line:
                    dependencyDepth=dependencyDepth-1
                if(dependencyDepth == 0):
                    dependenciesBloc=False
                else:
                    #you are in you implementation bloc
                    #grad you dependencies as this (too complex else)
                    self.dependencies.append(ProjectDependencies.Dependencies(line))
            else:
                if ' applicationId ' in line :
                    self.applicationId = self.extractValue(line)
                if ' minSdkVersion ' in line :
                    self.minSdkVersion = self.extractValue(line)
                if 'versionCode ' in line  :
                    self.versionCode = self.extractValue(line)
                if 'versionName ' in line :
                    self.versionName = self.extractValue(line)
                if 'dependencies' in line:
                    dependencyDepth=1
                    dependenciesBloc=True
        print(CYAN+"\t"+str(self))
        #check if you have the minSDKVersion, versionName, appId, versionCode
        #if they contain "project." you don't have the information
        if 'project.' in self.versionCode.lower():
            print(RED+'fuck you with your code versionCode : '+self.versionCode)
            #if value contains project. => find where it has been defined
            #most probable values are in //gradle/var_def or in ../build.gradle
            self.findExternalProperties(self.projectPath+'//app//gradle//var_definition.gradle')
        if 'project.' in self.versionCode.lower():
            print(RED+'2fuck you with your code versionCode : '+self.versionCode)
            #if value contains project. => find where it has been defined
            #most probable values are in //gradle/var_def or in ../build.gradle
            self.findExternalProperties(self.projectPath+'//build.gradle')
        
        if 'project.' in self.versionCode.lower():
            print(RED+'Applying default values for version to the project (minSDK, versionCode, versionName) : '+self.versionCode)
            self.minSdkVersion = '14'
            self.versionCode = 1
            self.versionName = '1'
        else:
            print(GREEN+'Have found versions of the project (minSDK, versionCode, versionName) : '+self.versionCode)


    def extractValue(self, line):
        value=line.split(' ')[-1].replace('\n','')
        #if value contains project. => find where it has been defined
        #most probable values are in //gradle/var_def or in ../build.gradle
        return value
    
    def findExternalProperties(self,fileName):
        print(CYAN+'trying to find in the project the versionCode : '+fileName)
        if(path.isfile(fileName)):
            print(CYAN+'Using the following file found')
            #open the build.gradle file
            file=open(fileName)
            #Now read the file and extract information
            for line in file:
                if ' applicationId ' in line :
                    self.applicationId = self.extractValue(line)
                if ' minSdkVersion ' in line :
                    self.minSdkVersion = self.extractValue(line)
                if 'versionCode ' in line  :
                    self.versionCode = self.extractValue(line)
                if 'versionName ' in line :
                    self.versionName = self.extractValue(line)
        else:
            print(RED+'File not found in project')

        print(CYAN+"\t"+str(self))

#Testing
# gradleBuildFile="D:\\Git\\FormationAndroid2ee\\DepartTPForecast\\MyPermierProjetInfomil\\app\\build.gradle"
# projectMeta= ProjectMeta(gradleBuildFile)