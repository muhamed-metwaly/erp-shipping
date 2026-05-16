"""Backward-compatible imports — use trip_operations hub API."""

from haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations import (  # noqa: F401
    get_all_trips_hub,
    get_trip_accounting_detail,
    get_trip_accounting_list,
    get_trip_operations_list,
)
