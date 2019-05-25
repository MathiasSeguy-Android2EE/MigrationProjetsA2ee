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
from ProjectSignin import SignIn


from gradle_management import manageSigninAndJks
ROOT_PYTHON_PATH=os.path.dirname(os.path.abspath(__file__))

TEMPLATE_PATH=os.path.dirname(ROOT_PYTHON_PATH+'\\template_gradle\\')
REPO_NAME='not_set'
JKS_SAFE="D:\\GDrive\\Android\\Keystores"
workingRepository=""
#Is filled by the method findSigninConfig
signinConfigList=[]
repoName=""

def manageSpecificJKS(repository):
    print(BLUE+"\t Managing new signin config of "+repository)
    global signinConfigList
    signinConfigList=[]
    if(len(repository)==0):
        return
    #Check the build.gradle's signin config bloc
    global workingRepository
    workingRepository=os.path.abspath(repository)
    global repoName
    repoName = workingRepository.split('\\')[-1].replace("\"","")    
    #Find the Signin config
    findSigninConfig()
    #Move keystore to safe storage
    moveSigninToSafeStorage()
    #Generate final Signin Bloc
    generateSignInMigrated()
    # print("\n\n\n Finishin new signin config of "+workingRepository)


#####################################################
# Managing the Signin configuration discovery process
# 
# ###################################################
def findSigninConfig():    
    global workingRepository 
    global signinConfigList
    # print("\nfind signin of "+workingRepository)
    #open the build.init.gradle
    buildInitial=open(workingRepository+'\\app\\build.gradle',"r")
    #parse:
    inSigninDepth=0
    initialSigninBloc=""
    for line in buildInitial:
        #Manage the Signin depth parsing 
        if 'signingConfigs {' in line or 'signingConfigs{' in line:
            inSigninDepth=1
        elif '}' in line and inSigninDepth != 0:
            inSigninDepth=inSigninDepth-1
        elif '{' in line and inSigninDepth != 0:
            inSigninDepth=inSigninDepth+1
        if inSigninDepth > 0:#You are in the signin bloc
            initialSigninBloc=initialSigninBloc+line
            #parse each bloc
            if '{' in line:#You are in a nex signinConfig element
                signinName=line.replace(" ","").replace("{","")
            if 'storeFile' in line:
                storeFile=line.replace(" ","").replace("storeFile","")
            if 'storePassword' in line:
                storePassword=line.replace(" ","").replace("storePassword","")
            if 'keyAlias' in line:
                keyAlias=line.replace(" ","").replace("keyAlias","")
            if 'keyPassword' in line:
                keyPassword=line.replace(" ","").replace("keyPassword","")
            if '}' in line and inSigninDepth==1:
                #You have all the information on the SignIn, generates it
                signIn=SignIn(signinName,storeFile,storePassword,keyAlias,keyPassword)
                signIn=normalizeSigninConfig(signIn)
                signIn.addInitialInformation(workingRepository,repoName,initialSigninBloc)
                signinConfigList.append(signIn)
                print(GREEN+"\t\t"+str(signIn))
    buildInitial.close()

def logSigninConfig(repository,fileToLog):   
    if(len(repository)==0):
        return
    global workingRepository 
    workingRepository=repository
    print("manage signin of "+workingRepository)
    #open the build.init.gradle
    buildInitial=open(workingRepository+'\\app\\build.gradle',"r")
    #parse:
    inSigninDepth=0
    initialSigninBloc=""
    for line in buildInitial:
        #Manage the Signin depth parsing 
        if 'signingConfigs {' in line or 'signingConfigs{' in line:
            inSigninDepth=1
        elif '}' in line and inSigninDepth != 0:
            inSigninDepth=inSigninDepth-1
        elif '{' in line and inSigninDepth != 0:
            inSigninDepth=inSigninDepth+1
        #Manage the parsing
        if inSigninDepth > 0:#You are in the signin bloc
            initialSigninBloc=initialSigninBloc+line
            fileToLog.write(line)
            #parse each bloc
            if '{' in line:#You are in a next signinConfig element
                signinName=line.replace(" ","").replace("{","")
            if 'storeFile' in line:
                storeFile=line.replace(" ","").replace("storeFile","")
            if 'storePassword' in line:
                storePassword=line.replace(" ","").replace("storePassword","")
            if 'keyAlias' in line:
                keyAlias=line.replace(" ","").replace("keyAlias","")
            if 'keyPassword' in line:
                keyPassword=line.replace(" ","").replace("keyPassword","")
            if '}' in line and inSigninDepth==1:
                #You have all the information on the SignIn, generates it
                signIn=SignIn(signinName,storeFile,storePassword,keyAlias,keyPassword)
                signIn=normalizeSigninConfig(signIn)
                signIn.addInitialInformation(workingRepository,repoName,initialSigninBloc)
                signinConfigList.append(signIn)
                print(signIn)
        
    buildInitial.close()
  

#Normalize the Raw Signin config you have
def normalizeSigninConfig(signin):
    # print("manage signin of "+signin.signinName+" and "+signin.storeFile)
    global workingRepository     
    #check if direct path
    if('.ext.' in signin.storeFile):
        # print("it's a trap")
        #need to find the value
        signInNormalized=normalizeSignin(signin,workingRepository)
    else:#clean the string
        signinName=signin.signinName
        storeFile=signin.storeFile.replace("file","").replace("(","").replace("\"","").replace(";","").replace(")","")
        storeFile=storeFile.replace("project.","").replace("\'","")
        storePassword=signin.storePassword.replace("(","").replace("\"","").replace(";","").replace(")","")
        keyAlias=signin.keyAlias.replace("(","").replace("\"","").replace(";","").replace(")","")
        keyPassword=signin.keyPassword.replace("(","").replace("\"","").replace(";","").replace(")","")
        signInNormalized= SignIn(signinName,storeFile,storePassword,keyAlias,keyPassword)
    #when you have your path
    # print("found Singin:"+str(signInNormalized))
    return manageSigninConfigNormalize(signInNormalized)

  
def manageSigninConfigNormalize(signin):
    return signin

#Nomalise Signin config in case it's stored in an account.properties file
def normalizeSignin(signin,repo):    
    if(len(repo)==0):
        return None
    #Find the file that contains 'account' and '.properties'
    storeFileKey=signin.storeFile.replace("project.ext.","").replace("\n","") 
    storePasswordKey=signin.storePassword.replace("project.ext.","").replace("\n","") 
    keyAliasKey=signin.keyAlias.replace("project.ext.","").replace("\n","") 
    keyPasswordKey=signin.keyPassword.replace("project.ext.","").replace("\n","") 
    # print("workingRepository: "+str(repo) )
    # print("storeFileKey: "+storeFileKey) 
    # print("storePasswordKey: "+storePasswordKey) 
    # print("keyAliasKey: "+keyAliasKey) 
    # print("keyPasswordKey: "+keyPasswordKey)
    found=0
    signinResult=None
    #find in file in this directory
    for file in scandir(repo):
        if path.isfile(file):
            if 'account' in file.name.lower() and  '.properties' in file.name.lower() :            
                # print("have found the file: "+file.name)
                #open the file and find your signin
                accounts=open(file,"r") 
                # print("workingRepository: "+str(repo) )
                # print("storeFileKey: "+storeFileKey) 
                # print("storePasswordKey: "+storePasswordKey) 
                # print("keyAliasKey: "+keyAliasKey) 
                # print("keyPasswordKey: "+keyPasswordKey)
                for line in accounts:
                    if storeFileKey in line:
                        storeFileValue=line.replace(storeFileKey,"").replace("=","").replace(" ","").replace("\n","")       
                        # print("have found the storeFileValue: "+storeFileValue)
                        found=found+1
                    if storePasswordKey in line:
                        storePasswordValue=line.replace(storePasswordKey,"").replace("=","").replace(" ","").replace("\n","")    
                        # print("have found the storePasswordValue: "+storePasswordValue)
                        found=found+1
                    if keyAliasKey in line:
                        keyAliasValue=line.replace(keyAliasKey,"").replace("=","").replace(" ","").replace("\n","")    
                        # print("have found the keyAliasValue: "+keyAliasValue)
                        found=found+1
                    if keyPasswordKey in line:
                        keyPasswordValue=line.replace(keyPasswordKey,"").replace("=","").replace(" ","").replace("\n","")    
                        # print("have found the keyPasswordKey: "+keyPasswordKey)
                        found=found+1
                    if found == 4:
                        signinResult= SignIn(signin.signinName,storeFileValue,storePasswordValue,keyAliasValue,keyPasswordValue)
                        return signinResult
    #Recurse in directory    
    for folder in scandir(repo):
        if path.isdir(folder):
            if not('.git' in folder.path or 'build' in folder.path or '.gradle' in folder.path or 'src' in folder.path or 'test' in folder.path):
                signinResult=normalizeSignin(signin,folder.path)            
                if signinResult != None:
                    return signinResult
        
    return None

#Move the JKS and its configuration in a safe place
# JKS_SAFE="D:\\GDrive\\Android\\Keystores\\"
def moveSigninToSafeStorage():
    global repoName
    #Create the target folder
    targetName=JKS_SAFE+"\\"+repoName
    if not os.path.isdir(targetName):
        os.makedirs(targetName,mode=0o777)
    jksFoundReport=""
    for signin in signinConfigList:
        repoNameNormalized=repoName.replace(" ","")        
        #copy the JKS
        jksSrcPath=signin.jksFilePath
        # print("The jks src = "+jksSrcPath)
        jksTrgPath=targetName+"\\"+signin.signinName+"\\"+signin.jksFileSimpleName
        if not os.path.isdir(targetName+"\\"+signin.signinName):
            os.makedirs(targetName+"\\"+signin.signinName,mode=0o777)
        copyfile(jksSrcPath,jksTrgPath)
        #write account information for the specific signin
        account=open(targetName+"\\"+signin.signinName+"\\account.properties","w+")
        account.write("#Signin configuration for ")
        account.write("#"+workingRepository+"\n")
        account.write("#"+jksSrcPath+"\n")
        account.write("#"+repoNameNormalized+"\n")
        account.write("#"+signin.signinName+"\n")
        account.write("JKSFile_"+repoNameNormalized+"_"+signin.signinName+"="+signin.storeFile+"\n")
        account.write("JKSPassword_"+repoNameNormalized+"_"+signin.signinName+"="+signin.storePassword+"\n")
        account.write("JKSKeyAlias_"+repoNameNormalized+"_"+signin.signinName+"="+signin.keyAlias+"\n")
        account.write("JKSKeyPassword_"+repoNameNormalized+"_"+signin.signinName+"="+signin.keyPassword+"\n")
        account.close()        
        jksFoundReport=jksFoundReport+"#Initial JKS name:"+signin.jksFileSimpleName+"\n"
        jksFoundReport=jksFoundReport+"#Initial JKS path:"+signin.jksFilePath+"\n"
        jksFoundReport=jksFoundReport+"#Pass:"+signin.storePassword+"\n"
        jksFoundReport=jksFoundReport+"#Alias:"+signin.keyAlias+"\n"
        jksFoundReport=jksFoundReport+"#AliasPass:"+signin.keyPassword+"\n"
        signinOne=signin
    #Now for this Repo we will create the file "initial" condition    
    # signinOne=signinConfigList[0]
    initialSigninConfig=open(targetName+"\\signin_initial.txt","w+")
    initialSigninConfig.write("#Initial Signin configuration for "+signinOne.repoSimpleName+"\n")
    initialSigninConfig.write("#Initial Repo path:\n"+signinOne.initialRepo+"\n")
    initialSigninConfig.write("#Initial Repo name:\n"+signinOne.repoSimpleName+"\n")
    initialSigninConfig.write(jksFoundReport)
    initialSigninConfig.write("#Initial SigninConfig:\n"+signinOne.signinInitialBloc+"\n")
    initialSigninConfig.close()
    #For signinElm in signinConfigList
        #create the subfolder with the signinname
        #copy the jks in it
        #create in it the file account.properties and fill it
    
#Generate the new signin bloc
def generateSignInMigrated():
    global repoName
    global workingRepository 
    #Create the target folder
    keystorePath=workingRepository+"\\app\\gradle\\keystore\\"
    signInConfigBloc=open(workingRepository+"\\app\\signinbloc.txt","w+")
    # Create the folder if it doesn't exist.
    if not os.path.exists(workingRepository+"\\app\\gradle\\properties"):
        os.makedirs(workingRepository+"\\app\\gradle\\properties", mode=0o777)
    if not os.path.exists(keystorePath):
        os.makedirs(keystorePath, mode=0o777)
    legacyAccounts=open(workingRepository+"\\app\\gradle\\properties\\legacy_accounts.gradle","w+")    
    signInConfigBloc.write("\t/***********************************************************\n")
    signInConfigBloc.write("\t *  Signing\n")
    signInConfigBloc.write("\t **********************************************************/\n")
    signInConfigBloc.write('\tapply from: \'gradle/properties/legacy_accounts.gradle\'\n')    
    signInConfigBloc.write('\tsigningConfigs {\n') 
    signInConfigBloc.write("\t//TODO manage your signin configuration you have switched \n")
    

    legacyAccounts.write('/***********************************************************\n')
    legacyAccounts.write(' * We define the legacy value for legacy keystore\n')
    legacyAccounts.write(' * we directly use project.ext pattern for simplicity\n')
    legacyAccounts.write('***********************************************************/\n')
    legacyAccounts.write('project.ext{')
    strSetFileList=""
    debugConfigFound=False
    releaseConfigFound=False
    for signin in signinConfigList:
        #write account information for the specific signin
        if signin.signinName in "debug" and "debug" in signin.signinName:
            debugConfigFound=True
        if signin.signinName in "release" and "release" in signin.signinName:
            releaseConfigFound=True
        signInConfigBloc.write("\t\t "+signin.signinName+"{\n")
        signInConfigBloc.write("\t\t\t storeFile project.ext.JKSFile_"+signin.signinName+"\n")
        signInConfigBloc.write("\t\t\t storePassword project.ext.JKSPassword_"+signin.signinName+"\n")
        signInConfigBloc.write("\t\t\t keyAlias project.ext.JKSKeyAlias_"+signin.signinName+"\n")
        signInConfigBloc.write("\t\t\t keyPassword project.ext.JKSKeyPassword_"+signin.signinName+"\n")
        signInConfigBloc.write("\t\t}\n")
        #write the accounts
        legacyAccounts.write('\t//Signing configurations for '+signin.signinName+"\n")
        # legacyAccounts.write('\tJKSFile_'+signin.signinName+"=\"file(\"gradle/keystore/"+signin.jksFileSimpleName+"\")\"\n")
        strSetFileList=strSetFileList+"project.ext.set(\"JKSFile_"+signin.signinName+"\" , file('gradle/keystore/"+signin.jksFileSimpleName+"\'))\n"
        legacyAccounts.write('\tJKSPassword_'+signin.signinName+"=\""+signin.storePassword+"\"\n")
        legacyAccounts.write('\tJKSKeyAlias_'+signin.signinName+"=\""+signin.keyAlias+"\"\n")
        legacyAccounts.write('\tJKSKeyPassword_'+signin.signinName+"=\""+signin.keyPassword+"\"\n\n")
        #move the keystore to its new place
        srcKeyStore=workingRepository+'\\app\\'+signin.storeFile
        move(srcKeyStore,keystorePath+signin.jksFileSimpleName)
    #Add default Keystore        
    if(not debugConfigFound):
        signInConfigBloc.write("\t\tdebug {\n")
        signInConfigBloc.write("\t\t\tstoreFile project.ext.JKSFile\n")
        signInConfigBloc.write("\t\t\tstorePassword project.ext.JKSPassword\n")
        signInConfigBloc.write("\t\t\tkeyAlias project.ext.JKSKeyAlias\n")
        signInConfigBloc.write("\t\t\tkeyPassword project.ext.JKSKeyPassword\n")
        signInConfigBloc.write("\t\t}\n")    
    if(not releaseConfigFound):
        signInConfigBloc.write("\t\trelease {\n")
        signInConfigBloc.write("\t\t\tstoreFile project.ext.JKSFile_Release\n")
        signInConfigBloc.write("\t\t\tstorePassword project.ext.JKSPassword_Release\n")
        signInConfigBloc.write("\t\t\tkeyAlias project.ext.JKSKeyAlias_Release\n")
        signInConfigBloc.write("\t\t\tkeyPassword project.ext.JKSKeyPassword_Release\n")
        signInConfigBloc.write("\t\t}\n")
    #close files
    signInConfigBloc.write("\t}\n")
    signInConfigBloc.close() 
    legacyAccounts.write("}\n")
    legacyAccounts.write(strSetFileList)
    legacyAccounts.close() 

#Generate the new signin bloc
def generateSignInNormal(repository):
    #Create the target folder
    signInConfigBloc=open(repository+"\\app\\signinbloc.txt","w+")
    #write account information for the specific signin
    signInConfigBloc.write("/***********************************************************\n")
    signInConfigBloc.write(" *  Signing\n")
    signInConfigBloc.write(" **********************************************************/\n")
    signInConfigBloc.write("signingConfigs {\n")
    signInConfigBloc.write("    debug {\n")
    signInConfigBloc.write("        storeFile project.ext.JKSFile\n")
    signInConfigBloc.write("        storePassword project.ext.JKSPassword\n")
    signInConfigBloc.write("        keyAlias project.ext.JKSKeyAlias\n")
    signInConfigBloc.write("        keyPassword project.ext.JKSKeyPassword\n")
    signInConfigBloc.write("    }\n")
    signInConfigBloc.write("    release {\n")
    signInConfigBloc.write("        storeFile project.ext.JKSFile_Release\n")
    signInConfigBloc.write("        storePassword project.ext.JKSPassword_Release\n")
    signInConfigBloc.write("        keyAlias project.ext.JKSKeyAlias_Release\n")
    signInConfigBloc.write("        keyPassword project.ext.JKSKeyPassword_Release\n")
    signInConfigBloc.write("    }\n")
    signInConfigBloc.write("}\n")
    #close files
    signInConfigBloc.close() 