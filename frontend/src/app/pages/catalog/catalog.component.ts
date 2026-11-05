import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { CartService } from '../../services/cart.service';
import { Product } from '../../models';

@Component({
  selector: 'app-catalog',
  imports: [DecimalPipe, RouterLink],
  templateUrl: './catalog.component.html',
})
export class CatalogComponent implements OnInit {
  private api = inject(ApiService);
  cart = inject(CartService);

  products = signal<Product[]>([]);
  loading = signal(true);
  error = signal('');

  selectedGenre = signal('');

  genres = computed(() => {
    const all = this.products()
      .map((p) => p.genre)
      .filter((g): g is string => !!g);
    return [...new Set(all)].sort();
  });

  filteredProducts = computed(() => {
    const genre = this.selectedGenre();
    return genre
      ? this.products().filter((p) => p.genre === genre)
      : this.products();
  });

  // Цвет «обложки» зависит от жанра — просто для красоты
  private palette = ['#2f5d50', '#8a3b2e', '#3b4a7a', '#6b4f2a', '#5a3d6e', '#2d6170'];

  ngOnInit(): void {
    this.api.getProducts().subscribe({
      next: (list) => {
        this.products.set(list);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(errorText(err));
        this.loading.set(false);
      },
    });
  }

  coverColor(p: Product): string {
    const n = [...p.product_id].reduce((s, ch) => s * 31 + ch.charCodeAt(0), 7);
    return this.palette[n % this.palette.length];
  }

  canAdd(p: Product): boolean {
    return this.cart.quantityOf(p.product_id) < p.available;
  }
}