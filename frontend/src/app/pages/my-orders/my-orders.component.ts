// Мои заказы: все заказы покупателя, который вошёл. Django определяет его по токену входа.

import { Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { Order } from '../../models';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-my-orders',
  imports: [DatePipe, DecimalPipe, RouterLink],
  template: `<section class="page">
    <header class="page-head">
      <h1>{{ language.tr('My orders') }}</h1>
      <p class="muted">{{ language.tr('All orders made with your account e-mail.') }}</p>
    </header>

    @if (!auth.user()) {
      <p class="muted"><a routerLink="/login">{{ language.tr('Log in') }}</a> {{ language.tr('to see your orders.') }}</p>
    } @else if (loading()) {
      <p class="muted">{{ language.tr('Loading…') }}</p>
    } @else if (error()) {
      <p class="alert alert-error">{{ language.tr(error()) }}</p>
    } @else {
      @for (o of orders(); track o.order_id) {
        <a class="panel order-row" [routerLink]="['/orders', o.public_code]">
          <div>
            <strong>{{ language.tr('Order #') }}{{ o.order_id }}</strong>
            <p class="muted small">
              {{ o.order_date | date: 'dd.MM.yyyy HH:mm':undefined:language.dateLocale() }} ·
              {{ itemCount(o) }} {{ language.tr(itemCount(o) === 1 ? 'book' : 'books') }}:
              {{ titles(o) }}
            </p>
          </div>
          <div class="order-row-right">
            <span class="badge badge-{{ o.status }}">
              @switch (o.status) {
                @case ('reserved') { {{ language.tr('Reserved') }} }
                @case ('paid') { {{ language.tr('Paid') }} }
                @case ('cancelled') { {{ language.tr('Cancelled') }} }
              }
            </span>
            <strong>{{ o.total | number: '1.0-0' }} ₸</strong>
          </div>
        </a>
      } @empty {
        <div class="empty">
          <p class="muted">{{ language.tr('You have no orders yet.') }}</p>
          <a class="btn" routerLink="/catalog">{{ language.tr('Browse catalog') }}</a>
        </div>
      }
    }
  </section>`,
})
export class MyOrdersComponent implements OnInit {
  private api = inject(ApiService);
  auth = inject(AuthService);
  language = inject(LanguageService);

  orders = signal<Order[]>([]);
  loading = signal(true);
  error = signal('');

  ngOnInit(): void {
    const token = this.auth.user()?.token;
    if (!token) {
      this.loading.set(false);
      return;
    }
    this.api.getMyOrders(token).subscribe({
      next: (list) => { this.orders.set(list); this.loading.set(false); },
      error: (err) => { this.error.set(this.language.tr(errorText(err))); this.loading.set(false); },
    });
  }

  itemCount(order: Order): number {
    return order.items.reduce((sum, item) => sum + item.quantity, 0);
  }

  titles(order: Order): string {
    return order.items.map((item) => this.language.bookTitle(item.product_name)).join(', ');
  }
}
