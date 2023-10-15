import re
def get_standard_name(name: str) -> str:
    """It converts the ugly or unacceptable names into standard name

    Args:
        name (str): takes a string of the column name in the data

    Returns:
        str: correct standard name for the column
    """        

    part_of_name = [x for x in re.findall("[A-Z]*[a-z0-9]*", name) if x]
    new_name = "_".join(part_of_name).lower()
    if re.search(r"^\d+", new_name):
        new_name = "_" + new_name
    return new_name


def standardize_column_names(columns: str) ->list:
    """Standardize column names.

    Parameters
    ----------
    columns: Iterable[str]
        Iterable of columns names.
    """
    return [get_standard_name(x) for x in columns]
