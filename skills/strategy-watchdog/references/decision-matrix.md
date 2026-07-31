# Strategy Watchdog Decision Matrix

| Observation | Classification | Permitted action |
|---|---|---|
| Attributed fill/position matches approved package | `FILLED_OR_OPEN` | Verify management/exit process; do not resubmit |
| Attributed order accepted or partially filled | `WORKING` | Observe canonical order management; do not duplicate |
| Scheduler did not wake; entry window open; no order/fill/position | Infra failure | Repair exact scheduler and invoke canonical runner once |
| Runner timed out; broker order state unknown | `UNKNOWN` | Reconcile by client-order ID and OCC legs before any retry |
| Quote stale, credit too low, spread too wide, risk/collision gate failed | `VALID_NO_TRADE` | Preserve the skip; do not weaken the gate |
| Registry/runtime/release mismatch with one approved artifact | Infra failure | Restore exact approved lineage, test, then retry only in-window |
| Strategy-scoped lock exists and owning process is alive | `WORKING` or `UNKNOWN` | Wait/reconcile; never remove the lock |
| Strategy-scoped lock owner is conclusively gone | Infra failure | Remove/rotate only that lock, record evidence, retry in-window |
| Existing overlapping order or position has uncertain attribution | `UNKNOWN` | Stop new entry; reconcile ownership |
| Entry window closed or safe recovery requires altered economics | `STOPPED_SAFE` | Do not chase; preserve evidence and fix infra for next run |

## Duplicate-proof retry checklist

- Confirm broker clock is inside the original strategy entry window.
- Search recent and working orders by strategy/client-order lineage.
- Compare every OCC leg, not only the underlying.
- Check current broker positions and strategy state.
- Confirm the canonical idempotency key has not succeeded already.
- Invoke only the approved scheduler/runner path.
- Re-read orders and positions after the invocation.
