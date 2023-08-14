
# Automate the deployment of the infrastructure
terraform-plan: infrastructure/terraform/ infrastructure/terraform/main.tf infrastructure/terraform/variables.tf infrastructure/terraform/terraform.tfvars
	terraform -chdir=infrastructure/terraform/ plan -var-file=terraform.tfvars -out=terraform.tfplan
terraform-apply: terraform-plan
	terraform -chdir=infrastructure/terraform/ apply "terraform.tfplan"
terraform-docs: infrastructure/terraform/ infrastructure/terraform/main.tf
	terraform-docs markdown infrastructure/terraform/ --header-from main.tf --output-file README.md --indent 2

# Run the tests
tests: tests/ tests/**/test_*.py
	pytest -v tests/

# Deployment of flows
make-deployments: flows/orchestrator.py flows/media.py flows/oryx.py deployments/
	prefect deployments build flows/orchestrator.py:borderlands_flow \
		--name Daily \
		--description "Orchestrates the Oryx pipeline execution and dataset releases." \
		--infra-block ecs-task/ecs-task-oryx \
		--storage-block github-repository/github-repository-borderlands \
		--cron "0 12 * * *" \
		--timezone "America/New_York" \
		--tag "oryx" \
		--work-queue "default" \
		--skip-upload \
		--output "deployments/orchestrator-daily.yaml"
upload-deployments: deployments/orchestrator-daily.yaml
	prefect deployments apply deployments/orchestrator-daily.yaml
deployments-workflow: make-deployments upload-deployments

# Documentation generation
docs: docs/ docs/*.md tool.py
	python tool.py docs
