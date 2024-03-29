[![](./assets/borderlands%20soldier%20header.png)](https://www.midjourney.com/app/jobs/c2dff0de-6977-4260-9368-95ec2b0752e6/)

# Borderlands

<a href="https://www.kaggle.com/dominictarro/borderlands" target="_blank"><img src="https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white"></a>
<a href="https://patreon.com/tarrodot" target="_blank"><img src="https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white"></a>
<a href="https://dominictarro.github.io/Borderlands/" target="_blank"><img src="https://img.shields.io/badge/Documentation-indigo?style=for-the-badge&logo=gitbook&logoColor=white"></a>

The *Borderlands* project is a publicized collection of high-granularity datasets related to the Russo-Ukrainian War.

## About

This project was started with the objective of making the Oryx's visually-confirmed losses for the Russo-Ukrainian War more accessible for analysis. While I am personally incurring the AWS costs, I greatly appreciate [donations](https://patreon.com/tarrodot?utm_medium=clipboard_copy&utm_source=copyLink&utm_campaign=creatorshare_creator&utm_content=join_link) to help support the maintenance and growth of this project. Borderlands was built such that others may replicate the system privately should they choose to do so.

## Access

The JSON form of the Oryx dataset is available for download on [Kaggle](https://www.kaggle.com/dominictarro/borderlands).

## References

- [Attack On Europe: Documenting Ukrainian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html)
- [Attack On Europe: Documenting Russian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html)
- [List Of Naval Losses During The Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/03/list-of-naval-losses-during-2022.html)
- [List Of Aircraft Losses During The Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/03/list-of-aircraft-losses-during-2022.html)
- [ISO Codes](https://www.iso.org/obp/ui/#home)
- [Infrastructure](./infrastructure/README.md)

## For Developers

### Infrastructure

The core infrastructure for this project is built on AWS.

#### Prefect Generated Infrastructure

```sh
prefect work-pool create --type ecs:push --provision-infra ecs-pool
```

You will be prompted for custom names. Choose no.

Once that is done, you have to update the `PrefectEcsTaskExecutionRole` with the
AWS-managed policy `AmazonEC2ContainerRegistryReadOnly` for reading the Docker image
from ECR.

#### Self-managed Infrastructure

Set up the other AWS resources using the following commands:

```sh
terraform -chdir=infrastructure/terraform/ plan -var-file=terraform.tfvars -out=terraform.tfplan
# Review the plan
terraform -chdir=infrastructure/terraform/ apply "terraform.tfplan"
# Update the docs (if applicable)
terraform-docs markdown infrastructure/terraform/ --header-from main.tf --output-file README.md --indent 2
````

[Read more](./infrastructure/terraform/README.md)
