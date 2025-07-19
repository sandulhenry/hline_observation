import requests
import time
import datetime as datetime
from observation import timeexp
from experiment import Experiment
from makeemail import send_email
from plotting_tools import plot_all
import os

SERVER_URL = "https://hydrogenline-backend-f7becb704ae8.herokuapp.com/"

# Run experiment is what carries out, compiles results, and emails them to the 
# user. The use of an Experiment object, from experiment.py, is convenient for
# its string method, and having all the variables associated with a function in
# one place. We also need to make a valid folder inside the results storage, to 
# garuntee that pyplot.savefig() will not run into problems when it tries to save
def run_experiment(exp):
    
    print("Running on experiment with parameters ", exp)

    try: 
        timeexp(start = exp.start, 
                end = exp.end, 
                NFFT = 1024, 
                length_avg = exp.num_iterations)
        
        newpath = "/home/pi/Documents/HLINE/hline_observation/observations_img/" + str(exp.ID) 
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        plot_all("/home/pi/Documents/HLINE/hline_observation/observations_raw", exp.ID)

        send_email(recipient = exp.email, hash = exp.ID)

        print("Complete? marking done.")
        requests.post(f"{SERVER_URL}/finished/{currExp.ID}")
    except:
        print("Error running on expirement", exp)
        requests.post(f"{SERVER_URL}/failed/{currExp.ID}")

# Poll and Run is the primary function within this code. It polls the backend 
# every 5 minutes, and checks for the next task. If it is within its valid time-
# frame, it runs the experiment, and the user should receive their email. This 
# problem of a experiment being defined, and having to wait 5 minutes is avoided 
# in the backend. An experiment is still valid 5 minutes past its start date, 
# therefore the function polling every x minutes works. 
def poll_and_run():
    while True:
        try:
            resp = requests.get(f"{SERVER_URL}/next_task", timeout=10)
            if resp.status_code == 200:
                task = resp.json()
                now = datetime.datetime.now().timestamp()

                currExp = Experiment(num_iterations = task['num_iterations'], 
                                    start = task['start'],
                                    end = task['end'],
                                    email = task['email'])

                currExp.ID = task['id'] # update ID to match, hash is not internally one-to-one

                print("Found next expirement, it is currently", currExp)
                if currExp.start <= now <= currExp.end:
                    print(f"Current time {datetime.datetime.utcfromtimestamp(now)} is within experiment timeframe.")
                    requests.post(f"{SERVER_URL}/in_prog/{currExp.ID}")
                    run_experiment(currExp)
                else:
                    print(f"Experiment not active yet or expired. Now: {datetime.datetime.utcfromtimestamp(now)}, start: {task['start_utc']}, end: {task['end_utc']}")
            elif resp.status_code == 204:
                print("No pending experiments at this time.")
            else:
                print(f"Unexpected server response: {resp.status_code} - {resp.text}")
        except requests.RequestException as e:
            print(f"Error contacting server: {e}")
        
        print("Waiting 1 minute(s) before next poll...")
        time.sleep(60)  # 1 minutes

if __name__ == "__main__":
    poll_and_run()
