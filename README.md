[![](./assets/borderlands%20soldier%20header.png)](https://www.midjourney.com/app/jobs/c2dff0de-6977-4260-9368-95ec2b0752e6/)

# Borderlands

<a href="https://patreon.com/tarrodot" target="_blank"><img src="https://img.shields.io/badge/Donate-Patreon-blue"></a>
<a href="https://borderlands-core.s3.amazonaws.com/landing/latest.json" target="_blank"><img src="https://img.shields.io/badge/Oryx_Dataset-fff"></a>

*ETL for Russo-Ukrainian war data.*

- [Borderlands](#borderlands)
  - [Introduction](#introduction)
  - [Project Structure](#project-structure)
    - [Infrastructure](#infrastructure)
    - [Flows](#flows)
    - [Deployments](#deployments)
    - [Prefect UI](#prefect-ui)
  - [Visually-confirmed equipment losses](#visually-confirmed-equipment-losses)
    - [Access](#access)
      - [Records](#records)
      - [Media](#media)
    - [Pages](#pages)
  - [References](#references)

## Introduction

This project was started with the objective of making the Oryx's visually-confirmed losses for the Russo-Ukrainian War more accessible for analysis. While I am personally incurring the AWS costs, I greatly appreciate [donations](https://patreon.com/tarrodot?utm_medium=clipboard_copy&utm_source=copyLink&utm_campaign=creatorshare_creator&utm_content=join_link) to help support the maintenance and growth of this project. Borderlands was built such that others may replicate the system privately should they choose to do so.

## Project Structure

### Infrastructure

Terraform is used to build the AWS VPC and the assets within it. More can be found in [infrastructure](./infrastructure).

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

### Prefect UI

The system will result in a Flow UI like this.

![Oryx Flows and Deployments](./assets/flows%20and%20deployments.png)

A Blocks UI like this.

![Oryx Blocks](./assets/blocks.png)

## Visually-confirmed equipment losses

The `borderlands.oryx` module is configured to scrape visually-confirmed equipment loss data
from [**Oryx**](https://www.oryxspioenkop.com/), a military analysis blog. You can donate to
the Oryx team at [Patreon](https://www.patreon.com/oryxspioenkop).

### Access

#### Records

Oryx loss records are free and publicly available via [HTTPS](https://borderlands-core.s3.amazonaws.com/landing/latest.json) and S3.

```shell
curl https://borderlands-core.s3.amazonaws.com/landing/latest.json -o latest.json
```

```shell
aws s3 cp s3://borderlands-core/landing/latest.json .
```

#### Media

The media files are publicly available via S3, but the requester (you) [shoulders the AWS costs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ObjectsinRequesterPaysBuckets.html).

```shell
aws s3 ls s3://borderlands-media/postimg/
```

```shell
aws s3 cp s3://borderlands-media/postimg/$FILENAME .
```

### Pages

- [Attack On Europe: Documenting Ukrainian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html)
- [Attack On Europe: Documenting Russian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html)

## References

- [ISO Codes](https://www.iso.org/obp/ui/#home)
- [Infrastructure](./infrastructure/README.md)
