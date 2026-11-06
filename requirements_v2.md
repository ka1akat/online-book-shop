# Online Book Shop — Requirements v2 (Week 10)

**Author:** Omerbayeva Aidana (24B032184), Systems Analysis & Requirements
**Date:** 06.11.2026
**Based on:** Task 04–09, feedback from Week 9 check ("updated ERD / new requirements / separate tables for categories and addresses")

---

## 1. What changed since v1 (Task 9)

| # | Change | Why (problem found) | Effect on the system |
|---|--------|---------------------|----------------------|
| C-1 | New table **CATEGORIES**; `PRODUCTS.genre` (free text) replaced by `PRODUCTS.category_id` (FK) | Genre was typed by hand ("Fantasy", "fantasy", "Фэнтези") → duplicates, impossible to filter reliably on the main page | Main page can show a category menu (FR-04); one record to change when a category is renamed |
| C-2 | New table **ADDRESSES**; `ORDERS.address_id` (FK) | We had no place to store delivery data at all; a customer with several addresses would repeat data in every order | Checkout step gets a delivery address (FR-05); address stored once per customer |
| C-3 | New table **EMPLOYEES**; `STOCK_LOG.changed_by` (text) replaced by `STOCK_LOG.employee_id` (FK) | Text login cannot be validated; anyone could write any name into the audit log | Only a real employee can change stock; supports role-based access in Django (FR-06, Moldyr's task) |
| C-4 | New table **STOCK_REQUESTS** | Open question from Task 9: "we do not store how many customers wanted a book that was out of stock" — the Inventory Manager report could not be built | New requirement FR-07 and a new business report (R-02) |
| C-5 | BR-01 (15-minute reservation) now has an explicit automatic cancellation requirement | In Task 9 the scheduled job was only in the problem table, not in requirements | FR-08 is now testable (Ayaulym's task) |

**Normalization check:** every fact is still stored once — customer contact in CUSTOMERS, address in ADDRESSES, category name in CATEGORIES, employee name in EMPLOYEES. The only deliberate copy remains `ORDER_ITEMS.unit_price` (price at the moment of purchase). All tables are in 3NF: no repeating groups, no partial dependencies, no non-key column depends on another non-key column.

---

## 2. Functional requirements

### Existing (v1, unchanged)

| ID | Requirement | Acceptance criteria |
|----|-------------|---------------------|
| FR-01 | The system blocks adding a book with `stock_quantity = 0` to the cart | Click "Add to cart" on a book with stock 0 → nothing is added, message "Out of stock" is shown |
| FR-02 | When an order is paid, the stock is reduced by the ordered quantity in the same transaction | After payment of 1 copy: `stock_quantity` is −1, a row appears in STOCK_LOG with `reason = 'sale'`; if payment fails, stock is unchanged |
| FR-03 | A book with stock 0 is shown with the label "Out of stock" | Product list shows the label; "Add to cart" button is disabled |

### New in v2

| ID | Requirement | Owner (team) | Acceptance criteria (how we will check it) |
|----|-------------|--------------|-------------------------------------------|
| **FR-04** | Every book belongs to exactly one category from the CATEGORIES table; the main page allows filtering books by category | Karakat (frontend), Sabina (DB) | 1) A product cannot be saved with an empty or non-existent `category_id` (FK + NOT NULL). 2) Main page shows the list of categories from the table, not a hard-coded list. 3) Choosing "Fantasy" shows only books with that `category_id`. 4) Renaming a category changes it for all its books (1 UPDATE). |
| **FR-05** | At checkout the customer chooses a delivery address from their saved addresses or adds a new one; the order stores `address_id` | Karakat (frontend), Sabina (DB) | 1) A customer can have 0..N addresses; one may be `is_default = true`. 2) An order cannot be paid without an `address_id`. 3) An address can only be chosen by its owner (`ADDRESSES.customer_id = ORDERS.customer_id`). 4) Deleting an address used in an order is rejected (ON DELETE RESTRICT). |
| **FR-06** | Only employees with role `warehouse` (and `admin`) may change stock; every change is written to STOCK_LOG with the employee's login and `employee_id`. Every other role sees only the data it needs for its work. | Moldyr (security), Sabina (DB) | 1) EMPLOYEES has roles: `warehouse`, `finance`, `support`, `manager`, `admin`. 2) Stock changes (Products in Django admin, `POST /api/products/`) are allowed only for `warehouse` and `admin`; other roles are read-only or get HTTP 403. 3) `/api/products/low-stock/` returns 403 for anonymous users, `finance` and `support`. 4) `warehouse` cannot open Customers, Orders or Payments (HTTP 403). 5) Each employee stock edit writes a STOCK_LOG row with `changed_by` = login, `employee_id` and `reason` = `delivery` or `correction`; automatic sale rows have `employee_id = NULL` and `changed_by = 'payment-system'`. 6) A customer account (no Staff status, no Employee record) cannot open `/admin/`. 7) Roles are covered by automated tests (`python manage.py test shop`). |
| **FR-07** | When a book is out of stock, the customer can press "Notify me"; the system saves the request in STOCK_REQUESTS | Karakat (frontend), Aidana (requirement + report) | 1) Button appears only when `stock_quantity = 0`. 2) One customer can request one book only once (UNIQUE customer_id + product_id). 3) Report R-02 returns the number of requests per book. 4) (Later) when stock becomes > 0, `notified` is set to true. |
| **FR-08** | An unpaid order is cancelled automatically when `reserved_until` passes; the reserved quantity returns to stock | Ayaulym (reservation logic) | 1) A job runs every minute. 2) Order with status `reserved` and `reserved_until < now()` becomes `cancelled`. 3) STOCK_LOG gets a row `+quantity`, `reason = 'reservation_expired'`. 4) A paid order is never cancelled by the job. |

### Business rules

| ID | Rule |
|----|------|
| BR-01 | An unpaid order reserves the books for 15 minutes (`reserved_until = order_date + 15 min`). |
| BR-02 | `stock_quantity` can never be negative (CHECK ≥ 0). |
| BR-03 | Stock check and stock reduction happen in **one** database transaction with a row lock (`SELECT ... FOR UPDATE`). |
| BR-04 | A `transaction_id` from the bank is unique — the same payment is never processed twice. |
| BR-05 (new) | A category cannot be deleted while it has books; an employee cannot be deleted while STOCK_LOG rows refer to them (they are deactivated with `is_active = false`). |

---

## 3. Reports the business gets from the database

| ID | Question | Who uses it | Query |
|----|----------|-------------|-------|
| R-01 | Which books have fewer than 10 copies? | Inventory Manager | `SELECT product_name, stock_quantity FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity;` |
| **R-02 (new)** | How many customers wanted a book that was out of stock? | Inventory Manager (what to reorder first) | `SELECT p.product_name, COUNT(r.request_id) AS demand FROM stock_requests r JOIN products p ON p.product_id = r.product_id WHERE r.notified = false GROUP BY p.product_name ORDER BY demand DESC;` |
| **R-03 (new)** | How many books are sold per category this month? | Shop owner | `SELECT c.category_name, SUM(oi.quantity) AS sold FROM order_items oi JOIN products p ON p.product_id = oi.product_id JOIN categories c ON c.category_id = p.category_id JOIN orders o ON o.order_id = oi.order_id WHERE o.status = 'paid' AND o.order_date >= date_trunc('month', now()) GROUP BY c.category_name ORDER BY sold DESC;` |

---

## 4. User roles and access (summary for the ERD)

| Role | Can see | Can change |
|------|---------|------------|
| Customer (website only) | catalog, own order page | create order, pay (public API; no login session yet) |
| warehouse | Products, Categories, STOCK_LOG, stock requests, low-stock report | products and categories, stock requests (every stock edit is logged) |
| finance | Customers, Addresses, Orders, Payments, Products | orders (refund: planned, see 6.2) |
| support | Customers, Addresses, Orders, stock requests | addresses, orders, stock requests |
| manager | almost everything (overview) | categories, addresses, stock requests |
| admin | everything | everything, user and role management |

Principle: each role sees only the data it needs. Customer contact data (name, phone, email, address) and payments are hidden from `warehouse`.

---

## 5. Risks / open points (status: At Risk)

| Risk | Impact | Response | Owner | Date |
|------|--------|----------|-------|------|
| Prototype (localhost:4200) is not yet connected to PostgreSQL | No end-to-end demo | Connect Django to DB, replace fixed book list with PRODUCTS | Karakat, Sabina | 10.11 |
| Race condition test (2 payments for the last book) not done | Core problem of the project not proven | Write test with 2 parallel transactions | Ayaulym | 10.11 |
| ERD v2 not yet reflected in Django models | Code and model diverge again | Sabina migrates models from `docs/erd_v2.sql` | Sabina | 10.11 |
| Roles work only in Django admin and 2 API endpoints; website login does not create a session | "Customer sees only own data" and staff login on the website cannot be enforced yet | Add session or token login together with the frontend | Moldyr | 10.11 |
| Refund by finance is not implemented | Requirement "finance: read, refund" is only half done | Admin action: payment `refunded`, order `cancelled`, stock returned, STOCK_LOG row, one transaction (task 6.2) | Moldyr | 10.11 |
---

## 6. Next measurable task (Aidana, by 13.11.2026)

Write and run **5 acceptance test scenarios** for the main process (register → add to cart → pay → stock −1; out-of-stock case; expired reservation; wrong category; address missing) and record pass/fail for each in `docs/acceptance_tests.md`.
