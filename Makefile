
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
