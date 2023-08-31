import util_jobs as uj

class Job:

    def __init__(self, question):

        self.creation_date    = uj.get_current_datetime()
        self.completion_date  = None
        self.question         = question
        self.answer           = None
        self.code             = None
        self.solution_summary = None

    def complete(self, answer, code, solution_summary ):

        self.answer           = answer
        self.code             = code
        self.solution_summary = solution_summary
        self.completion_date  = uj.get_current_datetime()

    def __str__(self):

        return {
            "creation_date"   : self.creation_date,
            "completion_date" : self.completion_date,
            "question"        : self.question,
            "answer"          : self.answer,
            "code"            : self.code,
            "solution_summary": self.solution_summary
        }
    
    
    

    