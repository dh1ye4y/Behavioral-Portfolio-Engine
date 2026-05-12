"""
main.py
--------
Behavioral Finance + Portfolio Construction Engine

Run this file and answer the questionnaire to receive a
personalized investment portfolio based on your psychology —
not just math.

    $ python main.py

No external libraries needed. Pure Python 3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Concepts used:
    • Prospect Theory       (Kahneman & Tversky, 1992)
    • Loss Aversion
    • Behavioral Utility    (Mean-Variance with personal A)
    • Drawdown Tolerance
    • Profile-driven Asset Allocation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from behavioral_utils import (
    build_investor_profile,
    prospect_value_custom,
    utility,
    get_risk_aversion_coefficient,
    drawdown_tolerance,
    construct_portfolio,
    portfolio_expected_return,
    portfolio_volatility,
    max_drawdown,
)


# ─────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────

def banner(text: str):
    width = 56
    print("\n" + "━" * width)
    print(f"  {text}")
    print("━" * width)


def section(title: str):
    print(f"\n{'─' * 56}")
    print(f"  {title}")
    print(f"{'─' * 56}")


def print_portfolio(allocation: dict):
    print(f"\n  {'Asset':<26} {'Weight':>7}   Bar")
    print(f"  {'─'*26}  {'─'*7}   {'─'*20}")
    for asset, weight in allocation.items():
        bar   = "█" * int(weight / 2)
        empty = "░" * (20 - int(weight / 2))
        print(f"  {asset:<26} {weight:>6.1f}%   {bar}{empty}")


# ─────────────────────────────────────────────
# QUESTIONNAIRE
# ─────────────────────────────────────────────

QUESTIONS = [
    {
        "id":   "loss_aversion",
        "text": "How do you feel when your portfolio drops 10% in a month?",
        "options": [
            "Completely unbothered — it's just a number.",
            "Mildly uncomfortable, but I stay the course.",
            "Anxious, and I check my portfolio every day.",
            "I strongly consider moving to safer assets.",
            "I would sell immediately to stop further losses.",
        ],
    },
    {
        "id":   "risk_tolerance",
        "text": "Which type of investment best describes your preference?",
        "options": [
            "Fixed deposits — guaranteed returns, no surprises.",
            "Balanced funds — a mix of equity and debt.",
            "Large cap equity — stable, steady growth.",
            "Mid/small cap — higher growth, higher volatility.",
            "Concentrated bets — I want maximum returns.",
        ],
    },
    {
        "id":   "panic_selling",
        "text": "Markets crash 30% in 3 months (think COVID-2020). What do you do?",
        "options": [
            "Buy more — this is a great opportunity.",
            "Hold everything and wait it out.",
            "Review the portfolio but take no action.",
            "Move some money into safer assets.",
            "Exit entirely and wait for recovery.",
        ],
    },
    {
        "id":   "investment_horizon",
        "text": "When do you plan to use this money?",
        "options": [
            "Within 1 year.",
            "1–3 years.",
            "3–5 years.",
            "5–10 years.",
            "10+ years — long-term wealth creation.",
        ],
    },
]


def ask_question(q: dict, num: int, total: int) -> int:
    """
    Displays a single question with numbered options.
    Returns the selected score (1–5).
    """
    print(f"\n  Question {num}/{total}")
    print(f"\n  {q['text']}\n")
    for i, opt in enumerate(q["options"], start=1):
        print(f"    {i}. {opt}")

    while True:
        try:
            val = int(input("\n  Your answer (1–5): ").strip())
            if 1 <= val <= 5:
                return val
            print("  ⚠  Please enter a number between 1 and 5.")
        except ValueError:
            print("  ⚠  Invalid input. Please enter a number.")


def run_questionnaire(name: str) -> dict:
    """Runs all questions and returns a scores dictionary."""
    print(f"\n  Hi {name}! Answer 4 quick questions.")
    print("  Each answer is on a scale of 1 (low) to 5 (high).\n")

    answers = {}
    total   = len(QUESTIONS)

    for i, q in enumerate(QUESTIONS, start=1):
        score           = ask_question(q, i, total)
        answers[q["id"]] = score
        print(f"  ✓ Noted.\n")

    return answers


# ─────────────────────────────────────────────
# RESULTS SECTIONS
# ─────────────────────────────────────────────

def show_profile(profile: dict, name: str):
    section(f"Behavioral Profile  —  {name}")

    labels = {
        "loss_aversion":     "Loss Aversion     (1=low, 5=high)",
        "risk_tolerance":    "Risk Tolerance    (1=low, 5=high)",
        "panic_score":       "Panic Sensitivity (1=calm, 5=panic)",
        "investment_horizon":"Investment Horizon(1=short, 5=long)",
        "composite_score":   "Composite Score   (out of 5.00)",
        "profile_label":     "Profile Label",
    }
    for key, label in labels.items():
        print(f"  {label:<42}: {profile[key]}")


def show_prospect_theory(profile: dict, name: str):
    section(f"Prospect Theory  —  {name}")

    la = profile["loss_aversion"]
    # Lambda personalised to their score
    lambda_ = 1.5 + (la - 1) * 0.5

    print(f"  Your loss aversion score : {la}/5")
    print(f"  Personalised lambda (λ)  : {lambda_:.2f}")
    print(f"\n  This means losses feel {lambda_:.1f}x worse than equivalent")
    print(f"  gains feel good for you.\n")

    print(f"  {'Scenario':<20} {'Actual':>8}   {'Felt Value':>10}   Note")
    print(f"  {'─'*20}  {'─'*8}   {'─'*10}   {'─'*22}")

    scenarios = [
        ("Gain of  5%",  0.05),
        ("Gain of 15%",  0.15),
        ("Gain of 25%",  0.25),
        ("Loss of  5%", -0.05),
        ("Loss of 15%", -0.15),
        ("Loss of 25%", -0.25),
    ]

    for label, x in scenarios:
        felt = prospect_value_custom(x, la)
        note = "gain" if x > 0 else "LOSS  ← feels bigger"
        print(f"  {label:<20} {x:>+8.0%}   {felt:>+10.3f}   {note}")

    print("\n  ↳ Losses always feel disproportionately worse.")
    print(f"  ↳ At your score, a 15% loss feels as bad as a")
    pos_equiv = abs(prospect_value_custom(-0.15, la))
    # find equivalent positive x: x^0.88 = pos_equiv → x = pos_equiv^(1/0.88)
    equiv_gain = pos_equiv ** (1 / 0.88)
    print(f"    {equiv_gain:.0%} gain feels good. That's the asymmetry.")


def show_utility(profile: dict, name: str):
    section(f"Behavioral Utility Score  —  {name}")

    # Hypothetical annual returns for a diversified portfolio
    sample_returns = [0.12, -0.08, 0.15, 0.04, -0.05,
                      0.18,  0.09, -0.12, 0.20, 0.07]

    ra      = get_risk_aversion_coefficient(profile["profile_label"])
    u_score = utility(sample_returns, ra)
    mean_r  = sum(sample_returns) / len(sample_returns)
    var_r   = sum((r - mean_r) ** 2 for r in sample_returns) / len(sample_returns)

    print(f"  Profile                : {profile['profile_label']}")
    print(f"  Risk aversion coeff (A): {ra}")
    print(f"\n  Sample return series   : {[f'{r:+.0%}' for r in sample_returns]}")
    print(f"\n  Mean return            : {mean_r:.2%}")
    print(f"  Return variance        : {var_r:.4f}")
    print(f"\n  Utility  U = E(R) - (A/2)·Var(R)")
    print(f"           U = {mean_r:.4f} - ({ra}/2)·{var_r:.4f}")
    print(f"           U = {u_score:.4f}")
    print(f"\n  ↳ A higher U means this portfolio suits your risk preference better.")
    print(f"  ↳ Two investors with the same returns get different U scores")
    print(f"    because their A (risk aversion) differs.")


def show_portfolio(profile: dict, name: str) -> dict:
    section(f"Your Behaviorally Optimised Portfolio  —  {name}")

    alloc   = construct_portfolio(profile)
    exp_ret = portfolio_expected_return(alloc)
    vol     = portfolio_volatility(alloc)
    sharpe  = round((exp_ret - 0.04) / vol, 2) if vol > 0 else 0
    dd_lim  = drawdown_tolerance(profile["panic_score"])

    print(f"  Profile              : {profile['profile_label']}")
    print(f"  Composite score      : {profile['composite_score']} / 5.00")
    print(f"  Drawdown tolerance   : up to {dd_lim:.0%} drop before you'd likely react\n")

    print_portfolio(alloc)

    print(f"\n  ┌─────────────────────────────────────────┐")
    print(f"  │  Expected annual return  :  {exp_ret:.2%}        │")
    print(f"  │  Portfolio volatility    :  {vol:.2%}        │")
    print(f"  │  Sharpe ratio (approx)   :  {sharpe}           │")
    print(f"  │  Risk-free rate assumed  :  4.00% (G-sec) │")
    print(f"  └─────────────────────────────────────────┘")

    return alloc


def show_drawdown_demo(profile: dict):
    section("Drawdown Sensitivity")

    # Simulated portfolio values during a correction
    prices = [100, 108, 115, 110, 98, 85, 80, 88, 95, 102, 110]
    dd     = max_drawdown(prices)
    ps     = profile["panic_score"]
    my_tol = drawdown_tolerance(ps)

    print(f"  Simulated NAV path: {prices}")
    print(f"  Maximum drawdown in this period: {dd:.2%}\n")
    print(f"  {'Score':<8} {'Tolerance':>10}   {'Reaction'}")
    print(f"  {'─'*8}  {'─'*10}   {'─'*30}")

    for score in range(1, 6):
        tol     = drawdown_tolerance(score)
        reacts  = abs(dd) > tol
        marker  = "  ← YOU" if score == ps else ""
        verdict = "Would likely panic-sell" if reacts else "Can handle this drawdown"
        icon    = "✗" if reacts else "✓"
        print(f"  {score}/5     {tol:>9.0%}   {icon} {verdict}{marker}")

    if abs(dd) > my_tol:
        print(f"\n  ↳ This portfolio would exceed your comfort zone.")
        print(f"    The engine has already adjusted your allocation")
        print(f"    to reduce drawdown risk accordingly.")
    else:
        print(f"\n  ↳ Your allocation is sized to stay within your")
        print(f"    drawdown tolerance of {my_tol:.0%}.")


def show_explanation():
    section("Why your portfolio looks the way it does")

    print("""
  Traditional portfolio theory asks:
      "What maximises return per unit of risk?"

  Behavioral portfolio theory asks:
      "What maximises return per unit of emotional pain?"

  Two investors. Same wealth. Very different psychologies.
  They get different portfolios — because the best portfolio
  is the one you'll actually hold through a market crash.

  This engine uses three behavioral adjustments on top of
  standard mean-variance optimisation:

    1. Loss Aversion (Prospect Theory)
       Losses hurt ~2x more than gains feel good.
       More loss-averse investors get more gold + bonds.

    2. Panic Sensitivity (Drawdown Tolerance)
       Investors likely to sell in a crash get lower
       equity exposure to avoid triggering that reaction.

    3. Investment Horizon
       Longer horizons can absorb more short-term volatility,
       so the engine allows higher equity weights.

  References:
    • Kahneman & Tversky (1979). Prospect Theory. Econometrica.
    • Tversky & Kahneman (1992). Advances in Prospect Theory.
    • Thaler (1980). Toward a Positive Theory of Consumer Choice.
    """)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    banner("Behavioral Finance + Portfolio Construction Engine")

    print("""
  Most portfolio tools optimise for Sharpe ratio.
  This engine optimises for YOU — your psychology,
  your loss aversion, your panic threshold.

  Answer 4 questions. Get your behavioral portfolio.
    """)

    # Get name
    while True:
        name = input("  What's your name? ").strip()
        if name:
            break
        print("  ⚠  Please enter your name.")

    # Run questionnaire
    answers = run_questionnaire(name)

    # Build profile
    profile = build_investor_profile(answers)

    # Show results
    show_profile(profile, name)
    show_prospect_theory(profile, name)
    show_utility(profile, name)
    show_portfolio(profile, name)
    show_drawdown_demo(profile)
    show_explanation()

    banner(f"Done — {name}'s behavioral portfolio is ready.")
    print(f"\n  Profile   : {profile['profile_label']}")
    print(f"  Score     : {profile['composite_score']} / 5.00")
    print(f"\n  Share this project: github.com/your-username/behavioral-portfolio\n")


if __name__ == "__main__":
    main()
