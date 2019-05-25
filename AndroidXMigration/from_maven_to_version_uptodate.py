#This file is used in android Migration to create the referential files for the versionninig of the library
#It parse the page https://dl.google.com/dl/android/maven2/index.html
#And create list of (pair,value) where pair is the library version's name, and value is the value of the version
#it's always the latest stable available version
from sys import path
import from_csv_to_python

import xml.etree.ElementTree as ET
from urllib.request import urlopen
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


#Read the GoogleMaven Page and return it
#https://dl.google.com/dl/android/maven2/index.html
def fromGoogleMavenToVersionDefGradle():    
    print(BLUE+'We are creating the gradle file that list all the JetPack libraries version.')
    print(BLUE+'We are here '+ROOT_PYTHON_PATH)
    gradleFileName=ROOT_PYTHON_PATH+'\\..\\gradle_management\\template_gradle\\app\\gradle\\google_lib_version.gradle'
    gradleFile=open(gradleFileName,"w+")
    os.chmod(gradleFileName,0o777)
    dependencies_hash=open(ROOT_PYTHON_PATH+'\\dependencies_google_hash.py',"w+")
    dependencies_hash.write("dependencies_hash = [\n")

    gradleFile.write("//Last version of Google Lib are listed below, to update run from_maven_to_version_uptodate.py and then your migration script")
    gradleFile.write("\nproject.ext{\n")
    contentRawXml = urlopen("https://dl.google.com/dl/android/maven2/master-index.xml").read().decode("UTF-8")
    contentXml = contentRawXml.split("\n")
    for line in contentXml:
        # print(line)
        if "metadata" in line or "encoding=" in line:
            print(line)
        elif '.' in line:
            groupId=line.replace('<','').replace('/>','').replace(" ","")
            subUrl=groupId.replace('.','/')
            # print("Calling :https://dl.google.com/dl/android/maven2/"+subUrl+"/group-index.xml")
            versionRawXml = urlopen("https://dl.google.com/dl/android/maven2/"+subUrl+"/group-index.xml").read().decode("UTF-8")
            versionContent = versionRawXml.split("\n")
            for versionLine in versionContent:
                # print(versionLine)
                if "versions=" in versionLine:
                    versionLine=versionLine.replace('<','').replace('/>','')
                    # print(versionLine)
                    elem=versionLine.split(' ')
                    # print("elem "+str(elem))
                    artifactId=elem[2]
                    # print("artifactId "+artifactId)
                    versions=elem[3]
                    # print(versionLine)
                    # print("versionLine "+versionLine)
                    lastStableVersion=getLastStableVersion(versions)          
                    versionVarName=from_csv_to_python.getVersionName(groupId+":"+artifactId+":"+lastStableVersion)          
                    print(groupId+":"+artifactId+":"+versionVarName)       
                    print(versionVarName+" = \""+lastStableVersion+"\"")
                    gradleFile.write("\t"+versionVarName+" = \""+lastStableVersion+"\"\n")
                    pair1="\""+groupId+":"+artifactId+":\""
                    pair2="\""+groupId+":"+artifactId+":${"+versionVarName+"}\""
                    dependencies_hash.write("("+pair1+","+pair2+"),\n")
                    #over bob you have coordinate= groupid:artifactId and the version to use
    gradleFile.write("}")
    gradleFile.close() 
    dependencies_hash.write("\t(\'over:over:over:choupy\',\'job:is:done\')\n")
    dependencies_hash.write("]\n")    
    dependencies_hash.write("def testDependenciesHashMap(): \n")
    dependencies_hash.write("    for aPair in dependencies_hash:\n")
    dependencies_hash.write("        print(aPair[0]+\"=>\"+aPair[1])\n")
    dependencies_hash.write(" \n")
    dependencies_hash.write("#testDependenciesHashMap()    ")
    dependencies_hash.close()

def getLastStableVersion(versions):
    versions=versions.replace("versions=","").replace("\"/>","").replace("\"","")
    # print(versions)
    versionsList=versions.split(",")[::-1]#To reverse the order
    # print(versionsList)
    alphaVersion="0"
    betaVersion="0"
    for version in versionsList:
        if "alpha" in version:
            # print("This is alpha "+version+" and currAlpha= "+alphaVersion)
            if alphaVersion == "0":
                alphaVersion=version
        elif "beta" in version :
            # print("This is beta "+version+" and currBeta= "+betaVersion)
            if betaVersion == "0":
                betaVersion=version
        else:
            # print("This is release "+version)
            # print("This is beta  "+betaVersion)
            # print("This is alpha "+alphaVersion)
            return version
    #It means there is no release version
    if betaVersion != "0":
        return betaVersion
    else:
        return alphaVersion
#List of index
#https://dl.google.com/dl/android/maven2/master-index.xml
    # <metadata>
    # <com.android.support.constraint/>
    # <com.android.databinding/>
    # <com.android.support/>
#https://dl.google.com/dl/android/maven2/com/android/support/constraint/group-index.xml
    # <com.android.support.constraint>
    # <constraint-layout-solver versions="1.0.2,1.1.0-beta1,1.1.0-beta2,1.1.0-beta3,1.1.0-beta4,1.1.0-beta5,1.1.0-beta6,1.1.0,1.1.1,1.1.2,1.1.3,2.0.0-alpha1,2.0.0-alpha2,2.0.0-alpha3,2.0.0-alpha4,2.0.0-alpha5,2.0.0-beta1"/>
    # <constraint-layout versions="1.0.2,1.1.0-beta1,1.1.0-beta2,1.1.0-beta3,1.1.0-beta4,1.1.0-beta5,1.1.0-beta6,1.1.0,1.1.1,1.1.2,1.1.3,2.0.0-alpha1,2.0.0-alpha2,2.0.0-alpha3,2.0.0-alpha4,2.0.0-alpha5,2.0.0-beta1"/>
    # </com.android.support.constraint>

#In case you want to test or generate
# fromGoogleMavenToVersionDefGradle()
