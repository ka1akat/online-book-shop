import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { StoreReview } from '../../models';
import { StarsComponent } from '../../stars.component';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-shop-reviews',
  imports: [DatePipe, FormsModule, RouterLink, StarsComponent],
  template: `<section class="page shop-reviews-page">
    <a class="back-link" routerLink="/">← {{ language.tr('Back to shop') }}</a>
    <header class="page-head">
      <h1>{{ language.tr('Reviews about our shop') }}</h1>
      <p class="muted">{{ language.tr('Share your experience with our book shop.') }}</p>
    </header>

    <div class="reviews">
      @if (auth.user()) {
        <form class="review-form" (ngSubmit)="submit()">
          <h3>{{ language.tr(myReview() ? 'Edit your review' : 'Write a shop review') }}</h3>
          <div class="star-picker" role="radiogroup" [attr.aria-label]="language.tr('Your rating')" (mouseleave)="hoverRating.set(0)">
            @for (n of [1, 2, 3, 4, 5]; track n) {
              <button type="button" role="radio" [attr.aria-checked]="rating() === n"
                [attr.aria-label]="n + ' ' + language.tr('stars')" [class.star-on]="n <= (hoverRating() || rating())"
                (mouseenter)="hoverRating.set(n)" (click)="rating.set(n)">★</button>
            }
          </div>
          <textarea name="comment" rows="3" maxlength="1000"
            [placeholder]="language.tr('Tell us about your experience (optional)')" [(ngModel)]="comment"></textarea>
          @if (formError()) { <p class="alert alert-error">{{ language.tr(formError()) }}</p> }
          @if (formDone()) { <p class="alert alert-ok">{{ language.tr('Thank you! Your review is published.') }}</p> }
          <button class="btn" type="submit" [disabled]="sending()">
            {{ language.tr(sending() ? 'Sending…' : myReview() ? 'Update review' : 'Publish review') }}
          </button>
        </form>
      } @else {
        <p class="review-login muted"><a routerLink="/login">{{ language.tr('Log in') }}</a> {{ language.tr('to rate our shop and leave a review.') }}</p>
      }

      <h2>{{ language.tr('Customer reviews') }}</h2>
      @if (loading()) {
        <p class="muted">{{ language.tr('Loading…') }}</p>
      } @else if (loadError()) {
        <p class="alert alert-error">{{ language.tr(loadError()) }}</p>
      } @else {
        @for (review of reviews(); track review.review_id) {
          <article class="review">
            <div class="review-head">
              <strong>{{ review.customer_name }}</strong>
              <app-stars [rating]="review.rating" />
              <span class="muted small">{{ review.created_at | date: 'd MMM y':undefined:language.dateLocale() }}</span>
            </div>
            @if (review.comment) { <p>{{ review.comment }}</p> }
          </article>
        } @empty {
          <p class="muted">{{ language.tr('Be the first to review our shop.') }}</p>
        }
      }
    </div>
  </section>`,
})
export class ShopReviewsComponent implements OnInit {
  private api = inject(ApiService);
  auth = inject(AuthService);
  language = inject(LanguageService);

  reviews = signal<StoreReview[]>([]);
  loading = signal(true);
  loadError = signal('');
  rating = signal(0);
  hoverRating = signal(0);
  comment = '';
  sending = signal(false);
  formError = signal('');
  formDone = signal(false);
  myReview = computed(() => this.auth.user() ? this.reviews().find((review) => review.is_mine) ?? null : null);

  ngOnInit(): void {
    this.loadReviews();
  }

  loadReviews(): void {
    this.api.getStoreReviews(this.auth.user()?.token).subscribe({
      next: (reviews) => {
        this.reviews.set(reviews);
        const mine = reviews.find((review) => review.is_mine);
        if (mine) {
          this.rating.set(mine.rating);
          this.comment = mine.comment;
        }
        this.loading.set(false);
      },
      error: (err) => {
        this.loadError.set(this.language.tr(errorText(err)));
        this.loading.set(false);
      },
    });
  }

  submit(): void {
    const token = this.auth.user()?.token;
    if (!token) {
      this.formError.set(this.language.tr('Please log in to leave a shop review.'));
      return;
    }
    if (this.rating() === 0) {
      this.formError.set(this.language.tr('Choose from 1 to 5 stars.'));
      return;
    }
    this.sending.set(true);
    this.formError.set('');
    this.formDone.set(false);
    this.api.addStoreReview(this.rating(), this.comment, token).subscribe({
      next: () => {
        this.sending.set(false);
        this.formDone.set(true);
        this.loadReviews();
      },
      error: (err) => {
        this.formError.set(this.language.tr(errorText(err)));
        this.sending.set(false);
      },
    });
  }
}
