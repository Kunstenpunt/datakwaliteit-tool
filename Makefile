.PHONY: typecheck
typecheck:
	mypy --strict --follow-untyped-imports src/
.PHONY: test
test:
	pytest
.PHONY: format
format:
	black . --exclude "src/ui/designer"
.PHONY: build_ui
build_ui:
	python src/ui/designer/build.py
