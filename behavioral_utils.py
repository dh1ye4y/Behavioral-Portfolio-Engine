"""
behavioral_utils.py
--------------------
All behavioral finance calculations used by the portfolio engine.

Concepts:
    - Prospect Theory  (Kahneman & Tversky, 1979)
    - Loss Aversion
    - Behavioral Utility Function
    - Drawdown Sensitivity
    - Profile-driven Asset Allocation
"""

import math


# ─────────────────────────────────────────────
# ASSET UNIVERSE
# Expected return and volatility assumptions
# (simplified; based on long-run Indian market estimates)
# ─────────────────────────────────────────────

ASSET_UNIVERSE = {
    "Large Cap Equity":    {"exp_return": 0.12, "volatility": 0.18},
    "Mid Cap Equity":      {"exp_return": 0.15, "volatility": 0.24},
    "Small Cap Equity":    {"exp_return": 0.18, "volatility": 0.30},
    "Government Bonds":    {"exp_return": 0.06, "volatility": 0.05},
    "Corporate Bonds":     {"exp_return": 0.08, "volatility": 0.08},
    "Gold":                {"exp_return": 0.07, "volatility": 0.15},
    "Cash / Liquid Funds": {"exp_return": 0.04, "volatility": 0.01},
}


# ─────────────────────────────────────────────
# 1. INVESTOR PROFILING
# ─────────────────────────────────────────────

def build_investor_profile(answers: dict) -> dict:
    """
    Converts questionnaire answers into a behavioral investor profile.

    Parameters:
        answers (dict): scores for loss_aversion, risk_tolerance,
                        panic_selling, investment_horizon  (each 1–5)

    Returns:
        dict: composite score, profile label, and individual scores
    """
    la = answers["loss_aversion"]
    rt = answers["risk_tolerance"]
    ps = answers["panic_selling"]
    ih = answers["investment_horizon"]

    # Weighted composite — higher = more aggressive
    composite = (
        (rt  * 0.35) +
        ((6 - la) * 0.30) +   # high loss aversion → lower score
        ((6 - ps) * 0.20) +   # high panic → lower score
        (ih  * 0.15)
    )

    if composite >= 4.0:
        label = "Aggressive Growth"
    elif composite >= 3.0:
        label = "Growth"
    elif composite >= 2.0:
        label = "Balanced"
    else:
        label = "Conservative"

    return {
        "loss_aversion":     la,
        "risk_tolerance":    rt,
        "panic_score":       ps,
        "investment_horizon": ih,
        "composite_score":   round(composite, 2),
        "profile_label":     label,
    }


# ─────────────────────────────────────────────
# 2. PROSPECT THEORY
# ─────────────────────────────────────────────

def prospect_value(x: float, alpha: float = 0.88, beta: float = 0.88,
                   lambda_: float = 2.25) -> float:
    """
    Kahneman & Tversky (1992) value function.

    Gains and losses of the same size feel very different.
    Losses feel ~2.25x worse than equivalent gains feel good.

    Args:
        x       : outcome (positive = gain, negative = loss)
        alpha   : diminishing sensitivity for gains  (default 0.88)
        beta    : diminishing sensitivity for losses (default 0.88)
        lambda_ : loss aversion coefficient          (default 2.25)
    """
    if x >= 0:
        return x ** alpha
    else:
        return -lambda_ * ((-x) ** beta)


def prospect_value_custom(x: float, loss_aversion_score: int) -> float:
    """
    Personalised prospect value — lambda scales with the investor's
    loss aversion score (1–5).

        Score 1 → lambda = 1.5  (mildly loss averse)
        Score 5 → lambda = 3.5  (strongly loss averse)
    """
    lambda_ = 1.5 + (loss_aversion_score - 1) * 0.5
    return prospect_value(x, lambda_=lambda_)


# ─────────────────────────────────────────────
# 3. UTILITY FUNCTION
# ─────────────────────────────────────────────

def utility(returns: list, risk_aversion: float) -> float:
    """
    Mean-variance utility:  U = E(R) - (A/2) * Var(R)

    A higher risk_aversion coefficient penalises variance more,
    reflecting a conservative investor's preference.

    Args:
        returns       : list of periodic returns (decimals)
        risk_aversion : coefficient A (higher = more conservative)
    """
    n       = len(returns)
    mean_r  = sum(returns) / n
    var_r   = sum((r - mean_r) ** 2 for r in returns) / n
    return round(mean_r - (risk_aversion / 2) * var_r, 6)


def get_risk_aversion_coefficient(profile_label: str) -> float:
    """Maps a profile label to a standard risk aversion coefficient."""
    return {
        "Aggressive Growth": 1.0,
        "Growth":            2.0,
        "Balanced":          3.5,
        "Conservative":      5.0,
    }.get(profile_label, 3.0)


# ─────────────────────────────────────────────
# 4. DRAWDOWN
# ─────────────────────────────────────────────

def max_drawdown(prices: list) -> float:
    """
    Maximum drawdown from a price/NAV series.
    Returns a negative decimal, e.g. -0.25 means -25%.
    """
    peak   = prices[0]
    max_dd = 0.0
    for p in prices:
        if p > peak:
            peak = p
        dd = (p - peak) / peak
        if dd < max_dd:
            max_dd = dd
    return round(max_dd, 4)


def drawdown_tolerance(panic_score: int) -> float:
    """
    Converts panic score (1–5) to maximum acceptable drawdown.

        Score 1 (very calm)   → tolerates up to 30% drawdown
        Score 5 (panic-prone) → tolerates only up to  8% drawdown
    """
    return round(0.30 - (panic_score - 1) * 0.055, 3)


# ─────────────────────────────────────────────
# 5. PORTFOLIO CONSTRUCTION
# ─────────────────────────────────────────────

def construct_portfolio(profile: dict) -> dict:
    """
    Builds a behaviorally-adjusted asset allocation.

    Step 1 — Start from a base allocation for the profile label.
    Step 2 — Apply behavioral nudges:
        • High panic score  → cut volatile assets, add cash + govt bonds
        • High loss aversion → cut large cap, add gold + corporate bonds
    Step 3 — Normalise to 100%.

    Returns:
        dict: {asset_name: allocation_percentage}
    """
    label   = profile["profile_label"]
    panic   = profile["panic_score"]
    loss_av = profile["loss_aversion"]

    base = {
        "Aggressive Growth": {
            "Large Cap Equity": 30, "Mid Cap Equity": 25, "Small Cap Equity": 20,
            "Government Bonds":  5, "Corporate Bonds":  5,
            "Gold": 10, "Cash / Liquid Funds":  5,
        },
        "Growth": {
            "Large Cap Equity": 30, "Mid Cap Equity": 20, "Small Cap Equity": 10,
            "Government Bonds": 10, "Corporate Bonds": 10,
            "Gold": 12, "Cash / Liquid Funds":  8,
        },
        "Balanced": {
            "Large Cap Equity": 25, "Mid Cap Equity": 10, "Small Cap Equity":  5,
            "Government Bonds": 20, "Corporate Bonds": 15,
            "Gold": 15, "Cash / Liquid Funds": 10,
        },
        "Conservative": {
            "Large Cap Equity": 15, "Mid Cap Equity":  5, "Small Cap Equity":  0,
            "Government Bonds": 30, "Corporate Bonds": 20,
            "Gold": 15, "Cash / Liquid Funds": 15,
        },
    }

    alloc = base[label].copy()

    # Behavioral nudge 1: panic-prone → de-risk
    if panic >= 4:
        alloc["Small Cap Equity"]    = max(0, alloc["Small Cap Equity"] - 5)
        alloc["Mid Cap Equity"]      = max(0, alloc["Mid Cap Equity"]   - 5)
        alloc["Cash / Liquid Funds"] += 5
        alloc["Government Bonds"]    += 5

    # Behavioral nudge 2: loss-averse → hedge more
    if loss_av >= 4:
        alloc["Large Cap Equity"] = max(0, alloc["Large Cap Equity"] - 5)
        alloc["Gold"]             += 3
        alloc["Corporate Bonds"]  += 2

    # Normalise
    total = sum(alloc.values())
    return {k: round(v / total * 100, 1) for k, v in alloc.items()}


def portfolio_expected_return(allocation: dict) -> float:
    """Weighted expected return of the portfolio."""
    return round(sum(
        (w / 100) * ASSET_UNIVERSE[a]["exp_return"]
        for a, w in allocation.items()
    ), 4)


def portfolio_volatility(allocation: dict) -> float:
    """
    Simplified weighted volatility (assumes zero correlation).
    A real system would use a covariance matrix.
    """
    var = sum(
        ((w / 100) * ASSET_UNIVERSE[a]["volatility"]) ** 2
        for a, w in allocation.items()
    )
    return round(math.sqrt(var), 4)
