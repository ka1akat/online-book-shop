// Страница «Корзина»: список книг + форма покупателя.
// Кнопка «Оформить заказ» создаёт заказ в базе (статус reserved, бронь 15 минут).

import { Component, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { CartService } from '../../services/cart.service';
import { CartLine, CustomerForm } from '../../models';

@Component({
  selector: 'app-cart',
  imports: [DecimalPipe, FormsModule, RouterLink],
  templateUrl: './cart.component.html',
})
export class CartComponent {
  private api = inject(ApiService);
  private router = inject(Router);
  cart = inject(CartService);

  customer: CustomerForm = {
    full_name: '', email: '', phone: '', city: '', full_address: '', within_city: null, entrance: '', apartment: '',
    intercom_code: '', floor: '', delivery_method: 'delivery',
  };
  sending = signal(false);
  error = signal('');

  change(line: CartLine, delta: number): void {
    const next = Math.min(line.quantity + delta, line.product.available);
    this.cart.setQuantity(line.product, next);
  }

  deliveryFee(): number {
    return this.customer.within_city ? 1000 : 1500;
  }

  checkout(): void {
    this.sending.set(true);
    this.error.set('');
    this.api.createOrder(this.customer, this.cart.lines()).subscribe({
      next: (order) => {
        this.cart.clear();
        this.router.navigate(['/orders', order.order_id]); // переходим к оплате
      },
      error: (err) => {
        this.error.set(errorText(err));
        this.sending.set(false);
      },
    });
  }
}
