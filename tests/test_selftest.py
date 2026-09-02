"""The bundled offline self-test must pass 5/5 with no AWS calls."""
import selftest


def test_selftest_registers_five_checks():
    assert len(selftest.CHECKS) == 5


def test_selftest_reports_all_plans_valid():
    assert selftest.main() == 0
