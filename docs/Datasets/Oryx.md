# Oryx

The Oryx dataset is a complete collection of the equipment losses in the Oryx database. The loss cases have been cleaned and transformed into JSON objects.

## Sources

- [Attack On Europe: Documenting Ukrainian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html)
- [Attack On Europe: Documenting Russian Equipment Losses During The 2022 Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html)
- [List Of Naval Losses During The Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/03/list-of-naval-losses-during-2022.html)
- [List Of Aircraft Losses During The Russian Invasion Of Ukraine](https://www.oryxspioenkop.com/2022/03/list-of-aircraft-losses-during-2022.html)

## Schema

<!-- BEGIN SCHEMA SECTION -->

| Name                           | Type         | Description                                                                                                              |
|:-------------------------------|:-------------|:-------------------------------------------------------------------------------------------------------------------------|
| country                        | string       | The country that suffered the equipment loss.                                                                            |
| category                       | string       | The equipment category.                                                                                                  |
| model                          | string       | The equipment model.                                                                                                     |
| url_hash                       | string       | A SHA-256 hash of the `evidence_url`.                                                                                    |
| case_id                        | numeric      | A special ID for discriminating equipment losses when their `country`, `category`, `model`, and `url_hash` are the same. |
| status                         | list(string) | The statuses of the equipment loss.                                                                                      |
| evidence_url                   | string       | The URL to the evidence of the equipment loss.                                                                           |
| country_of_production          | string       | The ISO Alpha-3 code of the country that produces the `model`.                                                           |
| country_of_production_flag_url | string       | The URL to the flag of the country that produces the `model`.                                                            |
| evidence_source                | string       | The source of the evidence.                                                                                              |
| description                    | string       | The Oryx description the equipment loss was extracted from.                                                              |
| id_                            | numeric      | The Oryx ID the equipment loss was labeled with.                                                                         |
| as_of_date                     | datetime     | The date the row was generated.                                                                                          |

<!-- END SCHEMA SECTION -->

The `url_hash` is used as a file name and identifier for downloaded media from the [Media Inventory](./Media%20Inventory.md) dataset.

## Examples

```json
{
    "as_of_date": "2023-05-05T06:27:55.585531+00:00",
    "case_id": 1,
    "category": "Tanks",
    "country": "Russia",
    "country_of_production": "SUN",
    "country_of_production_flag_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/23px-Flag_of_the_Soviet_Union.svg.png",
    "description": "1, captured",
    "evidence_source": "postimg",
    "evidence_url": "https://i.postimg.cc/yxw0SFD6/1001-T-62-Obr-1967-capt.jpg",
    "id_": 1,
    "model": "T-62 Obr. 1967",
    "status": [
        "captured"
    ],
    "url_hash": "e32852f22ee32db27b3733229e1e518a67443adf4c6fc40ce60690f1ac6f3b6a"
}
```

The [Kaggle](https://www.kaggle.com/dominictarro/borderlands) dataset only contains the essential fields.

```json
{
  "country": "Russia",
  "category": "Aircraft",
  "model": "Beriev A-50",
  "url_hash": "b77d72f5bef846998d2b2be6226865a16cf3741f7fb5d6992dd77f93d31130bc",
  "case_id": 1,
  "status": [
    "destroyed"
  ],
  "evidence_url": "https://i.postimg.cc/g2Xg4dgw/1032-a50-awacs-destr-14-01-24.jpg",
  "country_of_production": "SUN",
  "evidence_source": "postimg"
}
```
