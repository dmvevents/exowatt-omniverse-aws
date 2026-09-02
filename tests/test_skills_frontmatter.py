"""Smoke test: every .claude/skills/*/SKILL.md has name + description front-matter.

Pure stdlib (no PyYAML): parse the leading '---' fenced block and check keys.
"""
import glob
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


def _skill_files():
    return sorted(glob.glob(os.path.join(_ROOT, ".claude", "skills", "*", "SKILL.md")))


def test_skills_present():
    assert len(_skill_files()) >= 10


def test_every_skill_has_name_and_description():
    for path in _skill_files():
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        m = _FRONT_MATTER.match(text)
        assert m, f"{path}: missing leading '---' front-matter block"
        fm = m.group(1)
        assert re.search(r"(?m)^name:\s*\S", fm), f"{path}: front-matter missing non-empty 'name'"
        assert re.search(r"(?m)^description:\s*\S", fm), f"{path}: front-matter missing non-empty 'description'"
