months = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}


## Date Convertors
## Map different date formats to a common format, if failed, return original date


def code4rena_date_convertor(date: str) -> str:
    """
    Example:
    input: "2020-11-15"
    output: "2020-11"
    """
    try:
        date = date.split("-")
        return f"{date[0]}-{date[1]}"
    except:
        return date


def consensys_date_convertor(date: str) -> str:
    """
    Example:
    input: "November 2020"
    output: "2020-11"
    """
    try:
        date = date.split(" ")
        return f"{date[1]}-{months[date[0].lower()]}"
    except:
        return date


def openzeppelin_date_convertor(date: str) -> str:
    """
    Example:
    input: "OCTOBER 12, 2023"
    output: "2023-10"
    """
    try:
        date = date.split(" ")
        return f"{date[2]}-{months[date[0].lower()]}"
    except:
        return date


def quantstamp_date_convertor(date: str) -> str:
    """
    Example:
    input: "April 12th 2024"
    output: "2024-04"
    """
    try:
        date = date.split(" ")
        return f"{date[2]}-{months[date[0].lower()]}"
    except:
        return date


if __name__ == "__main__":
    test_cases = {
        "code4rena": [
            ("2020-11-15", "2020-11"),
            ("2023-12-15", "2023-12"),
            ("2019-01-15", "2019-01"),
        ],
        "openzeppelin": [
            ("OCTOBER 12, 2023", "2023-10"),
            ("NOVEMBER 12, 2023", "2023-11"),
            ("DECEMBER 12, 2023", "2023-12"),
        ],
        "quantstamp": [
            ("April 12th 2024", "2024-04"),
            ("May 12th 2024", "2024-05"),
            ("June 12th 2024", "2024-06"),
        ],
        "consensys": [
            ("November 2020", "2020-11"),
            ("December 2020", "2020-12"),
            ("January 2021", "2021-01"),
        ],
    }

    for date, expected in test_cases["code4rena"]:
        assert code4rena_date_convertor(date) == expected

    for date, expected in test_cases["openzeppelin"]:
        assert openzeppelin_date_convertor(date) == expected

    for date, expected in test_cases["quantstamp"]:
        assert quantstamp_date_convertor(date) == expected

    for date, expected in test_cases["consensys"]:
        assert consensys_date_convertor(date) == expected
