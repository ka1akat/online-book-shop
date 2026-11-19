// Wishlist: книги, которые покупатель отложил кнопкой ♡ на странице книги.

import { Component, OnInit, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AccountService } from '../../services/account.service';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';
import { Product } from '../../models';
import { StarsComponent } from '../../stars.component';

@Component({
  selector: 'app-wishlist',
  imports: [DecimalPipe, RouterLink, StarsComponent],
  template: `<section class="page">
    <header class="page-head">
      <h1>Wishlist</h1>
      <p class="muted">Books you saved for later.</p>
    </header>

    @if (!auth.user()) {
      <p class="muted"><a routerLink="/login">Log in</a> to save books to your wishlist.</p>
    } @else {
      @for (b of account.wishlist(); track b.product_id) {
        <article class="panel wish-row">
          <div>
            <a class="book-card-name" [routerLink]="['/books', b.product_id]">{{ b.product_name }}</a>
            <p class="muted small">by {{ b.author }}</p>
            <app-stars [rating]="b.avg_rating" />
          </div>
          <div class="wish-row-right">
            <strong>{{ b.price | number: '1.0-0' }} ₸</strong>
            @if (b.available > 0) {
              <button class="btn" type="button" [disabled]="!canAdd(b)" (click)="cart.add(b)">
                {{ cart.quantityOf(b.product_id) > 0 ? 'In cart: ' + cart.quantityOf(b.product_id) : 'Add to cart' }}
              </button>
            } @else {
              <a class="btn btn-secondary" [routerLink]="['/books', b.product_id]">Out of stock · Notify me</a>
            }
            <button class="wishlist-btn wishlist-on" type="button" (click)="account.toggleWishlist(b).subscribe()">
              ♥ Remove
            </button>
          </div>
        </article>
      } @empty {
        <div class="empty">
          <p class="muted">Your wishlist is empty. Press ♡ on a book page to save it here.</p>
          <a class="btn" routerLink="/catalog">Browse catalog</a>
        </div>
      }
    }
  </section>`,
})
export class WishlistComponent implements OnInit {
  auth = inject(AuthService);
  account = inject(AccountService);
  cart = inject(CartService);

  ngOnInit(): void {
    this.account.refresh();
  }

  canAdd(p: Product): boolean {
    return this.cart.quantityOf(p.product_id) < p.available;
  }
}
