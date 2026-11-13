# Online Book Shop — Requirements v3 (Week 11)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Date:** 13.11.2026
**Replaces:** requirements_v2.md (06.11.2026)
**Based on:** acceptance testing of build `f9b0ebc` (see `docs/acceptance_tests.md`), Week 10 feedback ("new requirements 3 / STOCK_LOG roles / pass or fail / report")

---

## 1. What changed since v2

| # | Change | Why |
|---|--------|-----|
| C-6 | **3 new requirements** FR-09 (refund), FR-10 (delivery fee), FR-11 (reviews, ratings and catalog filters) | These features were built this week by Moldyr and Karakat without a written requirement. Now they have acceptance criteria and were tested (AT-05b, AT-08, AT-09, AT-10 — all pass). |
| C-7 | **FR-06 rewritten with the real roles** `warehouse / finance / support / manager / admin` and the exact access matrix (§4) | v2 named a role `inventory_manager` that was never implemented; the matrix now matches `admin.py` and `permissions.py`. |
| C-8 | **FR-08 criteria corrected** | Testing showed that stock is not reduced at reservation, so nothing is "returned" on expiry and no scheduled job is needed. |
| C-9 | FR-04 and FR-07 marked **not accepted yet** (defects DEF-01, DEF-02) | Book can be saved without category; "Notify me" has no endpoint and no button. |
| C-10 | New table **REVIEWS** added to the data model (ERD v3 pending) | one review per customer per book, rating 1–5. |

---

## 2. Functional requirements

Status: ACCEPTED (acceptance test passed) / NOT ACCEPTED (defect open) / NOT TESTED yet

| ID | Requirement | Owner | Acceptance criteria | Status |
|----|-------------|-------|---------------------|--------|
| FR-01 | The system blocks adding a book with `stock_quantity = 0` to the cart | Karakat | "Add to cart" on a book with stock 0 → nothing added, "Out of stock" shown | ACCEPTED — AT-02 |
| FR-02 | When an order is paid, stock is reduced by the ordered quantity **in the same transaction** as the payment and the STOCK_LOG row | Sabina, Ayaulym | After payment of 1 copy: stock −1, STOCK_LOG `sale −1`, PAYMENTS `success`; if the bank declines, stock unchanged and PAYMENTS `failed` row saved | ACCEPTED — AT-01 |
| FR-03 | A book with stock 0 is shown with "Out of stock"; the button is disabled | Karakat | Catalog shows the label; button disabled | ACCEPTED — AT-02 |
| FR-04 | Every book belongs to exactly one category from CATEGORIES; the catalog can be filtered by category | Sabina (DB), Karakat (UI) | 1) A book **cannot** be saved without a category (NOT NULL + required in API). 2) Category list on the site comes from the table. 3) Filter by category returns only that category's books. 4) Renaming a category changes it for all its books | NOT ACCEPTED — crit. 1 fails (DEF-01); crit. 3 ACCEPTED — AT-04b |
| FR-05 | A delivery order stores the customer's delivery address (`address_id`) | Sabina, Karakat | 1) Delivery order without address → HTTP 400. 2) A customer can save several addresses, one `is_default`. 3) Address used in an order cannot be deleted | ACCEPTED — AT-05 |
| **FR-06** | **Role-based access to data (STOCK_LOG roles).** Only `warehouse` (and `admin`) may change stock; every stock change is written to STOCK_LOG with the employee's `employee_id` and login. Every other role sees only the data it needs (§4) | Moldyr | 1) EMPLOYEES roles: `warehouse`, `finance`, `support`, `manager`, `admin`. 2) `POST /api/products/` and Products in admin: allowed only for `warehouse`/`admin`; others HTTP 403. 3) `/api/products/low-stock/`: 403 for anonymous, `finance`, `support`. 4) `warehouse` cannot open Customers, Orders, Payments. 5) Each employee stock edit → STOCK_LOG row with `employee_id`, `changed_by` = login, reason `delivery`/`correction`; automatic rows (`sale`, `refund` by system) have `employee_id = NULL`. 6) A customer account cannot open `/admin/`. 7) Covered by automated tests | ACCEPTED — AT-06, AT-06b (+ 12 unit tests) |
| FR-07 | When a book is out of stock, the customer can press "Notify me"; the request is saved in STOCK_REQUESTS | Karakat (UI + API), Aidana (report R-02) | 1) Button visible only when stock = 0. 2) `POST /api/products/<id>/notify/` saves a row; same customer + same book twice → 1 row. 3) Report R-02 returns requests per book. 4) When stock > 0 again, `notified = true` | NOT ACCEPTED — DEF-02 — table exists, endpoint and button missing |
| FR-08 | An unpaid order whose 15-minute reservation has expired is cancelled and no longer blocks the book for other customers | Ayaulym | 1) `status = reserved` and `reserved_until < now()` → `cancelled` at the next request. 2) The expired order is not counted in `available_quantity`. 3) Paying an expired order → HTTP 409. 4) A paid order is never cancelled by expiry | ACCEPTED — AT-03 |
| **FR-09 (new)** | **Refund.** An employee with role `finance` (or `admin`) can refund a successful payment. In one transaction: payment → `refunded` with reason and time, order → `cancelled`, books returned to stock, STOCK_LOG row `refund +quantity` | Moldyr | 1) Only `success` payments can be refunded; `failed` → error. 2) Second refund of the same payment → error "already refunded". 3) Stock +quantity and STOCK_LOG `refund` row appear; if any step fails, nothing is saved (ROLLBACK). 4) Reason is one of `changed_mind / defective / other`. 5) `warehouse`, `support`, `manager` cannot refund (403). 6) Payments can never be deleted, even by admin | ACCEPTED — AT-08 (+ 11 unit tests) |
| **FR-10 (new)** | **Delivery fee** is added to the order total: 1000 KZT within city limits, 1500 KZT outside. The fee depends on the address flag `within_city`, not on the city name | Sabina, Karakat | 1) Order with `within_city = true` → total = books + 1000. 2) `within_city = false` → books + 1500. 3) The fee is shown on the order page before payment. 4) The paid amount in PAYMENTS equals this total | ACCEPTED — AT-05b |
| **FR-11 (new)** | **Reviews, ratings and catalog filters.** A logged-in customer can rate a book 1–5 and leave a comment; the catalog shows the average rating and can be filtered by price range and minimum rating, and sorted by price or rating | Karakat | 1) Review requires login (anonymous → 401). 2) One review per customer per book: second post updates the first, still 1 row. 3) Rating outside 1–5 → 400. 4) `?min_price=&max_price=` returns only books in range; a non-number → 400. 5) `?min_rating=4` returns only books with average ≥ 4 (books without reviews excluded). 6) Average rating is computed by the database (AVG), not in the frontend | ACCEPTED — AT-09, AT-10 (+ 8 unit tests) |

### Business rules

| ID | Rule |
|----|------|
| BR-01 | An unpaid order reserves the books for 15 minutes (`reserved_until = order_date + 15 min`). Stock is **not** reduced at reservation; availability = stock − reserved by unexpired orders. |
| BR-02 | `stock_quantity` can never be negative (CHECK ≥ 0). |
| BR-03 | Stock check and stock reduction happen in **one** database transaction with a row lock (`select_for_update`). Two payments for the last copy: one succeeds, one gets "out of stock" (covered by `test_concurrency.py`). |
| BR-04 | `transaction_id` is unique — the same payment is never processed twice; double click on "Pay" pays once. |
| BR-05 | A category with books, an employee referenced by STOCK_LOG, a customer with orders, an address used in an order — cannot be deleted (ON DELETE RESTRICT / PROTECT). |
| BR-06 (new) | A payment row is never deleted; a refund changes its status to `refunded`. |
| BR-07 (new) | The delivery fee is fixed at the moment of ordering (part of the order total) and is refunded together with the books. |

---

## 3. Reports the business gets from the database

| ID | Question | Who uses it | Status |
|----|----------|-------------|--------|
| R-01 | Which books have fewer than 10 copies? (`/api/products/low-stock/`) | warehouse, manager | ACCEPTED — works, protected by role |
| R-02 | How many customers wanted a book that was out of stock? (`SELECT product, COUNT(*) FROM stock_requests … GROUP BY product`) | warehouse (what to reorder first) | NOT ACCEPTED — blocked by DEF-02 — no data comes in yet |
| R-03 | Books sold per category this month | manager | NOT TESTED — query written (v2), not exposed in admin yet |
| R-04 (new) | Average rating and number of reviews per book (`AVG(rating), COUNT(*) FROM reviews GROUP BY product`) | manager, catalog page | ACCEPTED — computed by the DB in `/api/products/` |

---

## 4. Roles and access matrix (as implemented in `admin.py` / `permissions.py`)

| Data | warehouse | finance | support | manager | admin |
|------|-----------|---------|---------|---------|-------|
| Products, stock | **edit** (logged) | view | — | view | all |
| Categories | edit | view | view | edit | all |
| Customers, Addresses | — | view | view / edit addresses | view / edit addresses | all |
| Orders | — | edit | edit | view | all |
| Payments, refund | — | **view + refund** | — | view | all |
| STOCK_LOG | view | — | — | view | all |
| STOCK_REQUESTS | edit | — | edit | edit | all |
| Reviews | — | — | edit | edit | all |
| Low-stock report (R-01) | yes | 403 | 403 | yes | yes |
| Customer (website) | catalog, own orders, own reviews — no admin access |||||

Principle: each role sees only what its work needs; customer contact data and payments are hidden from `warehouse`.

---

## 5. Risks / open points

| Risk | Impact | Response | Owner | Date |
|------|--------|----------|-------|------|
| DEF-01: book without category can be saved | Invisible in category filter; two fields (`genre`, `category_id`) for the same fact | NOT NULL + migration, drop `genre` | Sabina, Karakat | 20.11 |
| DEF-02: "Notify me" not implemented | Report R-02 impossible; FR-07 not accepted | Endpoint + button | Karakat | 20.11 |
| Website login does not yet give the customer "my orders / my addresses" pages | Customer still types email at checkout | Use the login token for orders and addresses | Karakat, Moldyr | 20.11 |
| ERD v3 not yet drawn (REVIEWS table, `delivery_method`, address details) | Diagram behind the code again | Update ERD after DEF-01 (so `genre` is already gone) | Aidana | 20.11 |

Status: **On Track** — core process (reserve → pay → stock −1, race condition, refund, roles) is tested and passes; the two open defects are in secondary features and have owners and dates.

---

## 6. Next measurable task (Aidana, by 20.11.2026)

1. **Requirements for next week's features before they are built** (agreed in the team chat 12–13.11): FR-12 book page with description, author, category, price, availability (Sabina/Karakat); FR-13 shop feedback form (Sabina); FR-14 support tickets — customer writes about an order or refund, `support` role sees and closes it in admin (Moldyr); FR-15 demo employees for every role (Moldyr); R-02 demand report and R-03 monthly sales per category exposed as API (Sabina). Each with owner and acceptance criteria, agreed with Karakat (frontend) — by 16.11 so the team builds from them, not the other way round.
2. Re-test AT-04 and AT-07 after the fixes; add 3 scenarios (race on the website, refund by non-finance role, `min_rating` filter) → target 16 / 16 PASS in `docs/acceptance_tests.md`.
3. ERD v3 with REVIEWS, SUPPORT_TICKETS and without `genre` / `changed_by`.
