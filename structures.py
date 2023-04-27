class Contest:
    def __init__(self,time,href):
        self.time = time
        self.href = href
        self.contest_id = href.split("/")[-1]

class Submission:
    def __init__(self,time,task,user,language,status,code):
        self.time = time
        self.code = code
        self.status = status
        self.user = user
        self.task = task
        self.language = language





