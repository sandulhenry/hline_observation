import datetime as datetime
import string

class Experiment: 
    status: int = 0 #0 inc; 1 in progress; 2 complete; 3 failed?

    def __init__(self, num_iterations: int, start: int, end: int, email: str):
        self.num_iterations = num_iterations # number of iterations per average
        self.start = start
        self.end = end
        self.email = email
        self.ID = self.create_ID()
    
    def __str__(self):
        return f"The number of samples per average is {self.num_iterations},\
        start time is {datetime.datetime.utcfromtimestamp(self.start).strftime('%Y-%m-%d %H:%M:%S')},\
        end time is {datetime.datetime.utcfromtimestamp(self.end).strftime('%Y-%m-%d %H:%M:%S')},\
        recipient email address is {self.email}"
    
    def duration(self):
        duration = self.end - self.start
        duration = divmod(duration, 3600)[0]

        return duration
    
    def create_ID(self):
        return hash(self.start)




    
    