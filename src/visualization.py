import folium
import pandas as pd
import json
from numpy import median
from folium import Choropleth, Circle, Marker, Icon, Map
import ast
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')



def pie_plot ():
    
    punctuation = {'vegan_rest': 32.0, 'preschool': 20.0, 'starbucks': 28.0, 'club': 20.0}

    # Convert the dictionary into a pandas DataFrame
    df = pd.DataFrame.from_dict(punctuation, orient='index', columns=['Percentage'])

    # Create the pie chart
    plt.pie(df['Percentage'], labels=df.index, autopct='%1.1f%%', colors=['#ffa600', '#008f5c', '#bc5090', '#ff6361'])

    # Add a title
    plt.title('Pie chart')

    # Save the plot
    plt.savefig("figures/pie_chart.png")

    # Show the plot
    plt.show()



def map_plot(df, df_subset_vegan_rest, df_subset_preschool, df_subset_starbucks, df_subset_clubs):
    
    # This code assigns the string values 'Vegan', 'Preschools', 'Starbucks', and 'Clubs' to the 'category_name' column of four different subsets of a dataframe.
    df_subset_vegan_rest['category_name'] = 'Vegan'
    df_subset_preschool['category_name'] = 'Preschools'
    df_subset_starbucks['category_name'] = 'Starbucks'
    df_subset_clubs['category_name'] = 'Clubs'

    # Concatenates the four dataframes into a single one.
    near_office = pd.concat([df_subset_vegan_rest, df_subset_preschool, df_subset_starbucks, df_subset_clubs], ignore_index=True)
    
    # This code creates a map with different feature groups for each category of location (vegan restaurants, Starbucks, preschools, clubs).  
    office_nearby = Map(location = [40.749376, -73.995323], zoom_start = 11.4)
    vegan_group = folium.FeatureGroup(name = f"Vegan restaurants ({near_office[near_office['category_name'] == 'Vegan'].shape[0]})")
    starbucks_group = folium.FeatureGroup(name = f"Starbucks ({near_office[near_office['category_name'] == 'Starbucks'].shape[0]})")
    preschool_group = folium.FeatureGroup(name = f"Preschools ({near_office[near_office['category_name'] == 'Preschools'].shape[0]})")
    clubs_group = folium.FeatureGroup(name = f"Clubs ({near_office[near_office['category_name'] == 'Clubs'].shape[0]})")

    # This code iterates through each row in the "near_office" dataframe and creates a dictionary called "company" containing the location and tooltip of each row. 
    # Based on the value of the "category_name" column in each row, it assigns a different color and icon to the "icon" variable. 
    # Creates a new marker with the location and icon properties, and adds it to the corresponding feature group (e.g., vegan, Starbucks, etc.). 
    # Adds all the feature groups to the "office_nearby" map.
    for index, row in near_office.iterrows():

        company = {
            "location": [row["latitude"], row["longitude"]],
            "tooltip": row["category_name"]
                 }


        if row["category_name"] == "Vegan":
            icon = Icon (
                color = "lightgreen",
                prefix="fa",
                icon="leaf"
                )
            
        elif row["category_name"] == "Starbucks":
            icon = Icon (
                color = "darkgreen",
                prefix="fa",
                icon="coffee"
                )
            
        elif row["category_name"] == "Preschools":
            icon = Icon (
                color = "blue",
                prefix="fa",
                icon="school"
                )
            
        elif row["category_name"] == "Clubs":
            icon = Icon (
                color = "darkblue",
                prefix="fa",
                icon="martini-glass"
                )


        new_marker = Marker (**company, icon = icon)
 
        if row["category_name"] == "Vegan":
            new_marker.add_to(vegan_group)
        
        elif row["category_name"] == "Starbucks":
            new_marker.add_to(starbucks_group)
        
        elif row["category_name"] == "Preschools":
            new_marker.add_to(preschool_group)
        
        elif row["category_name"] == "Clubs":
            new_marker.add_to(clubs_group)


    vegan_group.add_to(office_nearby)
    starbucks_group.add_to(office_nearby)
    preschool_group.add_to(office_nearby)
    clubs_group.add_to(office_nearby)

    # This code adds five Circle markers to the office_nearby map, each representing a different office location. 
    # It also adds a LayerControl to the map to allow toggling of the various feature groups.
    folium.LayerControl(collapsed=False, position="topleft").add_to(office_nearby)
    
    df = df.reset_index(drop=True)

    p1_lat_NY, p1_lon_NY, p2_lat_NY, p2_lon_NY, p3_lat_NY, p3_lon_NY = df['offices_latitude'][0], df['offices_longitude'][0], df['offices_latitude'][1], df['offices_longitude'][1], df['offices_latitude'][2], df['offices_longitude'][2]
    p1_lat_CA, p1_lon_CA, p2_lat_CA, p2_lon_CA = df['offices_latitude'][3], df['offices_longitude'][3], df['offices_latitude'][4], df['offices_longitude'][4]

    folium.Circle(location=[p1_lat_NY, p1_lon_NY], popup='Point 1A', fill_color='#ff0000', radius=500, weight=2, color="#000000").add_to(office_nearby)
    folium.Circle(location=[p2_lat_NY, p2_lon_NY], popup='Point 1B', fill_color='#00ff00', radius=500, weight=2, color="#000000").add_to(office_nearby)
    folium.Circle(location=[p3_lat_NY, p3_lon_NY], popup='Point 1C', fill_color='#0000ff', radius=500, weight=2, color="#000000").add_to(office_nearby)
    folium.Circle(location=[p1_lat_CA, p1_lon_CA], popup='Point 1D', fill_color='#20B2AA', radius=500, weight=2, color="#000000").add_to(office_nearby)
    folium.Circle(location=[p2_lat_CA, p2_lon_CA], popup='Point 1E', fill_color='#00CED1', radius=500, weight=2, color="#000000").add_to(office_nearby)

    return office_nearby

