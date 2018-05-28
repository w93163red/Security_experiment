import numpy as np
import math
import random
import csv

class Task:
    def __init__(self, wcet, period, name):
        self.wcet = wcet
        self.period = period
        self.name = name
    def __str__(self):
        return "wcet = " + str(self.wcet) + " period = " + str(self.period)

class Job:
    def __init__(self, wcet, deadline, period, name):
        self.remain_work = wcet
        self.deadline = deadline
        self.period = period
        self.wcet = wcet
        self.name = name
    def __str__(self):
        return "name: " + self.name +" remain = " + str(self.remain_work) + " deadline = " + str(self.deadline)

def test(delta, taskset):
    task_list = []
    maxhp = 0
    count = 0
    for task in taskset:
        t = Task(task[0], task[1], str(count))
        maxhp = max(maxhp, t.period)
        task_list.append(t)
        count += 1

    hyper_period = maxhp
    ready_queue = []
    time = 0
    period = maxhp
    entropy_total = 0
    select = None
    # simulate the scheduler
    while time < hyper_period:
        if time % period == 0:
            # print("period_entropy: ", entropy_total)
            entropy_total = 0

        # check if a task misses deadline
        for job in ready_queue:
            if job.deadline < time:
                print("time: ", time)
                print("%s misses deadline!" % job.name)
                exit(-1)

        for task in task_list:
            if time % task.period == 0:
                ready_queue.append(Job(task.wcet, task.period + time, task.period, task.name))

        if select != None:
            select.remain_work -= 1
            if select.remain_work <= 0:
                ready_queue.remove(select)
                select = None

        if time % delta != 0 and select != None and select.remain_work > 0:
            time += 1
            continue


        # print("time: ", time)

        ready_queue.sort(key=lambda x: x.deadline)

        # Calculate the budget
        budget = []
        for i in range(0, len(ready_queue)):
            b = ready_queue[i].deadline - time
            r1 = 0
            r2 = 0
            for j in range(0, i):
                r1 += ready_queue[j].remain_work
                r2 += math.ceil((ready_queue[i].deadline - ready_queue[j].deadline) / ready_queue[j].period) * \
                     ready_queue[j].wcet
            b = b - r1 - r2
            budget.append(b)
        # print("Budget: ", budget)
        # random selection
        pi = []
        str_ready = ""
        flag = False
        flag_job = None

        for i in range(0, len(ready_queue)):
            job = ready_queue[i]
            str_ready += job.name + " "
            # print(job)
            pi.append(job.remain_work / budget[i])
            # this job must be executed, otherwise it will miss deadline
            if job.remain_work / budget[i] == 1:
                flag_index = i
                flag = True

        # print("READY_QUEUE: ", str_ready)

        # print("Possibility: ", pi)

        if flag:
            #print("TASKS ARE GOING TO MISS DEADLINE")
            new_r_queue = ready_queue[0: flag_index + 1]
            new_pi = pi[0: flag_index + 1]
            new_pi = np.array(new_pi)
            select = np.random.choice(new_r_queue, p=new_pi / new_pi.sum())
            entropy = 0.0
            for i in range(0, new_pi.size):
                pp = new_pi[i] / new_pi.sum()
                entropy += -pp * math.log(pp, 2)
                entropy_total += entropy

            # print(select)
            # print("---------------------\n")
            continue

        entropy = 0
        if len(pi) != 0:
            pi = np.array(pi)
            for n in pi:
                if n < 0:
                    print(pi)
                    exit(-3)
            select = np.random.choice(ready_queue, p=pi / pi.sum())
            entropy = 0.0
            for i in range(0, pi.size):
                pp = pi[i] / pi.sum()
                entropy += -pp * math.log(pp, 2)
                entropy_total += entropy


        # print(time, select)
        # print("ENTROPY= ", entropy)
        time += 1
        # print("---------------------\n")

    # print("ENTROPY_TOTAL:", entropy_total)
    # with open("t2t3t6_5.txt","a") as f:
    #     f.write(str(entropy_total) + "\n")
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
    with open("result2.csv", "w", newline="") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["n", "u", "entropy"])
        for n in range(5, 16, 2):
            u = 0.90
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
                    entropy = test(8, taskset)
                    csvwriter.writerow([n, u, entropy])
                u += 0.05
