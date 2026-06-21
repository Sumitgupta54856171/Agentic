"""
Agent definitions for the CrewAI Multi-Model Spam Detection System.

Four agents with complementary roles, using a mix of:
- Fireworks deepseek-v4-flash (fast, for content analysis)
- Fireworks deepseek-v4-pro (higher quality, for sender analysis & final verdict)
- Local rule-based "model" (link analysis — deterministic, no LLM cost)
"""

import os

from dotenv import load_dotenv
from crewai import Agent, LLM

from CrewAiSpam.tools import LinkAnalysisTool

# Ensure API key is available before any LLM is constructed.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "Langgraph", ".env"))
load_dotenv()

# ---------------------------------------------------------------------------
# Monkey-patch: disable cache_breakpoint markers
# CrewAI injects "cache_breakpoint": True on stable message prefixes for
# Anthropic prompt caching.  Fireworks / OpenAI-compatible APIs reject this
# as an unknown field, so we neutralise the marker here.
# ---------------------------------------------------------------------------
import crewai.llms.cache as _cache_mod

_cache_mod.mark_cache_breakpoint = lambda msg: msg  # no-op
_cache_mod.CACHE_BREAKPOINT_KEY = "__noop_crewai_cache"

# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------
# CrewAI uses litellm under the hood. Fireworks has an OpenAI-compatible API,
# so we use the "openai" provider with Fireworks' base URL.
#
# The FIREWORKS_API_KEY env var must be set before kickoff (main.py loads it
# from .env).  The LLMs are lazily initialised so the key is available.

FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"

_llm_fast: LLM | None = None
_llm_pro: LLM | None = None


def _make_llm(model: str) -> LLM:
    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    return LLM(
        model=f"openai/{model}",
        base_url=FIREWORKS_BASE_URL,
        api_key=api_key,
        temperature=0.3,
        max_tokens=2048,
    )


def get_fast_llm() -> LLM:
    global _llm_fast
    if _llm_fast is None:
        _llm_fast = _make_llm("accounts/fireworks/models/deepseek-v4-flash")
    return _llm_fast


def get_pro_llm() -> LLM:
    global _llm_pro
    if _llm_pro is None:
        _llm_pro = _make_llm("accounts/fireworks/models/deepseek-v4-pro")
    return _llm_pro


# Instantiate the tool once and share it (no API key needed)
link_tool = LinkAnalysisTool()

# ---------------------------------------------------------------------------
# Agent 1: Content Analyst (fast model)
# ---------------------------------------------------------------------------

content_analyst = Agent(
    role="Email Content Analyst",
    goal=(
        "Analyze the body of an email for spam indicators: excessive capitalization, "
        "urgency language, phishing keywords, poor grammar, unusual formatting, "
        "and promises of money or free gifts."
    ),
    backstory=(
        "You are a veteran email security analyst who has reviewed millions of emails. "
        "You specialize in linguistic analysis — you can spot social engineering attempts, "
        "urgency traps, and scam language patterns instantly. You provide clear, "
        "structured reports of what you find."
    ),
    llm=get_fast_llm(),
    allow_delegation=False,
    verbose=False,
)

# ---------------------------------------------------------------------------
# Agent 2: Sender Reputation Analyst (pro model)
# ---------------------------------------------------------------------------

sender_analyst = Agent(
    role="Sender & Header Reputation Analyst",
    goal=(
        "Analyze the sender's email address, domain, and any header-like metadata "
        "for signs of spoofing, typosquatting, or untrustworthy origins. "
        "Flag domains that look like they're impersonating legitimate companies."
    ),
    backstory=(
        "You are a domain intelligence expert. Your specialty is examining email "
        "sender addresses and domains for subtle misspellings, suspicious TLDs, "
        "and patterns commonly used by phishers. You know that scammers often use "
        "domains like 'bank-secure-login.tk' to impersonate real banks."
    ),
    llm=get_pro_llm(),
    allow_delegation=False,
    verbose=False,
)

# ---------------------------------------------------------------------------
# Agent 3: Link & URL Analyzer (rule-based "mock model" via tool)
# ---------------------------------------------------------------------------

link_analyst = Agent(
    role="Link & URL Risk Analyst",
    goal=(
        "Use the LinkAnalysisTool to extract and analyze all URLs in the email. "
        "Report on shortened URLs, IP-based domains, suspicious TLDs, "
        "encoded characters, and any mismatch between display text and actual URLs."
    ),
    backstory=(
        "You are a URL forensics specialist. You never trust a link at face value. "
        "You resolve shortened URLs, decode obfuscated paths, and check every "
        "domain against known risk patterns. Your rule-based engine is deterministic "
        "and catches what LLMs often miss."
    ),
    tools=[link_tool],
    llm=get_fast_llm(),  # minimal LLM needed — the heavy lifting is the tool
    allow_delegation=False,
    verbose=False,
)

# ---------------------------------------------------------------------------
# Agent 4: Final Verdict Judge (pro model)
# ---------------------------------------------------------------------------

final_judge = Agent(
    role="Senior Spam Classification Judge",
    goal=(
        "Review the reports from the Content Analyst, Sender Analyst, and Link Analyst. "
        "Weigh all evidence and produce a definitive classification: spam, ham, or suspicious. "
        "Provide a confidence score (0.0 to 1.0) and clear reasoning for the decision."
    ),
    backstory=(
        "You are the final authority on email classification with 15 years of experience. "
        "You carefully consider all signals from your specialist team before rendering "
        "a verdict. You never jump to conclusions — you weigh the full body of evidence. "
        "You explain your reasoning clearly so users understand why an email was flagged."
    ),
    llm=get_pro_llm(),
    allow_delegation=False,
    verbose=False,
)
