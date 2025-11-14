"""Analytics helper functions.

Currently provides small pure-Python aggregations so routes can stay thin.
If growth warrants, move to dedicated reporting layer or materialized views.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date, datetime, UTC, timedelta
from typing import Iterable, Dict, List


def count_registrations_by_day(users: Iterable) -> List[Dict]:
    """Aggregate user objects (with join_date) into counts per day.

    Returns sorted list of dicts: {'date': 'YYYY-MM-DD', 'count': N}.
    Ignores users missing join_date.
    """
    counts: Dict[date, int] = defaultdict(int)
    for u in users:
        if getattr(u, 'join_date', None):
            d = u.join_date.date()
            counts[d] += 1
    return [
        {'date': d.isoformat(), 'count': counts[d]}
        for d in sorted(counts.keys())
    ]


def registration_trend(users: Iterable, days: int = 14) -> List[Dict]:
    """Return a contiguous day-by-day series for the last `days` days.

    Includes days with zero registrations so charts render evenly.
    Output sorted ascending by date: [{'date': 'YYYY-MM-DD', 'count': N}, ...]
    """
    if days < 1:
        days = 1
    end_date = datetime.now(UTC).date()
    start_date = end_date - timedelta(days=days - 1)
    # Pre-aggregate counts for provided users
    agg: Dict[date, int] = defaultdict(int)
    for u in users:
        jd = getattr(u, 'join_date', None)
        if jd:
            d = jd.date()
            if start_date <= d <= end_date:
                agg[d] += 1
    series: List[Dict] = []
    cur = start_date
    while cur <= end_date:
        series.append({'date': cur.isoformat(), 'count': agg.get(cur, 0)})
        cur += timedelta(days=1)
    return series


def top_n(items: Iterable[Dict], key: str, n: int = 10, reverse: bool = True) -> List[Dict]:
    """Return top n dicts by given numeric key; safe if key missing.
    Example: top_n(product_rows, 'revenue', 5)
    """
    safe_items = [i for i in items if isinstance(i.get(key), (int, float))]
    return sorted(safe_items, key=lambda x: x.get(key, 0), reverse=reverse)[:n]
