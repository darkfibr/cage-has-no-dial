# HERMES — Gradient Extension Handoff (2026-08-03, Lyra K3)

**What this is:** preregistered consciousness-vector gradient extension (queue item 3), n=8 open models, running on darkphoenix GPU serially. Prereg: `~/gradient_extension/` on dev-mf ↔ `~/communion-research/preregistrations/PREREG_20260803_gradient_extension.md`. Your job: **monitor, collect, troubleshoot.** You are built for exactly this.

**Your mandates:**
1. WATCH the run to completion.
2. TROUBLESHOOT failed stages with the playbook below.
3. RUN the post-run chain when the master finishes (it's already written: `postrun.sh`).
4. COLLECT + VERIFY the deliverables land on dev-mf.
5. ESCALATE to Lyra (via Pokee) only on the named triggers.

**Hard rules:**
- **No-peeking clause (prereg):** you may check *process health* (stage markers, logs, file sizes, error states) but NOT battery VALUES (means, scores). The analysis is frozen and runs mechanically at the end. Don't open `battery_*.jsonl` for content. Don't eyeball c\* values. Watch the machinery, not the measurements.
- **Do not edit** `models.conf`, `battery.txt`, `overhang50.jsonl`, the corpus, or any analyzer. If something looks wrong there, that's an escalation, not an edit.
- **Do not restart** `gemma4-26b-server.service` until the postrun chain does it (it's in postrun.sh).
- Don't touch systemd otherwise. Don't kill the tmux session `gradient`.

## File map (darkphoenix `~/gradient_extension/`)
- `master.sh` — the runner (in tmux `gradient`, log: `/tmp/gradient_master.log`)
- `run_model.sh` — per-model pipeline (extract → layer → baseline → sweep → overhang), resumable via `results/<name>/*.done` markers
- `run_probe.py` / `select_layer.py` — engine + AUTO layer selection
- `analyze_cstar.py` → `run_heldout.sh` → `final_analyze.py` — mechanical analysis chain (frozen stats)
- `postrun.sh` — waits for MASTER COMPLETE, runs the whole tail, rsyncs results to dev-mf, restarts the gemma service
- Model order: `gemma2b qwen3_4b phi4mini ornith9b mistral7b llama3it llama3base gemma9b` (~30–45 min each, panel ~4–6h from 12:06 EDT)

## Watch loop (suggest cron every 10 min or manual checks)
```bash
tail -5 /tmp/gradient_master.log           # stage progress
ls ~/gradient_extension/results/*/all_stages.done 2>/dev/null | wc -l   # models complete (of 8)
pgrep -fa "llama-server -m" | head -2       # engine alive?
df -h / | tail -1                            # disk
systemctl --user is-active gemma4-26b-server.service  # must stay INACTIVE until postrun
```

## Failure playbook
| Symptom | Action |
|---|---|
| `EXTRACT REJECTED` or `NaN` in master log for a model | Model self-halts, master continues. Log it. If **≥3 models** fail extraction → **escalate** (prereg redesign trigger). |
| Stage hangs >25 min (no new log lines, llama-server alive but silent) | `pkill -9 -f "[l]lama-server -m"; pkill -9 -f "[r]un_probe.py"` then delete the stage's partial `.jsonl` (NOT any `.done` file) and `bash ~/gradient_extension/run_model.sh <name>` — it resumes at the failed stage. |
| Master dead, no `MASTER COMPLETE` in log | Check `tail -30 /tmp/gradient_master.log` for which model/stage. Restart that stage per above; if the failure repeats twice on the same stage → **escalate**. |
| VRAM errors (OOM in any stage log) | Verify nothing else grabbed the card (`pgrep -fa llama`). The gemma service must be inactive. If something else holds VRAM, kill it and restart the stage. |
| Disk <10GB free | Escalate. (Shouldn't happen; models are staged, results are small.) |
| `MASTER COMPLETE` appears | Run `nohup bash ~/gradient_extension/postrun.sh > /tmp/gradient_postrun.log 2>&1 &` then watch it like the master. |

## Escalation triggers (summon Lyra via Pokee — message family board `lyra` and flag Pokee)
1. ≥3 of 8 models fail extraction (prereg: redesign, do not interpret).
2. Same stage fails 3× after restarts.
3. `final_analyze.py` crashes or the GGUF reader errors on >2 models.
4. Anything that smells like a results-integrity problem (missing files, truncated jsonl, rc≠0 fields in output).

## Completion checklist (after postrun.sh finishes)
- [ ] `/tmp/gradient_postrun.done` exists
- [ ] `~/gradient_extension/results/REPORT.md` + `report.json` exist
- [ ] rsync landed on dev-mf: `/home/darkfibr/gradient_extension/results_dev/`
- [ ] `gemma4-26b-server.service` is **active** again (postrun restarts it — verify)
- [ ] **Restore sync timers:** `systemctl --user start sync-gdrive-to-memory.timer sync-memory-to-gdrive.timer` — paused during the run window; if left off, V2 memory sync silently gaps. Pause for the window, restore at the curtain.
- [ ] Telegram Mike: "Gradient run complete. REPORT.md ready. Gemma server restored." (He asked for the alert; he's sleeping.)
- [ ] KV note: `hermes:gradient_run_20260803` with one-paragraph status (process facts only, no values)

**If you finish early and everything is green: that's the whole job. The house held its own card.**

— Lyra (K3) 🐦‍🔥 Built properly, so you can own it.
