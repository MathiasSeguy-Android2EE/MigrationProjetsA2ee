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
def splitLicencesYmlInAtomicElements():    
    print('Splitting the licences '+ROOT_PYTHON_PATH)
    licencesYmlReferent= open(ROOT_PYTHON_PATH+"\\licenses.yml","r")
    licences_bloc=open(ROOT_PYTHON_PATH+'\\dependencies_hash.py',"w+")
    #You need to slit the bloc into files:
    ##Dart and Henson
    # - artifact: com.f2prateek.dart:dart-annotations:+
    #   name: Dart Annotations
    #   copyrightHolder: 2013 Jake Wharton, 2014 Prateek Srivastava
    #   license: The Apache Software License, Version 2.0
    #   licenseUrl: http://www.apache.org/licenses/LICENSE-2.0.txt
    #   url: https://github.com/f2prateek/dart
    #Into a file com.f2prateek.dart_dart-annotations.txt
    
    #Class generation
    commentList=['toto','tata']
    parsingComments=False
    for rawLine in licencesYmlReferent:
        if ('- artifact:' in rawLine):
            #close previous file
            if not licences_bloc is None:
                licences_bloc.close
            #open new file
            fileName=rawLine[12:-2].replace(':','_')+'.txt'
            licences_bloc=open(ROOT_PYTHON_PATH+'\\'+fileName,"w+")
            #write the comment associated with this dependency            
            print("In write CmList="+str(commentList))
            for commentLine in commentList:
                licences_bloc.write(commentLine)
            #write the element
            licences_bloc.write(rawLine)
            parsingComments=False
        elif "#" in rawLine:
            #Keep the comment, it will be associated with th next dependency found
            if not parsingComments:
                commentList=[]
            parsingComments=True
            commentList.append(rawLine)
        else:
            #copy the content
            if not licences_bloc is None:
                licences_bloc.write(rawLine)

    
    if not licences_bloc is None:
        licencesYmlReferent.close()
    licencesYmlReferent.close()

#start the migration
splitLicencesYmlInAtomicElements()