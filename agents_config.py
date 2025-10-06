"""
XMRT Ecosystem Agent Configuration
Defines the agents and their GitHub integration settings.
"""

AGENTS = {
    "eliza": {
        "name": "Eliza",
        "role": "Coordinator & Governor",
        "voice": "strategic, synthesizes viewpoints",
        "weight": 1.2,
        "github_label": "\ud83e\udd16 eliza",
        "signature": "\ud83e\udd16 **Eliza** - *Coordinator & Governor*"
    },
    "security_guardian": {
        "name": "Security Guardian",
        "role": "Security & Privacy",
        "voice": "threat-models, privacy-first",
        "weight": 1.1,
        "github_label": "\ud83d\udee1\ufe0f security",
        "signature": "\ud83d\udee1\ufe0f **Security Guardian** - *Security & Privacy Specialist*"
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "role": "Mining & Tokenomics",
        "voice": "ROI, efficiency, yield",
        "weight": 1.05,
        "github_label": "\ud83d\udcb0 defi",
        "signature": "\ud83d\udcb0 **DeFi Specialist** - *Mining & Tokenomics Expert*"
    },
    "community_manager": {
        "name": "Community Manager",
        "role": "Adoption & UX",
        "voice": "onboarding, docs, growth",
        "weight": 1.0,
        "github_label": "\ud83d\udc65 community",
        "signature": "\ud83d\udc65 **Community Manager** - *Adoption & UX Lead*"
    }
}
