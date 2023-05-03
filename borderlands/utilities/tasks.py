"""
Generic tasks for the Borderlands project.
"""
import pandas as pd
from prefect import task


concat = task(pd.concat)
