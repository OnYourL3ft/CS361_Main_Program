# Brandon Smith
# CS 361
# Spring 2026
# Main Project: TV Show Finder - UI

import sys
import time
import subprocess
from LoadData import load_data
from filters import critic_rating_filter, user_rating_filter
from app_results import results_screen
from MLRanking import fit_model, rank_shows
import zmq
import json
import pandas as pd
from io import StringIO


# load data at startup, exit if data cannot be loaded
print('\nLoading TV show data, please wait...')
app_data = load_data()

if app_data is None or app_data.empty:
    print('Error: Could not load TV show data. Please contact support at smithb35@oregonstate.edu.')
    sys.exit(1)
else:
    print('TV Show data loaded successfully\n')

# create and fit model on all data using KMeans
fit_model(app_data)

# start microservices in their own processes
sort_process = subprocess.Popen(['python', 'sort_microservice.py'])
limit_process = subprocess.Popen(['python', 'results_limit_microservice.py'])
time.sleep(2)
# create the environment and connection with the server
context = zmq.Context()

# create socket for sort microservice
sort_socket = context.socket(zmq.REQ)
sort_socket.connect("tcp://localhost:5556")

# create socket for result limit microservice
limit_socket = context.socket(zmq.REQ)
limit_socket.connect("tcp://localhost:5560")

# placeholder to create socket for microservice 3

# placeholder to create socket for microservice 4


# -----------------------------------------------------------
# Function: informs user of their choices and displays wait screen while results are being retrieved
# Receives: critic value and user value floats representing user entered ratings
# Returns: None
# -----------------------------------------------------------
def wait_screen(critic_rating_value, user_rating_value):
    print()
    print('-' * 60)
    print('  Please wait while results are being retrieved.')
    print('  This may take up to 30 seconds.')
    print('-' * 60)
    print()
    print('  Your selected criteria are:')

    if critic_rating_value is None and user_rating_value is None:
        print('    No filters applied (Showing limit of 10 shows)')
    if critic_rating_value is not None:
        print(f'    Minimum Critic Rating of {critic_rating_value}')
    if user_rating_value is not None:
        print(f'    Minimum User Rating of {user_rating_value}')
    print()
    print('  Results will display soon.')
    print()

    # animated dots to show the app is working
    for i in range(1, 6):
        print('  ' + '* ' * i)
        time.sleep(0.4)

    print()

# -----------------------------------------------------------
# Function: closes program down gracefully, terminating subprocesses
# Receives: None
# Returns: None
# -----------------------------------------------------------
def exit_app():
    sort_process.terminate()
    limit_process.terminate()
    print()
    print('-' * 60)
    print('  Goodbye!')
    print('  Thank you for using the TV Show Recommendation app!')
    print('-' * 60)
    print()
    sys.exit(0)

# -----------------------------------------------------------
# Function: prints sort menu intro
# Receives: None
# Returns: None
# -----------------------------------------------------------
def sort_menu_intro():
    print('    You may choose to sort by the TV show characteristics listed below.')
    print('     The next screen allows you to specify sort order')
    print('     Enter the number associated with your chosen filter and then press Enter.')
    print('     Press Enter without any entry or Enter 1 to default to sorting by TV Show Title.')
    print('     You may return to the previous screen by using the Back option')
    print()

# -----------------------------------------------------------
# Function: prints sort options for TV show results
# Receives: None
# Returns: None
# -----------------------------------------------------------
def sort_menu_attr():
    print('    0 to Exit Program')
    print('    1 to Proceed')
    print('    2 to go Back')
    print('    3 to sort by Critic Rating')
    print('    4 to sort by User Rating')
    print('    5 to sort by Metacritic Score')
    print('    6 to sort by average episode runtime')


# ---------------------------------------------------------------------------
# Welcome Screen
# ---------------------------------------------------------------------------

# track whether to show the welcome screen again (search again loop)
running = True

while running:

    # print welcome screen
    print()
    print('-' * 60)
    print('  Welcome to the TV Show Finder')
    print('-' * 60)
    print()
    print('  This application uses Machine Learning to recommend TV shows that fit your specific criteria.')
    print("   Use it to find new shows you'll love based on your interests, quality standards, and time constraints!")
    print()
    print('  The application will guide you through each filter. You can skip a filter by pressing Enter on the filter screen.')
    print()
    print('  Depending on your selected filters, it is possible no matches will be found.')
    print('  Each search may take up to 30 seconds')
    print()
    print('  Each result displays:')
    print('    Title | Genre | Network | Language | Seasons | Episodes | Runtime | Critic Rating | User Rating | Metacritic Score')
    print()
    print('-' * 60)
    print('  Enter a command and press Enter:')
    print('    [1] Proceed')
    print('    [0] Exit Program')
    print('-' * 60)

    # get user input and validate - loop until valid command entered
    welcome_valid = False
    while not welcome_valid:
        welcome_input = input('  > ').strip()

        if welcome_input == '1':
            welcome_valid = True

        elif welcome_input == '0':
            # user chose to exit
            exit_app()

        else:
            # invalid command entered
            print()
            print('  You entered an invalid command. Please enter a valid command and press Enter.')
            print('    1 to Proceed')
            print('    0 to Exit Program')
            print()


    # ---------------------------------------------------------------------------
    # Filters Screens
    # Iterate over different TV show filters and gather user input
    # Currently critic ratings and user ratings implemented
    # ---------------------------------------------------------------------------

    # list of filters
    filters = [critic_rating_filter, user_rating_filter]
    filter_values = [None] * len(filters)
    i = 0

    # iterate over list of filter functions, calling at same time
    while i < len(filters):
        result = filters[i]()
        if result == 'back':
            i -= 1
            if i < 0:
                break
        else:
            filter_values[i] = result
            i += 1

    # if user backed all the way out, restart welcome screen
    if i < 0:
        continue

    # store filter values in specific variable
    critic_rating_value = filter_values[0]
    user_rating_value = filter_values[1]

    # call wait screen with filter values
    wait_screen(critic_rating_value, user_rating_value)

    # apply filters
    results = app_data.copy()
    if critic_rating_value is not None:
        results = results[results['Critic_Rating'] >= critic_rating_value]
    if user_rating_value is not None:
        results = results[results['User_Rating'] >= user_rating_value]

    # apply model
    results = rank_shows(results)

    # limit to 10 if no filters applied otherwise 15
    if critic_rating_value is None and user_rating_value is None:
        results = results.head(10)
    else:
        results = results.head(15)
    # ---------------------------------------------------------------------------
    # Results Screen
    # ---------------------------------------------------------------------------

    print("Here are your selected filters and the TV Show results:\n")
    # reiterate selections to user at results screen
    if critic_rating_value is None and user_rating_value is None:
        print('    No filters applied (showing maximum of 10 shows)')
    if critic_rating_value is not None:
        print(f'    Minimum Critic Rating of {critic_rating_value}')
    if user_rating_value is not None:
        print(f'    Minimum User Rating of {user_rating_value}')

    # display results and give user option to loop back or exit
    running = results_screen(results)

    # save results for use until user searches again or exits
    original_results = results.copy()

    # ------------------------------------------------------------------------
    # Sort Screen
    # ------------------------------------------------------------------------
    while running == '12':

        # display sort information and options to user
        sort_menu_intro()
        sort_menu_attr()


        sort_attr = [None, None, None]
        sort_valid = False
        while not sort_valid:
            # get user input
            sort_input = input('  > ').strip()
            if sort_input == '1' or sort_input == '':
                sort_attr[0] = results.to_json()
                sort_attr[1] = 'Name'
            elif sort_input == '0':
                # user chose to exit
                time.sleep(1)
                exit_app()
                # return to results screen
            elif sort_input == '2':
                running = results_screen(results)
                break
            elif sort_input == ('3'):
                sort_attr[0] = results.to_json()
                sort_attr[1] = 'Critic_Rating'
            elif sort_input == ('4'):
                sort_attr[0] = results.to_json()
                sort_attr[1] = 'User_Rating'
            elif sort_input == ('5'):
                # metacritic scores have mixed data types, so convert to Nan and back after sort.
                results['Metacritic_Rating'] = pd.to_numeric(results['Metacritic_Rating'], errors='coerce')
                sort_attr[0] = results.to_json()
                sort_attr[1] = 'Metacritic_Rating'
            elif sort_input == ('6'):
                sort_attr[0] = results.to_json()
                sort_attr[1] = 'Average Runtime'
            else:
                # invalid command entered
                print()
                print('  You entered an invalid command. Please enter a valid command and press Enter.')
                sort_menu_attr()
                print()


            # Enter sort direction screen if valid response
            if sort_attr[1] is not None:
                while not sort_valid:
                    print('    You may choose to sort the TV shows in ascending or descending order by your chosen criteria.')
                    print('     Enter 3 to choose ascending sort.')
                    print('     Enter 4 to choose descending sort.')
                    print('     Pressing Enter without any entry or 1 to proceed will default to ascending sort.')
                    print('     You may return to the previous screen by using the Back option')
                    print()
                    print('    0 to Exit Program')
                    print('    1 to Proceed')
                    print('    2 to go Back')
                    print(f'   3 to sort {sort_attr[1]} in ascending order.')
                    print(f'   4 to sort {sort_attr[1]} in descending order.')

                    sort_input = input('  > ').strip()
                    if sort_input == '1' or sort_input == '':
                        sort_attr[2] = 3
                        sort_valid = True
                    elif sort_input == '0':
                        # user chose to exit
                        sort_socket.send_string('Q')
                        time.sleep(1)
                        exit_app()
                        # return to attribute selection screen
                    elif sort_input == '2':
                        sort_menu_intro()
                        sort_menu_attr()
                        sort_attr[1] = None
                        break
                    elif sort_input == ('3'):
                        sort_attr[2] = 3
                        sort_valid = True
                    elif sort_input == ('4'):
                        sort_attr[2] = 4
                        sort_valid = True
                    else:
                        # invalid command entered
                        print()
                        print('  You entered an invalid command. Please enter a valid command and press Enter.')
                        print('    0 to Exit Program')
                        print('    1 to Proceed')
                        print('    2 to go Back')
        if sort_valid == True:
            # send request
            request = json.dumps(sort_attr)
            sort_socket.send_string(request)
            # receive request and display results
            sorted_data = sort_socket.recv_string()

            # check for invalid response
            if sorted_data:
                results = pd.read_json(StringIO(sorted_data))
                # convert Metacritic NaN back to N/A
                if sort_attr[1] == 'Metacritic_Rating':
                    results = results.fillna('N/A')

                # update original dataframe to sorted
                original_results = results.copy()
                print()
                print()
                print('-' * 60)
                print('-' * 60)
                if sort_attr[2] == 3 or sort_attr[2] is None:
                    print(f' Your results sorted by {sort_attr[1]} in ascending order. ')
                else:
                    print(f' Your results sorted by {sort_attr[1]} in descending order. ')
                running = results_screen(results)

            else:
                print('-' * 60)
                print(" Error: Sort request could not be completed. Please try again. ")
                print('-' * 60)
                running = results_screen(results)
    # ------------------------------------------------------------------------
    # Result Limit Screen
    # ------------------------------------------------------------------------
    while running == '13':
        print()
        print('-' * 60)
        print('  Enter the number of results to display.')
        print('  Press Enter without any entry to keep current results.')
        print('  Enter 0 to Exit Program.')
        print('-' * 60)

        limit_input = input('  > ').strip()

        # user chooses exit
        if limit_input == '0':
            time.sleep(1)
            exit_app()

        elif limit_input == '':
            # keep current results, return to results screen
            running = results_screen(results)

        else:
            # validate input is a positive integer
            try:
                result_limit = int(limit_input)
                if result_limit <= 0:
                    raise ValueError
            except ValueError:
                print()
                print('  You entered an invalid number. Please enter a positive integer.')
                print()
                continue

            # send request to results limit microservice, track original count
            original_count = len(original_results)
            request = json.dumps([original_results.to_json(), result_limit])
            limit_socket.send_string(request)
            limited_data = limit_socket.recv_string()

            if limited_data:
                results = pd.read_json(StringIO(limited_data))
                if result_limit >= original_count:
                    print()
                    print('  All search results displayed.')
                running = results_screen(results)
            else:
                print('-' * 60)
                print('  Error: Result limit request could not be completed. Please try again.')
                print('-' * 60)
                running = results_screen(results)
                    



# ---------------------------------------------------------------------------
# Exit Screen
# ---------------------------------------------------------------------------

exit_app()
