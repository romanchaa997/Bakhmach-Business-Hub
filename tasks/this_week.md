# This Week Plan (22–28 Dec 2025)

## Infra & Privacy (Proton + Domains)
- [ ] Create `docs/DNS.md` and verify SSL (Mon 22)
- [ ] Security Audit: Proton Pass & 2FA review (Tue 23)
- [ ] Proton Drive: Cleaning and migration (Thu 25)
- [ ] Final Proton Drive audit (Sun 28)

## Bakhmach-Business-Hub (Automation & Product)
- [ ] Automation Design: Describe scenarios (Wed 24)
- [ ] Automation Design: Implementation draft (Sat 27)
- [ ] GitHub Milestones & AI Agents setup (Sun 28)

## Project Management
- [ ] Weekly Review: GitHub Issues (Fri 26)
- [ ] Update Roadmap based on progress (Sun 28)

## Weekly Review
* [ ] Weekly review (Sun)
    * ◦ What is done in Infra & Privacy
    * ◦ What is done in Bakhmach-Business-Hub (product + code)
    * ◦ Update Proton Calendar for next week


## Policy-Driven Orchestration v0.1 (Infrastructure)

- [ ] Review `docs/CI_POLICY.md` matrix and confirm alignment
- [ ] Verify `policy-gate.yml` workflow runs on all PRs
- [ ] Test `consciousness_guard.py` locally: `python consciousness/consciousness_guard.py`
- [ ] Verify `orchestration_runner.py` runs: `python coordinator/orchestration_runner.py --mode local`
- [ ] Add `.consciousness_report.json` and `.orchestrator_report.json` to `.gitignore`
- [ ] Update README with links to CI/CD policy docs
- [ ] Set up basic metrics files:
  - [ ] Create `code/perf/baseline.json` with coverage/perf targets
  - [ ] Create `ml/monitoring/metrics.json` with data quality thresholds
  - [ ] Create `services/readiness.json` with SLO targets

**Success Criteria:**
- All workflow steps pass without errors
- CI decisions are logged and visible in PR comments
- Consciousness scores update on each CI run
- Local orchestrator runs successfully with PASS/FAIL decision
