.PHONY: feature-store modeling advanced-dashboard ab-testing research validate test test-notebooks report-figures report

REPORT_TEX := [GROUP 7] Final Project Report.tex
REPORT_PDF := [GROUP 7] Final_Project_Report.pdf
REPORT_BUILD_DIR := build/report

feature-store:
	python scripts/run_feature_store.py

modeling:
	python scripts/run_multi_horizon_modeling.py

advanced-dashboard:
	python scripts/export_advanced_dashboard_tables.py

ab-testing:
	python scripts/export_ab_testing_tables.py

research:
	python scripts/run_research_pipeline.py

validate:
	python scripts/validate_research_outputs.py

test:
	python -m unittest discover -s tests -v

test-notebooks:
	RUN_NOTEBOOK_INTEGRATION=1 python -m unittest tests.test_notebook_execution -v

report-figures:
	python scripts/generate_report_figures.py

report: report-figures
	mkdir -p "$(REPORT_BUILD_DIR)"
	tectonic --outdir "$(REPORT_BUILD_DIR)" "$(REPORT_TEX)"
	cp "$(REPORT_BUILD_DIR)/[GROUP 7] Final Project Report.pdf" "$(REPORT_PDF)"
