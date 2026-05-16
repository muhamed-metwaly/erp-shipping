frappe.listview_settings["Haulage Trip"] = {
	get_indicator(doc) {
		const colors = haulage_mgmt.i18n ? haulage_mgmt.i18n.trip_status_colors : {
			Preparing: "orange",
			Started: "blue",
			Paused: "yellow",
			Completed: "green",
			Cancelled: "red",
		};
		const status = doc.trip_status || "";
		return [__(status), colors[status] || "grey", `trip_status,=,${status}`];
	},
	formatters: {
		trip_status(value) {
			return __(value);
		},
	},
	onload(list_view) {
		// Add batch operations button
		list_view.page.add_menu_item(
			__("Batch Operations"),
			function() {
				const selected = list_view.get_checked_items();
				if (!selected || selected.length === 0) {
					frappe.show_alert({
						message: __("Please select at least one trip"),
						indicator: "red"
					});
					return;
				}

				const trip_ids = selected.map(item => item.name);
				
				// Show dialog with batch operation options
				frappe.call({
					method: "haulage_mgmt.haulage_logistics.api.create_batch_sales_invoices",
					args: {
						trip_ids: trip_ids
					},
					freeze: true,
					freeze_message: __("Creating invoices..."),
					callback: function(r) {
						if (r.exc) { return; }
						if (r.message) {
							const result = r.message;
							let msg = __("Batch Operations Complete:\n");
							msg += __("✓ {0} invoices created", [result.total_created]) + "\n";
							if (result.total_failed > 0) {
								msg += __("✗ {0} failed", [result.total_failed]) + "\n";
								result.failed.forEach(f => {
									msg += `  - ${frappe.utils.escape_html(f.trip)}: ${frappe.utils.escape_html(f.error)}\n`;
								});
							}
							frappe.show_alert({
								message: msg,
								indicator: result.total_failed === 0 ? "green" : "orange"
							});
							list_view.refresh();
						}
					}
				});
			);
		// Add button for batch journal entries
		list_view.page.add_menu_item(
			__("Batch Journal Entries"),
			function() {
				const selected = list_view.get_checked_items();
				if (!selected || selected.length === 0) {
					frappe.show_alert({
						message: __("Please select at least one trip"),
						indicator: "red"
					});
					return;
				}

				const trip_ids = selected.map(item => item.name);
				
				frappe.call({
					method: "haulage_mgmt.haulage_logistics.api.create_batch_journal_entries",
					args: {
						trip_ids: trip_ids
					},
					freeze: true,
					freeze_message: __("Creating journal entries..."),
					callback: function(r) {
						if (r.exc) { return; }
						if (r.message) {
							const result = r.message;
							let msg = __("Batch Operations Complete:\n");
							msg += __("✓ {0} journal entries created", [result.total_created]) + "\n";
							if (result.total_failed > 0) {
								msg += __("✗ {0} failed", [result.total_failed]) + "\n";
								result.failed.forEach(f => {
									msg += `  - ${frappe.utils.escape_html(f.trip)}: ${frappe.utils.escape_html(f.error)}\n`;
								});
							}
							frappe.show_alert({
								message: msg,
								indicator: result.total_failed === 0 ? "green" : "orange"
							});
							list_view.refresh();
						}
					}
				});
			);
	},
};
