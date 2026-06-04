# Wira end-to-end swarm brief

Date: 2026-06-04
Mode: BUSINESS
Repo: /Users/motwe/Wira
Live operating surface: https://wira-local-agent.nibiashara.workers.dev
Public product page: https://nibiashara.biz/products/wira/

Founder intent for this pass:
- Get people talking to their agent on WhatsApp as fast and intuitively as possible.
- Do not rely on hope that a local server is already running on the buyer's machine.
- Surface the free path first.
- Also surface the easy ChatGPT-subscription path clearly and quickly.
- Validate the journey end to end: website -> payment -> download/start link -> onboarding -> first WhatsApp conversation.
- Fix issues found, not just report them.

Known grounded issues before swarm:
- `python3 -m unittest -q` in `/Users/motwe/Wira/agent` is failing on copy alignment tests.
- `site/src/pages/Onboarding.tsx` still heavily surfaces `local model` / `API key` style language in first-run copy.
- `agent/gui.py` still presents the local path as the recommended/default brain choice.
- `STATUS.md` claims a ChatGPT-first thesis that does not match current site code.

Guardrails:
- Do not deploy from a child worktree.
- Keep changes scoped to Wira; do not touch unrelated repos.
- No fake completion claims. Run real commands and cite them in handoff.
- If you change copy/tests, align them with the founder intent above instead of merely deleting assertions.

Desired acceptance for the final merged result:
1. First-run website copy is non-technical and clearly prioritizes the fastest free path.
2. ChatGPT path is obvious, easy, and human-readable.
3. Post-payment success flow clearly gets the buyer to download/start Wira and continue setup.
4. Desktop onboarding no longer assumes local-model/Ollama as the main path.
5. Relevant tests pass.
6. Local/browser verification shows the user can move from page to checkout to success to onboarding without dead ends.
