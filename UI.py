# Brandon Smith
# CS 361
# Main Project: TV Show Finder - UI

import sys
import time
from LoadData import load_data
from filters import critic_rating_filter, user_rating_filter


# load data at startup, exit if data cannot be loaded
print('\nLoading TV show data, please wait...')
app_data = load_data()

if app_data is None or app_data.empty:
    print('Error: Could not load TV show data. Please contact support at smithb35@oregonstate.edu.')
    #sys.exit(1)
else:
    print('TV Show data loaded successfully\n')

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
        print('    No filters applied (showing all shows)')
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

# app exit
def exit_app():
    print()
    print('-' * 60)
    print('  Goodbye!')
    print('  Thank you for using the TV Show Recommendation app!')
    print('-' * 60)
    print()
    sys.exit(0)

# print TV show attributes of machine learning results
def print_results(row):
    name          = row.get('Name', 'N/A')
    genres        = row.get('Genres', 'N/A')
    network       = row.get('Network', 'N/A')
    language      = row.get('Language', 'N/A')
    seasons       = row.get('Total Seasons', 'N/A')
    episodes      = row.get('Total Episodes', 'N/A')
    runtime       = row.get('Average Runtime', 'N/A')
    critic_rating = row.get('Critic_Rating', 'N/A')
    user_rating   = row.get('User_Rating', 'N/A')
    metacritic    = row.get('Metacritic_Rating', 'N/A')

    print(f'  - {name} | {genres} | Language: {language} | Network: {network} | '
          f'{seasons} Seasons | {episodes} Episodes | Runtime: {runtime} min | '
          f'Critic: {critic_rating} | User: {user_rating} | Metacritic: {metacritic}')


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
    print('    [0] Exit')
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
            print('    0 to Exit')
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

    # limit to 10 if no filters applied
    if critic_rating_value is None and user_rating_value is None:
        results = results.head(10)

    # no filters implemented yet. limit output to 10. Will carry to all results displayed.
    results = app_data.copy()
    results = results.head(10)

    # ---------------------------------------------------------------------------
    # Results Screen
    # ---------------------------------------------------------------------------

    # results functionality to be added. For now, skips results display and prints user entered filters. Give
    # user option to loop back through or exit.

    # reiterate selections to user at results screen
    if critic_rating_value is None and user_rating_value is None:
        print('    No filters applied (showing all shows)')
    if critic_rating_value is not None:
        print(f'    Minimum Critic Rating of {critic_rating_value}')
    if user_rating_value is not None:
        print(f'    Minimum User Rating of {user_rating_value}')

    # user option to search again
    print('-' * 60)
    print('  Enter a command:')
    print('    [1] Search Again')
    print('    [0] Exit')
    print('-' * 60)

    # get user input and validate and loop until valid command entered
    results_valid = False
    while not results_valid:
        results_input = input('  > ').strip()

        if results_input == '1':
            # search again, loop back to welcome screen
            results_valid = True

        elif results_input == '0':
            # user chose to exit, close program
            results_valid = True
            running = False

        else:
            # invalid command entered
            print()
            print('  You entered an invalid command. Please enter a valid command and press Enter.')
            print('    1 to Search Again')
            print('    0 to Exit')
            print()


# ---------------------------------------------------------------------------
# Exit Screen
# ---------------------------------------------------------------------------

exit_app()
