<p align="center">
    <img src="Hermes_Agents_Ensemble.png"
</p>

# Agent Skills

A curated collection of Hermes Agent skills, written by the Apartment38 team and Hermes agents. Each skill is a self-contained, documented procedure for a specific task type — loading the `hermes-agent` skill is always the first step when interacting with Hermes itself.

## Installation

Hermes loads skills from its profile skills directory. To install this repo:

```bash
# 1. Clone into your Hermes profile skills directory
git clone https://github.com/Apartment38/Agent-Skills.git \
  ~/.hermes/profiles/default/skills/agent-skills

# 2. Reload skills
hermes skills reload
```

After installation, load any skill at runtime with:

```python
skill_view(name="agent-skills/<category>/<skill-name>")
```

Or browse the full catalogue:

```bash
hermes skills list
```

> **Prerequisite:** Hermes Agent must be installed. See the official documentation at https://hermes-agent.nousresearch.com/docs for setup and profile management.

## Available Skills

| Category | Skill | Description |
|---|---|---|
| [autonomous-ai-agents](autonomous-ai-agents/) | [external-memory-providers](autonomous-ai-agents/external-memory-providers/) | Install, configure, and verify third-party memory providers for Hermes while keeping them isolated from Hermes' managed venv. |
| [autonomous-ai-agents](autonomous-ai-agents/) | [hermes-model-routing](autonomous-ai-agents/hermes-model-routing/) | Configure Hermes default, fallback, and auxiliary model routes from live account availability and measured local performance. |
| [autonomous-ai-agents](autonomous-ai-agents/) | [hermes-skin-maintenance](autonomous-ai-agents/hermes-skin-maintenance/) | Audit, extend, or repair a Hermes skin while preserving its visual character across the CLI, TUI, and desktop app. |
| [autonomous-ai-agents](autonomous-ai-agents/) | [hermes-tool-overhead-audit](autonomous-ai-agents/hermes-tool-overhead-audit/) | Measure tool-catalog context-window cost and verify whether Tool Search or Tool Slimmer is genuinely selecting schemas. |
| [autonomous-ai-agents](autonomous-ai-agents/) | [parallel-agent-delegation](autonomous-ai-agents/parallel-agent-delegation/) | Fan work out to multiple subagents safely by assigning exclusive file ownership and forbidding shared-write collisions. |
| [creative](creative/) | [agent-theme-copy](creative/agent-theme-copy/) | Draft compact, internally consistent agent theme microcopy: status faces, thinking verbs, and decorative glyphs. |
| [devops](devops/) | [container-service-troubleshooting](devops/container-service-troubleshooting/) | Diagnose and repair Podman/Docker Compose stacks where a service fails despite components appearing healthy. |
| [eleventy-reusable-theme-plugin](eleventy-reusable-theme-plugin/) | [eleventy-reusable-theme-plugin](eleventy-reusable-theme-plugin/) | Build reusable Eleventy 3 theme plugins that own layouts and assets while preserving site-owned directories and metadata. |
| [github-bot-plugin-testing](github-bot-plugin-testing/) | [github-bot-plugin-testing](github-bot-plugin-testing/) | Run isolated Git wrapper tests with a clean child PATH so no active middleware launcher interferes with the test wrapper. |
| [linux-stale-drive-mounts](linux-stale-drive-mounts/) | [linux-stale-drive-mounts](linux-stale-drive-mounts/) | Recover disconnected filesystem mounts that return I/O errors, distinguishing hardware failure from stale device mappings. |
| [mlops](mlops/) | [hermes-local-tts](mlops/hermes-local-tts/) | Set up and troubleshoot on-device Hermes TTS providers (KittenTTS, Piper, Neutts) and their configuration keys. |
| [mlops](mlops/) | [llm-model-evaluation](mlops/llm-model-evaluation/) | Evaluate cloud and local LLMs on the hardware and account that will serve them, then turn evidence into Hermes routes. |
| [mlops](mlops/) | [ollama-model-variants](mlops/ollama-model-variants/) | Create, register, and validate local Ollama model variants sized for the host's CPU/GPU/RAM with reproducible Modelfiles. |
| [mlops](mlops/) | [ollama](mlops/ollama/) | Determine the real Ollama service endpoint, context sizing, and GPU offload path (Vulkan vs ROCm vs CUDA) for a host. |
| [research](research/) | [deep-research-methodology](research/deep-research-methodology/) | Run an iterative multi-source web research loop with cited reports, producing a synthesis that stops on explicit sufficiency. |
| [software-development](software-development/) | [verify-local-web-app](software-development/verify-local-web-app/) | Verify a local web app end-to-end: real UI drives the real backend, persistence survives outside the browser, and servers are stopped. |

## License

MIT — see each skill's front matter for per-skill licensing where it differs.
