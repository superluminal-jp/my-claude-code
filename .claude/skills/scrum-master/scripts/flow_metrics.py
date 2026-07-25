#!/usr/bin/env python3
"""Compute Cycle Time, Throughput, and WIP from a CSV of ticket start/completion dates.

Grounded in The Kanban Guide for Scrum Teams (Scrum.org / Vacanti / Yeret, 2021):
WIP, Cycle Time, Work Item Age, and Throughput are the four base flow metrics,
and a Service Level Expectation (SLE) is a probability + timeframe forecast
built from the observed Cycle Time distribution (e.g. "85% of items finish
within N days"). This script never invents numbers: every figure comes from
the rows in the input CSV.

Usage:
    python3 flow_metrics.py tickets.csv

Input CSV columns (header required): item_id,started_at,completed_at
Dates are ISO 8601 (e.g. 2026-07-01). Leave completed_at empty for items
still in progress -- they count toward WIP but not Cycle Time or Throughput.
"""
import argparse
import csv
import statistics
import sys
from datetime import date, datetime, timedelta

# The Kanban Guide's own worked examples use the 85th percentile as the
# default Service Level Expectation -- it balances a useful forecast against
# being skewed by a handful of outliers. [KGS21, p.6]
SLE_PERCENTILE = 85


def parse_date(value: str) -> date:
    return datetime.fromisoformat(value.strip()).date()


def load_items(path: str):
    """Read the CSV, skipping and warning on rows that can't be used rather than aborting."""
    items = []
    try:
        f = open(path, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with f:
        reader = csv.DictReader(f)
        missing = {"item_id", "started_at"} - set(reader.fieldnames or [])
        if missing:
            print(f"error: CSV is missing required column(s): {', '.join(sorted(missing))}", file=sys.stderr)
            sys.exit(1)

        for i, row in enumerate(reader, start=2):  # header is row 1
            item_id = (row.get("item_id") or "").strip()
            if not item_id:
                print(f"warning: row {i}: missing item_id, skipped", file=sys.stderr)
                continue
            try:
                started = parse_date(row["started_at"])
            except (ValueError, KeyError):
                print(f"warning: row {i} ({item_id}): unparseable started_at, skipped", file=sys.stderr)
                continue

            completed_raw = (row.get("completed_at") or "").strip()
            completed = None
            if completed_raw:
                try:
                    completed = parse_date(completed_raw)
                except ValueError:
                    print(f"warning: row {i} ({item_id}): unparseable completed_at, treated as in-progress", file=sys.stderr)
                if completed is not None and completed < started:
                    print(f"warning: row {i} ({item_id}): completed_at before started_at, skipped", file=sys.stderr)
                    continue

            items.append({"item_id": item_id, "started": started, "completed": completed})
    return items


def percentile(values, pct):
    """Nearest-rank percentile -- no interpolation, so the result is always an observed value."""
    ordered = sorted(values)
    if not ordered:
        return None
    rank = max(1, round(pct / 100 * len(ordered)))
    return ordered[min(rank, len(ordered)) - 1]


def iso_week_label(d: date) -> str:
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def week_end(d: date) -> date:
    # ISO weeks run Monday-Sunday; return the Sunday for the week containing d.
    return d + timedelta(days=6 - d.weekday())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_path", help="CSV file with item_id,started_at,completed_at")
    args = parser.parse_args()

    items = load_items(args.csv_path)
    if not items:
        print("No usable rows found.", file=sys.stderr)
        sys.exit(1)

    completed_items = [i for i in items if i["completed"] is not None]
    open_items = [i for i in items if i["completed"] is None]
    cycle_times = [(i["completed"] - i["started"]).days for i in completed_items]

    print(f"# Flow metrics — {args.csv_path}\n")
    print(f"- Items read: {len(items)}")
    print(f"- Completed: {len(completed_items)}")
    print(f"- In progress (WIP as of latest data): {len(open_items)}\n")

    if cycle_times:
        p85 = percentile(cycle_times, SLE_PERCENTILE)
        print("## Cycle Time (days)\n")
        print("| min | median | p85 (SLE) | max |")
        print("|---|---|---|---|")
        print(f"| {min(cycle_times)} | {statistics.median(cycle_times)} | {p85} | {max(cycle_times)} |")
        print(f"\nSLE: {SLE_PERCENTILE}% of completed items finished within {p85} day(s), based on {len(cycle_times)} observations. [KGS21, p.6]\n")
    else:
        print("## Cycle Time\n\nNo completed items to measure.\n")

    if completed_items:
        by_week = {}
        for i in completed_items:
            by_week.setdefault(iso_week_label(i["completed"]), 0)
            by_week[iso_week_label(i["completed"])] += 1
        print("## Throughput (completed items per ISO week)\n")
        print("| Week | Completed |")
        print("|---|---|")
        for week in sorted(by_week):
            print(f"| {week} | {by_week[week]} |")
        print()

    all_dates = [i["started"] for i in items] + [i["completed"] for i in items if i["completed"]]
    if all_dates:
        start_range = min(all_dates)
        end_range = max(all_dates + [date.today()])
        wip_by_week = {}
        cursor = start_range
        while cursor <= end_range:
            wk_end = week_end(cursor)
            label = iso_week_label(cursor)
            wip = sum(1 for i in items if i["started"] <= wk_end and (i["completed"] is None or i["completed"] > wk_end))
            wip_by_week[label] = wip
            cursor = wk_end + timedelta(days=1)
        print("## WIP (snapshot at end of each ISO week)\n")
        print("| Week | WIP |")
        print("|---|---|")
        for week in sorted(wip_by_week):
            print(f"| {week} | {wip_by_week[week]} |")


if __name__ == "__main__":
    main()
