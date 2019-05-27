from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN

#Aims to represents a library dependency
class Dependencies:
    #Constants as to be accessed by Dependencies
    TYPE_NORMAL    ='wNormal'
    TYPE_FILETREE='wFileTree'
    TYPE_TRANSITIVE='wTransitive'
    TYPE_WEIRD     ='wWeird'
    TYPE_ERROR     ='wError'
    TYPE_COMMENTED='wComment'
    NOT_DEFINED='NOT_DEFINED'
    NOT_DEFINED_VERSION=-1
    #Normal line to parse look like
    # androidTestImplementation "androidx.test.ext:junit:${androidXJunitVersion}"
    # implementation "com.facebook.stetho:stetho-okhttp3:1.5.0"
    #then type is androidTestImplementation or implementation or ...
    #Weird lines are
    # implementation fileTree(dir: 'libs', include: ['*.jar'])
    # implementation('com.crashlytics.sdk.android:crashlytics:2.9.3@aar') {
    #     transitive = true;
    # }
    #also type can be weird and only raw value is defined. type is wFileTree or wTransitive
    typeValue=NOT_DEFINED
    type=NOT_DEFINED
    rawValue=NOT_DEFINED
    coordinate=NOT_DEFINED
    version=NOT_DEFINED_VERSION
    def __init__(self,line):
        self.parseLine(line)
        pass
    def __str__(self):
     return ''+self.type+', '+self.typeValue+" "+self.coordinate+"  ::  "+str(self.version)
    #  return 'type ='+self.type+', typeValue ='+self.typeValue+', raw='+self.rawValue+", coordinate="+self.coordinate+", version="+str(self.version)
    
    #Parse the initial line to spread the information in
    #the dependency class format
    def parseLine(self,line):
        line=line.replace('\'','\"')
        #Replace compile by implementation
        #this is not that simple because grouid or artifactid can contains "compile" set of letters
        # print("line.split() "+str(line.split(" ")))
        firstNotNullIndex=0
        splittedLine=line.split(" ")
        while splittedLine[firstNotNullIndex] == None or len(splittedLine[firstNotNullIndex])==0:
            firstNotNullIndex=firstNotNullIndex+1
        if('ompile' in splittedLine[firstNotNullIndex] ):
            #replace
            templine=splittedLine[firstNotNullIndex].replace('compile','implementation')
            templine=templine.replace('Compile','Implementation')
            # print("templine = "+templine)
            line= templine+" "
            for subline in splittedLine[firstNotNullIndex+1:]:
                # print("Adding subline "+subline)
                line = line + subline + " "
        print(BLUE+"\t "+line.replace("\n",""))
        #then you can parse your line
        if len(line.split(':')) != 3:
            #print('\n')            
            # print('Error case')
            #print('line      ='+line.replace("\n",""))
            self.analyseError(line)
            self.printParsing(line)
            return
        if '//' in line:
            #print('\n')            
            # print('Comments case')
            self.type=Dependencies.TYPE_COMMENTED
            self.rawValue=Dependencies.TYPE_COMMENTED
            self.version=Dependencies.NOT_DEFINED_VERSION
            self.coordinate=Dependencies.TYPE_COMMENTED
            self.printParsing(line)
            return
        if 'fileTree' in line:
            #print('\n')            
            # print('fileTree case')
            self.type=Dependencies.TYPE_FILETREE
            self.rawValue=line.replace("\n","")
            self.version=Dependencies.NOT_DEFINED_VERSION
            self.coordinate=Dependencies.NOT_DEFINED
            self.printParsing(line)
            return
        if '{' in line and not '}' in line: 
            #print('\n')            
            # print('Transitive case')
            self.type=Dependencies.TYPE_TRANSITIVE
            self.rawValue=line.replace("\n","")
            self.typeValue=line.split(' ')[-2]
            self.rawValue=line.replace("\n","")
            rawCoord=line.split(' ')[-1]
            rawCoordNormalized=rawCoord.replace("'","").replace("\n","")
            self.version=rawCoordNormalized.split(':')[-1]
            self.coordinate=rawCoordNormalized.replace(self.version,'')
            self.printParsing(line)
            return
        
        # androidTestImplementation "androidx.test.ext:junit:${androidXJunitVersion}"
        #print('\n')            
        # print('Normal case')
        self.type=Dependencies.TYPE_NORMAL
        self.typeValue=line.split(' ')[-2]
        self.rawValue=line.replace("\n","")
        #print('line.split      ='+str(line.split(' ')))
        rawCoord=line.split(' ')[-1]
        #print('rawCoord      ='+rawCoord.replace("\n",""))
        rawCoordNormalized=rawCoord.replace("\"","").replace("\n","")
        #print('rawCoordNormalized      ='+rawCoordNormalized)
        self.version=rawCoordNormalized.split(':')[-1]
        self.coordinate=rawCoordNormalized.replace(self.version,'')
        self.printParsing(line)

    def printParsing(self, line):
        #print('line      ='+line.replace("\n",""))
        #print('lineSplit ='+str(line.split(' ')))
        # TYPE_NORMAL    ='wNormal'
        # TYPE_FILETREE='wFileTree'
        # TYPE_TRANSITIVE='wTransitive'
        # TYPE_WEIRD     ='wWeird'
        # TYPE_ERROR     ='wError'
        # TYPE_COMMENTED='wComment'
        # NOT_DEFINED='NOT_DEFINED'
        # NOT_DEFINED_VERSION=-1
        if self.type == Dependencies.NOT_DEFINED:
            #Do nothing
            pass
        if self.type == Dependencies.TYPE_NORMAL:
            print(GREEN+'\tObject    ='+str(self))
        if self.type == Dependencies.TYPE_ERROR or self.type == Dependencies.TYPE_WEIRD:
            print(RED+'\tObject    ='+str(self))
        
    def analyseError(self,line):
        self.type=Dependencies.TYPE_ERROR
        self.rawValue=line.replace("\n","")
        # print('analayse error: '+line.replace('\n',''))
        pass

