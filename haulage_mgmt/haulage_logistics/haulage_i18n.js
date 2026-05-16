frappe.provide("haulage_mgmt");
frappe.provide("haulage_mgmt.i18n");

/** Translate stored English status / enum values for display (DB value unchanged). */
haulage_mgmt.i18n.status = function (value) {
	return value ? __(value) : "";
};

haulage_mgmt.i18n.trip_statuses = ["Preparing", "Started", "Paused", "Completed", "Cancelled"];

haulage_mgmt.i18n.trip_status_filter_options = function () {
	return "\n" + haulage_mgmt.i18n.trip_statuses.join("\n");
};

haulage_mgmt.i18n.trip_status_colors = {
	Preparing: "orange",
	Started: "blue",
	Paused: "yellow",
	Completed: "green",
	Cancelled: "red",
};

/** HTML indicator pill for list pages. */
haulage_mgmt.i18n.status_badge = function (status) {
	const color = haulage_mgmt.i18n.trip_status_colors[status] || "grey";
	const label = haulage_mgmt.i18n.status(status);
	return `<span class="indicator-pill ${color} filterable ellipsis">${frappe.utils.escape_html(
		label,
	)}</span>`;
};
