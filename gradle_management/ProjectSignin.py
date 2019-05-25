import sys

import os
import subprocess
from shutil import copyfile
from shutil import rmtree
from shutil import move
from os import scandir
from os import remove
from os import path
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
#Aims to represents a library dependency
class SignIn:
    NOT_DEFINED='NOT_DEFINED'
    signinName=NOT_DEFINED
    storeFile=NOT_DEFINED
    storePassword=NOT_DEFINED
    keyAlias=NOT_DEFINED
    keyPassword=NOT_DEFINED
    initialRepo=NOT_DEFINED
    repoSimpleName=NOT_DEFINED
    jksFileSimpleName=NOT_DEFINED
    signinInitialBloc=NOT_DEFINED
    jksFilePath=NOT_DEFINED
    def __init__(self,signinName,storeFile,storePassword,keyAlias,keyPassword):
        self.signinName=signinName.replace("\n","")
        self.storeFile=storeFile.replace("\n","")#don't remove space, its path
        self.storePassword=storePassword.replace("\n","")
        self.keyAlias=keyAlias.replace("\n","")
        self.keyPassword=keyPassword.replace("\n","")

   
    def __str__(self):
     return ''+self.signinName+': '+self.storeFile+", "+self.storePassword+", "+self.keyAlias+", "+self.keyPassword+", "+self.initialRepo+", "+self.repoSimpleName
    
    def setJksAbsolutePathAndName(self):
        self.jksFilePath=os.path.abspath(self.initialRepo+"\\app\\"+self.storeFile)
        print("******\nHave found the path of the jks :"+self.jksFilePath)
        self.jksFileSimpleName=self.jksFilePath.split("\\")[-1]
        print("******\nHave found the name of the jks :"+self.jksFileSimpleName)

    def addInitialInformation(self,initialRepo,repoSimpleName,signinInitialBloc):        
        self.initialRepo=initialRepo
        self.repoSimpleName=repoSimpleName
        self.signinInitialBloc=signinInitialBloc
        #Now grab the others informations
        print(self)
        self.setJksAbsolutePathAndName()


  