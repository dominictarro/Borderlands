[![](./assets/borderlands%20soldier%20header.png)](https://www.midjourney.com/app/jobs/c2dff0de-6977-4260-9368-95ec2b0752e6/)

# Borderlands

ETL for Russo-Ukrainian war data.

- [Borderlands](#borderlands)
  - [Project Structure](#project-structure)
    - [Infrastructure](#infrastructure)
    - [Flows](#flows)
    - [Deployments](#deployments)
  - [Visually-confirmed equipment losses](#visually-confirmed-equipment-losses)
    - [Pages](#pages)
  - [References](#references)

## Project Structure

### Infrastructure

Terraform is used to build the AWS VPC and components. More can be found in [infrastructure](./infrastructure).

### Flows

Flows are organized into their own libraries within the [`borderlands`](./borderlands) library.

### Deployments

Deployments for production and testing are managed through `manage.py`.

Derived blocks are created from the parent set in the deployment definition. The `-s/--save` argument saves these blocks.

`-a/--apply` applies the deployment.

To create a development deployment

```bash
# Creates a test deployment that pulls code from the branch 'debug'.
# -o outputs the deployment to a yaml.
# --save saves the generated blocks.
python manage.py deploy borderlands.oryx.deployment::oryx_deployment\
  -r debug\
  -o ./test.yaml\
  --save
```

To create a production deployment

```bash
# Creates a production deployment that pulls code from the tag '1.1.3'.
# The generated blocks are saved.
# The deployment is applied.
python manage.py deploy --production\
  -r 1.1.3
  --save
  --apply
```

Development and production follow different naming conventions and build from parent blocks differently.

More can be found in [borderlands/deployer.py](./borderlands/deployer.py).

## Visually-confirmed equipment losses

The `borderlands.oryx` module is configured to scrape visually-confirmed equipment loss data
from [**Oryx**](https://www.oryxspioenkop.com/), a military analysis blog. You can donate to
the Oryx team at [Patreon](https://www.patreon.com/oryxspioenkop).

### Pages

- [Attack On Europe: Documenting Ukrainian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html)
- [Attack On Europe: Documenting Russian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html)

## References

- [ISO Codes](https://www.iso.org/obp/ui/#home)
