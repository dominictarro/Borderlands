[![](../assets/borderlands%20soldier%20header.png)](https://www.midjourney.com/app/jobs/c2dff0de-6977-4260-9368-95ec2b0752e6/)

<a href="https://borderlands-core.s3.amazonaws.com/landing/latest.json" target="_blank"><img src="https://img.shields.io/badge/Latest_Dataset-fff"></a>

# Oryx

Oryx dataset documentation and notes.

## Introduction

The Oryx dataset is a collection of visually-confirmed equipment losses for the Russo-Ukrainian War. The dataset is maintained by an open source community and the Oryx moderators.

## Schema

The parent JSON object contains the `metadata` and `data` fields. The data fields contains a list of objects, each of which represents a confirmed loss.

Some fields came directly from the parsed Oryx page, and some were generated by Borderlands's Oryx processes.

| Column | Type | Origin | Description |
| --- | --- | --- | --- |
| `as_of_date` | `string` | borderlands | The record's extraction date. |
| `category` | `string` | oryx | Category of equipment that was lost. |
| `country` | `string` | oryx | Country that suffered the equipment loss. {*Russia*, *Ukraine*} |
| `country_of_production` | `string` | borderlands | ISO Alpha 3 country code that produces/produced the equipment model. |
| `country_of_production_flag_url` | `string` | oryx | URL to the flag of the country of production. |
| `description` | `string` | oryx | Raw description. |
| `domain` | `string` | borderlands | Domain of the URL to the visual evidence. |
| `evidence_source` | `string` | borderlands | Source of the visual evidence. {*postimg*, *twitter*, *other*} |
| `evidence_url` | `string` | oryx | URL to the visual evidence. |
| `failed_duplicate_check` | `boolean` | borderlands | True if there are multiple entires of a given `evidence_url`/`category`/`model`/`id_` combination. |
| `id_` | `string` | oryx | Unique ID for the loss (specific to `category`/`model`). |
| `media_key` | `string` | borderlands | Key to the extracted media. Only available in records after media extraction. |
| `model` | `string` | oryx | Model of equipment that was lost. |
| `source_file` | `string` | borderlands | Name of the source file the record was collected from. Used when media extraction is performed over all available records. |
| `status` | `list[string]` | borderlands | List of statuses that the loss has been assigned. {*abandoned*, *captured*, *damaged*, *destroyed*, *scuttled*, *stripped*, *sunk*, *raised*} |
| `url_hash` | `string` | borderlands | Hash of the `evidence_url`. |

### **Examples**

```json
{
    "as_of_date": "2023-05-05T06:27:55.585531+00:00",
    "category": "Tanks",
    "country": "Russia",
    "country_of_production": "SUN",
    "country_of_production_flag_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/23px-Flag_of_the_Soviet_Union.svg.png",
    "description": "1, captured",
    "domain": "i.postimg.cc",
    "evidence_source": "postimg",
    "evidence_url": "https://i.postimg.cc/yxw0SFD6/1001-T-62-Obr-1967-capt.jpg",
    "failed_duplicate_check": false,
    "id_": "1",
    "media_key": "postimg/e32852f22ee32db27b3733229e1e518a67443adf4c6fc40ce60690f1ac6f3b6a.jpg",
    "model": "T-62 Obr. 1967",
    "source_file": "oryx/landing/year=2023/month=05/day=22/hour=17/oryx_20230522.json",
    "status": [
        "captured"
    ],
    "url_hash": "e32852f22ee32db27b3733229e1e518a67443adf4c6fc40ce60690f1ac6f3b6a"
}
```

Evidence is largely composed of JPEGs and PNGs.

| 1 | 2 |
| --- | --- |
| ![Example of an image in Oryx media dataset.](../assets/example%20oryx%20media.jpeg) | ![Example of an image in Oryx media dataset.](../assets/example%20oryx%20media.png) |


## Access

### **Records**

Oryx loss records are free and publicly available via [HTTPS](https://borderlands-core.s3.amazonaws.com/landing/latest.json) and S3.

```shell
curl https://borderlands-core.s3.amazonaws.com/landing/latest.json -o latest.json
```

```shell
aws s3 cp s3://borderlands-core/landing/latest.json .
```

The record archive is organized by year, month, day, and hour.

```text
s3://borderlands-core/
  landing/
    latest.json
    year=2023/
      month=05/
        day=07/
          hour=00/
            oryx_20230507.json
```

### **Media**

The Oryx media files are publicly available via S3, but the requester (you) [shoulders the AWS transfer costs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ObjectsinRequesterPaysBuckets.html).

```shell
aws s3 ls s3://borderlands-media/postimg/
```

```shell
aws s3 cp s3://borderlands-media/postimg/$FILENAME .
```

The media archive is organized by media source.

```text
s3://borderlands-media/
  postimg/
    <url-hash>.jpg
    <url-hash>.jpg
    ...
```

Media files are named with the `url_hash` field found in records. These are SHA-256 hashes of the URL provided by the Oryx team. The file is untouched from the original source.
