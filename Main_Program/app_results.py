# Brandon Smith
# CS361
# Spring 2026
# Main Project - TV Show App Results

import pandas as pd
import os

# -------------------------------------------------------------------
# Function: clears screen before each results displays
# Receives: None
# Returns: None
# -------------------------------------------------------------------
def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

# -------------------------------------------------------------------
# Function: prints the TV show attributes for each search result
# Receives: TV show vector
# Returns: None
# -------------------------------------------------------------------

# print TV show attributes of machine learning results
def print_results(results_df, format_socket):
    num_rows = len(results_df)
    width = os.get_terminal_size().columns

    # display only TV show attributes pertinent
    display_cols = ['Name', 'Genres', 'Network', 'Language', 'Total Seasons',
                    'Total Episodes', 'Average Runtime', 'Critic_Rating',
                    'User_Rating', 'Metacritic_Rating']
    display_df = results_df[display_cols].astype(str)


    # send request with data and display parameters
    format_socket.send_json({
    "width": width,
    "limit": num_rows,
    "data": display_df.to_dict(orient='records'),
    "format_headers": True
})

    response = format_socket.recv_json()
    print(response["data"])


# -----------------------------------------------------------------
# Function: displays results screen text with option to search again or exit, calls print results
# Receives: results as dataframe
# Returns: None
# -----------------------------------------------------------------
def results_screen(results, format_socket):

    clear_screen()
    print()
    print('-' * 60)
    print('-' * 60)
    print('  Results:')
    print()

    # no results case
    if results.empty:
        print("  We're sorry. There are no TV shows that match your")
        print('  selected criteria. You can adjust your filters and try again.')
        print()
        # user option to search again, exit, or sort
        print('-' * 60)
        print('  Enter a command:')
        print('    [1] Search Again')
        print('    [0] Exit')
        print('-' * 60)
    # display results
    else:
        print_results(results, format_socket)
        # user option to search again, exit, or sort
        print('-' * 60)
        print('  Enter a command:')
        print('    [1] Search Again')
        print('    [0] Exit')
        print('    [12] Sort Results by critic rating, user score, metacritic rating, or runtime')
        print('    [13] Change number of displayed results')
        print('    [14] Search result TV Show Titles by keyword')
        print('-' * 60)

    # get user input and validate and loop until valid command entered
    results_valid = False
    while not results_valid:
        results_input = input('  > ').strip()

        if results_input == '1':
            # search again, loop back to welcome screen
            return True

        elif results_input == '0':
            # user chose to exit, close program
            return False
        elif results_input =='12' and not results.empty:
            # display sort screen to user with sort options
            return '12'
        elif results_input == '13' and not results.empty:
            # show user result limit selection
            return '13'
        elif results_input == '14' and not results.empty:
            # allow user to search titles by keyword
            return '14'
        elif results.empty:
            # invalid command entered
            print()
            print('  You entered an invalid command. Please enter a valid command and press Enter.')
            print('    1 to Search Again')
            print('    0 to Exit')
            print()
        else:
            print('  You entered an invalid command. Please enter a valid command and press Enter.')
            print('    1 to Search Again')
            print('    0 to Exit')
            print('    12 to sort results by critic rating, user score, metacritic rating, or runtime')
            print('    13 to change number of displayed results')
            print('    [14] Search results by TV Show Title')