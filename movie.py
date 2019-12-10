import json
import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import plotly.graph_objects as go
#
# Part 1: Scrape data from database
#create cache file
CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

##create ident in cache file
def params_unique_combination(baseurl, params_d):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

### make request
def request_use_cache(unique_ident,url,pd):
    if unique_ident in CACHE_DICTION:
        #print("Getting cached data...")
        result = CACHE_DICTION[unique_ident]
    else:
        #print("Making a request for new data...")
        resp = requests.get(url,pd)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        result = CACHE_DICTION[unique_ident]
    return result

### create movie object
class Movie():
    def __init__(self, name, genre,distributor,url=None):
        self.name = name
        self.url= url
        # needs to be changed, obvi.
        self.distributor = distributor
        self.genre = genre

        self.release=0
        self.international_income=0
        self.domestic_income=0
    def __str__(self):
        return self.name + "by" + self.distributor

def get_movie_list():
    movie_list=[]
    name_list=[]
    genre_list=[]
    url_list=[]
    distributor_list=[]
    domestic_income_list=[]
    international_income_list=[]
    total=[]
    for i in range(1,13):
        if i<10:
            url="https://www.boxofficemojo.com/calendar/"+"2018-0"+str(i)+"-01/"
        else:
            url="https://www.boxofficemojo.com/calendar/"+"2018-"+str(i)+"-01/"
        unique_ident = params_unique_combination(url,params_d={})
        result=request_use_cache(unique_ident,url,pd={})
        page_soup = BeautifulSoup(result, 'html.parser')
        content=page_soup.find('table')
        movie=content.find_all('tr')
    #get_movie_list
        for i in movie:
            if i.find('h3'):
                name=i.find('h3').text
                genre=i.find("div",{'class':"a-section a-spacing-none mojo-schedule-genres"})
                if genre != None:
                    genre=genre.text.split()
                    genre_list.append(genre)
                else:
                    genre_list.append("UnKnow")
                distributor=i.find("td",{'class':"a-text-left mojo-field-type-release_studios"}).text.rstrip()
                distributor_list.append(distributor)
            #get income for each movie
                baseurl=i.find("a",{'class':"a-link-normal aok-float-left"})['href']
                url_list.append(baseurl)
                movieurl="https://www.boxofficemojo.com" + baseurl
                unique_ident_url=params_unique_combination(movieurl,params_d={})
                result_income=request_use_cache(unique_ident_url,movieurl,pd={})
                page = BeautifulSoup(result_income, 'html.parser')
                income_page= page.find("div",{'class':"a-section a-spacing-none mojo-performance-summary-table"})
                income=income_page.find_all("div",{'class':"a-section a-spacing-none"})
                release_page=page.find("div",{'class':"a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile"})
                release=release_page.find_all("div",{'class':"a-section a-spacing-none"})
                for i in release:
                    if i.text.split()[0]=="Widest":
                        number=i.text.split()[1]
                        theater=re.findall('[0-9]+',number)
                        theaternum=''
                        for i in theater:
                            theaternum=theaternum+i
                        theaternum=int(theaternum)
                count=0
                for i in income:
                    money=i.find("span",{'class':"a-size-medium a-text-bold"})
                    count=count+1
                    if count==1:
                        domestic_income=(money.text.split())[0].replace(",","").replace("$","")
                        if domestic_income=="–":
                            domestic_income=0
                        domestic_income_list.append(domestic_income)
                    elif count==2:
                        international_income=(money.text.split())[0].replace(",","").replace("$","")
                        if international_income=="–":
                            international_income=0
                        international_income_list.append(international_income)
                    else:
                        total.append((money.text.split())[0].replace(",","").replace("$",""))
                if name not in name_list:
                    name_list.append(name)
                    movie=Movie(name,genre,distributor,baseurl)
                    movie.international_income=international_income
                    movie.domestic_income=domestic_income
                    movie.theater=theaternum
                    movie_list.append(movie)
    return movie_list

#Part 2: Create Database
###start to create database
DBNAME = 'movie.db'
#create schema for database
def init_db():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Movie';
    '''
    c.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Genre';
    '''
    c.execute(statement)

    conn.commit()

    statement1 = '''
        CREATE TABLE 'Movie' ('Id' integer PRIMARY KEY, 'Name' text, 'Distributor' text, 'Theater' integer,'Domestic_income' integer, 'International_income' integer);
    '''
    statement2= '''
        CREATE TABLE 'Genre' ('Id' integer PRIMARY KEY, 'Genre' text, MovieId text, FOREIGN KEY (MovieId) REFERENCES Movie (id) ON UPDATE CASCADE);
        '''
    c.execute(statement1)
    c.execute(statement2)

    conn.commit()
    conn.close()

def insert_stuff():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    movie=get_movie_list()


    for i in movie:
        row=(i.name,i.distributor,i.theater,i.domestic_income,i.international_income)
        statement='''
        INSERT INTO "Movie"(Name,Distributor,Theater,Domestic_income,International_income) VALUES (?,?,?,?,?)'''
        c.execute(statement, row)
    conn.commit()


    genre_list=[]
    for i in movie:
        name=i.name
        if i.genre=="Unknow":
            genre_list.append((name,genre))
        elif i.genre==None:
            genre_list.append((name,"Unknow"))
        else:
            for g in i.genre:
                genre=g
                genre_list.append((name,genre))
    statement='''INSERT INTO "Genre"(MovieId,Genre) VALUES (?,?)'''
    c.executemany(statement,genre_list)
    conn.commit()
    conn.close()

def update_stuff():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    statement='''
    UPDATE Genre SET (MovieId) = (SELECT m.Id FROM Movie m WHERE Genre.MovieId=m.Name);
    '''
    c.execute(statement)

    conn.commit()
    conn.close()
init_db()
insert_stuff()
update_stuff()

#Part 3: Data Visualization
# get top 10 most successful distributor in one genre
def plot_graphs(genre):
    theater_select='''
            SELECT m.Distributor, AVG(m.Domestic_income) as average_income
            FROM Movie m
                JOIN Genre g
                ON m.ID=g.MovieId
            WHERE [Genre]= '''+"\""+str(genre)+"\"" +''' GROUP BY m.Distributor ORDER BY average_income DESC LIMIT 10'''
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    result=c.execute(theater_select).fetchall()
    conn.commit()
    conn.close()
    x=[]
    y=[]
    for row in result:
        x.append(row[0])
        y.append(row[1])
    fig = go.Figure([go.Bar(x=x, y=y)])
    #fig.show()
    fig.write_html('mapbox_1.html',auto_open=True)



# to show the most lucrative movie domestically or internationally or worldwide
def plot_table(parameter,limit):
    if parameter=="US":
        movie_select='''
            SELECT Name,Domestic_income
            FROM Movie
			ORDER BY Domestic_income DESC LIMIT ''' + str(limit)
    elif parameter=="International":
        movie_select='''
            SELECT m.Name,m.International_income
            FROM Movie m
			ORDER BY International_income DESC LIMIT ''' + str(limit)
    else:
        movie_select='''
            SELECT Name, sum(International_income+Domestic_income) AS Gross
            FROM Movie
			ORDER BY Gross DESC LIMIT ''' + str(limit)
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    result=c.execute(movie_select).fetchall()
    conn.commit()
    conn.close()
    x=[]
    y=[]
    for row in result:
        x.append(row[0])
        y.append(row[1])

    fig = go.Figure(data=[go.Table(header=dict(values=['Movies', str(parameter)]),
                 cells=dict(values=[x, y]))
                     ])
    fig.show()
#print(plot_table("US",20))



### plot the relationship between domestic_income and theater for one genre category
def plot_scattorplot(parameter):
    sql='''
      SELECT m.Domestic_income, m.Theater
            FROM Movie m
                LEFT JOIN Genre g
                ON m.ID=g.MovieId
            WHERE [Genre]='''+"\""+str(parameter)+"\""

    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    result=c.execute(sql).fetchall()
    conn.commit()
    conn.close()
    theater=[]
    income=[]
    for row in result:
        theater.append(row[0])
        income.append(row[1])
    fig = go.Figure(data=go.Scatter(x=theater, y=income, mode='markers'))
    #fig.show()
    fig.write_html('mapbox_1.html',auto_open=True)
#print(plot_scattorplot("Action"))


###plot the distrbution of boxoffice of a movie in 2019
def plot_bar(name):
    sql='''
      SELECT m.Domestic_income, m.International_income
            FROM Movie m
            WHERE Name='''+"\""+str(name)+"\""

    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    result=c.execute(sql).fetchall()
    conn.commit()
    conn.close()

    labels = ['Domestic','International']
    values = [result[0][0], result[0][1]]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    #fig.show()
    fig.write_html('mapbox_1.html',auto_open=True)



##interactive command
def interactive_prompt():
    parameter=["relation","success","distributor","movie"]
    help_text =  '''
                relation <genre>
                    available only if there is an existing movie genre
                    show the domestic_income and international_income of all movies in a spefic genre
                    graph: scatterplot
                    valid inputs: common movie genres "Comedy, War, Sport, ect." First letter needs to be Capitablized
                success <area> <limit>
                    available any time
                    list top movies with highest either domestic or international or gross revenue
                    graph: table
                    valid inputs: area accepts "US", "International" if novalue and other values are inputted, it will be default value as "gross"; limit requires an integer
                distributor <genre>
                    available only if there is an active site or nearby result set
                    show you who are the distributors good at producing average most lucrative movies in a specific genre
                    graph: barchart
                    valid input: common movie genres "Comedy, War, Sport, ect." First letter needs to be Capitablized
                movie <name>
                    available to all moveis released in 2018
                    show you the component of a movie's income
                    graph: piechart
                    valid input: movie name
                exit
                    exits the program
                help
                    lists available commands (these instructions)'''
    response = ''
    while response != 'exit':
        name=''
        response = input('Enter a command: ')
        if response == 'help':
            print(help_text)
            continue
        elif response == 'exit':
            print("bye")
            break
        elif response == '':
            print("Command not recognized:" + response)
            continue
        elif (response.split(" ")[0]) not in parameter:
            print("Command not recognized:" + response)
            continue
        elif response.startswith("relation"):
            genre=response.split(" ")[1]
            print(plot_scattorplot(genre))
            continue
        elif response.startswith("success"):
            limit=response.split(" ")[2]
            parameter=response.split(" ")[1]
            print(plot_table(parameter,limit))
            continue
        elif response.startswith("distributor"):
            genre=response.split(" ")[1]
            print(plot_graphs(genre)) 
	    continue
        else:
            object = response.split(" ")[1]
            print(plot_bar(object))
	    continue



if __name__=="__main__":
    interactive_prompt()
