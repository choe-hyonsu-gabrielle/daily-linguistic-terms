import re
import json
import random
import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'}


def load_terms():
    return json.load(open('data/terms.json', encoding='utf-8', mode='r'))


def scrap_contents(url):
    response = requests.get(url=url, headers=HEADER)
    if response.status_code == 200:
        _html = response.text
        parsed = parse_html(_html, url)
    return parsed


def parse_html(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find("h2", {"class": "page-title"}).text
    url = "<a href=" + url + ">" + url + "</a>"

    definition = str(soup.select_one("#block-system-main > div > div > div.col-sm-8 > div.field.field-name-field-glossary-definition.field-type-text-long.field-label-above > div.field-items > div"))
    discussion = str(soup.select_one("#block-system-main > div > div > div.col-sm-8 > div.field.field-name-field-glossary-discussion.field-type-text-long.field-label-above > div.field-items > div"))
    examples = str(soup.select_one("#block-system-main > div > div > div.col-sm-8 > div.group-examples.field-group-div > div > div.field-items > div"))
    see_also = str(soup.select_one("#block-system-main > div > div > div.col-sm-8 > div.field.field-name-field-glossary-see-also.field-type-entityreference.field-label-above > div.field-items > div"))
    see_also = re.sub(r'href="(/term/.*)"', r'href="https://glossary.sil.org\1"', see_also)
    reference = str(soup.select_one("#block-system-main > div > div > div.col-sm-8 > div.field.field-name-field-glossary-source-collection.field-type-field-collection.field-label-above > div.field-items"))
    reference = re.sub(r'href="(/bibliography/.*)"', r'href="https://glossary.sil.org\1"', reference)
    hierarchy = str(soup.select_one("#block-system-main > div > div > div.col-sm-4 > div > div > div > div"))
    hierarchy = re.sub(r'href="(/term/.*)"', r'href="https://glossary.sil.org\1"', hierarchy)

    return dict(title=title, url=url, definition=definition, discussion=discussion, examples=examples, see_also=see_also, reference=reference, hierarchy=hierarchy)


@app.route('/')
def landing():
    term, url = random.choice(list(terms.items()))
    print('loading', term, 'from', url)
    contents = scrap_contents(url)
    return render_template('linguists_landing.html', contents=contents)

if __name__ == '__main__':
    terms = load_terms()
    app.run(debug=False)