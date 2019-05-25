# -*- coding: utf-8 -*-
# script for multiple find/replace pairs for all HTML files in a directory.
from sys import path
path.insert(0, './androidx_mapping')
from AndroidXMigration import androidx_mapping
import os
from os import walk
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN

inputDir = "../app/src/"

fileExtension = [".xml", ".java", ".kt" , ".gradle",".legacy"]


def replaceStringInFile(filePath):
    #"replaces all findStr by repStr in file filePath"
    # print(CYAN+"Start migrating the following file "+str(filePath))
    tempName = filePath + 'O_o'
    try:
        inputFile = open(filePath,'r', encoding="utf-8")
        outputFile = open(tempName, 'w+', encoding="utf-8")
        fContent = inputFile.read()
    except Exception as e: 
        print(e)

    # print(fContent)
    for aPair in androidx_mapping.findreplace:
        outputText = fContent.replace(aPair[0], aPair[1])
        fContent = outputText

    outputFile.write(outputText)

    outputFile.close()
    inputFile.close()

    # print (CYAN+"processed "+format(filePath))
    os.remove(filePath)
    os.rename(tempName, filePath)
    # print (CYAN+"files are closed")


# for (dirpath, dirnames, filenames) in walk(inputDir):
#     for file in filenames:
#         if (fileExtension[0] in file
#                 or fileExtension[1] in file
#                 or fileExtension[2] in file):
#             replaceStringInFile(dirpath + '/' + file)
#             print("toto " + dirpath + '/' + file)
# print ('done')
# for aPair in findreplace:
#     print(": "+aPair[0]+" => "+aPair[1])
def migrateGradle(repository):
    print(CYAN+"Start migrating to AndroidX the build.gradle found in the project")
    if os.path.isfile(repository+'\\build_gradle_eclipse_initial.legacy'):
        print(CYAN+"Migrating the following file: "+repository + '\\build_gradle_eclipse_initial.legacy')
        replaceStringInFile(repository + '\\build_gradle_eclipse_initial.legacy')
        print(GREEN+"\tDone")

    if os.path.isfile(repository+'\\app\\build_gradle_eclipse_initial.legacy'):
        print(CYAN+"Migrating the following file: "+repository + '\\app\\build_gradle_eclipse_initial.legacy')
        replaceStringInFile(repository + '\\app\\build_gradle_eclipse_initial.legacy')
        print(GREEN+"\tDone")

    if os.path.isfile(repository+'\\app\\build.gradle'):
        print(CYAN+"Migrating the following file: "+repository + '\\app\\build.gradle')
        replaceStringInFile(repository + '\\app\\build.gradle')
        print(GREEN+"\tDone")

    if os.path.isfile(repository+'\\build.gradle'):
        print(CYAN+"Migrating the following file: "+repository + '\\build.gradle')
        replaceStringInFile(repository + '\\build.gradle')    
        print(GREEN+"\tDone")
    print(CYAN+"Migrating to AndroidX the build.gradle is done")

def migrate(repository):
    print(CYAN+"Start migrating to AndroidX the folowing project: "+str(repository))
    for (dirpath, dirnames, filenames) in walk(repository):
        for file in filenames:
            if (fileExtension[0] in file
                    or fileExtension[1] in file
                    or fileExtension[2] in file
                    or fileExtension[3] in file
                    or fileExtension[4] in file):
                replaceStringInFile(dirpath + '/' + file)
                # print("toto " + dirpath + '/' + file)
    print (GREEN+'\nAndroid X migration done by referent AndroidXMigrationTool')
# for aPair in findreplace:
#     print(": "+aPair[0]+" => "+aPair[1])
# test:migrateGradle('D:\Git\Temp\Res\AmberTeam')