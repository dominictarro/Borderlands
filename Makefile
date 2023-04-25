
# Automate the deployment of the infrastructure
terraform-plan: infrastructure/ infrastructure/main.tf infrastructure/variables.tf infrastructure/terraform.tfvars
	terraform -chdir=infrastructure plan -var-file=terraform.tfvars -out=terraform.tfplan
terraform-apply: terraform-plan
	terraform -chdir=infrastructure apply "terraform.tfplan"
terraform-destroy: infrastructure/ infrastructure/main.tf infrastructure/variables.tf infrastructure/terraform.tfvars
	terraform -chdir=infrastructure destroy -var-file=terraform.tfvars

# Automate the deployment of the pipeline
tests: tests/ tests/**/test_*.py
	pytest -v tests/
