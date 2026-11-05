// Маршруты: какой адрес в браузере открывает какую страницу.

import { Routes } from '@angular/router';
import { CatalogComponent } from './pages/catalog/catalog.component';
import { CartComponent } from './pages/cart/cart.component';
import { OrderComponent } from './pages/order/order.component';

export const routes: Routes = [
  { path: '', component: CatalogComponent, title: 'Каталог · Online Book Shop' },
  { path: 'cart', component: CartComponent, title: 'Корзина · Online Book Shop' },
  { path: 'orders/:id', component: OrderComponent, title: 'Заказ · Online Book Shop' },
  { path: '**', redirectTo: '' },
];
