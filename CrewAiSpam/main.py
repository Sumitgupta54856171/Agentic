"""
CrewAI Multi-Model Spam Detection System — Entry Point.

Uses 4 agents (3 Fireworks models + 1 rule-based tool) to collaboratively
analyze and classify emails as spam, ham, or suspicious.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from crewai import Crew, Process

from CrewAiSpam.agents import (
    content_analyst,
    sender_analyst,
    link_analyst,
    final_judge,
)
from CrewAiSpam.tasks import (
    analyze_content_task,
    analyze_sender_task,
    analyze_links_task,
    final_verdict_task,
)
from CrewAiSpam.test_emails import all_emails

# ---------------------------------------------------------------------------
# Load API key
# ---------------------------------------------------------------------------

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "Langgraph", ".env")
load_dotenv(dotenv_path)
load_dotenv()

if not os.environ.get("FIREWORKS_API_KEY"):
    print("⚠️  FIREWORKS_API_KEY not found. Set it in Langgraph/.env or your shell.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_classification(text: str) -> str:
    """Pull classification from the judge's output (spam / ham / suspicious)."""
    text_lower = text.lower()
    # Pattern: "Classification: spam|ham|suspicious"
    m = re.search(r"classification[:\s]+(spam|ham|suspicious)", text_lower)
    if m:
        return m.group(1)

    # Fallback: look for the words themselves at sentence start
    for word in ("spam", "ham", "suspicious"):
        if re.search(rf"(?<![a-z]){word}(?![a-z])", text_lower):
            return word
    return "unknown"


# ---------------------------------------------------------------------------
# Spam detection runner
# ---------------------------------------------------------------------------

def detect_spam(subject: str, sender: str, body: str) -> dict:
    """Run the full CrewAI multi-agent pipeline on one email."""
    inputs = {"subject": subject, "sender": sender, "body": body}

    crew = Crew(
        agents=[content_analyst, sender_analyst, link_analyst, final_judge],
        tasks=[
            analyze_content_task,
            analyze_sender_task,
            analyze_links_task,
            final_verdict_task,
        ],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff(inputs=inputs)

    task_outputs = result.tasks_output if hasattr(result, "tasks_output") else []
    reports = {}
    for i, to in enumerate(task_outputs):
        role = (
            "content_analyst" if i == 0
            else "sender_analyst" if i == 1
            else "link_analyst" if i == 2
            else "final_verdict"
        )
        reports[role] = to.raw if hasattr(to, "raw") else str(to)

    final_raw = task_outputs[-1].raw if task_outputs else ""
    classification = _extract_classification(final_raw) if final_raw else "error"

    return {
        "email_subject": subject,
        "classification": classification,
        "classification_raw": final_raw,
        "reports": reports,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  🛡️  CrewAI Multi-Model Spam Detection System")
    print("=" * 60)
    print(f"  Models: deepseek-v4-flash (x2) + deepseek-v4-pro (x2)")
    print(f"  Agents: Content Analyst, Sender Analyst, Link Analyst, Final Judge")
    print(f"  Emails to check: {len(all_emails)}")
    print("=" * 60)

    results = []

    for idx, email in enumerate(all_emails):
        print(f"\n{'─' * 60}")
        print(f"📧 Email #{idx + 1}: {email.subject[:80]}")
        print(f"   From: {email.sender}")
        print(f"   Expected: {email.expected.upper()}")
        print(f"{'─' * 60}")

        try:
            result = detect_spam(email.subject, email.sender, email.body)
            results.append(result)

            print(f"\n📋 Final Verdict ({result['classification'].upper()}):")
            print(f"   {result['classification_raw'][:600]}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        print()

    # ---- Summary table ----
    print("=" * 60)
    print("  📊  S U M M A R Y")
    print("=" * 60)
    correct = 0
    for idx, email in enumerate(all_emails):
        cls = results[idx]["classification"] if idx < len(results) else "error"
        ok = cls == email.expected
        correct += 1 if ok else 0
        icon = "✅" if ok else ("❌" if cls != "unknown" else "❓")
        print(f"  {icon} #{idx + 1}: {cls:<12s} (expected {email.expected})  {email.subject[:50]}")

    total = len(all_emails)
    print(f"\n  🎯 Accuracy: {correct}/{total} ({correct / total * 100:.0f}%)")
    print("=" * 60)


if __name__ == "__main__":
    main()
