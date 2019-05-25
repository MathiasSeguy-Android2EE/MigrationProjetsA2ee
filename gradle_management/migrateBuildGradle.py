#This file is managing the Gradle Dependencies part of the migration by:
#Analysing teh initial build.gradle and extracting all the dependencies founds.
#For each dependency, it looks if the library is well known (using dependencies_hash.py) or not
#According to this information, it find the last version of the library or reuse the existing version
#Then it will manage the open source libraries of the project by creating the licenses.yml file

from sys import path
path.insert(0, './ProjectMetaData')
path.insert(0, './AndroidXMigration')
import ProjectMetaData
from os import path
from AndroidXMigration  import dependency_lib_version,from_csv_to_python
import manageSigninAndJks
from ProjectDependencies import Dependencies 
import dependencies_hash
from AndroidXMigration import dependencies_google_hash
from shutil import move
import os
from os import scandir
import subprocess
from subprocess import PIPE, STDOUT

from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN

ROOT_PYTHON_PATH=os.path.dirname(os.path.abspath(__file__))
#The goal of this file is to manage the build.gradle file of the app module
#It has to face with the dependencies blocs and rebuild it
#It has to handle already existing keyStore
#It has to extract Project MetaData (like the pom of the project)
def migrateBuildGradle(gradleBuildFile,repository,needToRenameWhenOver):
    global projectMeta
    #Analyse your project and find Meta
    createProjectMetaData(gradleBuildFile)
    #create your dependencies block
    createDependenciesBlock(projectMeta,repository)
    #Check for keystore
    manageKeyStore(repository)
    #change the name of your file:
    if needToRenameWhenOver:
        move(gradleBuildFile,repository+'\\build_gradle.legacy')
    return projectMeta


def createProjectMetaData(gradleBuildFile):
    #Retrieve your data
    global projectMeta
    projectMeta= ProjectMetaData.ProjectMeta(gradleBuildFile)
    return projectMeta

def createDependenciesBlock(projectMeta,repository):
    #create a file, fill it with the depencies found in the project
    print(BLUE+"Writing the dependency file (for later) of "+repository)
    dependenciesBlock=open(repository+'\\dependenciesBlock.txt',"w+")
    licencesBlock=open(repository+'\\app\\licenses.yml',"w+")
    versionLibBlock=open(repository+'\\app\\var_def_lib.gradle',"w+") #TODO merge it with gradle/varoable_def
    versionLibBlock.write("//This is the list of the version of library you use\n")
    versionLibBlock.write("project.ext {\n")
    for dependency in projectMeta.dependencies:
        #junit is not managed here
        if 'junit' in dependency.coordinate or 'resolutionStrategy' in dependency.typeValue:
            pass
        #If the type is normal
        elif dependency.type in Dependencies.TYPE_NORMAL:
            found=False
            #find if it's a known dependency
            for aPair in dependencies_hash.dependencies_hash:
                #Manage dependendcy
                if dependency.coordinate in aPair[0]:
                    try:
                        found=True
                        # print('\n\nWe have managed this dependency: '+dependency.coordinate+', and aPair=('+aPair[0]+','+aPair[0]+')')
                        #Add the line
                        
                        if not "COMMENT" in aPair[0]:
                            dependenciesBlock.write("\t"+dependency.typeValue+"\""+aPair[1]+'\"\n')
                            # print(CYAN+"\tAdding dep: "+aPair[1])
                        else:
                            dependenciesBlock.write(aPair[1]+'\n')

                        #Manage licences
                        # print('With this line: '+dependency.coordinate)
                        if not "COMMENT" in aPair[0]:
                        #     #D:\Git\Python\MigrationProjetsA2ee\gradle_management\template_licences_yml
                        #     #D:\Git\Python\MigrationProjetsA2ee\gradle_management\com.google.android.material_material_.txt
                            licenceFileName=ROOT_PYTHON_PATH+'\\template_licences_yml\\'+dependency.coordinate.replace(':','_')+'.txt'                                
                            if os.path.isfile(licenceFileName):
                                # print('look for the file :'+licenceFileName)
                                licenceElements=open(licenceFileName,"r")
                                for line in licenceElements:
                                    licencesBlock.write(line)
                                licenceElements.close
                    except:
                        print(RED+'\tA problem occured while looking for '+dependency.coordinate)
            #find if it's a google libraries dependency
            if not found:
                for aPair in dependencies_google_hash.dependencies_hash:
                    #Manage dependendcy
                    if dependency.coordinate in aPair[0]:
                        try:
                            found=True
                            # print('\n\nWe have managed this dependency: '+dependency.coordinate+', and aPair=('+aPair[0]+','+aPair[0]+')')
                            #Add the line
                            
                            if not "COMMENT" in aPair[0]:
                                dependenciesBlock.write("\t"+dependency.typeValue+" \""+aPair[1]+'\"\n')
                                # print(CYAN+"\tAdding dep: "+aPair[1])
                            else:
                                dependenciesBlock.write(""+aPair[1]+'\n')

                            #Manage licences
                            # print('With this line: '+dependency.coordinate)
                            if not "COMMENT" in aPair[0]:
                            #     #D:\Git\Python\MigrationProjetsA2ee\gradle_management\template_licences_yml
                            #     #D:\Git\Python\MigrationProjetsA2ee\gradle_management\com.google.android.material_material_.txt
                                licenceFileName=ROOT_PYTHON_PATH+'\\template_licences_yml\\'+dependency.coordinate.replace(':','_')+'.txt'                                
                                if os.path.isfile(licenceFileName):
                                    # print('look for the file :'+licenceFileName)
                                    licenceElements=open(licenceFileName,"r")
                                    for line in licenceElements:
                                        licencesBlock.write(line)
                                    licenceElements.close
                        except:
                            print(RED+'\tA problem occured while looking for '+dependency.coordinate)
            if not found:
                #Not know neither as google lib neither as a known lib
                #Your dependencies line
                #androidTestImplementation "androidx.test.espresso:espresso-core:${espressoVersion}"
                #and use the good versionSuffix
                # print("Changin from :"+dependency.coordinate+" to ${"+dependency.coordinate.split(':')[-2].replace('-','_')+'Version}"')
                versionVarName=from_csv_to_python.getVersionName(dependency.coordinate)
                dependencyNewBlock="\t"+dependency.typeValue+" \""+dependency.coordinate+"${"+versionVarName+"}\""
                print("\ttrying to find the version name: "+dependency.coordinate)
                # print(dependencyNewBlock)
                #Add the dependencyNewBlock
                dependenciesBlock.write(dependencyNewBlock+'\n')
                # print(CYAN+"\tAdding dep: "+dependencyNewBlock)
                licenceFileName=ROOT_PYTHON_PATH+'\\template_licences_yml\\'+dependency.coordinate.replace(':','_')+'.txt'
                if os.path.isfile(licenceFileName):
                    # print ('look for the file :'+licenceFileName)
                    licenceElements=open(licenceFileName,"r")
                    for line in licenceElements:
                        licencesBlock.write(line)
                    licenceElements.close
                #find the version value by browsing all files
                #first check if it's belong to the new libraries
                versionValue=findValueOfTheVersionOfDependency(dependency.version,repository)
                if versionValue == None:
                    print(RED+"\tUnknown version value for :"+dependency.version)
                    versionValue="\'Unknown\'"
                    versionLibBlock.write("//"+versionVarName+"_NotFound="+versionValue+"\n")
                else:
                    print(GREEN+"\tVersion value for :"+dependency.version+"="+versionValue)
                    versionLibBlock.write(versionVarName+"="+versionValue+"\n")
                #paste the line and pray
                # dependencyNewBlock="\t"+dependency.typeValue+" \""+dependency.coordinate+dependency.version+"\""       
                # dependenciesBlock.write(dependencyNewBlock+'\n')   
                # print(GREEN+"\tWe have an unknown dependency which has been managed this way:")
                # print(CYAN+"\tAdding dep: "+dependencyNewBlock)
                #TODO track this error

        #If the type is fileTree        
        if dependency.type in Dependencies.TYPE_FILETREE:
            dependenciesBlock.write('    implementation fileTree(include: [\'*.jar\'], dir: \'libs\')\n')
        #If the type is transitive
        #If the type is weird => log
        #If the type is error => log
        #If the type is comment =>Skip
        #If the type is NotDefined => log
    #Add the crashlytics elements
    dependenciesBlock.write('    //Crashlytics\n')
    dependenciesBlock.write('    implementation("com.crashlytics.sdk.android:crashlytics:${comCrashlyticsSdkAndroid_crashlytics_Version}") {\n')
    dependenciesBlock.write('        transitive = true;\n')
    dependenciesBlock.write('    }\n')
    dependenciesBlock.write('    //Junit elements    \n')
    dependenciesBlock.write('    androidTestImplementation "junit:junit:${junit_junit_Version}" \n')
    dependenciesBlock.write('    testImplementation "junit:junit:${junit_junit_Version}"\n')
    dependenciesBlock.close()
    versionLibBlock.write("}\n")
    versionLibBlock.close()

#Find if you achieve to find the value of the version
#when versionVar looks like $project.toto, you look for the value of toto
def findValueOfTheVersionOfDependency(versionVar,repository):    
    # print("versionVar="+versionVar)
    versionName=versionVar.split(".")[-1]
    versionName=versionName.replace("project.","").replace("ext.","")
    versionName=versionName.replace("$","").replace("\'","").replace("\"","").replace("{","").replace("}","")
    # print("versionName="+versionName)
    return findValueOfTheVersionOfDependencyRecurse(versionName,repository)

#Recusive method
def findValueOfTheVersionOfDependencyRecurse(versionVar,repository):
    #find all files with .properties or .gradle extension
    # print("Trying to find out this :"+repository)
    #search the key in them
    for file in scandir(repository):
        # print("in scanDir with  :"+file.path)
        if path.isdir(file):
            # print("Recurse with :"+file.path)
            result=findValueOfTheVersionOfDependencyRecurse(versionVar,file.path)
            if result!=None:
                return result
        else:
            if ".gradle" in file.name or ".properties" in file.name:
                #read the file
                fileStream=open(file,"r")
                for line in fileStream:
                    if versionVar in line and "=" in line:
                        result=line.split("=")[-1].replace("\n","")
                        # print("Have found version value of "+versionVar+"="+result)
                        return result
    return None


#Manage the keystore
# if legacy keystores exist migrate them
#else generate the generic signin configuration
def manageKeyStore(repository):
    if foundLegacyKeyStore(repository):
        manageSigninAndJks.manageSpecificJKS(repository)
    else:
        manageSigninAndJks.generateSignInNormal(repository)

#Found if the project has a legacy jks
def foundLegacyKeyStore(repository):
    found=False
    #find if any jks file in the project    
    for file in scandir(repository):
        if path.isdir(file):
            found=foundLegacyKeyStore(file)
            if found:
                return found
        elif '.jks' in file.name.lower():
            return True  
    return found

#Update the build.gradle file
#with the dependencies bloc
#and the signin bloc
def updateGradleBuild(repository):
    #open the build.init.gradle
    buildInitial=open(repository+'\\app\\build_init.gradle',"r")
    #open the dependencies block generated before
    dependenciesBlock=open(repository+'\\dependenciesBlock.txt',"r")
    #open the signin block generated before
    signinBlock=open(repository+"\\app\\signinbloc.txt","r")
    #open the build.gradle, the final file you want to generate
    buildGradle=open(repository+'\\app\\build.gradle',"w+")
    #open licenses.yml
    # licencesYml=open(repository+'\\app\\licenses.yml',"w+")
    for line in buildInitial:
        if '#DEPENDENCIES_BLOCK' in line :
            buildGradle.write('apply from: \'./var_def_lib.gradle\'\n')
            buildGradle.write('dependencies {\n')
            for depLine in dependenciesBlock:
                buildGradle.write(depLine)
                # licencesYml.write('TODO for :'+depLine)            
            buildGradle.write('}\n')
        elif '#SIGNIN_BLOCK' in line :
            for signinLine in signinBlock:
                buildGradle.write(signinLine)    
        else:
            buildGradle.write(line)
    buildInitial.close()
    dependenciesBlock.close()
    buildGradle.close()
    # licencesYml.close


def insureLicencesYmlCompliant(repository):
    #https://stackoverflow.com/questions/45896398/peeking-stdout-of-subprocess-popen-objects-does-not-behave-correctly-am-i-missi
    # curdir=subprocess.run([repository+"\\gradlew.bat", "checkLicenses"], cwd=repository,stdout=PIPE,stderr=STDOUT)
    # print("toto")
    # # curdir = Popen(['pwd'], stdout=PIPE, stderr=STDOUT)
    # output=curdir.stdout.read()
    # outerror=curdir.stderr.read()
    # print(output)
    # print(outerror)
    # for line in output:
    #     print("OutputLine "+line)
    # for line in outerror:
    #     print("ErrorLine "+line)
    try:        
        #use the build task instead of checkLicenses directly else you'll miss dependencies
        #because checkLicenses is not working on up to date elements (need a build first)
        # output = subprocess.check_output(
        #     [repository+"\\gradlew.bat", "checkLicenses"], cwd=repository, stderr=subprocess.STDOUT, shell=True, 
        #     universal_newlines=True)
        output = subprocess.check_output(
            [repository+"\\gradlew.bat", "checkLicenses"], cwd=repository, stderr=subprocess.STDOUT, shell=True, 
            universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        print(RED+"\tcheckLicences failed, parsing the stderr to rebuild a new licenses.yml")        
        print(RED+"\tcheckLicences has failed with "+str(exc))
        inLicencesBlock=False
        copyrightHolder="unknown"
        #move the element
        os.rename(repository+'\\app\\licenses.yml', repository+'\\app\\licenses_init.yml')
        licencesYml=open(repository+'\\app\\licenses.yml',"w+")
        elementsAsList=exc.output.split('\n')
        print(RED+"\tThe stacktrace has "+str(len(elementsAsList))+" elements")
        for line in elementsAsList:
            line=line.replace('\n','')
            inLicencesBlock=('artifact:' in line or 'name' in line  or 'copyrightHolder:' in line or 'license' in line or 'licenseUrl' in line or 'url' in line)
            if(inLicencesBlock):
                #check if you have 
                if 'artifact:' in line:
                    #if contains 2 ": " remove the others than the first one because of yaml table array separator                   
                    if line.count(': ')!=1:
                        #die
                        splittedLine=line.split(': ')
                        firstWordLenght=len(splittedLine[0])+2
                        line=splittedLine[0]+': '+line[firstWordLenght:].replace(': ',':_')
                        # print(RED+"\tAfter removing the : this is what we obtain "+line)
                    licencesYml.write(line+'\n')

                    # print(CYAN+line)
                    #if the coordinate is known: use the file
                    #else
                    #grab the Holder
                    if('android.' in line or 'androidx.' in line or 'google.' in line):
                        copyrightHolder="Google, Inc."
                    else:
                        #Just use the coordinates as owner like this
                        #artifact: com.crashlytics.sdk.android:crashlytics:+
                        # should return crashlytics
                        #and - artifact: commons-cli:commons-cli:+
                        #returns commons-cli
                        copyrightTemp=line.split(':')[1]
                        try:
                            # print(RESET+copyrightTemp)
                            # print(RESET+str(copyrightTemp.split('.')))
                            if len(copyrightTemp.split('.')) == 1:
                                # print(RESET+"in the 0 case")
                                copyrightHolder=copyrightTemp+', Inc.'
                            else:
                                # print(RESET+"in the 1 case")
                                copyrightHolder=line.split(':')[1].split('.')[1]+', Inc.'
                            # print(CYAN+"copyrightHolder "+copyrightHolder)
                        except:
                            # print(RED+"Checking licences failed to extract copyrightHolder with the following line "+line)
                            copyrightHolder=copyrightTemp=line.split(':')[1]
                elif '#COPYRIGHT_HOLDER#' in line:                    
                    licencesYml.write(line.replace('#COPYRIGHT_HOLDER#',copyrightHolder.replace(': ',':_'))+'\n')
                    # print(CYAN+line.replace('#COPYRIGHT_HOLDER#',copyrightHolder))
                elif  'name:' in line  or 'license:' in line or 'licenseUrl:' in line or 'url:' in line:
                    #copy
                    #if contains 2 ": " remove the others than the first one because of yaml table array separator
                    if line.count(': ')!=1:
                        #die
                        splittedLine=line.split(': ')
                        firstWordLenght=len(splittedLine[0])+2
                        line=splittedLine[0]+': '+line[firstWordLenght:].replace(': ',':_')
                        print(RED+"\tAfter removing the : this is what we obtain "+line)
                    licencesYml.write(line+'\n')
                    # print(CYAN+line)
                

        #Still in th except
        # Now start parsing the answer, wait for > Task :app:checkLicenses FAILED and start the copy into licenses.yml
        # Copy the initial file        
        licencesYmlInit=open(repository+'\\app\\licenses_init.yml',"r")
        print(CYAN+"\tCopying the initial licenses file into the new one")
        for line in licencesYmlInit:
            line=line.replace('\n','')
            #copy
            licencesYml.write(line+'\n')
            # print(CYAN+line)
        #close file
        licencesYml.close()
        print(CYAN+"\tlicencesYml.close() done")
        licencesYmlInit.close()
        print(CYAN+"\tlicencesYmlInit.close() done")
        #delete old one
        os.remove(repository+'\\app\\licenses_init.yml') 
        print(GREEN+"\tall clean licenses have been completly managed")
    else:
        print(GREEN+"\tCheckLicenses worked directly")
    finally:
        print(BLUE+"\tlicences migration is done")

    # line=curdir.stderr.readline()
    # print(line)
    # while not line is None:
    #     print(line)
    # print(line)