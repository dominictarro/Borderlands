![Borderlands](https://raw.githubusercontent.com/dominictarro/Borderlands/719584af68326f8263f5935743d3c86cc62e2515/assets/borderlands%20soldier%20header.png)

<a href="https://github.com/dominictarro/Borderlands" target="_blank"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://patreon.com/tarrodot" target="_blank"><img src="https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white"></a>

The *Borderlands* project is a public collection of high-granularity datasets related to the Russo-Ukrainian War.

*This dataset is currently private.*

<!-- BEGIN SCHEMA SECTION -->

## Media Inventory

The Media Inventory is a collection of evidence files that were extracted from the Oryx dataset.

### Supported Sources

 - [Postimages](https://postimg.cc/)

### Schema

| Name | Type | Description |
| :--- | :--- | :----------- |
| url_hash | string | A SHA-256 hash of the `url`. |
| url | string | The URL to the evidence. |
| evidence_source | string | The source of the evidence. |
| media_key | string | The S3 Object Key to the media. |
| file_type | string | The file type/extension. |
| media_type | string | The media classification. |
| as_of_date | datetime | The date the row was generated. |

<!-- END SCHEMA SECTION -->

### Evidence Media

Evidence is largely composed of JPEGs and PNGs.

| 1 | 2 |
| --- | --- |
| ![Example of an image in Oryx media dataset.](../assets/example%20oryx%20media.jpeg) | ![Example of an image in Oryx media dataset.](../assets/example%20oryx%20media.png) |
