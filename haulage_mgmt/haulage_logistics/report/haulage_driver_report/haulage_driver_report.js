frappe.query_reports["Haulage Driver Report"] = {
	onload(report) {
		haulage_mgmt.report_common.default_period_filters(report);
	},
	formatter: haulage_mgmt.report_common.report_formatter,
};
