# Online Book Shop — Requirements v4 (Week 12)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Date:** 20.11.2026
**Extends:** requirements_v3.md (13.11) — FR-01 … FR-11, business rules BR-01 … BR-07, roles matrix stay valid and are not repeated here
**Purpose:** requirements for the five functions the team planned in the chat on 13.11 — written **before** they are built, so frontend (Karakat), database (Sabina) and security (Moldyr) build from one document. Agreed with Karakat (frontend) on 19.11.

---

## 1. Scope of this version

| ID | Function | Planned by | Builds on | Priority |
|----|----------|-----------|-----------|----------|
| FR-12 | Book page with description | Sabina (data), Karakat (page) | FR-04, FR-11 | High — needed for the catalog demo |
| FR-13 | Shop feedback form | Sabina | FR-11 | Medium |
| FR-14 | Support tickets | Moldyr | FR-06, FR-09 | High — closes the "what if the customer has a problem" gap |
| FR-15 | Demo employees for every role | Moldyr | FR-06 | High — needed to demonstrate roles at the check |
| FR-16 | API reports: demand (R-02) and monthly sales per category (R-03) | Sabina | FR-07 (DEF-02), FR-04 | Medium — R-02 blocked until DEF-02 is fixed |

Priority rule: FR-12, FR-14, FR-15 first (they are shown at the check); FR-13 and FR-16 after.

---

## 2. Functional requirements

### FR-12 — Book page

**Requirement.** Every book has a text description. Clicking a card in the catalog opens the book's own page with: title, author, category, description, price, availability (in stock / out of stock with quantity), average rating and the reviews (FR-11). From this page the customer can add the book to the cart or, when stock is 0, press "Notify me" (FR-07).

**Owner.** Sabina — `PRODUCTS.description` + seed data; Karakat — page `/books/<product_id>`.

**Data.** New column `PRODUCTS.description TEXT NOT NULL DEFAULT ''` (ERD v3). Existing endpoint `GET /api/products/<id>/` already returns one book with `avg_rating` — add `description` to the serializer; no new endpoint needed.

**Acceptance criteria.**
1. `GET /api/products/P-1004/` returns `description`; for all five seed books the description is not empty.
2. Clicking any card in the catalog opens `/books/<product_id>`; the page shows title, author, category name (not category_id), description, price, availability, average rating and the review list.
3. For a book with stock 0 the page shows "Out of stock" and the "Add to cart" button is disabled (same rule as FR-03).
4. Opening `/books/P-9999` (unknown id) shows "Book not found", not an error page.
5. "Add to cart" on the book page puts exactly one copy in the cart and the cart counter increases by one.

### FR-13 — Shop feedback form

**Requirement.** A customer can leave feedback about the shop as a whole (not about a book): rating 1–5 and a comment. The feedback is stored separately from book reviews and is visible to `support` and `manager` in admin; it is **not** shown on the public site (so the manager can read it first).

**Owner.** Sabina — table + endpoint; Karakat — form on the page "About / Feedback".

**Data.** New table `SHOP_FEEDBACK (feedback_id PK, customer_id FK → CUSTOMERS nullable, rating 1–5, comment, created_at, is_resolved boolean default false)`. `customer_id` is nullable so a visitor without an account can also send feedback; in that case `email` is stored in a `contact_email` column.

**Acceptance criteria.**
1. `POST /api/feedback/` with `rating=5, comment="…"` from a logged-in customer → 201 and a row with `customer_id`.
2. The same request without login but with `contact_email` → 201, `customer_id = NULL`.
3. `rating = 0` or `6` → 400 (CHECK constraint 1–5, like `reviews`).
4. `comment` longer than 1000 characters → 400.
5. Feedback does **not** appear in `GET /api/products/<id>/reviews/` and is not shown anywhere on the public site.
6. In admin, `support` and `manager` can open Shop feedback and set `is_resolved`; `warehouse` and `finance` cannot open it (403).

### FR-14 — Support tickets

**Requirement.** A customer can open a ticket about an order or a refund. A `support` employee sees all open tickets in admin, answers, and closes the ticket. If the ticket asks for a refund, support can mark it "refund requested", but only `finance` executes the refund (FR-09) — support never touches payments.

**Owner.** Moldyr — table, admin, permissions; Karakat — "My orders → Need help?" button and the ticket form.

**Data.** New table `SUPPORT_TICKETS (ticket_id PK, customer_id FK → CUSTOMERS, order_id FK → ORDERS nullable, subject, message, status ENUM('open','in_progress','refund_requested','closed') default 'open', assigned_employee_id FK → EMPLOYEES nullable, reply, created_at, closed_at nullable)`.

**Acceptance criteria.**
1. A logged-in customer can create a ticket from their order page; `order_id` is filled automatically and must belong to that customer (ticket for someone else's order → 403).
2. A ticket without login → 401.
3. `support` sees all tickets in admin, can change `status`, write `reply`, and `assigned_employee_id` is filled with their employee id when they take a ticket.
4. Closing a ticket sets `closed_at`; a closed ticket cannot be reopened by the customer (new message → new ticket).
5. `support` can set `refund_requested`, but has no access to Payments and cannot call the refund action (403 — AT-11 already covers this).
6. `finance` sees tickets with status `refund_requested` (read-only) and executes the refund in Payments; after the refund the ticket is closed by support.
7. `warehouse` cannot open Support tickets at all (403). Customer contact data stays hidden from warehouse (roles matrix, v3 §4).
8. Business rule **BR-08:** a ticket can reference an order only; a ticket about a payment is created from the order that payment belongs to.

### FR-15 — Demo employees for every role

**Requirement.** The database contains one ready-made employee account per role — `warehouse`, `finance`, `support`, `manager`, `admin` — created by a management command, so that at every weekly check the team can log in as any role and show what that role sees.

**Owner.** Moldyr.

**Data.** No new tables. Command `python manage.py seed_employees` (like `seed_books`), idempotent — running it twice does not duplicate rows.

**Acceptance criteria.**
1. After `seed_employees`: 5 users + 5 EMPLOYEES rows, one per role, `is_active = true`, each linked to its Django user (`user_id` not null).
2. Logins and passwords are documented in `README.md` in a "Demo accounts" table (demo passwords only, not real ones).
3. Running `seed_employees` twice → still 5 rows (no duplicates, no error).
4. Logging in as each demo account and opening `/admin/` shows exactly the sections from the roles matrix (v3 §4): e.g. `warehouse` sees Products, Categories, Stock log, Stock requests and not Customers / Orders / Payments.
5. A demo employee account cannot be used as a customer on the website to leave a review (employees are not customers; review → 401 for an employee token, or the employee has no customer record).
6. `seed_employees` is part of the setup instructions in `README.md` next to `seed_books`.

### FR-16 — Business reports as API

**Requirement.** Two reports from requirements v2/v3 are exposed as protected API endpoints, so they can be shown on an admin page and checked at the weekly check:
- **R-02 Demand:** which books customers requested most while out of stock (from STOCK_REQUESTS).
- **R-03 Monthly sales per category:** how many books were sold in each category this month (paid orders only).

**Owner.** Sabina (endpoints), Moldyr (permissions). **Depends on DEF-02** for R-02 data.

**Data.** No new tables. Endpoints `GET /api/reports/demand/` and `GET /api/reports/sales-by-category/?month=2026-11`.

**Acceptance criteria.**
1. `GET /api/reports/demand/` returns `[ {product_id, product_name, requests} … ]` sorted by `requests` descending, counting only rows with `notified = false`.
2. `GET /api/reports/sales-by-category/?month=2026-11` returns `[ {category_name, books_sold, revenue} … ]` using only orders with `status = paid`; refunded orders (`cancelled` after refund) are excluded.
3. `month` missing → current month; `month=2026-13` → 400.
4. Both endpoints: 403 for anonymous, customers, `support`; allowed for `manager`, `warehouse` (demand only), `finance` (sales only), `admin`.
5. The numbers are computed by the database (`COUNT`, `SUM … GROUP BY`), not by looping in Python — the SQL is written in the view docstring, like `LowStockView`.
6. After AT-01 (one paid copy of "The Little Prince", category Children's Books), R-03 for the current month returns `Children's Books: books_sold = 1, revenue = 3000`.

---

## 3. Data model changes for ERD v3

| Table / column | Change | For |
|---|---|---|
| `PRODUCTS.description` | new, TEXT, NOT NULL default '' | FR-12 |
| `SHOP_FEEDBACK` | new table (feedback_id PK, customer_id FK nullable, contact_email, rating, comment, is_resolved, created_at) | FR-13 |
| `SUPPORT_TICKETS` | new table (ticket_id PK, customer_id FK, order_id FK nullable, subject, message, status, assigned_employee_id FK nullable, reply, created_at, closed_at) | FR-14 |
| `REVIEWS` | already exists since 13.11 — added to the diagram (review_id PK, product_id FK, customer_id FK, rating, comment, created_at, updated_at; UNIQUE customer+product, CHECK rating 1–5) | FR-11 |
| `ADDRESSES` | diagram updated to the real columns: full_address, entrance, floor, intercom_code, within_city; old `street`, `building` to be dropped | FR-05, FR-10 |
| `PAYMENTS` | added refund_reason, refunded_at | FR-09 |
| `PRODUCTS.genre`, `STOCK_LOG.changed_by` | to be dropped after DEF-01 (already replaced by category_id / employee_id) | FR-04, FR-06 |

Result: 13 tables (10 in v2 + REVIEWS + SHOP_FEEDBACK + SUPPORT_TICKETS). See `docs/ERD_v3_OnlineBookShop.png`.

---

## 4. Business rules added

| ID | Rule |
|----|------|
| BR-08 | A support ticket references an order; refunds are executed only by `finance` (FR-09), support can only request them. |
| BR-09 | Shop feedback and book reviews are different entities: a review is always about one product and is public; feedback is about the shop and is internal. |
| BR-10 | Demo employee accounts are for demonstration only: they are created by `seed_employees`, documented in README, and never used for real data entry. |

---

## 5. Process rule found by testing (week 12)

The race-condition tests (`test_concurrency.py`) are skipped automatically on SQLite. Before every weekly check one teammate runs them on PostgreSQL:
`DB_ENGINE=postgres … python manage.py test shop.test_concurrency` — and the result is written in the test report. Owner: Ayaulym. README gets this line.

---

## 6. Status and risks

| Risk | Impact | Response | Owner | Date |
|------|--------|----------|-------|------|
| DEF-01, DEF-02 not fixed by 19.11 | FR-04 / FR-07 still not accepted; FR-16 R-02 has no data | Fix first, before new functions | Sabina, Karakat | 22.11 |
| Five functions planned for one week | Not everything will be ready for the check | Priority order FR-12, FR-14, FR-15 first (§1) | team | 27.11 |
| Support tickets touch customer data and payments | Wrong permissions could expose data | Criteria 5–7 of FR-14 + AT-11 | Moldyr | 27.11 |

Status: **On Track** — core process accepted (14 / 16), new functions have written requirements before coding.

---

## 7. Next measurable task (Aidana, by 27.11.2026)

1. Acceptance scenarios AT-14 … AT-25 for FR-12 – FR-16 (one per criterion that can be checked on the site or API), run as each function is merged; target: every merged function accepted the same week.
2. Re-test DEF-01 / DEF-02 → 16 / 16.
3. ERD v3 published (`docs/ERD_v3_OnlineBookShop.png`) — done with this version.
