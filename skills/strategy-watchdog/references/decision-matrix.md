# Strategy Watchdog Decision Matrix

| Observation | Classification | Permitted action |
|---|---|---|
| Attributed fill/position matches approved package | `FILLED_OR_OPEN` | Verify management/exit process; do not resubmit |
| Attributed order accepted or partially filled | `WORKING` | Observe canonical order management; do not duplicate |
| Scheduler did not wake; authorized window open; no attributed order/fill/position | Infra failure | Repair exact scheduler and invoke canonical runner |
| Runner timed out; broker order state unknown | `UNKNOWN` | Reconcile by client-order ID and OCC legs before any retry |
| Quote stale, credit too low, spread too wide, or risk gate failed under current contract | `VALID_NO_TRADE` | Preserve the skip unless the operator explicitly amends the applicable parameter |
| Registry/runtime/release mismatch with one approved artifact | Infra failure | Restore exact approved lineage, test, then retry in the authorized window |
| Strategy-scoped lock exists and owning process is alive | `WORKING` or `UNKNOWN` | Wait/reconcile; never remove the lock |
| Strategy-scoped lock owner is conclusively gone | Infra failure | Remove/rotate only that lock, record evidence, retry in the authorized window |
| Other strategy has unrelated OCC contracts | No collision | Continue the candidate; never block the whole account or underlying |
| Other strategy has same OCC on the same side | Shared exposure | Continue if attribution and aggregate risk pass; do not mistake it for a duplicate |
| Existing same OCC on the opposite side | Netting conflict | Block that candidate package because broker netting destroys strategy ownership |
| Existing order or position has uncertain OCC/side/attribution | `UNKNOWN` | Reconcile promptly; do not convert ambiguity into a permanent global stop |
| Original window closed but operator explicitly opened a catch-up window/tolerance | Authorized amendment | Record the amendment, reprice the original candidate, run gates, and recover canonically |
| No authorized window remains or a concrete risk/account constraint still fails | `BLOCKED` | Preserve exact evidence after exhausting authorized recovery |

## Duplicate-proof retry checklist

- Confirm broker clock is inside the original or explicitly amended catch-up window.
- Search recent and working orders by strategy/client-order lineage.
- Compare every OCC leg and side, not only the underlying.
- Check current broker positions and strategy state.
- Confirm the canonical idempotency key has not succeeded already.
- Prefer the scheduler/runner; use an attributable ExecutionGateway recovery entry point if the
  operator explicitly authorizes recovery that the scheduler cannot express.
- Re-read orders and positions after the invocation.
