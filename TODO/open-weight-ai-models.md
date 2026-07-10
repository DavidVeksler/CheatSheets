# Open-Weight AI Models Compared

**Target file:** `open-weight-ai-models.html`
**Category:** AI & Safety

## Why this topic

People who want to run capable AI themselves face a materially different decision from people choosing a hosted frontier provider: licence, model weights, hardware, quantisation, runtime, privacy, and support all matter. This page should be the practical companion to `ai-frontier.html`, not another general list of AI labs. Its reader leaves able to choose a legitimate open-weight candidate and a realistic local or self-hosted deployment path.

## Targeting

- **Primary query:** `open weight ai models`
- **Secondary queries:** `open source llm comparison`, `llama vs qwen vs deepseek`, `best local llm`, `self hosted ai models`, `open weight model license`
- **Search mode:** research with a deployment decision at the end.
- **Title:** `Open-Weight AI Models: Llama, Qwen, DeepSeek & Mistral`
- **H1:** `Open-Weight AI Models Compared: Run, License, and Choose`
- **Meta description:** `Compare open-weight AI models from Llama, Qwen, DeepSeek, Mistral and more: licensing, hardware, local runtimes, privacy, context, and deployment tradeoffs.`
- **Reader outcome:** choose a model family, runtime, and deployment shape that fits a real privacy, hardware, and licensing constraint.
- **Success metric:** organic entries for open-weight comparison queries plus outbound use of the local-install links.
- **Geographic scope:** global; licences, regional availability, and cloud terms must be stated precisely where they vary.
- **Reading conditions:** developers reading at a workstation before spending time downloading models or provisioning GPU capacity; dense desktop table with a horizontally scrollable mobile version and useful print summary.

## Staleness register

**Overall: VOLATILE.** Model names, released weights, licences, context windows, hardware guidance, and benchmark results change quickly.

- **Model availability / released weights:** verify each build against the owner’s official release or model card.
- **Licence terms:** verify against the exact upstream licence text; never call a model “open source” unless the licence supports that label.
- **Hardware / quantisation examples:** verify against the runtime documentation and label them as examples, not guarantees.
- **Benchmarks:** cite the benchmark owner, model version, harness, and date; never compare unlike harnesses as a single ranking.

## Content approach

### Quick reference

- A decision table with at least 12 entries across current model families and sizes: model family, weight availability, licence, suitable runtime, rough hardware class, strongest fit, and a primary-source link.
- A four-question chooser: offline/privacy requirement, hardware class, language/modality, and commercial/licensing constraint.
- One fully worked realistic path: a developer with a single consumer GPU choosing a local coding assistant, including what they should verify before downloading.

### Fundamentals

- Define open weight, open source, downloadable, self-hosted, local, and API-hosted; distinguish them clearly.
- Explain parameter count, quantisation, context window, VRAM/RAM, tokens per second, and why model cards matter.
- Comparison table: local, self-hosted, managed open-model API, and closed API across privacy, operational burden, update control, cost visibility, and support.

### Working knowledge

- Family profiles for Llama, Qwen, DeepSeek, Mistral, Gemma, and other inclusion-qualified providers, with official sources and clear scope limits.
- Runtime decision matrix: Ollama, llama.cpp, vLLM, and a managed-host route; state what each is for and where it is a poor choice.
- Licence and distribution checklist; include a concrete deployment-review example.
- Evaluation recipe: hold-out prompts, structured-output test, tool-call test, latency, memory, and failure logging.

### Edge and advanced

- Quantisation tradeoffs, batching, KV cache, context-length claims, multimodal support, and tool/function calling.
- Supply-chain, model-file, prompt-injection, data-retention, and GPU-driver pitfalls.
- Common mistakes / anti-patterns: calling all downloadable models open source; trusting leaderboard averages; ignoring licence conditions; selecting by parameter count alone; running untrusted model packages; treating a demo as production capacity.

## Cross-link map

- **Inbound:** `ai-frontier.html` as the provider landscape; `ubuntu-linux-for-ai-developers.html` as the host setup guide.
- **Outbound:** `ubuntu-linux-for-ai-developers.html` for installation; `ai-model-picker.html` for hosted-model choice; `ai-coding-agents-compared.html` when the use case is coding agents.
- Do not duplicate the provider-history, safety-framework, or AGI-goal content of `ai-frontier.html`.

## Research sources

- Exact upstream licence/model-card/release page for every row.
- Official documentation for each runtime and official GPU/runtime compatibility documentation for any hardware claim.
- Benchmark-owner pages for every benchmark statement.
- The Frontier Model Forum definition only for terminology context; it is not evidence that a specific model belongs in the table.

## Visual design

- **Aesthetic:** field notebook / deployment console: deep graphite background, restrained signal green, hardware-blue, and licence-amber accents.
- **Signature visual:** a visible “deployment path” chooser that routes from privacy and hardware constraints to local, self-hosted, managed-open, or closed API—not a fake live benchmark leaderboard.
- **OG image:** the four-path chooser and headline, at 1200×630.
- **Mobile / print:** chooser stacks vertically; large comparison table scrolls; a one-page deployment checklist prints cleanly.
