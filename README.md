# PySBR

> A Python client for accessing the Sportsbook Review GraphQL endpoint.

[![Python Version][python-image]][python-url]
[![Build Status][circleci-image]][circleci-url]

This library allows you to get odds and other information from [Sportsbook Review](https://SportsbookReview.com) (SBR) for any of the leagues that are supported on the website, including NFL, NCAAB, UFC, ATP, EPL and many others. For a given event, you can get the current, best, opening lines and line history for any combination of betting markets and sportsbooks available on the website.

The SBR GraphQL endpoint is undocumented and subject to change, so use at your own risk. Try and avoid getting rate limited so we can keep this available for everyone to use!

Project documentation found on [ReadTheDocs][readthedocs]

There is also a [discord channel][discord] set up for this project that may be helpful.

![example-img](https://raw.githubusercontent.com/JeMorriso/PySBR/main/docs/img/readme250.gif)

## Installation

```sh
pip install python-sbr
```

## Examples

```python
from pysbr import *
from datetime import datetime
```

### Current lines for Sunday's NFL games

```python
dt = datetime.strptime('2020-12-06', '%Y-%m-%d')

nfl = NFL()
sb = Sportsbook()
```

`NFL` and `Sportsbook` are examples of config classes that are provided so you don't need to remember various interal IDs, such as team, league, sport, sportsbook, or betting market ids. The full list of config classes can be found in the documentation.

Using the `NFL` config class to get the NFL's league id, the `EventsByDate` query can then be used to retrieve all the events on some date for a given league or sport.

```python
e = EventsByDate(nfl.league_id, dt)
```

All queries have `list` and `dataframe` as available instance methods, producing a readable and formatted list or dataframe of the server response. You can also view the raw response from the server by accessing the `_raw` instance variable.

```python
e.list()[0]
```

```python
    {'scores': [],
     'sport id': 4,
     'league id': 16,
     'season id': 8582,
     'event id': 4143414,
     'description': 'Jacksonville Jaguars@Minnesota Vikings',
     'location': 'Minneapolis',
     'country': 'USA',
     'event status': 'scheduled',
     'datetime': '2020-12-06T10:00:00-08:00',
     'stadium type': 'artificial',
     'participants': [{'participant id': 1529,
       'is home': False,
       'source': {'name': 'Jacksonville',
        'nickname': 'Jaguars',
        'short name': 'Jacksonville',
        'abbreviation': 'JAC',
        'location': 'Jacksonville'}},
      {'participant id': 1541,
       'is home': True,
       'source': {'name': 'Minnesota',
        'nickname': 'Vikings',
        'short name': 'Minnesota',
        'abbreviation': 'MIN',
        'location': 'Minnesota'}}],
     'event group': {'event group id': 22,
      'name': 'REG Week 13',
      'alias': 'Week 13'}}
```

Then you can get the current lines for any betting markets and sportsbooks of interest by using `CurrentLines`.

```python
cl = CurrentLines(e.ids(), nfl.market_ids(['1Qou', 'ps', '1st half moneyline']), sb.ids(['Pinnacle', 'Bovada']))
```

Notice how you can use the `NFL` config class to find the betting market ids for 1st quarter over/under, full game point spread, and 1st half moneyline. See the documentation for accepted formats. Similarly, you can use `Sportsbook` to find sportsbook ids.

```python
cl.list(e)[0]
```

```python
    {'market id': 91,
     'event id': 4143414,
     'sportsbook id': 20,
     'datetime': '2020-12-05T07:26:01-08:00',
     'participant id': 1529,
     'spread / total': 0,
     'decimal odds': 3.56,
     'american odds': 256,
     'event': 'Jacksonville Jaguars@Minnesota Vikings',
     'market': '1st Half - Draw No Bet',
     'sportsbook': 'Pinnacle',
     'participant': 'JAC'}
```

In order to get the 'event', 'market', 'sportsbook' and 'participant' fields, pass the event object into `list` or `dataframe` for any lines-related query.

---

If an event is already completed, 'scores' will be populated in the response. The score data can then be used to calculate the result of the bet.

```python
dt = datetime.strptime('2020-11-30', '%Y-%m-%d')

e = EventsByDate(nfl.league_id, dt)
cl = CurrentLines(e.ids(), nfl.market_ids(['1Qou', 'ps', '1st half moneyline']), sb.ids(['Pinnacle', 'Bovada']))

cl.list(e)[:2]
```

```python
    [{'market id': 91,
      'event id': 4143550,
      'sportsbook id': 20,
      'datetime': '2020-11-30T17:12:25-08:00',
      'participant id': 1536,
      'spread / total': 0,
      'decimal odds': 2.7,
      'american odds': 170,
      'event': 'Seattle Seahawks@Philadelphia Eagles',
      'market': '1st Half - Draw No Bet',
      'result': 'L',
      'profit': -100.0,
      'participant score': 17,
      'sportsbook': 'Pinnacle',
      'participant': 'PHI'},
     {'market id': 91,
      'event id': 4143550,
      'sportsbook id': 20,
      'datetime': '2020-11-30T17:12:25-08:00',
      'participant id': 1548,
      'spread / total': 0,
      'decimal odds': 1.5128,
      'american odds': -195,
      'event': 'Seattle Seahawks@Philadelphia Eagles',
      'market': '1st Half - Draw No Bet',
      'result': 'W',
      'profit': 51.28,
      'participant score': 23,
      'sportsbook': 'Pinnacle',
      'participant': 'SEA'}]
```

You can see that Seahawks won the 1st half by a score of 23-17, netting a profit of \$51.28 on a \$100 bet on Seahawks 1st half ML if you were to bet Pinnacle's closing line.

### Opening lines for teams over date range

```python
ncaab = NCAAB()
sb = Sportsbook()

start = datetime.strptime('2020-11-25', '%Y-%m-%d')
end = datetime.strptime('2020-12-03', '%Y-%m-%d')
```

For NCAA basketball all the teams have been added to the config class, so here you can use the `team_ids` method.

```python
gonzaga = ncaab.team_id("GONZ")
baylor = ncaab.team_id("baylor")
```

`EventsByParticipants` includes any games that Gonzaga or Baylor played in over the given date range.

```python
e = EventsByParticipants([gonzaga, baylor], start, end, ncaab.league_id)
```

Use the `OpeningLines` query to get the opening lines on Bovada for all the matching games:

```python
ol = OpeningLines(e.ids(), ncaab.market_id('ps'), sb.id('Bovada'))
```

```python
ol.list(e)[1]
```

```python
    {'market id': 401,
     'event id': 4285569,
     'sportsbook id': 9,
     'datetime': '2020-11-23T17:55:49-08:00',
     'participant id': 651,
     'spread / total': -4,
     'decimal odds': 1.9091,
     'american odds': -110,
     'event': 'Gonzaga Bulldogs@Kansas Jayhawks',
     'market': 'Point Spread (Including OT)',
     'result': 'W',
     'profit': 90.91,
     'participant score': 102,
     'sportsbook': 'Bovada',
     'participant': 'GONZ'}
```

```python
ol.list(e)[5]
```

```python
    {'market id': 401,
     'event id': 4286230,
     'sportsbook id': 9,
     'datetime': '2020-12-01T15:10:19-08:00',
     'participant id': 687,
     'spread / total': -5.5,
     'decimal odds': 1.9091,
     'american odds': -110,
     'event': 'Illinois Fighting Illini@Baylor Bears',
     'market': 'Point Spread (Including OT)',
     'result': 'W',
     'profit': 90.91,
     'participant score': 82,
     'sportsbook': 'Bovada',
     'participant': 'BAY'}
```

Gonzaga opened as a 4 point favorite against Kansas, and Baylor opened as a 5.5 point favorite against Illinois.

### Search for event and get line history

```python
ufc = UFC()
sb = Sportsbook()
```

For some leagues there is no configuration class, or it doesn't have teams or participants. In this case `SearchEvents` comes in handy. You can search for an upcoming event by participant like so:

```python
s = SearchEvents('vettori')
```

```python
s.list()[0]
```

```python
    {'description': 'Jack Hermansson@Marvin Vettori',
     'datetime': '2020-12-05T20:59:00-08:00',
     'league': 'UFC',
     'sport': 'fighting',
     'sport id': 9,
     'event id': 4293126,
     'participants': [{'psid': 66013,
       'rot': 24149,
       'event id': 4293126,
       'participant id': 66013,
       'is home': False,
       'source': {'team id': 66013,
        'league id': 26,
        'name': 'Jack Hermansson',
        'nickname': None,
        'short name': None,
        'abbreviation': None},
       'name': 'Jack Hermansson'},
      {'psid': 66261,
       'rot': 24150,
       'event id': 4293126,
       'participant id': 66261,
       'is home': True,
       'source': {'team id': 66261,
        'league id': 26,
        'name': 'Marvin Vettori',
        'nickname': None,
        'short name': None,
        'abbreviation': None},
       'name': 'Marvin Vettori'}],
     'league id': 26}
```

You can get the complete line movement history for an event for a given market and sportsbook. Here you can see the line moving in Vettori's favor.

```python
vettori = s.list()[0]['participants'][1]['participant id']

lh = LineHistory(s.id(), ufc.default_market_id, sb.id('Pinnacle'), vettori)

lh.list(s)[0]
```

```python
    {'market id': 126,
     'event id': 4293126,
     'sportsbook id': 20,
     'datetime': '2020-12-05T20:27:03-08:00',
     'participant id': 66261,
     'spread / total': 0,
     'decimal odds': 1.6944,
     'american odds': -144,
     'event': 'Jack Hermansson@Marvin Vettori',
     'market': '2way',
     'sportsbook': 'Pinnacle',
     'participant': 'Marvin Vettori'}
```

```python
lh.list(s)[1]
```

```python
    {'market id': 126,
     'event id': 4293126,
     'sportsbook id': 20,
     'datetime': '2020-12-05T20:20:20-08:00',
     'participant id': 66261,
     'spread / total': 0,
     'decimal odds': 1.7092,
     'american odds': -141,
     'event': 'Jack Hermansson@Marvin Vettori',
     'market': '2way',
     'sportsbook': 'Pinnacle',
     'participant': 'Marvin Vettori'}
```

### Getting odds on Wimbledon futures

```python
sb = Sportsbook()
atp = ATP()
```

Sometimes it may not be obvious how to find a given market id. In this case you can call `sport_config` on a league configuration class and search for the market you are looking for. See the documentation for other config methods.

```python
print(atp.sport_config())
```

```python
    {'default market id': 126, 'consensus market ids': [126, 395, 396], 'markets': [{'periods': 0, 'alias': '', 'market types': [{'alias': 'Money Lines', 'market id': 126, 'name': '2way', 'url': 'money-line'}, {'alias': 'Point Spreads', 'market id': 395, 'name': 'Point Spread', 'url': 'pointspread'}, {'alias': 'Total Games', 'market id': 396, 'name': 'American Total', 'url': 'totals'}], 'market group id': 217, 'name': 'Full Game', 'url': 'full-game'}, {'alias': 'Futures', 'market types': [{'alias': 'French Open Winner', 'market id': 719, 'name': 'French Open Winner', 'url': 'french-open-winner'}, {'alias': 'Wimbledon Winner', 'market id': 720, 'name': 'Wimbledon Winner', 'url': 'davis-cup-winner'}, {'alias': 'US Open Winner', 'market id': 721, 'name': 'US Open Winner', 'url': 'us-open-winner'}, {'alias': 'Australian Open Winner', 'market id': 723, 'name': 'Australian Open Winner', 'url': 'australian-open-winner'}], 'market group id': 224, 'name': 'Futures', 'url': 'futures'}], 'sport id': 8}
```

```python
wimbledon_futures_id = 720

start = datetime.strptime('2021-06-28', '%Y-%m-%d')
end = datetime.strptime('2021-07-12', '%Y-%m-%d')
```

You can use `EventsByDateRange` to find Wimbledon's event id.

```python
e = EventsByDateRange(atp.league_id, start, end)

wimbledon_eid = e.list()[0]['event id']
```

With Wimbledon's event id and the futures market id, you can get the current odds on Bet365 for each competitor to win Wimbledon.

```python
cl = CurrentLines(wimbledon_eid, wimbledon_futures_id, sb.id('bet365'))

[o for o in cl.list(e) if o['participant'] in ['Dimitrov', 'Djokovic', 'Nadal']]
```

```python
    [{'market id': 720,
      'event id': 4138561,
      'sportsbook id': 5,
      'datetime': '2020-04-04T10:46:32-07:00',
      'participant id': 5371,
      'spread / total': 0,
      'decimal odds': 67,
      'american odds': 6600,
      'event': '2021 Wimbledon Winner ATP',
      'market': 'Wimbledon Winner',
      'sportsbook': 'Bet365',
      'participant': 'Dimitrov'},
     {'market id': 720,
      'event id': 4138561,
      'sportsbook id': 5,
      'datetime': '2020-04-04T10:46:32-07:00',
      'participant id': 5373,
      'spread / total': 0,
      'decimal odds': 2.5,
      'american odds': 150,
      'event': '2021 Wimbledon Winner ATP',
      'market': 'Wimbledon Winner',
      'sportsbook': 'Bet365',
      'participant': 'Djokovic'},
     {'market id': 720,
      'event id': 4138561,
      'sportsbook id': 5,
      'datetime': '2020-04-04T10:46:32-07:00',
      'participant id': 5684,
      'spread / total': 0,
      'decimal odds': 8,
      'american odds': 700,
      'event': '2021 Wimbledon Winner ATP',
      'market': 'Wimbledon Winner',
      'sportsbook': 'Bet365',
      'participant': 'Nadal'}]
```

## Development setup

Use Pipenv. Clone this repo, and then run `pipenv install --dev --pre black` to create a virtual environment with dev dependencies installed.

To run the test suite:

```sh
pipenv run pytest --cov=pysbr tests/
```

Inside `conftest.py` there are 3 global variables, `QUERY_SERVER`, `WAIT_MEAN` and `WAIT_DEVIATION` that you can change to actually query the SBR server when testing, otherwise the test suite will **not** query the server, it will use the saved cassettes.

## Release History

- 0.3.2
  - FIX: Add fake-useragent to install-requires
- 0.3.1
  - FIX: HTTP error 463
- 0.3.0
  - ADD: 'participant full name' and 'sportsbook alias' keys on lines lists / dataframes
  - ADD: New league config classes
- 0.2.1
  - CHANGE: Update README
- 0.2.0
  - FIX: LineHistory bug
  - ADD: id methods for Query and Config classes
- 0.1.3
  - CHANGE: Update docs
- 0.1.0
  - Initial release

## Meta

Jeremy Morrison – [jeremymorrison.ca](https://jeremymorrison.ca) - contact@jeremymorrison.ca

Distributed under the MIT license. See `LICENSE` for more information.

[github.com/JeMorriso/PySBR](https://github.com/JeMorriso/PySBR)

## Contributing

1. Fork it (<https://github.com/JeMorriso/PySBR/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->

[python-image]: https://img.shields.io/pypi/pyversions/python-sbr
[python-url]: https://www.python.org/downloads/release/python-390/
[circleci-image]: https://img.shields.io/circleci/build/github/JeMorriso/PySBR?token=9edfd6cf500869db3c74fc7691b80a0701b38b64
[circleci-url]: https://app.circleci.com/pipelines/github/JeMorriso
[readthedocs]: https://pysbr.readthedocs.io/
[discord]: https://discord.com/invite/X2RvzHeBWf
