import time

# Thread to simulate traffic light
class LightTimer:
    def __init__(self, delay=0.5):
        self.time_to_sleep = delay
    
    def lightChanger(self, redlight_on, end_program):
        color = "green"
        while True:
            if end_program.is_set():
                return
            if redlight_on.is_set():
                if color == "green":
                    print("green light")
                    color = "yellow"  
                    redlight_on.clear() 
                    
                time.sleep(self.time_to_sleep)
            else:
                if color == "yellow":
                    print("yellow light")
                    color = "green" 
                else:
                    print("red light")
                    redlight_on.set()
                time.sleep(self.time_to_sleep)