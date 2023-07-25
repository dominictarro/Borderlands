[![](../assets/borderlands%20soldier%20header.png)](https://www.midjourney.com/app/jobs/c2dff0de-6977-4260-9368-95ec2b0752e6/)

# Media

Media dataset documentation and notes.

## Introduction

The Media dataset is a collection of media files that were extracted from the Oryx dataset.

## Schema

| Column | Type | Origin | Description |
| --- | --- | --- | --- |
| `as_of_date` | `string` | borderlands | The record's extraction date. |
| `file_type` | `string` | borderlands | File type. {*jpg*, *png*, *unknown*} |
| `media_key` | `string` | borderlands | S3 key to the media file. |
| `media_type` | `string` | borderlands | Media type. {*image*} |
| `url` | `string` | oryx | URL to the media file. |
| `url_hash` | `string` | borderlands | Hash of the `url`. |

## Access

An inventory of downloaded media can be retrieved with:

```shell
aws s3 cp s3://borderlands-core/releases/media-inventory.parquet .
```

Images can be found at the following location:

```shell
aws s3 ls s3://borderlands-core/media/postimg/
```

```shell
aws s3 cp s3://borderlands-core/media/postimg/$FILENAME .
```

The media archive is organized by media source.

```text
s3://borderlands-core/
  releases/
    media-inventory.parquet
  media/
    postimg/
      <url-hash>.jpg
      <url-hash>.jpg
      ...
```

Media files are named with the `url_hash` field found in records. These are SHA-256 hashes of the URL provided by the Oryx team. The file is untouched from the original source.
