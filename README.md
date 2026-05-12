![Python](https://img.shields.io/badge/Python-3.10-blue)
![Finance](https://img.shields.io/badge/Domain-Behavioral%20Finance-green)
![Status](https://img.shields.io/badge/Status-Complete-success)

# Behavioral Finance + Portfolio Construction Engine

> *"The best portfolio isn't the one with the highest Sharpe ratio. It's the one you'll actually hold through a market crash."*

Most robo-advisors optimize mathematically. This engine optimizes **psychologically** — it builds a portfolio based on your loss aversion, panic threshold, and investment horizon, not just your age or income.

---

## What makes this different?

Traditional portfolio theory treats all investors the same given the same risk-return inputs.

Behavioral portfolio theory says: two investors with identical wealth can need **very different portfolios** because they experience gains and losses differently.

This project applies:

- **Prospect Theory** (Kahneman & Tversky, 1992) — models how losses feel ~2x worse than equivalent gains
- **Personalised Loss Aversion** — your λ (lambda) is calculated from your questionnaire score
- **Behavioral Utility Function** — `U = E(R) - (A/2) · Var(R)` with your personal risk aversion coefficient A
- **Drawdown Tolerance** — maps your panic score to a maximum acceptable portfolio drawdown
- **Profile-driven Allocation** — base allocation adjusted by behavioral nudges, not just a static risk bucket

---

## Quickstart

No external libraries needed. Pure Python 3.

```bash
git clone https://github.com/your-username/behavioral-portfolio.git
cd behavioral-portfolio
python main.py
```

Answer 4 questions. Get your portfolio.

---

## What the questionnaire measures

| Question | Behavioral Concept |
|---|---|
| How you feel when portfolio drops 10% | Loss Aversion |
| Preferred investment type | Risk Tolerance |
| Reaction to a 30% market crash | Panic Sensitivity |
| When you need the money | Investment Horizon |

Each answer is scored 1–5. The engine computes a **composite behavioral score** and maps it to one of four profiles:

| Profile | Composite Score | Equity Weight |
|---|---|---|
| Conservative | < 2.0 | ~20% |
| Balanced | 2.0 – 3.0 | ~40% |
| Growth | 3.0 – 4.0 | ~60% |
| Aggressive Growth | ≥ 4.0 | ~75% |

The base allocation is then adjusted further based on your individual scores — so two "Growth" investors with different panic scores still get different portfolios.

---

## Asset universe

| Asset | Expected Return | Volatility |
|---|---|---|
| Large Cap Equity | 12% | 18% |
| Mid Cap Equity | 15% | 24% |
| Small Cap Equity | 18% | 30% |
| Government Bonds | 6% | 5% |
| Corporate Bonds | 8% | 8% |
| Gold | 7% | 15% |
| Cash / Liquid Funds | 4% | 1% |

*Assumptions based on long-run Indian market estimates. Volatility is simplified (zero correlation assumed). A production system would use a full covariance matrix.*

---

## Sample output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Behavioral Finance + Portfolio Construction Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  What's your name? Arjun

  Hi Arjun! Answer 4 quick questions.

──────────────────────────────────────────────────────────
  Your Behaviorally Optimised Portfolio  —  Arjun
──────────────────────────────────────────────────────────

  Profile              : Growth
  Composite score      : 3.45 / 5.00
  Drawdown tolerance   : up to 19% drop before you'd likely react

  Asset                      Weight   Bar
  ──────────────────────────  ───────  ────────────────────
  Large Cap Equity            28.6%   ██████████████░░░░░░
  Mid Cap Equity              19.0%   █████████░░░░░░░░░░░
  Small Cap Equity             9.5%   ████░░░░░░░░░░░░░░░░
  Government Bonds             9.5%   ████░░░░░░░░░░░░░░░░
  Corporate Bonds              9.5%   ████░░░░░░░░░░░░░░░░
  Gold                        11.4%   █████░░░░░░░░░░░░░░░
  Cash / Liquid Funds          7.6%   ███░░░░░░░░░░░░░░░░░

  ┌─────────────────────────────────────────┐
  │  Expected annual return  :  11.38%      │
  │  Portfolio volatility    :   9.62%      │
  │  Sharpe ratio (approx)   :  0.77        │
  │  Risk-free rate assumed  :  4.00% (G-sec│
  └─────────────────────────────────────────┘
```

---

## Project structure

```
behavioral-portfolio/
│
├── main.py               ← Run this. Takes your input, shows your portfolio.
├── behavioral_utils.py   ← All finance logic and calculations.
└── README.md
```

---

## The math

### Prospect Theory value function

```
         x^α                   if x ≥ 0  (gains)
V(x) = {
         −λ · (−x)^β           if x < 0  (losses)
```

Standard parameters: `α = β = 0.88`, `λ = 2.25` (Tversky & Kahneman, 1992).  
In this engine, λ is personalised: `λ = 1.5 + (loss_aversion_score − 1) × 0.5`

### Utility function

```
U = E(R) − (A/2) · Var(R)
```

Where A (risk aversion coefficient) is derived from your behavioral profile rather than assumed uniform.

---
## Future Improvements

- Monte Carlo portfolio simulations
- Efficient frontier visualization
- Historical market backtesting
- Dynamic covariance matrix estimation
- Black-Litterman allocation model
- Streamlit web interface
- Real-time market data integration
- Machine learning investor clustering
  
## References

- Kahneman, D. & Tversky, A. (1979). *Prospect Theory: An Analysis of Decision under Risk.* Econometrica, 47(2), 263–291.
- Tversky, A. & Kahneman, D. (1992). *Advances in Prospect Theory: Cumulative Representation of Uncertainty.* Journal of Risk and Uncertainty, 5, 297–323.
- Thaler, R. (1980). *Toward a Positive Theory of Consumer Choice.* Journal of Economic Behavior & Organization, 1(1), 39–60.

---

## Author
Dhyey Desai-
Built as a course based project exploring behavioral finance applications in wealth management.
