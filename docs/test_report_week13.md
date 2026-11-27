# Test Report — Week 13 (27.11.2026)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Tested build:** `main` at commit `6c4cad2` (27.11, 11:00) — this week's changes: order opened by secret code (Moldyr, DEF-05), support replies + "My requests" + message moderation + About page (Moldyr), personal account page, **deploy to Render** with PostgreSQL, top-rated podium, back-in-stock e-mail, favourite categories + "For you" recommendations (Karakat), catalog of 40 books with descriptions, Russian translation, search fixes (Sabina).
**Previous report:** `test_report_week12.md` (20.11, 24 / 27).
**How it was run:** 33 acceptance scenarios against the backend API on a fresh `seed_books` + `seed_employees` database; race scenario on PostgreSQL. Team unit tests: `python manage.py test shop`.

## 1. Summary

| | Week 12 (20.11) | Week 13 (27.11) |
|---|---|---|
| Scenarios | 27 | **33** (+6: support reply, moderation, order tickets, top rated, similar books, For you) |
| PASS | 24 | **31** (30 on SQLite + race on PostgreSQL) |
| Open | 3 | **2 defects + 1 decision** |
| DEF-05 (order readable by number) | open | **closed** — order URL is now a UUID code; number → 404, random code → 404 |
| DEF-03 (team tests red) | open | **still open, worse**: 39 of 101 fail (34 category + 4 new static-files errors + 1 address) |
| DEF-04 (reports 403 for everyone) | open | **still open** — not touched |
| Server | localhost only | **deployed**: `online-book-shop-xkbi.onrender.com`, PostgreSQL on Render |

Status: **On Track for features, At Risk for quality** — every function the customer sees is accepted; the two open defects are both on the backend side and both are two-line fixes that were not done this week.

## 2. Results

### Existing requirements (FR-01 – FR-11) — 16 scenarios, all PASS
AT-01 … AT-12 unchanged from week 12 (order → pay → stock −1; out of stock; expired reservation; category required; address required; delivery fee; roles; notify; refund; reviews; price / rating filters; support cannot refund).
AT-13 race (two buyers, double click): **PASS on PostgreSQL** — but only with the one-line category fix in the test (DEF-03); in the repository the test still errors.

### Week-12 functions (FR-12 – FR-18) — 11 scenarios

| ID | Requirement | Result 27.11 | Change |
|---|---|---|---|
| AT-14 | FR-12 book page | PASS | = |
| AT-15 | FR-13 shop review | PASS | = |
| AT-16 | FR-14 ticket on own / other's order | PASS (other's order → 404; note: moderation runs first, a too-short message gets 400 before the ownership check) | = |
| AT-16b | FR-14 support sees tickets, not payments | PASS | = |
| AT-17 | FR-15 demo employees | PASS | = |
| AT-18 | FR-16 reports | **FAIL — DEF-04** (403 for manager and admin) | = open |
| AT-19 | FR-17 my orders | PASS | = |
| AT-19b | FR-17 crit. 5 / **DEF-05** | **PASS**: `/api/orders/6/` → 404, `/api/orders/<code>/` → 200, random UUID → 404 | **FAIL → PASS** |
| AT-20 | FR-18 wishlist | PASS | = |
| AT-20b | FR-18 crit. 3 wishlist → waiting list | OPEN — decision (keep separate) | = |
| AT-21 | FR-07+ back-in-stock notification | PASS | = |

### Week-13 functions — 6 new scenarios

| ID | Requirement | Scenario | Actual | Result |
|---|---|---|---|---|
| AT-22 | FR-14 crit. 3–4 | support writes `staff_reply`; owner sees it in `/api/my-tickets/`; another customer sees an empty list; anonymous → 401 | 200 + reply / `[]` / 401 | **PASS** |
| AT-23 | FR-14 message check (new rule) | message with a link → 400; "hi" → 400; "1234567890 !!!" → 400; normal sentence → 201 | 400 / 400 / 400 / 201 | **PASS** |
| AT-24 | FR-14 / FR-17 | tickets of an order listed on the order page by its code | 200, 2 tickets | **PASS** |
| AT-25 | FR-11 / top rating | `/api/products/top-rated/?limit=3` → at most 3, sorted by rating desc, all rated | 200, sorted | **PASS** |
| AT-26 | similar books | `/api/products/P-1005/similar/` → same category first, never the book itself | 4 books, Fantasy first | **PASS** |
| AT-27 | For you | preferences need login (401); unknown category → 400; recommendations follow favourite categories, exclude wished books | 401 / 200 / 400 / 5 books, all Fantasy | **PASS** |

AT-04b (category filter) re-written: the catalog now has 40 books and 10 categories, the check compares the whole set — PASS (4 Fantasy books).

## 3. Defect log

| ID | Status 27.11 | What is wrong | Owner | Deadline | Note |
|---|---|---|---|---|---|
| DEF-05 | **closed** | order readable by number | Moldyr | — | Fixed by `public_code` UUID: the link is the secret. Different from my proposal (owner check), but closes the enumeration risk; accepted. |
| DEF-03 | **open (2nd week)** | 39 of 101 tests fail: 34 × `NOT NULL constraint failed: products.category_id` (tests create products without a category); **4 new** × `Missing staticfiles manifest entry 'admin/css/base.css'` — the production static-files storage (whitenoise manifest, added for Render) is active in tests too, so every admin-page test fails locally; 1 × address test 401. The race tests pass on PostgreSQL once a category is added in `setUp`. | Sabina (category in tests), Karakat (static storage only when `not DEBUG`), Ayaulym (address test, race on PostgreSQL) | **29.11** | Two sprints with a red suite: no teammate can tell a real regression from noise. Rule: no merge while `test shop` is red. |
| DEF-04 | **open (2nd week)** | `/api/reports/demand/`, `/api/reports/monthly-sales/` → 403 for everyone: `permission_classes` set, `authentication_classes` missing (project default is "none"). `LowStockView` has the two lines. | Sabina | **29.11** | Two-line fix; FR-16 cannot be demonstrated until then. |
| T-1 … T-5 | new (data model review) | 7 legacy columns, nullable `orders.address_id`, inconsistent table names, two address flags, single-value `delivery_method` — see `tables_review_week13.md` | Sabina, Moldyr | T-1, T-2 this week; T-3 next; T-4, T-5 decision | T-1 also unblocks DEF-03: the admin-form test posts the dead `genre` field. |

## 4. Deployment check (NFR-01)

`render.yaml` defines PostgreSQL `bookshop-db`, backend `online-book-shop-api`, frontend `online-book-shop-xkbi`. NFR-01 criteria: 1) one URL in README — **to check**; 2) PostgreSQL behind it — yes (Render); 3) `seed_books`, `seed_employees` run there — `build.sh` runs `seed_books`, **`seed_employees` missing**; 4) auto-deploy from `main` — yes (Render). → NFR-01 partially accepted; add `seed_employees` to `build.sh` and the URL + demo logins to README (Karakat).

## 5. Next step (Aidana, by 04.12.2026)

1. Re-test DEF-03 and DEF-04 → 33 / 33; run the full suite on PostgreSQL after the clean-up migration (T-1, T-2).
2. Acceptance of the deployed site: AT-01, AT-02, AT-14, AT-19 run against `online-book-shop-xkbi.onrender.com` instead of localhost — the final demo will be shown there.
3. Confirm T-3 … T-6 decisions (T-6: languages as a table, not JSON) and publish ERD v3.2 after the clean-up migration: 15 tables, no legacy columns.
4. Requirements v5: write FR-19 (top rating / podium), FR-20 (For you: favourite categories, similar books, recommendations), FR-21 (back-in-stock e-mail), FR-22 (catalog language switch) — built this week without a requirement; criteria from AT-25 – AT-27.
