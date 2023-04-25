"""
Oryx equipment losses parser.

The page is structured roughly like this

<article>
    ...
    <div>
        <!-- info about the article -->
    </div>
    ...
    <div>
        <h3>
            <!-- asset category and its summary statistics -->
        </h3>
        <ul>
            <li>
                <!-- asset model and its supporting data -->
                <a>
                    <!-- confirmed equipment losses -->
                    <!-- these are just image/video URLs, there may be more than one loss
                    per <a> tag -->
                </a>
                <a>
                    <!-- confirmed equipment losses -->
                </a>
                ...
            </li>
            ...
        </ul>
        <!-- repeat the pattern of h3 tags followed by respective ul tags -->
        ...
    </div>
    ...
</article>

So the parser is structured to generate standardized confirmed losses like so

for asset category
    for asset model
        for confirmed loss <a> tag
            for confirmed loss
                yield case


Confirmed losses have several required fields

 - Asset Category:          a text descriptor of the asset (e.g. tanks, infantry transports, etc.)

     - may include non alphanumerics
     - found in the <h3> tag

 - Model:                   a text descriptor of the machine's model (e.g. T-64BV)

     - uses exact spelling as seen on the website
     - found in the <li> tag

 - Country of Loss:         a text label of the country that the asset belonged to

     - set by the parsing function

 - Country of production:   a text label of the country that produces or produced the asset

     - derived from the flag <img>'s source url (Wikimedia origin)

 - Model case ID:           an integer ID assigned to the case

     - every asset model starts at 1 (e.g. T-64BV and T-62M both have one case where its id=1)
     - on the website, can find multiple in the same <a> tag
     - found in the <a> tag

 - Confirmation URL:        a url to the visual confirmation (image, video)

     - may not point directly to the media (e.g. to a tweet that has an image/video)
     - found in the <a> tag

 - Status:                  a list of states the asset is or was in (e.g. damaged, captured)

     - some have multiple (e.g. damaged and captured)
     - all elements of the list are lowercase strings
     - found in the <a> tag


Optional fields include

 - Cause:                   a list of causes related to the asset's status

     - Many point to other weapons systems
     - Some have multiple (e.g. damaged and captured)
     - All elements of the list are lowercase strings
     - found in the <a> tag


In the end, every document should look something like

    {
        "model_case_id": 2,
        "status": [
            "damaged"
        ],
        "confirmation_url": "https://i.postimg.cc/yYx8J43v/Screenshot-8073.png",
        "cause": [
            "Bayraktar TB2"
        ],
        "asset_category": "towed artillery",
        "model": "152mm 2A65 Msta-B howitzer",
        "country_of_loss": "russia",
        "country_of_production": "soviet union"
    }

    or

    {
        "model_case_id": 6,
        "status": [
            "destroyed"
        ],
        "confirmation_url": "https://postimg.cc/hJQ6678b",
        "cause": [
            "Bayraktar TB2",
            "artillery"
        ],
        "asset_category": "helicopters",
        "model": "Mi-8 transport helicopter",
        "country_of_loss": "russia",
        "country_of_production": "russia"
    }

    or

    {
        "model_case_id": 7,
        "status": [
            "abandoned",
            "destroyed"
        ],
        "confirmation_url": "https://i.postimg.cc/ncL87Pvg/65.png",
        "cause": null,
        "asset_category": "helicopters",
        "model": "Mi-8 transport helicopter",
        "country_of_loss": "russia",
        "country_of_production": "russia"
    }


Limitations of the data

    While the Oryx article is consistently formatted quite well, it isn't perfect. There are some
    issues with

        1. the case information being divided between <a> tags
        2. Unprecedented status values

    There are others, but these are a few that I have spotted. Fortunately, they are not frequent
    and the error between Oryx's stated totals and the scraped totals is insignificant.


Extras

 - Russian Equipment Losses
     - https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html

 - Ukrainian Equipment Losses
     - https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html


"""
from __future__ import annotations

import abc
import logging
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    import bs4


class ParserBase(abc.ABC):
    """Base parser for visually-confirmed equipment losses."""

    def __init__(self, tag: bs4.Tag, logger: logging.Logger | None = None) -> None:
        super().__init__()
        self.tag: bs4.Tag = tag
        self.logger: logging.Logger | None = logger or logging.getLogger()

    @abc.abstractmethod
    def parse(self) -> Generator[dict, None, None]:
        """Parses the `tag`.

        Yields
        ------
        dict
            A standardized equipment loss case.
        """
