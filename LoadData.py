# Brandon Smith
# TV Show App
# AppData Preparation - Data Loading, Cleaning, and Merging

import pandas as pd
import numpy as np
import re

# function to import, clean, and prep data for TV Show App.
# made into function so it can be imported to UI
def load_data():
    # ---------------------------------
    # Process first dataset - TMDB
    # ---------------------------------
    
    filepath = 'TMDB.csv'

    # initialize dataframe and read CSV into dataframe. Exit and display message to user if no file found.
    try:
        tmdb_df = pd.read_csv(filepath)
    except FileNotFoundError:
        print('Error: TV data not found. Please contact support at smithb35@oregonstate.edu.')
        exit()

    # drop columns that do not serve purpose of the app
    # keeping: name, vote_average, vote_count, poster_path, tagline
    drop_cols = ['id', 'overview', 'adult', 'backdrop_path', 'homepage', 'in_production', 'original_name', 'popularity',
                 'status', 'created_by', 'production_companies', 'production_countries', 'languages', 'spoken_languages']

    # drop unnecessary attributes
    tmdb_df.drop(columns=drop_cols, inplace=True)

    # remove rows containing any NaN values
    tmdb_df.dropna(inplace=True)


    # remove entries with vote_average below 3.0
    tmdb_df = tmdb_df[tmdb_df['vote_average'] > 3.0]

    # convert datatypes of dataframe to correct types
    tmdb_df['first_air_date'] = pd.to_datetime(tmdb_df['first_air_date'], errors='coerce')
    tmdb_df['last_air_date'] = pd.to_datetime(tmdb_df['last_air_date'], errors='coerce')

    # convert to categorical
    tmdb_df['original_language'] = tmdb_df['original_language'].astype('category')
    tmdb_df['type'] = tmdb_df['type'].astype('category')
    tmdb_df['origin_country'] = tmdb_df['origin_country'].astype('category')


    # ---------------------------------
    # Process second dataset - Primary
    # ---------------------------------

    filepath = 'Primary.csv'

    # initialize dataframe and read CSV into dataframe, save to local repo
    try:
        Primary_df = pd.read_csv(filepath)
    except FileNotFoundError:
        print('Error: TV data not found. Please contact support at smithb35@oregonstate.edu.')
        exit()

    # drop columns that do not serve purpose of the app
    # keeping: Name, Rating, Genres, Network, Language, Type, Premiere Date, End Date, Total Seasons, Total Episodes, Average Runtime
    drop_cols = ['Summary', 'Schedule (days)', 'Schedule (time)', 'Character Names', 'Person Names', 'Official Site']
    Primary_df.drop(columns=drop_cols, inplace=True)

    # remove rows containing any NaN values
    Primary_df.dropna(inplace=True)

    # remove rows with critic rating of 3.0 or below
    Primary_df = Primary_df[Primary_df['Rating'] > 3.0]

    # rename Rating column to Critic_Rating for clarity
    Primary_df.rename(columns={'Rating': 'Critic_Rating'}, inplace=True)

    # convert data types
    Primary_df['End Date'] = pd.to_datetime(Primary_df['End Date'], errors='coerce')
    Primary_df['Premier Date'] = pd.to_datetime(Primary_df['Premiere Date'], errors='coerce')
    Primary_df['Type'] = Primary_df['Type'].astype('category')

    # -----------------------------------------
    # Metacritic dataset processing/cleaning
    # ----------------------------------------

    filepath = 'Metacritic.csv'

    # initialize dataframe and read CSV into dataframe
    try:
        Metacritic = pd.read_csv(filepath)
    except FileNotFoundError:
        print('Error: TV data not found. Please contact support at smithb35@oregonstate.edu.')
        exit()

    # drop all columns except title and metascore - user_score not needed for AppData
    drop_cols = ['id', 'release_date', 'sort_no', 'summary', 'user_score']
    Metacritic.drop(columns=drop_cols, inplace=True)

    # extract show name from title by stripping season/series suffixes
    def extract_show_name(title):
        show_name = re.split(r':\s*Season\s*\d+|:\s*Series\s*\d+|-\s*Season\s*\d+|-\s*Series\s*\d+', str(title), flags=re.IGNORECASE)[0]
        return show_name.strip()

    # apply the extraction to create show_name column
    Metacritic['show_name'] = Metacritic['title'].apply(extract_show_name)

    # calculate average metascore across all seasons of a show
    show_averages = Metacritic.groupby('show_name').agg({
        'metascore': 'mean'
    }).reset_index()

    # rename columns
    show_averages.columns = ['show_name', 'avg_metascore']

    # round the averages
    show_averages['avg_metascore'] = show_averages['avg_metascore'].round(2)

    # -------------------------
    # Merge datasets into AppData
    # -------------------------

    # rename "name" column to "Name" to match Primary_df
    tmdb_df.rename(columns={'name': 'Name'}, inplace=True)

    # merge the TMDB vote_average, vote_count, poster_path, and tagline into Primary_df
    Primary_df = Primary_df.merge(
        tmdb_df[['Name', 'vote_average', 'vote_count', 'poster_path', 'tagline']],
        on='Name',
        how='left'
    )

    # rename vote_average to User_Rating for clarity
    Primary_df.rename(columns={'vote_average': 'User_Rating'}, inplace=True)

    # merge Metacritic avg_metascore into Primary_df by matching show names
    Primary_df = Primary_df.merge(
        show_averages[['show_name', 'avg_metascore']],
        left_on='Name',
        right_on='show_name',
        how='left'
    )

    # drop the redundant show_name column that came from the Metacritic merge
    Primary_df.drop(columns=['show_name'], inplace=True)

    # rename avg_metascore to Metacritic_Rating for clarity
    Primary_df.rename(columns={'avg_metascore': 'Metacritic_Rating'}, inplace=True)

    # drop rows where no User_Rating or vote_count (no TMDB match)
    Primary_df.dropna(subset=['User_Rating', 'vote_count'], inplace=True)
    Primary_df['Metacritic_Rating'] = Primary_df['Metacritic_Rating'].fillna('N/A')

    # final AppData dataframe
    AppData = Primary_df.copy()

    # save AppData to CSV
    AppData.to_csv('AppData.csv', index=False)

    return AppData

# Load data function used for debugging. Print statements to eval data cleaning/prep/formatting.
def load_data_debug():
    # ---------------------------------
    # Process first dataset - TMDB
    # ---------------------------------
    # variable to hold absolute file path for TMDB dataset
    filepath = '/Users/bsmith/Desktop/CS361/Main_Project/TMDB.csv'

    # initialize dataframe and read CSV into dataframe. Exit and display message to user if no file found.
    try:
        tmdb_df = pd.read_csv(filepath)
    except FileNotFoundError:
        print('Error: TV data not found. Please contact support at smithb35@oregonstate.edu.')
        exit()

    # set console display options for dataframe
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 400)
    pd.set_option('display.max_columns', 12)
    pd.set_option('display.max_rows', 12)

    # print number of rows and columns for each dataframe
    print(tmdb_df.shape)
    print('Data types in uncleaned TMDB dataset\n', tmdb_df.dtypes, '\n')

    # drop columns that do not serve purpose of the app
    # keeping: name, vote_average, vote_count, poster_path, tagline
    drop_cols = ['id', 'overview', 'adult', 'backdrop_path', 'homepage', 'in_production', 'original_name', 'popularity',
                 'status', 'created_by', 'production_companies', 'production_countries', 'languages',
                 'spoken_languages']

    tmdb_df.drop(columns=drop_cols, inplace=True)

    print('TMDB Dataset with dropped columns. \n', tmdb_df)
    print(tmdb_df.shape)
    print('Data types of remaining columns for TMDB Dataset. \n', tmdb_df.dtypes)

    # count NaN values for each column
    nan_counts = tmdb_df.isna().sum()
    print('\nNaN counts per column in TMDB Dataset:')
    print(nan_counts)

    # remove rows containing any NaN values
    tmdb_df.dropna(inplace=True)

    # verify no NaN values remain
    print('NaN counts after cleaning:')
    print(tmdb_df.isna().sum())

    # remove entries with vote_average below 3.0
    tmdb_df = tmdb_df[tmdb_df['vote_average'] > 3.0]
    print()
    print('Filtered TMDB Dataset:\n', tmdb_df)

    print('Data types of remaining columns for TMDB Dataset. \n', tmdb_df.dtypes)

    # convert datatypes of dataframe to correct types
    tmdb_df['first_air_date'] = pd.to_datetime(tmdb_df['first_air_date'], errors='coerce')
    tmdb_df['last_air_date'] = pd.to_datetime(tmdb_df['last_air_date'], errors='coerce')

    # convert to categorical
    tmdb_df['original_language'] = tmdb_df['original_language'].astype('category')
    tmdb_df['type'] = tmdb_df['type'].astype('category')
    tmdb_df['origin_country'] = tmdb_df['origin_country'].astype('category')

    # verify the datatype conversions
    print('Data types after conversion:')
    print(tmdb_df.dtypes)
    print()

    print(tmdb_df.shape)
    print('Cleaned TMDB Dataset \n', tmdb_df)
    print()

    # ---------------------------------
    # Process second dataset - Primary
    # ---------------------------------

    # variable to hold absolute file path for Primary dataset
    filepath = '/Users/bsmith/Desktop/CS361/Main_Project/Primary.csv'

    # initialize dataframe and read CSV into dataframe, save to local repo
    try:
        Primary_df = pd.read_csv(filepath)
    except FileNotFoundError:
        print('Error: TV data not found. Please contact support at smithb35@oregonstate.edu.')
        exit()

    # print number of rows and columns for each dataframe
    print(Primary_df.shape)
    print()
    print('Data types in uncleaned Primary dataset\n', Primary_df.dtypes, '\n')

    # drop columns that do not serve purpose of the app
    # keeping: Name, Rating, Genres, Network, Language, Type, Premiere Date, End Date, Total Seasons, Total Episodes, Average Runtime
    drop_cols = ['Summary', 'Schedule (days)', 'Schedule (time)', 'Character Names', 'Person Names', 'Official Site']

    Primary_df.drop(columns=drop_cols, inplace=True)

    print('Primary Dataset with dropped columns. \n', Primary_df)
    print(Primary_df.shape)
    print('Data types of remaining columns for Primary Dataset. \n', Primary_df.dtypes)

    # count NaN values
    nan_counts = Primary_df.isna().sum()
    print('\nNaN counts per column in Primary Dataset:')
    print(nan_counts)

    # remove rows containing any NaN values
    Primary_df.dropna(inplace=True)

    # verify no NaN values remain
    print('NaN counts after cleaning:')
    print(Primary_df.isna().sum())

    # remove rows with critic rating of 3.0 or below
    Primary_df = Primary_df[Primary_df['Rating'] > 3.0]
    print('Filtered Primary Dataset:\n', Primary_df)

    # confirm the minimum critic rating is now above 3.0
    print(f'\nMinimum critic rating after filtering: {Primary_df["Rating"].min()}')
    print(f'Maximum critic rating after filtering: {Primary_df["Rating"].max()}')

    # rename Rating column to Critic_Rating for clarity
    Primary_df.rename(columns={'Rating': 'Critic_Rating'}, inplace=True)

    # show data types and convert if necessary
    print('Data types in cleaned Primary dataset\n', Primary_df.dtypes, '\n')

    # convert data types
    Primary_df['End Date'] = pd.to_datetime(Primary_df['End Date'], errors='coerce')
    Primary_df['Premier Date'] = pd.to_datetime(Primary_df['Premiere Date'], errors='coerce')
    Primary_df['Type'] = Primary_df['Type'].astype('category')

    # display converted data types
    print()
    print('Data types converted in cleaned Primary dataset\n', Primary_df.dtypes, '\n')

    print('Cleaned Primary Dataset \n', Primary_df)
    print(Primary_df.shape)

    # -----------------------------------------
    # Metacritic dataset processing/cleaning
    # ----------------------------------------

    # variable to hold absolute file path for Metacritic dataset
    filepath = '/Users/bsmith/Desktop/CS361/Main_Project/Metacritic.csv'

    # initialize dataframe and read CSV into dataframe
    try:
        Metacritic = pd.read_csv(filepath)
    except FileNotFoundError:
        print('Error: TV data not found. Please contact support at smithb35@oregonstate.edu.')
        exit()

    # print number of rows and columns for each dataframe
    print(Metacritic.shape)
    print('Uncleaned Metacritic dataset \n', Metacritic)
    print()
    print('Metacritic dataset datatypes', Metacritic.dtypes)

    # drop all columns except title and metascore - user_score not needed for AppData
    drop_cols = ['id', 'release_date', 'sort_no', 'summary', 'user_score']
    Metacritic.drop(columns=drop_cols, inplace=True)
    print('Data types of remaining columns for Metacritic dataset. \n', Metacritic.dtypes)
    print()

    # show NaN counts
    nan_counts = Metacritic.isna().sum()
    print('\nNaN counts per column in Metacritic dataset:')
    print(nan_counts)

    # extract show name from title by stripping season/series suffixes
    def extract_show_name(title):
        show_name = re.split(r':\s*Season\s*\d+|:\s*Series\s*\d+|-\s*Season\s*\d+|-\s*Series\s*\d+', str(title),
                             flags=re.IGNORECASE)[0]
        return show_name.strip()

    # apply the extraction to create show_name column
    Metacritic['show_name'] = Metacritic['title'].apply(extract_show_name)

    # calculate average metascore across all seasons of a show
    show_averages = Metacritic.groupby('show_name').agg({
        'metascore': 'mean'
    }).reset_index()

    # rename columns
    show_averages.columns = ['show_name', 'avg_metascore']

    # round the averages
    show_averages['avg_metascore'] = show_averages['avg_metascore'].round(2)

    print('Metacritic show averages:')
    print(show_averages)
    print()

    # -------------------------
    # Merge datasets into AppData
    # -------------------------

    # rename "name" column to "Name" to match Primary_df
    tmdb_df.rename(columns={'name': 'Name'}, inplace=True)

    # merge the TMDB vote_average, vote_count, poster_path, and tagline into Primary_df
    Primary_df = Primary_df.merge(
        tmdb_df[['Name', 'vote_average', 'vote_count', 'poster_path', 'tagline']],
        on='Name',
        how='left'
    )

    print('Primary Dataset merged with TMDB (vote_average, vote_count, poster_path, tagline): \n', Primary_df)
    print()

    # rename vote_average to User_Rating for clarity
    Primary_df.rename(columns={'vote_average': 'User_Rating'}, inplace=True)

    # merge Metacritic avg_metascore into Primary_df by matching show names
    Primary_df = Primary_df.merge(
        show_averages[['show_name', 'avg_metascore']],
        left_on='Name',
        right_on='show_name',
        how='left'
    )

    # drop the redundant show_name column that came from the Metacritic merge
    Primary_df.drop(columns=['show_name'], inplace=True)

    # rename avg_metascore to Metacritic_Rating for clarity
    Primary_df.rename(columns={'avg_metascore': 'Metacritic_Rating'}, inplace=True)

    print('AppData after merging Metacritic ratings: \n', Primary_df)
    print()

    # drop rows where no User_Rating or vote_count (no TMDB match)
    print(f'Shape before dropping rows with no TMDB match: {Primary_df.shape}')
    Primary_df.dropna(subset=['User_Rating', 'vote_count'], inplace=True)
    Primary_df['Metacritic_Rating'] = Primary_df['Metacritic_Rating'].fillna('N/A')

    # Metacritic_Rating NaN converted to N/A for display to user. Not used as filter.
    print('NaN counts in AppData after cleaning:')

    # show all columns and rows
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    print(Primary_df.isna().sum())
    print()

    # final AppData dataframe
    AppData = Primary_df.copy()

    # show all columns and rows
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    print('Final AppData: \n', AppData)
    print()
    print('AppData column data types: \n', AppData.dtypes)
    print()

    # save AppData to CSV
    AppData.to_csv('AppData.csv', index=False)
    print('AppData saved to AppData.csv.')

    return AppData

# for use in debugging and viewing TV show data as needed.
if __name__ == '__main__':
    AppData = load_data_debug()

    print(AppData.head(20))