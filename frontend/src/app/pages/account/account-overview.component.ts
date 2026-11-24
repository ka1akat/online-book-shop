// Главная страница личного кабинета: короткая сводка по всем разделам.

import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { AccountService } from '../../services/account.service';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';

@Component({
  selector: 'app-account-overview',
  imports: [RouterLink],
  template: `<section>
    <header class="page-head">
      <h1>Hello, {{ auth.user()?.full_name }}!</h1>
      <p class="muted">Your orders, saved books and notifications in one place.</p>
    </header>

    <div class="account-cards">
      <a class="panel account-card" routerLink="/account/cart">
        <span class="account-card-num">{{ cart.count() }}</span>
        <span>{{ cart.count() === 1 ? 'book' : 'books' }} in cart</span>
      </a>
      <a class="panel account-card" routerLink="/account/orders">
        <span class="account-card-num">{{ ordersCount() ?? '…' }}</span>
        <span>{{ ordersCount() === 1 ? 'order' : 'orders' }}</span>
      </a>
      <a class="panel account-card" routerLink="/account/tickets">
        <span class="account-card-num">{{ ticketsCount() ?? '…' }}</span>
        <span>{{ ticketsCount() === 1 ? 'support request' : 'support requests' }}</span>
      </a>
      <a class="panel account-card" routerLink="/account/wishlist">
        <span class="account-card-num">{{ account.wishlist().length }}</span>
        <span>in wishlist</span>
      </a>
      <a class="panel account-card" routerLink="/account/notifications">
        <span class="account-card-num">{{ waitingCount() }}</span>
        <span>on waiting list</span>
        @if (account.unreadCount() > 0) {
          <span class="badge badge-paid">{{ account.unreadCount() }} back in stock</span>
        }
      </a>
    </div>
  </section>`,
})
export class AccountOverviewComponent implements OnInit {
  private api = inject(ApiService);
  auth = inject(AuthService);
  account = inject(AccountService);
  cart = inject(CartService);

  ordersCount = signal<number | null>(null);
  ticketsCount = signal<number | null>(null);
  waitingCount = computed(() => this.account.notifications().filter((n) => !n.notified).length);

  ngOnInit(): void {
    this.account.refresh();
    const token = this.auth.user()?.token;
    if (token) {
      this.api.getMyOrders(token).subscribe({ next: (list) => this.ordersCount.set(list.length), error: () => {} });
      this.api.getMyTickets(token).subscribe({ next: (list) => this.ticketsCount.set(list.length), error: () => {} });
    }
  }
}
