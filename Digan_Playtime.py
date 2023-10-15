from pulp import *
import pandas as pd

# Upload csv with task ID and hours per task
pm_csv = pd.read_csv('ProjectManagement_Tasks.csv')
pm_csv= pm_csv[pm_csv.taskID != 'D']
# Create a dictionary of the activities and their durations
activities = dict(zip(pm_csv.taskID, pm_csv.Expected))

# Create a list of the activities
activities_list = list(activities.keys())

# Create a dictionary of the activity precedences
precedences = {'A': [], 'B': [], 'C':['A'],
               'D1': ['A'], 'D2': ['D1'], 'D3':['D1'], 'D4':['D2', 'D3'], 'D5':['D4'], 'D6':['D4'], 'D7': ['D6'], 'D8':['D5', 'D7'],
              'E': ['B', 'C'], 'F': ['D8', 'E'], 'G': ['A', 'D8'], 'H': ['F', 'G']}

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)
# Create the LP variables
start_times = {activity: LpVariable(f"start_{activity}", 0, None) for activity in activities_list}
end_times = {activity: LpVariable(f"end_{activity}", 0, None) for activity in activities_list}


# Add the constraints
for activity in activities_list:
    print(activity)
    prob += end_times[activity] == start_times[activity] + activities[activity], f"{activity}_duration"
    print (prob)
    for predecessor in precedences[activity]:
        prob += start_times[activity] >= end_times[predecessor], f"{activity}_predecessor_{predecessor}"
        print(prob)


# Set the objective function
prob += lpSum([end_times[activity] for activity in activities_list]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for activity in activities_list:
    if value(start_times[activity]) == 0:
        print(f"{activity} starts at time 0")
    if value(end_times[activity]) == max([value(end_times[activity]) for activity in activities_list]):
        print(f"{activity} ends at {value(end_times[activity])} days in duration")

# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)
