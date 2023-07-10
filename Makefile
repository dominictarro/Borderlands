
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
make-deployments: flows/oryx_stage.py flows/oryx_media.py deployments/
	prefect deployments build flows/oryx_stage.py:stage_oryx_equipment_losses \
		--name Daily \
		--description "Scrapes the Oryx site for visually-confirmed equipment losses." \
		--infra-block ecs-task/ecs-task-oryx \
		--storage-block github-repository/github-repository-borderlands \
		--cron "0 12 * * *" \
		--timezone "America/New_York" \
		--tag "oryx" \
		--work-queue "default" \
		--skip-upload \
		--output "deployments/oryx-staging-daily.yaml"

	prefect deployments build flows/oryx_media.py:extract_oryx_media \
		--name Trigger \
		--description "Downloads images to the media bucket if they haven't been already." \
		--infra-block ecs-task/ecs-task-oryx \
		--storage-block github-repository/github-repository-borderlands \
		--tag "oryx" \
		--tag "trigger" \
		--work-queue "default" \
		--skip-upload \
		--output "deployments/oryx-media-trigger.yaml"
upload-deployments: deployments/oryx-staging-daily.yaml deployments/oryx-media-trigger.yaml
	prefect deployments apply deployments/oryx-staging-daily.yaml
	prefect deployments apply deployments/oryx-media-trigger.yaml
deployments-workflow: make-deployments upload-deployments
