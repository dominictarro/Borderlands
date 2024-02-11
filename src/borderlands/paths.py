"""
Module for generating storage paths for the data lake.
"""

from pathlib import Path

# Creating reference since it's used as a func below
property_wrapper = property


class LakePath:
    """A class for generating storage paths for the data lake.

    Example:

    ```python
    from borderlands.paths import LakePath

    LakePath().equipment_loss.date("2021-01-01").render()
    # 'equipment-loss/date=2021-01-01'

    LakePath().evidence.source("postimg").url_hash("1234567890").join(".csv).render()
    # 'evidence/source=postimg/url-hash=1234567890.csv'
    ```

    """

    def __init__(self, root: Path | str | None = None) -> None:
        """Initialize the LakePath object.

        Args:
            root (Path | str | None, optional): The root path of the data lake. Defaults to None.

        """
        if isinstance(root, Path):
            self.root = root
        elif isinstance(root, str):
            self.root = Path(root)
        elif root is None:
            self.root = Path("")
        else:
            raise TypeError(f"Invalid type for root: {type(root)}")

    @property_wrapper
    def images(self) -> "LakePath":
        """Return the path to the images data."""
        return LakePath(self.root / "images")

    @property_wrapper
    def pages(self) -> "LakePath":
        """Return the path to the pages data."""
        return LakePath(self.root / "pages")

    @property_wrapper
    def processed(self) -> "LakePath":
        """Return the path to the processed data."""
        return LakePath(self.root / "processed")

    @property_wrapper
    def equipment_loss(self) -> "LakePath":
        """Return the path to the equipment loss data."""
        return LakePath(self.root / "equipment-loss")

    @property_wrapper
    def evidence(self) -> "LakePath":
        """Return the path to the evidence data."""
        return LakePath(self.root / "evidence")

    def page(self, page: str) -> "LakePath":
        """Return the path to the data for a specific page."""
        return LakePath(self.root / f"page={page}")

    def date(self, date: str) -> "LakePath":
        """Return the path to the data for a specific date."""
        return LakePath(self.root / f"date={date}")

    def source(self, source: str) -> "LakePath":
        """Return the path to the data for a specific source."""
        return LakePath(self.root / f"source={source}")

    def url_hash(self, url_hash: str) -> "LakePath":
        """Return the path to the data for a specific URL hash."""
        return LakePath(self.root / f"url-hash={url_hash}")

    def render(self) -> str:
        """Render the path as a string."""
        return self.root.as_posix()

    def join(self, *args: str) -> "LakePath":
        """Join the path with additional elements."""
        return LakePath(self.root.joinpath(*args))


class LakeNav:
    """A collection of recipes for navigating the paths of the data lake.

    # Equipment Loss Data

    The equipment loss data is stored in the `equipment-loss` directory. This
    data tends to be dumped and left alone in perpetuity. Most accesses
    will be for testing and debugging purposes. Keeping the data for a run
    on a specific date in a single directory makes it easy to find and
    utilize related files. Rarely will a like file types be accessed or processed
    together in bulk.

    ```
    equipment-loss/
    ├── date=2021-01-01
    │   ├── pages
    │   │   ├── page=naval.html
    │   │   └── page=aircraft.html
    │   │   └── ...
    │   └── processed
    │       ├── oryx.csv
    │       └── ...
    └── ...
    ```

    # Evidence Data

    The evidence data is stored in the `evidence` directory. Different sources
    will have fundamentally different data. For example, the postimg source
    has information in both images and the body text of the page. However,
    X data may include text, images, and/or video. Each source's data is
    stored in a subdirectory of the evidence directory, and those subdirectories
    are uniquely organized by the needs of the source.

    ```
    evidence/
    ├── source=postimg
    │   ├── pages
    │   │   ├── url-hash=1234567890.html
    │   │   └── ...
    │   └── images
    │       ├── url-hash=1234567890.jpg
    │       └── ...
    └── ...
    ```

    """

    def __init__(self, root: Path | str | None = None) -> None:
        """Initialize the Recipes object."""
        self.lake_path = LakePath(root)

    def equipment_page(self, date: str, page: str, ext: str = "html") -> str:
        """Return the path to the equipment loss page for a specific date.

        Args:
            date (str): The date of the equipment loss page.
            page (str): The page name.
            ext (str): The file extension.

        Example:

        ```python
        LakeNav().equipment_page("2021-01-01")
        # 'equipment-loss/date=2021-01-01/pages/page=naval.html'
        ```
        """
        ext = "." + ext.lstrip(".")
        return self.lake_path.equipment_loss.date(date).pages.page(page + ext).render()

    def equipment_data(self, date: str, ext: str = "csv") -> str:
        """Return the path to the equipment loss data for a specific date.

        Args:
            date (str): The date of the equipment loss data.
            ext (str): The file extension.

        Example:

        ```python
        LakeNav().equipment_data("2021-01-01")
        # 'equipment-loss/date=2021-01-01/processed/oryx.csv'
        ```
        """
        ext = "." + ext.lstrip(".")
        return (
            self.lake_path.equipment_loss.date(date)
            .processed.join("oryx" + ext)
            .render()
        )

    def evidence_page(self, source: str, url_hash: str, ext: str = "html") -> str:
        """Return the path to the evidence page for a specific source and URL hash.

        Args:
            source (str): The source of the evidence.
            url_hash (str): The URL hash of the evidence.
            ext (str): The file extension.

        Example:

        ```python
        LakeNav().evidence_page("postimg", "1234567890")
        # 'evidence/source=postimg/pages/url-hash=1234567890.html'
        ```
        """
        ext = "." + ext.lstrip(".")
        return (
            self.lake_path.evidence.source(source)
            .pages.url_hash(url_hash + ext)
            .render()
        )

    def evidence_img(self, source: str, url_hash: str, ext: str = "jpg") -> str:
        """Return the path to the evidence image for a specific source and URL hash.

        Args:
            source (str): The source of the evidence.
            url_hash (str): The URL hash of the evidence.
            ext (str): The file extension.

        Example:

        ```python
        LakeNav().evidence_img("postimg", "1234567890")
        # 'evidence/source=postimg/images/url-hash=1234567890.jpg'
        ```
        """
        ext = "." + ext.lstrip(".")
        return (
            self.lake_path.evidence.source(source)
            .images.url_hash(url_hash + ext)
            .render()
        )
