# Data Model Review — tables in code vs ERD (Week 13, 27.11.2026)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Source of truth:** `backend/shop/models.py` at commit `6c4cad2` (27.11, 11:00) — every table and column below was read from the Django models, not from the diagram.
**Result:** 15 tables in the database (ERD v3 showed 13). ERD v3.1 now matches the code column by column. 7 legacy columns and 5 structural issues found (one of them a 1NF violation added this morning); 3 need a decision this week.

## 1. Table-by-table check

| Table (db_table) | In ERD v3? | Matches code? | What differs / finding | Verdict |
|---|---|---|---|---|
| `customers` | yes | yes | `email` is UNIQUE — the whole login / "my orders" / reviews logic keys on it. OK. | OK |
| `addresses` | yes | **no** | Code has `full_address`, `apartment`, `entrance`, `floor`, `intercom_code`, `within_city`, `is_saved`, `is_default` **and** the old `street`, `building` (both empty, nothing reads them). Two flags `is_saved` / `is_default` overlap: "saved for next time" vs "default". | legacy: drop `street`, `building`; decide one flag |
| `categories` | yes | yes | `category_name` UNIQUE — correct, this is why "Fantasy"/"fantasy" can no longer be two genres. | OK |
| `products` | yes | **no** | `publication_year`, `page_count`, `edition_info` added; **`available_languages` is a JSON list in one cell** (`["ru","en"]`) — a repeating group, not 1NF: cannot filter "books in Kazakh" with an index or a FK to a languages table; `genre` still present **and still required by the admin form** although `category_id` is NOT NULL since DEF-01. Two columns for one fact = not 3NF. | legacy: drop `genre` |
| `orders` | yes | **no** | `public_code` UUID UNIQUE added (DEF-05 fix: order opened by secret code, not by number). `address_id` is **nullable** in the DB while the API requires an address — the rule lives only in the serializer. `delivery_method` has a single choice `delivery`. | add NOT NULL on `address_id`; keep `delivery_method` only if pickup is planned |
| `order_items` | yes | yes | CHECK `quantity >= 1`; `unit_price` is the deliberate copy (price at purchase). | OK |
| `payments` | yes | yes | `status` success/failed/refunded, `refund_reason`, `refunded_at`. `transaction_id` UNIQUE = BR-04. | OK |
| `shop_employee` (EMPLOYEES) | yes | **no** | Linked 1:1 to Django `auth_user`, **but still stores its own `login`, `full_name`, `password_hash`** — a second copy of the user, and a second password hash nobody maintains. Only `role`, `is_active`, `user_id` are used. | drop `login`, `full_name`, `password_hash` |
| `stock_log` | yes | **no** | `employee_id` FK is used; old `changed_by` text still written in parallel (both filled on every row). | legacy: drop `changed_by` after a last check that nothing reads it |
| `stock_requests` | yes | **no** | `notified_at`, `is_read` added — the waiting list doubles as the notification inbox. Acceptable for one notification type; a separate NOTIFICATIONS table only if more types appear. UNIQUE(customer, product) = FR-07. | OK, noted |
| `reviews` | yes | yes | CHECK rating 1–5, UNIQUE(customer, product). | OK |
| `support_tickets` | yes | **no** | Code: `topic` (refund/delivery/other), `status` open/in_progress/closed, `employee_id` (handled by), `staff_reply`, `replied_at`, `closed_at`. My v4 proposal had `subject` and a `refund_requested` status — the team chose `topic = refund` instead; simpler and enough. Requirement FR-14 updated to the built version. | OK, FR-14 text updated |
| `shop_store_reviews` (SHOP_FEEDBACK in v4) | yes (as SHOP_FEEDBACK) | name differs | Same content as planned: one per customer, rating 1–5. No `contact_email` — a shop review needs login; fine. **Table names are inconsistent**: `shop_store_reviews` and `shop_employee` carry the Django prefix, the other 12 tables do not. | rename to `store_reviews`, `employees` |
| `wishlist_items` | **no** | — | New table, UNIQUE(customer, product) — exactly FR-18. Added to ERD v3.1. | OK |
| `customer_favorite_categories` | **no** | — | New this morning (Karakat, "For you"): M:N customer ↔ category, done correctly as a separate table (not a list in CUSTOMERS). Added to ERD v3.1. | OK |
| `stock_requests` ↔ `wishlist_items` | — | — | Separate, no link (FR-18 crit. 3 not built). Decision at the stand-up: keep separate (my proposal). | decision |

Relationships: all FKs on the ERD exist in code; the two M:N relations (wishlist, favourite categories) are proper junction tables with PROTECT / RESTRICT where history must survive (orders, payments, stock_log, tickets) and CASCADE only for wishlist and stock_requests — matches BR-05.

## 2. Findings summary

| # | Finding | Why it matters | Owner | Proposed fix | Priority |
|---|---|---|---|---|---|
| T-1 | **7 legacy columns**: `products.genre`, `stock_log.changed_by`, `addresses.street`, `addresses.building`, `shop_employee.login`, `.full_name`, `.password_hash` | Two places for one fact → they drift (genre already differs from category for test data). `password_hash` is a dead credential store. Not 3NF. | Sabina (migration), Moldyr (employee) | one clean-up migration `0020_drop_legacy_columns`; remove `genre` from the admin form first | this week — blocks DEF-03 fix (the admin form test posts `genre`) |
| T-2 | `orders.address_id` nullable in DB | An order without address can be inserted from admin or a script; FR-05 crit. 2 is enforced only in the API | Sabina | `null=False` + migration (all existing orders have an address) | this week |
| T-3 | Inconsistent table names `shop_employee`, `shop_store_reviews` | Reports and SQL written by hand (R-02, R-03) break on the prefix; the ERD and the DB must use one naming | Sabina | `db_table = "employees"`, `"store_reviews"` | next week |
| T-4 | `addresses.is_saved` vs `is_default` | Two booleans, no rule which wins; "saved" is already implied by the row existing | Sabina, Karakat | keep `is_default` only, or document: `is_saved` = show in the list, `is_default` = pre-select | decision |
| T-5 | `orders.delivery_method` with one value | Dead column unless pickup is planned (NFR / future) | team | keep if pickup is in the final scope, otherwise drop | decision |
| T-6 | `products.available_languages` JSONField (list of codes) | Repeating group in one column = 1NF violation; no FK, no index, no filter "show books in Kazakh"; the same mistake was fixed for `genre` → CATEGORIES two weeks ago | Sabina | table `PRODUCT_LANGUAGES (product_id FK, language_code)` or a `LANGUAGES` lookup + M:N, like `customer_favorite_categories` | next week |

## 3. Normalization statement for ERD v3.1

- 1NF: every column atomic **except** `products.available_languages` (T-6) — a list in a cell; the only 1NF break in the schema.
- 2NF: all tables have a single-column PK, so no partial dependencies.
- 3NF: every non-key column depends only on the key, **except** the 7 legacy columns in T-1 (`genre` depends on `category_id`, `changed_by` / `login` / `full_name` depend on `employee_id → user_id`). After migration `0020` the schema is in 3NF; the only deliberate copy stays `order_items.unit_price`.

## 4. What changed in the requirements because of this review

- FR-14: statuses `open / in_progress / closed`, topic `refund / delivery / other`, fields `staff_reply`, `replied_at` — as built; "support requests refund" is expressed by `topic = refund`.
- FR-17 crit. 5 rewritten: the order page is opened by `public_code` (UUID), never by number; a guessed code → 404. Accepted (AT-19b).
- FR-18 crit. 3 removed (wishlist and waiting list stay separate) — pending team confirmation.
- New non-functional rule NFR-02: a column replaced by another column is dropped in the same or the next sprint, never kept "just in case".
