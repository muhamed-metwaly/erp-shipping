frappe.provide("haulage_mgmt.report_common");

haulage_mgmt.report_common.default_period_filters = function (report) {
	const today = frappe.datetime.get_today();
	const month_start = frappe.datetime.month_start(today);
	if (!report.get_filter_value("from_date")) {
		report.set_filter_value("from_date", month_start);
	}
	if (!report.get_filter_value("to_date")) {
		report.set_filter_value("to_date", today);
	}
};

haulage_mgmt.report_common.STATUS_COLUMNS = ["trip_status", "request_status", "truck_status", "driver_status"];

haulage_mgmt.report_common.net_income_formatter = function (
	value,
	row,
	column,
	data,
	default_formatter,
) {
	const formatted = default_formatter(value, row, column, data);
	if (column.fieldname === "net_income" && data && flt(data.net_income) < 0) {
		return `<span class="text-danger">${formatted}</span>`;
	}
	if (column.fieldname === "net_income" && data && flt(data.net_income) > 0) {
		return `<span class="text-success">${formatted}</span>`;
	}
	return formatted;
};

haulage_mgmt.report_common.report_formatter = function (
	value,
	row,
	column,
	data,
	default_formatter,
) {
	if (haulage_mgmt.report_common.STATUS_COLUMNS.includes(column.fieldname) && value) {
		return __(value);
	}
	return haulage_mgmt.report_common.net_income_formatter(
		value,
		row,
		column,
		data,
		default_formatter,
	);
};
