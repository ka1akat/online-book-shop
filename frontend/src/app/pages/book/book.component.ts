// Страница одной книги: информация, средняя оценка, все отзывы и форма своего отзыва.

import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AccountService } from '../../services/account.service';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';
import { Product, Review } from '../../models';
import { StarsComponent } from '../../stars.component';

@Component({
  selector: 'app-book',
  imports: [DatePipe, DecimalPipe, FormsModule, RouterLink, StarsComponent],
  templateUrl: './book.component.html',
})
export class BookComponent implements OnInit {
  private api = inject(ApiService);
  private route = inject(ActivatedRoute);
  auth = inject(AuthService);
  cart = inject(CartService);
  account = inject(AccountService);

  productId = '';
  book = signal<Product | null>(null);
  reviews = signal<Review[]>([]);
  loading = signal(true);
  error = signal('');

  // Форма отзыва
  rating = signal(0);        // 0 = ещё не выбрали звёзды
  hoverRating = signal(0);   // подсветка звёзд под мышкой
  comment = '';
  sending = signal(false);
  formError = signal('');
  formDone = signal('');

  // «Notify me»: книги нет на складе — покупатель встаёт в лист ожидания (FR-07)
  notifyEmail = '';
  notifySending = signal(false);
  notifyError = signal('');
  guestNotified = signal(false); // гость оставил email — показываем «мы сообщим»

  // Избранное
  wishlistBusy = signal(false);
  wishlistError = signal('');

  // Уже есть мой отзыв? Тогда форма работает как «изменить отзыв»
  myReview = computed(() => (this.auth.user() ? this.reviews().find((r) => r.is_mine) ?? null : null));

  ngOnInit(): void {
    this.productId = this.route.snapshot.paramMap.get('id') ?? '';
    this.api.getProduct(this.productId).subscribe({
      next: (book) => { this.book.set(book); this.loading.set(false); },
      error: (err) => { this.error.set(errorText(err)); this.loading.set(false); },
    });
    this.loadReviews();
  }

  loadReviews(): void {
    this.api.getReviews(this.productId, this.auth.user()?.token).subscribe({
      next: (list) => {
        this.reviews.set(list);
        // если отзыв уже есть — заполняем форму им, чтобы было удобно исправить
        const mine = list.find((r) => r.is_mine);
        if (mine && this.rating() === 0) {
          this.rating.set(mine.rating);
          this.comment = mine.comment;
        }
      },
    });
  }

  canAdd(p: Product): boolean {
    return this.cart.quantityOf(p.product_id) < p.available;
  }

  submit(): void {
    const token = this.auth.user()?.token;
    if (!token) {
      // Пользователь вошёл до того, как появились токены: нужно войти заново
      this.formError.set('Please log out and log in again to leave a review.');
      return;
    }
    if (this.rating() === 0) {
      this.formError.set('Choose from 1 to 5 stars.');
      return;
    }
    this.sending.set(true);
    this.formError.set('');
    this.formDone.set('');
    this.api.addReview(this.productId, this.rating(), this.comment, token).subscribe({
      next: () => {
        this.sending.set(false);
        this.formDone.set('Thank you! Your review is published.');
        this.loadReviews();
        // средняя оценка изменилась — берём книгу заново
        this.api.getProduct(this.productId).subscribe({ next: (book) => this.book.set(book) });
      },
      error: (err) => {
        this.formError.set(errorText(err));
        this.sending.set(false);
      },
    });
  }

  notifyMe(): void {
    const loggedIn = !!this.auth.user()?.token;
    if (!loggedIn && !this.notifyEmail.trim()) {
      this.notifyError.set('Enter your e-mail and we will let you know.');
      return;
    }
    this.notifySending.set(true);
    this.notifyError.set('');
    this.account.notifyMe(this.productId, this.notifyEmail.trim()).subscribe({
      next: () => {
        this.notifySending.set(false);
        if (!loggedIn) this.guestNotified.set(true);
      },
      error: (err) => {
        this.notifySending.set(false);
        this.notifyError.set(errorText(err));
      },
    });
  }

  stopWaiting(): void {
    this.notifySending.set(true);
    this.account.stopWaiting(this.productId).subscribe({
      next: () => this.notifySending.set(false),
      error: (err) => {
        this.notifySending.set(false);
        this.notifyError.set(errorText(err));
      },
    });
  }

  toggleWishlist(book: Product): void {
    this.wishlistBusy.set(true);
    this.wishlistError.set('');
    this.account.toggleWishlist(book).subscribe({
      next: () => this.wishlistBusy.set(false),
      error: (err) => {
        this.wishlistBusy.set(false);
        this.wishlistError.set(errorText(err));
      },
    });
  }
}
