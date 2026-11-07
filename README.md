# Retirement Age Calculator

A custom-input deterministic calculator, not a bundled-scenario exercise. Money is integer cents in one currency. Rates are integer basis points (100 basis points = 1%). The host chat translates a description into typed input and asks for missing personal facts. The task itself runs one Python tool without an inner LLM loop. The model does not produce schedules.

## Tools

Task `project-retirement` directly runs `calculate_retirement`. Both share the same typed input and compact output in `contract.py`. Essential personal inputs have no defaults; ask for them. Nullable assumption keys are still required in machine input: pass `null` to use their documented defaults. Zero is an explicit value, not a request for a default. Effective assumptions and the names of defaulted fields are always returned.

```json
{
  "current_age": 40,
  "investments_cents": 25000000,
  "annual_income_cents": 10000000,
  "annual_expenses_cents": 5000000,
  "investment_return_bps": null,
  "wage_growth_bps": null,
  "spending_inflation_bps": null
}
```

## Financial rules

Required inputs: current age (integer 0–99), invested balance, annual take-home income, and annual expenses. Monetary inputs range from 0 to 10^15 cents. Starting age 100 or above produces a clear validation error, not an exception trace in normal MCP use. Missing essential values must be requested; gross income must not be treated as take-home income without clarification.

Defaults: nominal investment return 900 bps (9%), annual wage growth 200 bps (2%), spending inflation 200 bps (2%). Return and wage growth allow −10000 to 10000 bps; spending inflation allows 0 to 10000 bps. The maximum search age is fixed at 100 and the withdrawal rate is fixed at 400 bps (4%). Users can override the three nullable rates, not the 4% rule or age limit.

At the current age, check investments >= 25 × current annual expenses. If true, retirement is immediate. Otherwise, for each working year: apply the return to opening investments; add that year's take-home income minus expenses at year-end; grow income and expenses for the next year; then check the target on the next birthday. Every growth amount is rounded separately to cents, nearest with ties away from zero. New savings receive returns starting the next year. Spending inflation is separate from wage growth and investment returns are nominal, not inflation-adjusted.

Income shortfalls draw down investments after returns. If funds cannot cover the shortfall, stop without borrowing and report `funding_shortfall`, with investments zero. Otherwise search through the 100th birthday inclusively. If no qualifying age is found, report `search_limit`. A non-successful result uses null retirement age/years; projected amounts describe the final projection age. Zero expenses imply a zero target and immediate qualification.

Output: earliest retirement age, years remaining, projected investments/expenses, the 25× target, status, and assumptions. No yearly schedule. This is the earliest age under these fixed assumptions, not a guarantee of retirement safety. It does not simulate post-retirement withdrawals or test survival to a planning age.

Out of scope: taxes (use take-home income), pensions/Social Security, contribution limits, account types, investment volatility, fees beyond the supplied return, currency conversion, debts, and borrowing. Annual expenses are assumed to continue into retirement at the inflation-adjusted level.

## Layout

`contract.py` declares the typed task/tool. `nanoagent.yaml` selects `runner: tool`. `src/plugin/` contains the deterministic calculator and MCP server. `verifier/` independently replays the calculation using Decimal arithmetic, with no imports from the calculator. `tests/` covers boundaries, malformed data, default handling, differential replay, and real MCP transport. `product/` and `ui/` provide catalog metadata and the host's standard structured-output display.

## Develop and run

Use Python 3.12+:

```bash
python3 tests/validate.py
uv sync --frozen --extra dev
uv run python tests/validate.py --require-runtime
uv run ruff check .
# With NanoAgent installed, check publication rules too:
nanoagent plugin inspect .
```

The dependency-free run skips integration tests when dependencies are absent. `--require-runtime` fails on skipped tests. For a direct local calculation from the editable example:

```bash
PYTHONPATH=src python3 -c 'import json; from plugin.calculations import solve; print(json.dumps(solve(json.load(open("tests/example.json"))), indent=2))'
```

The MCP server requires `NANOAGENT_WORKSPACE`; after installation it starts with `NANOAGENT_WORKSPACE=/tmp uv run --frozen python -m plugin`. No network access or filesystem writes are requested by this plugin. Every calculation is independently verified; verification ignores supplied reference answers and rejects wrong assumptions, missing/extra fields, booleans in integer fields, and changed results. Invalid essential inputs return clear MCP error results.

The standard layout follows arxiv-source at commit 30b5534 and NanoAgent v0001. The slimconfig source follows NanoAgent's required master declaration; `uv.lock` pins its resolved commit. Version 0.2.0 replaces the incompatible scenario-based API. Old scenario IDs, schedule outputs, and offline scenario solver are intentionally removed.

For the assignment, collect live task inputs, logs, and verifier verdicts outside this repository for the report. Passing local checks is not a claim of marketplace publication or a successful live chat run. Interpreting ambiguous natural-language facts is the outer chat's responsibility; deterministic verification validates the structured calculation request, not the user's intended meaning.
