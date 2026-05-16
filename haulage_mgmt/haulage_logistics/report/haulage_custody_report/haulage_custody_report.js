frappe.query_reports["Haulage Custody Report"] = {
	onload(report) {
		haulage_mgmt.report_common.default_period_filters(report);
	},
	formatter: haulage_mgmt.report_common.report_formatter,
};
