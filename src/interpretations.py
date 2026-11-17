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
        "The operating loss widened from $116.4 million to $293.3 million, "
        "and the net loss widened from $15.2 million to $162.5 million. "
        "The calculated net-income growth rate is about 966%. Both years are losses and the loss got larger, "
        "so that percent is not growth. The figure shown for the year is loss widened."
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
    "AMD": (
        "Operating expenses grew 24.3% in FY2025, behind revenue growth of 34.3%, "
        "and fell from 42.0% of revenue in FY2024 to 38.9% in FY2025."
    ),
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
        "In FY2026, operating-expense growth exceeded revenue growth by 4.5 percentage points. "
        "Research and development rose from $1.076 billion to $1.385 billion, "
        "and general and administrative rose from $481 million to $670 million. Both grew faster than revenue. "
        "Sales and marketing rose from $1.523 billion to $1.831 billion, or 20.2%, a little slower than revenue."
    ),
    "Microsoft": (
        "Operating expenses grew 7.4% in FY2026, against revenue growth of 17.8%. "
        "They were 21.2% of revenue, down from 23.2% in FY2025 and 25.1% in FY2024. "
        "Revenue growth exceeded operating-expense growth by 10.3 percentage points."
    ),
    "NVIDIA": (
        "Operating expenses grew 40.7% in FY2026, slower than revenue growth of 65.5%, "
        "and fell from 12.6% of revenue in FY2025 to 10.7% in FY2026."
    ),
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
        "Operating cash flow fell 5.7% in FY2025, from $118.3 billion to $111.5 billion, "
        "the same year net income grew 19.5%. "
        "The operating-cash-flow margin fell from 30.2% in FY2024 to 26.8% in FY2025. "
        "Cash conversion was 0.995, down from 1.262. Both years are meaningful. "
        "Receivables rose by $6.4 billion, inventory fell by $1.6 billion, and payables rose by $0.9 billion. "
        "Together those year-end changes are a net use of about $3.9 billion, versus a net source of about $1.5 billion in FY2024. "
        "Stock-based compensation rose from $11.7 billion to $12.9 billion, and depreciation and amortization rose from $11.4 billion to $11.7 billion. "
        "Those add-backs increased, so they do not explain the cash decline. "
        "Net income plus the two add-backs and the $3.9 billion net use is about $21.2 billion above FY2025 operating cash flow. "
        "The same sum was within $107 million of operating cash flow in FY2024. "
        "Other current liabilities rose about $19.5 billion in FY2024 and fell about $11.9 billion in FY2025. "
        "Putting that change into the same sum does not close FY2025, and it opens a large gap in FY2024, "
        "the year the smaller set of items had nearly matched. "
        "Year-end balances are not the cash-flow statement's operating lines, so none of these accounts can be named as the cause."
    ),
    "CrowdStrike": (
        "Operating cash flow stayed positive and grew 16.7%, to $1.612 billion. "
        "The operating-cash-flow margin was 38.2% in FY2024, 34.9% in FY2025, and 33.5% in FY2026. "
        "Cash conversion is not meaningful because net income is negative. "
        "The net loss widened from $15.2 million to $162.5 million. "
        "The calculated net-income growth rate is about 966%. Both years are losses and the loss got larger, "
        "so that percent is not growth. The figure shown for the year is loss widened. "
        "Stock-based compensation was $1.097 billion, up from $861 million. That is 22.8% of revenue and about 68% of operating cash flow. "
        "Operating cash flow exceeded net income by $1.775 billion. Stock-based compensation is $1.097 billion of that gap, and about $678 million is still unexplained. "
        "Depreciation and amortization is missing for CrowdStrike, so it is not part of this comparison and it is not treated as zero."
    ),
    "Microsoft": (
        "Operating cash flow grew 34.4% in FY2026, faster than revenue and faster than operating profit. "
        "The operating-cash-flow margin rose from 48.3% in FY2025 to 55.1% in FY2026, a gain of 6.8 percentage points. "
        "The operating margin gained 1.2."
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
        "Cash fell from $7.6 billion to $5.4 billion, while short-term investments rose from $0.3 billion to $1.2 billion. "
        "Short-term debt went from $1.5 billion to zero, and long-term debt rose from $4.1 billion to $6.2 billion. "
        "Current assets fell from $11.2 billion to $10.2 billion, and current liabilities fell from $10.5 billion to $10.2 billion. "
        "The current ratio slipped below 1 because current assets fell by more. "
        "Share repurchases were $11.3 billion, compared with $9.5 billion. "
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
            "AMD's revenue growth, operating margin, and operating cash flow all rose in FY2025. "
            "Operating margin is 10.7%, up from 7.4%, and still well below Microsoft, Apple, NVIDIA, and Adobe. "
            "Expenses grew 24.3%, behind revenue, so the margin gain is real and the level is still low. "
            "These totals do not show the expense mix or product-level profit, so they do not support a cost cut. "
            "The thing to watch is whether growth keeps flowing through to operating margin."
        ),
    },
    "Adobe": {
        "Growth": GROWTH["Adobe"],
        "Profitability": PROFITABILITY["Adobe"],
        "Operations": OPERATIONS["Adobe"],
        "Cash Flow": CASH["Adobe"],
        "Financial Health": HEALTH["Adobe"],
        "Management Attention": (
            "Adobe's operating margin rose from 31.3% to 36.6% because expenses grew 0.9% against revenue growth of 10.5%. "
            "In the same year the current ratio fell from 1.068 to 0.996 and debt-to-equity rose from 0.399 to 0.534. "
            "Cash fell from $7.6 billion to $5.4 billion, short-term debt went from $1.5 billion to zero, "
            "and long-term debt rose from $4.1 billion to $6.2 billion. "
            "A current ratio just under 1 is a liquidity signal, not a crisis. "
            "Share repurchases were $11.3 billion, up from $9.5 billion. "
            "The expense ratio and the cash-and-debt shift are two different questions. "
            "One is whether spending can stay near 52.6% of revenue. "
            "The other is the lower cash balance and the move from short-term debt into long-term debt."
        ),
    },
    "Apple": {
        "Growth": GROWTH["Apple"],
        "Profitability": PROFITABILITY["Apple"],
        "Operations": OPERATIONS["Apple"],
        "Cash Flow": CASH["Apple"],
        "Financial Health": HEALTH["Apple"],
        "Management Attention": (
            "Apple's net income grew 19.5% in FY2025, from $93.7 billion to $112.0 billion, while operating cash flow fell 5.7%, "
            "from $118.3 billion to $111.5 billion. Cash conversion fell from 1.262 to 0.995. "
            "Receivables, inventory, and payables moved in different directions, and stock-based compensation and depreciation both increased. "
            "That is not a cash increase. Those accounts are already in the file, and they do not explain the drop. "
            "The next place to look is the cash-flow statement's own operating lines."
        ),
    },
    "CrowdStrike": {
        "Growth": GROWTH["CrowdStrike"],
        "Profitability": PROFITABILITY["CrowdStrike"],
        "Operations": OPERATIONS["CrowdStrike"],
        "Cash Flow": CASH["CrowdStrike"],
        "Financial Health": HEALTH["CrowdStrike"],
        "Management Attention": (
            "CrowdStrike's operating loss widened from $116.4 million to $293.3 million, and the net loss widened from $15.2 million to $162.5 million. "
            "Revenue still grew 21.7%. Research and development rose from $1.076 billion to $1.385 billion, "
            "and general and administrative rose from $481 million to $670 million. Both grew faster than sales. "
            "Sales and marketing rose 20.2%, a little slower than revenue. "
            "Operating cash flow stayed positive, at $1.612 billion. "
            "Stock-based compensation was $1.097 billion, about 68% of that cash flow, and about $678 million of the gap is still unexplained. "
            "Positive operating cash flow is not a GAAP profit. R&D and G&A are the spending lines that outgrew sales."
        ),
    },
    "Microsoft": {
        "Growth": GROWTH["Microsoft"],
        "Profitability": PROFITABILITY["Microsoft"],
        "Operations": OPERATIONS["Microsoft"],
        "Cash Flow": CASH["Microsoft"],
        "Financial Health": HEALTH["Microsoft"],
        "Management Attention": (
            "Microsoft's operating margin rose from 45.6% to 46.8% and the operating-cash-flow margin rose from 48.3% to 55.1%, "
            "while gross margin eased from 68.8% to 67.9%. "
            "Expenses grew 7.4% against revenue growth of 17.8%, so the operating-margin gain did not come from gross margin. "
            "Gross margin and the expense ratio moved in opposite directions and need to be looked at separately. "
            "The company-year totals do not say whether the gross-margin dip is mix or delivery cost, "
            "or whether expenses can stay at 21.2% of revenue as sales keep growing."
        ),
    },
    "NVIDIA": {
        "Growth": GROWTH["NVIDIA"],
        "Profitability": PROFITABILITY["NVIDIA"],
        "Operations": OPERATIONS["NVIDIA"],
        "Cash Flow": CASH["NVIDIA"],
        "Financial Health": HEALTH["NVIDIA"],
        "Management Attention": (
            "NVIDIA's revenue grew 65.5% in FY2026, down from 114.2% in FY2025. Revenue is still rising. "
            "Gross margin fell from 75.0% to 71.1%. Operating margin was 60.4%, down from 62.4% and still above 54.1% in FY2024. "
            "Read FY2026 against a more ordinary growth rate, not against 114.2%. "
            "The open question is whether gross margin, operating margin, and the operating-cash-flow margin stay near these levels if growth cools further. "
            "Slower growth is not weaker demand unless volume or price says so."
        ),
    },
}

CONCLUSION = (
    "This comparison uses each company's own latest reported year. "
    "Microsoft, NVIDIA, and CrowdStrike are FY2026. Apple, Adobe, and AMD are FY2025. "
    "Those years do not cover the same months. NVIDIA and CrowdStrike end in January, Microsoft ends in June, "
    "Apple ends in September, and Adobe and AMD end near the calendar year. "
    "FY2025 is the last year on file for all six, so the peer ranks stay on FY2025. "
    "A lower average rank is a stronger result on those nine metrics. It is context, not a ranking of which company is best.\n\n"
    "NVIDIA and Microsoft are the strongest operating stories in their latest year, for different reasons. "
    "NVIDIA still turns 60.4% of revenue into operating profit, and operating cash flow grew 60.3%, "
    "even though growth and margins came down from FY2025. "
    "Microsoft grew revenue faster than in FY2025, raised its operating margin, "
    "and raised its operating-cash-flow margin from 48.3% to 55.1%. "
    "Adobe also turned modest revenue growth into a higher operating margin and higher operating cash flow, "
    "because operating expenses barely grew.\n\n"
    "AMD is improving from a lower profit level. Revenue growth, operating margin, and operating cash flow all rose in FY2025. "
    "The operating margin is 10.7%, up from 7.4%, and still well below Microsoft, Apple, NVIDIA, and Adobe.\n\n"
    "Three results are worth a closer look even though revenue did not fall. "
    "Apple's net income grew 19.5% while operating cash flow fell 5.7%. "
    "Receivables, inventory, payables, stock-based compensation, and depreciation are already in the file, and they do not close that gap. "
    "Adobe's profit and cash improved while the current ratio moved from 1.068 to 0.996 and debt-to-equity rose from 0.399 to 0.534. "
    "Cash fell from $7.6 billion to $5.4 billion, and long-term debt rose from $4.1 billion to $6.2 billion. "
    "CrowdStrike is still growing and still generating operating cash flow, "
    "and the operating loss widened from $116.4 million to $293.3 million. "
    "Stock-based compensation was $1.097 billion. That is a large non-cash expense, "
    "and it is not the whole reason operating cash flow stayed positive.\n\n"
    "Revenue growth does not explain these differences. "
    "NVIDIA grew 65.5% and CrowdStrike grew 21.7%, and both grew more slowly than the year before. "
    "Microsoft grew faster, at 17.8%. Apple grew 6.4%. "
    "What matters is whether growth is showing up in operating profit, "
    "whether operating expenses are growing slower than revenue, "
    "and whether earnings and operating cash are moving in the same direction."
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
            "Gross margin and the expense ratio moved in opposite directions, so look at them separately. "
            "The totals do not say which products or cost lines did it, or whether expenses can stay at 21.2% of revenue as sales keep growing."
        ),
        "monitor": "Gross margin, operating expense / revenue, operating margin, and operating-cash-flow margin.",
    },
    {
        "company": "Apple",
        "area": "Earnings and cash",
        "kind": "investigate",
        "signal": (
            "Net income grew 19.5% in FY2025, from $93.7 billion to $112.0 billion, while operating cash flow fell 5.7%, "
            "from $118.3 billion to $111.5 billion. "
            "Cash conversion fell from 1.262 to 0.995. "
            "Receivables rose $6.4 billion, inventory fell $1.6 billion, and payables rose $0.9 billion."
        ),
        "trend": "Earnings improved and operating cash flow declined. The working-capital accounts did not move in one direction, and the non-cash add-backs increased.",
        "why": (
            "A higher net income figure is not more cash from operations. "
            "Stock-based compensation rose from $11.7 billion to $12.9 billion, and depreciation and amortization rose from $11.4 billion to $11.7 billion. "
            "Those increases would support operating cash flow, so they do not explain the decline. "
            "The combined year-end change in receivables, inventory, and payables is a use of about $3.9 billion. "
            "Net income plus the two add-backs and that use is still about $21.2 billion above reported operating cash flow. "
            "Year-end balances are not the cash-flow statement's working-capital lines."
        ),
        "attention": (
            "The earnings increase is not a cash increase. "
            "Higher stock-based compensation, higher depreciation, and the year-end move in receivables, inventory, and payables do not explain the cash decline. "
            "Those amounts are already in the file. The next look is the cash-flow statement's own operating section."
        ),
        "monitor": "Net income, operating cash flow, cash conversion, receivables, inventory, and payables.",
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
            "Read FY2026 against a more ordinary growth rate, not only against 114.2%. "
            "Watch whether gross margin, operating margin, and the operating-cash-flow margin stay near these levels if growth cools again. "
            "Slower growth is not weaker demand unless volume or price says so."
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
            "The current ratio fell from 1.068 to 0.996, and debt-to-equity rose from 0.399 to 0.534. "
            "Cash fell from $7.6 billion to $5.4 billion. Short-term debt went from $1.5 billion to zero, and long-term debt rose from $4.1 billion to $6.2 billion."
        ),
        "trend": "Profit and operating cash flow improved. Cash declined, and debt shifted toward the long-term balance.",
        "why": "The operating improvement came from very slow expense growth. A current ratio just under 1.0 is a liquidity signal, not proof of distress. Current assets fell by more than current liabilities.",
        "attention": (
            "The expense ratio fell to 52.6% of revenue because spending barely grew. That is the part to test: can it stay there. "
            "Cash and debt are separate. Cash is lower, short-term debt is gone, and long-term debt is higher. "
            "The year-end balances show the direction. They do not show the maturity schedule. "
            "A current ratio of 0.996 is a liquidity flag, not a crisis."
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
            "Watch whether revenue growth keeps lifting an operating margin that is still only 10.7%. "
            "The consolidated totals do not show expense mix or product-level profit, so they do not support a specific cost cut."
        ),
        "monitor": "Revenue growth, operating margin, operating expense / revenue, and operating-cash-flow margin.",
    },
    {
        "company": "CrowdStrike",
        "area": "Operating loss",
        "kind": "investigate",
        "signal": (
            "Operating margin fell from -2.9% to -6.1%. The operating loss widened from $116.4 million to $293.3 million, "
            "and the net loss widened from $15.2 million to $162.5 million. "
            "Operating expenses grew 26.2% against revenue growth of 21.7% and reached 80.8% of revenue. "
            "Operating cash flow grew 16.7% to $1.612 billion. Stock-based compensation was $1.097 billion."
        ),
        "trend": "Revenue and operating cash flow are still growing. The GAAP loss widened. Research and development and general and administrative grew faster than revenue.",
        "why": (
            "Positive operating cash flow does not mean the company is GAAP profitable. Operating income and net income are losses. "
            "Stock-based compensation is a non-cash expense, so it reduces GAAP earnings without the same cash outflow. "
            "It was about 68% of operating cash flow. Operating cash flow exceeded net income by $1.775 billion, "
            "and stock-based compensation is $1.097 billion of that difference, not all of it."
        ),
        "attention": (
            "R&D and general and administrative grew faster than the 21.7% sales growth. Sales and marketing did not. "
            "Read the $1.612 billion of operating cash flow next to the GAAP loss. "
            "Stock-based compensation is a large part of why cash and earnings differ, and about $678 million of that gap is still unexplained."
        ),
        "monitor": "Revenue growth, operating margin, operating expense / revenue, stock-based compensation, and the operating-cash-flow margin.",
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
