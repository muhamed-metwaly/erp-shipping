"""
Trip status transitions driven by action buttons (not manual select).

Implements a state machine for trip statuses with validation rules
and optional event logging.
"""
from typing import Dict, Any
import logging

import frappe
from frappe import _
from frappe.utils import now_datetime

logger = logging.getLogger(__name__)

# State machine definition for trip status transitions
TRIP_STATUS_ACTIONS: Dict[str, Dict[str, Any]] = {
    "start": {
        "label": _("Start trip"),
        "event": "Start",
        "from": ("Preparing", "Paused"),
        "to": "Started",
        "set_departure": True,
    },
    "pause": {
        "label": _("Pause trip"),
        "event": "Pause",
        "from": ("Started",),
        "to": "Paused",
    },
    "resume": {
        "label": _("Resume trip"),
        "event": "Resume",
        "from": ("Paused",),
        "to": "Started",
    },
    "arrive": {
        "label": _("Trip arrival"),
        "event": "Arrival",
        "from": ("Started", "Paused"),
        "to": "Completed",
    },
    "cancel": {
        "label": _("Cancel trip"),
        "event": None,
        "from": ("Preparing", "Started", "Paused"),
        "to": "Cancelled",
    },
}

# Valid trip statuses
VALID_TRIP_STATUSES = ("Preparing", "Paused", "Started", "Completed", "Cancelled")


def apply_trip_status_action(trip: Any, action: str) -> str:
    """
    Update trip status and optional event log based on action.
    
    Implements state machine validation:
    - Validates action is known
    - Checks current status allows this action
    - Transitions to new status
    - Optionally logs event and sets timestamps
    
    Args:
        trip: The Haulage Trip document instance
        action: The action to perform (start, pause, arrive, cancel)
        
    Returns:
        The new trip status
        
    Raises:
        frappe.ValidationError: If action is invalid or status transition not allowed
        
    Note:
        Caller must save the document after calling this function.
    """
    action = (action or "").strip().lower()
    
    # Validate action exists
    rules = TRIP_STATUS_ACTIONS.get(action)
    if not rules:
        msg = _("Unknown trip action: {0}. Valid actions: {1}").format(
            action, ", ".join(TRIP_STATUS_ACTIONS.keys())
        )
        logger.error(f"Invalid action on trip {trip.name}: {action}")
        frappe.throw(msg, title=_("Invalid Action"))

    # Get current status
    current = trip.trip_status or "Preparing"
    
    # Validate status transition
    if current not in rules["from"]:
        allowed_statuses = ", ".join(_(s) for s in rules["from"])
        msg = _("Cannot perform action '{label}' on trip in status '{current}'. Allowed statuses: {allowed}").format(
            label=rules["label"],
            current=_(current),
            allowed=allowed_statuses
        )
        logger.warning(f"Invalid status transition on trip {trip.name}: {current} -> {action}")
        frappe.throw(msg, title=_("Invalid Status"))

    # Perform status transition
    new_status = rules["to"]
    trip.trip_status = new_status
    logger.info(f"Trip {trip.name} status transition: {current} -> {new_status} (action={action})")
    
    # Set departure time if starting
    if rules.get("set_departure") and not trip.departure_date:
        trip.departure_date = now_datetime()
        logger.debug(f"Trip {trip.name} departure date set to {trip.departure_date}")

    # Log event if configured
    event_type = rules.get("event")
    if event_type and frappe.get_meta("Haulage Trip").has_field("trip_events"):
        trip.append(
            "trip_events",
            {
                "event_type": event_type,
                "event_datetime": now_datetime()
            },
        )
        logger.debug(f"Trip {trip.name} event logged: {event_type}")

    return trip.trip_status
