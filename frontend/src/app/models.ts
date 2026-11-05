// Интерфейсы описывают форму JSON, который присылает Django.
// Названия полей те же, что в таблицах Task 9.

export interface Product {
  product_id: string;      // P-1001
  product_name: string;
  author: string;
  genre: string;
  price: string;           // Django присылает DECIMAL как строку: "6500.00"
  stock_quantity: number;  // сколько на складе
  available: number;       // сколько можно купить (склад минус брони)
  last_updated: string;
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
}

export interface CartLine {
  product: Product;
  quantity: number;
}

export interface CustomerForm {
  full_name: string;
  email: string;
  phone: string;
}
