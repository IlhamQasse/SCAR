from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


def extract_tags(section: WebElement, tag_name: str) -> list[str]:
    try:
        tags = section.find_elements(By.TAG_NAME, tag_name)
        return [tag.text for tag in tags]
    except NoSuchElementException:
        return []


def extract_links(section: WebElement) -> list[str]:
    try:
        links = section.find_elements(By.TAG_NAME, "a")
        return [
            {"hypertext": link.text, "url": link.get_attribute("href")}
            for link in links
        ]
    except NoSuchElementException:
        return []


def extract_codes(section: WebElement) -> list[str]:
    # get code in the section
    return extract_tags(section, "code")


def get_title_tag(section: WebElement) -> str:
    titles = section.find_elements(By.TAG_NAME, "h2")
    return "h2" if titles else "h3"


def extract_dl(dl_element: WebElement) -> list[dict[str, list]]:
    """
    list of dict using dt as key and dd as value to represent dl
    """
    ds = dl_element.find_elements(By.XPATH, "./*")
    res = []
    for i in range(0, len(ds)):
        if ds[i].tag_name == "dd":
            continue
        dt, dd_list = ds[i].text, []
        for j in range(i + 1, len(ds)):
            if ds[j].tag_name == "dt":
                break
            dd_list.append(ds[j].text)
        res.append({dt: dd_list})
    return res


def extract_nested_list(list_element: WebElement, prefix=""):
    """
    Recursively fetch list items
    Args:
    - ol_element: The Selenium WebElement representing an <ol>
    - prefix: A string prefix representing the current list hierarchy

    Returns:
    - A dictionary representing the list items with their hierarchy as keys
    """
    list_items = {}
    # Get all direct <li> children of this <ol>
    try:
        items = list_element.find_elements(By.XPATH, "./li")
    except NoSuchElementException:
        return list_items
    for index, item in enumerate(items, start=1):
        # Construct the key based on the item's position
        key = f"{prefix}{index}" if prefix else str(index)

        # Try to find a nested <ol> within the current <li>
        nested_list = item.find_elements(By.XPATH, "./ol | ./ul")
        if nested_list:
            # only content in li tag not in ol tag
            list_items[key] = item.text.split("\n")[0] or ""

            # If a nested list exists, recurse into it
            list_items.update(extract_nested_list(nested_list[0], prefix=f"{key}-"))
        else:
            list_items[key] = item.text or None
    return list_items


def extract_class(element: WebElement) -> str:
    return element.get_attribute("class")


def extract_description(section: WebElement, tag_name="span") -> str:
    try:
        description = section.find_element(By.TAG_NAME, tag_name)
        return description.text
    except NoSuchElementException:
        return ""


def extract_h4(section: WebElement) -> str:
    # get urls in the section
    try:
        return section.find_element(By.TAG_NAME, "h4").text
    except NoSuchElementException:
        return "No h4 tag found"


def extract_tags_in_webelement(section: WebElement, tag_name: str) -> list[WebElement]:
    try:
        return section.find_elements(By.TAG_NAME, tag_name)
    except NoSuchElementException:
        return []


def extract_tag_names_in(element: WebElement) -> list[str]:
    try:
        sub_elements = element.find_elements(By.XPATH, "./*")
        return [el.tag_name for el in sub_elements]
    except NoSuchElementException:
        return []
