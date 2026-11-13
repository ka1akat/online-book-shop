// Маленький компонент «звёзды»: показывает оценку от 1 до 5.
// Используется в каталоге и на странице книги, поэтому вынесен отдельно.

import { Component, computed, input } from '@angular/core';

@Component({
  selector: 'app-stars',
  template: `<span class="stars" [attr.aria-label]="label()">
    @for (filled of stars(); track $index) {
      <span [class.star-on]="filled">★</span>
    }
  </span>`,
})
export class StarsComponent {
  rating = input<number | null>(null);

  // [true, true, true, true, false] для оценки 4.2 (округляем до целого)
  stars = computed(() => {
    const full = Math.round(this.rating() ?? 0);
    return [1, 2, 3, 4, 5].map((n) => n <= full);
  });

  label = computed(() => (this.rating() === null ? 'No rating yet' : `Rated ${this.rating()} out of 5`));
}
