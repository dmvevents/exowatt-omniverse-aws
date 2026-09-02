---
name: ngc-api-key
description: Use when you need to pull NVIDIA Omniverse Kit containers or assets from nvcr.io and no NGC_API_KEY is set, or when docker login to nvcr.io fails with unauthorized. Walks getting the key, storing it safely, and verifying the pull on the g6e host.
---

# Get and use an NGC API key

Pulling NVIDIA Omniverse Kit containers / assets from `nvcr.io` requires an
NVIDIA NGC API key. Without it, `docker pull` returns
`unauthorized: authentication required`. This runs on the **g6e host**, as part
of the `omniverse_setup` install step that fetches Kit.

## 1. Generate the key (human step — hand this to the user)

1. Go to https://ngc.nvidia.com and sign in (create a free account if needed;
   company email preferred so pulls tie to the org).
2. Top-right avatar -> **Setup** -> **Generate API Key** -> **Generate**.
3. Copy the key NOW — NGC shows it once. It starts with `nvapi-`.

## 2. Store it (never in git)

```bash
# Shell profile on the g6e host:
echo 'export NGC_API_KEY=nvapi-...' >> ~/.bashrc && source ~/.bashrc
```

Rules: the key never goes in a committed file, a Dockerfile, a log, or a chat
message. `.env` is gitignored (as are `*.env`, `*.pem`, `*.key`) and acceptable
for a single sandbox host.

## 3. Log in and verify

```bash
docker login nvcr.io
# username: $oauthtoken        <- literally that string
# password: <the NGC_API_KEY>
```

Then pull the Omniverse Kit container / assets per the current NVIDIA Omniverse
Kit documentation, and confirm the image is present:

```bash
docker images | grep -i kit    # the pulled Kit image should be listed
```

## 4. Avoid NGC throttling

For repeated standups, mirror the pulled image to the customer's ECR once, then
pull from ECR — the host never depends on NGC bandwidth at run time.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `unauthorized` on pull | key wrong/expired, or username not `$oauthtoken` | regenerate key, re-login |
| pull painfully slow | NGC throttling | mirror to ECR, pull from there |
| `docker: permission denied` | user not in the `docker` group | `sudo usermod -aG docker $USER` then re-login |
