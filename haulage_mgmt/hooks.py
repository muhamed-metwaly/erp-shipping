app_name = "haulage_mgmt"
app_title = "Haulage Management"
app_publisher = "Haulage Mgmt"
app_description = (
    "Fleet haulage: master data, shipping requests, trips, trip accounting, custody, and ERPNext billing."
)
app_email = ""
app_license = "MIT"
app_version = "0.1.30"
app_icon = "truck"
app_logo_url = "/assets/haulage_mgmt/images/haulage-desk.svg"

required_apps = ["erpnext"]

app_include_js = [
    "haulage_mgmt/haulage_logistics/haulage_i18n.js",
    "haulage_mgmt/haulage_logistics/haulage_trip_hub.js",
    "haulage_mgmt/haulage_logistics/report/report_common.js",
    # Desk pages (always register routes; avoids missing page bundles on site)
    "haulage_mgmt/haulage_logistics/page/trip_operations/trip_operations.js",
    "haulage_mgmt/haulage_logistics/page/trip_accounting/trip_accounting.js",
    "haulage_mgmt/haulage_logistics/page/trip_accounting_entry/trip_accounting_entry.js",
]

add_to_apps_screen = [
    {
        "name": "haulage_mgmt",
        "logo": app_logo_url,
        "title": "Haulage Management",
        "has_permission": "haulage_mgmt.boot.check_haulage_app_permission",
    }
]

after_install = "haulage_mgmt.install.after_install"
before_migrate = "haulage_mgmt.install.before_migrate"
after_migrate = "haulage_mgmt.install.after_migrate"
before_uninstall = "haulage_mgmt.install.before_uninstall"
after_uninstall = "haulage_mgmt.install.after_uninstall"

override_doctype_dashboards = {
    "Customer": "haulage_mgmt.haulage_logistics.dashboard.customer_dashboard.get_dashboard_data",
}

scheduler_events = {
    "daily": [
        "haulage_mgmt.haulage_logistics.tasks.send_fleet_expiry_reminders",
    ],
}

doc_events = {
    "Haulage Trip": {
        "on_update": "haulage_mgmt.haulage_logistics.doctype.haulage_trip.haulage_trip.on_trip_update",
    },
}

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["name", "in", [
                "Delivery Note-custom_shipping_request",
            ]]
        ],
    },
]
