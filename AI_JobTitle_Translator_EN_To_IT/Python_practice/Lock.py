# Example WITHOUT a Lock (The Problem)
# Here, two threads try to increase a counter 50 times. Without a lock, they will clash.

import threading

counter = 0

def increase():
    global counter
    for _ in range(100000):
        counter += 1

# Create two threads
t1 = threading.Thread(target=increase)
t2 = threading.Thread(target=increase)

t1.start()
t2.start()

t1.join()
t2.join()

print(f"Final counter value: {counter}")


# Example WITH a Lock (The Solution)
# We use threading.Lock() to make sure only one thread touches the counter at a time.

import threading

counter = 0
# Create a Lock object
count_lock = threading.Lock()


def increase():
    global counter
    for _ in range(100000):
        # 1. Acquire the lock (Get the key)
        count_lock.acquire()

        counter += 1

        # 2. Release the lock (Give the key back)
        count_lock.release()


t1 = threading.Thread(target=increase)
t2 = threading.Thread(target=increase)

t1.start()
t2.start()

t1.join()
t2.join()

print(f"Final counter value: {counter}")