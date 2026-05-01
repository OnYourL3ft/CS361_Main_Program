# Brandon Smith
# CS361
# Main Project - TV Show App Results

# -------------------------------------------------------------------
# Function: prints the TV show attributes for each search result
# Receives: TV show vector
# Returns: None
# -------------------------------------------------------------------

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


# -----------------------------------------------------------------
# Function: displays results screen text with option to search again or exit, calls print results
# Receives: results as dataframe
# Returns: None
# -----------------------------------------------------------------
def results_screen(results):

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
    # display results
    else:
        for index, row in results.iterrows():
            print_results(row)
        print()

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
            return True

        elif results_input == '0':
            # user chose to exit, close program
            return False

        else:
            # invalid command entered
            print()
            print('  You entered an invalid command. Please enter a valid command and press Enter.')
            print('    1 to Search Again')
            print('    0 to Exit')
            print()