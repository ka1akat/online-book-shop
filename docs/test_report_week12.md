# Test Report — Week 12 (20.11.2026)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Tested build:** `main` at commit `d0a2f8d` (20.11.2026, 11:40) — includes this week's work of all four teammates: category required (DEF-01), "Notify me" + waiting list + notifications (DEF-02 / FR-07+), book page with description (FR-12), shop reviews (FR-13), support tickets (FR-14), `seed_employees` (FR-15), reports API (FR-16), "My orders" (FR-17), wishlist (FR-18).
**Previous reports:** `acceptance_tests.md` (13.11, 11 / 13).
**How it was run:** 27 acceptance scenarios against the backend API on a fresh `seed_books` + `seed_employees` database; the race scenario (AT-13) on PostgreSQL. Main scenario also checked manually on the website.

## 1. Summary

| | Week 11 (13.11) | Week 12 (20.11) |
|---|---|---|
| Scenarios | 13 | **27** (16 for FR-01–11, 11 new for FR-12–18) |
| PASS | 11 | **24** |
| Open | 2 | **3** (2 defects + 1 criterion to agree) |
| Previous defects DEF-01, DEF-02 | open | **closed** (AT-04, AT-07 pass) |
| Team unit tests | 56 OK | **35 of 92 fail** → DEF-03 |
| Core process (reserve → pay → stock −1, race, refund, roles) | PASS | PASS |

Status: **On Track** — both defects from last week are fixed, 7 of 8 new functions accepted; three new findings, all with owner and date, none in the core process.

## 2. Results — existing requirements (FR-01 – FR-11)

| ID | Requirement | Scenario | Result | Change vs 13.11 |
|---|---|---|---|---|
| AT-01 | FR-02, BR-01 | Order → pay → stock 25 → 24, STOCK_LOG `sale`, PAYMENTS `success` | **PASS** | = |
| AT-02 | FR-01, FR-03 | Order for a book with stock 0 → 409 | **PASS** | = |
| AT-03 | FR-08 | Expired reservation → 409, order `cancelled`, stock unchanged | **PASS** | = |
| AT-04 | FR-04 crit. 1 | Book without category → **400, not saved** | **PASS** | **FAIL → PASS (DEF-01 closed)** |
| AT-04b | FR-04 crit. 3 | Category filter | **PASS** | = |
| AT-05 | FR-05 | Delivery order without address → 400 | **PASS** | = |
| AT-05b | FR-10 | Delivery fee +1000 / +1500 | **PASS** | = |
| AT-06 | FR-06 | `finance` → 403 on stock report and stock change | **PASS** | = |
| AT-06b | FR-06 | `warehouse` stock change logged with employee_id | **PASS** | = |
| AT-07 | FR-07 crit. 1–2 | "Notify me" on out-of-stock book → 201; twice → one row; in-stock book → 400 | **PASS** | **FAIL → PASS (DEF-02 closed)** |
| AT-08 | FR-09 | Refund: refunded / cancelled / stock +1 / log; second refund rejected | **PASS** | = |
| AT-09 | FR-11 | One review per customer; rating 1–5; login required | **PASS** | = |
| AT-10 | FR-11 | Price filter | **PASS** | = |
| AT-11 | FR-09 crit. 5 | `support` cannot refund in admin → 403 | **PASS** | = |
| AT-12 | FR-11 crit. 5 | `min_rating` filter | **PASS** | = |
| AT-13 | BR-03, BR-04 | Two buyers for the last copy; double click on Pay — PostgreSQL | **PASS\*** | \* only after a one-line fix in the test (see DEF-03) |

## 3. Results — new functions (FR-12 – FR-18, week 12)

| ID | Requirement | Scenario | Actual | Result |
|---|---|---|---|---|
| AT-14 | FR-12 book page | `GET /api/products/P-1004/` returns description, category name, rating, year; all seed books have a description; unknown id → 404 | description present, category "Fiction", year 1949; P-9999 → 404 | **PASS** |
| AT-15 | FR-13 shop review | login required; one per customer (second updates); rating 6 → 400; not mixed into book reviews | 201 / 200 / 1 row / 400 / 401; absent from book reviews | **PASS** |
| AT-16 | FR-14 ticket | ticket on own order → 201 `open`; on another customer's order → rejected; anonymous without email → 400 | 201 / 404 / 400 | **PASS** |
| AT-16b | FR-14 roles | `support` opens Support tickets in admin, cannot open Payments | 200 / 403 | **PASS** |
| AT-17 | FR-15 demo employees | `seed_employees` twice → exactly 5, one per role; `demo_warehouse` logs in, cannot open Customers | 5 rows, roles admin/finance/manager/support/warehouse; 200 / 403 | **PASS** |
| AT-18 | FR-16 reports | `demo_manager` opens `/api/reports/demand/` and `/api/reports/monthly-sales/` | **403 for manager, admin and everyone** | **FAIL → DEF-04** |
| AT-19 | FR-17 my orders | login required; returns only own orders | 401 anonymous; `[6]` = own order only | **PASS** |
| AT-19b | FR-17 crit. 5 | another customer's order must not be readable by id | **`GET /api/orders/6/` → 200 for another customer and for anonymous — address and items visible** | **FAIL → DEF-05** |
| AT-20 | FR-18 wishlist | login required; add twice → one row; per customer; remove | 401 / 201 / 200 / own list only / 204 | **PASS** |
| AT-20b | FR-18 crit. 3 | out-of-stock book in wishlist also joins the waiting list | not implemented — wishlist and waiting list are separate | **OPEN — criterion to agree** |
| AT-21 | FR-07+ waiting list | `warehouse` restocks a waited book in admin → request `notified = true`, customer gets a notification | stock 0 → 5, notified = true, 1 notification | **PASS** |

## 4. Defect log

| ID | Status | What is wrong | Why it matters | Owner | Fix | Deadline |
|---|---|---|---|---|---|---|
| DEF-01 | **closed 20.11** | book without category | — | Sabina | migration 0011 | — |
| DEF-02 | **closed 20.11** | no "Notify me" | — | Karakat | `POST /api/products/<id>/notify/` + button | — |
| **DEF-03** | open | Making `category` NOT NULL (DEF-01 fix) broke the team's own tests: **35 of 92 fail** (`NOT NULL constraint failed: products.category_id`) because old tests create products without a category; `test_concurrency` fails the same way on PostgreSQL. One more test fails on addresses (401 ≠ 200). | The suite is red, so nobody can see a real regression; the race-condition protection is currently **not verified by any passing test**. The feature branches were merged without running the full suite. | Sabina (tests that create Product), Ayaulym (concurrency + address test) | add `category=` to every `Product.objects.create(...)` in tests (a shared fixture); run `python manage.py test shop` before merging; race tests on PostgreSQL | 22.11 |
| **DEF-04** | open | `/api/reports/demand/` and `/api/reports/monthly-sales/` return 403 to **everyone**, including manager and admin: the views have `permission_classes` but no `authentication_classes`, and the project default is "no authentication", so `request.user` is always anonymous. `LowStockView` sets `authentication_classes = [SessionAuthentication, BasicAuthentication]` and works. | FR-16 cannot be shown; both reports are dead code | Sabina | copy `authentication_classes` from `LowStockView` to both report views (2 lines) + a test "manager gets 200" | 22.11 |
| **DEF-05** | open | `GET /api/orders/<id>/` is open by id: any customer (or anonymous) can read any order — items, total, delivery address of another person. "My orders" (FR-17) itself is correct; the old detail endpoint was not closed. | Personal data leak; it was flagged in requirements v4 (FR-17 crit. 5, risk table) and is still open | Karakat, Moldyr | if a token is present, allow only the owner; otherwise require the order's email (like `support_view`); 403/404 for others | 27.11 |

## 5. Decisions needed from the team

| Topic | Question | My proposal |
|---|---|---|
| FR-18 crit. 3 (wishlist ↔ waiting list) | Should adding an out-of-stock book to the wishlist also create a "Notify me" request? Karakat built them as separate lists. | Keep separate for now, show a "Notify me" button inside the wishlist for out-of-stock items; drop crit. 3 from FR-18 — decision at the stand-up. |
| Old fields `genre`, `changed_by`, `street`, `building` | Still in the model (and `genre` is still required by the admin form). | Drop in one clean-up migration after DEF-03, then ERD v3.1. |

## 6. Next step (Aidana, by 27.11.2026)

1. Re-test DEF-03, DEF-04, DEF-05 → target 27 / 27.
2. Confirm FR-18 crit. 3 decision and update requirements v4.
3. ERD v3.1: add WISHLIST_ITEMS and the notification fields of STOCK_REQUESTS (`notified_at`, `is_read`), remove the dropped fields.
4. Manual walk-through on the website of the four functions shown at the check: book page, ticket from "My orders", `demo_support` closing the ticket, wishlist.
