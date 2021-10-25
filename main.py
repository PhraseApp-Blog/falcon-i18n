import falcon
import falcon.asgi
import json
import jinja2
import glob
from babel.plural import PluralRule
from babel.dates import format_date, format_time
from babel.numbers import format_decimal
import datetime


class ExampleResource:
    async def on_get(self, req, resp, locale):
        if(locale not in locales):
            locale = default_fallback

        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        print(req.prefix)
        template = env.get_template("index.html")
        resp.text = template.render(**locales[locale], locale=locale, attendee_value=100, date_value=datetime.date(2021, 12, 4), time_value=datetime.time(10, 30, 0))


app = falcon.asgi.App()
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

default_fallback = 'en'
locales = {}
plural_rule = PluralRule({'one': 'n in 0..1'})

language_list = glob.glob("locales/*.json")
for lang in language_list:
    filename = lang.split('\\')
    lang_code = filename[1].split('.')[0]

    with open(lang, 'r', encoding='utf8') as file:
        locales[lang_code] = json.load(file)


# custom filters for Jinja2
def plural_formatting(key_value, input, locale):
    key = ''
    for i in locales[locale]:
        if(key_value == locales[locale][i]):
            key = i
            break

    if not key:
        return key_value

    plural_key = f"{key}_plural"

    if(plural_rule(input) != 'one' and plural_key in locales[locale]):
        key = plural_key

    return locales[locale][key]


def number_formatting(input, locale):
    return format_decimal(input, locale=locale)


def date_formatting(input, locale):
    return format_date(input, format='full', locale=locale)


def time_formatting(input, locale):
    return format_time(input, locale=locale)


env.filters['plural_formatting'] = plural_formatting
env.filters['number_formatting'] = number_formatting
env.filters['date_formatting'] = date_formatting
env.filters['time_formatting'] = time_formatting

example = ExampleResource()

app.add_route('/{locale}/main', example)
