import pandas as pd
import numpy as np
import requests
import json
from getpass import getpass
from dotenv import load_dotenv
import os
import ast



load_dotenv()
token = os.getenv("token")


def mongo_filter (c):

    # This code searches for documents in a MongoDB collection ("companies") that satisfy two conditions:
        # 1.The total_money_raised field ends with the letter "M", meaning that the resulting startups have raised at least 1 Million dollars.
        # 2.The tag_list field contains the word "design", meaning that there must be some nearby companies that also do design.
    condition_1 = {"total_money_raised": {"$regex": "M$"}}
    condition_2 = {"tag_list": {"$regex": "design"}}
    query = {"$and": [condition_1, condition_2]}
    projection = {"name":1, "offices":1, "total_money_raised": 1, "_id":0}
    result = list(c.find(query, projection))

    # This code creates a pandas DataFrame from the collection "companies", then explodes the offices column so that each row in the DataFrame contains only one office. 
    # Resets the DataFrame's index so that it starts at 0 and increments by 1 for each row.
    df = pd.DataFrame(result)
    df = df.explode('offices')
    df = df.reset_index(drop=True)
    
    return df



def basic_cleaning_1 (df):
   
    # This code creates a new column with the value of the country_code key from the offices column of each row. 
    # Counts each unique value in the offices_country_code column and stores the result in a dictionary named value_counts_offices_country. 
    # Creates a list of tuples from the dictionary, and filters the DataFrame to include only rows that contains the most frequent country code. 
    # Resets the DataFrame's index so that it starts at 0 and increments by 1 for each row.
    df['offices_country_code'] = df['offices'].apply(lambda x: x['country_code'])
    value_counts_offices_country = df['offices_country_code'].value_counts().to_dict()
    value_counts_offices_country_tup = list(value_counts_offices_country.items())
    df = df[df['offices_country_code'].apply(lambda x: value_counts_offices_country_tup[0][0] in x)]
    df = df.reset_index(drop=True)

    return df



def basic_cleaning_2 (df):

    # This code creates a new column with the value of the state_code key from the offices column of each row. 
    # Counts each unique value in the offices_state_code column and stores the result in a Pandas Series named value_counts_offices_state_code. 
    # Creates a list of tuples from the series, and filters the DataFrame to include only rows that contains any of the top four most frequent state codes. 
    # Resets the DataFrame's index so that it starts at 0 and increments by 1 for each row.
    df['offices_state_code'] = df['offices'].apply(lambda x : x['state_code'])
    value_counts_offices_state_code = df['offices_state_code'].value_counts()
    value_counts_offices_state_code_tup = list(value_counts_offices_state_code.items())
    df = df[df['offices_state_code'].apply(lambda x: any(val in x for val in [value_counts_offices_state_code_tup[0][0],value_counts_offices_state_code_tup[1][0], value_counts_offices_state_code_tup[2][0], value_counts_offices_state_code_tup[3][0]]))]
    df = df.reset_index(drop=True)

    return df



def basic_cleaning_3 (df):

    # This code adds new columns to the DataFrame df containing the latitude, longitude, address line 1, address line 2, and zip code of the offices.
    df['offices_latitude'] = df['offices'].apply(lambda x : x['latitude'])
    df['offices_longitude'] = df['offices'].apply(lambda x : x['longitude'])
    df['offices_address_1'] = df['offices'].apply(lambda x : x['address1'])
    df['offices_address_2'] = df['offices'].apply(lambda x : x['address2'])
    df['offices_zip_code'] = df['offices'].apply(lambda x : x['zip_code'])

    # This code drops the 'offices' column
    # Replaces empty strings with NaN values
    # Drops rows that have NaN values in columns 'offices_latitude', 'offices_longitude', 'offices_address_1', and 'offices_address_2', 
    # Resets the index of the dataframe to be consecutive numbers, all in one line.
    df = df.drop('offices', axis=1)
    df = df.replace('', np.nan)
    df.dropna(subset=['offices_latitude', 'offices_longitude', 'offices_address_1', 'offices_address_2'], how='all', inplace=True)
    df = df.reset_index(drop=True)

    return df



def insert_coordinates (df):
   
    # This code code creates a subset of the dataframe where latitude and longitude values are missing. 
    # Creates a list with the missing coordinates, for latitude and longitude, respectively. Those values have been introduced manually. 
    # Creates a dictionary from the lists with the missing coordinates and turns it into a dataframe.
    # Resets the index of the dataframe to be consecutive numbers, all in one line.
    # Creates a joined dataframe, which is then joined to the original dataframe on the common column index to add the latitude and longitude columns to df.
    df_subset = df.loc[df['offices_latitude'].isnull(), ['name', 'offices_address_1', 'offices_address_2']]
    NaN_name_list = df.loc[df['offices_latitude'].isnull(), 'name'].tolist()
    NaN_lat_list = [40.7493756, 40.7208632, 40.720812, None, 40.7467544, 37.4499108, 37.4433618, 34.080633]
    NaN_lon_list = [-73.9964352, -74.0035362, -74.0037199, None, -73.9953227, -122.1211875, -122.1630406, -118.3885556]
    Nan_index_list = [2, 9, 14, 15, 16, 19, 20, 21]
    my_dict = {key: value for key, value in zip(['name', 'latitude', 'longitude', 'index'], [NaN_name_list, NaN_lat_list, NaN_lon_list, Nan_index_list])}
    dict_df = pd.DataFrame(my_dict)
    dict_df.set_index('index', inplace=True)
    joined_df = df_subset.join(dict_df[['latitude', 'longitude']], on=df_subset.index)
    df = df.join(joined_df[['latitude', 'longitude']], on=df.index)

    # This code replaces the missing coordinates with the values from of latitude and longitude.
    df.loc[df['offices_latitude'].isna(), 'offices_latitude'] = df.loc[df['offices_latitude'].isna(), 'latitude']
    df.loc[df['offices_longitude'].isna(), 'offices_longitude'] = df.loc[df['offices_longitude'].isna(), 'longitude']

    # This code drops the 'latitude' and 'longitude' columns from the dataframe.
    # Removes any rows that have missing values for 'offices_latitude' or 'offices_longitude'.
    # Resets the index of the dataframe after dropping the specified columns and rows.
    df.drop(columns=['latitude', 'longitude'], inplace=True)
    df.dropna(subset=['offices_latitude', 'offices_longitude'], how='all', inplace=True)
    df = df.reset_index(drop=True)

    return df



def function_venue (venue, lat, lon, radius):

    # This function uses the Foursquare Places API to search for venues that match the input parameters
    # and returns the resulting JSON object containing information about the matching venues.
    url = f"https://api.foursquare.com/v3/places/search?query={venue}&ll={lat}%2C{lon}&radius={radius}"
    headers = {
        "accept": "application/json",
        "Authorization": token
    }
    response = requests.get(url, headers=headers).json()

    return response['results']



def matching_companies (df):

    # The code creates columns for the resulting list of venues ('vegan_rest', 'preschool', 'starbucks', and 'clubs') within a 500-meter radius of each office location.
    # Counts the number of venues within each list.
    df['vegan_rest'] = df.apply(lambda row: function_venue("vegan", row['offices_latitude'], row['offices_longitude'], 500), axis=1)
    df['num_vegan_rest'] = df['vegan_rest'].apply(lambda row: len(row))
    df['preschool'] = df.apply(lambda row: function_venue("preschool", row['offices_latitude'], row['offices_longitude'], 500), axis=1)
    df['num_preschool'] = df['preschool'].apply(lambda row: len(row))
    df['starbucks'] = df.apply(lambda row: function_venue("starbucks", row['offices_latitude'], row['offices_longitude'], 500), axis=1)
    df['num_starbucks'] = df['starbucks'].apply(lambda row: len(row))
    df['clubs'] = df.apply(lambda row: function_venue('night%20clubs', row['offices_latitude'], row['offices_longitude'], 500), axis=1)
    df['num_clubs'] = df['clubs'].apply(lambda row: len(row))

    return df



punctuation = {
    "vegan_rest": 8,
    "preschool": 5,
    "starbucks": 7,
    "club": 5
}

def weighs_function (punctuation):
    
    # This function calculates the total sum of values in the punctuation dictionary, and then calculates the % weight of each value in the dictionary with respect to the total sum. 
    # The function then returns a new dictionary containing the same keys as 'punctuation' but with values replaced by their respective percentage weights.
    total = sum(punctuation.values())
    weights = {k: round(v/total*100, 2) for k, v in punctuation.items()}

    return weights



weights = weighs_function(punctuation)



def function_weighted_punct (weights, col1, col2, col3, col4):

    # This function calculates a weighted sum of the input columns using the weights specified in the input dictionary, and returns the resulting weighted sum.
    weighted_punct = col1 * weights['vegan_rest'] \
                       + col2 * weights['preschool'] \
                       + col3 * weights['starbucks'] \
                       + col4 * weights['club']
    
    return weighted_punct



def final_punctuation (df):

    # This code adds a ne:w column to the dataframe containing the weighted sum of four numerical columns ('num_vegan_rest', 'num_preschool', 'num_starbucks', and 'num_clubs') using a function 'function_weighted_punct'. 
    # Sorts the rows of the dataframe 'df' in descending order based on the values in the weighted column.
    df['weighted_punct'] = df.apply(lambda row: function_weighted_punct(weights, row['num_vegan_rest'], row['num_preschool'], row['num_starbucks'], row['num_clubs']), axis=1)
    df = df.sort_values(by='weighted_punct', ascending=False)

    return df



def subset_function (df):

    # This code creates a subset of the dataframe where the value in the "weighted_punct" column is greater than 600
    df_subset = df[df['weighted_punct'] > 600]

    return df_subset



def pre_explode(row, name):

    # This code creates an empty list named "new_list". Then, it iterates over each element of the row in the specified column and extracts the latitude and longitude values.
    # Appends them to the "new_list". 
    # Returns the "new_list" of tuples.
    new_list = []
    for i in row[name]:
        lat = i["geocodes"]["main"]["latitude"]
        lon = i["geocodes"]["main"]["longitude"]
        new_list.append((lat, lon))

    return new_list



def explode_vegan (df_subset):

    # This code creates a subset of the dataframe that contains the expanded and exploded latitude and longitude coordinates of a specific location type (vegan_rest). 
    df_subset_vegan_rest = df_subset[['name', 'offices_state_code', 'offices_latitude', 'offices_longitude', 'vegan_rest', 'num_vegan_rest']]
    df_subset_vegan_rest['vegan_rest_coord'] = df_subset_vegan_rest.apply(lambda row: pre_explode(row, 'vegan_rest'), axis=1)
    df_subset_vegan_rest = df_subset_vegan_rest.explode('vegan_rest_coord')
    df_subset_vegan_rest = df_subset_vegan_rest.reset_index(drop=True)
    df_subset_vegan_rest[['latitude', 'longitude']] = df_subset_vegan_rest['vegan_rest_coord'].apply(lambda x: pd.Series([x[0], x[1]]))
    df_subset_vegan_rest = df_subset_vegan_rest.drop_duplicates(subset='vegan_rest_coord', keep='first')

    return df_subset_vegan_rest



def explode_preschool (df_subset):

    # This code creates a subset of the dataframe that contains the expanded and exploded latitude and longitude coordinates of a specific location type (preschool). 
    df_subset_preschool = df_subset[['name', 'offices_state_code', 'offices_latitude', 'offices_longitude', 'preschool', 'num_preschool']]
    df_subset_preschool['preschool_coord'] = df_subset_preschool.apply(lambda row: pre_explode(row, 'preschool'), axis=1)
    df_subset_preschool = df_subset_preschool.explode('preschool_coord')
    df_subset_preschool = df_subset_preschool.reset_index(drop=True)
    df_subset_preschool[['latitude', 'longitude']] = df_subset_preschool['preschool_coord'].apply(lambda x: pd.Series([x[0], x[1]]))
    df_subset_preschool = df_subset_preschool.drop_duplicates(subset='preschool_coord', keep='first')

    return df_subset_preschool



def explode_starbucks (df_subset):
 
    # This code creates a subset of the dataframe that contains the expanded and exploded latitude and longitude coordinates of a specific location type (starbucks). 
    df_subset_starbucks = df_subset[['name', 'offices_state_code', 'offices_latitude', 'offices_longitude', 'starbucks', 'num_starbucks']]
    df_subset_starbucks['starbucks_coord'] = df_subset_starbucks.apply(lambda row: pre_explode(row, 'starbucks'), axis=1)
    df_subset_starbucks = df_subset_starbucks.explode('starbucks_coord')
    df_subset_starbucks = df_subset_starbucks.reset_index(drop=True)
    df_subset_starbucks[['latitude', 'longitude']] = df_subset_starbucks['starbucks_coord'].apply(lambda x: pd.Series([x[0], x[1]]))
    df_subset_starbucks = df_subset_starbucks.drop_duplicates(subset='starbucks_coord', keep='first')

    return df_subset_starbucks



def explode_clubs (df_subset):

    # This code creates a subset of the dataframe that contains the expanded and exploded latitude and longitude coordinates of a specific location type (clubs). 
    df_subset_clubs = df_subset[['name', 'offices_state_code', 'offices_latitude', 'offices_longitude', 'clubs', 'num_clubs']]
    df_subset_clubs['clubs_coord'] = df_subset_clubs.apply(lambda row: pre_explode(row, 'clubs'), axis=1)
    df_subset_clubs = df_subset_clubs.explode('clubs_coord')
    df_subset_clubs = df_subset_clubs.reset_index(drop=True)
    df_subset_clubs[['latitude', 'longitude']] = df_subset_clubs['clubs_coord'].apply(lambda x: pd.Series([x[0], x[1]]))
    df_subset_clubs = df_subset_clubs.drop_duplicates(subset='clubs_coord', keep='first')

    return df_subset_clubs





