# Retirement Sustainability Planner

Project whether a retirement portfolio funds annual spending for a configurable 1–60 year horizon. Use a prescribed withdrawal policy, account returns, inflation, pension timing, and fictional progressive taxation. The normal example covers 30 years.

Task ID: `project-retirement`. Runner: `agent`. Each monetary value is an integer number of cents; a basis point is 1/100 of a percentage point. No tool solves the task or calls an LLM. All scenarios are synthetic, bundled JSON fixtures, not live financial data.

## Task input and output

Example task input:

```json
{
  "scenario_id": "comfortable",
  "years": 30
}
```

The complete typed output is `RetirementOutput` in `contract.py`; nested row types also live there. All fields and rows are required. Month/year indices start at 1. Only the scenario IDs listed below are accepted. Arbitrary financial inputs are deliberately outside this task's scope.

Submit every year through the requested horizon or the first shortfall. All growth, pension income, required withdrawals, actual withdrawals, tax, surplus, shortfall, balances, and summary fields must match the prescribed policy. sustainable=true means no shortfall during this finite projection; it is not a guarantee about real retirement.

## Tools

Task `project-retirement` uses the following tools.

| Tool | Input | Output |
|---|---|---|
| `get_account_balances` | scenario_id | Initial cash, tax-deferred, and tax-free balances. |
| `get_assumptions` | scenario_id | Spending, pension amount and start year, inflation, account returns, and mandatory withdrawal rate. |
| `get_tax_schedule` | scenario_id | Fictional marginal brackets in cents and basis points. The last upper_cents=0 means no upper limit. |
| `get_rules` | none | Annual event order, withdrawal priority, tax treatment, rounding, and failure behavior. |

## Exact financial rules

1. This is a fictional deterministic model, not current tax law or investment advice. Money is integer cents.
2. Project 1 to 60 years (default CLI example: 30). Year 1 uses annual_spending_cents; later spending increases by inflation_bps, rounded to cents.
3. At the start of each year apply each account annual return to its opening balance, rounding the signed gain to nearest cent, ties away from zero.
4. Pension income is taxable and starts in income_start_year. There is no other income or tax deduction.
5. Tax brackets list cumulative upper_cents and rate_bps, with upper_cents=0 for the final unlimited bracket. Compute total progressive tax exactly, then round once to cents, ties up.
6. First withdraw the required minimum from tax_deferred: post-growth balance times minimum_deferred_bps, rounded to cents.
7. To cover spending plus tax, use cash first, then additional tax_deferred, then tax_free. At each step withdraw the smallest whole-cent amount sufficient, or exhaust the account.
8. Cash and tax_free withdrawals are untaxed. All tax_deferred withdrawals are taxable. Recompute tax as withdrawals increase.
9. Any surplus after spending and tax is deposited into cash at year end. On failure, report the shortfall and stop at that year. first_shortfall_year=0 means no failure in the requested horizon.

## Bundled scenarios

- `comfortable`
- `early-retirement`
- `depleting`
- `income-only`
- `exact-funds`
- `market-loss`
- `tax-gross-up`
- `mandatory-surplus`

Data: `src/plugin/data/scenarios.json`; authoritative rule text: `src/plugin/data/rules.json`. Scenario IDs are dictionary keys, never paths. Tools reread packaged fixtures and do not mutate data or use the workspace. Permission declarations request no network hosts or filesystem writes.

## Layout

```text
contract.py             Typed task/tool schemas and registries
nanoagent.yaml          NanoAgent runtime, permissions, tools, and agent task
pyproject.toml, uv.lock Standalone package metadata and pinned dependencies
src/plugin/            MCP server, read-only tools, bundled data, offline sample calculations
verifier/              Semantic validation and independent financial replay
tests/                 Verifier tests, validation/example CLIs, and optional runtime integration
product/, ui/          Catalog metadata, icon, and default host-renderer declaration
```

Layout and MCP integration follow [arxiv-source at commit 30b5534](https://github.com/zeyuyang8/arxiv-source/tree/30b5534a8ed17f53c3e87d7a092ae20b1e5f6d24). The financial tasks, tools, data, and checks are original implementations. This directory is standalone and does not import either sibling finance plugin or the reference checkout.


## Develop and run

Use Python 3.12 or later. From this plugin's directory:

```bash
# Financial calculations, fixture tools, malformed-output tests, and boundary tests:
python3 tests/validate.py

# Sample candidate output plus the independent verifier verdict; no dependencies needed:
python3 tests/solve.py comfortable --years 30 > /tmp/retirement-planner-example.json

# Full typed-contract and MCP integration, after installing uv:
uv sync --frozen --extra dev
uv run python tests/validate.py --require-runtime
uv run ruff check .
```

The standard-library test command explicitly skips the integration tests if runtime dependencies are missing. `--require-runtime` fails if any tests are skipped, so a partial run cannot count as complete runtime validation. Integration tests round-trip real slimconfig contracts, call every MCP handler, and launch the actual stdio server with an MCP client.

`uv.lock` inherits the resolved dependency graph and package hashes from the supplied arxiv-source reference, with this project's identity updated. The slimconfig source follows NanoAgent's required `master` branch declaration; `uv.lock` pins the reference's exact commit for frozen installs. Runtime dependency installation requires network access once; the task itself runs offline afterward. The frozen lock still needs a successful uv sync on a network-enabled machine to confirm installation.

To start the server directly after installation:

```bash
NANOAGENT_WORKSPACE=/tmp uv run --frozen python -m plugin
```

The server communicates via MCP stdio; it is normally launched by NanoAgent, not used as an interactive terminal program. `tests/solve.py` is an offline example candidate generator, excluded from the MCP tool list; it is not an agent evaluation run.

## Verifier

The verifier uses Decimal arithmetic and solves tax-bracket withdrawal gross-ups algebraically, independently of the sample solver’s integer tax arithmetic and binary search. This checks that withdrawals also fund their own tax, and that minimum-withdrawal surpluses return to cash.

The verifier accepts either contract dataclass instances (the harness interface) or raw dictionaries (local checks). Public entry points follow the reference: `verify_input(tool, value)`, `verify_output(tool, input_value, output_value, workspace)`, and `verify_task(task, arguments, output, reference, workspace)`. Verdicts contain `valid`, `score`, `message`, and `details`. The task check ignores any supplied reference answer and recomputes from trusted literals in `verifier/fixtures.py`. Tests ensure those literals match the packaged JSON. The verifier imports no MCP implementation code and reads no agent-controlled fixture files.

Checks reject missing/extra fields, changed values, truncated or duplicated rows, incorrect ordering, booleans/floats substituted for integer cents, unknown scenarios, and invalid input bounds. Tool verifiers compare retrieved data to fixtures; task verifiers use independent financial implementations. Tests include hand-calculated cases, all bundled scenarios, negative-output mutations, and 100 deterministically seeded scenario variations per plugin.


## Limitations and submission evidence

This is a deterministic projection, not a search for a globally optimal tax strategy. Tax brackets and the mandatory withdrawal percentage are fictional and do not model current law. Returns are fixed per account; there is no market randomness, sequence-of-returns analysis, fees, inheritance, healthcare modeling, or pension indexing.

These scenarios demonstrate calculations under stated assumptions and are not personalized financial advice. No RUSH Lab publication or live agent run is claimed. Collect actual task inputs, validation logs, and verifier verdicts outside this repository for the assignment PDF; the example command above writes to `/tmp` for that reason. A passing sample solver run demonstrates the verifier path, not that an agent successfully completed the task.
