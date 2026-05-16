"""
Haulage Logistics API Module

Provides REST endpoints for:
- Trip status management
- Sales invoice creation from shipments
- Journal entry creation for trip expenses
- Account validation and financial calculations
"""
from collections import defaultdict
from typing import Dict, Any, List
import logging

import frappe
from frappe import _
from frappe.utils import flt

from haulage_mgmt.haulage_logistics.trip_status import apply_trip_status_action

# Setup structured logging
logger = logging.getLogger(__name__)


def _log_api_call(action: str, user: str, details: str = None):
    """Log API calls with user and action context."""
    log_msg = f"API: {action} by user={user}"
    if details:
        log_msg += f" | {details}"
    logger.info(log_msg)


@frappe.whitelist()
def set_trip_status(trip_name: str, action: str) -> Dict[str, str]:
    """
    Update trip status via action button: start | pause | arrive | cancel.
    
    Args:
        trip_name: The Haulage Trip document name
        action: The status action to perform (start, pause, arrive, cancel)
        
    Returns:
        Dictionary with updated trip name and status
        
    Raises:
        frappe.ValidationError: If trip doesn't exist or action is invalid
        frappe.PermissionError: If user lacks write permission
    """
    trip_name = (trip_name or "").strip()
    action = (action or "").strip().lower()
    
    if not trip_name or not frappe.db.exists("Haulage Trip", trip_name):
        frappe.throw(
            _("Trip {0} does not exist.").format(trip_name),
            title=_("Invalid Trip")
        )
    
    if not frappe.has_permission("Haulage Trip", "write", doc=trip_name):
        frappe.throw(_("You do not have permission to edit this trip."), frappe.PermissionError)

    trip = frappe.get_doc("Haulage Trip", trip_name)
    apply_trip_status_action(trip, action)
    trip.save()
    
    _log_api_call("set_trip_status", frappe.session.user, f"trip={trip_name}, action={action}, new_status={trip.trip_status}")
    
    return {"name": trip.name, "trip_status": trip.trip_status}


@frappe.whitelist()
def create_sales_invoice_from_shipment(trip_name: str, shipping_request_name: str) -> Dict[str, str]:
    """
    Create a draft Sales Invoice from a shipment on a trip.
    
    Args:
        trip_name: The Haulage Trip document name
        shipping_request_name: The Shipping Request document name
        
    Returns:
        Dictionary with created invoice name
        
    Raises:
        frappe.PermissionError: If user lacks permissions
        frappe.ValidationError: If shipment/trip is invalid or settings missing
    """
    trip_name = (trip_name or "").strip()
    shipping_request_name = (shipping_request_name or "").strip()
    
    if not trip_name or not frappe.db.exists("Haulage Trip", trip_name):
        frappe.throw(_("Trip {0} does not exist.").format(trip_name), title=_("Invalid Trip"))
    if not frappe.has_permission("Haulage Trip", "write", doc=trip_name):
        frappe.throw(_("You do not have permission to edit this trip."), frappe.PermissionError)
    if not frappe.has_permission("Sales Invoice", "create"):
        frappe.throw(
            _("You do not have permission to create a Sales Invoice."),
            frappe.PermissionError
        )

    trip = _validate_shipment_on_trip(trip_name, shipping_request_name)

    item_code = frappe.db.get_single_value(
        "Haulage Logistics Settings", "default_freight_item"
    )
    if not item_code:
        frappe.throw(
            _(
                "Please set the default freight Item in Haulage Logistics Settings before creating the invoice."
            ),
            title=_("Missing Configuration")
        )

    sr = frappe.get_doc("Shipping Request", shipping_request_name)
    if not frappe.has_permission("Shipping Request", "read", doc=sr.name):
        frappe.throw(
            _("You do not have permission to read this shipping request."),
            frappe.PermissionError
        )

    company = trip.get("company") or frappe.defaults.get_user_default("Company")
    if not company:
        companies = frappe.get_all("Company", pluck="name", order_by="creation asc", limit=1)
        company = companies[0] if companies else None
    
    if not company:
        frappe.throw(
            _("No company available. Please set a default company or specify one on the trip."),
            title=_("No Company")
        )

    si = frappe.new_doc("Sales Invoice")
    si.customer = sr.customer
    si.company = company
    si.posting_date = frappe.utils.today()
    si.due_date = frappe.utils.add_days(si.posting_date, 30)
    si.append(
        "items",
        {
            "item_code": item_code,
            "qty": 1,
            "rate": flt(sr.agreed_price),
            "description": _("Freight — request {0} — trip {1}").format(sr.name, trip_name),
        },
    )
    if hasattr(si, "set_missing_values"):
        si.set_missing_values()
    
    si.flags.ignore_permissions = True
    si.insert()
    
    _log_api_call(
        "create_sales_invoice_from_shipment",
        frappe.session.user,
        f"trip={trip_name}, shipping_request={shipping_request_name}, invoice={si.name}, amount={sr.agreed_price}"
    )
    
    return {"name": si.name}


@frappe.whitelist()
def create_trip_expense_journal_entry(trip_name: str) -> Dict[str, str]:
    """
    Create a draft Journal Entry for trip expenses (debit expense accounts, credit configured account).
    
    Args:
        trip_name: The Haulage Trip document name
        
    Returns:
        Dictionary with created journal entry name
        
    Raises:
        frappe.PermissionError: If user lacks permissions
        frappe.ValidationError: If trip data is invalid or incomplete
    """
    trip_name = (trip_name or "").strip()
    if not trip_name or not frappe.db.exists("Haulage Trip", trip_name):
        frappe.throw(_("Trip {0} does not exist.").format(trip_name), title=_("Invalid Trip"))
    if not frappe.has_permission("Haulage Trip", "write", doc=trip_name):
        frappe.throw(_("You do not have permission to edit this trip."), frappe.PermissionError)
    if not frappe.has_permission("Journal Entry", "create"):
        frappe.throw(
            _("You need permission to create a Journal Entry (e.g. Accounts Manager or a custom role)."),
            frappe.PermissionError,
        )

    trip = frappe.get_doc("Haulage Trip", trip_name)
    
    # Validation: check trip status
    if trip.trip_status == "Cancelled":
        frappe.throw(_("Cannot post expenses for a cancelled trip."))
    
    # Validation: check for existing journal entry
    if trip.trip_journal_entry:
        frappe.throw(
            _("A journal entry is already linked: {0}. Delete it first or use a different trip.").format(
                trip.trip_journal_entry
            )
        )

    # Get credit account configuration
    credit_acc = frappe.db.get_single_value(
        "Haulage Logistics Settings", "trip_expense_credit_account"
    )
    if not credit_acc:
        frappe.throw(
            _("Please configure the expense credit account in Haulage Logistics Settings."),
            title=_("Missing Configuration")
        )

    # Validate credit account
    _validate_account_company(credit_acc, trip.company)

    # Build expense totals grouped by GL account
    totals: Dict[str, float] = defaultdict(float)
    invalid_expenses: List[str] = []
    
    for idx, row in enumerate(trip.get("trip_expenses") or []):
        if not row.expense_type or not flt(row.amount):
            continue
            
        # Get GL account for expense type
        exp_acc = frappe.db.get_value("Haulage Expense Type", row.expense_type, "account")
        if not exp_acc:
            invalid_expenses.append(
                f"Row {idx + 1}: Expense type '{row.expense_type}' has no GL account configured"
            )
            continue
        
        # Validate expense account
        try:
            _validate_account_company(exp_acc, trip.company)
        except frappe.ValidationError as e:
            invalid_expenses.append(f"Row {idx + 1}: {str(e)}")
            continue
            
        totals[exp_acc] += flt(row.amount)

    if invalid_expenses:
        error_msg = _("Expense validation failed:\n") + "\n".join(invalid_expenses)
        frappe.throw(error_msg, title=_("Invalid Expenses"))

    if not totals:
        frappe.throw(
            _("There are no valid expense lines with amounts to post."),
            title=_("No Expenses")
        )

    # Create journal entry
    je = frappe.new_doc("Journal Entry")
    je.company = trip.company
    je.posting_date = frappe.utils.today()
    je.voucher_type = "Journal Entry"
    je.user_remark = _("Haulage trip expenses {0}").format(trip.name)

    # Add debit entries
    grand_total = 0.0
    for acc, amt in totals.items():
        je.append(
            "accounts",
            {
                "account": acc,
                "debit_in_account_currency": amt,
                "credit_in_account_currency": 0,
            },
        )
        grand_total += amt

    # Add credit entry
    je.append(
        "accounts",
        {
            "account": credit_acc,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": grand_total,
        },
    )

    je.flags.ignore_permissions = True
    je.insert()
    frappe.db.set_value("Haulage Trip", trip.name, "trip_journal_entry", je.name)
    
    _log_api_call(
        "create_trip_expense_journal_entry",
        frappe.session.user,
        f"trip={trip_name}, je={je.name}, amount={grand_total}"
    )
    
    return {"name": je.name}


def _validate_account_company(account: str, company: str) -> None:
    """
    Validate that an account exists and belongs to the specified company.
    
    Args:
        account: The GL account code/name
        company: The company name
        
    Raises:
        frappe.ValidationError: If account is missing, doesn't exist, or belongs to different company
    """
    if not account:
        frappe.throw(
            _("Account name is required but was empty."),
            title=_("Missing Account")
        )
    
    # Check if account exists
    acc_doc = frappe.db.get_value("Account", account, ["name", "company", "disabled"])
    if not acc_doc:
        frappe.throw(
            _("Account {0} does not exist. Please create it in Chart of Accounts.").format(account),
            title=_("Invalid Account")
        )
    
    acc_name, acc_company, acc_disabled = acc_doc
    
    # Check if account is disabled
    if acc_disabled:
        frappe.throw(
            _("Account {0} is disabled and cannot be used.").format(account),
            title=_("Disabled Account")
        )
    
    # Check if account belongs to correct company
    if company and acc_company != company:
        frappe.throw(
            _("Account {0} belongs to company {1} but trip is in company {2}.").format(
                account, acc_company, company
            ),
            title=_("Company Mismatch")
        )
    
    _log_api_call("validate_account", frappe.session.user, f"account={account}, company={company}")


def _validate_shipment_on_trip(trip_name: str, shipping_request_name: str) -> Any:
    """
    Validate that a shipping request is linked to the specified trip.
    
    Args:
        trip_name: The Haulage Trip document name
        shipping_request_name: The Shipping Request document name
        
    Returns:
        The trip document
        
    Raises:
        frappe.ValidationError: If shipment is not on the trip
    """
    trip = frappe.get_doc("Haulage Trip", trip_name)
    linked = {r.shipping_request for r in (trip.get("shipments") or []) if r.shipping_request}
    
    if shipping_request_name not in linked:
        available = ", ".join(linked) if linked else "none"
        frappe.throw(
            _("Shipping request {0} is not linked to trip {1}. Available shipments: {2}").format(
                shipping_request_name, trip_name, available
            ),
            title=_("Invalid Shipment")
        )
    
    return trip


# ============================================================================
# Batch Operations API (Quick Win Feature)
# ============================================================================


@frappe.whitelist()
def create_batch_sales_invoices(trip_ids: List[str]) -> Dict[str, Any]:
    """
    Create Sales Invoices for all shipments in multiple trips (batch operation).
    
    This is a quick-win feature to speed up invoice generation for multiple trips.
    
    Args:
        trip_ids: List of Haulage Trip document names (JSON string or Python list)
        
    Returns:
        Dictionary with:
        - success: List of created invoice names
        - failed: List of dictionaries with failed trip info and error message
        - total_created: Count of successfully created invoices
        - total_failed: Count of failed operations
        
    Note:
        - Each trip's shipments are processed independently
        - Partial failures are handled gracefully (some succeed, some fail)
        - Requires read/write permission on Haulage Trip and Sales Invoice create permission
    """
    if isinstance(trip_ids, str):
        try:
            trip_ids = frappe.parse_json(trip_ids)
        except Exception as e:
            frappe.throw(
                _("Invalid trip_ids format: {0}").format(str(e)),
                title=_("Invalid Input")
            )
    
    if not isinstance(trip_ids, list) or not trip_ids:
        frappe.throw(
            _("trip_ids must be a non-empty list of trip names"),
            title=_("Invalid Input")
        )
    
    # Check permissions
    if not frappe.has_permission("Sales Invoice", "create"):
        frappe.throw(
            _("You do not have permission to create Sales Invoices."),
            frappe.PermissionError
        )
    
    success_invoices: List[str] = []
    failed_invoices: List[Dict[str, str]] = []
    
    _log_api_call(
        "create_batch_sales_invoices",
        frappe.session.user,
        f"trip_count={len(trip_ids)}"
    )
    
    for trip_name in trip_ids:
        try:
            trip_name = (trip_name or "").strip()
            if not trip_name:
                continue
            
            if not frappe.db.exists("Haulage Trip", trip_name):
                failed_invoices.append({
                    "trip": trip_name,
                    "error": _("Trip does not exist")
                })
                continue
            
            if not frappe.has_permission("Haulage Trip", "write", doc=trip_name):
                failed_invoices.append({
                    "trip": trip_name,
                    "error": _("Permission denied")
                })
                continue
            
            trip = frappe.get_doc("Haulage Trip", trip_name)
            invoice_count = 0
            
            # Create invoice for each shipment on the trip
            for shipment in trip.get("shipments") or []:
                if not shipment.shipping_request:
                    continue
                
                try:
                    result = create_sales_invoice_from_shipment(trip_name, shipment.shipping_request)
                    success_invoices.append(result["name"])
                    invoice_count += 1
                except Exception as e:
                    logger.warning(f"Failed to create invoice for shipment {shipment.shipping_request} on trip {trip_name}: {str(e)}")
                    # Continue with next shipment
                    continue
            
            if invoice_count == 0 and trip.get("shipments"):
                failed_invoices.append({
                    "trip": trip_name,
                    "error": _("No invoices could be created (check shipment data)")
                })
        
        except Exception as e:
            logger.error(f"Error processing trip {trip_name} in batch invoice creation: {str(e)}")
            failed_invoices.append({
                "trip": trip_name,
                "error": str(e)[:100]  # Truncate error message
            })
    
    return {
        "success": success_invoices,
        "failed": failed_invoices,
        "total_created": len(success_invoices),
        "total_failed": len(failed_invoices),
    }


@frappe.whitelist()
def create_batch_journal_entries(trip_ids: List[str]) -> Dict[str, Any]:
    """
    Create Journal Entries for expenses in multiple trips (batch operation).
    
    This is a quick-win feature to speed up journal entry generation for multiple trips.
    
    Args:
        trip_ids: List of Haulage Trip document names (JSON string or Python list)
        
    Returns:
        Dictionary with:
        - success: List of created journal entry names
        - failed: List of dictionaries with failed trip info and error message
        - total_created: Count of successfully created journal entries
        - total_failed: Count of failed operations
        
    Note:
        - Each trip is processed independently
        - Partial failures are handled gracefully
        - Requires write permission on Haulage Trip and Journal Entry create permission
        - Skips trips with no expenses or already-linked journal entries
    """
    if isinstance(trip_ids, str):
        try:
            trip_ids = frappe.parse_json(trip_ids)
        except Exception as e:
            frappe.throw(
                _("Invalid trip_ids format: {0}").format(str(e)),
                title=_("Invalid Input")
            )
    
    if not isinstance(trip_ids, list) or not trip_ids:
        frappe.throw(
            _("trip_ids must be a non-empty list of trip names"),
            title=_("Invalid Input")
        )
    
    # Check permissions
    if not frappe.has_permission("Journal Entry", "create"):
        frappe.throw(
            _("You do not have permission to create Journal Entries."),
            frappe.PermissionError
        )
    
    success_entries: List[str] = []
    failed_entries: List[Dict[str, str]] = []
    
    _log_api_call(
        "create_batch_journal_entries",
        frappe.session.user,
        f"trip_count={len(trip_ids)}"
    )
    
    for trip_name in trip_ids:
        try:
            trip_name = (trip_name or "").strip()
            if not trip_name:
                continue
            
            if not frappe.db.exists("Haulage Trip", trip_name):
                failed_entries.append({
                    "trip": trip_name,
                    "error": _("Trip does not exist")
                })
                continue
            
            if not frappe.has_permission("Haulage Trip", "write", doc=trip_name):
                failed_entries.append({
                    "trip": trip_name,
                    "error": _("Permission denied")
                })
                continue
            
            trip = frappe.get_doc("Haulage Trip", trip_name)
            
            # Check if trip has expenses
            if not trip.get("trip_expenses"):
                logger.debug(f"Trip {trip_name} has no expenses, skipping")
                continue
            
            # Check if journal entry already exists
            if trip.trip_journal_entry:
                logger.debug(f"Trip {trip_name} already has journal entry {trip.trip_journal_entry}, skipping")
                continue
            
            try:
                result = create_trip_expense_journal_entry(trip_name)
                success_entries.append(result["name"])
            except Exception as e:
                logger.warning(f"Failed to create journal entry for trip {trip_name}: {str(e)}")
                failed_entries.append({
                    "trip": trip_name,
                    "error": str(e)[:100]  # Truncate error message
                })
        
        except Exception as e:
            logger.error(f"Error processing trip {trip_name} in batch journal entry creation: {str(e)}")
            failed_entries.append({
                "trip": trip_name,
                "error": str(e)[:100]  # Truncate error message
            })
    
    return {
        "success": success_entries,
        "failed": failed_entries,
        "total_created": len(success_entries),
        "total_failed": len(failed_entries),
    }
