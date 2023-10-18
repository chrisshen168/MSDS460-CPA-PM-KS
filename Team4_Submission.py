from pulp import *
import pandas as pd


# Upload csv with task ID and hours per task
pm_csv = pd.read_csv('ProjectManagement_Tasks.csv')
pm_csv = pm_csv[pm_csv.taskID != 'D']

# Define a function to perform sensitivity analysis
def perform_sensitivity_analysis(scenario_name):
    print('\n\n')
    print('=========================={}=========================='.format(scenario_name))
    data = pm_csv[scenario_name]
    
    # Create a dictionary of the activities and their durations
    activities = dict(zip(pm_csv.taskID, data))

    # Create a list of the activities
    activities_list = list(activities.keys())

    # Create a dictionary of the activity precedences
    precedences = {'A': [], 'B': [], 'C':['A'],
               'D1': ['A'], 'D2': ['D1'], 'D3':['D1'], 'D4':['D2', 'D3'], 'D5':['D4'], 
               'D6':['D4'], 'D7': ['D6'], 'D8':['D5', 'D7'],
              'E': ['B', 'C'], 'F': ['D8', 'E'], 'G': ['A', 'D8'], 'H': ['F', 'G']}

    # Create the LP problem
    prob = LpProblem(f"Critical Path ({scenario_name})", LpMinimize)

    # Create the LP variables
    start_times = {activity: LpVariable(f"start_{activity}", 0, None) for activity in activities_list}
    end_times = {activity: LpVariable(f"end_{activity}", 0, None) for activity in activities_list}

    
    # Define the objective function to minimize the maximum end time of final tasks
    prob += lpSum([end_times[activity] for activity in ['H']]), "minimize_end_times"

    # Add the constraints
    for activity in activities_list:
        prob += end_times[activity] == start_times[activity] + activities[activity], f"{activity}_duration"
        for predecessor in precedences[activity]:
            prob += start_times[activity] >= end_times[predecessor], f"{activity}_predecessor_{predecessor}"

   
    # Solve the LP problem
    status = prob.solve()

    # Print the results for this scenario
    print(f"{scenario_name} Projection:")
    for activity in activities_list:
        if value(start_times[activity]) == 0:
            print(f"{activity} starts at time 0")
        if value(end_times[activity]) == max([value(end_times[activity]) for activity in activities_list]):
            duration_hours = value(end_times[activity])
            print(f"{activity} takes {duration_hours} hours in duration")
            print(f"Project takes {duration_hours} hours in duration")
            print(f"Project takes {duration_hours / 8} days in duration")
            print(f"Project takes {duration_hours / 40} weeks in duration")
            print(f"Project takes {duration_hours / 40 / 4} months in duration")
            print(f"Project costs {duration_hours * 50} in Wages")
            print(f"Project costs {duration_hours * 50 * 1.25} to the company (includes Markup)")

    # Print sensitivity analysis for shadow prices
    print("\nSensitivity Analysis (Shadow Prices):")
    for activity in activities_list:
        shadow_price = prob.constraints[f"{activity}_duration"].pi
        print(f"Shadow Price for {activity}_duration: {shadow_price}")

    # Print sensitivity analysis for slack values
    print("\nSensitivity Analysis (Slack Values):")
    for constr in prob.constraints:
        if 'predecessor' in constr:
            slack_value = prob.constraints[constr].slack
            print(f"Slack for {constr}: {slack_value}")

perform_sensitivity_analysis("BestCase")
perform_sensitivity_analysis("Expected")
perform_sensitivity_analysis("WorstCase")
