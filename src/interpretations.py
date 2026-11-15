"""Company reads for the app. Figures follow the notebook company analysis."""

from __future__ import annotations

GROWTH = {
    "AMD": (
        "Revenue growth accelerated from 13.7% in FY2024 to 34.3% in FY2025. "
        "The FY2025 rate was 20.6 percentage points higher than the FY2024 rate. "
        "Revenue is growing faster, not declining."
    ),
    "Adobe": (
        "Revenue grew 10.5% in FY2025, compared with 10.8% in FY2024. "
        "The rate eased by 0.3 percentage points. Revenue is still growing, and the pace is relatively stable."
    ),
    "Apple": (
        "Revenue grew 6.4% in FY2025, up from 2.0% in FY2024. "
        "The FY2025 growth rate improved by 4.4 percentage points from the FY2024 rate."
    ),
    "CrowdStrike": (
        "Revenue is still growing, and the rate has slowed: 36.3% in FY2024, 29.4% in FY2025, and 21.7% in FY2026. "
        "The slower rate is not a decline in revenue."
    ),
    "Microsoft": (
        "Revenue grew 17.8% in FY2026, up from 14.9% in FY2025. "
        "The FY2026 growth rate rose by 2.9 percentage points from the FY2025 rate. Revenue is still increasing."
    ),
    "NVIDIA": (
        "Revenue grew 65.5% in FY2026, down from 114.2% in FY2025. "
        "The FY2026 growth rate fell by 48.7 percentage points from the FY2025 rate. "
        "Revenue is still growing. The slower rate is a cooldown from an unusually high FY2025, not a decline in revenue."
    ),
}

PROFITABILITY = {
    "AMD": (
        "Gross margin was nearly unchanged, 49.4% in FY2024 and 49.5% in FY2025. "
        "The operating margin rose from 7.4% to 10.7%, and the net income margin rose from 6.4% to 12.5%. "
        "Operating income grew 94.4% in FY2025 after growing 373.8% in FY2024. Operating income is still rising. "
        "The lower FY2025 growth rate is not a decline in operating income. "
        "An operating margin of 10.7% and average-balance ROA of 5.9% are still below Microsoft, Apple, NVIDIA, and Adobe."
    ),
    "Adobe": (
        "Gross margin was 89.3% in FY2025, compared with 89.0% in FY2024. "
        "The operating margin rose from 31.3% to 36.6%, and the net income margin rose from 25.9% to 30.0%."
    ),
    "Apple": (
        "Gross margin rose from 46.2% in FY2024 to 46.9% in FY2025. "
        "The operating margin rose from 31.5% to 32.0%. Operating income grew 8.0% in FY2025. "
        "The net income margin rose from 24.0% to 26.9%. "
        "Net income grew 19.5%, from $93.7 billion in FY2024 to $112.0 billion in FY2025."
    ),
    "CrowdStrike": (
        "Gross margin was 75.2% in FY2024, 75.0% in FY2025, and 74.7% in FY2026. "
        "The operating margin went from -0.6% to -2.9% to -6.1%. "
        "The net income margin went from 2.4% to -0.4% to -3.4%. "
        "Operating and net margins are negative, and both are weaker than in FY2024."
    ),
    "Microsoft": (
        "Gross margin eased from 68.8% in FY2025 to 67.9% in FY2026. "
        "The operating margin rose from 45.6% to 46.8%, and the net income margin rose from 36.1% to 40.3%."
    ),
    "NVIDIA": (
        "Gross margin was 71.1% in FY2026, after 75.0% in FY2025 and 72.7% in FY2024. "
        "The operating margin was 60.4%, after 62.4% in FY2025 and 54.1% in FY2024. "
        "The net income margin was 55.6%, compared with 55.8% in FY2025."
    ),
}

OPERATIONS = {
    "AMD": "Operating expenses fell from 42.0% of revenue in FY2024 to 38.9% in FY2025.",
    "Adobe": (
        "Operating-expense growth was 0.9% in FY2025, against revenue growth of 10.5%. "
        "Operating expenses fell from 57.7% of revenue in FY2024 to 52.6% in FY2025."
    ),
    "Apple": (
        "Operating-expense growth exceeded revenue growth by 1.7 percentage points in FY2025. "
        "Operating expenses were 14.9% of revenue in FY2025, up from 14.7% in FY2024."
    ),
    "CrowdStrike": (
        "Operating expenses were 75.8% of revenue in FY2024, 77.9% in FY2025, and 80.8% in FY2026. "
        "In FY2026, operating-expense growth exceeded revenue growth by 4.5 percentage points."
    ),
    "Microsoft": (
        "Operating expenses were 21.2% of revenue in FY2026, down from 23.2% in FY2025 and 25.1% in FY2024. "
        "In FY2026, revenue growth exceeded operating-expense growth by 10.3 percentage points."
    ),
    "NVIDIA": "Operating expenses fell from 12.6% of revenue in FY2025 to 10.7% in FY2026.",
}

CASH = {
    "AMD": (
        "The operating-cash-flow margin rose from 11.8% in FY2024 to 22.3% in FY2025, "
        "and operating cash flow grew 153.5% in FY2025."
    ),
    "Adobe": (
        "The operating-cash-flow margin rose from 37.5% in FY2024 to 42.2% in FY2025, "
        "and operating cash flow grew 24.5% in FY2025."
    ),
    "Apple": (
        "Operating cash flow fell 5.7% in FY2025, the same year net income grew 19.5%. "
        "The operating-cash-flow margin fell from 30.2% in FY2024 to 26.8% in FY2025. "
        "Cash conversion was 0.995, down from 1.262. Both years are meaningful. "
        "Operating cash flow was about equal to net income in FY2025, after running above it in FY2024."
    ),
    "CrowdStrike": (
        "Operating cash flow stayed positive. The operating-cash-flow margin was 38.2% in FY2024, "
        "34.9% in FY2025, and 33.5% in FY2026. Cash conversion is not meaningful because net income is negative. "
        "The FY2026 net-income growth rate is not a useful read of earnings, because the loss got larger."
    ),
    "Microsoft": (
        "Operating cash flow grew 34.4% in FY2026. "
        "The operating-cash-flow margin rose from 48.3% in FY2025 to 55.1% in FY2026."
    ),
    "NVIDIA": (
        "The operating-cash-flow margin was 47.6% in FY2026, down from 49.1% in FY2025, "
        "and operating cash flow grew 60.3% in FY2026. Cash generation is still strong. "
        "The margin is a little lower than the prior year."
    ),
}

HEALTH = {
    "AMD": (
        "The current ratio improved from 2.62 in FY2024 to 2.85 in FY2025. "
        "Debt-to-equity rose from 0.030 to 0.051. "
        "Liabilities-to-assets rose from 16.8% to 18.1%. AMD does not report total liabilities, "
        "so that ratio uses assets minus equity. "
        "Average-balance ROA rose from 2.4% to 5.9%, and average-balance ROE rose from 2.9% to 7.2%. "
        "The FY2025 average rank was 3.889, the same as Adobe. That comparison uses FY2025 only."
    ),
    "Adobe": (
        "The current ratio fell from 1.068 in FY2024 to 0.996 in FY2025. "
        "A current ratio slightly below 1.0 is a liquidity signal, not by itself a crisis. "
        "Debt-to-equity rose from 0.399 to 0.534, and liabilities-to-assets rose from 53.3% to 60.6%. "
        "Average-balance ROA rose from 18.5% to 23.9%, and average-balance ROE rose from 36.3% to 55.4%. "
        "The FY2025 average rank was 3.889, the same as AMD. That comparison uses FY2025 only."
    ),
    "Apple": (
        "Debt-to-equity fell from 1.70 in FY2024 to 1.23 in FY2025, and liabilities-to-assets fell from 84.4% to 79.5%. "
        "The current ratio rose from 0.867 to 0.893 and remained below 1. "
        "Average-balance ROA rose from 26.1% to 30.9%. Average-balance ROE rose from 157.4% to 171.4%. "
        "The high ROE is inflated by buybacks, which shrink equity. "
        "The FY2025 average rank was 4.000. In FY2025, Apple ranked 6th on revenue growth, "
        "6th on the current ratio, and 6th on debt-to-equity, and 1st on ROE."
    ),
    "CrowdStrike": (
        "The current ratio was 1.764 in FY2024, 1.766 in FY2025, and 1.773 in FY2026. "
        "Debt-to-equity fell from 0.322 in FY2024 to 0.227 in FY2025 to 0.168 in FY2026. "
        "Average-balance ROA went from 1.2% in FY2024 to -0.2% in FY2025 to -1.6% in FY2026. "
        "The FY2025 average rank was 4.889. That comparison uses FY2025 only."
    ),
    "Microsoft": (
        "The balance sheet stayed conservative and leverage eased. "
        "The current ratio was 1.353 in FY2025 and 1.230 in FY2026. "
        "Debt-to-equity fell from 0.126 to 0.091, and liabilities-to-assets fell from 44.5% to 41.7%. "
        "Average-balance ROA rose from 18.0% to 19.4%, and average-balance ROE rose from 33.3% to 34.0%. "
        "The FY2025 average rank was 3.111. That comparison uses FY2025 only."
    ),
    "NVIDIA": (
        "The current ratio fell from 4.440 in FY2025 to 3.905 in FY2026 and remains high. "
        "Debt-to-equity fell from 0.107 to 0.054, and liabilities-to-assets fell from 28.9% to 23.9%. "
        "Average-balance ROA fell from 82.2% to 75.4%. Ending-balance ROA fell from 65.3% to 58.1%. "
        "Those two ROA figures use different denominators. The primary figure is the average-balance return. "
        "Average-balance ROE fell from 119.2% to 101.5%. "
        "The FY2025 average rank was 1.222. That comparison uses FY2025 only."
    ),
}

EXECUTIVE = {
    "AMD": {
        "Growth": GROWTH["AMD"],
        "Profitability": PROFITABILITY["AMD"],
        "Operations": OPERATIONS["AMD"],
        "Cash Flow": CASH["AMD"],
        "Financial Health": HEALTH["AMD"],
        "Management Attention": (
            "Growth, margins, operating cash flow, and returns improved in FY2025. "
            "Liabilities-to-assets rose from 16.8% to 18.1%, using assets minus equity. "
            "Investigate what accompanied the acceleration, including that rise. "
            "The results do not establish the cause."
        ),
    },
    "Adobe": {
        "Growth": GROWTH["Adobe"],
        "Profitability": PROFITABILITY["Adobe"],
        "Operations": OPERATIONS["Adobe"],
        "Cash Flow": CASH["Adobe"],
        "Financial Health": HEALTH["Adobe"],
        "Management Attention": (
            "Profit and operating cash flow improved in FY2025. Liquidity and leverage moved the other way. "
            "The current ratio fell from 1.068 to 0.996. "
            "Investigate what changed in current assets, current liabilities, and debt. "
            "The results do not establish the cause."
        ),
    },
    "Apple": {
        "Growth": GROWTH["Apple"],
        "Profitability": PROFITABILITY["Apple"],
        "Operations": OPERATIONS["Apple"],
        "Cash Flow": CASH["Apple"],
        "Financial Health": HEALTH["Apple"],
        "Management Attention": (
            "Net income grew 19.5% in FY2025 while operating cash flow fell 5.7%. "
            "Debt-to-equity improved, and the current ratio stayed below 1. "
            "Investigate the gap between earnings growth and the decline in operating cash flow, "
            "and what leaves the current ratio below 1. The results do not establish the cause."
        ),
    },
    "CrowdStrike": {
        "Growth": GROWTH["CrowdStrike"],
        "Profitability": PROFITABILITY["CrowdStrike"],
        "Operations": OPERATIONS["CrowdStrike"],
        "Cash Flow": CASH["CrowdStrike"],
        "Financial Health": HEALTH["CrowdStrike"],
        "Management Attention": (
            "Operating expenses reached 80.8% of revenue in FY2026, and the operating margin was -6.1%. "
            "Revenue was still growing, and operating cash flow stayed positive. "
            "Investigate which operating costs grew faster than revenue. "
            "The results do not name those costs."
        ),
    },
    "Microsoft": {
        "Growth": GROWTH["Microsoft"],
        "Profitability": PROFITABILITY["Microsoft"],
        "Operations": OPERATIONS["Microsoft"],
        "Cash Flow": CASH["Microsoft"],
        "Financial Health": HEALTH["Microsoft"],
        "Management Attention": (
            "Gross margin eased from 68.8% to 67.9% in FY2026, while the operating margin rose from 45.6% to 46.8% "
            "and operating cash flow grew 34.4%. "
            "Investigate what moved gross margin down and whether the lower expense ratio offset it. "
            "The results do not establish that cause."
        ),
    },
    "NVIDIA": {
        "Growth": GROWTH["NVIDIA"],
        "Profitability": PROFITABILITY["NVIDIA"],
        "Operations": OPERATIONS["NVIDIA"],
        "Cash Flow": CASH["NVIDIA"],
        "Financial Health": HEALTH["NVIDIA"],
        "Management Attention": (
            "FY2026 revenue growth of 65.5% is slower than 114.2% in FY2025, and revenue is still rising. "
            "Gross margin fell from 75.0% to 71.1%. Operating profit and operating cash flow are still strong. "
            "Investigate whether the gross margin, the operating margin, and the operating-cash-flow margin "
            "hold if revenue growth continues to cool. The results do not show that those margins will fall further."
        ),
    },
}

CONCLUSION = (
    "NVIDIA's FY2025 average rank was 1.222 and Microsoft's was 3.111. "
    "A lower average rank is stronger, and the rank is context rather than a single verdict. "
    "NVIDIA's FY2026 revenue growth of 65.5% is slower than 114.2% in FY2025, and revenue is still rising. "
    "Gross margin fell from 75.0% in FY2025 to 71.1% in FY2026, while the operating margin was still 60.4% "
    "and the operating-cash-flow margin was 47.6%. "
    "Microsoft's revenue growth was 17.8% in FY2026, up from 14.9% in FY2025. "
    "Gross margin eased from 68.8% to 67.9%, while the operating margin rose from 45.6% to 46.8% "
    "and the operating-cash-flow margin rose from 48.3% to 55.1%.\n\n"
    "AMD and Adobe each have an FY2025 average rank of 3.889, with different latest-year patterns. "
    "AMD's revenue growth accelerated from 13.7% in FY2024 to 34.3% in FY2025, the operating margin rose "
    "from 7.4% to 10.7%, and operating cash flow grew 153.5%. Liabilities-to-assets rose from 16.8% to 18.1%, "
    "using imputed liabilities. Adobe's operating margin rose from 31.3% in FY2024 to 36.6% in FY2025 "
    "and operating expenses fell from 57.7% of revenue to 52.6%, while the current ratio fell from 1.068 "
    "to 0.996 and debt-to-equity rose from 0.399 to 0.534.\n\n"
    "Apple's FY2025 revenue growth was 6.4%. Net income grew 19.5%, from $93.7 billion in FY2024 to "
    "$112.0 billion in FY2025, while operating cash flow fell 5.7% and cash conversion fell from 1.262 to 0.995. "
    "Debt-to-equity fell from 1.70 to 1.23, and the current ratio was 0.893. "
    "FY2025 average-balance ROE was 171.4%, inflated by buybacks that shrink equity. "
    "Apple's FY2025 average rank was 4.000. In that year it ranked 6th on revenue growth and 1st on ROE.\n\n"
    "CrowdStrike's revenue is still growing, at 21.7% in FY2026 after 29.4% in FY2025 and 36.3% in FY2024. "
    "Gross margin was 74.7% in FY2026. The operating margin moved from -0.6% in FY2024 to -6.1% in FY2026, "
    "and operating expenses rose from 75.8% of revenue to 80.8%. Operating cash flow stayed positive, "
    "with a FY2026 margin of 33.5%. Its FY2025 average rank was 4.889.\n\n"
    "Slower growth is not falling revenue. NVIDIA and CrowdStrike both grew more slowly in the latest year "
    "and still grew. The sharper differences are elsewhere. Microsoft's gross margin eased while its operating "
    "margin and operating cash flow improved. Apple's earnings rose while operating cash flow fell. "
    "Adobe's margins improved while its current ratio slipped below 1 and leverage rose. "
    "CrowdStrike's gross margin held near 75% while the operating margin became more negative and operating "
    "cash flow stayed positive."
)

PEER = (
    "The FY2025 average rank compares the six companies on nine metrics. "
    "A lower average is stronger on those metrics. NVIDIA's average rank was 1.222 and CrowdStrike's was 4.889. "
    "AMD and Adobe tied at 3.889. "
    "These companies operate in different technology subsectors and do not share one business model. "
    "The average is a descriptive comparison, not a ranking of which company is best."
)

ALERTS = [
    {
        "company": "Microsoft",
        "area": "Profitability",
        "kind": "mixed",
        "signal": (
            "Gross margin eased from 68.8% in FY2025 to 67.9% in FY2026. "
            "The operating margin rose from 45.6% to 46.8%, and operating expenses fell from 23.2% of revenue to 21.2%. "
            "Operating cash flow grew 34.4%, and the operating-cash-flow margin rose from 48.3% to 55.1%."
        ),
        "trend": "Operating profit and operating cash flow are improving. Gross margin is not.",
        "why": (
            "The higher operating margin depends on the lower expense ratio, not on a higher gross margin."
        ),
        "attention": (
            "Investigate what moved gross margin down in FY2026 and whether the lower expense ratio is what offset it. "
            "The results do not establish that cause."
        ),
    },
    {
        "company": "Apple",
        "area": "Cash Flow",
        "kind": "investigate",
        "signal": (
            "Net income grew 19.5% in FY2025, from $93.7 billion to $112.0 billion, while operating cash flow fell 5.7%. "
            "The operating-cash-flow margin fell from 30.2% to 26.8%, and cash conversion fell from 1.262 to 0.995. "
            "The current ratio rose from 0.867 to 0.893 and stayed below 1. Debt-to-equity improved from 1.70 to 1.23."
        ),
        "trend": "Earnings and leverage improved. Operating cash flow weakened.",
        "why": "Reported earnings and cash generation moved in opposite directions in the same year.",
        "attention": (
            "Investigate the gap between FY2025 net-income growth and the decline in operating cash flow, "
            "and what leaves the current ratio below 1. The results do not establish the cause."
        ),
    },
    {
        "company": "NVIDIA",
        "area": "Growth",
        "kind": "mixed",
        "signal": (
            "Revenue grew 65.5% in FY2026. The growth rate was 48.7 percentage points lower than the 114.2% rate in FY2025. "
            "That is slower growth, not a decline in revenue. Gross margin fell from 75.0% to 71.1%. "
            "The operating margin was 60.4%, and the operating-cash-flow margin was 47.6%, with operating cash flow up 60.3%."
        ),
        "trend": "Revenue growth is decelerating, and gross margin is lower than in FY2025. Operating profit and operating cash flow are still strong.",
        "why": "Gross margin is already lower than in FY2025. Operating profit and operating cash flow are still strong.",
        "attention": (
            "Investigate whether the gross margin, the operating margin, and the operating-cash-flow margin hold "
            "if revenue growth continues to cool. The results do not show that those margins will fall further."
        ),
    },
    {
        "company": "Adobe",
        "area": "Financial Health",
        "kind": "mixed",
        "signal": (
            "The operating margin rose from 31.3% in FY2024 to 36.6% in FY2025, and the operating-cash-flow margin "
            "rose from 37.5% to 42.2%. Operating expenses fell from 57.7% of revenue to 52.6%. "
            "The current ratio fell from 1.068 to 0.996, debt-to-equity rose from 0.399 to 0.534, "
            "and liabilities-to-assets rose from 53.3% to 60.6%."
        ),
        "trend": "Profit and operating cash flow are improving. Liquidity and leverage are deteriorating.",
        "why": "A current ratio slightly below 1.0 is a liquidity signal, not by itself a crisis. Leverage rose in the same year.",
        "attention": (
            "Investigate what changed in current assets, current liabilities, and debt. "
            "The results do not establish the cause."
        ),
    },
    {
        "company": "AMD",
        "area": "Financial Health",
        "kind": "mixed",
        "signal": (
            "Revenue growth accelerated from 13.7% in FY2024 to 34.3% in FY2025. "
            "The operating margin rose from 7.4% to 10.7%, the operating-cash-flow margin rose from 11.8% to 22.3%, "
            "and average-balance ROA rose from 2.4% to 5.9%. Liabilities-to-assets rose from 16.8% to 18.1%."
        ),
        "trend": "Growth, margins, operating cash flow, and returns are improving. Liabilities-to-assets moved the other way, from a low base.",
        "why": (
            "The liabilities-to-assets ratio uses assets minus equity, because AMD does not report total liabilities. "
            "Operating profitability and returns improved, and at 10.7% and 5.9% they are still below the other profitable companies in this set."
        ),
        "attention": (
            "Investigate what accompanied the FY2025 acceleration, including the rise in liabilities-to-assets. "
            "The results do not establish the cause of that rise."
        ),
    },
    {
        "company": "CrowdStrike",
        "area": "Operations",
        "kind": "investigate",
        "signal": (
            "Operating expenses rose from 75.8% of revenue in FY2024 to 77.9% in FY2025 and 80.8% in FY2026. "
            "In FY2026, operating-expense growth exceeded revenue growth by 4.5 percentage points. "
            "The operating margin went from -0.6% in FY2024 to -6.1% in FY2026. "
            "Revenue still grew 21.7%. Operating cash flow stayed positive, and the operating-cash-flow margin eased from 34.9% to 33.5%."
        ),
        "trend": "Revenue growth is slowing and still positive. Profitability is deteriorating. Operating cash flow stayed positive.",
        "why": "This is not a finding that operating cash flow turned negative. The operating loss is wider because costs took a larger share of revenue.",
        "attention": (
            "Investigate which operating costs grew faster than revenue. "
            "The results do not name those costs or establish why the gap opened."
        ),
    },
]


def notes_for(mapping: dict[str, str], company: str) -> str:
    if company == "All Companies":
        return "\n\n".join(mapping[name] for name in mapping)
    return mapping.get(company, "No interpretation is recorded for this company.")


def alerts_for(company: str) -> list[dict]:
    if company == "All Companies":
        return ALERTS
    return [a for a in ALERTS if a["company"] == company]
