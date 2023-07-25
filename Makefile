
# Automate the deployment of the infrastructure
terraform-plan: infrastructure/ infrastructure/main.tf infrastructure/variables.tf infrastructure/terraform.tfvars
	terraform -chdir=infrastructure plan -var-file=terraform.tfvars -out=terraform.tfplan
terraform-apply: terraform-plan
	terraform -chdir=infrastructure apply "terraform.tfplan"
terraform-docs: infrastructure/ infrastructure/main.tf
	terraform-docs markdown infrastructure/ --header-from main.tf --output-file README.md --indent 2

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
