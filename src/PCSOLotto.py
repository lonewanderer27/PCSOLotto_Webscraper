from bs4 import BeautifulSoup
import calendar
from datetime import datetime, timedelta
import requests


class PCSOLotto:

    def __init__(
        self,
        link: str = 'https://www.pcso.gov.ph/SearchLottoResult.aspx'
    ):
        self.__result_rows_raw = []
        self.__result_rows = {}
        self.result_list_str = []
        self.__link = link
        self.games_list = {
            58: 'Ultra Lotto 6/58',
            55: 'Grand Lotto 6/55',
            49: 'Super Lotto 6/49',
            45: 'Mega Lotto 6/45',
            42: 'Lotto 6/42',
            6: '6Digit',
            4: '4Digit',
            33: 'Suertres Lotto 11AM',
            32: 'Suertres Lotto 4PM',
            31: 'Suertres Lotto 9PM',
            23: 'EZ2 Lotto 11AM',
            22: 'EZ2 Lotto 4PM',
            21: 'EZ2 Lotto 9PM'
        }

    def __download_page(self) -> BeautifulSoup:
        '''Retrieves the BeautifulSoup4 object that contains the page html'''

        r = requests.get(self.__link)
        self.__soup = BeautifulSoup(r.text, 'html.parser')
        return self.__soup

    def __get_asp_hidden_vals(self) -> dict:
        '''Retrieves ASP Hidden Values used for authentication / cookie'''

        self.__viewstate = self.__soup.find(id='__VIEWSTATE')['value']
        self.__viewstategenerator = self.__soup.find(
            id='__VIEWSTATEGENERATOR')['value']
        self.__eventvalidation = self.__soup.find(
            id='__EVENTVALIDATION')['value']
        return {
            'VIEWSTATE': self.__viewstate,
            'VIEWSTATEGENERATOR': self.__viewstategenerator,
            'EVENTVALIDATION': self.__eventvalidation
        }

    def __construct_post_data(self) -> dict:
        '''Make the necessary post data'''
        # convert month int to text
        self.__start_month = calendar.month_name[self.__start_month]

        # convert month int to text
        self.__end_month = calendar.month_name[self.__end_month]

        data = {
            'ctl00$ctl00$cphContainer$cpContent$ddlStartMonth': self.__start_month,
            'ctl00$ctl00$cphContainer$cpContent$ddlStartDate': self.__start_day,
            'ctl00$ctl00$cphContainer$cpContent$ddlStartYear': self.__start_year,
            'ctl00$ctl00$cphContainer$cpContent$ddlEndMonth': self.__end_month,
            'ctl00$ctl00$cphContainer$cpContent$ddlEndDay': self.__end_day,
            'ctl00$ctl00$cphContainer$cpContent$ddlEndYear': self.__end_year,
            'ctl00$ctl00$cphContainer$cpContent$ddlSelectGame': '0',
            'ctl00$ctl00$cphContainer$cpContent$btnSearch': 'Search+Lotto',
            '__VIEWSTATE': self.__viewstate,
            '__VIEWSTATEGENERATOR': self.__viewstategenerator,
            '__EVENTVALIDATION': self.__eventvalidation
        }

        return data

    def __post_page(self, data: dict) -> BeautifulSoup:
        '''
        Posts to PCSO website with the form data
        and retrieves the BeautifulSoup4 object that
        contains the page html
        (with the desired start and end date)
        '''

        r = requests.post(self.__link, data)
        self.__soup = BeautifulSoup(r.text, 'html.parser')
        return self.__soup

    def __get_result_rows_raw(self) -> list:
        '''
        Retrieves all the raw bs4 rows that contains the lotto results
        '''

        # find all the rows, skip the first row as that's the table header
        rows = self.__soup.find_all('tr')[1:]
        self.__result_rows_raw = []
        for row in rows:
            cells = row.findChildren('td')
            self.__result_rows_raw.append(cells)

        return self.__result_rows_raw

    def __filter_result(self, result: dict) -> bool:
        '''
        Filters the results according to user's choice.
        '''

        # If user chose a set of games
        # Then check if the game is in that list
        # Otherwise include the game

        if self.__games:
            for game in self.__games:
                if game in result['lotto_game']:
                    if result['draw_date'] in self.__dates_between:
                        return True

        # Check if the draw date
        # matches one of the dates in daterange

        else:
            if result['draw_date'] in self.__dates_between:
                return True

    def __convert_raw_result_rows(self) -> dict:
        '''
        Converts all the raw bs4 rows into list of dictionaries.
        '''

        def __strip_text(row):
            return row.text.strip()

        def __split_combinations(combinations):
            return combinations.split("-")

        def __create_date_key(date):
            try:
                self.__result_rows[date]
            except KeyError:
                self.__result_rows[date] = {}

        for cells in self.__result_rows_raw:
            # strip texts around of the text row
            cells = list(map(__strip_text, cells))

            # split the combination string into a list of str
            cells[1] = __split_combinations(cells[1])

            # convert month/day/year to year/month/day
            cells[2] = datetime.strptime(
                                        cells[2],
                                        '%m/%d/%Y'
                                    ).strftime('%Y/%m/%d')

            # add Peso sign before jackpot price
            # if self.__peso_sign is True
            if self.__peso_sign:
                cells[3] = '₱' + cells[3]

            # convert the winners to int
            cells[4] = int(cells[4])

            result = {
                'lotto_game': cells[0],
                'combinations': cells[1],
                'draw_date': cells[2],
                'jackpot': cells[3],
                'winners': cells[4]
            }

            if self.__filter_result(result):

                # create the date key if it's empty
                __create_date_key(cells[2])

                # insert the result
                self.__result_rows[cells[2]][cells[0]] = result

                combinations_str = f'{"-".join(str(n) for n in cells[1])}'

                self.result_list_str.append(
                    f"{cells[0]}\nResult: {combinations_str}\nDraw Date: {cells[2]}\nJackpot: {cells[3]}\nWinners: {cells[4]}"
                )

        return self.__result_rows

    def __vali_date(self, date_str: str):
        return datetime.strptime(date_str, '%Y/%m/%d')

    def __gen_dates_between(self) -> list:
        '''
        Generates dates between start date & end date
        '''

        def gen_daterange(date1, date2):
            date1 = datetime.strptime(date1, '%Y/%m/%d')
            date2 = datetime.strptime(date2, '%Y/%m/%d')
            return [date1 + timedelta(days=x) for x in range((date2-date1).days + 1)]
    
        def convert_daterange(date):
            return str(date.strftime("%Y/%m/%d"))

        def filter_date_by_day(datesb):
            '''Removes dates that are not in chosen weekdays'''

            if datetime.strptime(
                                datesb, "%Y/%m/%d"
                                ).strftime('%a') in self.__days:
                return True

        # sdate = date(
        #     self.__start_year,
        #     self.__start_month,
        #     self.__start_day
        #     )
        # edate = date(
        #     self.__end_year,
        #     self.__end_month,
        #     self.__end_day
        # )

        # Generate dates between the start & end date
        # self.__dates_between = pandas.date_range(
        #     sdate, edate,
        #     freq='d'
        # ).strftime("%Y/%m/%d").tolist()

        sdate = f"{self.__start_year}/{self.__start_month}/{self.__start_day}"
        edate = f"{self.__end_year}/{self.__end_month}/{self.__end_day}"

        self.__dates_between = list(map(convert_daterange, gen_daterange(sdate, edate)))

        # If user has provided specific weekdays
        # Then append matching dates
        if self.__days:
            filtered_dates_between = []
            for datesb in self.__dates_between:
                if filter_date_by_day(datesb):
                    filtered_dates_between.append(datesb)
            self.__dates_between = filtered_dates_between

        return self.__dates_between

    def results(
        self,
        start_date: str,
        end_date: str,
        days: list = None,
        games: list = None,
        peso_sign: bool = True
    ) -> dict:
        '''
        Args:
        - start_date    (str)       : date to start searching                       | YYYY/MM/DD        | Required
        - end_date      (str)       : date to end searching                         | YYYY/MM/DD        | Required
        - days          list(str)   : days to select                                | Sun, Mon, Tue ... | Default = All Days, Optional
        - games         list(str)   : lotto games to search                         | EZ2, 6/42, 6/55   | Default = All Games, Optional
        - peso_sign     (bool)      : to prefix a peso sign in the jackpot, or not  | True or False     | Default = True, Optional

        Examples:
        >>> # Search for results from Aug 1 2022 to Aug 10 2022
        >>> lotto.results(start_date='2022/08/01', end_date='2022/08/10')
        >>>
        >>> # Search for 6/58 results from Aug 1 2022 to Aug 10 2022
        >>> lotto.results(start_date='2022/08/01', end_date='2022/08/10', games=['6/58'])
        >>>
        >>> # Search for 6/58, 6/55 & 6/42 results
        >>> # from Aug 1 2022 to Aug 10 2022
        >>> lotto.results(start_date='2022/08/01', end_date='2022/08/10', games=['6/58', '6/55', '6/42'])
        >>>
        >>> # Search for results every Mon, Wed and Fri
        >>> # from Aug 1 2022 to Aug 10 2022
        >>> lotto.results(start_date='2022/08/01', end_date='2022/08/10', days=['Mon', 'Wed', 'Fri'])
        '''

        # Validate date inputs
        sdate = self.__vali_date(start_date)
        edate = self.__vali_date(end_date)

        self.__games = games
        self.__start_year = sdate.year
        self.__start_month = sdate.month
        self.__start_day = sdate.day
        self.__end_year = edate.year
        self.__end_month = edate.month
        self.__end_day = edate.day
        self.__days = days
        self.__peso_sign = peso_sign

        # Generate dates between start date & end date
        # And optionally filter it based on the weekday
        self.__dates_between = {}
        self.__gen_dates_between()

        # Empty variables that might have a previous value
        self.__result_rows_raw = []
        self.__result_rows = {}
        self.result_list_str = []

        self.__download_page()               # download the webpage
        self.__get_asp_hidden_vals()         # get asp hidden vals for auth
        data = self.__construct_post_data()  # construct data that we'll POST
        self.__post_page(data)               # post data and get results
        self.__get_result_rows_raw()         # get the bs4 table rows
        self.__convert_raw_result_rows()     # convert each rows into dict
        return self.__result_rows

    def results_today(
        self,
        games: list = None,
        peso_sign: bool = True
    ):
        '''
        Retrieve lotto results today.
        Check self.results for options explanation.
        '''

        today = datetime.today()
        print(f"Today's Date: {today}")

        return self.results(
            start_date=today.strftime("%Y/%m/%d"),
            end_date=today.strftime("%Y/%m/%d"),
            games=games,
            peso_sign=peso_sign
            )

    def results_yesterday(
        self,
        games: list = None,
        peso_sign: bool = True
    ):
        '''
        Retrieve lotto results from yesterday.
        Check self.results for options explanation.
        '''

        edate = datetime.today()
        sdate = edate - timedelta(days=1)
        print(f"Yesterday's Date: {sdate}")

        return self.results(
            start_date=sdate.strftime("%Y/%m/%d"),
            end_date=sdate.strftime("%Y/%m/%d"),
            games=games,
            peso_sign=peso_sign
            )

    def results_default_pcso(
        self,
        games: list = None,
        peso_sign: bool = True
    ):
        '''
        Retrieve lotto results from 3 days prior up to today.
        Default selection on PCSO website.
        Check self.results for options explanation.
        '''

        edate = datetime.today()
        sdate = edate - timedelta(days=3)

        return self.results(
            start_date=sdate.strftime("%Y/%m/%d"),
            end_date=edate.strftime("%Y/%m/%d"),
            games=games,
            peso_sign=peso_sign
            )
