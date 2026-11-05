// Маршруты: какой адрес в браузере открывает какую страницу.

import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { CatalogComponent } from './pages/catalog/catalog.component';
import { CartComponent } from './pages/cart/cart.component';
import { OrderComponent } from './pages/order/order.component';
import { RegisterComponent } from './pages/register/register.component';
import { LoginComponent } from './pages/login/login.component';

export const routes: Routes = [
  { path: '', component: HomeComponent, title: 'Online Book Shop' },
  { path: 'catalog', component: CatalogComponent, title: 'Catalog · Online Book Shop' },
  { path: 'cart', component: CartComponent, title: 'Cart · Online Book Shop' },
  { path: 'orders/:id', component: OrderComponent, title: 'Order · Online Book Shop' },
  { path: 'register', component: RegisterComponent, title: 'Sign up · Online Book Shop' },
  { path: 'login', component: LoginComponent, title: 'Log in · Online Book Shop' },
  { path: '**', redirectTo: '' },
];