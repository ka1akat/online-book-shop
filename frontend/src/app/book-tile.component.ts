// Маленькая карточка книги: название, автор, звёзды, цена и кнопка «в корзину».
// Используется на главной (Top rated), на странице рейтинга, в «You may also like» и в «For you».

import { Component, computed, inject, input } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Product } from './models';
import { CartService } from './services/cart.service';
import { StarsComponent } from './stars.component';

@Component({
  selector: 'app-book-tile',
  imports: [DecimalPipe, RouterLink, StarsComponent],
  template: `@let b = book();
    <article class="tile">
      @if (rank()) { <span class="tile-rank">#{{ rank() }}</span> }
      <a class="tile-name" [routerLink]="['/books', b.product_id]">{{ b.product_name }}</a>
      <span class="muted small">{{ b.author }}</span>
      <span class="tile-rating">
        <app-stars [rating]="b.avg_rating" />
        @if (b.avg_rating !== null) {
          <strong>{{ b.avg_rating | number: '1.1-1' }}</strong>
          <span class="muted small">({{ b.review_count }} {{ b.review_count === 1 ? 'review' : 'reviews' }})</span>
        } @else {
          <span class="muted small">no reviews yet</span>
        }
      </span>
      <span class="muted small">{{ b.category_name }}</span>
      <div class="tile-bottom">
        <strong>{{ b.price | number: '1.0-0' }} ₸</strong>
        @if (b.available > 0) {
          <button class="btn btn-small" type="button" [disabled]="!canAdd()" (click)="cart.add(b)">
            {{ inCart() > 0 ? 'In cart: ' + inCart() : 'Add to cart' }}
          </button>
        } @else {
          <a class="btn btn-secondary btn-small" [routerLink]="['/books', b.product_id]">Notify me</a>
        }
      </div>
    </article>`,
})
export class BookTileComponent {
  book = input.required<Product>();
  rank = input<number | null>(null); // место в рейтинге (#1, #2...) — только на странице Top rating

  cart = inject(CartService);
  inCart = computed(() => this.cart.quantityOf(this.book().product_id));
  canAdd = computed(() => this.inCart() < this.book().available);
}
