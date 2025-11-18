# crawlers/quantstamp/report.py

import json
import os
import re
import time
from typing import List, Dict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from configs.quantstamp.project import PROJECT_LIST_PATH
from configs.quantstamp.report import (
    REPORT_SECTION_ID,
    REPORT_CONTAINER_XPATH,
    REPORT_DATA_PATH,         # kept for compatibility with the base
    REPORT_ERROR_LOG_PATH,    # kept for compatibility with the base
    SUMMARY_OF_FINGINDS_COLUMNS,
)

from ..base.report import ReportCrawlerBase, ReportCrawlerConfig

# Optional fallbacks from your repo (keep if you already have them)
from .helper import (
    extract_details_from_finding,   # fallback only
    extract_update_from_finding,    # fallback only
)

from helpers.selenium import (
    extract_description,
    extract_codes,
    extract_links,
    extract_tags,
    extract_tags_in_webelement,
    extract_h4,
    extract_nested_list,
)

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3",
    "LPT1", "LPT2", "LPT3"
}

def safe_filename(name: str, maxlen: int = 120, repl: str = "_") -> str:
    """Windows-safe slug for filenames/folders."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]+', repl, name)
    name = re.sub(r"\s+", " ", name).strip().rstrip(".")
    if name.upper() in WINDOWS_RESERVED:
        name = f"_{name}"
    name = re.sub(r"[^\w\- ]+", repl, name).replace(" ", "_")
    return name[:maxlen].rstrip("_")


def _grab_sections_from_text(container_text: str) -> Dict[str, Any]:
    """
    Robustly extract Description / Recommendation / Update / Files affected
    from the plain text of the finding block.
    Works even if DOM structure varies slightly between cert pages.
    """
    def cut(label: str, next_labels: List[str]) -> str:
        # case-insensitive: label: ... (until any of the next labels or end)
        pat = r"(?i)" + re.escape(label) + r":\s*(.*?)(?:" + "|".join(re.escape(n) + r":" for n in next_labels) + r"|$)"
        m = re.search(pat, container_text, flags=re.S)
        return (m.group(1).strip() if m else "")

    label_order = [
        "Description", "Recommendation", "Update",
        "File(s) affected", "Files affected", "Affected files"
    ]

    description    = cut("Description",    label_order[1:])
    recommendation = cut("Recommendation", label_order[2:])
    update         = cut("Update",         label_order[3:])

    files_block = (
        cut("File(s) affected", []) or
        cut("Files affected",    []) or
        cut("Affected files",    [])
    )

    files_affected: List[str] = []
    if files_block:
        for line in [ln.strip("•- \t") for ln in files_block.splitlines()]:
            # Accept typical code paths
            if re.search(r"(?:^|/)[A-Za-z0-9_.-]+\.(?:sol|vy)\b", line):
                files_affected.append(line)

    return {
        "description": description,
        "recommendation": recommendation,
        "update": update,
        "files_affected": files_affected,
    }


# -----------------------------------------------------------------------------
# Quantstamp Report Crawler
# -----------------------------------------------------------------------------

class ReportCrawler(ReportCrawlerBase):
    """
    Quantstamp crawler:
      - Windows-safe filenames + ensured directories.
      - Summary-of-findings table + per-finding bodies via #findings-qs* anchors.
      - Severity/Status filled from the summary table (canonical).
      - Optional sections handled leniently (no crashes).
    """

    def __init__(self, options: List[str], root_dir: str = ""):
        config = ReportCrawlerConfig(
            root_dir=root_dir,
            project_list_path=PROJECT_LIST_PATH,
            report_data_path=REPORT_DATA_PATH,       # base compatibility (not used for output name)
            error_file_path=REPORT_ERROR_LOG_PATH,   # base compatibility
            title_tag="",
            subtitle_tag="",
            smtitle_tag="",
        )
        super().__init__(options, config)
        # important: define root_dir for this subclass before using it
        self.config = config
        self.root_dir = root_dir or getattr(config, "root_dir", "") or os.getcwd()

        # Vendor-scoped output
        self.vendor_root = os.path.join(self.root_dir, "data", "quantstamp")
        self.reports_dir = os.path.join(self.vendor_root, "reports")
        self.errors_dir  = os.path.join(self.vendor_root, "errors")
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.errors_dir,  exist_ok=True)

        # per-project tracking
        self.current_project_name_raw: str = ""
        self.current_project_name_safe: str = ""
        self.current_project_dir: str = ""   # optional dump for debug (sections)

    # ---------------- Core page loader ----------------

    def load_page(self, url: str):
        """
        Navigate to the given URL and wait for the first section of the report
        to appear.  Quantstamp recently migrated to a React-based layout
        without a traditional container element, so waiting on the old
        REPORT_CONTAINER_XPATH often fails.  Instead, we wait for the
        executive-summary section to be present on the page.  This id is
        consistent across new reports.
        """
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "executive-summary"))
            )
        except Exception:
            # fall back to the old container if the new id is not found
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, REPORT_CONTAINER_XPATH))
            )

    # ---------------- I/O helpers ----------------

    def _begin_project(self, project_name: str):
        self.current_project_name_raw  = project_name
        self.current_project_name_safe = safe_filename(project_name)
        self.current_project_dir = os.path.join(self.vendor_root, "sections", self.current_project_name_safe)
        os.makedirs(self.current_project_dir, exist_ok=True)

    def _write_json(self, project_name: str, data: dict):
        out_path = os.path.join(self.reports_dir, f"{safe_filename(project_name)}.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ wrote {os.path.relpath(out_path, self.root_dir)}")

    def _log_error(self, section_id_or_name: str, error_msg: str):
        err_path = os.path.join(self.errors_dir, f"{self.current_project_name_safe or 'general'}.txt")
        os.makedirs(os.path.dirname(err_path), exist_ok=True)
        with open(err_path, "a", encoding="utf-8") as f:
            f.write(f"============== {section_id_or_name} ==============\n")
            f.write(error_msg.rstrip() + "\n")

    # kept for compatibility with your other crawlers
    def write_section_data(self, section_name: str, content: dict):
        section_path = os.path.join(self.current_project_dir, f"{section_name}.json")
        os.makedirs(os.path.dirname(section_path), exist_ok=True)
        with open(section_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(content, indent=2, ensure_ascii=False))

    def record_error(self, section_id, error: str):
        self._log_error(section_id, error)

    # ---------------- Section: Executive Summary ----------------

    def handle_executive_summary(self) -> dict:
        # The executive summary section now uses a card-based layout rather than
        # a simple table.  Each attribute (Type, Timeline, Language, Methods,
        # etc.) appears as a pair of adjacent <div> elements with the same
        # class prefix (sc-eAKupa) or with a font-weight style.  We pair up
        # adjacent cells to extract key/value pairs.
        try:
            # section_id may not exist in REPORT_SECTION_ID if configs are out of date.
            section_id = getattr(REPORT_SECTION_ID, "EXECUTIVE_SUMMARY", None)
            section_id = section_id.value if section_id else "executive-summary"
        except Exception:
            section_id = "executive-summary"
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            # Extract a free‑form description at the top
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            # Collect candidate cells: these divs alternate key/value
            cells = section.find_elements(By.XPATH, ".//div[contains(@class,'sc-eAKupa')]")
            # Fallback: if no such cells, try the older table‑based logic
            if not cells:
                table_cells = []
                for i in range(1, 3):
                    table_cells += section.find_elements(By.XPATH, f"./div/div[{i}]/div")
                cells = table_cells
            for i in range(0, len(cells) - 1, 2):
                key_el = cells[i]
                val_el = cells[i + 1]
                key = key_el.text.strip()
                val_text = val_el.text.strip()
                # If value contains multiple lines, split them
                vals = [ln.strip() for ln in val_text.split("\n") if ln.strip()]
                if key:
                    res["details"].append({"key": key, "value": vals})
        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Operational Considerations ----------------

    def handle_operational_considerations(self) -> dict:
        """
        Extract the "Operational Considerations" section.  Quantstamp's new
        reports include this section as a simple bullet list of
        assumptions, caveats and expectations.  We capture the plain
        text and any code snippets or links contained within the
        section.  If the corresponding constant is missing from
        REPORT_SECTION_ID, we fall back to the literal id used on the
        page ("operational-considerations").
        """
        # Determine the section id: try the config enum first, then default
        try:
            sec = getattr(REPORT_SECTION_ID, "OPERATIONAL_CONSIDERATIONS")
            section_id = sec.value if sec else "operational-considerations"
        except Exception:
            section_id = "operational-considerations"
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            # description: first paragraph(s) until the list begins
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)
            # Attempt to parse nested lists for better structure
            try:
                # If a UL/OL exists, use nested list extractor
                list_el = section.find_element(By.XPATH, ".//ul | .//ol")
                nested = extract_nested_list(list_el)
                res["details"] = nested if nested else list_el.text.split("\n")
            except NoSuchElementException:
                # Fallback: split by line breaks
                res["details"] = [ln.strip() for ln in section.text.split("\n") if ln.strip()]
        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Key Actors and Capabilities ----------------

    def handle_key_actors_and_capabilities(self) -> dict:
        """
        Extract the "Key Actors and Capabilities" section.  This section
        groups bullet lists under subheadings (e.g., bucket_usd, bucket_oracle,
        etc.).  We use nested list extraction to preserve the hierarchy of
        actors and their actions.  If the REPORT_SECTION_ID enum does not
        contain an entry for this section, we fall back to the literal id
        string "key-actors-and-capabilities".
        """
        try:
            sec = getattr(REPORT_SECTION_ID, "KEY_ACTORS_AND_CAPABILITIES")
            section_id = sec.value if sec else "key-actors-and-capabilities"
        except Exception:
            section_id = "key-actors-and-capabilities"
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)
            # Use nested list extraction on the first UL/OL; this returns a
            # nested structure representing actor groups and their capabilities.
            try:
                list_el = section.find_element(By.XPATH, ".//ul | .//ol")
                nested = extract_nested_list(list_el)
                res["details"] = nested if nested else list_el.text.split("\n")
            except NoSuchElementException:
                res["details"] = [ln.strip() for ln in section.text.split("\n") if ln.strip()]
        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Auditor Suggestions ----------------

    def handle_auditor_suggestions(self) -> dict:
        """
        Extract the "Auditor Suggestions" section.  Suggestions are labelled
        S1, S2, etc., and resemble findings with an identifier, title,
        status, update, description and recommendation.  We attempt to
        parse each suggestion by scanning through h3/h4 headings and
        matching subsequent text blocks.  In cases where the DOM
        structure is inconsistent, we fall back to capturing the raw
        lines of text.  If REPORT_SECTION_ID lacks an entry, use the
        literal id "auditor-suggestions" as a default.
        """
        try:
            sec = getattr(REPORT_SECTION_ID, "AUDITOR_SUGGESTIONS")
            section_id = sec.value if sec else "auditor-suggestions"
        except Exception:
            section_id = "auditor-suggestions"
        res = {
            "title": section_id,
            "index": [],
            "details": [],
            "links": [],
            "codes": [],
        }
        try:
            # Auditor suggestions may not have an id on the container.  Try
            # locating via id first; if that fails, find the H1 heading.
            try:
                section = self.driver.find_element(By.ID, section_id)
            except NoSuchElementException:
                # locate the h1 heading and take its parent section
                h1 = self.driver.find_element(By.XPATH, f"//h1[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'auditor suggestions')]")
                section = h1.find_element(By.XPATH, "ancestor::section")

            res["links"] = extract_links(section)
            res["codes"] = extract_codes(section)
            # Build an index of suggestion ids and titles
            headers = section.find_elements(By.CSS_SELECTOR, "h3, h4")
            # We'll iterate through headers and gather text between them
            for idx, hdr in enumerate(headers):
                title_text = hdr.text.strip()
                # Start a new suggestion if it begins with something like "S1"
                if not title_text:
                    continue
                parts = title_text.split(None, 1)
                sid = parts[0]
                pretty_title = parts[1] if len(parts) > 1 else title_text
                # Determine the container boundary for the suggestion
                # by looking at the next header or end of section
                next_el = headers[idx + 1] if idx + 1 < len(headers) else None
                content_elems = []
                # gather siblings after hdr until next hdr
                sibling = hdr
                while True:
                    try:
                        sibling = sibling.find_element(By.XPATH, "following-sibling::*[1]")
                    except Exception:
                        break
                    if next_el is not None and sibling == next_el:
                        break
                    content_elems.append(sibling)
                    # move to next sibling for next iteration
                    hdr = sibling
                # Extract textual description, recommendation and update using
                # the fallback text parsing helper
                text_block = "\n".join([el.text for el in content_elems if el.text.strip()])
                sec_parts = _grab_sections_from_text(text_block)
                res["details"].append({
                    "id": sid,
                    "title": pretty_title,
                    "severity": "",  # suggestions do not have severity
                    "status": "",    # capture status if present in text
                    "description": sec_parts.get("description", text_block),
                    "recommendation": sec_parts.get("recommendation", ""),
                    "update": sec_parts.get("update", ""),
                    "files_affected": sec_parts.get("files_affected", []),
                })
                res["index"].append({"text": title_text, "href": ""})
        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: About Quantstamp ----------------

    def handle_about_quantstamp(self) -> dict:
        """
        Extract the "About Quantstamp" section.  This section usually
        contains informational paragraphs about the company and may
        include a list of services or links.  We collect the textual
        description, any nested list items, code snippets and links.
        Fallback to the literal id if the enum entry is missing.
        """
        try:
            sec = getattr(REPORT_SECTION_ID, "ABOUT_QUANTSTAMP")
            section_id = sec.value if sec else "about-quantstamp"
        except Exception:
            section_id = "about-quantstamp"
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)
            # Extract nested lists if present
            try:
                list_el = section.find_element(By.XPATH, ".//ul | .//ol")
                nested = extract_nested_list(list_el)
                res["details"] = nested if nested else list_el.text.split("\n")
            except NoSuchElementException:
                res["details"] = [ln.strip() for ln in section.text.split("\n") if ln.strip()]
        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Summary of Findings ----------------

    def handle_summary_of_findings(self) -> dict:
        section_id = REPORT_SECTION_ID.SUMMARY_OF_FINDINGS.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            trs = extract_tags_in_webelement(section, "tr")
            # often first TR is header; iterate all and map columns defensively
            for tr in trs[1:] if len(trs) > 1 else trs:
                row = {}
                tds = extract_tags_in_webelement(tr, "td")
                if not tds:
                    continue
                for i, td in enumerate(tds):
                    col_name = SUMMARY_OF_FINGINDS_COLUMNS[i] if i < len(SUMMARY_OF_FINGINDS_COLUMNS) else f"col_{i}"
                    row[col_name.lower()] = td.text.strip()
                if any(row.values()):
                    res["details"].append(row)

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Assessment Breakdown ----------------

    def handle_assessment_breakdown(self) -> dict:
        section_id = REPORT_SECTION_ID.ASSESSMENT_BREAKDOWN.value
        res = {"title": section_id, "codes": [], "issues": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            try:
                disclaimer = section.find_element(By.CSS_SELECTOR, "div.sc-khjJjR")
                res["disclaimer"] = disclaimer.find_element(By.TAG_NAME, "span").text
            except NoSuchElementException:
                res["disclaimer"] = ""

            try:
                ul = section.find_element(By.TAG_NAME, "ul")
                res["issues"] = ul.text.split("\n") or []
            except NoSuchElementException:
                res["issues"] = []

            try:
                ol = section.find_element(By.TAG_NAME, "ol")
                res["methodology"] = extract_nested_list(ol) or {}
            except NoSuchElementException:
                res["methodology"] = {}

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Scope ----------------

    def handle_scope(self) -> dict:
        section_id = REPORT_SECTION_ID.SCOPE.value
        res = {"title": section_id, "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            divs = section.find_elements(By.TAG_NAME, "div")
            for div in divs:
                try:
                    key = div.find_element(By.TAG_NAME, "h4").text.strip()
                    span = div.find_element(By.TAG_NAME, "span")
                    res[key] = [line for line in span.text.split("\n") if line.strip()]
                except NoSuchElementException:
                    continue

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Findings helpers ----------------

    def _collect_finding_anchor_hrefs(self) -> List[str]:
        hrefs: List[str] = []
        try:
            anchors = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='#findings-qs']")
            for a in anchors:
                href = a.get_attribute("href")
                if href and "#findings-qs" in href:
                    hrefs.append(href)
        except Exception:
            pass
        # de-dupe preserving order
        return list(dict.fromkeys(hrefs))

    def _extract_severity_status_from_summary_table(self) -> Dict[str, Dict[str, str]]:
        """
        Build a map { 'YIELD-1': {'severity': 'High', 'status': 'Fixed'}, ... }
        from the on-page summary table.
        """
        id2meta: Dict[str, Dict[str, str]] = {}
        try:
            table = self.driver.find_element(
                By.XPATH, "//table[.//th[contains(.,'Severity')] and .//th[contains(.,'ID')]]"
            )
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            for tr in rows:
                cells = tr.find_elements(By.XPATH, "./th|./td")
                if not cells:
                    continue
                fid = cells[0].text.strip()
                sev = ""
                sta = ""
                # heuristics: scan the rest of cells
                for c in cells[1:]:
                    t = c.text.strip()
                    if t in ("Critical", "High", "Medium", "Low", "Informational", "Undetermined"):
                        sev = t
                    elif t in ("Fixed", "Mitigated", "Acknowledged", "Won't fix", "Wontfix", "Invalid", "Open"):
                        sta = t
                if fid:
                    id2meta[fid] = {"severity": sev, "status": sta}
        except Exception:
            pass
        return id2meta

    def _extract_finding_from_anchor(self, href: str, id2meta: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Visit an anchor like ...#findings-qs3 and extract the long body.
        """
        # Navigate to the specific finding
        self.driver.get(href)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='findings-qs']"))
        )

        # IMPORTANT: use the exact fragment id so we don't pick the first block
        frag = href.rsplit("#", 1)[-1]  # e.g., "findings-qs3"
        container = self.driver.find_element(By.ID, frag)

        # Title, e.g., "YIELD-1  Staker Address Update Does Not Transfer Staker's Balance"
        title_text = ""
        try:
            h = container.find_element(By.CSS_SELECTOR, "h2, h3, h4")
            title_text = h.text.strip()
        except Exception:
            pass

        fid, pretty_title = "", title_text
        if title_text:
            parts = title_text.split(None, 1)
            fid = parts[0]
            pretty_title = parts[1] if len(parts) > 1 else title_text

        # Extract long sections from the raw text robustly
        block_txt = container.text
        sections = _grab_sections_from_text(block_txt)

        # Fallback enrichments (optional)
        try:
            links = extract_links(container)
        except Exception:
            links = []
        try:
            codes = extract_codes(container)
        except Exception:
            codes = []

        severity = ""
        status = ""
        # fill from summary table if available (canonical)
        if fid in id2meta:
            severity = id2meta[fid].get("severity", "") or severity
            status   = id2meta[fid].get("status", "")   or status

        return {
            "id": fid,
            "title": pretty_title,
            "severity": severity,
            "status": status,
            "description": sections["description"],
            "recommendation": sections["recommendation"],
            "update": sections["update"],
            "files_affected": sections["files_affected"],
            "link": href,
            "links": links,
            "codes": codes,
        }

    # ---------------- Section: Findings ----------------

    def handle_findings(self) -> dict:
        section_id = REPORT_SECTION_ID.FINDINGS.value
        res = {"title": section_id, "links": [], "index": [], "details": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["links"] = extract_links(section)

            # Build index (nice to have)
            try:
                anchors = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='#findings-qs']")
                seen = set()
                for a in anchors:
                    href = a.get_attribute("href")
                    txt = a.text.strip()
                    if href and "#findings-qs" in href and href not in seen:
                        res["index"].append({"text": txt, "href": href})
                        seen.add(href)
            except Exception:
                pass

            # Authoritative: visit each anchor and extract long body
            id2meta = self._extract_severity_status_from_summary_table()
            anchor_hrefs = self._collect_finding_anchor_hrefs()
            seen_ids = set()

            for href in anchor_hrefs:
                try:
                    item = self._extract_finding_from_anchor(href, id2meta)
                    fid = item.get("id") or ""
                    if fid:
                        if fid in seen_ids:
                            # Already captured; optional: merge missing fields here
                            continue
                        seen_ids.add(fid)
                    res["details"].append(item)
                except Exception as e:
                    self.record_error(f"{section_id}-anchor", f"{href} -> {e!r}")
                    continue
                finally:
                    time.sleep(0.2)

            # Fallback (if no anchors at all): try simple cards on the page
            if not res["details"]:
                cards = section.find_elements(By.XPATH, ".//h3/ancestor::div[1]")
                for card in cards:
                    try:
                        title = card.find_element(By.CSS_SELECTOR, "h3").text.strip()
                    except NoSuchElementException:
                        continue
                    severity = ""
                    status = ""
                    try:
                        severity = card.find_element(
                            By.XPATH,
                            ".//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'critical') or "
                            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'high') or "
                            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'medium') or "
                            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'low') or "
                            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'informational')]"
                        ).text.strip()
                    except Exception:
                        pass
                    try:
                        status = card.find_element(
                            By.XPATH,
                            ".//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'fix') or "
                            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'mitigat') or "
                            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'acknowledg') or "
                            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'open')]"
                        ).text.strip()
                    except Exception:
                        pass

                    update = ""
                    try:
                        update = extract_update_from_finding(card)
                    except Exception:
                        pass
                    content = {}
                    try:
                        content = extract_details_from_finding(card)
                    except Exception:
                        pass

                    if title:
                        # attempt to parse ID from title beginning
                        parts = title.split(None, 1)
                        fid = parts[0] if parts else ""
                        if fid and fid in id2meta:
                            severity = id2meta[fid].get("severity", "") or severity
                            status   = id2meta[fid].get("status", "")   or status
                        res["details"].append({
                            "id": fid,
                            "title": parts[1] if len(parts) > 1 else title,
                            "severity": severity,
                            "status": status,
                            "update": update,
                            "content": content,
                        })

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Definitions ----------------

    def handle_definition(self) -> dict:
        section_id = REPORT_SECTION_ID.DEFINITIONS.value
        res = {"title": section_id, "details": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            lis = extract_tags_in_webelement(section, "li")
            for li in lis:
                try:
                    title = li.find_element(By.TAG_NAME, "b").text
                    content = li.text.split(title, 1)[1].strip()
                    if content.startswith("-"):
                        content = content[1:].strip()
                    res["details"].append({"title": title, "content": content})
                except Exception:
                    continue
        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Appendix ----------------

    def handle_appendix(self) -> dict:
        section_id = REPORT_SECTION_ID.APPENDIX.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            divs = section.find_elements(By.XPATH, "./div")
            for div in divs:
                try:
                    content = div.find_element(By.XPATH, "./*[not(self::h4)]")
                    res["details"].append({
                        "title": extract_h4(div),
                        "content": [line for line in content.text.split("\n") if line.strip()],
                    })
                except Exception:
                    continue

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Toolset ----------------

    def handle_toolset(self) -> dict:
        section_id = REPORT_SECTION_ID.TOOLSET.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["description"] = extract_description(section)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            divs = section.find_elements(By.XPATH, "./div") or []
            for div in divs:
                try:
                    title = div.find_element(By.XPATH, "./p").text
                except Exception:
                    title = ""
                res["details"].append({
                    "title": title,
                    "content": extract_tags(div, "li"),
                })

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Automated Analysis ----------------

    def handle_automated_analysis(self) -> dict:
        section_id = REPORT_SECTION_ID.AUTOMATED_ANALYSIS.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            divs = section.find_elements(By.XPATH, "./div") or []
            for div in divs:
                try:
                    content = div.find_element(By.XPATH, "./*[not(self::h4)]")
                    res["details"].append({
                        "title": extract_h4(div),
                        "content": [line for line in content.text.split("\n") if line.strip()],
                    })
                except Exception:
                    continue

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Test Suite Results ----------------

    def handle_test_suite_results(self) -> dict:
        section_id = REPORT_SECTION_ID.TEST_SUITE_RESULTS.value
        res = {"title": section_id, "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)

            contents = section.find_elements(By.XPATH, "./*/*[not(self::pre)]") or []
            codes_inline = section.find_elements(By.XPATH, ".//code[not(ancestor::pre)]")
            res["description"] = [con.text for con in contents if con.text.strip()]
            res["code_block"] = extract_tags(section, "pre")
            res["codes"] = [code.text for code in codes_inline if code.text.strip()]
            res["links"] = extract_links(section)

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Code Coverage ----------------

    def handle_code_coverage(self) -> dict:
        section_id = REPORT_SECTION_ID.CODE_COVERAGE.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            xpath = ".//{tag}[not(ancestor::pre) and not(ancestor::table)]"
            contents = section.find_elements(
                By.XPATH, xpath.format(tag="span") + "|" + xpath.format(tag="li")
            )

            tables = section.find_elements(By.XPATH, "./div/span/table | ./div/span/pre")
            details = []
            for table in tables:
                if table.tag_name == "pre":
                    details.append({"code_block": table.text})
                    continue
                if table.tag_name != "table":
                    continue
                rows = table.find_elements(By.TAG_NAME, "tr")
                details.append({
                    "column": extract_tags(table, "th"),
                    "rows": [extract_tags(row, "td") for row in rows],
                })

            res["description"] = [con.text for con in contents if con.text.strip()]
            res["details"] = details

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Changelog ----------------

    def handle_changelog(self) -> dict:
        section_id = REPORT_SECTION_ID.CHANGELOG.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["details"] = extract_tags(section, "li")
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)
        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Adherence to Best Practices ----------------

    def handle_adherence_to_best_practices(self) -> dict:
        section_id = REPORT_SECTION_ID.ADHERENCE_TO_BEST_PRACTICES.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            try:
                list_element = section.find_element(By.XPATH, "./span/ul | ./span/ol")
                res["details"] = extract_nested_list(list_element) or {}
            except NoSuchElementException:
                res["details"] = section.text.split("\n")

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Section: Code Documentation ----------------

    def handle_code_documentation(self) -> dict:
        section_id = REPORT_SECTION_ID.CODE_DOCUMENTATION.value
        res = {"title": section_id, "details": [], "codes": [], "links": []}
        try:
            section = self.driver.find_element(By.ID, section_id)
            res["codes"] = extract_codes(section)
            res["links"] = extract_links(section)

            try:
                list_element = section.find_element(By.XPATH, "./span/ul | ./span/ol")
                res["details"] = extract_nested_list(list_element) or {}
            except NoSuchElementException:
                res["details"] = section.text.split("\n")

        except NoSuchElementException as e:
            self.record_error(section_id, e.msg)
        except Exception as e:
            self.record_error(section_id, str(e))
        finally:
            return res

    # ---------------- Crawl orchestration ----------------

    def crawl(self, url: str, project_name: str):
        self._begin_project(project_name)
        self.load_page(url)

        details = {
            "project_name": self.current_project_name_raw,
            "project_name_safe": self.current_project_name_safe,
            "report_url": url,
            "data": [],
        }

        # Call all "handle_*" methods
        for method in dir(self):
            if method.startswith("handle_"):
                section = method.replace("handle_", "")
                print(f"Crawling {self.current_project_name_raw}: {section}")
                try:
                    data = getattr(self, method)()
                    details["data"].append(data)
                except Exception as e:
                    self.record_error(section, str(e))
                time.sleep(0.25)

        self._write_json(self.current_project_name_raw, details)

    def crawl_all(self) -> None:
        if self.driver is None:
            raise ValueError("Driver is not initialized.")
        project_list = self.load_project_list()

        for project in project_list:
            project_name = project.get("project_name") or project.get("name") or ""
            report_url   = project.get("report_link") or project.get("url") or ""
            if not project_name or not report_url:
                continue
            if report_url.lower().endswith(".pdf"):
                print(f"Skipping {project_name} (pdf).")
                continue

            try:
                self.crawl(report_url, project_name)
            except Exception as e:
                self._begin_project(project_name)
                self.record_error("crawl_all", f"{project_name}: {e!r}")

        self.driver.quit()
