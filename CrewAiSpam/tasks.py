"""
Task definitions for the CrewAI Multi-Model Spam Detection System.

Three parallel analysis tasks feed into a final judgment task.
"""

from crewai import Task

from CrewAiSpam.agents import (
    content_analyst,
    sender_analyst,
    link_analyst,
    final_judge,
)

# ---------------------------------------------------------------------------
# Task 1: Content Analysis
# ---------------------------------------------------------------------------

analyze_content_task = Task(
    description=(
        "Analyze the email body below for spam and phishing indicators in the TEXT CONTENT.\n\n"
        "Look for:\n"
        "- Excessive use of ALL CAPS\n"
        "- Urgency language ('act now', 'limited time', 'expires in 24 hours')\n"
        "- Promises of free money, prizes, or gifts\n"
        "- Poor grammar or unusual phrasing\n"
        "- Excessive exclamation marks\n"
        "- Requests for personal/financial information\n"
        "- Pressure to click links immediately\n\n"
        "Email subject: {subject}\n"
        "Email sender: {sender}\n"
        "Email body:\n{body}\n\n"
        "Provide a structured report of your findings. End with a clear verdict "
        "on whether the CONTENT appears spammy (scale 0-10, where 10 = definitely spam content)."
    ),
    expected_output=(
        "A structured report listing each content-based spam indicator found (or noting none), "
        "with a final numeric content-spam score from 0 to 10."
    ),
    agent=content_analyst,
)

# ---------------------------------------------------------------------------
# Task 2: Sender Analysis
# ---------------------------------------------------------------------------

analyze_sender_task = Task(
    description=(
        "Analyze the sender information of the email below for spoofing, "
        "impersonation, or suspicious origin signals.\n\n"
        "Look for:\n"
        "- Suspicious domain name (typosquatting, unusual TLDs)\n"
        "- Sender claiming to be from a company but using a different domain\n"
        "- Generic or suspicious email patterns\n"
        "- Signs of impersonation of well-known brands\n\n"
        "Email subject: {subject}\n"
        "Email sender: {sender}\n"
        "Email body:\n{body}\n\n"
        "Provide a structured report of your findings. End with a clear verdict "
        "on whether the SENDER appears suspicious (scale 0-10, where 10 = definitely suspicious sender)."
    ),
    expected_output=(
        "A structured report listing each sender-based red flag found (or noting none), "
        "with a final numeric sender-risk score from 0 to 10."
    ),
    agent=sender_analyst,
    context=[],  # Don't include previous task output — analyze the email independently
)

# ---------------------------------------------------------------------------
# Task 3: Link Analysis (uses the rule-based tool)
# ---------------------------------------------------------------------------

analyze_links_task = Task(
    description=(
        "Use the LinkAnalysisTool to extract and analyze all URLs in the email body below.\n\n"
        "Email subject: {subject}\n"
        "Email sender: {sender}\n"
        "Email body:\n{body}\n\n"
        "Call the LinkAnalysisTool with the email body as input, then summarize the results. "
        "Focus on: URL count, risk scores, suspicious TLDs, shortened URLs, IP-based domains, "
        "and mismatched anchor text."
    ),
    expected_output=(
        "A summary of the link analysis results: how many URLs found, the risk scores, "
        "any specific flags raised, and whether the links are suspicious or safe."
    ),
    agent=link_analyst,
    context=[],  # Don't include previous task outputs — analyze links independently
)

# ---------------------------------------------------------------------------
# Task 4: Final Judgment (depends on all three analyses)
# ---------------------------------------------------------------------------

final_verdict_task = Task(
    description=(
        "You are the Senior Spam Classification Judge. Review the three team reports below "
        "(Content Analysis, Sender Analysis, Link Analysis) and make the FINAL CLASSIFICATION.\n\n"
        "=== YOUR JUDGMENT ===\n"
        "Based on ALL of the above evidence, classify this email. "
        "Consider the severity and number of flags across all three reports.\n\n"
        "Provide your verdict in this exact format:\n"
        "Classification: spam | ham | suspicious\n"
        "Confidence: 0.0 to 1.0\n"
        "Reasoning: <detailed explanation>\n"
        "Key Flags: <comma-separated list>\n\n"
        "Be thorough but fair. A legitimate email with one minor flag should not be classified as spam."
    ),
    expected_output=(
        "Classification: spam|ham|suspicious with confidence score, reasoning, and key flags."
    ),
    agent=final_judge,
    context=[analyze_content_task, analyze_sender_task, analyze_links_task],
)
