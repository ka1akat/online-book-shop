// О нас: что это за магазин, как им пользоваться и как связаться с поддержкой.
// Страница открывается без входа. Цифры (бронь 15 минут, стоимость доставки) совпадают с кодом бэкенда.

import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-about',
  imports: [RouterLink],
  template: `<section class="page about">
    <header class="page-head">
      <h1>About us</h1>
      <p class="muted">Online Book Shop is a student project made at KBTU.</p>
    </header>

    <div class="panel">
      <h2>What you can do here</h2>
      <ul>
        <li>Browse the <a routerLink="/catalog">catalog</a>, filter books by category, price and rating.</li>
        <li>Read book pages and reviews, and leave your own review after you log in.</li>
        <li>Add books to the cart and the wishlist.</li>
        <li>Press “Notify me” on a book that is out of stock and we will tell you when it is back.</li>
        <li>Rate the shop on the <a routerLink="/shop-reviews">shop reviews</a> page.</li>
      </ul>
    </div>

    <div class="panel">
      <h2>Orders, delivery and payment</h2>
      <ul>
        <li>After you place an order, the books are reserved for you for 15 minutes. Pay within this time, otherwise the reservation expires.</li>
        <li>Delivery costs 1 000 ₸ inside the city limits and 1 500 ₸ outside them.</li>
        <li>Payment in this project is simulated: no real money is taken.</li>
        <li>Every order has its own secret link. Keep it: anyone who has the link can open the order, and nobody can guess it.</li>
      </ul>
    </div>

    <div class="panel">
      <h2>Contact support</h2>
      <p>
        Have a problem with an order, a refund or delivery? Open your order and press
        “Contact support about this order”. Choose a topic and describe the problem in a few clear words.
      </p>
      <ul>
        <li>Please write politely. Messages with rude words, links or meaningless text are not sent.</li>
        <li>Support answers on the same order page. If you are logged in, all your messages and answers are in
          <a routerLink="/account/tickets">My requests</a>.</li>
        <li>A request can be <b>open</b> (not seen yet), <b>in progress</b> (support is working on it) or <b>closed</b> (solved).</li>
      </ul>
    </div>

    <div class="panel">
      <h2>The team</h2>
      <p>The shop was built by the KBTU Online Shop Team: Django REST backend, Angular frontend, PostgreSQL on Render.</p>
    </div>
  </section>`,
})
export class AboutComponent {}
