from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def extract_update_from_finding(finding: WebElement):
    try:
        update = finding.find_element(By.CSS_SELECTOR, "div.sc-khjJjR")
        content = update.find_element(By.TAG_NAME, "span").text.strip()
        codes = update.find_elements(By.TAG_NAME, "code") or []
        update_info = {
            "title": "update",
            "content": content,
            "codes": [code.text for code in codes],
        }
    except:
        update_info = None
    return update_info


def extract_details_from_finding(finding: WebElement) -> dict[str, dict]:
    details = {}
    elements = finding.find_elements(By.XPATH, "./*/*")

    for i, element in enumerate(elements):
        key = f"key_not_found_{i}"
        try:
            strong_tag = element.find_element(By.XPATH, ".//strong")
            key = strong_tag.text[0:-1].lower()
        except NoSuchElementException as e:
            continue

        details[key] = {}
        # find code-block in the element
        code_blocks = element.find_elements(By.CLASS_NAME, "code-block")
        if code_blocks:
            details[key]["code-block"] = [code.text for code in code_blocks]

        # find list in the element
        list_elements = element.find_elements(By.TAG_NAME, "li")
        if list_elements:
            details[key]["list"] = [item.text for item in list_elements]

        # find p_tag in the element
        p_tags = element.find_elements(By.TAG_NAME, "p")
        if p_tags:
            details[key]["content"] = [p_tag.text for p_tag in p_tags]

        # find all code tags in the element
        code_tags = element.find_elements(By.TAG_NAME, "code")
        if code_tags:
            details[key]["codes"] = [code.text for code in code_tags]

        # double quoted all the contents in details
        details[key] = {
            k: f'"{v}"' if isinstance(v, str) else v for k, v in details[key].items()
        }
    return details
