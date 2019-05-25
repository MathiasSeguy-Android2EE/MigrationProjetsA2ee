
class JenkinsJob:
    NOT_DEFINED='NOT_DEFINED'
    name=NOT_DEFINED
    branch=NOT_DEFINED
    tasks=NOT_DEFINED
    def __init__(self,name,branch,tasks):
        self.name=name
        self.branch=branch
        self.tasks=tasks

   
    def __str__(self):
     return ''+self.name+':'+self.branch+":"+self.tasks
    