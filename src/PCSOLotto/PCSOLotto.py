#!/usr/bin/env python

from bs4 import BeautifulSoup
import calendar
import pytz
from datetime import datetime, timedelta
import requests
import argparse
from prettytable import PrettyTable
import json
from pprint import pprint


class PCSOLotto:

    def __init__(
        self,
        link: str = 'https://www.pcso.gov.ph/SearchLottoResult.aspx',
        headers: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0"
    ):
        self.__results_raw = []
        self.results_dict = {}
        self.results_str_list = []
        self.results_table = PrettyTable(
            ['Lotto Game',
             'Combinations',
             'Draw Date',
             'Jackpot (₱)',
             'Winners'])
        self.__link = link
        self.__headers = headers
        self.games_list = {
            58: 'Ultra Lotto 6/58',
            55: 'Grand Lotto 6/55',
            49: 'Superlotto 6/49',
            45: 'Megalotto 6/45',
            42: 'Lotto 6/42',
            6: '6D Lotto',
            4: '4D Lotto',
            33: '3D Lotto 2PM',
            32: '3D Lotto 5PM',
            31: '3D Lotto 9PM',
            23: '2D Lotto 11AM',
            22: '2D Lotto 4PM',
            21: '2D Lotto 9PM'
        }

    def __download_page(self) -> BeautifulSoup:
        '''Retrieves the BeautifulSoup4 object that contains the page html'''

        r = requests.get(self.__link, headers={
            'user-agent': self.__headers
        })
        self.__soup = BeautifulSoup(r.text, 'html.parser')
        # print(self.__soup.contents)
        return self.__soup

    def __get_asp_hidden_vals(self) -> dict:
        '''Retrieves ASP Hidden Values used for authentication / cookie'''

        self.__viewstate = self.__soup.find(id='__VIEWSTATE')['value']
        self.__viewstategenerator = self.__soup.find(
            id='__VIEWSTATEGENERATOR')['value']
        self.__eventvalidation = self.__soup.find(
            id='__EVENTVALIDATION')['value']
        # print(f"__viewstate: {self.__viewstate}")
        # print(f"__viewstategenerator: {self.__viewstategenerator}")
        # print(f"__eventvalidation: {self.__eventvalidation}")
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

        r = requests.post(url=self.__link, data=data, headers={
            'user-agent': self.__headers
        })
        self.__soup = BeautifulSoup(r.text, 'html.parser')
        return self.__soup

    def __get_result_rows_raw(self) -> list:
        '''
        Retrieves all the raw bs4 rows that contains the lotto results
        '''

        # find all the rows, skip the first row as that's the table header
        rows = self.__soup.find_all('tr')[1:]
        self.__results_raw = []
        for row in rows:
            cells = row.findChildren('td')
            self.__results_raw.append(cells)

        return self.__results_raw

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
        Converts bs4 rows into output variables.
        '''

        def __strip_text(row):
            return row.text.strip()

        def __split_combinations(combinations):
            return combinations.split("-")

        def __create_date_key(date):
            try:
                self.results_dict[date]
            except KeyError:
                self.results_dict[date] = {}

        for cells in self.__results_raw:
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

                # insert the result to results_dict
                self.results_dict[cells[2]][cells[0]] = result

                # convert combination list to string
                combinations_str = f'{"-".join(str(n) for n in cells[1])}'

                # append the result to results_list_str
                self.results_str_list.append(
                    f"{cells[0]}\nResult: {combinations_str}\nDraw Date: {cells[2]}\nJackpot: {cells[3]}\nWinners: {cells[4]}"
                )

                # append results to results_table
                self.results_table.add_row(
                    [cells[0], combinations_str, cells[2], cells[3], cells[4]]
                )

        return self.results_dict

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

        # Reset variables that might have a previous value
        self.__results_raw = []
        self.results_dict = {}
        self.results_str_list = []
        self.results_table = PrettyTable(
            ['Lotto Game',
             'Combinations',
             'Draw Date',
             'Jackpot (₱)',
             'Winners'])

        # Generate dates between start date & end date
        # And optionally filter it based on the weekday
        self.__dates_between = {}
        self.__gen_dates_between()

        self.__download_page()               # download the webpage
        self.__get_asp_hidden_vals()         # get asp hidden vals for auth
        data = self.__construct_post_data()  # construct data that we'll POST
        self.__post_page(data)               # post data and get results
        self.__get_result_rows_raw()         # get the bs4 table rows
        self.__convert_raw_result_rows()     # convert rows to output variables
        return self.results_dict

    def results_today(
        self,
        games: list = None,
        peso_sign: bool = True
    ):
        '''
        Retrieve lotto results today.
        Check self.results for options explanation.
        '''

        tz = pytz.timezone("Asia/Manila")
        today = datetime.today().astimezone(tz)
        # print(f"Today's Date: {today.strftime('%Y/%m/%d')}")

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

        tz = pytz.timezone("Asia/Manila")
        edate = datetime.today().astimezone(tz)
        sdate = edate - timedelta(days=1)
        # print(f"Yesterday's Date: {sdate.strftime('%Y/%m/%d')}")

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

        tz = pytz.timezone("Asia/Manila")
        edate = datetime.today().astimezone(tz)
        sdate = edate - timedelta(days=3)
        # print(f"Today's Date: {edate.strftime('%Y/%m/%d')}")
        # print(f"3 Days Ago Date: {sdate.strftime('%Y/%m/%d')}")

        return self.results(
            start_date=sdate.strftime("%Y/%m/%d"),
            end_date=edate.strftime("%Y/%m/%d"),
            games=games,
            peso_sign=peso_sign
            )


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                    description='CLI tool for web scraping lottery '
                                'results from the PCSO website',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s',
        '--start_date',
        type=str,
        default=None,
        help='date to start searching. Format: YYYY/MM/DD')
    parser.add_argument(
        '-e',
        '--end_date',
        type=str,
        default=None,
        help='date to end searching. Format: YYYY/MM/DD')
    parser.add_argument(
        '-t',
        '--results_today',
        default=False,
        action='store_true',
        help='retrieve lotto results today')
    parser.add_argument(
        '-y',
        '--results_yesterday',
        default=False,
        action='store_true',
        help='retrieve lotto results yesterday')
    parser.add_argument(
        '-z',
        '--results_default_pcso',
        default=False,
        action='store_true',
        help='retrieve lotto results from 3 days prior up to today')
    parser.add_argument(
        '-d',
        '--days',
        type=str,
        nargs='*',
        help='days to select',
        default=None)
    parser.add_argument(
        '-g',
        '--games',
        type=str,
        nargs='*',
        help='lotto games to search',
        default=None)
    parser.add_argument(
        '-p',
        '--peso_sign',
        type=lambda x: (str(x).lower() == 'true'),
        default=True,
        help='to prefix a peso sign in the jackpot, or not')
    parser.add_argument(
        '-c',
        '--csv',
        type=str,
        default=None,
        help='csv file to output the results to')
    parser.add_argument(
        '-j',
        '--json',
        type=str,
        default=None,
        help='json file to output the results to')

    args = parser.parse_args()
    config = vars(args)

    # pprint(config)
    arguments_sufficient = True

    lotto = PCSOLotto()

    if config['results_today']:
        lotto.results_today(
            config['games'],
            config['peso_sign'])
        arguments_sufficient = True

    elif config['results_yesterday']:
        lotto.results_yesterday(
            config['games'],
            config['peso_sign'])
        arguments_sufficient = True

    elif config['results_default_pcso']:
        lotto.results_default_pcso(
            config['games'],
            config['peso_sign'])
        arguments_sufficient = True

    else:
        if config['start_date'] is None:
            print("start_date argument is empty")

        elif config['end_date'] is None:
            print("end_date argument is empty")

        else:
            lotto.results(
                start_date=config['start_date'],
                end_date=config['end_date'],
                days=config['days'],
                games=config['games'],
                peso_sign=config['peso_sign'])
            arguments_sufficient = True

    if arguments_sufficient is True:

        # print the results in table format
        print(lotto.results_table)

        # write results to csv file
        if config['csv']:
            with open(config['csv'], 'w', newline='') as csv_file:
                csv_file.write(lotto.results_table.get_csv_string())
                csv_file.close()

        # write results to json file
        if config['json']:
            with open(config['json'], 'w') as json_file:
                json.dump(
                    lotto.results_dict,
                    json_file,
                    indent=4,
                    ensure_ascii=False)
                json_file.close()
