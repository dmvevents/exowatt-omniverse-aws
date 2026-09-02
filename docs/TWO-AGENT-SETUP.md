# Two-agent setup — laptop agent + EC2 jump-box agent

This POC runs as **two cooperating agents**: one on an EC2 jump box that runs the
Omniverse standup, and one on the operator's laptop that the operator actually
talks to.

| Agent | Where | What it is | Job |
|---|---|---|---|
| **EC2 jump-box agent** | a persistent control EC2 (the "standup" host) holding this repo + the provisioning IAM | Claude Code on **AWS Bedrock** | Runs the standup end-to-end — quota-check -> provision the g6e / L40S render host -> install Omniverse Kit -> first scene (`.claude/skills/omniverse-g6e-standup`). The backbone: holds this repo, Bedrock access, and the EC2/quota/Spot permissions; it **provisions and drives the g6e over SSH**. |
| **Laptop agent** | the operator's / Exowatt engineer's laptop | a **general coding agent** (Claude Code, Cursor, Codex, Windsurf, …) | The thing the operator talks to. It connects out to the jump box over SSH and drives the standup there. |

The operator talks to the **laptop agent** in plain language; the laptop agent
reaches the jump box over **SSH** and either runs one `make` target there or hands
a natural-language instruction to the jump-box agent. The standup always executes
**from the jump box** — that is where Bedrock access and the EC2/quota permissions
live. The **g6e / L40S Omniverse host** is the GPU render host the jump box brings
up and drives; it is not where the engineer logs in. Nothing is exposed to the
internet; everything rides SSH.

```
  engineer ── talks to ──▶ laptop agent ── SSH ──▶ jump-box agent (Claude/Bedrock)
  (plain language)         (general coder)         runs the Omniverse standup
                                 │                        │
                                 │                        ├── provisions ──▶ g6e / L40S render host
                                 └── agent/laptop-connect.sh ──┘              (Omniverse Kit, first scene)
                                     status · attach · run · ask · upload
```

Why two agents (not just SSH in and type)? Exowatt's engineers (Tim, Kamau)
already work in Claude Code + Bedrock. This lets them stay in their laptop agent:
they instruct it, it connects out, runs the standup on the properly-provisioned
jump box, and brings the answer back. The jump box stays the single place with
Bedrock + the EC2/quota/Spot IAM.

---

## Part A — Configure the EC2 jump-box agent (the backbone)

Owned by the AWS SA. This is the persistent control host that runs the standup
and provisions the g6e. Full detail is in `.claude/skills/claude-code-on-bedrock`
and `.claude/skills/bedrock-setup`; the checklist:

1. **Instance + repo.** A small Linux EC2 (tmux installed) with this repo cloned
   at `/home/ubuntu/exowatt-omniverse-aws` (or set `EXOWATT_REPO`). It does not
   need a GPU — it *provisions* the GPU host.
2. **Claude Code on Bedrock.** Install Claude Code; point it at Bedrock:
   ```bash
   export CLAUDE_CODE_USE_BEDROCK=1
   export AWS_REGION=us-east-1                               # the POC account's region
   export ANTHROPIC_MODEL="us.anthropic.claude-sonnet-4-6"  # a real us. inference-profile ID
   ```
   Prefer the jump box's **EC2 instance role** for credentials — no long-lived
   keys on disk (`.claude/skills/claude-code-on-bedrock`).
3. **Bedrock model access** granted in the region; verify with
   `aws bedrock list-inference-profiles --region us-east-1` — never guess IDs
   (`.claude/skills/bedrock-setup`). The customer currently **lacks direct
   Bedrock access** — that is the standup prerequisite (`docs/POC-PLAN.md`).
4. **IAM on the jump box's role** (least privilege, `docs/SETUP-GUIDE.md` §3):
   the **Bedrock** actions **plus** Service-Quotas (`GetServiceQuota`,
   `RequestServiceQuotaIncrease`) and EC2 provisioning (`RunInstances`,
   `RequestSpotFleet`, `Describe*`, `CreateTags`) so the standup can check the
   G/VT quota and launch the g6e (or the Spot fallback).
5. **Baseline green** (offline, no AWS spend, no GPU):
   ```bash
   make verify                                  # the offline harness self-test CI runs
   make plan                                    # print all four standup plans
   python3 harness/quota_check.py --dry-run     # the known blocker (G/VT On-Demand = 0)
   ```
6. **Start a tracked session** the laptop will attach to:
   ```bash
   agent/loop.sh standup    # named tmux session 'standup', transcript kept, reads agent/AUTOPILOT.md
   ```
   For a hands-off demo, run the session with auto-approved permissions
   (`claude --dangerously-skip-permissions`) so it does not stop on every tool
   call — see `.claude/skills/agent-loop`.
7. **Security group: inbound port 22 (SSH) only** on the jump box (or use SSM
   Session Manager and skip inbound SSH entirely). The g6e render host it
   provisions gets the same SSH-only treatment; any Omniverse streaming viewport
   is reached over an SSH tunnel, never a public listener.

---

## Part B — Configure the laptop agent + connection

Owned by each operator / Exowatt engineer, once.

> **On Windows?** Do the `windows-wsl-setup` skill first (WSL2 + Claude Code +
> SSH keygen inside WSL), then the steps below run unchanged inside the WSL
> Ubuntu shell. macOS/Linux users continue here directly.

1. **SSH access to the jump box.** Put the laptop's SSH public key on the jump
   box (`~/.ssh/authorized_keys` for the login user). Confirm a plain
   `ssh user@host` works before involving any agent.
2. **A general coding agent** installed on the laptop (Claude Code, Cursor,
   Codex CLI, Windsurf — any that can run shell commands). A laptop that only
   *connects to* the jump box does not need Bedrock creds of its own; the jump
   box holds Bedrock access.
3. **Point the laptop at the jump box.** Clone this repo on the laptop (for
   `agent/laptop-connect.sh`), then create `~/.exowatt-remote`:
   ```bash
   cat > ~/.exowatt-remote <<'CONF'
   EXOWATT_HOST=<jump-box-host-or-ip>
   EXOWATT_USER=ubuntu
   EXOWATT_KEY=~/.ssh/id_ed25519      # optional if your SSH config/agent handles it
   EXOWATT_REPO=/home/ubuntu/exowatt-omniverse-aws
   EXOWATT_TMUX=standup
   CONF
   ```
4. **Optional quick alias** to attach the live session in one word:
   ```bash
   # ~/.bashrc or ~/.zshrc
   alias exowatt='ssh -t <user>@<host> "tmux attach -t standup || tmux new -s standup"'
   ```

### The connection helper: `agent/laptop-connect.sh`

One SSH-only bridge the laptop agent (or a human) calls. It never opens a port.
Config comes from `~/.exowatt-remote` (or the `EXOWATT_*` env vars).

```bash
agent/laptop-connect.sh status                 # host reachable? 'standup' session up? + the quota headline
agent/laptop-connect.sh attach                 # interactive: join the live jump-box agent session
agent/laptop-connect.sh run "verify"           # run one MAKE TARGET on the jump box
agent/laptop-connect.sh run "quota"            # the G/VT quota check
agent/laptop-connect.sh run "provision"        # the on-demand g6e.4xlarge launch PLAN (dry-run)
agent/laptop-connect.sh ask "check the G/VT quota and plan the g6e launch"
agent/laptop-connect.sh upload ./exowatt-P3.step   # copy a CAD/CFD/Python input into scratch/uploads/
```

Three ways the laptop agent drives the standup:
- **`run "<make target>"`** — the laptop agent runs one `make` target on the jump
  box (`verify` / `plan` / `quota` / `provision` / `provision-spot` / `omniverse`
  / `scene`) and reads the plan JSON / self-test output. Deterministic; note this
  helper runs **`make <target>`**, not an arbitrary command.
- **`ask "<instruction>"`** — the laptop agent hands a plain-language instruction
  to the **jump-box Claude agent** (headless, `claude --dangerously-skip-permissions -p`),
  which routes it via `AGENTS.md` (`omniverse-g6e-standup`, `data-onboarding`,
  `first-scene-hello-omniverse`, …), runs it, and returns the narrated answer.
  Best for open-ended requests; this is agent-delegating-to-agent.
- **`upload <local-file>`** — copy an Exowatt input (CAD / CFD / Python) into the
  jump box's `scratch/uploads/` (gitignored), then `ask` the agent to onboard it
  (`data-onboarding`) and bring it toward a USD asset. The file never lands in
  git on either side.

---

## The instruction card — paste this to the laptop agent

Give the laptop coding agent this, once, as its standing instruction:

> You are my local coding agent. The Exowatt Omniverse standup runs on a remote
> EC2 **jump box** (it provisions and drives the g6e render host), reachable only
> over SSH. Use the helper `agent/laptop-connect.sh` in this repo to reach it —
> never try to open a network port.
>
> - First, run `agent/laptop-connect.sh status` and tell me if the jump box is
>   reachable, whether the `standup` session is live, and the G/VT quota headline.
> - When I ask standup questions (check the quota, plan the g6e launch, install
>   Omniverse, draw the first scene), either run the matching `make` target with
>   `agent/laptop-connect.sh run "<target>"` (e.g. `run "quota"`,
>   `run "provision"`) and summarize the plan JSON, **or** delegate the whole
>   request with `agent/laptop-connect.sh ask "<my request in plain language>"`
>   and relay the answer.
> - When I give you a CAD/CFD/Python file, run
>   `agent/laptop-connect.sh upload <path>`, then
>   `agent/laptop-connect.sh ask "onboard the file I just uploaded"`.
> - **Stop and check with me before the first live AWS spend** (any
>   RunInstances / RequestSpotFleet — the harness refuses `--run` on purpose),
>   anything leaving the machine (git push, publish), or anything destructive
>   (terminate instances, delete volumes). These are the human checkpoints in
>   `agent/AUTOPILOT.md`.
> - Always cite the evidence (the plan JSON path + values the jump box returns).
>   **Nothing is fabricated** — no fake instance IDs, no fake render frames; the
>   G/VT On-Demand quota is 0 today, so say so. Omniverse is the render layer;
>   Exowatt owns the physics (Titan) — don't invent physics results. Customer
>   inputs stay in `scratch/`; don't copy them to this laptop or commit them.
>
> Config lives in `~/.exowatt-remote` (host, user, key, repo, tmux session). If
> `status` fails, check that file and that my SSH key is on the jump box.

---

## The two-agent demo — `agent/demo-two-agents.sh`

A no-spend, offline narration of the operating pattern, for a customer-success
walkthrough. Here the "two agents" are the two **roles** the same pattern plays
on the standup:

```bash
agent/demo-two-agents.sh            # full narrated demo (both roles + the through-line)
agent/demo-two-agents.sh provision  # just the PROVISIONING role (quota -> g6e / Spot launch plan)
agent/demo-two-agents.sh render     # just the RENDER role (Omniverse install -> first USD scene)
```

Part 1 runs the real offline provisioning plan (`quota_check.py`,
`provision_g6e.py` on-demand and Spot) and surfaces the true blocker (On-Demand
G/VT quota = 0 -> Spot fallback); Part 2 runs the offline install + first-scene
plans. The through-line: one operating pattern (plain-language in, deterministic
plan out, kept audit trail, tmux-session-per-agent, live steps gated) applied to
both provisioning and rendering. See `docs/HARNESS-DEPLOY.md` for why this single
g6e host uses `agent/loop.sh` rather than the standalone agentic-harness.

---

## Verify the whole path (before the room)

```bash
# On the laptop, after ~/.exowatt-remote is set:
agent/laptop-connect.sh status
#   -> SSH reachable  +  agent session 'standup' is live  +  the offline quota headline

agent/laptop-connect.sh run "verify"
#   -> the offline harness self-test, green, computed on the jump box (no AWS, no GPU)

agent/laptop-connect.sh ask "in one line, what's the standup blocker right now?"
#   -> the jump-box agent's narrated one-liner (expected: On-Demand G/VT quota = 0)
```

If `status` fails: `ssh user@host` directly to isolate SSH vs config; check the
security group allows your IP on port 22; check `~/.exowatt-remote`.

## Security (non-negotiable)

- **SSH only.** Inbound security group = port 22 from known IPs (or SSM Session
  Manager, no inbound SSH). No app ports, never `0.0.0.0/0` except SSH — on both
  the jump box and the g6e it provisions. Any Omniverse viewport is reached over
  an SSH tunnel, never a public listener.
- **Customer inputs stay on the box.** CAD / CFD / Python and any derived USD
  live in `scratch/` (gitignored). The laptop copies them over `scp` via
  `upload`; they are never committed on either side.
- Prefer SSH keys + the jump box's **EC2 instance role** over any long-lived
  cloud keys on disk.
- **The boundary holds over the wire too:** Omniverse renders; Exowatt owns the
  physics (Titan). The agent never fabricates a launch, a host, or a physics
  result — the human checkpoints in `agent/AUTOPILOT.md` gate every live step.
