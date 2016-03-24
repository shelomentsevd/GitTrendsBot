# Author: Dmitriy Shelomentsev (shelomentsev@protonmail.ch)
# -*- coding: utf-8 -*-
from lxml import html
import requests

githubtrends = 'https://github.com/trending'
periods = ['daily', 'weekly', 'monthly']
repo_css = '.repo-list-item'
repo_name_css = '.repo-list-name'
repo_description_css = '.repo-list-description'
meta_css = 'p.repo-list-meta'
languages_css = '.select-menu-item-text.js-select-button-text.js-navigation-open'
languages = []

class GitTrendsError(Exception):

    def __init__(self, message):
        super(GitTrendsError, self).__init__()
        self.message = message

    def __str__(self):
        return '%s' % (self.message)

if not languages:
    import os
    path = os.path.dirname(os.path.realpath(__file__)) + '/languages'
    file = open(path, 'r')
    with file: 
        languages = [language.strip() for language in file]
    file.close()
    if not language:
        raise GitTrendsError('Failed to load languages list')

def select(item, css):
    return item.cssselect(css)

def get_meta(item):
    meta = select(item, meta_css)
    if meta:
        metas = meta[0].text_content().split(u'\u2022')
        if len(metas) == 2:
            stars, _ = metas
            return ['unknow', stars.strip()]
        elif len(metas) == 3:
            language, stars, _ = metas
            return [language.strip(), stars.strip()]

    return []

def get_name(item):
    name = select(item, repo_name_css)
    if name:
        text = name[0].text_content()
        return ''.join(text.split()) # TODO: Refactoring!
    return False

def get_description(item):
    description = select(item, repo_description_css)
    if description:
        text = description[0].text_content()
        return text.strip()
    return ''

def get_langs(tree):
    languages = select(tree, languages_css)
    return [item.text_content().lower() for item in languages]


def get_trends(period='daily', language=''):
    if period not in periods:
        raise GitTrendsError('Wrong period name: %s' % period)
    if language and language.lower() not in languages:
        raise GitTrendsError('Wrong language name: %s ' % language)
    url = githubtrends + '/' + language + '?since=' + period
    page = requests.get(url)
    tree = html.fromstring(page.content)
    repolist = tree.cssselect(repo_css)
    result = list()
    for repo in repolist:
        name = get_name(repo)
        description = get_description(repo)
        language, stars = get_meta(repo)
        result.append({
                       'name': name,
                       'description': description,
                       'language': language,
                       'stars': stars
                      })

    return result