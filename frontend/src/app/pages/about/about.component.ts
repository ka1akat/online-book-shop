// О нас: что это за магазин, как им пользоваться и как связаться с поддержкой.
// Страница открывается без входа. Цифры (бронь 15 минут, стоимость доставки) совпадают с кодом бэкенда.

import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-about',
  imports: [RouterLink],
  template: `<section class="page about">
    <header class="page-head">
      <h1>{{ language.tr('About us') }}</h1>
      <p class="muted">{{ language.tr('Online Book Shop is a student project made at KBTU.') }}</p>
    </header>

    <div class="panel">
      <h2>{{ language.tr('What you can do here') }}</h2>
      <ul>
        <li>{{ language.tr('Browse the') }} <a routerLink="/catalog">{{ language.tr('catalog') }}</a>{{ language.tr('filter books by category, price and rating.') }}</li>
        <li>{{ language.tr('Read book pages and reviews, and leave your own review after you log in.') }}</li>
        <li>{{ language.tr('Add books to the cart and the wishlist.') }}</li>
        <li>{{ language.tr('Press “Notify me” on a book that is out of stock and we will tell you when it is back.') }}</li>
        <li>{{ language.tr('Rate the shop on the') }} <a routerLink="/shop-reviews">{{ language.tr('Shop reviews') }}</a> {{ language.tr('page.') }}</li>
      </ul>
    </div>

    <div class="panel">
      <h2>{{ language.tr('Orders, delivery and payment') }}</h2>
      <ul>
        <li>{{ language.tr('After you place an order, the books are reserved for you for 15 minutes. Pay within this time, otherwise the reservation expires.') }}</li>
        <li>{{ language.tr('Delivery costs 1 000 ₸ inside the city limits and 1 500 ₸ outside them.') }}</li>
        <li>{{ language.tr('Payment in this project is simulated: no real money is taken.') }}</li>
        <li>{{ language.tr('Every order has its own secret link. Keep it: anyone who has the link can open the order, and nobody can guess it.') }}</li>
      </ul>
    </div>

    <div class="panel">
      <h2>{{ language.tr('Contact support') }}</h2>
      <p>
        {{ language.tr('Have a problem with an order, a refund or delivery? Open your order and press') }}
        «{{ language.tr('Contact support about this order') }}». {{ language.tr('Choose a topic and describe the problem in a few clear words.') }}
      </p>
      <ul>
        <li>{{ language.tr('Please write politely. Messages with rude words, links or meaningless text are not sent.') }}</li>
        <li>{{ language.tr('Support answers on the same order page. If you are logged in, all your messages and answers are in') }}
          <a routerLink="/account/tickets">{{ language.tr('My requests') }}</a>.</li>
        <li>{{ language.tr('A request can be') }} <b>{{ language.tr('Open') }}</b>{{ language.tr(' (not seen yet), ') }} <b>{{ language.tr('In progress') }}</b>{{ language.tr(' (support is working on it) or ') }} <b>{{ language.tr('Closed') }}</b>{{ language.tr(' (solved).') }}</li>
      </ul>
    </div>

    <div class="panel">
      <h2>{{ language.tr('The team') }}</h2>
      <p>{{ language.tr('The shop was built by the KBTU Online Shop Team: Django REST backend, Angular frontend, PostgreSQL on Render.') }}</p>
    </div>
  </section>`,
})
export class AboutComponent {
  constructor(public language: LanguageService) {}
}
