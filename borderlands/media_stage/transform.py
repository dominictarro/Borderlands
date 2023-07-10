"""
Basic transformations for the media staging.

Source data from the Oryx equipment losses page is structured like

```json
{
    'evidence_url': 'https://twitter.com/UAWeapons/status/1572672235726573568',
    'description': '3, destroyed',
    'id_': '3',
    'model': 'T-62M',
    'country_of_production_flag_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/23px-Flag_of_the_Soviet_Union.svg.png',
    'category': 'Tanks',
    'country': 'Russia',
    'as_of_date': '2023-04-23T19:51:43.705293+00:00',
    'status': ['destroyed'],
    'country_of_production': 'SUN',
    'domain': 'twitter.com',
    'evidence_source': 'twitter',
    'failed_duplicate_check': False,
    'url_hash': 'd41d8cd98f00b204e9800998ecf8427e'
}
```

"""
from pathlib import Path

import pandas as pd
from prefect import task


@task
def convert_to_dataframe(pages: list[list]) -> pd.DataFrame:
    """Converts a list of lists into a single DataFrame.

    Each document in the list of lists is a dictionary like

    """
    data = []
    for page in pages:
        data.extend(page)
    df = pd.DataFrame(data)
    return df


@task
def join_media(df: pd.DataFrame, media_df: pd.DataFrame) -> pd.DataFrame:
    """Creates a DataFrame that associates existing media files with the records.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of records to associate with existing media files.
    media_files : list[dict[str, Any]]
        DataFrame of the media files that exist in the bucket.

    Returns
    -------
    pd.DataFrame
        DataFrame of records with associated media files.

    Notes
    -----

    Returned DataFrame will be like:

    | evidence_source | url_hash | ... | key |
    |-----------------|----------|-----|-----|
    | twitter         | abc123   | ... | None|
    | twitter         | def456   | ... | media/def456.jpg|
    | postimg         | abc124   | ... | media/abc124.jpg|

    """
    # Extract the filename from the key: "path/to/evidence_source/url_hash.ext"
    media_df["filename"] = media_df["Key"].apply(lambda k: Path(k).parts[-1])
    media_df["evidence_source"] = media_df["Key"].apply(lambda k: Path(k).parent.stem)
    # Extract the hash from the filename: "url_hash.ext"
    media_df["url_hash"] = media_df["Key"].apply(lambda k: Path(k).stem)

    # Deduplicate url_hashses that have multiple files. Choose the most recent
    media_df = (
        media_df.sort_values(["LastModified"], ascending=False)
        .groupby(["evidence_source", "url_hash"], as_index=False)
        .first()
    )

    # Mark the files as downloaded
    media_df = media_df.rename(columns={"Key": "key"})
    media_df = media_df[["evidence_source", "url_hash", "key"]]

    # Merge the two DataFrames
    df = df.merge(
        media_df, on=["evidence_source", "url_hash"], how="left", validate="many_to_one"
    )
    return df


@task
def filter_for_files_that_need_download(df_state: pd.DataFrame) -> pd.DataFrame:
    """Filters the media state DataFrame for files that need to be downloaded.

    Parameters
    ----------
    df_state : pd.DataFrame
        DataFrame of records where a 'key' exists if the record's evidence has already been downloaded.

    """
    # Filter out already downloaded files
    dl_df = df_state[df_state["key"].isna()]
    # Deduplicate the URLs that need to be downloaded
    dl_df = dl_df.drop_duplicates(["evidence_url"], keep="first")
    return dl_df[["evidence_source", "evidence_url", "url_hash", "key"]]


@task
def update_with_results(
    df: pd.DataFrame, results: list[dict[str, str | None]]
) -> pd.DataFrame:
    """Associate rows in a DataFrame with their download results.

    Input media files are a list of dictionaries like

    ```python
    {
        "evidence_url": "https://....",
        "key": "path/to/file.ext",
    }
    {
        "evidence_url": "https://....",
        "key": None,
    }
    ```

    Outputs a DataFrame with the result keys merged in.

    """
    dl_result_df = pd.DataFrame(results, columns=["evidence_url", "key"])
    df = df.merge(
        dl_result_df,
        on="evidence_url",
        how="left",
        validate="many_to_one",
        suffixes=("", "_dl"),
    )
    # Update with latest keys
    df["key"] = df["key_dl"].fillna(df["key"])
    df = df.drop(columns=["key_dl"])
    df = df.rename(columns={"key": "media_key"})
    return df
