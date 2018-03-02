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
    def __init__(self, wcet, deadline, period, name):
        self.remain_work = wcet
        self.deadline = deadline
        self.period = period
        self.wcet = wcet
        self.name = name
    def __str__(self):
        return "name: " + self.name +" remain = " + str(self.remain_work) + " deadline = " + str(self.deadline)

def test(delta):
    t1 = Task(1.0, 4.0, "t1")
    t2 = Task(3.0, 8.0, "t2")
    t3 = Task(3.0, 16.0, "t3")
    t4 = Task(1.0, 16.0, "t4")

    task_list = [t1, t2, t3, t4]

    for task in task_list:
        print(task)
    print("\n")

    hyper_period = 32
    ready_queue = []
    time = 0
    period = 16
    entropy_total = 0
    # simulate the scheduler
    while time < hyper_period:
        if time % period == 0:
            print("period_entropy: ", entropy_total)
            entropy_total = 0

        print("time: ", time)
        # check if a task misses deadline
        for job in ready_queue:
            if job.deadline < time:
                print("%s misses deadline!" % job.name)
                exit(-1)

        for task in task_list:
            if time % task.period == 0:
                ready_queue.append(Job(task.wcet, task.period + time, task.period, task.name))

        if time % delta != 0:
            time += 0.1
            continue

        ready_queue.sort(key=lambda x: x.deadline)

        # Calculate the budget
        budget = []
        for i in range(0, len(ready_queue)):
            b = ready_queue[i].deadline - time
            r1 = 0
            r2 = 0
            for j in range(0, i):
                r1 = ready_queue[i].remain_work
                r2 = math.ceil((ready_queue[i].deadline - ready_queue[j].deadline) / ready_queue[j].period) * \
                     ready_queue[j].wcet
            b = b - r1 - r2
            budget.append(b)

        # random selection
        pi = []
        str_ready = ""
        flag = False
        flag_job = None

        for i in range(0, len(ready_queue)):
            job = ready_queue[i]
            str_ready += job.name + " "
            pi.append(job.remain_work / budget[i])
            # this job must be executed, otherwise it will miss deadline
            if job.remain_work / budget[i] == 1:
                flag_index = i
                flag = True

        print("READY_QUEUE: ", str_ready)

        print("Possibility: ", pi)

        if flag:
            print("TASKS ARE GOING TO MISS DEADLINE")
            new_r_queue = ready_queue[0: flag_index + 1]
            new_pi = pi[0: flag_index + 1]
            new_pi = np.array(new_pi)
            select = np.random.choice(new_r_queue, p=new_pi / new_pi.sum())
            entropy = 0.0
            for i in range(0, new_pi.size):
                pp = new_pi[i] / new_pi.sum()
                entropy += -pp * math.log(pp, 2)
                entropy_total += entropy
            select.remain_work -= delta
            if select.remain_work <= 0:
                ready_queue.remove(select)
            print(select)
            time += delta
            print("---------------------\n")
            continue

        entropy = 0
        if len(pi) != 0:
            pi = np.array(pi)
            select = np.random.choice(ready_queue, p=pi / pi.sum())
            entropy = 0.0
            for i in range(0, pi.size):
                pp = pi[i] / pi.sum()
                entropy += -pp * math.log(pp, 2)
                entropy_total += entropy
            select.remain_work -= delta
            if select.remain_work <= 0:
                ready_queue.remove(select)
            print(select)

        print("ENTROPY= ", entropy)
        time += 0.1
        print("---------------------\n")

    print("ENTROPY_TOTAL:", entropy_total)



if __name__ == "__main__":
    test(delta=0.3)

