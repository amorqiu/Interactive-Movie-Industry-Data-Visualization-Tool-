● Data sources used, including instructions for a user to access the data sources

My data is scraped from a movie website https://www.boxofficemojo.com/calendar/ which contains the movie name, distributor, revenues and ect. I scraped all movies released in 2018, in total 951 movies. Firstly, I scraped all the movie names in the baseurl and get all detail urls for each movie. And then I made request to each single url and get distributors, wide theaters, and revenue information. 


● Brief description of how your code is structured, including the names of significant data processing functions (just the 2- 3 most important functions

My code is mainly consisting of three major parts
Part 1: Scraping data from website
The most importance function here is the get_movie_list() which is used to scrape data from website. Actually, some movies may appear more than once in different pages. So I used if condition to filter all movies that has been added into my list and created movie objects which has 3 required parameters, genre, name and distributors

Part 2: Create Database
The most importance function here is insert_stuff(). Since each movie has more than one genre, so here I used for loop to create multiple tuples for each movie so that every row will only contain one movie and one genre. My relational Database is connected through movie name or MovieID in genre table.


● Brief user guide, including how to run the program and how to choose presentation options.

I have four presentation ways. And detail guide lines is listed below.
    relation <genre>
                    available only if there is an existing movie genre
                    show the domestic_income and international_income of all movies in a spefic genre
                    graph: scatterplot
                    valid inputs: common movie genres "Comedy, War, Sport, ect." First letter needs to be Capitablized
                success <area> <limit>
                    available any time
                    list top movies with highest either domestic or international or gross revenue
                    graph: table
                    valid inputs: area accepts "US", "International" if novalue and other values are inputted, it will be default value                     as "gross"; limit requires an integer
                distributor <genre>
                    available only if there is an active site or nearby result set
                    show you who are the distributors good at producing average most lucrative movies in a specific genre
                    graph: barchart
                    valid input: common movie genres "Comedy, War, Sport, ect." First letter needs to be Capitablized
                movie <name>
                    available to all moveis released in 2018
                    show you the component of a movie's income
                    graph: piechart
