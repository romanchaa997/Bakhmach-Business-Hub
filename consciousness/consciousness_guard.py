#!/usr/bin/env python3
"""Consciousness Guard: Evaluates system integration and well-being metrics."""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Tuple
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Guard:
    """Consciousness Guard evaluates system metrics and gates deployments."""

    def __init__(self):
        self.integration_score = 70  # Default: assume medium
        self.wellbeing_score = 65
        self.stability_score = 75
        self.mode = "SAFE"
        self.load_metrics()

    def load_metrics(self):
        """Load metrics from various sources."""
        self.integration_score = self._calculate_integration_score()
        self.wellbeing_score = self._calculate_wellbeing_score()
        self.stability_score = self._calculate_stability_score()
        self._determine_mode()

    def _calculate_integration_score(self) -> int:
        """Calculate code/ML/services integration score (0-100)."""
        score = 0
        try:
            # Check if backend tests exist and pass (33 points)
            if os.path.exists("code/perf/baseline.json"):
                with open("code/perf/baseline.json") as f:
                    data = json.load(f)
                    if data.get("coverage", 0) >= 80:
                        score += 33
                    else:
                        score += 20
        except Exception as e:
            logger.warning(f"Could not read code metrics: {e}")
            score += 15

        try:
            # Check ML metrics (33 points)
            if os.path.exists("ml/monitoring/metrics.json"):
                with open("ml/monitoring/metrics.json") as f:
                    data = json.load(f)
                    if data.get("data_drift", 1.0) < 0.3:
                        score += 33
                    else:
                        score += 15
        except Exception as e:
            logger.warning(f"Could not read ML metrics: {e}")
            score += 15

        try:
            # Check services readiness (34 points)
            if os.path.exists("services/readiness.json"):
                with open("services/readiness.json") as f:
                    data = json.load(f)
                    if data.get("slo_passing", False):
                        score += 34
                    else:
                        score += 10
        except Exception as e:
            logger.warning(f"Could not read services metrics: {e}")
            score += 10

        return min(100, score)

    def _calculate_wellbeing_score(self) -> int:
        """Calculate personal well-being score from PDP (0-100)."""
        score = 0
        try:
            if os.path.exists("workflow/PDP.md"):
                with open("workflow/PDP.md") as f:
                    content = f.read()
                    # Check if weekly review is recent (+20)
                    if "weekly review" in content:
                        score += 20
                    # Simple heuristic: if file size reasonable, assume good state (+30)
                    if len(content) > 500:
                        score += 30
        except Exception as e:
            logger.warning(f"Could not read PDP: {e}")
            score = 50  # Default moderate

        # Check task completion (0-30 points)
        try:
            if os.path.exists("tasks/this_week.md"):
                with open("tasks/this_week.md") as f:
                    content = f.read()
                    lines = content.split("\n")
                    completed = sum(1 for line in lines if "[x]" in line.lower())
                    total = sum(1 for line in lines if "[" in line)
                    if total > 0:
                        completion_rate = completed / total
                        score += int(completion_rate * 30)
        except Exception as e:
            logger.warning(f"Could not read tasks: {e}")

        # Check for incidents (0-20 points)
        if not os.path.exists("workflow/incidents.log"):
            score += 20  # No incidents = good
        else:
            try:
                with open("workflow/incidents.log") as f:
                    lines = f.readlines()
                    recent_incidents = [
                        l for l in lines
                        if datetime.now() - datetime.fromisoformat(l[:19]) < timedelta(days=7)
                    ]
                    if len(recent_incidents) == 0:
                        score += 20
                    elif len(recent_incidents) <= 1:
                        score += 10
            except Exception as e:
                logger.warning(f"Could not read incidents: {e}")

        return min(100, score)

    def _calculate_stability_score(self) -> int:
        """Calculate system stability score (0-100)."""
        score = 0

        # Default: assume system is stable
        score = 75

        # TODO: Parse CI/CD logs for actual incidents
        # TODO: Check error rates from observability platform
        # TODO: Parse git history for rollbacks

        return min(100, score)

    def _determine_mode(self):
        """Determine FAST/SAFE/HALT mode based on scores."""
        if self.integration_score >= 70 and self.wellbeing_score >= 60 and self.stability_score >= 70:
            self.mode = "FAST"
        elif self.integration_score >= 50 and self.wellbeing_score >= 50 and self.stability_score >= 50:
            self.mode = "SAFE"
        else:
            self.mode = "HALT"

    def can_proceed(self, change_type: str = "other") -> bool:
        """Check if a change type is allowed in current mode."""
        allowed = {
            "FAST": ["docs", "refactor", "feature", "ml-model"],
            "SAFE": ["docs", "security", "bug-fix"],
            "HALT": ["security", "bug-fix"],
        }
        return change_type in allowed.get(self.mode, [])

    def report(self) -> Dict:
        """Generate a consciousness report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "integration_score": self.integration_score,
            "wellbeing_score": self.wellbeing_score,
            "stability_score": self.stability_score,
            "mode": self.mode,
            "decision": "PROCEED" if self.mode in ["FAST", "SAFE"] else "BLOCK",
        }


def main():
    guard = Guard()
    report = guard.report()

    print(f"\n{'='*60}")
    print("CONSCIOUSNESS GUARD REPORT")
    print(f"{'='*60}")
    print(f"Integration Score:  {report['integration_score']:>3d}/100 {'✅' if report['integration_score'] >= 70 else '⚠️' if report['integration_score'] >= 50 else '❌'}")
    print(f"Well-being Score:   {report['wellbeing_score']:>3d}/100 {'✅' if report['wellbeing_score'] >= 70 else '⚠️' if report['wellbeing_score'] >= 50 else '❌'}")
    print(f"Stability Score:    {report['stability_score']:>3d}/100 {'✅' if report['stability_score'] >= 70 else '⚠️' if report['stability_score'] >= 50 else '❌'}")
    print(f"\nMode:               {report['mode']}")
    print(f"Decision:           {report['decision']}")
    print(f"{'='*60}\n")

    # Write report to JSON
    with open(".consciousness_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Exit code: 0 if proceed, 1 if block
    sys.exit(0 if report["decision"] == "PROCEED" else 1)


if __name__ == "__main__":
    main()
