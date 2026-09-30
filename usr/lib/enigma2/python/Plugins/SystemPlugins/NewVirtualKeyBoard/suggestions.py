#!/usr/bin/python
# -*- coding: utf-8 -*-

# Search suggestions (Google, YouTube, Bing, DuckDuckGo, IMDb) and the
# search history of the keyboard.

import json
import os
import re

from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import PY3, setting, urlread

if PY3:
    from urllib.parse import quote
else:
    from urllib import quote

# (config value, name shown in the suggestions header)
SUGGESTION_PROVIDERS = [('google', 'Google'), ('youtube', 'YouTube'), ('bing', 'Bing'), ('duckduckgo', 'DuckDuckGo'), ('imdb', 'IMDb')]

HISTORY_FILE = '/etc/history'


def getSuggestionsUrl(provider, text, locale):
    # locale like 'de_DE', 'de-DE' or 'sr_Cyrl-CS'
    parts = re.split('[_-]', locale)
    lang = parts[0] or 'en'
    country = parts[-1] if len(parts) > 1 else lang.upper()
    query = quote(text)
    if provider == 'bing':
        return 'https://api.bing.com/osjson.aspx?query=%s&mkt=%s-%s' % (query, lang, country)
    if provider == 'duckduckgo':
        return 'https://duckduckgo.com/ac/?q=%s' % query
    if provider == 'imdb':
        # the first path part is the query's first letter (any other letter
        # works too, 'x' is used for non-ASCII)
        first = text[:1].lower()
        if not first or first not in 'abcdefghijklmnopqrstuvwxyz0123456789':
            first = 'x'
        return 'https://v3.sg.media-imdb.com/suggestion/%s/%s.json' % (first, quote(text.lower()))
    # ie/oe=utf-8: else Google answers some languages (ar, ru, el, tr, fa, ...)
    # in a legacy Windows code page
    return 'https://suggestqueries.google.com/complete/search?output=firefox&ie=utf-8&oe=utf-8&hl=%s&gl=%s%s&q=%s' % (lang, country.lower(), '&ds=yt' if provider == 'youtube' else '', query)


def parseSuggestions(provider, raw, contentType=''):
    # list of suggestions (native str) from a provider's JSON answer
    charset = 'utf-8'
    if 'charset=' in contentType:
        charset = contentType.split('charset=', 1)[1].split(';')[0].strip() or 'utf-8'
    try:
        text = raw.decode(charset, 'replace')
    except LookupError:
        text = raw.decode('utf-8', 'replace')
    data = json.loads(text)
    if provider == 'duckduckgo':
        items = [item.get('phrase') for item in data if isinstance(item, dict)]
    elif provider == 'imdb':
        # titles only (ids tt...), no people
        items = [item.get('l') for item in data.get('d', []) if isinstance(item, dict) and str(item.get('id', '')).startswith('tt')]
    else:
        # Google/YouTube/Bing: [query, [suggestions, ...], ...]
        items = data[1]
    suggestions = []
    for item in items:
        if not item:
            continue
        if not PY3 and not isinstance(item, str):
            item = item.encode('utf-8')
        suggestions.append(item)
    return suggestions


def fetchSuggestions(provider, text, locale):
    # runs in a worker thread (threads.deferToThread), never in the GUI thread
    raw, contentType = urlread(getSuggestionsUrl(provider, text, locale), 5)
    return parseSuggestions(provider, raw, contentType)


class SuggestionsFetcher(object):
    # Mixin: fetches suggestions in a worker thread, one request at a time.
    # Text typed while a request runs is fetched next; answers that are no
    # longer wanted (text cleared, provider changed, screen closed) are
    # dropped: each cancel bumps the generation, an answer of an older one is
    # ignored.

    def __init__(self, callback):
        self.suggestionsCallback = callback
        self.suggestionsProvider = setting('suggestionsprovider', 'google')
        self.suggestionsBusy = False
        self.suggestionsPending = None      # (text, locale) waiting for a free slot
        self.suggestionsGeneration = 0      # bumped to invalidate running requests
        self.suggestionsRequestGeneration = 0

    def suggestionsProviderName(self):
        return dict(SUGGESTION_PROVIDERS).get(self.suggestionsProvider, 'Google')

    def setSuggestionsProvider(self, provider):
        if provider != self.suggestionsProvider:
            self.suggestionsProvider = provider
            self.cancelSuggestions()

    def requestSuggestions(self, text, locale):
        self.suggestionsPending = (text, locale)
        if not self.suggestionsBusy:
            self._startSuggestionsRequest()

    def cancelSuggestions(self):
        # an answer still on its way is not shown any more (also used when
        # the screen closes)
        self.suggestionsGeneration += 1
        self.suggestionsPending = None

    def _startSuggestionsRequest(self):
        from twisted.internet import threads
        text, locale = self.suggestionsPending
        self.suggestionsPending = None
        self.suggestionsBusy = True
        self.suggestionsRequestGeneration = self.suggestionsGeneration
        d = threads.deferToThread(fetchSuggestions, self.suggestionsProvider, text, locale)
        d.addCallbacks(self._suggestionsDone, self._suggestionsFailed)

    def _suggestionsDone(self, suggestions):
        self.suggestionsBusy = False
        if self.suggestionsPending:
            self._startSuggestionsRequest()
            return
        if self.suggestionsRequestGeneration == self.suggestionsGeneration:
            self.suggestionsCallback(suggestions)

    def _suggestionsFailed(self, failure):
        print('[NewVirtualKeyBoard] unable to get suggestions: %s' % failure.getErrorMessage())
        self._suggestionsDone([])


def historyLimit():
    try:
        return max(1, int(setting('historysize', 100)))
    except (TypeError, ValueError):
        return 100


class SearchHistory(object):
    # /etc/history, newest entry first; read again only when the file changed
    # (not on every keystroke)

    def __init__(self, path=None):
        self.path = path or HISTORY_FILE
        self._cache = (None, [])

    def entries(self):
        try:
            mtime = os.path.getmtime(self.path)
        except OSError:
            return []
        if self._cache[0] != mtime:
            try:
                with open(self.path, 'rb') as f:
                    raw = f.read()
            except (IOError, OSError):
                return []
            lines = [line.strip() for line in raw.splitlines()]
            if PY3:
                lines = [line.decode('utf-8', 'replace') for line in lines]
            self._cache = (mtime, [line for line in lines if line])
        return self._cache[1][:historyLimit()]

    def sortedFor(self, word):
        # entries starting with the typed text first, the others in their order
        entries = self.entries()
        word = (word or '').lower().strip()
        if not word:
            return entries
        matches, others = [], []
        for entry in entries:
            (matches if entry.lower().startswith(word) else others).append(entry)
        return matches + others

    def add(self, text):
        text = (text or '').strip()
        if not text:
            return
        entries = [text] + [entry for entry in self.entries() if entry != text]
        del entries[historyLimit():]
        try:
            data = '\n'.join(entries) + '\n'
            with open(self.path, 'wb') as f:
                f.write(data.encode('utf-8') if PY3 else data)
        except (IOError, OSError) as e:
            print('[NewVirtualKeyBoard] writing the search history failed: %s' % e)
        self._cache = (None, [])

    def clear(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        self._cache = (None, [])
