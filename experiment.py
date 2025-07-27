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
        return f"The number of samples per average is {self.num_iterations}, start time is {datetime.datetime.utcfromtimestamp(self.start).strftime('%Y-%m-%d %H:%M:%S')}, end time is {datetime.datetime.utcfromtimestamp(self.end).strftime('%Y-%m-%d %H:%M:%S')}, and recipient email address is {self.email}"
    
    def duration(self):
        duration = self.end - self.start
        duration = divmod(duration, 3600)[0]

        return duration
    
    # Create ID is generally not used, instead to just get a placeholder hash 
    # value. In the backend, a hash value is made using start, end, and email 
    # values, and this is assigned to the experiment object. Hash is not 
    # one-to-one in the mathematical sense, but two objects of the equal 
    # compareable values should have the same hash. For now, let the backend 
    # assign the hash value, and this function here hopefully creates the same 
    # one. 
    def create_ID(self):
        return hash((self.start, self.end, self.email))




    
    