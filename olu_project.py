import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.bbc.co.uk/sport/football/premier-league/table"


class PremierLeague:
    url = "https://www.bbc.co.uk/sport/football/premier-league/table"

    def __init__(self, url):
        self.url = url
        self.response = requests.get(url)
        self.fixture_page = BeautifulSoup(self.response.content, 'lxml')
        print(pd.read_html(str(self.fixture_page))[0])
        self.table = self.fixture_page.select("table.gs-o-table")[0]
        self.columns = self.table.find("thead").find_all("th")
        self.column_names = [c.string for c in self.columns]
        self.table_rows = self.table.find("tbody").find_all("tr")
        self.table_to_df()
        
        #This is a test change

    def get_pl_table_meta_data(self):
        return self.table

    def get_columns(self):
        self.columns = self.table.find("thead").find_all("th")
        self.column_names = [c.string for c in self.columns]

    def get_table_rows(self):
        return self.table_rows

    def table_to_df(self):
        l = []
        for tr in self.table_rows:
            td = tr.find_all('td')
            row = [str(tr.get_text()) for tr in td]
            l.append(row)
        df = pd.DataFrame(l, columns=self.column_names)
        # df.to_excel('premier.xlsx', index=False)
        print(df)

# df = pd.DataFrame(l, columns=column_names)


PremierLeague(url)
