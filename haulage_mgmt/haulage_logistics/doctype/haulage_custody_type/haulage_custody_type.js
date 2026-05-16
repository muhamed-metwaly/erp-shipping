frappe.ui.form.on("Haulage Custody Type", {
	refresh(frm) {
		if (frm.doc.account) {
			frm.add_custom_button(
				__("Open Account"),
				() => frappe.set_route("Form", "Account", frm.doc.account),
				__("ERPNext"),
			);
		}
	},
});
