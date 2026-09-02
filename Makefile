# Exowatt Omniverse-on-AWS standup harness - common tasks
#
# Every target here is OFFLINE and SAFE: the harness plans are pure standard
# library, boto3 is imported lazily, and no target launches an instance,
# installs on a host, or renders a frame. There is no GPU dependency and no
# AWS spend. Live paths are gated TODOs inside the harness modules.

.DEFAULT_GOAL := help
PYTHON ?= python3

.PHONY: help preflight verify test plan quota provision provision-spot omniverse scene clean

help:
	@echo "Exowatt Omniverse-on-AWS standup - common tasks"
	@echo ""
	@echo "  make verify         - offline harness self-test (what CI runs; no AWS, no GPU)"
	@echo "  make test           - offline pytest suite (pip install -r requirements-dev.txt)"
	@echo "  make plan           - print all four standup plans (human-readable)"
	@echo "  make quota          - GPU (G/VT) vCPU quota check (offline baseline)"
	@echo "  make provision      - the on-demand g6e.4xlarge launch plan"
	@echo "  make provision-spot - the Spot Fleet g6.24xlarge fallback plan"
	@echo "  make omniverse      - the headless Omniverse Kit install plan"
	@echo "  make scene          - the 'hello Omniverse' USD scene target"
	@echo "  make clean          - remove __pycache__ and scratch artifacts"

# Fail early and clearly if the interpreter is too old.
preflight:
	@$(PYTHON) -c "import sys; v=sys.version_info; \
ok = v >= (3, 11); \
print(f'Python {v.major}.{v.minor}.{v.micro} OK') if ok else \
sys.exit(f'Python {v.major}.{v.minor} is too old - this POC needs 3.11+.')"

# The one target CI runs. Offline, stdlib-only, no AWS spend, no GPU.
verify: preflight
	$(PYTHON) harness/selftest.py
	@echo ""
	@echo "All offline standup plans validated (no AWS calls, no GPU, no spend)."

plan: quota provision provision-spot omniverse scene

quota:
	$(PYTHON) harness/quota_check.py --dry-run

provision:
	$(PYTHON) harness/provision_g6e.py --dry-run

provision-spot:
	$(PYTHON) harness/provision_g6e.py --strategy spot --dry-run

omniverse:
	$(PYTHON) harness/omniverse_setup.py --plan

scene:
	$(PYTHON) harness/first_scene.py --dry-run

clean:
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	rm -rf scratch/ 2>/dev/null || true
	@echo "cleaned."

# Offline pytest suite. Mocks all boto3/AWS; no network, no GPU, no spend.
# Needs pytest:  pip install -r requirements-dev.txt
test: preflight
	$(PYTHON) -m pytest -q
