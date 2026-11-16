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
            "Revenue growth, operating margin, and operating cash flow all improved in FY2025. "
            "The operating margin is 10.7%, up from 7.4%, and still well below the other profitable companies in this set. "
            "Management should see whether growth keeps lifting operating margin, "
            "and look at expense mix and product-level profit before changing costs."
        ),
    },
    "Adobe": {
        "Growth": GROWTH["Adobe"],
        "Profitability": PROFITABILITY["Adobe"],
        "Operations": OPERATIONS["Adobe"],
        "Cash Flow": CASH["Adobe"],
        "Financial Health": HEALTH["Adobe"],
        "Management Attention": (
            "Operating margin rose from 31.3% to 36.6% because expenses grew 0.9% against revenue growth of 10.5%. "
            "In the same year the current ratio fell from 1.068 to 0.996 and debt-to-equity rose from 0.399 to 0.534. "
            "A current ratio just under 1 is a liquidity signal, not evidence of distress. "
            "Management should check whether the expense ratio can hold, and review current liabilities, cash, and debt."
        ),
    },
    "Apple": {
        "Growth": GROWTH["Apple"],
        "Profitability": PROFITABILITY["Apple"],
        "Operations": OPERATIONS["Apple"],
        "Cash Flow": CASH["Apple"],
        "Financial Health": HEALTH["Apple"],
        "Management Attention": (
            "Net income grew 19.5% in FY2025, from $93.7 billion to $112.0 billion, while operating cash flow fell 5.7%. "
            "Cash conversion fell from 1.262 to 0.995. "
            "Management should review the bridge from net income to operating cash flow, including working capital and non-cash adjustments. "
            "The statements do not show which account caused the decline."
        ),
    },
    "CrowdStrike": {
        "Growth": GROWTH["CrowdStrike"],
        "Profitability": PROFITABILITY["CrowdStrike"],
        "Operations": OPERATIONS["CrowdStrike"],
        "Cash Flow": CASH["CrowdStrike"],
        "Financial Health": HEALTH["CrowdStrike"],
        "Management Attention": (
            "The operating loss widened from about $116.4 million to $293.3 million, and the operating margin fell from -2.9% to -6.1%. "
            "Revenue still grew 21.7%, and operating cash flow stayed positive. "
            "Positive operating cash flow is not operating profit. "
            "Management should find which costs grew faster than revenue, and read the cash result next to the operating loss."
        ),
    },
    "Microsoft": {
        "Growth": GROWTH["Microsoft"],
        "Profitability": PROFITABILITY["Microsoft"],
        "Operations": OPERATIONS["Microsoft"],
        "Cash Flow": CASH["Microsoft"],
        "Financial Health": HEALTH["Microsoft"],
        "Management Attention": (
            "Operating margin rose from 45.6% to 46.8% and the operating-cash-flow margin rose from 48.3% to 55.1%, "
            "while gross margin eased from 68.8% to 67.9%. "
            "The operating-margin gain came from expenses growing slower than revenue, not from a higher gross margin. "
            "Management should find what moved gross margin and whether the lower expense ratio can continue as the company grows."
        ),
    },
    "NVIDIA": {
        "Growth": GROWTH["NVIDIA"],
        "Profitability": PROFITABILITY["NVIDIA"],
        "Operations": OPERATIONS["NVIDIA"],
        "Cash Flow": CASH["NVIDIA"],
        "Financial Health": HEALTH["NVIDIA"],
        "Management Attention": (
            "Revenue grew 65.5% in FY2026, down from 114.2% in FY2025. Revenue is still rising. "
            "Gross margin fell from 75.0% to 71.1%, and the operating margin was still 60.4%. "
            "Slower growth is not weaker demand unless volume or price evidence says so. "
            "Management should judge whether these margins hold as growth becomes less extreme."
        ),
    },
}

CONCLUSION = (
    "Revenue growth does not settle this comparison. NVIDIA grew 65.5% in FY2026 and CrowdStrike grew 21.7%, "
    "and both grew more slowly than the year before. Microsoft grew faster, at 17.8%. "
    "The sharper differences are whether growth is showing up in operating profit, "
    "whether expenses are growing slower than revenue, and whether earnings and operating cash move together.\n\n"
    "NVIDIA still converts 60.4% of revenue into operating profit, with operating cash flow up 60.3%, "
    "even though gross margin fell from 75.0% to 71.1%. "
    "Microsoft raised its operating margin from 45.6% to 46.8% and its operating-cash-flow margin from 48.3% to 55.1% "
    "while gross margin eased from 68.8% to 67.9%. The operating-margin gain came from slower expense growth, "
    "not from a higher gross margin. "
    "Adobe did the same kind of thing on a smaller growth rate: expenses grew 0.9% against revenue growth of 10.5%, "
    "and the operating margin rose from 31.3% to 36.6%.\n\n"
    "AMD's revenue growth accelerated from 13.7% to 34.3%, the operating margin rose from 7.4% to 10.7%, "
    "and operating cash flow grew 153.5%. That is improvement from a lower profit level. "
    "Apple's net income grew 19.5%, from $93.7 billion to $112.0 billion, while operating cash flow fell 5.7% "
    "and cash conversion fell from 1.262 to 0.995. "
    "CrowdStrike is still growing and still producing operating cash flow, and the operating loss widened "
    "from about $116.4 million to $293.3 million. Positive operating cash flow is not operating profit.\n\n"
    "The FY2025 average ranks, from 1.222 for NVIDIA to 4.889 for CrowdStrike, are context on nine metrics. "
    "They are not the management conclusion. Adobe's profit improved in the same year its current ratio "
    "moved from 1.068 to 0.996. A current ratio just under 1 is a liquidity signal, not evidence of distress. "
    "The companies also do not share a fiscal calendar, so FY2025 is a common label, not a common set of months."
)

ALERTS = [
    {
        "company": "Microsoft",
        "area": "Operating efficiency",
        "kind": "mixed",
        "signal": (
            "Revenue growth was 17.8% in FY2026, up from 14.9%. Gross margin eased from 68.8% to 67.9%. "
            "Operating margin rose from 45.6% to 46.8%, and operating expenses grew 7.4%. "
            "Operating cash flow grew 34.4%, and the operating-cash-flow margin rose from 48.3% to 55.1%."
        ),
        "trend": "Operating profit and cash generation improved. Gross margin eased.",
        "why": "The higher operating margin came from expenses growing slower than revenue, not from a higher gross margin.",
        "attention": (
            "Find what moved gross margin, and whether the lower expense ratio can continue as the company grows. "
            "The company-year totals do not name the product or cost line."
        ),
        "monitor": "Gross margin, operating expense / revenue, operating margin, and operating-cash-flow margin.",
    },
    {
        "company": "Apple",
        "area": "Earnings and cash",
        "kind": "investigate",
        "signal": (
            "Net income grew 19.5% in FY2025, from $93.7 billion to $112.0 billion, while operating cash flow fell 5.7%. "
            "The operating-cash-flow margin fell from 30.2% to 26.8%, and cash conversion fell from 1.262 to 0.995. "
            "The current ratio was 0.893."
        ),
        "trend": "Earnings improved. Operating cash flow declined. The current ratio stayed below 1.",
        "why": "A higher net income figure is not the same as more cash from operations. Cash conversion near 1.0 can be reasonable. The issue is that it fell in the year earnings grew.",
        "attention": (
            "Review the bridge from net income to operating cash flow, including working capital and non-cash adjustments. "
            "Do not assign the decline to receivables, inventory, or payables until those lines are in hand."
        ),
        "monitor": "Net income growth, operating cash flow growth, cash conversion, and the current ratio.",
    },
    {
        "company": "NVIDIA",
        "area": "Growth and margins",
        "kind": "mixed",
        "signal": (
            "Revenue grew 65.5% in FY2026, down from 114.2% in FY2025. That is slower growth, not a decline in revenue. "
            "Gross margin fell from 75.0% to 71.1%. The operating margin was 60.4%. "
            "Operating expenses grew 40.7%, and operating cash flow grew 60.3%."
        ),
        "trend": "Growth and gross margin cooled from an unusually strong FY2025. Operating profit and operating cash flow are still strong.",
        "why": "High growth and high margins both eased. Slower growth is not, by itself, evidence of weaker demand.",
        "attention": (
            "Judge whether gross margin, operating margin, and the operating-cash-flow margin hold as growth becomes less extreme. "
            "Compare FY2026 with a more normal growth rate, not only with 114.2%."
        ),
        "monitor": "Revenue growth, gross margin, operating margin, and operating-cash-flow margin.",
    },
    {
        "company": "Adobe",
        "area": "Efficiency and liquidity",
        "kind": "mixed",
        "signal": (
            "Operating margin rose from 31.3% to 36.6%. Operating expenses grew 0.9% against revenue growth of 10.5%, "
            "and fell from 57.7% of revenue to 52.6%. The operating-cash-flow margin rose from 37.5% to 42.2%. "
            "The current ratio fell from 1.068 to 0.996, and debt-to-equity rose from 0.399 to 0.534."
        ),
        "trend": "Profit and operating cash flow improved. The current ratio slipped below 1 and debt-to-equity rose.",
        "why": "The operating improvement came from very slow expense growth. A current ratio just under 1.0 is a liquidity signal, not proof of distress.",
        "attention": (
            "Check whether the expense ratio can stay near 52.6% of revenue, and review current liabilities, cash, and debt. "
            "The ratios show the direction. They do not name the accounts."
        ),
        "monitor": "Operating margin, operating expense / revenue, operating-cash-flow margin, current ratio, and debt-to-equity.",
    },
    {
        "company": "AMD",
        "area": "Growth into profit",
        "kind": "mixed",
        "signal": (
            "Revenue growth accelerated from 13.7% to 34.3%. Operating margin rose from 7.4% to 10.7%, "
            "and operating income grew 94.4%. Operating cash flow grew 153.5%, "
            "and the operating-cash-flow margin rose from 11.8% to 22.3%."
        ),
        "trend": "Revenue growth, operating margin, and operating cash flow improved. Gross margin was almost flat, 49.4% then 49.5%.",
        "why": "Faster growth is turning into higher operating profit and cash. A 10.7% operating margin is still well below the other profitable companies in this set.",
        "attention": (
            "See whether growth keeps lifting operating margin. "
            "Look at expense composition and product-level profit before recommending a cost change."
        ),
        "monitor": "Revenue growth, operating margin, operating expense / revenue, and operating-cash-flow margin.",
    },
    {
        "company": "CrowdStrike",
        "area": "Operating loss",
        "kind": "investigate",
        "signal": (
            "Operating margin fell from -2.9% to -6.1%. Operating expenses grew 26.2% against revenue growth of 21.7% "
            "and reached 80.8% of revenue. The operating loss widened from about $116.4 million to $293.3 million. "
            "Operating cash flow still grew 16.7%, with a margin of 33.5%."
        ),
        "trend": "Revenue is still growing. The operating loss widened. Operating cash flow stayed positive.",
        "why": "Positive operating cash flow does not mean the company is profitable. GAAP operating income is a loss, and spending grew faster than revenue.",
        "attention": (
            "Identify which operating costs grew faster than revenue, and read operating cash flow next to the operating loss. "
            "Stock-based compensation may be part of the cash-flow bridge. It is not in this dataset, so it is not an established cause."
        ),
        "monitor": "Revenue growth, operating margin, operating expense / revenue, and operating-cash-flow margin.",
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
