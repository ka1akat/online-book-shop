// Маленький компонент «звёзды»: показывает оценку от 1 до 5.
// Используется в каталоге и на странице книги, поэтому вынесен отдельно.

import { Component, computed, inject, input } from '@angular/core';
import { LanguageService } from './services/language.service';

@Component({
  selector: 'app-stars',
  template: `<span class="stars" [attr.aria-label]="label()">
    @for (filled of stars(); track $index) {
      <span [class.star-on]="filled">★</span>
    }
  </span>`,
})
export class StarsComponent {
  language = inject(LanguageService);
  rating = input<number | null>(null);

  // [true, true, true, true, false] для оценки 4.2 (округляем до целого)
  stars = computed(() => {
    const full = Math.round(this.rating() ?? 0);
    return [1, 2, 3, 4, 5].map((n) => n <= full);
  });

  label = computed(() => this.rating() === null ? this.language.tr('No rating yet') : `${this.language.tr('Rated')} ${this.rating()} ${this.language.tr('out of 5')}`);
}
