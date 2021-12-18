import re

import numpy as np
import pandas as pd


def clean_subjects(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans data table of subjects"""
    # Remove rows with NaN
    df = df.dropna().reset_index(drop=True)

    # Drop extra time column
    df.drop(columns="Days / Time.1", inplace=True)

    # Change CRN from float to int
    df = df.astype({"CRN": int})

    # Make TBD's nan
    df["Days / Time"] = df["Days / Time"].str.replace("TBD  TBD", str(np.nan), regex=True)

    # Get list of course meet dates
    df = split_start_end_time(df)
    return df


def split_start_end_time(df: pd.DataFrame) -> pd.DataFrame:
    """Create list of valid day/time"""
    df["Days / Time"] = df["Days / Time"].map(
        lambda x: re.findall(r'([A-Z]+\s+\d{2}:\d{2}\s(?:am|pm)\s-\s\d{2}:\d{2}\s(?:am|pm))',
                             x) if x != 'nan' else np.nan)

    return df
