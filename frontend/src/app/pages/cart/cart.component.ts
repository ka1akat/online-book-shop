// Страница «Корзина»: список книг + форма покупателя.
// Кнопка «Оформить заказ» создаёт заказ в базе (статус reserved, бронь 15 минут).

import { Component, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';
import { CartLine, CustomerForm, SavedAddress } from '../../models';

@Component({
  selector: 'app-cart',
  imports: [DecimalPipe, FormsModule, RouterLink],
  templateUrl: './cart.component.html',
})
export class CartComponent {
  private api = inject(ApiService);
  private router = inject(Router);
  private auth = inject(AuthService);
  cart = inject(CartService);

  customer: CustomerForm = {
    full_name: '', email: '', phone: '', city: '', full_address: '', within_city: null, entrance: '', apartment: '',
    intercom_code: '', floor: '', delivery_method: 'delivery', save_address: false,
  };
  sending = signal(false);
  error = signal('');
  savedAddresses = signal<SavedAddress[]>([]);
  savedAddressMessage = signal('');
  selectedSavedAddressId: number | null = null;

  constructor() {
    const user = this.auth.user();
    if (user) {
      this.customer.full_name = user.full_name;
      this.customer.email = user.email;
      this.loadSavedAddresses();
    }
  }

  emailChanged(): void {
    this.savedAddresses.set([]);
    this.selectedSavedAddressId = null;
    this.customer.saved_address_id = null;
    this.customer.save_address = false;
    this.customer.city = '';
    this.customer.full_address = '';
    this.customer.within_city = null;
    this.customer.entrance = '';
    this.customer.apartment = '';
    this.customer.intercom_code = '';
    this.customer.floor = '';
  }

  loadSavedAddresses(): void {
    this.savedAddressMessage.set('');
    this.selectedSavedAddressId = null;
    this.customer.saved_address_id = null;
    this.customer.save_address = false;
    const token = this.auth.user()?.token;
    if (!token) {
      this.savedAddresses.set([]);
      this.savedAddressMessage.set('Log in with your account to use saved addresses.');
      return;
    }
    if (!this.customer.email.trim()) return;
    this.api.getSavedAddresses(this.customer.email.trim(), token).subscribe({
      next: (addresses) => {
        this.savedAddresses.set(addresses);
        const preferred = addresses.find((address) => address.is_default) ?? addresses[0];
        if (preferred) this.useSavedAddress(preferred.address_id);
        else this.savedAddressMessage.set('No saved addresses yet. You can choose to save the new address below.');
      },
      error: () => {
        this.savedAddresses.set([]);
        this.savedAddressMessage.set('');
      },
    });
  }

  useSavedAddress(id: number | null): void {
    this.selectedSavedAddressId = id;
    this.customer.saved_address_id = id;
    this.customer.save_address = false;
    const address = this.savedAddresses().find((item) => item.address_id === id);
    if (!address) {
      this.customer.city = '';
      this.customer.full_address = '';
      this.customer.within_city = null;
      this.customer.entrance = '';
      this.customer.apartment = '';
      this.customer.intercom_code = '';
      this.customer.floor = '';
      return;
    }
    this.customer.city = address.city;
    this.customer.full_address = address.full_address;
    this.customer.within_city = address.within_city;
    this.customer.entrance = address.entrance;
    this.customer.apartment = address.apartment;
    this.customer.intercom_code = address.intercom_code;
    this.customer.floor = address.floor;
  }

  editAddress(): void {
    this.selectedSavedAddressId = null;
    this.customer.saved_address_id = null;
    this.customer.save_address = false;
  }

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
    this.api.createOrder(this.customer, this.cart.lines(), this.auth.user()?.token).subscribe({
      next: (order) => {
        this.cart.clear();
        this.router.navigate(['/orders', order.public_code]); // переходим к оплате по секретной ссылке
      },
      error: (err) => {
        this.error.set(errorText(err));
        this.sending.set(false);
      },
    });
  }
}
