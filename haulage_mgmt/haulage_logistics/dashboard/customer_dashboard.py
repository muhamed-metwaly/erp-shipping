from frappe import _


def get_dashboard_data(data=None, **kwargs):
    """Append Shipping Request to the Customer dashboard."""
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return data
    transactions = data.setdefault("transactions", [])
    transactions.append({"label": _("Fleet & Haulage"), "items": ["Shipping Request"]})
    return data
