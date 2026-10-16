"""Public-only GitHub metrics. Standard library; GITHUB_TOKEN is optional.

Queries public commit/issue search, never private repositories or local gh auth.
Counts are not equivalent to GitHub's contribution-calendar total.
"""
import calendar
from datetime import datetime, timezone, date
from html import escape
import json
import os
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'profile'
USER = 'ElRaxy'
TODAY = datetime.now(timezone.utc).date()
TOKEN = os.environ.get('GITHUB_TOKEN', '')
SOURCES = []


def count(kind, query):
    url = f'https://api.github.com/search/{kind}?' + urlencode({'q': query, 'per_page': 1})
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'ElRaxy-profile-metrics', 'X-GitHub-Api-Version': '2022-11-28'}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    with urlopen(Request(url, headers=headers), timeout=30) as response:
        result = json.load(response)
    if result.get('incomplete_results') or type(result.get('total_count')) is not int:
        raise RuntimeError('GitHub returned incomplete search data; previous metrics kept')
    SOURCES.append(url)
    # Anonymous search allows fewer calls per minute. No local credentials used.
    time.sleep(2.1 if TOKEN else 6.1)
    return result['total_count']


def render(data, dark, mobile=False):
    fg, muted, blue, line, tile = ('#e6edf3', '#a4b0be', '#879aff', '#30363d', '#161b22') if dark else ('#1f2328', '#59636e', '#2448ff', '#d1d9e0', '#f6f8fa')
    def text(x, y, value, size=14, color=fg, weight='400', anchor='start'):
        return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'
    body = [text(24, 32, 'Public work, in numbers', 21, blue, '600'), text(24, 55, f"{data['from']} to {data['to']} · UTC", 12, muted)]
    for index, (value, label) in enumerate([(data['commits'], 'Commits authored'), (data['pull_requests'], 'PRs authored'), (data['issues'], 'Issues created')]):
        if mobile:
            y = 76 + index * 66
            body += [f'<rect x="24" y="{y}" width="312" height="56" rx="7" fill="{tile}" stroke="{line}"/>', text(36, y + 37, value, 27, fg, '600'), text(118, y + 34, label, 15, muted)]
        else:
            x = 24 + index * 152
            body += [f'<rect x="{x}" y="76" width="140" height="86" rx="7" fill="{tile}" stroke="{line}"/>', text(x + 12, 115, value, 30, fg, '600'), text(x + 12, 143, label, 12, muted)]
    offset = 98 if mobile else 0
    body += [text(24, 194 + offset, 'Commits authored by month', 14, fg, '600')]
    maximum = max(1, *(item['count'] for item in data['months']))
    for index, item in enumerate(data['months']):
        x = 25 + index * (26 if mobile else 38)
        height = round(78 * item['count'] / maximum, 1)
        body += [f'<rect x="{x}" y="{294 + offset - height}" width="{18 if mobile else 24}" height="{height}" rx="3" fill="{blue}"/>', text(x + 9, 282 + offset - height, item['count'], 12 if mobile else 11, muted, anchor='middle'), text(x + 9, 316 + offset, item['month'], 12 if mobile else 11, muted, anchor='middle')]
    if mobile:
        body += [text(24, 450, 'Public repositories · default-branch commits', 12, muted), text(24, 470, f"GitHub Search API · updated {data['to']}", 12, muted)]
    else:
        body += [text(24, 348, 'Public repositories only · default-branch commits', 11, muted), text(24, 367, f"GitHub Search API · updated {data['to']}", 11, muted)]
    size = '360 490' if mobile else '504 388'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size}" role="img" aria-labelledby="title desc"><title id="title">Public contribution metrics for Alex Micó</title><desc id="desc">' + escape(f"{data['from']} to {data['to']}: {data['commits']} public commits authored, {data['pull_requests']} pull requests authored and {data['issues']} issues created. GitHub Search indexes commits on default branches. This is not the contribution-calendar total.") + '</desc><g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">' + ''.join(body) + '</g></svg>\n'


def main():
    start = date(TODAY.year, 1, 1)
    months = []
    for month in range(1, TODAY.month + 1):
        first = date(TODAY.year, month, 1)
        last = min(TODAY, date(TODAY.year, month, calendar.monthrange(TODAY.year, month)[1]))
        total = count('commits', f'author:{USER} is:public author-date:{first}..{last}')
        months.append({'month': calendar.month_abbr[month], 'count': total, 'from': str(first), 'to': str(last)})
    prs = count('issues', f'author:{USER} type:pr is:public created:{start}..{TODAY}')
    issues = count('issues', f'author:{USER} type:issue is:public created:{start}..{TODAY}')
    data = {'user': USER, 'from': str(start), 'to': str(TODAY), 'commits': sum(item['count'] for item in months), 'pull_requests': prs, 'issues': issues, 'months': months, 'sources': SOURCES}
    # Write only after all requests succeeded, never replace metrics with zero placeholders.
    for dark in (False, True):
        for mobile in (False, True):
            (ROOT / f'metrics-{"dark" if dark else "light"}{"-mobile" if mobile else ""}.svg').write_text(render(data, dark, mobile), encoding='utf-8')
    (ROOT / 'metrics-public.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(f"Generated public metrics through {TODAY}; {len(SOURCES)} complete queries")


if __name__ == '__main__':
    main()
