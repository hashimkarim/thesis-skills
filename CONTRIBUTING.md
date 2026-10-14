# Contributing

Keep skills useful across projects and both assistants. Put project paths,
audiences, and local preferences in a brief rather than in reusable instructions.
Preserve a clear distinction between evidence, inference, and plans.

For a skill change, explain the user task it improves. Use a narrow description,
keep substantial optional guidance in referenced files, and avoid loading every
workflow for a small edit. Each skill must work when copied on its own. If you
add a resource, link it from the skill or a relevant reference.

For script changes, use Python 3.10-compatible standard-library code unless an
optional conversion dependency is clearly isolated. Keep dry runs free of
downloads and writes. Preserve existing files on failures and use tests that
exercise behavior rather than matching instructional wording.

Run the commands in [validation](docs/validation.md). Update related docs and
both Claude manifest versions when releasing a new version. Keep license copies
consistent. Do not commit private thesis material, credentials, caches, PDFs,
model weights, or generated reading copies.

Report a problem with the relevant command, OS, Python/assistant versions,
expected result, and a minimal non-confidential example. Remove secrets and
private source text from logs before sharing them.
