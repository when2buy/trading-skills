# Pitfalls (all hit in practice)

| Pitfall | Consequence | Avoid by |
|---|---|---|
| Planning without seeing the live system | Plan overturned within 30 minutes | Read-only survey is step zero |
| Gain smaller than noise | The "optimisation" is drift | A/A first, set a threshold |
| Cross-machine comparison | Machine difference read as effect | Same-machine ABABA |
| Trusting the status code | Wrong billing fields unnoticed | Check fields, not codes |
| Adopting a sub-agent's conclusion unchecked | Wrong claim enters config | Raw-data re-check + errata section |
| Replacing machines without telling anyone | Two outages | Check who else is operating first |
| `pkill -f <pattern>` | Kills the service and yourself | Kill by exact PID |
| Canary on a scanned port range | Dashboard counted it as production | Bind locally, avoid scanned ports |
| Docs say "done", live system unchanged | A public exposure stayed open | Periodically re-verify docs against the live system |
| Extrapolating an isolated-environment gain | Promise that cannot be kept | State the scope on every conclusion |
| Five plans with five numbering schemes | Nobody knows what to do | One task table, one ID scheme |
| Loop depends on people remembering | Rules not followed | Automate yardstick + gates + rollback per commit |
| Foreground long jobs | Die with the SSH session | tmux / `setsid nohup` |
