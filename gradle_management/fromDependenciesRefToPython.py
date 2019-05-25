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


ROOT_PYTHON_PATH=os.path.dirname(os.path.abspath(__file__))
def migrateDependenciesToPython():    
    print('We are here '+ROOT_PYTHON_PATH+" and we start generating the mapping python file for dependencies as a list of tuple")
    dependencies_ref= open(ROOT_PYTHON_PATH+"\\dependencies_ref.txt","r")
    dependencies_hash=open(ROOT_PYTHON_PATH+'\\dependencies_hash.py',"w+")
    #You need to migrate from:
    #androidTestImplementation "androidx.test.ext:junit:${androidXJunitVersion}"
    #to
    #('androidx.test.ext:junit','androidTestImplementation "androidx.test.ext:junit:${androidXJunitVersion}"')
    
    #Class generation
    dependencies_hash.write("dependencies_hash = [\n")
    commentList=['//toto','//tata']
    parsingComments=False
    for rawLine in dependencies_ref:
        line=rawLine.replace('\n','')
        splittedLine=line.split(':')
        if len(splittedLine)>2 and ('mplementation' in line or 'kapt' in line or 'api' in line):
            #Manage the content of the dependency (Implementation "androidx.test.ext:junit:${androidXJunitVersion}")     
            versionSuffix=splittedLine[-1]
            coordonate=(line.split(' ')[-1]).replace(versionSuffix,'').replace("\"",'').replace("\'",'')
            newLine='\t(\''
            #write the comment associated with this dependency            
            print("In write CmList="+str(commentList))
            for commentLine in commentList:
                dependencies_hash.write(newLine+coordonate+'COMMENT'+'\',\''+commentLine+'\'),\n')
            #write the dependency itself
            newLine=newLine+coordonate+'\',\''+coordonate+'${'+getVersionName(coordonate)+'}\'),\n'
            dependencies_hash.write(newLine)
            parsingComments=False
        elif "//" in line:
            #Keep the comment, it will be associated with th next dependency found
            if not parsingComments:
                commentList=[]
            parsingComments=True
            commentList.append(line)

    #When using this file, you need to add the crashlitycs and the junit :
    # //Crashlytics
    # implementation("com.crashlytics.sdk.android:crashlytics:${crashlyticsVersion}") {
    #     transitive = true;
    #     }
    # And    
    # androidTestImplementation "junit:junit:${junitVersion}" 
    # testImplementation "junit:junit:${junitVersion}"

    dependencies_hash.write("\t(\'over:over:over:choupy\',\'job:is:done\')\n")
    dependencies_hash.write("]\n")    
    dependencies_hash.write("def testDependenciesHashMap(): \n")
    dependencies_hash.write("    for aPair in dependencies_hash:\n")
    dependencies_hash.write("        print(aPair[0]+\"=>\"+aPair[1])\n")
    dependencies_hash.write(" \n")
    dependencies_hash.write("#testDependenciesHashMap()    ")
    dependencies_hash.close()
    dependencies_ref.close()

# Parameter: full coordinates androidx.test:runner:31.4
# Result: androidxTest_runner_Version
#It replace . by uppercase, - by upper case and append "_Version"
# So this is what you'll have in your build.gradle
# androidTestImplementation "androidx.test:runner:${androidxTest_runner_Version}"
# androidTestImplementation "androidx.test.espresso:espresso-core:${androidxTestEspresso_espressoCore_Version}"
def getVersionName(libCoordonate):
    #"${"+dependency.coordinate.split(':')[-2].replace('-','_')+'Version}"
    #NormalizeGroupId
    if(len(libCoordonate.split(':')) < 3):
        return libCoordonate
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
migrateDependenciesToPython()