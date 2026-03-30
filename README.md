# TripMind

**A transparent itinerary optimizer over a small supplied travel catalog.**

TripMind chooses one flight, one hotel and a compatible set of activities under a fixed integer budget. It exposes each cost component and the exact constraints behind its result. The demonstration uses fictional places, prices and preference scores.

## Run

Python 3.9+ · standard library only.

```sh
python3 main.py
python3 main.py --input example.json
python3 main.py --help
python3 -m unittest discover -s . -p 'test_main.py' -v
```

The default fixture is resolved beside the script, so the default demo works from any working directory. Explicit `--input` paths are relative to the caller.

## The model

- Money uses integer cents; hotel `cost_cents` is a nightly amount and is multiplied by `nights`.
- Only options at the requested destination are eligible.
- At most one activity can occupy each trip day.
- Every requested activity category must be represented.
- The objective maximizes the sum of the supplied flight, hotel and activity preference scores. Ties prefer lower total cost, then stable option IDs.

The default catalog produces score **20**, total **43,500 cents**, and **6,500 cents remaining**: `flight-flex`, `stay-view`, `museum` and `coastal-walk`. These are synthetic fixture results, not provider prices or measured travel quality.

The solver exhaustively checks its finite catalog. Limits of 20 flights, 20 hotels, 12 activities and 500,000 candidate combinations make the computation explicit and bounded. An infeasible request returns `feasible: false` with no invented itinerary.

## Tests and limits

Eight tests cover the optimal fixture result, insufficient budget, required categories, daily conflicts, destination filtering, stable tie-breaking and invalid inputs. The solver's optimality applies only to the supplied options and scoring model.

This reference has no dates, time zones, visa rules, transfer times, live availability, booking, LLM, MCP or provider integration. Scores are caller-defined preferences, not probabilities or objective quality measures. Add those constraints before using a similar model for an actual itinerary.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
