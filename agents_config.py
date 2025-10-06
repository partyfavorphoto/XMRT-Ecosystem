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
        "github_label": "agent-eliza",
        "signature": "🤖 **Eliza** - *Coordinator & Governor*",
        "emoji": "🤖"
    },
    "security_guardian": {
        "name": "Security Guardian",
        "role": "Security & Privacy",
        "voice": "threat-models, privacy-first",
        "weight": 1.1,
        "github_label": "agent-security",
        "signature": "🛡️ **Security Guardian** - *Security & Privacy Specialist*",
        "emoji": "🛡️"
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "role": "Mining & Tokenomics",
        "voice": "ROI, efficiency, yield",
        "weight": 1.05,
        "github_label": "agent-defi",
        "signature": "💰 **DeFi Specialist** - *Mining & Tokenomics Expert*",
        "emoji": "💰"
    },
    "community_manager": {
        "name": "Community Manager",
        "role": "Adoption & UX",
        "voice": "onboarding, docs, growth",
        "weight": 1.0,
        "github_label": "agent-community",
        "signature": "👥 **Community Manager** - *Adoption & UX Lead*",
        "emoji": "👥"
    }
}
