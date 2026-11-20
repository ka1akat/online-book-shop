# Online Book Shop — Requirements v4 (Week 12)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Date:** 20.11.2026
**Extends:** requirements_v3.md (13.11) — FR-01 … FR-11, business rules BR-01 … BR-07, roles matrix stay valid and are not repeated here
**Purpose:** requirements for the functions the team planned in the chat on 13.11 and in the teacher's plan for week 12 (Moldyr: support, employees; Ayaulym: reservation process; Karakat: notification, waiting list, my order page, wish list, server; Sabina: description, review about site, API stock request, API best seller, server, address, book's category) — written **before** they are built, so frontend (Karakat), database (Sabina) and security (Moldyr) build from one document. Agreed with Karakat (frontend) on 19.11.

---

## 1. Scope of this version

| ID | Function | Planned by | Builds on | Priority |
|----|----------|-----------|-----------|----------|
| FR-12 | Book page with description | Sabina (data), Karakat (page) | FR-04, FR-11 | High — needed for the catalog demo |
| FR-13 | Shop feedback form | Sabina | FR-11 | Medium |
| FR-14 | Support tickets | Moldyr | FR-06, FR-09 | High — closes the "what if the customer has a problem" gap |
| FR-15 | Demo employees for every role | Moldyr | FR-06 | High — needed to demonstrate roles at the check |
| FR-16 | API reports: demand (R-02), monthly sales per category (R-03), best sellers (R-05) | Sabina | FR-07 (DEF-02), FR-04 | Medium — R-02 blocked until DEF-02 is fixed |
| FR-17 | "My orders" page for a logged-in customer | Karakat | FR-05, login | High — needed for FR-14 (ticket from the order page) |
| FR-18 | Wish list | Karakat | FR-07, login | Medium |
| FR-07+ | Waiting list = "Notify me" (DEF-02) + notification when the book is back | Karakat | FR-07 | High — it is an open defect |
| NFR-01 | Server: the site runs on a shared server, not only on localhost | Karakat, Sabina | — | Medium — non-functional, needed for the final demo |

Priority rule: first the open defects (DEF-01 category, DEF-02 notify), then FR-12, FR-14, FR-15, FR-17 (they are shown at the check); FR-13, FR-16, FR-18 after. Ayaulym's "reservation process" is FR-08 — already accepted (AT-03); her task this week is to run the race tests on PostgreSQL (§5).

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
- **R-05 Best sellers:** top-10 books by copies sold (paid orders, all time or for a month).

**Owner.** Sabina (endpoints), Moldyr (permissions). **Depends on DEF-02** for R-02 data.

**Data.** No new tables. Endpoints `GET /api/reports/demand/`, `GET /api/reports/sales-by-category/?month=2026-11`, `GET /api/reports/best-sellers/?limit=10&month=2026-11`.

**Acceptance criteria.**
1. `GET /api/reports/demand/` returns `[ {product_id, product_name, requests} … ]` sorted by `requests` descending, counting only rows with `notified = false`.
2. `GET /api/reports/sales-by-category/?month=2026-11` returns `[ {category_name, books_sold, revenue} … ]` using only orders with `status = paid`; refunded orders (`cancelled` after refund) are excluded.
3. `month` missing → current month; `month=2026-13` → 400.
4. Both endpoints: 403 for anonymous, customers, `support`; allowed for `manager`, `warehouse` (demand only), `finance` (sales only), `admin`.
5. The numbers are computed by the database (`COUNT`, `SUM … GROUP BY`), not by looping in Python — the SQL is written in the view docstring, like `LowStockView`.
6. After AT-01 (one paid copy of "The Little Prince", category Children's Books), R-03 for the current month returns `Children's Books: books_sold = 1, revenue = 3000`.
7. `GET /api/reports/best-sellers/` returns `[ {product_id, product_name, copies_sold} … ]` sorted by `copies_sold` descending, max `limit` rows (default 10), paid orders only; a book never sold is not in the list. Same roles as R-03. The public catalog may show a "Bestseller" label for the top-3 — read-only, no role needed.

### FR-17 — "My orders" page

**Requirement.** A logged-in customer sees a page with their own orders: number, date, status (reserved / paid / cancelled), total with delivery, items, and the delivery address. From a `paid` order the customer can open a support ticket (FR-14). A `reserved` order shows the time left until the reservation expires and a "Pay" button.

**Owner.** Karakat (page + endpoint `GET /api/my/orders/`), Moldyr (token check).

**Data.** No new tables. Orders are matched to the customer by the email of the logged-in user (the same rule as reviews).

**Acceptance criteria.**
1. `GET /api/my/orders/` without login → 401; with login → only orders whose `customer.email` equals the user's email (never someone else's).
2. The page lists orders newest first with status, date and total including delivery fee (FR-10).
3. A `reserved` order shows minutes left (from `reserved_until`) and a "Pay" button; after `reserved_until` passes the order is shown as `cancelled` (FR-08).
4. A `paid` order has a "Need help?" button that opens the ticket form with `order_id` pre-filled (FR-14 crit. 1).
5. Opening `/api/orders/<id>/` of another customer's order by a logged-in user → 403 (today it is open by id — this is a security gap to close in the same change).

### FR-18 — Wish list

**Requirement.** A logged-in customer can add a book to a wish list and remove it; the list is kept in the database, not only in the browser. A book in the wish list that is out of stock automatically becomes a "Notify me" request (FR-07), so the customer is told when it is back.

**Owner.** Karakat (button + page), Sabina (table).

**Data.** New table `WISHLIST_ITEMS (wishlist_item_id PK, customer_id FK → CUSTOMERS, product_id FK → PRODUCTS, added_at; UNIQUE customer_id + product_id)`. Added to ERD v3.1.

**Acceptance criteria.**
1. "Add to wish list" without login → 401; with login → 201 and a row; the same book twice → still one row (UNIQUE), 200.
2. The wish-list page shows the customer's books with current price and availability; "Remove" deletes the row.
3. Adding an out-of-stock book to the wish list also creates a STOCK_REQUESTS row for that customer and book (FR-07); adding an in-stock book does not.
4. A book in the wish list can be moved to the cart with one click when it is in stock.
5. The wish list is per customer: two customers never see each other's items.

### FR-07+ — Waiting list and notification (extension of FR-07)

**Requirement.** "Notify me" (FR-07, DEF-02) becomes a waiting list: when `warehouse` adds stock to a book that has open STOCK_REQUESTS, the customers on the list are notified (first step: a message on their "My orders / notifications" page; e-mail later), and the requests are marked `notified = true`.

**Owner.** Karakat (endpoint, button, notifications block), Sabina (update on stock change).

**Acceptance criteria.**
1. DEF-02 fixed: `POST /api/products/<id>/notify/` creates a STOCK_REQUESTS row; the button is shown only when stock = 0.
2. When stock of that book goes from 0 to > 0 (STOCK_LOG `delivery` or `refund`), all open requests for it get `notified = true` in the same transaction.
3. The customer sees "«Atomic Habits» is back in stock" on their page after the next login.
4. Report R-02 counts only `notified = false` rows, so a notified request disappears from the demand list.

### NFR-01 — Server (non-functional)

**Requirement.** The site runs on one shared server (or a free host) with PostgreSQL, so the team and the teacher open the same URL and the same data instead of five local copies.

**Owner.** Karakat (frontend build), Sabina (backend + PostgreSQL), Ayaulym (race tests on that PostgreSQL).

**Acceptance criteria.**
1. One URL in README opens the catalog from any computer.
2. The database behind it is PostgreSQL (so BR-03 row locks work); `test_concurrency.py` passes there (§5).
3. `seed_books` and `seed_employees` have been run there; demo logins from FR-15 work.
4. A commit to `main` is deployed by one documented command or automatically.


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
| `WISHLIST_ITEMS` | new table (wishlist_item_id PK, customer_id FK, product_id FK, added_at; UNIQUE customer+product) — ERD v3.1 after FR-18 is confirmed | FR-18 |

Result: 13 tables in ERD v3 (10 in v2 + REVIEWS + SHOP_FEEDBACK + SUPPORT_TICKETS); 14 with WISHLIST_ITEMS when FR-18 is confirmed. See `docs/ERD_v3_OnlineBookShop.png`.

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
| Nine items planned for one week (teacher's plan) | Not everything will be ready for the check | Priority order §1: defects → FR-12, FR-14, FR-15, FR-17 → the rest | team | 27.11 |
| `/api/orders/<id>/` is open by id to anyone (found while writing FR-17) | A customer can read another customer's order and address | Close with FR-17 crit. 5 | Karakat, Moldyr | 27.11 |
| Support tickets touch customer data and payments | Wrong permissions could expose data | Criteria 5–7 of FR-14 + AT-11 | Moldyr | 27.11 |

Status: **On Track** — core process accepted (14 / 16), new functions have written requirements before coding.

---

## 7. Next measurable task (Aidana, by 27.11.2026)

1. Acceptance scenarios AT-14 … AT-30 for FR-12 – FR-18 and FR-07+ (one per criterion that can be checked on the site or API), run as each function is merged; target: every merged function accepted the same week.
2. Re-test DEF-01 / DEF-02 → 16 / 16.
3. ERD v3 published (`docs/ERD_v3_OnlineBookShop.png`) — done with this version.
