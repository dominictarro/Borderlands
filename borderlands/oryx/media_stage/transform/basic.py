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
    'failed_duplicate_check': False
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
def build_download_dataframe(df: pd.DataFrame, media_files: list[str]) -> pd.DataFrame:
    """Creates a DataFrame with URLs and their hashes to download.

    Output columns: evidence_source, evidence_url, url_hash, key
    """
    # Create keys to associate with the media files
    dl_df = df.groupby(["evidence_url", "evidence_source", "url_hash"], as_index=False).count()
    dl_df["assoc_key"] = dl_df["evidence_source"] + "_" + dl_df["url_hash"]
    # Calculate the key for the media files
    # This is the same as the assoc_key, but evidence sources are folders
    dl_df["key"] = dl_df["evidence_source"] + "/" + dl_df["url_hash"]

    # The first bucket scan before extracting will find 0 files. This prevents a crash in that case
    if media_files:
        media_df = pd.DataFrame(media_files)
    else:
        # No files to load?
        media_df = pd.DataFrame([], columns=["Key"])

    # Extract the filename from the key: "path/to/file.ext" -> "file"
    media_df["Filename"] = media_df["Key"].apply(lambda k: Path(k).stem)
    media_df["Folder"] = media_df["Key"].apply(lambda k: Path(k).parent.stem)
    # Create a key to associate with the records
    media_df["assoc_key"] = media_df["Folder"] + "_" + media_df["Filename"]
    # Mark the files as downloaded
    media_df["is_downloaded"] = True

    # Merge the two DataFrames
    dl_df = dl_df.merge(media_df, on="assoc_key", how="left", validate="one_to_one")

    # Filter out already downloaded files
    dl_df = dl_df[dl_df["is_downloaded"].isna()]
    return dl_df[["evidence_source", "evidence_url", "url_hash", "key"]]


@task
def update_with_results(df: pd.DataFrame, results: list[str]) -> pd.DataFrame:
    """Associate rows in a DataFrame with their download results.

    Results are a list of strings like `"path/to/source_hash.ext"` when they
    download successfully, or `None` when they fail. This function adds a
    column to the DataFrame indicating whether the download succeeded or not.
    """
    df["is_downloaded"] = pd.Series(results).notnull()
    return df


@task(persist_result=False)
def build_media_state(df: pd.DataFrame, dl_dfs: tuple[pd.DataFrame], include: tuple[str]) -> pd.DataFrame:
    """Builds a lookup table for media files based on the download dataframes
    with updated results.
    """
    dl_df = pd.concat(dl_dfs)
    df = df.merge(
        dl_df,
        on="evidence_url",
        how="left",
        validate="many_to_one",
        suffixes=("", "_dl")
    )

    # df does not have a is_downloaded column
    # dl_df does have an is_downloaded column
    #
    # After the merge, df will have an is_downloaded column but the rows that
    # were not considered for download will have nulls. Use this to judge
    # download status.
    #
    # If the key is null, then the file was excluded from the download df
    # because it was already downloaded. Mark it as downloaded.
    # If the key is not null, then the file was attempted to be downloaded.
    # Mark it as downloaded if the download succeeded.
    #
    # Some evidence sources are not included in the download df. Only allow the
    # ones that are included to use the above logic.
    df["is_downloaded"] = (df["key"].isnull() | df["is_downloaded"]) & df["evidence_source"].isin(include)

    # This is the state of the downloads
    df = df[["evidence_source", "url_hash", "is_downloaded"]]
    return df.sort_values(["evidence_source", "url_hash"], ignore_index=True)
