// Маршруты: какой адрес в браузере открывает какую страницу.

import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { CatalogComponent } from './pages/catalog/catalog.component';
import { CartComponent } from './pages/cart/cart.component';
import { OrderComponent } from './pages/order/order.component';
import { RegisterComponent } from './pages/register/register.component';
import { LoginComponent } from './pages/login/login.component';
import { BookComponent } from './pages/book/book.component';
import { ShopReviewsComponent } from './pages/shop-reviews/shop-reviews.component';
import { MyOrdersComponent } from './pages/my-orders/my-orders.component';
import { WishlistComponent } from './pages/wishlist/wishlist.component';
import { NotificationsComponent } from './pages/notifications/notifications.component';
import { AccountComponent } from './pages/account/account.component';
import { AccountOverviewComponent } from './pages/account/account-overview.component';
import { accountGuard, toAccount } from './auth.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent, title: 'Online Book Shop' },
  { path: 'catalog', component: CatalogComponent, title: 'Catalog · Online Book Shop' },
  { path: 'books/:id', component: BookComponent, title: 'Book · Online Book Shop' },
  { path: 'shop-reviews', component: ShopReviewsComponent, title: 'Shop reviews · Online Book Shop' },
  // Корзина без входа — отдельная страница; у вошедшего — раздел личного кабинета
  { path: 'cart', component: CartComponent, canActivate: [toAccount('cart')], title: 'Cart · Online Book Shop' },

  // Личный кабинет: /account, /account/cart, /account/orders, /account/wishlist, /account/notifications
  {
    path: 'account',
    component: AccountComponent,
    canActivate: [accountGuard],
    children: [
      { path: '', component: AccountOverviewComponent, title: 'My account · Online Book Shop' },
      { path: 'cart', component: CartComponent, title: 'Cart · Online Book Shop' },
      { path: 'orders', component: MyOrdersComponent, title: 'My orders · Online Book Shop' },
      { path: 'wishlist', component: WishlistComponent, title: 'Wishlist · Online Book Shop' },
      { path: 'notifications', component: NotificationsComponent, title: 'Notifications · Online Book Shop' },
    ],
  },
  // Старые адреса страниц ведут в кабинет
  { path: 'my-orders', redirectTo: 'account/orders' },
  { path: 'wishlist', redirectTo: 'account/wishlist' },
  { path: 'notifications', redirectTo: 'account/notifications' },
  { path: 'orders/:id', component: OrderComponent, title: 'Order · Online Book Shop' },
  { path: 'register', component: RegisterComponent, title: 'Sign up · Online Book Shop' },
  { path: 'login', component: LoginComponent, title: 'Log in · Online Book Shop' },
  { path: '**', redirectTo: '' },
];
