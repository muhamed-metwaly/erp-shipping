"""
Shared trip revenue, expenses, and custody totals (list, form, print).

Provides financial calculations for trips including:
- Revenue from linked shipping requests
- Expenses and custody allocations
- Net income calculation
- Performance optimization through caching
"""
from typing import Dict, Any, List, Optional
import logging

import frappe
from frappe.utils import flt

logger = logging.getLogger(__name__)

# Cache settings
CACHE_TTL = 300  # 5 minutes


def _get_cache_key(trip_name: str) -> str:
    """Generate cache key for trip financial summary."""
    return f"haulage_trip_financial_summary_{trip_name}"


def _invalidate_trip_cache(trip_name: str) -> None:
    """Invalidate financial summary cache for a trip."""
    cache_key = _get_cache_key(trip_name)
    frappe.cache().delete(cache_key)
    logger.debug(f"Cache invalidated for trip {trip_name}")


@frappe.whitelist()
def get_trip_financial_summary(trip_name: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Calculate financial breakdown for one trip (used by accounting UI and print).
    
    Computes:
    - Revenue from all shipments
    - Total expenses allocated to trip
    - Total custody amounts
    - Net income (revenue - expenses - custody)
    
    Results are cached for 5 minutes to improve performance on accounting pages.
    
    Args:
        trip_name: The Haulage Trip document name
        use_cache: Whether to use cached results if available (default: True)
        
    Returns:
        Dictionary with financial summary including:
        - trip: Trip name
        - trip_status: Current trip status
        - driver: Assigned driver
        - truck: Assigned truck
        - revenue_lines: List of shipment revenue details
        - total_revenue: Sum of all shipment prices
        - total_expenses: Sum of all trip expenses
        - total_custody: Sum of all custody amounts
        - net_income: revenue - expenses - custody
        
    Note:
        Returns empty summary if trip doesn't exist. Safe to call with invalid names.
        Cache is automatically invalidated on trip status changes or when child
        records (shipments, expenses, custodies) are updated.
    """
    trip_name = (trip_name or "").strip()
    
    if not trip_name:
        return {
            "revenue_lines": [],
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "total_custody": 0.0,
            "net_income": 0.0,
            "trip_status": "",
        }
    
    # Try cache first
    if use_cache:
        cache_key = _get_cache_key(trip_name)
        cached = frappe.cache().get_value(cache_key)
        if cached:
            logger.debug(f"Cache hit for trip {trip_name}")
            return cached
    
    if not frappe.db.exists("Haulage Trip", trip_name):
        logger.warning(f"get_trip_financial_summary called for non-existent trip: {trip_name}")
        return {
            "revenue_lines": [],
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "total_custody": 0.0,
            "net_income": 0.0,
            "trip_status": "",
        }

    try:
        trip = frappe.get_doc("Haulage Trip", trip_name)
    except Exception as e:
        logger.error(f"Error fetching trip {trip_name}: {str(e)}")
        return {
            "revenue_lines": [],
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "total_custody": 0.0,
            "net_income": 0.0,
            "trip_status": "",
        }

    # Calculate revenue from shipments
    revenue_lines: List[Dict[str, Any]] = []
    total_revenue = 0.0
    
    for row in trip.get("shipments") or []:
        if not row.shipping_request:
            continue
            
        try:
            sr = frappe.db.get_value(
                "Shipping Request",
                row.shipping_request,
                ["customer", "agreed_price", "pickup_location", "delivery_location"],
                as_dict=True,
            )
        except Exception as e:
            logger.error(f"Error fetching shipping request {row.shipping_request} for trip {trip_name}: {str(e)}")
            continue
            
        if not sr:
            logger.warning(f"Shipping request {row.shipping_request} not found for trip {trip_name}")
            continue
            
        amount = flt(sr.agreed_price)
        total_revenue += amount
        revenue_lines.append(
            {
                "shipping_request": row.shipping_request,
                "customer": sr.customer,
                "pickup_location": sr.pickup_location or "",
                "delivery_location": sr.delivery_location or "",
                "agreed_price": amount,
            }
        )

    # Calculate expenses and custody
    total_expenses = sum(flt(e.amount) for e in (trip.get("trip_expenses") or []))
    total_custody = sum(flt(c.amount) for c in (trip.get("trip_custodies") or []))
    net_income = total_revenue - total_expenses - total_custody
    
    summary = {
        "trip": trip_name,
        "trip_status": trip.trip_status,
        "driver": trip.driver,
        "truck": trip.truck,
        "revenue_lines": revenue_lines,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "total_custody": total_custody,
        "net_income": net_income,
    }
    
    # Store in cache
    if use_cache:
        cache_key = _get_cache_key(trip_name)
        frappe.cache().set_value(cache_key, summary, expires_in_sec=CACHE_TTL)
        logger.debug(f"Cache stored for trip {trip_name} with TTL={CACHE_TTL}s")
    
    logger.debug(f"Trip {trip_name} financial summary: revenue={total_revenue}, expenses={total_expenses}, custody={total_custody}, net={net_income}")
    
    return summary
