#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011-2025 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
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

import json
import re
import sys
import urllib
import pywikibot
import pywikibot.pagegenerators as pagegenerators
from wikidatafun import *

def main():
	site = pywikibot.Site('wikiindex', 'wikiindex')
	cat = pywikibot.Category(site, 'Category:Wiktionary')
	gen = pagegenerators.CategorizedPageGenerator(cat, start="!")
	pre = pagegenerators.PreloadingGenerator(gen)

	for page in pre:
		if not page.exists() or page.isRedirectPage():
			continue
		if not page.namespace() == 0:
			continue
		print(page.title())
		
		m = re.findall(r"(?im)\|\s*URL\s*=\s*(https?://[^/ ]+?/)", page.text)
		urls = []
		if m:
			for mm in m:
				urls.append(mm.strip().lower())
				urls = list(set(urls))
		print(urls)
		if len(urls) != 1:
			continue
		if not re.search(r"(wiktionary)\.org", urls[0]):
			continue
		urlapi = urls[0] + "w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json"
		raw = getURL(url=urlapi)
		print(raw)
		json1 = json.loads(raw)
		articles = json1["query"]["statistics"]["articles"]
		if articles == 0:
			continue
		print(articles)
		newtext = page.text
		newtext = re.sub(r"(?im)(\{\{wktsize\|[a-z]+\|)\d+(\}\})\(As of: [^\(\)]+\)", r"\g<1>%s\g<2>(As of: {{subst:CURRENTDAY2}} {{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}})" % (articles), newtext)
		newtext = re.sub(r"(?im)(\{\{wktsize\|[a-z]+\|)\d+(\}\})", r"\g<1>%s\g<2>" % (articles), newtext)
		pywikibot.showDiff(page.text, newtext)
		page.text = newtext
		page.save("BOT - Updating size")

if __name__ == '__main__':
	main()
