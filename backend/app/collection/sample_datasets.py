from typing import List, Dict

SAMPLE_STORIES: List[Dict] = [
    {
        "id": "ai-regulatory-accord",
        "title": "Global AI Safety & Regulatory Accord",
        "topic": "Artificial Intelligence Regulation and Global Tech Policy",
        "description": "Cross-outlet coverage of landmark international artificial intelligence regulations signed in Geneva, highlighting stark differences in economic framing, ethical concerns, and regulatory burden.",
        "articles": [
            {
                "title": "Landmark AI Treaty Signs Guardrails Against Exploitative Automation and Bias",
                "source": "The Guardian",
                "url": "https://www.theguardian.com/technology/ai-treaty-guardrails-ethical-risk",
                "author": "Elena Vance",
                "published_date": "2026-03-12",
                "content": """Global leaders and civil rights advocates hailed a historic breakthrough in Geneva as delegates signed the International Artificial Intelligence Safeguards Accord. The treaty establishes mandatory human oversight over algorithmic systems deployed in law enforcement, employment, and predictive healthcare.

Human rights organizations praised the binding provisions, emphasizing that unchecked corporate algorithms have already exacerbated discriminatory practices against marginalized communities. "This accord is a critical bulwark against reckless automated surveillance and corporate impunity," declared Sophia Chen, policy director at Algorithmic Justice Global. "For too long, Silicon Valley billionaires have treated public safety as an acceptable casualty of relentless disruption."

The agreement mandates comprehensive bias audits and grants workers statutory protections when synthetic intelligence systems are implemented in unionized workplaces. Independent civil liberties watchdogs warned that without strict enforcement penalties, predatory tech conglomerates might seek loopholes. However, officials insisted that international compliance committees will wield punitive investigative powers to protect vulnerable citizens."""
            },
            {
                "title": "Geneva AI Accord Sets Multilateral Standards and Compliance Timelines for Tech Firms",
                "source": "Reuters",
                "url": "https://www.reuters.com/technology/geneva-ai-accord-sets-standards-2026-03-12",
                "author": "Marcus Weber",
                "published_date": "2026-03-12",
                "content": """Delegates from forty-two nations ratified the International Artificial Intelligence Framework Agreement on Thursday, establishing synchronized compliance schedules and verification protocols for frontier model developers. The multilateral pact requires developers of foundation models exceeding 10^26 floating-point operations to file regular safety documentation with accredited auditing registries.

Under the agreed terms, international commercial software firms will have an eighteen-month transition window before standard inspections commence. "The objective is regulatory convergence across trade jurisdictions to eliminate cross-border friction while establishing standard evaluation metrics," said UN High Commissioner for Digital Policy Aris Thorne.

Trade ministry representatives stated that bilateral trade accords will incorporate the safety criteria. The treaty incorporates exemptions for open-weight models below specified compute thresholds and allows sovereign member states to establish localized oversight councils. Implementation costs are estimated by the OECD to average approximately 1.4% of annual compliance budgets for participating enterprises."""
            },
            {
                "title": "Stifling Innovation: Crippling Geneva AI Mandate Threatens Free Enterprise and Competitiveness",
                "source": "Fox Business",
                "url": "https://www.foxbusiness.com/technology/geneva-ai-mandate-threatens-competitiveness",
                "author": "Brett Calder",
                "published_date": "2026-03-12",
                "content": """A sweeping bureaucratic power-grab unfolded in Geneva on Thursday as unelected globalists approved suffocating new regulatory barriers for the burgeoning artificial intelligence sector. The crushing regulatory burden threatens to paralyze dynamic American tech innovators while foreign adversaries in Beijing operate unrestricted.

Industry leaders sounded the alarm over the disastrous compliance hurdles, warning that micromanagement by heavy-handed international panels will strangle private sector investment. "This catastrophic overreach will suffocate entrepreneurial dynamism and destroy thousands of high-paying tech jobs," insisted David Sterling, president of the Enterprise Innovation Coalition. "While Western startups are tied down in red tape and punitive paperwork, overseas rivals will aggressively dominate global markets."

Venture capital groups pointed out that the onerous auditing requirements impose massive legal costs that will wipe out promising small developers, effectively cementing a government-favored monopoly for entrenched legacy corporations. Free-market advocates called on lawmakers to reject the treaty's jurisdiction."""
            }
        ]
    },
    {
        "id": "clean-energy-transition",
        "title": "Clean Energy Grid Transition and Fossil Fuel Subsidies",
        "topic": "Energy Infrastructure, Climate Targets, and Economic Trade-offs",
        "description": "Contrasting reporting on a major national grid overhaul bill, exhibiting selective omission of nuclear subsidies and coal community impacts.",
        "articles": [
            {
                "title": "Bold Climate Package Mobilizes Billions for Clean Power and Renewable Jobs",
                "source": "Progressive Daily",
                "url": "https://www.progressivedaily.org/climate-grid-transition-act",
                "author": "Kavita Rao",
                "published_date": "2026-02-18",
                "content": """Parliament passed the visionary Green Infrastructure Modernization Act on Tuesday, committing $48 billion toward renewable solar, offshore wind, and next-generation battery storage. Environmental champions celebrated the landmark legislation as an indispensable stride toward halting catastrophic planetary heating and purifying contaminated air in frontline communities.

"This transformative investment represents our generation's decisive pledge to our children's future," declared Clean Future Coalition director Hannah Morales. "We are proving that decarbonization and vibrant prosperity can advance hand in hand."

The legislation earmarks dedicated grants for solar installation training in historically disadvantaged neighborhoods and establishes guaranteed green manufacturing tax credits. Grassroots environmental justice activists emphasized that phasing out toxic fossil fuel emissions will immediately reduce childhood asthma rates and healthcare expenditures across metropolitan centers."""
            },
            {
                "title": "Infrastructure Bill Backs Mixed Clean Power Grid with Nuclear Subsidies",
                "source": "Associated Press",
                "url": "https://www.apnews.com/article/energy-grid-nuclear-renewables-act",
                "author": "David Miller",
                "published_date": "2026-02-18",
                "content": """Lawmakers approved a bipartisan $48 billion energy grid modernization package on Tuesday following months of cross-party negotiations over base-load power reliability. The measure splits funding between solar arrays, offshore wind, and $14 billion in life-extension credits for existing commercial nuclear reactors.

Energy Department analysts estimated that upgrading transmission corridors will expand electrical grid capacity by 35 gigawatts over the next decade. "The legislative compromise balances long-term carbon reduction targets with the imperative of continuous baseload grid stability," said Energy Committee Chairman Arthur Vance.

The bill also allocates $4.5 billion for community transition funds targeted at municipal districts facing the planned decommissioning of older coal and natural gas generating stations between 2028 and 2032."""
            },
            {
                "title": "Soaring Energy Bills Loom as Reckless Mandates Threaten Power Grid Collapse",
                "source": "The National Sentinel",
                "url": "https://www.nationalsentinel.com/energy-grid-cost-collapse-risk",
                "author": "Thomas Sterling",
                "published_date": "2026-02-18",
                "content": """Working families and beleaguered manufacturers were delivered a devastating economic blow on Tuesday as partisan lawmakers rammed through an irresponsible $48 billion green energy spending spree. Industry experts warn the premature abandonment of reliable traditional fuel sources will trigger catastrophic rolling blackouts and sky-high utility bills.

"This radical green fantasy directly jeopardizes our energy independence," warned Greg Thornton, chief analyst at the Energy Security Foundation. "Intermittent wind and solar cannot support heavy manufacturing during extreme winter cold snaps, and consumers will be forced to shoulder crippling electricity price hikes."

The legislation virtually ignores the plight of thousands of skilled fossil fuel workers who face sudden unemployment and economic ruin in regional mining towns. Fiscal watchdogs condemned the ballooning national debt incurred by subsidizing unproven green technologies at taxpayer expense."""
            }
        ]
    }
]

def get_sample_events():
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "topic": s["topic"],
            "description": s["description"],
            "article_count": len(s["articles"]),
            "sources": [a["source"] for a in s["articles"]]
        }
        for s in SAMPLE_STORIES
    ]

def get_sample_by_id(story_id: str):
    for s in SAMPLE_STORIES:
        if s["id"] == story_id:
            return s
    return None
