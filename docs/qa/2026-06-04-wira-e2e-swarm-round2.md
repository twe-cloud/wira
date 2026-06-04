# Wira E2E swarm round 2

Goal: close the remaining buyer-journey gaps for Wira from landing page to first WhatsApp entry/pairing state, using visible cmux lanes plus isolated Claude worktrees.

Ground rules
- Work only inside your assigned isolated worktree.
- Do not commit, push, or deploy.
- Make the smallest correct changes that improve the real user journey.
- Run targeted validation in your lane.
- Before exit, write the required handoff file at the exact path assigned to your lane.

Product promise to protect
- A buyer should quickly understand that Wira gets them to their agent on WhatsApp.
- The fastest free option must be surfaced first.
- The ChatGPT subscription path must still be easy, clear, and credible.
- A fully private local path can exist, but it must not feel like the required default.
- Post-payment flow should clearly guide: download -> choose brain -> pair WhatsApp.

Required proof language
- Verified = you directly checked it in code/output.
- Partially verified = some relevant evidence exists, but not the final user-facing finish line.
- Unproven = not exercised.

Lane outputs
- Each lane must leave a HANDOFF_AGENT<n>.md file in its worktree root.
- Handoff sections: scope, files changed, validation run, findings, unresolved risks, recommended merge order.
