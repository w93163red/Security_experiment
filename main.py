import numpy as np
import math
class Task:
    def __init__(self, wcet, period, name):
        self.wcet = wcet
        self.period = period
        self.name = name
    def __str__(self):
        return "wcet = " + str(self.wcet) + " period = " + str(self.period)


class Job:
    def __init__(self, wcet, period, name):
        self.remain_work = wcet
        self.deadline = period
        self.name = name
    def __str__(self):
        return "name: " + self.name +" remain = " + str(self.remain_work) + " deadline = " + str(self.deadline)

if __name__ == "__main__":
    t1 = Task(1.0, 4.0, "t1")
    t2 = Task(3.0, 8.0, "t2")
    t3 = Task(3.0, 16.0, "t3")
    t4 = Task(1.0, 16.0, "t4")

    task_list = [t1, t2, t3, t4]

    for task in task_list:
        print(task)
    print("\n")

    hyper_period = 32
    delta = 0.5
    ready_queue = []
    time = 0
    period = 16
    entropy_total = 0
    #simulate the scheduler
    while time < hyper_period:
        if time % period == 0:
            print("period_entropy: ", entropy_total)
            entropy_total = 0

        print ("time: ", time)
        #check if a task misses deadline
        for job in ready_queue:
            if job.deadline < time:
                print("%s misses deadline!" % job.name)
                exit(-1)

        for task in task_list:
            if time % task.period == 0:
                ready_queue.append(Job(task.wcet, task.period + time, task.name))

        ready_queue.sort(key=lambda x: x.deadline)

        #random selection
        pi = []
        str_ready = ""
        flag = False
        flag_job = None

        for job in ready_queue:
            str_ready += job.name + " "
            pi.append(job.remain_work / (job.deadline - time))
            #this job must be executed, otherwise it will miss deadline
            if job.remain_work / (job.deadline - time) == 1:
                print(job)
                flag_job = job
                flag = True

        print("READY_QUEUE: ", str_ready)

        print("Possibility: ", pi)


        if flag:
            print(flag_job)
            print("MUST BE DONE!")
            flag_job.remain_work -= delta
            time += delta
            ready_queue.remove(flag_job)
            print("---------------------\n")
            continue

        entropy = 0
        if len(pi) != 0:
            pi = np.array(pi)
            select = np.random.choice(ready_queue, p= pi / pi.sum())
            entropy = 0.0
            for i in range(0, pi.size):
                pp = pi[i] / pi.sum()
                entropy += -pp * math.log(pp)
                entropy_total += entropy
            select.remain_work -= delta
            if select.remain_work == 0:
                ready_queue.remove(select)
            print(select)

        print("ENTROPY= ", entropy)
        time += delta
        print("---------------------\n")

    print("ENTROPY_TOTAL:", entropy_total)
