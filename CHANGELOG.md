# Changelog

## [0.1.30] — 2026-05-15

### Changed

- **Uninstall**: comprehensive `before_uninstall` / `after_uninstall` — removes workspace, pages, reports, print formats, Fleet Manager role, legacy DocTypes, and haulage ToDos; site stays clean after `uninstall-app`.

[0.1.30]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.30

## [0.1.29] — 2026-05-15

### Fixed

- **All Trips** page: fixed JavaScript crash (`flt` undefined on desk pages), load page scripts via `app_include_js`, sync Page docs on migrate, SQL fallback API, visible error messages.

[0.1.29]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.29

## [0.1.28] — 2026-05-15

### Fixed

- **All Trips** hub: unified list with status actions, financial columns, Open and Accounting buttons; fixed broken page container; restored legacy page redirects.
- Trip form: no duplicate action buttons on refresh; accounting mode persists after save.
- Shared `haulage_trip_hub.js` for list and form status/accounting navigation.

[0.1.28]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.28

## [0.1.27] — 2026-05-15

### Changed

- Code health: unified desk APIs in `trip_operations.py`, shared `haulage_i18n.status_badge`, legacy page cleanup on migrate, README architecture updated.

[0.1.27]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.27

## [0.1.25] — 2026-05-15

### Changed

- **Print formats**: two trip prints only — **Haulage Trip Operations** (shipments) and **Haulage Trip Summary** (status, revenue, expenses, custody, net). Removed duplicate Dispatch / Shipments Sheet formats.
- **Deduplication**: shared `trip_financials.py`; workspace trip card links only **All Trips** (removed parallel Haulage Trip list link).

[0.1.25]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.25

## [0.1.24] — 2026-05-15

### Changed

- Removed workspace **section 3 · Trip accounting**; operations and accounting merged under **section 2** via **All Trips** page (Operations list / Trip accounting toolbar).
- Legacy `trip-accounting` route redirects to the unified hub.

[0.1.24]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.24

## [0.1.23] — 2026-05-15

### Added

- **All Trips** page in workspace section 2 (list with status badges; next to **New Haulage Trip**).
- **Trip action buttons** on each trip: Start, Pause, Arrival, Cancel (replaces manual status dropdown).

### Changed

- `trip_status` is system-managed (hidden field); shipping requests and fleet status follow button actions.

[0.1.23]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.23

## [0.1.22] — 2026-05-15

### Fixed

- **Arabic translations**: trip/request/truck/driver statuses in list views, reports, trip accounting page, and form indicators; expanded `ar.csv`; workspace shortcut **Trip operations** link fixed.

[0.1.22]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.22

## [0.1.21] — 2026-05-15

### Removed

- **Operational Notes** field on **Haulage Trip** (operational form) and from dispatch print format.

[0.1.21]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.21

## [0.1.20] — 2026-05-15

### Fixed

- **Trip accounting** sheet: accounting fields hidden by default in DocType; reliable show/hide of expense and custody grids; mode survives save and reload; revenue summary HTML fix; invoice dialog uses API shipment list when grids are hidden.

### Changed

- **README**: full application concept, architecture, workflows, and structure (EN + AR overview).

[0.1.20]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.20

## [0.1.19] — 2026-05-15

### Fixed

- **Trip accounting**: list **Open sheet** opens the standard **Haulage Trip** form in accounting mode (reliable after uninstall/reinstall). Legacy `trip-accounting-entry` page redirects to the same form.
- Revenue summary HTML on the accounting form (closing tag fix).

### Changed

- **Workspace**: section **2 · Trip operations** (تشغيل رحلات الشحن) instead of **Trips**.
- **Reports**: default period to current month on open; net income highlighted (green/red); summary cards for totals on driver, trip, truck, and custody reports.

[0.1.19]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.19

## [0.1.18] — 2026-05-15

### Changed

- **Reports**: Unified **net income** = revenue − expenses − **custody** across driver, trip, and truck reports; **Custody** column added where relevant. Shared logic in `report_utils.py`.
- **Trip accounting** list API reuses the same financial SQL as reports.
- **Trip accounting entry**: revenue summary refreshes after save.
- **README** and app description updated for current workspace layout (operations vs accounting vs reports).

[0.1.18]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.18

## [0.1.17] — 2026-05-15

### Added

- **Haulage Trip Custody** child table on trips (custody type, amount, date, holder).
- **Trip accounting entry** page (`trip-accounting-entry`): separate sheet after choosing a trip from **Trip Accounting** list — expenses, custody, and revenue summary (operational trip form no longer shows accounting).
- **Haulage Custody Report**: filters for custody type, driver, from/to date; one row per custody line on trips.

### Changed

- **Trip Accounting** list shows custody column; net income = revenue − expenses − custody. **Open sheet** opens the dedicated entry page instead of the operational trip form.

[0.1.17]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.17

## [0.1.16] — 2026-05-15

### Added

- **Haulage Driver Report**, **Haulage Trip Report**, and **Haulage Truck Report**: each with optional **Driver** filter (all drivers when empty) and **From date** / **To date** period filters. Driver and truck reports aggregate trips; trip report lists one row per trip with revenue, expenses, and net income.

### Removed

- **Haulage Operations Summary** (replaced by the three reports above). `after_migrate` removes the legacy report record on existing sites.

### Changed

- **Haulage Logistics** workspace **Reports** section: three dedicated report shortcuts and link cards.

[0.1.16]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.16

## [0.1.15] — 2026-05-15

### Added

- **Haulage Custody Type** master data (custody name + ledger account), like expense types.
- **Trip Accounting** desk page: lists trips with revenue, expenses, and **net income**; opens the trip in accounting mode.
- Trip form **accounting mode**: revenue table per shipment, expense allocation, journal entry actions (via workspace or **Trip accounting** button on the operational form).

### Changed

- **Haulage Trip** operational form: removed **Trip execution** and **Expense allocation** sections (data kept; execution table hidden). Accounting sections shown only in accounting mode.
- **Haulage Logistics** workspace: **3 · Trip accounting** before **Reports**; **Haulage Custody Types** in master data.

[0.1.15]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.15

## [0.1.14] — 2026-05-15

### Changed

- **Truck**: Removed naming series; document name is **Truck Name** (required, unique). **License plate** is optional. **Photo** field (`Attach Image`) with list/form image display.
- **Driver**: Removed naming series; document name is **Full Name** (required, unique). **Photo** field added. **Driver status** no longer required (defaults to Active).
- **Links** (trips, reports, reminders): Truck and driver are selected and displayed by name, not `TRUCK-.####` / `DRV-.####` IDs.
- **Migrate**: `before_migrate` backfills `truck_name` from license plate; `after_migrate` renames legacy series document IDs to the name field when possible.

[0.1.14]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.14

## [0.1.13] — 2026-05-13

### Removed

- **Shipping Route** DocType and all desk links; trips no longer reference a shared route master.

### Changed

- **Shipping Request**: **Pickup location** and **Delivery location** (required text) replace **Shipping Route**; existing sites backfill from **Shipping Route** loading/delivery cities on migrate (`before_migrate`).
- **Haulage Trip**: **Shipping Route** field removed.
- **Haulage Trip Shipment**: **Pickup location** and **Delivery location** (read-only, from linked request) shown in the grid; server `validate` mirrors values from **Shipping Request** for print/API; client refreshes on link change.
- **Haulage Operations Summary** (Trip view): **Route** column replaced by **Shipment locations** (concatenated pickup → delivery per shipment line, in row order).
- **Print**: **Haulage Trip Dispatch** updated (shipments table with pickup/delivery); new **Haulage Trip Shipments Sheet** format; trip form adds **Print shipments sheet**.
- **Haulage Logistics** workspace: master data shortcuts/links no longer include Shipping Route.
- **Trip / trip shipment forms**: Field descriptions clarify that pickup and delivery on each trip line are loaded from the linked **Shipping Request** (Arabic strings in `ar.csv`).

[0.1.13]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.13

## [0.1.12] — 2026-05-13

### Removed

- **Shipment Preparation** DocType and desk flows that depended on it.

### Changed

- **Haulage Trip**: Validates linked **Shipping Request** documents directly and syncs request status from the trip lifecycle (no preparation records).
- **Haulage Trip Shipment**: Child rows reference **Shipping Request** only.
- **Shipping Request**: Removed the **Prepare shipment** client button.
- **Haulage Logistics** workspace: **Master data**, **1 · Shipping requests**, **2 · Trips**, **Reports**; standalone trip-expense and Sales Invoice shortcuts removed from the desk (billing and expenses remain on the trip form).
- **Arabic (`ar.csv`)** and **README** workflow text updated.

### Fixed

- **Install**: `before_migrate` clears legacy **Shipment Preparation** table rows when the old DocType still exists so **migrate** can drop the table cleanly.

[0.1.12]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.12

## [0.1.11] — 2026-05-14

### Changed

- **Truck**: Removed **Internal fleet ID** field; document name / naming series remains the primary identifier.
- **Truck status**: Replaced **Busy** with **Reserved for Trip** (Arabic: محجوزة لرحلة). Fleet auto-status from active trips now sets this value. `after_migrate` updates existing rows from `Busy` to `Reserved for Trip`.

[0.1.11]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.11

## [0.1.10] — 2026-05-14

### Changed

- **Haulage Operations Summary**: Added **Group by** filter (`Trip` / `Driver` / `Truck`). **Trip** shows each trip with revenue (agreed prices), expenses (trip lines), net income, and shipment count. **Driver** and **Truck** aggregate the same financials with trip count, total shipments, totals, and **average net per trip**.

[0.1.10]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.10

## [0.1.9] — 2026-05-14

### Changed

- **Workspace**: Numbered steps **5** (trip expenses shortcut → `Haulage Trip` list), **6** (revenue / Sales Invoices), **7** (reports). Removed the duplicate trip shortcut from the expenses row by using a distinct shortcut label **Trip expenses** (same list, for navigation clarity).
- **Reports**: Replaced **Trip Financial Summary**, **Driver Performance**, and **Truck Performance** with a single script report **Haulage Operations Summary** (`ref_doctype` `Haulage Trip`) with filters: **Trip**, **Driver**, **Truck**, **From date**, **To date** (combinable). Output is one row per trip with revenue, expenses, net income, and shipment count.
- **`after_migrate`**: Deletes legacy Report records for the three removed reports so desk links stay clean.

[0.1.9]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.9

## [0.1.7] — 2026-05-13

### Changed

- **Workspace**: Removed the bottom **Browse as cards** block so shortcuts are not doubled with link cards on the desk page.
- **Install**: `after_migrate` now **re-syncs** the Haulage Logistics workspace (content, shortcuts, links) from the app JSON so old duplicate shortcut rows are cleared on existing sites.
- **Arabic**: Expanded `ar.csv` (DocType names, roles, desk labels, status values, and common UI strings). File location is now **`haulage_mgmt/translations/ar.csv`** so Frappe loads translations with the app package; `setup.py` includes these CSV files in `package_data`.

### Fixed

- **Translations CSV**: Repaired quoting and removed duplicate source keys.

[0.1.7]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.7

## [0.1.6] — 2026-05-13

### Fixed

- **Haulage Trip**: Saving with status **Preparing** no longer resets linked preparation / shipping request from an in-progress state (e.g. after temporarily changing status). **Cancelled** still rolls preparation back to **Ready for Trip** as before.
- **Haulage Trip**: Shipment child rows must always specify a **shipping request** (no blank lines) when the trip is not cancelled.

[0.1.6]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.6

## [0.1.5] — 2026-05-13

### Changed

- **Workspace**: Removed the separate **Analytics** block; **script reports** live only under **8 · Reports**. Reordered shortcuts and link cards to match the operational flow (master data → requests → preparation → trips → ERPNext revenue → reports → settings). Added **Customer**, **New Shipment Preparation**, and **Sales Invoices** shortcuts; link cards are **Master data**, **Shipping & preparation**, **Trips & billing**, **Reports & configuration**.
- **Truck**: Optional **Internal fleet ID** field (alongside naming series / document name).
- **Haulage Trip**: Clearer section labels for execution and expense allocation; **Company** default uses the first `Company` when the user has no default (same pattern as install).
- **Arabic (`ar.csv`)**: New strings for workspace headers and the new labels.

[0.1.5]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.5

## [0.1.4] — 2026-05-13

### Changed

- **Workspace desk UX**: EditorJS `content` with section headers, **shortcut tiles** for every main DocType/report/settings (including **New** forms), and **link cards** (Operations, Fleet & master data, Reports, Configuration). `indicator_color` on workspace; `truck` icon for sidebar/app list.

[0.1.4]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.4

## [0.1.3] — 2026-05-13

### Fixed

- **Workspace 404 (`fleet-haulage`)**: Desk routes slug the workspace **name** (`Haulage Logistics` → `haulage-logistics`), but **title** was `Fleet Haulage` (`fleet-haulage`), so links broke. **Title** now matches **name**; `after_migrate` corrects existing sites and clears a wrong **parent_page** so the item is not nested under another workspace (e.g. Integrations).
- **App launcher**: `add_to_apps_screen` + `app_logo_url` / `app_icon` so **Haulage Management** appears as its own app tile with route `/desk/haulage-logistics` (run `bench build --app haulage_mgmt` after pull).

[0.1.3]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.3

## [0.1.2] — 2026-05-13

### Fixed

- **Bench `get-app` from Git URL:** moved `setup.py`, `MANIFEST.in`, `requirements.txt`, `license.txt`, and `translations/` to the **repository root** so Bench finds `apps/<repo>/setup.py` (fixes `FileNotFoundError: .../newapp/setup.py` when cloning `newapp`).

[0.1.2]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.2

## [0.1.1] — 2026-05-13

### Added

- **`translations/ar.csv`**: Arabic translations (Frappe CSV pattern).
- **`before_uninstall`**: removes **Fleet Manager** role and related **Has Role** rows on site uninstall.

### Changed

- **UI source language English** across DocTypes, workspace, print format, script reports, Python `_("…")`, and client `__(…)`.
- **`MANIFEST.in`**: include `translations/*.csv` for packaging.
- **Company fallback**: first `Company` via `get_all` in `install.py` and Sales Invoice API (replaces empty `get_value` filters).
- **Docs**: monorepo `get-app` path, `bench uninstall-app` / `bench remove-app`, ERPNext prerequisite.

[0.1.1]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.1

## [0.1.0] — 2026-05-13

### Added

- Initial `haulage_mgmt` app for the **Haulage Logistics** module on ERPNext.
- DocTypes: trucks, drivers, shipping routes, expense types, shipping requests, shipment preparation, trips with child tables (shipments, events, expenses).
- Customer link via `Customer`, and Sales Invoice shortcuts from shipping request and trip.
- Reports: trip financial summary, driver performance, truck performance.
- **Haulage Trip Dispatch** print format linked for trips.
- Logistics settings: default freight Item, credit account for trip expense journal.
- Draft Journal Entry from trip expenses, linked on the trip.
- Desk workspace and **Customer** dashboard extension for shipping requests.
- Sync of preparation/request status and truck status (busy/available) with trips.
- Daily scheduled task for fleet document reminders (ToDo).
- **Fleet Manager** role and permissions on relevant DocTypes.

[0.1.0]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.0
