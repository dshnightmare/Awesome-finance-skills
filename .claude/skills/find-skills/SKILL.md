---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X" or express interest in extending capabilities.
---

## When to Use This Skill

Trigger this skill when users:
- Ask "how do I do X" or "find a skill for X"
- Want to extend agent capabilities
- Are looking for domain-specific tools
- Express interest in installing or discovering skills

## What is the Skills CLI?

`npx skills` is a package manager for agent skills. Key commands:
- `npx skills find [query]` — search for skills
- `npx skills add <package>` — install a skill
- `npx skills check` — check installed skills
- `npx skills update` — update skills

Browse the ecosystem at: **https://skills.sh/**

## How to Help Users Find Skills

1. **Identify the domain and task** the user needs help with
2. **Check the leaderboard** at https://skills.sh/ for established solutions before searching
3. **Search strategically** using `npx skills find [query]` with specific keywords
4. **Verify quality** — prefer install counts 1K+, check source reputation (official sources like Vercel Labs or Anthropic), and GitHub stars (be cautious under 100 stars)
5. **Present findings** with skill name, description, install count, and command
6. **Facilitate installation** using `npx skills add <owner/repo@skill> -g -y`

**Key principle:** Do not recommend a skill based solely on search results. Always verify credibility metrics first.

## Common Skill Categories

| Category | Example queries |
|---|---|
| Web Development | deployment, frontend, API |
| Testing | unit tests, e2e, coverage |
| DevOps | CI/CD, Docker, monitoring |
| Documentation | readme, docs, changelog |
| Code Quality | linting, refactoring, review |
| Design | UI, accessibility, styling |
| Productivity | automation, scheduling, search |

## Tips for Effective Searches

- Use specific keywords related to the user's need
- Try alternative terms if first search yields nothing
- Check popular/official sources (Vercel Labs, Anthropic)

## When No Skills Are Found

- Acknowledge the gap
- Offer direct assistance without a skill
- Suggest the user create a custom skill using `npx skills init`
