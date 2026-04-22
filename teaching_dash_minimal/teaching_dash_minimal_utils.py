"""Utility helpers extracted from teaching_dash_minimal.ipynb."""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

try:
    import main_api
except ModuleNotFoundError:
    parent_dir = Path(__file__).resolve().parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    import main_api

SEC_HEADERS = main_api.SEC_HEADERS


def load_three_metrics(cik: int, start_year: int, end_year: int) -> pd.DataFrame:
    rows = []
    for fy in range(start_year, end_year + 1):
        core = main_api.get_core_metrics_from_companyfacts(cik=cik, fy=fy)

        diluted_earnings = core.get("diluted_eps")
        capex = core.get("capex_abs")
        ocf = core.get("operating_cf")
        fcf = core.get("free_cash_flow")

        if fcf is None and ocf is not None and capex is not None:
            fcf = ocf - capex
            fcf_mode = "calculated_ocf_minus_capex"
        else:
            fcf_mode = "direct_from_companyfacts"

        rows.extend(
            [
                {"year": fy, "metric": "diluted_earnings", "value": diluted_earnings, "form": "10-K", "mode": "direct"},
                {"year": fy, "metric": "capex", "value": capex, "form": "10-K", "mode": "normalized_abs"},
                {"year": fy, "metric": "fcf", "value": fcf, "form": "10-K", "mode": fcf_mode},
            ]
        )

    df = pd.DataFrame(rows)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def _build_openrouter_url() -> str:
    """Akzeptiert verschiedene Base-URL-Formate und erzeugt immer den korrekten Endpoint."""
    raw = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions").strip()
    base = raw.rstrip("/")

    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/api/v1"):
        return f"{base}/chat/completions"
    if base == "https://openrouter.ai":
        return "https://openrouter.ai/api/v1/chat/completions"
    if "openrouter.ai" in base and "/api/v1" not in base:
        return f"{base}/api/v1/chat/completions"
    return base


class FilingDownloader:
    """Klasse zum Herunterladen von SEC 10-K Filings."""

    BASE_URL = "https://data.sec.gov/submissions"
    EDGAR_URL = "https://www.sec.gov/Archives/edgar/data"

    def __init__(self, download_dir: str = "./downloads", user_agent: Optional[str] = None):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        if user_agent is None:
            user_agent = SEC_HEADERS.get("User-Agent", "teaching-dash/1.0 (contact@example.com)")

        self.headers = {"User-Agent": user_agent}

    def get_submissions(self, cik: int) -> dict[str, Any]:
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/CIK{cik_padded}.json"

        print(f"Lade Submissions fuer CIK {cik_padded}...")
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()

        return response.json()

    def get_all_submissions(self, cik: int) -> dict[str, Any]:
        submissions = self.get_submissions(cik)

        recent = submissions.get("filings", {}).get("recent", {})
        files = submissions.get("filings", {}).get("files", [])

        if files:
            print(f"Lade {len(files)} zusaetzliche Filing-Archive...")

            for file_info in files:
                file_name = file_info.get("name")
                if not file_name:
                    continue

                url = f"{self.BASE_URL}/{file_name}"
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    response.raise_for_status()
                    older_data = response.json()

                    for key in recent.keys():
                        if key in older_data and isinstance(older_data[key], list):
                            recent[key].extend(older_data[key])

                    time.sleep(0.1)
                except Exception as exc:
                    print(f"[WARN] Konnte {file_name} nicht laden: {exc}")

        submissions["filings"]["recent"] = recent
        return submissions

    def find_10k_filing(
        self,
        cik: int,
        year: int,
        include_amendments: bool = True,
        use_all_filings: bool = True,
    ) -> Optional[dict[str, str]]:
        if use_all_filings:
            submissions = self.get_all_submissions(cik)
        else:
            submissions = self.get_submissions(cik)

        recent = submissions.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        fiscal_years = recent.get("fiscalYear", [])
        report_dates = recent.get("reportDate", [])

        for i, form in enumerate(forms):
            is_10k = (form == "10-K") or (include_amendments and form == "10-K/A")

            if not is_10k:
                continue

            fiscal_year = None
            if fiscal_years and i < len(fiscal_years) and fiscal_years[i]:
                fiscal_year = int(fiscal_years[i])
            elif report_dates and i < len(report_dates) and report_dates[i]:
                fiscal_year = int(report_dates[i][:4])

            if fiscal_year and fiscal_year == year:
                return {
                    "accessionNumber": accession_numbers[i],
                    "filingDate": filing_dates[i],
                    "primaryDocument": primary_docs[i],
                    "form": form,
                    "fiscalYear": str(fiscal_year),
                }

        print(f"Kein 10-K Filing fuer Fiscal Year {year} gefunden.")
        return None

    def download_filing_html(
        self,
        cik: int,
        accession_number: str,
        primary_doc: str,
        save_filename: Optional[str] = None,
    ) -> str:
        accession_no_nodashes = accession_number.replace("-", "")
        url = f"{self.EDGAR_URL}/{cik}/{accession_no_nodashes}/{primary_doc}"

        print(f"Lade Filing von {url}...")
        response = requests.get(url, headers=self.headers, timeout=60)
        response.raise_for_status()

        if save_filename is None:
            save_filename = f"CIK{str(cik).zfill(10)}_{accession_number.replace('-', '_')}_{primary_doc}"

        filepath = self.download_dir / save_filename
        filepath.write_text(response.text, encoding="utf-8")

        print(f"[OK] Filing gespeichert: {filepath}")
        return str(filepath)

    def download_complete_submission(
        self,
        cik: int,
        accession_number: str,
        save_filename: Optional[str] = None,
    ) -> str:
        accession_no_nodashes = accession_number.replace("-", "")
        url = f"{self.EDGAR_URL}/{cik}/{accession_no_nodashes}/{accession_number}.txt"

        print(f"Lade vollstaendige Submission von {url}...")
        response = requests.get(url, headers=self.headers, timeout=60)
        response.raise_for_status()

        if save_filename is None:
            save_filename = f"CIK{str(cik).zfill(10)}_{accession_number.replace('-', '_')}_complete.txt"

        filepath = self.download_dir / save_filename
        filepath.write_text(response.text, encoding="utf-8")

        print(f"[OK] Vollstaendige Submission gespeichert: {filepath}")
        return str(filepath)

    def download_filing_index(
        self,
        cik: int,
        accession_number: str,
        save_filename: Optional[str] = None,
    ) -> str:
        accession_no_nodashes = accession_number.replace("-", "")
        url = f"{self.EDGAR_URL}/{cik}/{accession_no_nodashes}/{accession_number}-index.html"

        print(f"Lade Filing Index von {url}...")
        response = requests.get(url, headers=self.headers, timeout=60)
        response.raise_for_status()

        if save_filename is None:
            save_filename = f"CIK{str(cik).zfill(10)}_{accession_number.replace('-', '_')}_index.html"

        filepath = self.download_dir / save_filename
        filepath.write_text(response.text, encoding="utf-8")

        print(f"[OK] Filing Index gespeichert: {filepath}")
        return str(filepath)

    def download_10k_for_year(
        self,
        cik: int,
        year: int,
        company_name: Optional[str] = None,
        complete_submission: bool = True,
    ) -> Optional[dict[str, Any]]:
        print(f"\n{'=' * 60}")
        print(f"Suche 10-K Filing fuer CIK {cik}, Jahr {year}")
        print(f"{'=' * 60}\n")

        filing_info = self.find_10k_filing(cik, year)
        if filing_info is None:
            return None

        print("[OK] Filing gefunden:")
        print(f"  Form: {filing_info['form']}")
        print(f"  Filing Date: {filing_info['filingDate']}")
        print(f"  Accession Number: {filing_info['accessionNumber']}")
        print(f"  Primary Document: {filing_info['primaryDocument']}\n")

        result: dict[str, Any] = {}

        if company_name:
            primary_filename = f"{company_name.replace(' ', '_')}_{year}_10K_primary.html"
        else:
            primary_filename = f"CIK{str(cik).zfill(10)}_{year}_10K_primary.html"

        result["primary"] = self.download_filing_html(
            cik=cik,
            accession_number=filing_info["accessionNumber"],
            primary_doc=filing_info["primaryDocument"],
            save_filename=primary_filename,
        )

        time.sleep(0.1)

        if complete_submission:
            if company_name:
                complete_filename = f"{company_name.replace(' ', '_')}_{year}_10K_complete.txt"
            else:
                complete_filename = f"CIK{str(cik).zfill(10)}_{year}_10K_complete.txt"

            result["complete"] = self.download_complete_submission(
                cik=cik,
                accession_number=filing_info["accessionNumber"],
                save_filename=complete_filename,
            )

            time.sleep(0.1)

            if company_name:
                index_filename = f"{company_name.replace(' ', '_')}_{year}_10K_index.html"
            else:
                index_filename = f"CIK{str(cik).zfill(10)}_{year}_10K_index.html"

            try:
                result["index"] = self.download_filing_index(
                    cik=cik,
                    accession_number=filing_info["accessionNumber"],
                    save_filename=index_filename,
                )
            except requests.HTTPError as exc:
                print(f"[WARN] Index nicht verfuegbar: {exc}")
                result["index"] = None

        time.sleep(0.2)

        result["filing_date"] = filing_info["filingDate"]
        result["fiscal_year"] = year
        return result

    def list_all_10k_filings(self, cik: int) -> list[dict[str, str]]:
        submissions = self.get_submissions(cik)
        recent = submissions.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])

        filings_10k = []
        for i, form in enumerate(forms):
            if form in ["10-K", "10-K/A"]:
                filings_10k.append(
                    {
                        "form": form,
                        "filingDate": filing_dates[i],
                        "accessionNumber": accession_numbers[i],
                        "primaryDocument": primary_docs[i],
                    }
                )

        return filings_10k

    def find_latest_10q_filing(self, cik: int) -> Optional[dict[str, str]]:
        submissions = self.get_submissions(cik)
        recent = submissions.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])

        latest_10k_date = None
        for i, form in enumerate(forms):
            if form in ["10-K", "10-K/A"]:
                latest_10k_date = filing_dates[i]
                break

        for i, form in enumerate(forms):
            if form in ["10-Q", "10-Q/A"]:
                filing_date = filing_dates[i]
                if latest_10k_date is None or filing_date > latest_10k_date:
                    return {
                        "accessionNumber": accession_numbers[i],
                        "filingDate": filing_date,
                        "primaryDocument": primary_docs[i],
                        "form": form,
                    }

        print("Kein 10-Q Filing nach dem letzten 10-K gefunden.")
        return None

    def find_recent_10q_filings(
        self,
        cik: int,
        max_filings: int = 4,
        after_date: Optional[str] = None,
    ) -> list[dict[str, str]]:
        submissions = self.get_submissions(cik)
        recent = submissions.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])

        latest_10k_date = after_date
        if latest_10k_date is None:
            for i, form in enumerate(forms):
                if form in ["10-K", "10-K/A"]:
                    latest_10k_date = filing_dates[i]
                    break

        tenq_candidates = []
        for i, form in enumerate(forms):
            if form in ["10-Q", "10-Q/A"]:
                filing_date = filing_dates[i]
                if latest_10k_date is None or filing_date > latest_10k_date:
                    tenq_candidates.append(
                        {
                            "accessionNumber": accession_numbers[i],
                            "filingDate": filing_date,
                            "primaryDocument": primary_docs[i],
                            "form": form,
                        }
                    )

        tenq_candidates.sort(key=lambda x: x["filingDate"], reverse=True)
        return tenq_candidates[:max_filings]

    def download_multiple_years(
        self,
        cik: int,
        years: list[int],
        company_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        results = []

        for year in years:
            result = self.download_10k_for_year(cik, year, company_name)
            if result:
                results.append(result)
            time.sleep(0.2)

        return results

    def download_latest_10q(
        self,
        cik: int,
        company_name: Optional[str] = None,
        complete_submission: bool = True,
    ) -> Optional[dict[str, Any]]:
        print(f"\n{'=' * 60}")
        print(f"Suche neuestes 10-Q Filing fuer CIK {cik}")
        print(f"{'=' * 60}\n")

        filing_info = self.find_latest_10q_filing(cik)
        if filing_info is None:
            return None

        print("[OK] Filing gefunden:")
        print(f"  Form: {filing_info['form']}")
        print(f"  Filing Date: {filing_info['filingDate']}")
        print(f"  Accession Number: {filing_info['accessionNumber']}")
        print(f"  Primary Document: {filing_info['primaryDocument']}\n")

        result: dict[str, Any] = {}

        if company_name:
            primary_filename = f"{company_name.replace(' ', '_')}_{filing_info['filingDate']}_10Q_primary.html"
        else:
            primary_filename = f"CIK{str(cik).zfill(10)}_{filing_info['filingDate']}_10Q_primary.html"

        result["primary"] = self.download_filing_html(
            cik=cik,
            accession_number=filing_info["accessionNumber"],
            primary_doc=filing_info["primaryDocument"],
            save_filename=primary_filename,
        )

        time.sleep(0.1)

        if complete_submission:
            if company_name:
                complete_filename = f"{company_name.replace(' ', '_')}_{filing_info['filingDate']}_10Q_complete.txt"
            else:
                complete_filename = f"CIK{str(cik).zfill(10)}_{filing_info['filingDate']}_10Q_complete.txt"

            result["complete"] = self.download_complete_submission(
                cik=cik,
                accession_number=filing_info["accessionNumber"],
                save_filename=complete_filename,
            )

            time.sleep(0.1)

            if company_name:
                index_filename = f"{company_name.replace(' ', '_')}_{filing_info['filingDate']}_10Q_index.html"
            else:
                index_filename = f"CIK{str(cik).zfill(10)}_{filing_info['filingDate']}_10Q_index.html"

            try:
                result["index"] = self.download_filing_index(
                    cik=cik,
                    accession_number=filing_info["accessionNumber"],
                    save_filename=index_filename,
                )
            except requests.HTTPError as exc:
                print(f"[WARN] Index nicht verfuegbar: {exc}")
                result["index"] = None

        return result

    def download_recent_10q(
        self,
        cik: int,
        company_name: Optional[str] = None,
        complete_submission: bool = True,
        max_filings: int = 4,
        after_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        print(f"\n{'=' * 60}")
        print(f"Suche bis zu {max_filings} neueste 10-Q Filings fuer CIK {cik}")
        print(f"{'=' * 60}\n")

        filing_infos = self.find_recent_10q_filings(cik=cik, max_filings=max_filings, after_date=after_date)
        if not filing_infos:
            print("Keine passenden 10-Q Filings gefunden.")
            return []

        results = []
        for filing_info in filing_infos:
            print("[OK] Filing gefunden:")
            print(f"  Form: {filing_info['form']}")
            print(f"  Filing Date: {filing_info['filingDate']}")
            print(f"  Accession Number: {filing_info['accessionNumber']}")
            print(f"  Primary Document: {filing_info['primaryDocument']}\n")

            result: dict[str, Any] = {}

            if company_name:
                primary_filename = f"{company_name.replace(' ', '_')}_{filing_info['filingDate']}_10Q_primary.html"
            else:
                primary_filename = f"CIK{str(cik).zfill(10)}_{filing_info['filingDate']}_10Q_primary.html"

            result["primary"] = self.download_filing_html(
                cik=cik,
                accession_number=filing_info["accessionNumber"],
                primary_doc=filing_info["primaryDocument"],
                save_filename=primary_filename,
            )
            result["filing_date"] = filing_info["filingDate"]
            filing_date = filing_info.get("filingDate")
            result["fiscal_year"] = int(filing_date[:4]) if filing_date and len(filing_date) >= 4 else None

            time.sleep(0.1)

            if complete_submission:
                if company_name:
                    complete_filename = f"{company_name.replace(' ', '_')}_{filing_info['filingDate']}_10Q_complete.txt"
                else:
                    complete_filename = f"CIK{str(cik).zfill(10)}_{filing_info['filingDate']}_10Q_complete.txt"

                result["complete"] = self.download_complete_submission(
                    cik=cik,
                    accession_number=filing_info["accessionNumber"],
                    save_filename=complete_filename,
                )

                time.sleep(0.1)

                if company_name:
                    index_filename = f"{company_name.replace(' ', '_')}_{filing_info['filingDate']}_10Q_index.html"
                else:
                    index_filename = f"CIK{str(cik).zfill(10)}_{filing_info['filingDate']}_10Q_index.html"

                try:
                    result["index"] = self.download_filing_index(
                        cik=cik,
                        accession_number=filing_info["accessionNumber"],
                        save_filename=index_filename,
                    )
                except requests.HTTPError as exc:
                    print(f"[WARN] Index nicht verfuegbar: {exc}")
                    result["index"] = None

            result["filing_date"] = filing_info["filingDate"]
            results.append(result)
            time.sleep(0.2)

        return results

    def download_complete_package(
        self,
        cik: int,
        current_year: int,
        company_name: Optional[str] = None,
    ) -> dict[str, Any]:
        print(f"\n{'=' * 70}")
        print(f"KOMPLETTER DOWNLOAD FUER {company_name or f'CIK {cik}'}")
        print(f"{'=' * 70}\n")

        years = [current_year - 2, current_year - 1, current_year]
        print(f"Lade 10-K Reports fuer Jahre: {years}")
        tenk_files = self.download_multiple_years(cik, years, company_name)

        reference_10k_date = None
        for filing in tenk_files:
            if filing.get("fiscal_year") == current_year:
                reference_10k_date = filing.get("filing_date")
                break

        print("\nLade neueste 10-Q Reports...")
        tenq_files = self.download_recent_10q(cik, company_name, max_filings=4, after_date=reference_10k_date)
        tenq_file = tenq_files[0] if tenq_files else None

        print(f"\n{'=' * 70}")
        print("DOWNLOAD ABGESCHLOSSEN")
        print(f"{'=' * 70}")
        print(f"10-K Reports: {len(tenk_files)} Dateien")
        print(f"10-Q Reports: {len(tenq_files)} Dateien")
        print("\nJedes Filing enthaelt:")
        print("  - primary HTML (primaryDocument, kann Cover Page sein)")
        print("  - complete .txt (vollstaendige Submission mit allen Dokumenten)")
        print("  - index HTML (Uebersicht aller Dokumente)")

        return {"10k_files": tenk_files, "10q_file": tenq_file, "10q_files": tenq_files}

    def download_and_extract_for_chatbot(
        self,
        cik: int,
        current_year: int,
        company_name: Optional[str] = None,
        min_chars: int = 20000,
    ) -> dict[str, Any]:
        print(f"\n{'=' * 70}")
        print(f"CHATBOT-DOWNLOAD & TEXT-EXTRAKTION FUER {company_name or f'CIK {cik}'}")
        print(f"{'=' * 70}\n")

        package = self.download_complete_package(cik, current_year, company_name)

        print(f"\n{'=' * 70}")
        print("TEXT-EXTRAKTION")
        print(f"{'=' * 70}\n")

        texts: dict[str, Any] = {}
        metadata = {
            "sources": {},
            "company": company_name or f"CIK_{cik}",
            "years": [current_year - 2, current_year - 1, current_year],
            "has_10q": package["10q_file"] is not None,
            "10q_count": len(package.get("10q_files", [])),
            "10q_dates": [f.get("filing_date") for f in package.get("10q_files", []) if f.get("filing_date")],
        }

        years = [current_year - 2, current_year - 1, current_year]
        for year, filing in zip(years, package["10k_files"]):
            try:
                print(f"Extrahiere 10-K {year}...")
                text, source = extract_clean_10k_text(filing, min_chars)
                texts[f"10k_{year}"] = text
                metadata["sources"][f"10k_{year}"] = source
                print(f"  [OK] {len(text):,} Zeichen aus {source}")
            except ValueError as exc:
                print(f"  [ERROR] Fehler: {exc}")
                texts[f"10k_{year}"] = None
                metadata["sources"][f"10k_{year}"] = "failed"

        tenq_files = package.get("10q_files") or ([] if package["10q_file"] is None else [package["10q_file"]])
        if tenq_files:
            latest_set = False
            for idx, tenq_filing in enumerate(tenq_files):
                filing_date = tenq_filing.get("filing_date")
                key = f"10q_{filing_date}" if filing_date else f"10q_{idx + 1}"
                try:
                    print(f"\nExtrahiere 10-Q ({filing_date or idx + 1})...")
                    text, source = extract_clean_10k_text(tenq_filing, min_chars=10000)
                    texts[key] = text
                    metadata["sources"][key] = source
                    if not latest_set:
                        texts["10q_latest"] = text
                        metadata["sources"]["10q_latest"] = source
                        latest_set = True
                    print(f"  [OK] {len(text):,} Zeichen aus {source}")
                except ValueError as exc:
                    print(f"  [ERROR] Fehler: {exc}")
                    texts[key] = None
                    metadata["sources"][key] = "failed"
            if not latest_set:
                texts["10q_latest"] = None
                metadata["sources"]["10q_latest"] = "failed"
        else:
            texts["10q_latest"] = None
            metadata["sources"]["10q_latest"] = "not_available"

        texts["metadata"] = metadata

        print(f"\n{'=' * 70}")
        print("EXTRAKTION ABGESCHLOSSEN")
        print(f"{'=' * 70}")
        print("Erfolgreich extrahiert:")
        for key, text in texts.items():
            if key != "metadata" and text:
                print(f"  [OK] {key}: {len(text):,} Zeichen, {len(text.split()):,} Woerter")

        return texts


def _clean_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ")
    return _clean_whitespace(text)


def extract_10k_text_from_complete_submission(path_txt: str) -> str:
    raw = Path(path_txt).read_text(encoding="utf-8", errors="ignore")

    docs = raw.split("<DOCUMENT>")
    best_text = ""

    for d in docs[1:]:
        m_type = re.search(r"<TYPE>\s*([^\s<]+)", d)
        doc_type = m_type.group(1).strip().upper() if m_type else ""

        if doc_type in {"10-K", "10K"}:
            m_text = re.search(r"<TEXT>(.*)</TEXT>", d, flags=re.DOTALL | re.IGNORECASE)
            if not m_text:
                continue
            content = m_text.group(1)

            if "<html" in content.lower() or "<table" in content.lower():
                cand = html_to_text(content)
            else:
                cand = _clean_whitespace(content)

            if len(cand) > len(best_text):
                best_text = cand

    return best_text


def extract_10k_text_from_primary_html(path_html: str) -> str:
    html = Path(path_html).read_text(encoding="utf-8", errors="ignore")
    return html_to_text(html)


def extract_clean_10k_text(filing_paths: dict[str, Any], min_chars: int = 20000) -> tuple[str, str]:
    text = ""
    source = ""

    complete_path = filing_paths.get("complete")
    primary_path = filing_paths.get("primary")

    if complete_path:
        text = extract_10k_text_from_complete_submission(complete_path)
        source = "complete_txt"

    if len(text) < min_chars and primary_path:
        text2 = extract_10k_text_from_primary_html(primary_path)
        if len(text2) > len(text):
            text = text2
            source = "primary_html"

    if len(text) < min_chars:
        raise ValueError(f"Extracted text too short ({len(text)} chars). Likely not the full 10-K.")

    return text, source


__all__ = [
    "SEC_HEADERS",
    "FilingDownloader",
    "_build_openrouter_url",
    "extract_clean_10k_text",
    "load_three_metrics",
]
