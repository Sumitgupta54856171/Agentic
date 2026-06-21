"""
Sample test emails — 3 spam examples and 2 legitimate (ham) examples.
Each includes subject, sender, and body so agents have full context.
"""

from dataclasses import dataclass


@dataclass
class Email:
    subject: str
    sender: str
    body: str
    expected: str  # "spam" or "ham"


# ---------------------------------------------------------------------------
# SPAM EMAILS
# ---------------------------------------------------------------------------

spam_prize = Email(
    subject="YOU WON $10,000,000!!! CLAIM YOUR PRIZE NOW!!!",
    sender="claims-department@prize-winner.xyz",
    body="""
CONGRATULATIONS!!!

You have been selected as the GRAND PRIZE winner of our annual international lottery!!!
You have won $10,000,000 USD!!!

To claim your prize, you need to verify your identity immediately by clicking the link below:
[Verify Now](http://claim-prize.xyz/verify?id=12345&ref=spam)

Please provide your bank details for the wire transfer.
This offer expires in 24 hours!!! ACT NOW!!!

Warm regards,
Sir Richard Claim
Claims Department
""",
    expected="spam",
)

spam_phishing = Email(
    subject="URGENT: Your account has been compromised — verify immediately",
    sender="security@bank-secure-login.tk",
    body="""
Dear valued customer,

We detected suspicious activity on your account. For your security,
we have temporarily limited access to your account.

To restore full access, you must verify your credentials immediately:
[Click here to secure your account](http://bank-secure-login.tk/verify?token=abc123)

If you do not verify within 24 hours, your account will be permanently closed.

This is an automated security message. Do not reply to this email.

Thank you,
Bank Security Team
""",
    expected="spam",
)

spam_shortener = Email(
    subject="Exclusive Deal Just For You!!!",
    sender="marketing@deals4u.tk",
    body="""
Hey there,

Don't miss out on this EXCLUSIVE opportunity!!!

For a limited time only, you can get:
- 🎁 FREE iPhone 15 Pro
- 🎁 $500 Amazon Gift Card
- 🎁 Premium VPN Subscription (Lifetime)

All absolutely FREE!!! Just confirm your shipping details here:
[Get My Free Stuff](http://bit.ly/free-stuff-4u)

But hurry!!! This offer ends soon!!!

To unsubscribe, visit: [Unsubscribe](http://bit.ly/unsub-me)

Best regards,
Mike
""",
    expected="spam",
)

# ---------------------------------------------------------------------------
# HAM (LEGITIMATE) EMAILS
# ---------------------------------------------------------------------------

ham_meeting = Email(
    subject="Meeting agenda for Friday — Q2 review",
    sender="alice.johnson@company.com",
    body="""
Hi team,

Here's the agenda for our Q2 review meeting this Friday at 2pm:

1. Q2 results overview (15 min)
2. Engineering updates (20 min)
3. Marketing roadmap (15 min)
4. Q&A / open discussion (10 min)

Please review the attached report before the meeting:
[Q2 Report](https://drive.company.com/reports/q2-2026)

Let me know if you'd like to add anything to the agenda.

Best,
Alice
""",
    expected="ham",
)

ham_newsletter = Email(
    subject="Your weekly dev newsletter — Issue #42",
    sender="newsletter@devdigest.com",
    body="""""
Hi there,

Here's what's new in the dev world this week:

🐍 Python 3.14 alpha released — check out the new pattern matching features
🦀 Rust gains native async support in embedded targets
📦 Docker introduces rootless mode by default

Featured article:
[Understanding WebAssembly Components](https://devdigest.com/articles/webassembly-components)

Thanks for reading!
— The DevDigest Team

If you no longer wish to receive these emails, you can update your preferences here:
[Manage Preferences](https://devdigest.com/preferences)
""",
    expected="ham",
)

ham_recruiter = Email(
    subject="Exciting opportunity at TechCorp Inc.",
    sender="hiring@techcorp.com",
    body="""
Hi,

I came across your profile and was impressed by your experience.
We have a Senior Software Engineer role open at TechCorp that I think
would be a great fit.

TechCorp is a well-established SaaS company with 500+ employees.
The role is fully remote with competitive compensation.

If you're interested, here's the full job description:
[Senior Software Engineer - TechCorp](https://techcorp.com/careers/senior-swe)

Let me know if you'd like to set up a 15-min introductory call!

Best regards,
Sarah Chen
Technical Recruiter, TechCorp Inc.
""",
    expected="ham",
)


all_emails = [spam_prize, spam_phishing, spam_shortener, ham_meeting, ham_newsletter, ham_recruiter]
