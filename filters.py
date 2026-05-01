# Brandon Smith
# CS361
# Main Project - filters for TV Show data

# -----------------------------------------------------------------------
# Function: critic ratings filter gives user UI, option to select values for filters, and
# validates user input
#  input: none
#  returns:
#   a float value if the user entered a rating
#   None if the user skipped the filter
#   'back' if the user wants to go back to the previous screen
# ------------------------------------------------------------------------

# critic rating filter screen
def critic_rating_filter():
    print()
    print('-' * 60)
    print(' Filter: Minimum Critic Rating')
    print('-' * 60)
    print()
    print(' This is the minimum rating a critic has given a TV show.')
    print()
    print(' Enter a rating from 3.0 to 10.0 (e.g. 5, 7.5, 9.0) and press Enter.')
    print(' If no rating is entered, this filter will not be applied.')
    print()
    print(' Optional commands:')
    print('   [1] Continue  (proceed to next filter)')
    print('   [0] Skip      (do not apply this filter)')
    print('   [2] Back      (return to previous screen)')
    print('-' * 60)

    while True:
        user_input = input('  > ').strip()

        # skip filter
        if user_input == '0' or user_input == '':
            return None

        # back to welcome screen
        if user_input == '2':
            return 'back'

        # continue with no rating entered
        if user_input == '1':
            return None

        # attempt to parse as a number
        try:
            value = float(user_input)
        except ValueError:
            print()
            print(
                f'You entered an invalid rating of "{user_input}". Please enter a valid rating or optional command followed by Enter.')
            print()
            continue

        # validate range
        if value < 3.0 or value > 10.0:
            print()
            print(f'You entered an invalid rating of "{user_input}". Please enter a value between 3.0 and 10.0.')
            print()
            continue

        # valid rating entered
        return value

# -----------------------------------------------------------------------
# Function: user ratings filter gives user UI, option to select values for filters, and
# validates user input
#  input: none
#  returns:
#   a float value if the user entered a rating
#   None if the user skipped the filter
#   'back' if the user wants to go back to the previous screen
# ------------------------------------------------------------------------

# user rating filter screen
def user_rating_filter():
    print()
    print('-' * 60)
    print(' Filter: Minimum User Rating')
    print('-' * 60)
    print()
    print(' This is the minimum average rating users have given a TV show.')
    print(' Ratings are aggregated from IMDB, Rotten Tomatoes, and TMDB.')
    print()
    print(' Enter a rating from 3.0 to 10.0 (e.g. 5, 7.5, 9.0) and press Enter.')
    print(' If no rating is entered, this filter will not be applied.')
    print()
    print(' Optional commands:')
    print('   [1] Continue  (proceed to next filter)')
    print('   [0] Skip      (do not apply this filter)')
    print('   [2] Back      (return to previous screen)')
    print('-' * 60)

    while True:
        user_input = input('  > ').strip()

        # skip filter
        if user_input == '0' or user_input == '':
            return None

        # back to previous filter
        if user_input == '2':
            return 'back'

        # continue with no rating entered
        if user_input == '1':
            return None

        # attempt to parse as a number
        try:
            value = float(user_input)
        except ValueError:
            print()
            print(f' You entered an invalid rating of "{user_input}". Please enter a valid rating or optional command followed by Enter.')
            print()
            continue

        # validate range
        if value < 3.0 or value > 10.0:
            print()
            print(f' You entered an invalid rating of "{user_input}". Please enter a value between 3.0 and 10.0.')
            print()
            continue

        # valid rating entered
        return value