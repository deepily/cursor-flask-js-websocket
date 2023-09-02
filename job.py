import hashlib
import json
import util_jobs as uj

class Job:

    def __init__(self, push_counter, question):

        self.push_counter     = push_counter
        self.creation_date    = uj.get_current_datetime()
        self.id_hash          = hashlib.sha256((str(self.push_counter) + self.creation_date).encode()).hexdigest()
        
        self.completion_date  = None
        self.question         = question
        self.answer           = None
        self.code             = []
        self.solution_summary = None

    def complete(self, answer, code=[], solution_summary="" ):

        self.answer           = answer
        self.code             = code
        self.solution_summary = solution_summary
        self.completion_date  = uj.get_current_datetime()

    def __str__(self):

        return str({
            "creation_date"   : self.creation_date,
            "completion_date" : self.completion_date,
            "question"        : self.question,
            "answer"          : self.answer,
            "code"            : self.code,
            "solution_summary": self.solution_summary
        })
    
    def to_json(self):
        
        return json.dumps( self.__dict__ )
    
    def get_html(self):
        
        if self.answer is not None:
            return f"<li id='{self.id_hash}'>{self.creation_date} Q: {self.question} A: {self.answer}</li>"
        else:
            return f"<li id='{self.id_hash}'>{self.creation_date} Q: {self.question}</li>"
    
# Gratuitous change to test git
    

    