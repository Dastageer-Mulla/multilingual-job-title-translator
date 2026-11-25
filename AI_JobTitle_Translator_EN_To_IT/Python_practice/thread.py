import time

def task(name):
    print(f"Starting task {name}...")
    time.sleep(2) # Simulating a 2-second download
    print(f"Task {name} finished!")

start_time = time.time()

task("A")
task("B")

end_time = time.time()
print(f"Total time taken: {round(end_time - start_time)} seconds")



print("====================== using Thread ======================")
import threading
import time

def task(name):
    print(f"Starting task {name}...")
    time.sleep(2) # Simulating a 2-second download
    print(f"Task {name} finished!")

# 1. Create the thread objects
thread1 = threading.Thread(target=task, args=("A",))
thread2 = threading.Thread(target=task, args=("B",))

start_time = time.time()

# 2. Start the threads
thread1.start()
thread2.start()

# 3. Wait for both threads to finish before moving to the next line
thread1.join()
thread2.join()

end_time = time.time()
print(f"Total time taken: {round(end_time - start_time)} seconds")