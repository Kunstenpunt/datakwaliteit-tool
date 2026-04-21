.PHONY: typecheck
typecheck:
	uv run mypy --strict --follow-untyped-imports src/
.PHONY: test
test:
	uv run pytest
.PHONY: format
format:
	uv run black ./src ./test --exclude "src/datakwaliteit_tool/ui/designer"
.PHONY: build_ui
build_ui:
	uv run python src/datakwaliteit_tool/ui/designer/build.py
.PHONY: run
run: build_ui format
	uv run python -m datakwaliteit_tool
.PHONY: release
release: build_ui format
	uv run pyside6-deploy -c pysidedeploy.spec
