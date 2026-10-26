#!/usr/bin/env python3
"""Optimize a small synthetic travel itinerary under explicit budget and day constraints."""
import argparse
import itertools
import json
import math
from pathlib import Path


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(name + " must be an integer >= " + str(minimum))
    return value


def plan(request):
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    budget = integer(request.get("budget_cents"), "budget_cents", 1)
    nights = integer(request.get("nights"), "nights", 1)
    if nights > 14: raise ValueError("at most 14 nights")
    destination = request.get("destination")
    if not isinstance(destination, str) or not destination: raise ValueError("destination is required")
    required = request.get("required_categories", [])
    if not isinstance(required, list) or any(not isinstance(x, str) for x in required):
        raise ValueError("required_categories must contain strings")
    groups = []
    for key in ("flights", "hotels", "activities"):
        rows = request.get(key)
        if not isinstance(rows, list): raise ValueError(key + " must be a list")
        ids = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
                raise ValueError("every option needs an id")
            if row["id"] in ids: raise ValueError("duplicate " + key + " id")
            ids.add(row["id"])
            integer(row.get("cost_cents"), "cost_cents")
            integer(row.get("score"), "score")
            if not isinstance(row.get("destination"), str): raise ValueError("option destination is required")
            if key == "activities":
                day = integer(row.get("day"), "day", 1)
                if day > nights + 1: raise ValueError("activity day exceeds trip")
                if not isinstance(row.get("category"), str): raise ValueError("activity category is required")
        groups.append([row for row in rows if row["destination"] == destination])
    flights, hotels, activities = groups
    if len(activities) > 12 or len(flights) > 20 or len(hotels) > 20:
        raise ValueError("catalog exceeds bounded solver limits")
    activities_by_day = {}
    for activity in activities:
        activities_by_day.setdefault(activity["day"], []).append(activity)
    daily_options = [[None] + activities_by_day[day] for day in sorted(activities_by_day)]
    activity_combinations = math.prod(len(options) for options in daily_options)
    if len(flights) * len(hotels) * activity_combinations > 500000:
        raise ValueError("search exceeds 500000 candidate budget")
    best, best_key, examined = None, None, 0
    for flight, hotel in itertools.product(flights, hotels):
        base_cost = flight["cost_cents"] + nights * hotel["cost_cents"]
        if base_cost > budget: continue
        for daily_choice in itertools.product(*daily_options):
            examined += 1
            chosen = [activity for activity in daily_choice if activity is not None]
            if not set(required).issubset({a["category"] for a in chosen}): continue
            total = base_cost + sum(a["cost_cents"] for a in chosen)
            if total > budget: continue
            score = flight["score"] + hotel["score"] + sum(a["score"] for a in chosen)
            chosen.sort(key=lambda a: (a["day"], a["id"]))
            key = (-score, total, flight["id"], hotel["id"], tuple(a["id"] for a in chosen))
            if best_key is None or key < best_key:
                best_key = key
                best = {"flight": flight["id"], "hotel": hotel["id"], "activities": [a["id"] for a in chosen],
                        "score": score, "total_cents": total, "remaining_cents": budget - total,
                        "costs": {"flight": flight["cost_cents"], "hotel": nights * hotel["cost_cents"],
                                  "activities": total - base_cost}}
    return {"feasible": best is not None, "itinerary": best, "candidates_examined": examined,
            "reason": "optimal within supplied finite catalog" if best else "no catalog combination satisfies all constraints"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("example.json"))
    args = parser.parse_args()
    try: print(json.dumps(plan(json.loads(args.input.read_text())), indent=2))
    except (ValueError, OSError, TypeError, KeyError) as exc: parser.error(str(exc))


if __name__ == "__main__": main()
