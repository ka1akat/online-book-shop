# Acceptance Test Report — Week 11 (13.11.2026)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Tested build:** commit `f9b0ebc` (main, 13.11.2026)
**How it was run:** `backend/` → `python manage.py shell < docs/acceptance_tests.py` (Django test client against the real API, fresh `seed_books` data). The team's own unit tests were also run first: `python manage.py test shop` → **56 tests OK**.

## 1. Results

| ID | Requirement | Scenario (what a user does) | Expected | Actual | Result |
|---|---|---|---|---|---|
| AT-01 | FR-02, BR-01 | Create order for "The Little Prince" → pay with a valid card | Order `paid`; stock 25 → 24; STOCK_LOG row `sale −1`; PAYMENTS row `success` | order 201, pay 200, status `paid`, stock 25→24, log −1, payment success | **PASS** |
| AT-02 | FR-01, FR-03 | Try to order "Atomic Habits" (stock 0) | Order rejected, message "Out of stock" | HTTP 409 «в наличии только 0 шт.» | **PASS** |
| AT-03 | FR-08 | Create order, let the 15-minute reservation expire, try to pay | Payment refused; order becomes `cancelled`; stock unchanged | HTTP 409, status `cancelled`, stock 7→7 | **PASS** (criteria revised, see §3) |
| AT-04 | FR-04 (crit. 1) | Warehouse employee creates a book **without category** | Rejected (HTTP 400) | **HTTP 201 — book saved with category = NULL** | **FAIL → DEF-01** |
| AT-04b | FR-04 (crit. 3) | Filter catalog by category "Fantasy" | Only books of that category | `?category_id=5 → [P-1005]` | **PASS** |
| AT-05 | FR-05 (crit. 2) | Create delivery order **without address** | Rejected (HTTP 400) | HTTP 400 "Address is required for delivery." | **PASS** |
| AT-05b | FR-10 (new) | Order with address within city limits / outside | Total = books + 1000 / + 1500 | 3000 → 4000 / 4500 | **PASS** |
| AT-06 | FR-06 (crit. 2, 3) | Employee with role `finance` opens low-stock report and tries to add stock | HTTP 403 for both | 403 / 403 | **PASS** |
| AT-06b | FR-06 (crit. 5) | Employee with role `warehouse` adds a book with 20 copies | STOCK_LOG row with `employee_id`, login, reason `delivery` | employee_id=1, changed_by=wh_test, reason=delivery | **PASS** |
| AT-07 | FR-07 | Customer presses "Notify me" on an out-of-stock book | Row saved in STOCK_REQUESTS | **HTTP 404 — no API endpoint, no button on the site** | **FAIL → DEF-02** |
| AT-08 | FR-09 (new) | Finance refunds a successful payment; then tries again | Payment `refunded`, order `cancelled`, stock +1, STOCK_LOG `refund`; 2nd refund rejected | all true; 2nd refund → error "already refunded" | **PASS** |
| AT-09 | FR-11 (new) | Logged-in customer posts a review, posts again, posts rating 6, anonymous posts | 1st 201, 2nd updates (200) — still 1 row; rating 6 → 400; anonymous → 401 | 201 / 200 / 1 row / 400 / 401 | **PASS** |
| AT-10 | FR-11 (new) | Catalog filter `min_price=4000&max_price=6000` | Only books priced 4000–6000 | [4500, 5000] | **PASS** |

**Total: 11 PASS / 2 FAIL.** All 2 failures are gaps in the new requirements (FR-04, FR-07), not in the core process (overselling protection, payment, reservation, roles, refund — all pass).

## 2. Defect log

| ID | Found in | What is wrong | Why it matters | Requirement violated | Owner | Fix | Deadline |
|---|---|---|---|---|---|---|---|
| DEF-01 | AT-04 | `Product.category` is `null=True`; API `POST /api/products/` accepts a book with no category | Such a book is invisible in every category filter on the main page; old text field `genre` is still used instead of `category_id` | FR-04 crit. 1 | Sabina (model), Karakat (form) | Make `category` NOT NULL in the model + migration; serializer `category_id` required; then drop the old `genre` field | 20.11 |
| DEF-02 | AT-07 | Table STOCK_REQUESTS exists in the DB, but there is no API endpoint and no "Notify me" button on the book page | Report R-02 "demand for out-of-stock books" cannot be produced — the inventory manager still does not know what to reorder first | FR-07 crit. 1–3 | Karakat (endpoint + button), Aidana (report R-02 check) | `POST /api/products/<id>/notify/` with the customer's email; button shown only when stock = 0 | 20.11 |

## 3. Requirement changes found by testing

| Requirement | Finding | Decision |
|---|---|---|
| FR-08 (expired reservation) | v2 criteria said "a job runs every minute" and "STOCK_LOG gets a row +quantity". In the real design stock is **not** reduced at reservation — a reservation only counts against `available_quantity`, and expiry is checked at every request (`expire_reservations()`), not by a scheduler. So nothing has to be "returned" and no job is needed. | Criteria rewritten in requirements v3: expired order → `cancelled`; it is no longer counted in availability; payment of it is refused. No STOCK_LOG row. |
| FR-06 (roles) | v2 named roles `admin / inventory_manager / warehouse / finance`. The implemented roles are `warehouse / finance / support / manager / admin` (no `inventory_manager`). | FR-06 updated to the real roles and to what each one can see (v3 §4). |
| FR-05 (address) | Implemented together with a delivery fee that depends on `within_city`, not on the city name. This rule was never written down. | New requirement FR-10. |
| Refund, reviews, price/rating filters | Built this week by Moldyr and Karakat without a requirement. | New requirements FR-09 and FR-11 with acceptance criteria; both already pass (AT-08, AT-09, AT-10). |

## 4. Next step (Aidana, by 20.11.2026)

Re-run AT-04 and AT-07 after DEF-01 and DEF-02 are fixed, and add 3 scenarios for the race condition on the website (two browsers buying the last copy), the refund by a non-finance role (expect 403) and the rating filter `min_rating`. Target: 16 / 16 PASS, recorded in this file.
