#Import dependencies
from subprocess import call
from os import path
from ownStyle import GREEN,BLUE,BOLD,GREEN,RED,RESET,CYAN
#Push the new or update files
# call('git push origin master', shell = True)
#The command line will prompt you 
def runGitPushInCommandLine(repository):
    # print(repository)
    absRepo=path.abspath(repository)
    try:
        # print(absRepo)
        toto=call('git push --force',  cwd=absRepo, shell = True)
        # print(toto)
        if toto != 0:
            doitagain=input(RED+"try again ? [y (for yes) else ==no]\n")
            if doitagain in "y" or doitagain in "Y":
                runGitPushInCommandLine(repository)
                print(BLUE+"ok")
        else:
            print(GREEN+"Project has been pushed on GitHub, congrats.")

    except:
        doitagain=input("try aggain ? [y (for yes) else ==no]\n")
        if doitagain in "y" or doitagain in "Y":
            runGitPushInCommandLine(repository)
            print(BLUE+"ok")