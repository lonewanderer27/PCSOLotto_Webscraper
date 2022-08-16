# PCSOLotto

PCSOLotto (Webscraper) is a Python program for webscraping lottery results from the [PCSO website](https://www.pcso.gov.ph/SearchLottoResult.aspx)
Can be be both used in CLI and embedded in a python program.

## Installation

Use pip to install to your local machine.
```bash
pip install PCSOLotto-Webscraper
```

Or if you want the latest version, use git on your local machine to clone this repository:
```bash
git clone https://github.com/lonewanderer27/PCSOLotto_Webscraper
```

Then you can copy `./src/PCSLotto/PCSOLotto.py` file to your python project where you wanna use it with.

# CLI

Results are displayed in a tabular form.

## Simple Usage Examples

```bash
# display results today
# only works after 10PM or when PCSO has posted the results on the website.
./PCSOLotto.py -t

# display results yesterday
./PCSOLotto.py -y

# display results 3 days prior up to today
./PCSOLotto.py -z
```

Note: Using -t --results_today, -y --results_yesterday, -z --results_default_pcso overrides the -s --start_date and -e --end_date

## Advanced Usage Examples

```bash
# display EZ2 results yesterday
./PCSOLotto.py -y --games 'EZ2'

# display EZ2, Suertres & 6Digit results yesterday
./PCSOLotto.py -y --games 'EZ2' 'Suertres' '6Digit'

# display Suertres 11AM Draw result yesterday
./PCSOLotto.py -y --games 'Suertres Lotto 11AM'

# display 6/55 & 6/49 results yesterday
./PCSOLotto.py -y --games '6/55' '6/49'
```

By default, jackpot prices are prefixed with ₱ sign, you can disable that by adding `--peso_sign false` argument

```bash
# display 6/55 & 6/49 results yesterday
# but with ₱ sign omitted
./PCSOLotto.py -y --games '6/55' '6/49' --peso_sign false
```

## More Advanced Usage Examples

```bash
# display results from Aug 1 2022 to Aug 10 2022
# Note: the only accepted date format is YYYY/MM/DD

./PCSOLotto.py --start_date '2022/08/01' --end_date '2022/08/10'

# display 6/58 results from Aug 1 2022 to Aug 10 2022
./PCSOLotto.py --start_date '2022/08/01' --end_date '2022/08/10' --games '6/58'

# display 6/58, 6/55 & 6/42 results
# from Aug 1 2022 to Aug 10 2022
./PCSOLotto.py --start_date '2022/08/01' --end_date '2022/08/10' --games '6/58' '6/55' '6/42'

# display results every Mon, Wed, Fri
# from Aug 1 2022 to Aug 10 2022
./PCSOLotto.py --start_date '2022/08/01' --end_date '2022/08/10' --days Mon Wed Fri

# display only EZ2 results every Mon, Wed, Fri
# from Aug 1 2022 to Aug 10 2022
./PCSOLotto.py --start_date '2022/08/01' --end_date '2022/08/10' --days Mon Wed Fri --games 'EZ2'
```

See [Table-of-Games](#Table-of-Games) for complete list of game aliases and how to filter time specific draws for EZ2 & Suertres. 

## CLI Options Reference
```bash
usage: PCSOLotto.py [-h] [-s START_DATE] [-e END_DATE] [-t] [-y] [-z] [-d [DAYS ...]] [-g [GAMES ...]] [-p PESO_SIGN] [-c CSV] [-j JSON]

CLI tool for web scraping lottery results from the PCSO website

options:
  -h, --help            show this help message and exit
  -s START_DATE, --start_date START_DATE
                        date to start searching. Format: YYYY/MM/DD (default: None)
  -e END_DATE, --end_date END_DATE
                        date to end searching. Format: YYYY/MM/DD (default: None)
  -t, --results_today   retrieve lotto results today (default: False)
  -y, --results_yesterday
                        retrieve lotto results yesterday (default: False)
  -z, --results_default_pcso
                        retrieve lotto results from 3 days prior up to today (default: False)
  -d [DAYS ...], --days [DAYS ...]
                        days to select (default: None)
  -g [GAMES ...], --games [GAMES ...]
                        lotto games to search (default: None)
  -p PESO_SIGN, --peso_sign PESO_SIGN
                        to prefix a peso sign in the jackpot, or not (default: True)
  -c CSV, --csv CSV     csv file to output the results to (default: None)
  -j JSON, --json JSON  json file to output the results to (default: None)
```

# API / Library

All methods return a dictionary, organized by keys under which the actual results are contained in.

## Simple Usage Examples

```python
from PCSOLotto import PCSOLotto
from pprint import pprint # for pretty printing of returned dictionary 

# initiate an object from the class
lotto = PCSOLotto()


# return results today
# only works 10PM onwards as that is when PCSO updates their website
pprint(lotto.results_today(), indent=2)


# return results yesterday
pprint(lotto.results_yesterday(), indent=2)


# return results for the past 3 days
# default selection on the PCSO website
pprint(lotto.results_latest(), indent=2)
```

## Advanced Usage Examples

Methods `results_today()`, `results_yesterday()` and `results_latest()` all have an optional `games` parameter where you can customize what lottery games get returned.

To match a specific game, we have to use an alias or the whole name of the lottery game. Refer to [Table-of-Games](#Table-of-Games) for these aliases.

```python
from PCSOLotto import PCSOLotto
from pprint import pprint # for pretty printing of returned dictionary 

# initiate an object from the class
lotto = PCSOLotto()


# return EZ2 results yesterday
pprint(
    lotto.results_yesterday(
        games=['EZ2']),
    indent=2)


# return EZ2, Suertres & 6Digit results yesterday
pprint(
    lotto.results_yesterday(
        games=['EZ2', 'Suertres', '6Digit']),
    indent=2)


# return 6/55 & 6/49 results yesterday
pprint(
    lotto.results_yesterday(
        games=['6/55', '6/49']),
    indent=2)
```

And by default all of three methods we used prefix the jackpot price with ₱ sign, you can disable that by passing `peso_sign=False` parameter.

```python
# return 6/55 & 6/49 results yesterday
# but with ₱ sign omitted
pprint(
    lotto.results_yesterday(
        games=['6/55', '6/49'], 
        peso_sign=False),
    indent=2)
```

## More Advanced Usage Examples

Methods described in Simple & Advanced Usage all use a method underneath called `results()` which takes five parameters that are described in the [API-Reference](#API-Reference)

You can use this method directly if you want to customize the results date.

```python
from PCSOLotto import PCSOLotto
from pprint import pprint # for pretty printing of returned dictionary 

# initiate an object from the class
lotto = PCSOLotto()


# Search for results from Aug 1 2022 to Aug 10 2022
# Note: the only accepted date format is YYYY/MM/DD
pprint(
    lotto.results(
        start_date='2022/08/01', 
        end_date='2022/08/10'),
    indent=2
)


# Search for 6/58 results from Aug 1 2022 to Aug 10 2022
pprint(
    lotto.results(
        start_date='2022/08/01', 
        end_date='2022/08/10', 
        games=['6/58']),
    indent=2
)


# Search for 6/58, 6/55 & 6/42 results
# from Aug 1 2022 to Aug 10 2022
pprint(
    lotto.results(
        start_date='2022/08/01', 
        end_date='2022/08/10', 
        games=['6/58', '6/55', '6/42']),
    indent=2
)


# Search for results every Mon, Wed, Fri
# from Aug 1 2022 to Aug 10 2022
pprint(
    lotto.results(
        start_date='2022/08/01', 
        end_date='2022/08/10', 
        days=['Mon', 'Wed', 'Fri']),
    indent=2
)
```

# API-Reference

| Parameter    | Type     | Format       | Description                |
| :--------    | :------- | :------------|:------------------------- |
| `start_date` | `string` | YYYY/MM/DD   |**Required**. date to start searching |
| `end_date`   | `string` | YYYY/MM/DD   |**Required**. date to end searching |
| `days`       | `list(string)` | ['Sun', 'Mon'] ... | **Optional**. days to select |
| `games`      | `list(string)` | ['EZ2', 'Suetres'] ... | **Optional**. games to select |
| `peso_sign`  | `bool`   | `True` or `False` | **Optional**. to prefix a peso sign in the jackpot, or not |




# Table-of-Games

Note: 
Using "Suertres" alone will match all draws that happen in 11AM, 4PM & 9PM 

So if you only want the 4PM draw, use "Suertres Lotto 4PM" instead. The same concept applies for EZ2.

| Alias               	| Game Full Name      	|
|---------------------	|---------------------	|
| 6/58                	| Ultra Lotto 6/58    	|
| 6/55                	| Grand Lotto 6/55    	|
| 6/49                	| Super Lotto 6/49    	|
| 6/45                	| Mega Lotto 6/45     	|
| 6/42                	| Lotto 6/42          	|
| 6Digit              	| 6Digit              	|
| 4Digit              	| 4Digit              	|
| Suetres             	| Suetres             	|
| Suertres Lotto 11AM 	| Suertres Lotto 11AM 	|
| Suertres Lotto 4PM  	| Suertres Lotto 4PM  	|
| Suertres Lotto 9PM  	| Suertres Lotto 9PM  	|
| EZ2                 	| EZ2 / 2Digit        	|
| EZ2 Lotto 11AM      	| EZ2 Lotto 11AM      	|
| EZ2 Lotto 4PM       	| EZ2 Lotto 4PM       	|
| EZ2 Lotto 9PM       	| EZ2 Lotto 9PM       	|
