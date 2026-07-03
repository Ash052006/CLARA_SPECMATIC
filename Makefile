.PHONY: test test-contract test-smoke stub virtualize compatibility resilience run lint clean

test: test-smoke test-contract compatibility resilience

test-contract:
	powershell -ExecutionPolicy Bypass -File scripts/run_specmatic_tests.ps1

resilience:
	powershell -ExecutionPolicy Bypass -File scripts/run_resilience_tests.ps1

test-smoke:
	pytest

stub:
	powershell -ExecutionPolicy Bypass -File scripts/run_specmatic_stub.ps1

virtualize: stub

compatibility:
	powershell -ExecutionPolicy Bypass -File scripts/run_backward_compatibility_check.ps1

run:
	uvicorn main:app --reload

lint:
	python -m compileall .

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', 'htmlcov']]; [p.unlink(missing_ok=True) for p in pathlib.Path('.').rglob('*.pyc')]"
