# PCSOLotto

PCSOLotto (Webscraper) is a Python class library for webscraping lottery results from the [PCSO website](https://www.pcso.gov.ph/SearchLottoResult.aspx)

## Installation

Use git on your local machine to `git clone` this repository:
```bash
git clone https://github.com/lonewanderer27/PCSOLotto_Webscraper
```

Or by clicking the `Code` button in this page, then `Download ZIP` then extract.

Then you can copy the `PCSOLotto.py` beside your python project where you wanna use it with.

## Simple Usage Examples

```python
from PCSOLotto import PCSOLotto
from pprint import pprint # for pretty printing of returned dictionary 

# initiate an object from the class
lotto = PCSOLotto()


# returns all lottery results today as dictionary
# only works 10PM onwards as that is when PCSO updates their website
pprint(lotto.results_today(), indent=2)


# returns all lottery results yesterday as dictionary
pprint(lotto.results_yesterday(), indent=2)


# returns all lottery results for the past 3 days as dictionary
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


# returns all EZ2 results yesterday
pprint(
    lotto.results_yesterday(
        games=['EZ2'])
    indent=2)


# returns all EZ2, Suertres & 6Digit results yesterday
pprint(
    lotto.results_yesterday(
        games=['EZ2', 'Suertres', '6Digit'])
    indent=2)


# returns all 6/55 & 6/49 results yesterday
pprint(
    lotto.results_yesterday(
        games=['6/55', '6/49'])
    indent=2)
```

And by default all of three methods we used prefix the jackpot price with ₱ sign, you can disable that by passing `peso_sign=False` parameter.

```python
# returns all 6/55 & 6/49 results yesterday
# but with ₱ sign omitted
pprint(
    lotto.results_yesterday(
        games=['6/55', '6/49']),
        peso_sign=False
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
