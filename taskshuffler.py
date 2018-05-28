import numpy as np
import math
import random
import csv

class Task:
    def __init__(self, wcet, period, name, v):
        self.wcet = wcet
        self.period = period
        self.name = name
        self.v = v
    def __str__(self):
        return "wcet = " + str(self.wcet) + " period = " + str(self.period)

class Job:
    def __init__(self, wcet, deadline, period, name, v):
        self.remain_work = wcet
        self.deadline = deadline
        self.period = period
        self.wcet = wcet
        self.name = name
        self.v = v
    def __str__(self):
        return "name: " + self.name +" remain = " + str(self.remain_work) + " deadline = " + str(self.deadline) + " v = " + str(self.v)


def taskshuffler(ready_queue, t):
     M = [0 for _ in range(len(ready_queue))]
     stack = []

     if ready_queue[0].v <= 0:
         return 0, ready_queue[0].remain_work, 0

     for idx in range(len(ready_queue)):
         if ready_queue[idx].v > 0:
             stack.append(idx)
         else:
             while len(stack) > 0:
                 head = stack.pop()
                 M[head] = idx
             stack.append(idx)
     while len(stack) > 0:
         head = stack.pop()
         M[head] = len(ready_queue)

     candidate = [0]

     for idx in range(1, len(ready_queue)):
         if M[idx] >= M[0]:
             candidate.append(idx)
         if ready_queue[idx].v <= 0:
            break

     idx = random.randint(0, len(candidate)-2)
     #calculate the entropy
     n = len(candidate)

     if idx == 0:
         return 0, ready_queue[0].remain_work, math.log(n, 2)
     else:
         minv = 100000
         for i in range(idx):
             if i != len(ready_queue-1):
                minv = min(minv, ready_queue[i].v)
         delta = random.randint(1, minv)
         return idx, delta, math.log(n, 2)

def test(taskset):
    task_list = []
    log = open("log_ts.txt", "w")
    maxhp = 0
    count = 0
    for i in range(len(taskset)):
        #calculate the v
        v = 0
        for j in range(i):
            v += (math.ceil(taskset[i][1] / taskset[j][1]) + 1) * taskset[j][0]
        v = taskset[i][1] - taskset[i][0] - v
        t = Task(taskset[i][0], taskset[i][1], str(i), v)
        maxhp = max(maxhp, t.period)
        task_list.append(t)

    hyper_period = maxhp
    ready_queue = []
    time = 0
    period = maxhp
    entropy_total = 0
    delta = 0
    current_idx = None
    current_job = None
    while time < hyper_period:
        release = False
        if time % period == 0:
            # print("period_entropy: ", entropy_total)
            entropy_total = 0

        # check if a task misses deadline
        for job in ready_queue:
            if job.deadline < time:
                print("time: ", time)
                print("%s misses deadline!" % job.name, job)
                log.write("--miss--\n")
                for j in ready_queue:
                    log.write(j.__str__()+ "\n")
                exit(-1)

        for task in task_list:
            if time % task.period == 0:
                ready_queue.append(Job(task.wcet, task.period + time, task.period, task.name, task.v))
                log.write("-APPEND-" + ready_queue[-1].__str__() + "\n")
                release = True

        ready_queue.sort(key=lambda x: int(x.name))
        # A job release or job finishes
        if release == True or current_job.remain_work <= 0 or delta == time:
            if current_job != None and current_job.remain_work <= 0:
                ready_queue.remove(current_job)
            current_idx, delta, entropy = taskshuffler(ready_queue, t)
            current_job = ready_queue[current_idx]
            delta = delta + time
            entropy_total += entropy

        log.write("T:" + str(time) + " " + str(current_idx) + " " + current_job.__str__() + "\n")
        log.write("--V subtraction:-- \n")
        for i in range(current_idx):
            ready_queue[i].v -= 1
            log.write(ready_queue[i].__str__() + "\n")
        log.write("--V subtraction END-- \n\n")
        current_job.remain_work -= 1
        time += 1
    return entropy_total

def UUniFastDiscard(n, u):
    # Classic UUniFast algorithm:
    utilizations = []
    sumU = u
    for i in range(1, n):
        nextSumU = sumU * random.random() ** (1.0 / (n - i))
        utilizations.append(sumU - nextSumU)
        sumU = nextSumU
    utilizations.append(nextSumU)

    # If no task utilization exceeds 1:
    if not [ut for ut in utilizations if ut > 1]:
        return utilizations

if __name__ == "__main__":
    with open("taskshuffler.csv", "w", newline="") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["n", "u", "entropy"])
        for n in range(5, 16, 2):
            u = 0.5
            while u <= 0.95:
                for _ in range(20):
                    print("u=%f, n=%f\n"%(u, n))
                    period = np.random.randint(8, 12, size=n)
                    period = [2<<x for x in period]
                    utilization = []
                    flag = True
                    while flag:
                        utilization = UUniFastDiscard(n, u)
                        if len(utilization) > 0:
                            flag = False
                        wcet = [int(x*y) for x,y in zip(period, utilization)]
                        if 0 in wcet:
                            flag = True
                    taskset = []
                    for w,p in zip(wcet, period):
                        taskset.append([w, p])
                    taskset.append([1<<12, 1<<12])
                    taskset.sort(key=lambda x: x[1])
                    entropy = test(taskset)
                    csvwriter.writerow([n, u, entropy])
                u += 0.05

