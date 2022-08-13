# PCSOLotto

PCSOLotto (Webscraper) is a Python class library for webscraping lottery results from the [PCSO website](https://www.pcso.gov.ph/SearchLottoResult.aspx)

## Installation

Use git on your local machine to `git clone` this repository:
```bash
git clone https://github.com/lonewanderer27/PCSOLotto-Webscraper
```

Or by clicking the `Code` button in this page, then `Download ZIP` then extract.

Then you can copy the `PCSOLotto.py` beside your python project where you wanna use it with.

### Import

```python
from PCSOLotto import PCSOLotto

# import pretty print
# for pretty printing of returned dictionary 
from pprint import pprint 

# initiate an object from the class
lotto = PCSOLotto()
```

## Simple Usage Examples

```python
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

```python
# returns all EZ2 results yesterday
pprint(
    lotto.results_today(
        games=['EZ2'])
    indent=2)


# returns all EZ2, Suertres & 6Digit results yesterday
pprint(
    lotto.results_today(
        games=['EZ2', 'Suertres', '6Digit'])
    indent=2)


# returns all 6/55 & 6/49 results yesterday
pprint(
    lotto.results_today(
        games=['6/55', '6/49'])
    indent=2)
```

And by default all of three methods we used prefix the jackpot price with ₱ sign, you can disable that by passing `peso_sign=False` parameter.

```python
# returns all 6/55 & 6/49 results yesterday
# but with ₱ sign omitted
pprint(
    lotto.results_today(
        games=['6/55', '6/49']),
        peso_sign=False
    indent=2)
```

## More Advanced Usage Examples

Methods described in Simple & Advanced Usage all use a method underneath called `results()` which takes five parameters that are described in the API Reference.

You can use this method directly if you want to customize the results.

```python
# Search for results from Aug 1 2022 to Aug 10 2022
# Note: the only accepted date format is YYYY/MM/DD
pprint(
    lotto.results('2022/08/01', '2022/08/10'),
    indent=2
)


# Search for 6/58 results from Aug 1 2022 to Aug 10 2022
pprint(
    lotto.results('2022/08/01', '2022/08/10', ['6/58']),
    indent=2
)


# Search for 6/58, 6/55 & 6/42 results
# from Aug 1 2022 to Aug 10 2022
pprint(
    lotto.results('2022/08/01', '2022/08/10', ['6/58', '6/55', '6/42']),
    indent=2
)


# Search for results every Mon, Wed, Fri
# from Aug 1 2022 to Aug 10 2022
pprint(
    lotto.results('2022/08/01', '2022/08/10', ['Mon', 'Wed', 'Fri']),
    indent=2
)
```
