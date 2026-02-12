# In a utils.py or in your functions
import polars as pl


def convert_canvas_datetime(
    df: pl.DataFrame, column: str, timezone: str
) -> pl.DataFrame:
    """
    Convert Canvas UTC datetime string to specified timezone.

    Args:
        df: Polars DataFrame
        column: Name of the datetime column to convert
        timezone: IANA timezone string

    Returns:
        DataFrame with converted datetime column
    """
    return df.with_columns(
        pl.col(column)
        .str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%SZ")
        .dt.replace_time_zone("UTC")
        .dt.convert_time_zone(timezone)
        .alias(column)
    )
