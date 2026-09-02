---
name: windows-wsl-setup
description: Use when an Exowatt engineer is on a Windows laptop and needs to run Claude Code and reach the EC2 Omniverse standup agent. Covers installing WSL2, Claude Code inside WSL, SSH key generation, putting the key on the EC2, the ~/.exowatt-remote config, and matching the terminal window to the tmux session. This is the Windows path for the two-agent setup.
---

# Windows laptop -> WSL2 -> Claude Code -> EC2 Omniverse agent

Claude Code and the SSH/tmux workflow run cleanly inside **WSL2** (Windows
Subsystem for Linux) — that's the supported Windows path. This skill takes a
Windows laptop from nothing to "connected to the EC2 agent and running the
standup." Do this **before** the session, not the morning of.

## 1. Install WSL2 (one command, then reboot)

In an **Administrator** PowerShell:

```powershell
wsl --install -d Ubuntu
```

Reboot when prompted. On first launch Ubuntu asks for a UNIX username +
password (local to WSL — not the AWS account). If WSL is already present:

```powershell
wsl --set-default-version 2
wsl --install -d Ubuntu-24.04
```

Verify (PowerShell): `wsl -l -v` -> Ubuntu should show `VERSION 2`. From here,
**everything runs inside the Ubuntu (WSL) shell**, not PowerShell. Use
**Windows Terminal** (Microsoft Store) — it matters for tmux window sizing in
step 6.

## 2. Base tooling inside WSL

```bash
sudo apt update && sudo apt install -y git tmux openssh-client curl python3 python3-venv
git --version && tmux -V && ssh -V        # sanity
```

## 3. Install Claude Code inside WSL

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version                          # confirm it's on PATH
```

Point Claude Code at Bedrock exactly as `claude-code-on-bedrock` describes. A
laptop that only *connects to* the EC2 does not need Bedrock creds (the EC2
holds Bedrock access); it needs its own config only if it runs Claude locally.

## 4. Generate an SSH key (in WSL) and put it on the EC2

```bash
ssh-keygen -t ed25519 -C "exowatt-standup-$(whoami)"    # accept defaults; a passphrase is fine
cat ~/.ssh/id_ed25519.pub                                # copy this PUBLIC key
```

Give the **public** key to the AWS SA, who adds it to the EC2 login user's
`~/.ssh/authorized_keys`. Never share the private key
(`~/.ssh/id_ed25519` with no `.pub`). Test the raw connection first:

```bash
ssh <user>@<ec2-host> "echo connected; hostname"
```

## 5. Clone the repo + point at the EC2

```bash
git clone git@github.com:dmvevents/exowatt-omniverse-aws.git ~/exowatt-omniverse-aws
cd ~/exowatt-omniverse-aws
cat > ~/.exowatt-remote <<'CONF'
EXOWATT_HOST=<ec2-host-or-ip>
EXOWATT_USER=ubuntu
EXOWATT_KEY=~/.ssh/id_ed25519
EXOWATT_REPO=/home/ubuntu/exowatt-omniverse-aws
EXOWATT_TMUX=standup
CONF
```

Now the connection helper works:

```bash
./agent/laptop-connect.sh status      # reachable, session state, quota headline
./agent/laptop-connect.sh attach      # join the live EC2 agent session
```

## 6. Match the terminal window to the tmux session

tmux resizes the shared session to the **smallest** attached client. Before
attaching: use Windows Terminal, maximized, a readable font. If cramped after
attaching, on the host run `tmux attach -d -t standup` to detach other clients,
or inside tmux `Ctrl-b :` then `resize-window -A`.

## 7. Verify the whole path

```bash
./agent/laptop-connect.sh status
./agent/laptop-connect.sh run "verify"
./agent/laptop-connect.sh ask "check the G/VT quota and tell me the standup blocker in one line"
```

## Windows gotchas (the ones that actually bite)

| Symptom | Cause | Fix |
|---|---|---|
| `wsl --install` "not recognized" | old Windows build | update Windows, or enable "Virtual Machine Platform" + "WSL" features manually |
| SSH key "permissions too open" | key edited from Windows side | keep the key in WSL's `~/.ssh`, `chmod 600 ~/.ssh/id_ed25519` |
| `ssh` works, `laptop-connect.sh status` says host unset | `~/.exowatt-remote` missing/typo | recreate it (step 5); it's a WSL home file, not Windows |
| CRLF errors running the `.sh` helper | file cloned with Windows line endings | `git config --global core.autocrlf input` before cloning, or `dos2unix agent/*.sh` |
| tmux tiny / garbled | small or non-Windows-Terminal client | maximize Windows Terminal; detach other clients (step 6) |

Related: `claude-code-on-bedrock` (pointing Claude at Bedrock), `agent-loop`
(the tmux session on the EC2), `omniverse-g6e-standup` (the mission it runs).
