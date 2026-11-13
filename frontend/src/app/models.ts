// Интерфейсы описывают форму JSON, который присылает Django.
// Названия полей те же, что в таблицах Task 9.

export interface Product {
  product_id: string;      // P-1001
  product_name: string;
  author: string;
  genre: string;
  category_id: number | null;
  category_name: string | null;
  price: string;           // Django присылает DECIMAL как строку: "6500.00"
  stock_quantity: number;  // сколько на складе
  available: number;       // сколько можно купить (склад минус брони)
  last_updated: string;
  avg_rating: number | null; // средняя оценка 1–5, null — отзывов ещё нет
  review_count: number;      // сколько отзывов
}

// Фильтры каталога. Пустое значение (null или '') = фильтр не применяется.
export interface ProductFilters {
  category_id: number | null;
  min_price: number | null;
  max_price: number | null;
  min_rating: number | null;
  ordering: '' | 'price' | '-price' | '-rating';
}

export interface Review {
  review_id: number;
  customer_name: string;
  rating: number;      // 1–5
  comment: string;
  created_at: string;
  updated_at: string;
  is_mine: boolean;    // true — этот отзыв написал тот, кто сейчас вошёл
}

export interface Category {
  category_id: number;
  category_name: string;
  description: string;
}

export interface DeliveryAddress {
  city: string;
  full_address: string;
  within_city: boolean;
  entrance: string;
  apartment: string;
  intercom_code: string;
  floor: string;
}

export interface OrderItem {
  order_item_id: number;
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: string;
}

export interface Payment {
  payment_id: number;
  transaction_id: string;
  amount: string;
  status: 'success' | 'failed' | 'refunded';
  paid_at: string;
}

export interface Order {
  order_id: number;
  customer_id: number;
  customer_name: string;
  order_date: string;
  status: 'reserved' | 'paid' | 'cancelled';
  reserved_until: string;
  total: string;
  items: OrderItem[];
  payments: Payment[];
  delivery_method: 'delivery';
  address: DeliveryAddress | null;
  delivery_fee: number;
}

export interface CartLine {
  product: Product;
  quantity: number;
}

export interface CustomerForm {
  full_name: string;
  email: string;
  phone: string;
  city: string;
  full_address: string;
  within_city: boolean | null;
  entrance: string;
  apartment: string;
  intercom_code: string;
  floor: string;
  delivery_method: 'delivery';
}
