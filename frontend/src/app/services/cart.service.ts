// CartService — корзина. Хранится в браузере (не в базе),
// потому что заказ в базе появляется только после кнопки «Оформить».

import { Injectable, computed, signal } from '@angular/core';
import { CartLine, Product } from '../models';

const STORAGE_KEY = 'bookshop-cart';

@Injectable({ providedIn: 'root' })
export class CartService {
  // signal — «живая» переменная: когда она меняется, страница обновляется сама
  readonly lines = signal<CartLine[]>(this.load());

  readonly count = computed(() => this.lines().reduce((sum, l) => sum + l.quantity, 0));
  readonly total = computed(() =>
    this.lines().reduce((sum, l) => sum + Number(l.product.price) * l.quantity, 0),
  );

  quantityOf(productId: string): number {
    return this.lines().find((l) => l.product.product_id === productId)?.quantity ?? 0;
  }

  add(product: Product): void {
    const current = this.quantityOf(product.product_id);
    if (current >= product.available) return; // нельзя положить больше, чем есть
    this.setQuantity(product, current + 1);
  }

  setQuantity(product: Product, quantity: number): void {
    const others = this.lines().filter((l) => l.product.product_id !== product.product_id);
    const next = quantity > 0 ? [...others, { product, quantity }] : others;
    next.sort((a, b) => a.product.product_id.localeCompare(b.product.product_id));
    this.lines.set(next);
    this.save();
  }

  clear(): void {
    this.lines.set([]);
    this.save();
  }

  private load(): CartLine[] {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
    } catch {
      return [];
    }
  }

  private save(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.lines()));
    } catch {
      /* браузер запретил хранилище — корзина просто не запомнится */
    }
  }
}
