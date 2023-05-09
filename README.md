# Project3-geospatial

## Goal
The goal of this project is to find a location for the new company offices to grow.

## Requirements
- Developers like to be near successful tech startups --> Nearby companies tha have raised at least 1 Million dollars.
- Designers like to go to design talks and share knowledge --> Nearby companies that do design.
- The CEO is vegan --> Nearby vegan restaurants.
- Executives like Starbucks A LOT --> Nearby Starbucks.
- Account managers need to travel a lot --> Nearby internationa airports.
- Everyone in the company is between 25 and 40 --> Nearby night clubs.

## Methodology
Find those companies that meet as many requirements as possible, then select the most suitable one and take its coordinates as the reference for the location of the new company.

## Steps
### Mongo DB collection
1. Within the Mongo DB collection named "companies", select those companies that have raised at least 1 Million dollars and do design.
2. Count the number of companies by country and select USA as the chosen ubication, since its the most frequent country by far.
3. Count the number of companies by state and limit the companies located in the 4 most frequent states. Those states are New York, California, Florida and Illinois.
4. Search manually for the latitude and longitude of a reduced number of companies, since its coordinates are missing from the "companies" collection in Mongo.
### API search
5. Use the Foursquare Places API to search for places. 
6. Give a punctuation to each requirement and then weight each puctuation (see the graph below):

![image](https://user-images.githubusercontent.com/83134591/236970942-d93c6e37-0b84-403a-b343-4429df4271f3.png)

7. 




