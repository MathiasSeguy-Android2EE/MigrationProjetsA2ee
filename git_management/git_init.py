# https://github.com/gitpython-developers/GitPython
# https://github.com/gitpython-developers/GitPython/blob/master/git/test/test_docs.py
# https://github.com/PyGithub/PyGithub
import os
import subprocess
from shutil import copyfile
import git
from git import Actor
from git import Repo
from github import Github
import sh_command
from ownStyle import GREEN, BLUE, BOLD, GREEN, RED, RESET, CYAN
#Managing private account : the file git_private_account.py is not in git
import importlib
privateAccount = importlib.util.find_spec("git_private_account")
if privateAccount is not None:
    import git_private_account
    print(GREEN+" Private accounts for jenkins have been found. Using them.")
    githubAccessToken = git_private_account.githubAccessToken
    githubActorName = git_private_account.githubActorName
    githubActorEMail = git_private_account.githubActorEMail
else:
    print(RED+" /!\\________Warning________/!\\")
    print(RED+" You have to create your accounts file for github:")
    print(RED+" ?\\MigrationProjectA2ee\\git_management\\git_private_account.py")
    githubAccessToken=input("What is github access token to use ?\n")
    githubActorName =input('What is your github name ?\n')
    githubActorEMail = input('What is your github email ?\n')
 
# using username and password
# g = Github("user", "password")
# os.system('.\ssh_agent_init.sh')
# or using an access token
# First create a Github instance:
g = Github(githubAccessToken)
actor = Actor(githubActorName, githubActorEMail)

ROOT_PYTHON_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = ROOT_PYTHON_PATH+'\\template'
REPO_NAME = 'not_set'


def listGitHubRepo():
    # Then play with your Github objects:
    print(BLUE+"List of repo on GitHub :"+str(g.get_user()))
    try:
        for repo in g.get_user().get_repos():
                print(BLUE+repo.name)
    except Exception as e: 
        print(e)

def isGitHubRepoExisting(name):
    # Then play with your Github objects:
    for repo in g.get_user().get_repos():
        if(repo.name in REPO_NAME):
            return True
    return False


def xcreateGitHubRepo(repoDescription,isPrivate):
        if repoDescription is None or len(repoDescription) == 0:
                repoDescription="A simple test to see if repo can be created by python"
        if not isGitHubRepoExisting(REPO_NAME):
                # Then play with your Github objects:
                g.get_user().create_repo(REPO_NAME,
                                        description=repoDescription,
                                        homepage='https://www.android2ee.com/en/',
                                        private=isPrivate,
                                        has_issues=False,
                                        has_wiki=False,
                                        has_downloads=False,
                                        has_projects=False,
                                        auto_init=False,
                                        allow_squash_merge=True,
                                        allow_merge_commit=True,
                                        allow_rebase_merge=True)


def updateGitConfig(repository):
        # Need to find the file
    rootConfigFile = open(TEMPLATE_PATH+'\\git_config.txt', "r")
    destinationFile = open(repository+'\\.git\\config', "w+")
    # and update it according to our generic config file
    for line in rootConfigFile:
        newLine = line.replace("#NameOfTheProject", REPO_NAME)
        destinationFile.write(newLine)
    destinationFile.close
    rootConfigFile.close


def intializeGitIgnore(repository):
    print(BLUE+"Initializing git ignore by copying our referent git ignore")
    # Need to find the file
    copyfile(TEMPLATE_PATH+'\\git_ignore_referent.txt',
             repository+'\\.gitignore')
    # and update it according to our generic config file


def createCommit(repository, fileName, commit_message):
    global repo
    repo = Repo(repository)
    index = repo.index
    new_file_path = os.path.join(repo.working_tree_dir, fileName)
    index.add([new_file_path])
    # commit by commit message and author and committer
    index.commit(commit_message, author=actor, committer=actor)


def commitAll(repository, commit_message):
    global repo
    index = repo.index
    repo.git.add('--all')
    # commit by commit message and author and committer
    index.commit(commit_message, author=actor, committer=actor)


def gitInit(repository):
    print(BLUE+'Running git Init on the Working dir:' + repository)
    print(BLUE+'with ROOT_PYTHON_PATH:' + ROOT_PYTHON_PATH)
    print(BLUE+'and TEMPLATE_PATH:' + TEMPLATE_PATH)
    global REPO_NAME
    REPO_NAME = repository.split('\\')[-1]
    print(BLUE+'RepoName is the following:' + REPO_NAME)
    # put you in the repo
    g = git.cmd.Git(repository)
    # initialize the repo
    g.init()
    print(REPO_NAME+' has been intialized by git')
    global repo
    repo = Repo(repository)
    print(REPO_NAME+' git repo is created')
    # change the config values
    updateGitConfig(repository)
    print(REPO_NAME+' configuration is up to date')
    # add gitIgnore
    intializeGitIgnore(repository)
    print(REPO_NAME+' gitIgnore has been defined is up to date')
    # commit gitIgnore
    createCommit(repository, '.gitignore', 'commit of the .gitignore file')
    print(REPO_NAME+' gitIgnore is commit')
    # Add all sources and commit
    commitAll(repository, 'first commit before migration of the project')
    print(REPO_NAME+' git --all done and comit is done')


def gitCreateAndPush(repository,repoDescription):
    global REPO_NAME
    REPO_NAME = repository.split('\\')[-1]
    print(BLUE+'RepoName is the following:' + REPO_NAME)
    # put you in the repo
    g = git.cmd.Git(repository)
    try:
        # create the GitHub project
        if os.path.exists(repository+"\\githubPrivate.flag"):
                xcreateGitHubRepo("Github repository for the project "+REPO_NAME, True)
        else:
                xcreateGitHubRepo("Github repository for the project "+REPO_NAME, False)
        # push
        g.push()
    except Exception as e: 
        print(RED+str(e))
        print(RED+'Push doesn\'t work, you need to push '+REPO_NAME)
        #launch git bash in the repo
        sh_command.runGitPushInCommandLine(repository)
        

# print('test')
# listGitHubRepo()