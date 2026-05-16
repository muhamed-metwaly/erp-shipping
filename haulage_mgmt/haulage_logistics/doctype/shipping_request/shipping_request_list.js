frappe.listview_settings["Shipping Request"] = {
	get_indicator(doc) {
		const colors = {
			New: "blue",
			"Goods Prepared": "orange",
			"Out for Delivery": "purple",
			Delivered: "green",
			Cancelled: "red",
		};
		const status = doc.request_status || "";
		return [__(status), colors[status] || "grey", `request_status,=,${status}`];
	},
	formatters: {
		request_status(value) {
			return __(value);
		},
	},
};
