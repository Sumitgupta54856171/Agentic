"""
Custom tools for the CrewAI Multi-Model Spam Detection System.

Contains the LinkAnalysisTool — a rule-based "mock model" that analyzes URLs
for spam/phishing signals without needing an external LLM call.
"""

import re
import json
from typing import Type, Optional
from urllib.parse import urlparse

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Known risky patterns
# ---------------------------------------------------------------------------

SUSPICIOUS_TLDS = {
    ".xyz", ".tk", ".cf", ".ga", ".gq", ".ml", ".top", ".work",
    ".date", ".men", ".loan", ".download", ".review", ".win",
    ".bid", ".trade", ".webcam", ".science", ".stream",
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "tiny.cc", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "cli.gs", "shorturl.at", "t.co",
    "shorte.st", "adf.ly", "bit.do", "mcaf.ee", "tr.im",
    "v.gd", "u.to", "cutt.ly", "rebrand.ly", "bl.ink",
}

SPAMMY_ANCHOR_KEYWORDS = [
    "click here", "subscribe", "confirm", "verify", "update account",
    "claim prize", "free gift", "reset password", "secure your",
    "unsubscribe", "act now", "limited time",
]


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class LinkAnalysisInput(BaseModel):
    """Input schema for LinkAnalysisTool."""
    email_body: str = Field(..., description="The full plain-text body of the email to analyze for links.")


class LinkAnalysisTool(BaseTool):
    name: str = "Link URL Analyzer"
    description: str = (
        "Analyzes URLs found in an email body for spam and phishing signals. "
        "Returns a structured risk assessment including link count, suspicious TLDs, "
        "shortened URLs, IP-based URLs, and mismatched anchor text."
    )
    args_schema: Type[BaseModel] = LinkAnalysisInput

    def _extract_urls(self, text: str) -> list[dict]:
        """Extract all URLs from text, optionally with their anchor display text."""
        urls = []

        # Match markdown-style links: [text](url)
        md_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        for match in md_pattern.finditer(text):
            display_text, url = match.groups()
            urls.append({"url": url.strip(), "display_text": display_text.strip()})

        # Match bare URLs (http/https/ftp)
        bare_pattern = re.compile(
            r'(?:https?|ftp)://[^\s<>"\'\]\)]+(?:\.[^\s<>"\'\]\)]+)*'
        )
        for match in bare_pattern.finditer(text):
            url = match.group().rstrip(".,;:!?")
            # Avoid double-counting markdown-embedded URLs
            if not any(u["url"] == url for u in urls):
                urls.append({"url": url, "display_text": ""})

        return urls

    def _analyze_url(self, entry: dict) -> dict:
        """Analyze a single URL and return flags."""
        url = entry["url"]
        display_text = entry.get("display_text", "")
        flags = []
        risk_score = 0

        try:
            parsed = urlparse(url)
        except Exception:
            return {"url": url, "risk_score": 2, "flags": ["unparseable_url"]}

        domain = parsed.netloc.lower().lstrip("www.")
        path = parsed.path

        # 1. Check for IP-based domain
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        if ip_pattern.match(domain) or ip_pattern.match(parsed.netloc):
            flags.append("ip_based_domain")
            risk_score += 3

        # 2. Check for suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                flags.append(f"suspicious_tld:{tld}")
                risk_score += 2
                break

        # 3. Check for URL shortener
        for shortener in URL_SHORTENERS:
            if shortener in domain:
                flags.append(f"shortened_url:{shortener}")
                risk_score += 1
                break

        # 4. Check for hex encoding
        if "%" in url or re.search(r'\\x[0-9a-fA-F]{2}', url):
            flags.append("encoded_characters")
            risk_score += 2

        # 5. Check for excessive subdomains
        subdomain_count = domain.count(".")  # e.g. a.b.c.com -> 3 dots = 4 levels
        if subdomain_count >= 3:
            flags.append("excessive_subdomains")
            risk_score += 1

        # 6. Check for suspicious port
        try:
            if parsed.port and parsed.port not in (80, 443, 8080):
                flags.append(f"non_standard_port:{parsed.port}")
                risk_score += 1
        except ValueError:
            pass

        # 7. Check for mismatched anchor text
        if display_text and display_text.lower() != domain:
            # Check if display text matches any common domain-ish pattern
            if not any(kw in display_text.lower() for kw in SPAMMY_ANCHOR_KEYWORDS):
                # Still note it
                if "." not in display_text and len(display_text) > 3:
                    flags.append("mismatched_anchor_text")
                    risk_score += 1

        # 8. Check for spammy keywords in anchor text
        if display_text:
            for kw in SPAMMY_ANCHOR_KEYWORDS:
                if kw in display_text.lower():
                    flags.append(f"spammy_anchor_keyword:{kw}")
                    risk_score += 1
                    break

        # 9. Check for @ symbol in URL path (phishing)
        if "@" in parsed.path or "@" in parsed.params:
            flags.append("at_symbol_in_url")
            risk_score += 2

        return {
            "url": url,
            "display_text": display_text,
            "risk_score": min(risk_score, 10),
            "flags": flags,
        }

    def _run(self, email_body: str) -> str:
        urls = self._extract_urls(email_body)

        if not urls:
            return json.dumps({
                "url_count": 0,
                "total_risk_score": 0,
                "max_risk_score": 0,
                "average_risk_score": 0.0,
                "urls": [],
                "summary": "No URLs found in the email body.",
            })

        analyzed = [self._analyze_url(u) for u in urls]
        total_risk = sum(a["risk_score"] for a in analyzed)
        max_risk = max(a["risk_score"] for a in analyzed) if analyzed else 0
        avg_risk = total_risk / len(analyzed)

        # Collect all unique flags
        all_flags = []
        for a in analyzed:
            all_flags.extend(a["flags"])

        return json.dumps({
            "url_count": len(analyzed),
            "total_risk_score": total_risk,
            "max_risk_score": max_risk,
            "average_risk_score": round(avg_risk, 2),
            "urls": analyzed,
            "all_flags": list(set(all_flags)),
            "summary": (
                f"Found {len(analyzed)} URL(s). "
                f"Risk: avg={avg_risk:.1f}/10, max={max_risk}/10, total={total_risk}. "
                + (f"Flags: {', '.join(sorted(set(all_flags)))}." if all_flags else "No flags raised.")
            ),
        })
