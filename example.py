#!/usr/bin/python3

# typedload
# Copyright (C) 2018 Salvo "LtWorf" Tomaselli
#
# typedload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

#This is a basic example on how to use the typedload library.

#Json data is downloaded from the internet and then loaded into
#Python data structures (dictionaries, lists, strings, and so on).

#This example queries Yahoo weather and prints the forecast.

import json
import sys
from typing import Any, Dict, List, NamedTuple, Optional
import urllib.request

import typedload


def get_url(city: Optional[str]) -> str:
    """
    Get the URL for the Yahoo weather API for a
    given city
    """
    if not city:
        city = 'Catania'
    return "https://query.yahooapis.com/v1/public/yql?q=sele" \
        "ct%20*%20from%20weather.forecast%20where%20w" \
        "oeid%20in%20(select%20woeid%20from%20geo.pla" \
        "ces(1)%20where%20text%3D%22" + city + "%22)%" \
        "20and%20u%3D'c'&format=json&env=store%3A%2F%" \
        "2Fdatatables.org%2Falltableswithkeys"


def get_data(city: Optional[str]) -> Dict[str, Any]:
    """
    Use the Yahoo weather API to get weather information
    """
    req = urllib.request.Request(get_url(city))
    with urllib.request.urlopen(req) as f:
        r = f.read()
    answer = r.decode('ascii')
    data = json.loads(answer)
    r = data['query']['results']['channel']  # Remove some useless nesting
    return r


class Units(NamedTuple):
    distance: str
    pressure: str
    speed: str
    temperature: str


class Astronomy(NamedTuple):
    sunrise: str
    sunset: str


class Atmosphere(NamedTuple):
    humidity: int
    pressure: float
    rising: int
    visibility: float

class Forecast(NamedTuple):
    date: str
    day: str
    high: int
    low: int
    text: str


class Condition(NamedTuple):
    date: str
    temp: int
    text: str


class Item(NamedTuple):
    forecast: List[Forecast]
    condition: Condition
    title: str


class Weather(NamedTuple):
    item: Item
    units: Units
    astronomy: Astronomy
    atmosphere: Atmosphere


def main():
    raw_data = get_data(sys.argv[1] if len(sys.argv) == 2 else None)
    weather = typedload.load(raw_data, Weather)
    print(weather.item.title)
    print()
    print('Sunrise %s\t Sunset %s' % (weather.astronomy.sunrise, weather.astronomy.sunset))
    print()
    print('%s %s%s' % (weather.item.condition.text, weather.item.condition.temp, weather.units.temperature))
    print()
    print('Humidity: %s%%' % (weather.atmosphere.humidity, ))
    print('Pressure: %s%s' % (weather.atmosphere.pressure, weather.units.pressure))
    print('Visibility: %s%s' % (weather.atmosphere.humidity, weather.units.distance))
    print()
    print('Forecast')
    for i in weather.item.forecast:
        print('%s\tMin: %s%s\tMax: %s%s\t%s' % (i.day, i.low, weather.units.temperature, i.high, weather.units.temperature, i.text))


if __name__ == '__main__':
    main()
