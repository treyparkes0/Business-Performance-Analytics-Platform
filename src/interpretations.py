"""Interpretations from the Databricks notebook. Do not invent new conclusions."""

from __future__ import annotations

GROWTH = {
    "AMD": "AMD continues to improve its revenue performance, with revenue growth increasing from 13.7% to 34.3%. Its growth differential increased by approximately 21 percentage points, indicating that revenue growth has accelerated rather than slowed.",
    "Adobe": "Adobe has maintained moderate and stable revenue growth, with growth declining slightly from 10.8% to 10.5%. Its growth differential remained relatively consistent, indicating limited change in its revenue growth trajectory.",
    "Apple": "Apple’s revenue growth has remained relatively consistent with limited fluctuation. The company has also maintained slightly positive growth momentum, indicating a stable revenue performance profile with gradual improvement in its growth trajectory.",
    "CrowdStrike": "CrowdStrike has had a moderate growth rate from the prior few years; however they continue to lose momentum, which could be a problem in the future if the company keeps this downward trend.",
    "Microsoft": "Microsoft's growth rate shows a consistent and stable revenue performance, with relatively little fluctuation in growth acceleration. This suggests that Microsoft has maintained steady revenue growth rather than experiencing significant changes in its growth trajectory.",
    "NVIDIA": "NVIDIA continues to demonstrate strong top-line growth year over year. However, its growth differential declined by approximately 49 percentage points as revenue growth moderated from 114% to 65%. This reflects a significant normalization from its exceptionally high prior-year growth rate rather than a decline in overall revenue.",
}

PROFITABILITY = {
    "AMD": "AMD has maintained relatively stable gross margins while operating income and net income have grown year over year. However, operating income growth has declined significantly from 307% in the prior year, indicating that profitability is still improving but at a slower pace.",
    "Adobe": "Adobe has maintained a stable yet strong gross margin (89%) while operating and net income have grown year over year. Operating margin suggests that revenue growth is translating into improving profitability.",
    "Apple": "Apple has maintained a stable gross margin while operating income has remained relatively consistent, while net income has grown 45%. This suggests that factors beyond operating income growth are contributing to the increase in net income.",
    "CrowdStrike": "CrowdStrike has maintained a relatively consistent gross margin over the past several years; however, operating performance has continued to decline, with operating margins falling from -0.6% to -2.9% and then -6.1%. This indicates increasing operating pressure that is negatively affecting profitability.",
    "Microsoft": "Microsoft’s gross margin has gradually declined while operating income has continued to grow year over year. This suggests that Microsoft is generating stronger operating income despite some pressure on gross profitability.",
    "NVIDIA": "NVIDIA’s gross margin has fluctuated gradually but remains relatively consistent, while operating margin increased sharply from 54% to 62% before declining to around 60%. Net income growth has also moderated, suggesting that NVIDIA’s exceptional profitability and revenue growth are beginning to normalize after its significant prior-year increase.",
}

OPERATIONS = {
    "AMD": "AMD’s operating efficiency improved as revenue grew faster than operating expenses. Operating expenses also fell from 42.0% to 38.9% of revenue, showing that the company is managing its costs more effectively.",
    "Adobe": "Adobe’s operating efficiency improved significantly in 2025 as operating expense growth slowed to 0.9% while revenue continued to grow. Operating expenses also fell from 57.7% to 52.6% of revenue, showing better cost management.",
    "Apple": "Apple’s operating expenses have grown faster than revenue in both years, creating some pressure on costs. In 2025, operating expenses grew 1.8 percentage points faster than revenue, while operating expenses remained relatively low at about 15% of revenue.",
    "CrowdStrike": "CrowdStrike’s operating efficiency has weakened as operating expenses have grown faster than revenue. Operating expenses reached 80.8% of revenue in 2026, showing increasing pressure from operating costs.",
    "Microsoft": "Microsoft has maintained strong operating efficiency, with revenue growing faster than operating expenses. Operating expenses also fell from 25.1% to 21.2% of revenue, showing that the company is managing its costs effectively.",
    "NVIDIA": "NVIDIA continues to show strong operating efficiency, with revenue growing much faster than operating expenses. However, the gap has narrowed significantly, suggesting that its cost advantage is becoming less pronounced as the company grows.",
}

CASH = {
    "AMD": "AMD’s operating cash flow has strengthened significantly after declining in 2023. Its OCF margin increased to 22.3% in 2025, while operating cash flow grew 153.5%, indicating a strong improvement in cash generation.",
    "Adobe": "Adobe has maintained strong operating cash generation, with its OCF margin recovering to 42.2% in 2025. Operating cash flow also grew 24.5%, indicating improving cash generation compared with the prior year.",
    "Apple": "Apple continues to generate strong operating cash flow, but its OCF margin declined to 26.8% in 2025 and operating cash flow fell 5.7%. This indicates some weakening in cash-generation efficiency compared with the prior year.",
    "CrowdStrike": "CrowdStrike continues to generate positive operating cash flow despite reporting negative net income. However, its OCF margin has declined to 33.5%, indicating that cash generation is becoming less efficient relative to revenue.",
    "Microsoft": "Microsoft has significantly strengthened its operating cash generation, with its OCF margin increasing to 55.1% in 2026. Operating cash flow also grew 34.4%, indicating strong conversion of revenue into operating cash.",
    "NVIDIA": "NVIDIA has experienced exceptional growth in operating cash flow, with OCF increasing 60.3% in 2026. Although its OCF margin declined slightly to 47.6%, cash generation remains extremely strong relative to revenue.",
}

HEALTH = {
    "AMD": "AMD: Current ratio improved from 2.62 to 2.85, while liabilities-to-assets increased slightly from 16.8% to 18.1%. This indicates strong liquidity with a fair increase in balance-sheet obligations.",
    "Adobe": "Adobe: Current ratio declined slightly below 1.0 in 2025, while debt-to-equity and liabilities-to-assets increased. This indicates weaker short-term liquidity and increasing balance-sheet leverage that may warrant attention. A current ratio below 1.0 is a signal to monitor, not automatically a financial crisis.",
    "Apple": "Apple: Current ratio remained below 1.0, but debt-to-equity declined substantially from 1.70 to 1.23 and liabilities-to-assets also improved. This is improving leverage with tighter liquidity, not a simple finding that Apple is financially weak. A current ratio below 1.0 is a signal that may warrant attention.",
    "CrowdStrike": "CrowdStrike: Current ratio remained strong at around 1.8, while debt-to-equity and liabilities-to-assets continued to decline. However, ROA moved into negative territory, indicating that profitability relative to assets has weakened.",
    "Microsoft": "Microsoft maintained a current ratio above 1.0 while debt-to-equity and liabilities-to-assets declined. ROA remained strong, although it decreased slightly in 2025 before recovering in 2026. These trends indicate that Microsoft maintained strong financial health while reducing its relative reliance on debt and liabilities.",
    "NVIDIA": "NVIDIA has very strong liquidity and declining leverage, with debt-to-equity falling to 0.054 in 2026. ROA remains exceptionally strong despite declining from 65.3% to 58.1%.",
}

EXECUTIVE = {
    "AMD": {
        "Growth": "Revenue growth accelerated from 13.7% to 34.3%.",
        "Profitability": "Gross margins are relatively stable while operating and net income have grown, though operating-income growth has slowed from a very high prior-year rate.",
        "Operations": "Revenue is growing faster than operating expenses, and operating expenses fell from 42.0% to 38.9% of revenue.",
        "Cash Flow": "Operating cash generation strengthened, with OCF margin at 22.3% in 2025 and OCF growth of 153.5%.",
        "Financial Health": "Liquidity is strong (current ratio 2.62 to 2.85), with a modest increase in liabilities-to-assets.",
        "Management Attention": "Continue monitoring whether strong growth and cash generation hold as the company scales, and whether revenue continues to outpace operating expenses.",
    },
    "Adobe": {
        "Growth": "Revenue growth is moderate and stable (about 10.8% to 10.5%).",
        "Profitability": "Gross margin remains strong (about 89%), and operating and net income have grown.",
        "Operations": "In 2025, operating-expense growth slowed to 0.9% while revenue continued to grow; opex fell from 57.7% to 52.6% of revenue.",
        "Cash Flow": "Operating cash generation is strong, with OCF margin recovering to 42.2% in 2025.",
        "Financial Health": "Current ratio declined slightly below 1.0 in 2025 while leverage increased — a liquidity signal that may warrant attention.",
        "Management Attention": "Monitor the current ratio (1.068 to 0.996) so current assets remain sufficient for short-term obligations.",
    },
    "Apple": {
        "Growth": "Revenue growth has been relatively consistent, with slightly positive momentum.",
        "Profitability": "Gross margin is stable; operating income has been relatively consistent while net income grew about 45%.",
        "Operations": "Operating expenses grew faster than revenue in both years (1.8 percentage points faster in 2025), while opex stayed near 15% of revenue.",
        "Cash Flow": "Operating cash flow remains large, but OCF margin declined to 26.8% in 2025 and OCF fell 5.7%.",
        "Financial Health": "Improving leverage (debt-to-equity 1.70 to 1.23) with tighter liquidity (current ratio still below 1.0).",
        "Management Attention": "Monitor current assets and short-term liabilities, and whether operating-expense growth continues to outpace revenue.",
    },
    "CrowdStrike": {
        "Growth": "Growth remains moderate, but momentum has continued to slow.",
        "Profitability": "Gross margin is relatively consistent, but operating margins moved from -0.6% to -2.9% then -6.1%.",
        "Operations": "Operating expenses have grown faster than revenue and reached 80.8% of revenue in 2026.",
        "Cash Flow": "Operating cash flow is still positive despite negative net income, while OCF margin declined to 33.5%.",
        "Financial Health": "Liquidity remains strong (current ratio around 1.8) and leverage declined, but ROA moved into negative territory.",
        "Management Attention": "Investigate operating-cost pressure and the decline in net income margin from 2.4% (2024) to -0.4% (2025) and -3.4% (2026).",
    },
    "Microsoft": {
        "Growth": "Revenue growth has been consistent and stable, without large swings in acceleration.",
        "Profitability": "Gross margin has gradually declined while operating income has continued to grow.",
        "Operations": "Revenue is growing faster than operating expenses; opex fell from 25.1% to 21.2% of revenue.",
        "Cash Flow": "Operating cash generation strengthened, with OCF margin at 55.1% in 2026 and OCF growth of 34.4%.",
        "Financial Health": "Current ratio stayed above 1.0 while debt-to-equity and liabilities-to-assets declined.",
        "Management Attention": "Continue monitoring whether favorable leverage and liquidity trends are maintained.",
    },
    "NVIDIA": {
        "Growth": "Top-line growth remains strong, though it moderated from 114% to 65% (about a 49 percentage-point decline in the growth differential).",
        "Profitability": "Operating margin rose from 54% to 62% then eased toward 60%; net-income growth has also moderated.",
        "Operations": "Revenue still grows much faster than operating expenses, but that gap has narrowed as the company scales.",
        "Cash Flow": "OCF grew 60.3% in 2026; OCF margin eased slightly to 47.6% and remains very strong relative to revenue.",
        "Financial Health": "Liquidity is very strong and leverage declined (debt-to-equity 0.054 in 2026); ROA remains high though it declined from 65.3% to 58.1%.",
        "Management Attention": "Continue monitoring whether profitability and cash generation hold as exceptional revenue growth normalizes.",
    },
}

CONCLUSION = (
    "Overall, the analysis shows that company performance varies significantly across revenue growth, "
    "profitability, operating efficiency, cash generation, and financial health. NVIDIA and Microsoft "
    "demonstrated the strongest overall performance, although NVIDIA's exceptionally high revenue growth "
    "has begun to normalize while Microsoft has maintained more consistent growth and strong financial health.\n\n"
    "AMD showed improving performance, with stronger revenue growth, improved operating efficiency, and "
    "significant growth in operating cash flow. Adobe maintained strong profitability and cash generation, "
    "but its declining short-term liquidity and increasing leverage warrant continued monitoring. Apple "
    "continued to demonstrate strong profitability and cash generation, but its current ratio remained "
    "below 1.0 and operating expenses continued to grow faster than revenue. CrowdStrike maintained strong "
    "revenue growth and positive operating cash flow, but increasing operating expenses and declining net "
    "income margins indicate growing pressure on profitability.\n\n"
    "The analysis demonstrates that revenue growth alone does not provide a complete view of business "
    "performance. Evaluating growth alongside profitability, operating efficiency, cash generation, and "
    "financial health provides a more complete picture of how a company is performing and where management "
    "attention may be needed."
)

PEER = (
    "NVIDIA and Microsoft demonstrate stronger overall performance across several operating and financial "
    "indicators, while CrowdStrike shows stronger growth but greater pressure on profitability and operating "
    "costs. AMD’s recent results show accelerating growth and improving cash generation. Adobe remains highly "
    "profitable with a liquidity signal to monitor. Apple remains profitable and cash-generative, with tighter "
    "short-term liquidity and operating expenses growing faster than revenue."
)

ALERTS = [
    {
        "company": "CrowdStrike",
        "area": "Operating Efficiency",
        "kind": "investigate",
        "signal": "Operating expenses reached 80.8% of revenue in 2026.",
        "why": "Operating expenses are growing faster than revenue, creating increasing pressure on profitability.",
        "attention": "Management should investigate the factors contributing to the increase in operating costs and monitor whether the trend continues.",
    },
    {
        "company": "CrowdStrike",
        "area": "Profitability",
        "kind": "investigate",
        "signal": "Net income margin declined from 2.4% in 2024 to -0.4% in 2025 and -3.4% in 2026.",
        "why": "The decline sits alongside weaker operating margins, so reported growth is not translating into earnings.",
        "attention": "Follow up on what is driving operating losses and whether the margin path continues to deteriorate.",
    },
    {
        "company": "Adobe",
        "area": "Financial Health",
        "kind": "monitor",
        "signal": "Current ratio fell from 1.068 to 0.996 in 2025, while debt-to-equity and liabilities-to-assets increased.",
        "why": "A reading slightly below 1.0 is a short-term liquidity signal, not automatically a crisis. Leverage is also rising.",
        "attention": "Monitor current assets and liabilities to prevent further deterioration in short-term liquidity.",
    },
    {
        "company": "Apple",
        "area": "Financial Health",
        "kind": "mixed",
        "signal": "Debt-to-equity declined from 1.70 to 1.23, while the current ratio remained below 1.0 (about 0.87 to 0.89).",
        "why": "This is improving leverage with tighter liquidity — not a finding that Apple is simply financially weak.",
        "attention": "Monitor current assets and short-term liabilities so the current ratio does not continue to decline.",
    },
    {
        "company": "Apple",
        "area": "Operations",
        "kind": "monitor",
        "signal": "Operating expenses grew 1.8 percentage points faster than revenue in 2025, while opex stayed near 15% of revenue.",
        "why": "Cost growth ahead of revenue can pressure margins if it persists, even when the opex ratio is still low.",
        "attention": "Watch whether operating-expense growth continues to outpace revenue.",
    },
    {
        "company": "AMD",
        "area": "Growth & Cash",
        "kind": "positive",
        "signal": "Revenue growth accelerated and operating cash flow strengthened (OCF margin 22.3% in 2025).",
        "why": "The recent trend is favorable; the open question is durability as the company scales.",
        "attention": "Continue monitoring whether the favorable growth, efficiency, and cash-generation trend is maintained.",
    },
    {
        "company": "Microsoft",
        "area": "Financial Health",
        "kind": "positive",
        "signal": "Debt-to-equity declined from 0.167 in 2024 to 0.091 in 2026; liabilities-to-assets declined from 0.476 to 0.417; current ratio stayed above 1.0.",
        "why": "Leverage and liquidity trends are favorable.",
        "attention": "Continue monitoring whether the favorable leverage and liquidity trends are maintained.",
    },
    {
        "company": "NVIDIA",
        "area": "Growth",
        "kind": "mixed",
        "signal": "Revenue growth declined from 114% to 65%, while profitability and operating cash flow remain strong.",
        "why": "This is normalization from an exceptionally high prior-year growth rate, not a decline in revenue.",
        "attention": "Monitor whether NVIDIA can maintain strong profitability and cash generation as growth moderates.",
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
