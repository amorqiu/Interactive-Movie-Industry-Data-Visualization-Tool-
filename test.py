import unittest
from movie import *


class Test_scrape_data(unittest.TestCase):

    def test_movie_list(self):
        movie_list=get_movie_list()
        self.assertEqual(len(movie_list), 951)
        self.assertIsInstance(movie_list[0].name,str)
        self.assertEqual(str(movie_list[0]), "Insidious: The Last KeybyUniversal Pictures")


class TestDatabase(unittest.TestCase):

    def test_movie_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT name FROM Movie'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 951)
    def test_genre_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Distinct MovieId
            FROM Genre
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 951)

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT m.Name,m.Domestic_income
            FROM Movie m
                JOIN Genre g
                ON m.ID=g.MovieId
            WHERE [Genre]= "Comedy"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Goldbuster',186135), result_list)
        conn.close()

class TestMapping(unittest.TestCase):

    # we can't test to see if the maps are correct, but we can test that
    # the functions don't return an error!
    def test_show_movie(self):
        try:
            print(plot_graphs("Comedy"))
        except:
            self.fail()
    def test_show_table(self):
        try:
            print(plot_table('US',10))
        except:
            self.fail()

    def test_show_scatterplot(self):
        try:
            print(plot_scattorplot("Action"))
        except:
            self.fail()

    def test_show_perchart(self):
        try:
            print(plot_bar("Goldbuster"))
        except:
            self.fail()

unittest.main()
