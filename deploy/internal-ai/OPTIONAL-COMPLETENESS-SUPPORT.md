# Optional Completeness Support

## Purpose

The internal AI should write the main report and create the shell directly.

Use deterministic support only to reduce omission risk when the AI-written report has the right structure and quality but may be missing long-tail items.

## Good Uses

- exhaustive dataset inventory
- exhaustive component inventory
- exhaustive transaction inventory
- backend candidate cross-check
- machine-generated appendix tables
- CSV references linked from the matching report section

## Bad Uses

- primary shell generation
- visual placement truth
- dominant business interpretation
- final starter/mockup truth

## Practical Rule

If the AI has already produced the right shell and the right main report:

- keep them
- use deterministic support only to append or verify long lists
- link every long-list output back into the numbered section that owns it

Recommended pattern:

- main report keeps the readable summary
- CSV keeps the exhaustive detail
- the main report section includes a `Detailed Inventory` line with the exact CSV link

## Config Rule When Optional Support Is Used

If optional deterministic support needs real project roots:

- keep the base file `am-bridge.config.json` unchanged
- create `am-bridge.config.local.json` from `am-bridge.config.local.example.json`
- put real `sourceRoots` and `backendRoots` only in the local file

If deterministic support conflicts with clear screenshot/XML/source evidence, prefer the direct evidence.
