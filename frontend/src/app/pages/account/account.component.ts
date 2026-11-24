// Личный кабинет: слева профиль и меню разделов, справа выбранный раздел.
// Разделы — это дочерние маршруты /account/... (см. app.routes.ts), они показываются в <router-outlet>.

import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AccountService } from '../../services/account.service';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';

@Component({
  selector: 'app-account',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `@if (auth.user(); as user) {
    <div class="account">
      <aside class="account-side panel">
        <div class="account-user">
          <span class="account-avatar">{{ initial(user.full_name || user.email) }}</span>
          <div>
            <strong>{{ user.full_name }}</strong>
            <p class="muted small">{{ user.email }}</p>
          </div>
        </div>
        <nav class="account-nav" aria-label="My account">
          <a routerLink="/account" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Profile</a>
          <a routerLink="/account/cart" routerLinkActive="active">
            Cart @if (cart.count() > 0) { <span class="cart-count">{{ cart.count() }}</span> }
          </a>
          <a routerLink="/account/orders" routerLinkActive="active">My orders</a>
          <a routerLink="/account/tickets" routerLinkActive="active">My requests</a>
          <a routerLink="/account/wishlist" routerLinkActive="active">
            Wishlist @if (account.wishlist().length > 0) { <span class="cart-count">{{ account.wishlist().length }}</span> }
          </a>
          <a routerLink="/account/notifications" routerLinkActive="active">
            Notifications @if (account.unreadCount() > 0) { <span class="cart-count">{{ account.unreadCount() }}</span> }
          </a>
        </nav>
        <button class="btn btn-secondary btn-wide" type="button" (click)="logout()">Log out</button>
      </aside>

      <div class="account-main">
        <router-outlet />
      </div>
    </div>
  }`,
})
export class AccountComponent {
  auth = inject(AuthService);
  account = inject(AccountService);
  cart = inject(CartService);
  private router = inject(Router);

  initial(name: string): string {
    return name.trim().charAt(0).toUpperCase();
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}
