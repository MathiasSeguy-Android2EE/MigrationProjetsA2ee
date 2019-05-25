#This file is used in android Migration to create thereferential files of the migration
#It use the csv file provided by google
#And create list of (pair,value) where pair is the old package and value is the new package
#It has to handle the one for the class and the one for the class path (build.gradle)
#It also generate the file for versionning
from sys import path

import os
import subprocess
from shutil import copyfile
from shutil import copytree
from shutil import rmtree
from shutil import move
from os import scandir
from os import remove
from os import path
from collections import defaultdict,OrderedDict

#Defining console style for print output
RED   = "\033[1;31;40m "  
GREEN = "\033[0;32;40m "
BLUE  = "\033[1;34;40m "    
REVERSE = "\033[;7;40m "
CYAN  = "\033[1;36;40m "
RESET = "\033[0;0;40m "
BOLD    = "\033[;1;40m "

ROOT_PYTHON_PATH=os.path.dirname(os.path.abspath(__file__))

#Parse the files from Google and create
#1)The python mapping file for class
#2)The python mapping file for artefact
#3)The python mapping file for versionning
def migrateCsvToPython():    
    print(BLUE+'We are creating Python file for the mapping of the artefact and the classes for AndroidX migration.')
    print(BLUE+'We are here '+ROOT_PYTHON_PATH)
    initialArtifactCsv= open(ROOT_PYTHON_PATH+"\\androidx-artifact-mapping.csv","r")
    initialClassCsv= open(ROOT_PYTHON_PATH+"\\androidx-class-mapping.csv","r")
    pythonMappingFile=open(ROOT_PYTHON_PATH+'\\androidx_mapping.py',"w+")
    libVersionMappingFile=open(ROOT_PYTHON_PATH+'\\dependency_lib_version.py',"w+")
    #TODO insure you have the last version of the lib (you should donwload the csv files from the web)

    #Because sometimes you have elements contains in others elements like this:
    #android.support.v17.leanback.widget.Grid,androidx.leanback.widget.Grid
    #android.support.v17.leanback.widget.GridLayoutManager,androidx.leanback.widget.GridLayoutManager
    #you have to sort your key from biggest to smaller in terms of letters so you avoid the problem
    #To make this sort I use HashMap(Number of letters, list of lines)
    hashKeySizeToSentencesList=defaultdict(list)
    
    #Artifact generation
    #You need to migrate from:
    #android.arch.core:common,androidx.arch.core:core-common:2.0.0-rc01
    #to
    #('android.arch.core.executor.AppToolkitTaskExecutor','androidx.arch.core.executor.AppToolkitTaskExecutor')
    pythonMappingFile.write("findreplace = [\n")
    libVersionMappingFile.write("findreplace = [\n")
    for line in initialArtifactCsv:
        # if ',androidx.' in line or ',com.' in line :
        #la taille du bloc version :android.arch.core:common,androidx.arch.core:core-common:2.0.0-rc01
        #c'est la taille de 2.0.0-rc01 plus 1  
        # #version should be (core-common:2.0.0-rc01)      
        print(CYAN+"line.split(':')="+str(line.split(':')))
        if len(line.split(':')) > 2:
            #write the python mapping
            versionSize=-1*(len(line.split(':')[-1])+1)
            mappingLine='\t(\''
            mappingLine=mappingLine+line[:versionSize].replace(',','\',\'')
            mappingLine=mappingLine+('\'),\n')
            hashKeySizeToSentencesList[len(line.split(',')[0])].append(mappingLine)
            #write the version mapping
            version=line.split(':')[-1].replace('\n','')
            nickName=getVersionName(line)
            libVersionMappingFile.write('\t(\'')
            libVersionMappingFile.write(nickName+'\',\''+version)
            libVersionMappingFile.write('\'),\n')
        else:
            #not a normal line
            pass
    print(BLUE+"Aretfact migration to AndroidX is done")

    #Class generation
    #You need to migrate from:
    #android.support.design.widget.CollapsingToolbarLayout,com.google.android.material.appbar.CollapsingToolbarLayout
    #to
    #('android.support.design.widget.CollapsingToolbarLayout','com.google.android.material.appbar.CollapsingToolbarLayout')
    for line in initialClassCsv:
        # if ',androidx' in line:
        mappingLine='\t(\''
        mappingLine=mappingLine+line.replace(',','\',\'').replace('\n','')
        mappingLine=mappingLine+'\'),\n'
        hashKeySizeToSentencesList[len(line.split(',')[0])].append(mappingLine)    
    print(BLUE+"Classes migration to AndroidX is done")

    #Now write all those elements in order in the file
    for elem in sorted(hashKeySizeToSentencesList.keys(), reverse=True):
        for line in hashKeySizeToSentencesList[elem]:
            pythonMappingFile.write(line)
            print(str(elem)+"=>"+line.replace('\n',''))
    print(BLUE+"Writing all in the file is done")

    pythonMappingFile.write("\t(\'over:over:over:choupy\',\'job:is:done\')\n")
    pythonMappingFile.write("]\n")
    pythonMappingFile.close()
    libVersionMappingFile.write("\t(\'over:over:over:choupy\',\'job:is:done\')\n")
    libVersionMappingFile.write("]\n")
    libVersionMappingFile.close()
    initialArtifactCsv.close()
    initialClassCsv.close()

# Parameter: full coordinates androidx.test:runner:31.4
# Result:
# androidTestImplementation "androidx.test:runner:${runnerVersion}"
# androidTestImplementation "androidx.test.espresso:espresso-core:${espressoVersion}"
# implementation "androidx.appcompat:appcompat:${androidXVersion}"
# implementation "com.google.android.material:material:${androidXMaterial}"
# implementation "androidx.gridlayout:gridlayout:${androidXVersion}"
# implementation "androidx.cardview:cardview:${androidXVersion}"
# implementation "androidx.constraintlayout:constraintlayout:${androidXVersionConstraints}" 
def getVersionName(libCoordonate):
    #"${"+dependency.coordinate.split(':')[-2].replace('-','_')+'Version}"
    #NormalizeGroupId
    groupIdRaw=libCoordonate.split(':')[-3]
    groupId=''
    nextOneIsUpperCase=False
    for char in groupIdRaw:
        if nextOneIsUpperCase:
            groupId=groupId+char.upper()
            nextOneIsUpperCase=False
        elif '.' in char or '_' in char or '-' in char:
            nextOneIsUpperCase=True
        else:
            groupId=groupId+char
    #Normalize ArtifactId
    artifactIdRaw=libCoordonate.split(':')[-2].replace('-','_')
    artifactId=''
    nextOneIsUpperCase=False
    for char in artifactIdRaw:
        if nextOneIsUpperCase:
            artifactId=artifactId+char.upper()
            nextOneIsUpperCase=False
        elif '.' in char or '_' in char or '-' in char:
            nextOneIsUpperCase=True
        else:
            artifactId=artifactId+char
    nickName=groupId+"_"+artifactId+'_Version'
    print(nickName)
    return nickName

#start the migration
# migrateCsvToPython()