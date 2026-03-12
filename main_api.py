"""Minimal SEC Company Facts API helper used by the teaching notebook."""

from __future__ import annotations

import requests

SEC_HEADERS = {
    "User-Agent": "teaching-dash/1.0 (contact@example.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}

_BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
_ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "20-F/A"}


def _normalize_cik(cik: int | str) -> str:
    return str(cik).strip().zfill(10)


def _latest_fy_value(companyfacts: dict, taxonomy: str, tag: str, fy: int, unit: str):
    entries = (
        companyfacts.get("facts", {})
        .get(taxonomy, {})
        .get(tag, {})
        .get("units", {})
        .get(unit, [])
    )
    if not entries:
        return None

    annual = [
        row
        for row in entries
        if row.get("fy") == fy
        and row.get("val") is not None
        and str(row.get("form", "")).upper() in _ANNUAL_FORMS
    ]
    if not annual:
        return None

    # Prefer most recently filed value for a given FY.
    annual.sort(key=lambda x: (x.get("filed", ""), x.get("end", "")))
    return annual[-1].get("val")


def get_core_metrics_from_companyfacts(cik: int | str, fy: int) -> dict:
    """Return core annual metrics for one company and fiscal year.

    Returns keys:
    - diluted_eps
    - capex_abs
    - operating_cf
    - free_cash_flow
    """
    cik10 = _normalize_cik(cik)
    url = _BASE_URL.format(cik=cik10)

    response = requests.get(url, headers=SEC_HEADERS, timeout=30)
    response.raise_for_status()
    companyfacts = response.json()

    diluted_eps = _latest_fy_value(companyfacts, "us-gaap", "EarningsPerShareDiluted", fy, "USD/shares")

    capex_raw = _latest_fy_value(
        companyfacts,
        "us-gaap",
        "PaymentsToAcquirePropertyPlantAndEquipment",
        fy,
        "USD",
    )
    # SEC cash flow outflows are often negative, but teaching examples expect positive CapEx.
    capex_abs = abs(capex_raw) if capex_raw is not None else None

    operating_cf = _latest_fy_value(
        companyfacts,
        "us-gaap",
        "NetCashProvidedByUsedInOperatingActivities",
        fy,
        "USD",
    )

    free_cash_flow = None
    if operating_cf is not None and capex_abs is not None:
        free_cash_flow = operating_cf - capex_abs

    return {
        "diluted_eps": diluted_eps,
        "capex_abs": capex_abs,
        "operating_cf": operating_cf,
        "free_cash_flow": free_cash_flow,
    }
