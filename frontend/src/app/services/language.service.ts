import { Injectable, inject, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { RouterStateSnapshot, TitleStrategy } from '@angular/router';
import { registerLocaleData } from '@angular/common';
import localeRu from '@angular/common/locales/ru';
import { CATALOG_AUTHORS, CATALOG_BOOK_TITLES, CATALOG_PHRASES } from './catalog-translations';

registerLocaleData(localeRu);

export type ShopLanguage = 'en' | 'ru' | 'kk';

const translations: Record<ShopLanguage, Record<string, string>> = {
  en: {
    'nav.catalog': 'Catalog', 'nav.reviews': 'Shop reviews', 'nav.about': 'About us', 'nav.cart': 'Cart', 'nav.login': 'Log in', 'nav.language': 'Language',
    'home.title': 'What book are you looking for?', 'home.description': 'Novels, fairy tales, fantasy and self-development books. Browse the catalog and order online.', 'home.signup': 'Sign up', 'home.browse': 'Browse catalog',
    'catalog.title': 'Our books', 'catalog.subtitle': 'Browse by category and find your next book', 'catalog.all': 'All',
    'catalog.priceFrom': 'Price from, ₸', 'catalog.priceTo': 'Price to, ₸', 'catalog.any': 'Any', 'catalog.rating': 'Rating', 'catalog.anyRating': 'Any rating',
    'catalog.andUp': 'and up', 'catalog.sort': 'Sort by', 'catalog.default': 'Default', 'catalog.lowHigh': 'Price: low to high', 'catalog.highLow': 'Price: high to low',
    'catalog.topRated': 'Top rated', 'catalog.reset': 'Reset', 'catalog.reviews': 'reviews', 'catalog.noReviews': 'No reviews yet', 'catalog.outOfStock': 'Out of stock', 'catalog.inStock': 'in stock', 'catalog.only': 'Only', 'catalog.left': 'left',
    'catalog.noMatch': 'No books match these filters.', 'catalog.byReviews': "by our customers' reviews",
  },
  ru: {
    'nav.catalog': 'Каталог', 'nav.reviews': 'Отзывы о магазине', 'nav.about': 'О нас', 'nav.cart': 'Корзина', 'nav.login': 'Войти', 'nav.language': 'Язык',
    'home.title': 'Какую книгу вы ищете?', 'home.description': 'Романы, сказки, фантастика и книги по саморазвитию. Смотрите каталог и заказывайте онлайн.', 'home.signup': 'Регистрация', 'home.browse': 'Открыть каталог',
    'catalog.title': 'Наши книги', 'catalog.subtitle': 'Выберите категорию и найдите следующую книгу', 'catalog.all': 'Все',
    'catalog.priceFrom': 'Цена от, ₸', 'catalog.priceTo': 'Цена до, ₸', 'catalog.any': 'любая', 'catalog.rating': 'Рейтинг', 'catalog.anyRating': 'Любой рейтинг',
    'catalog.andUp': 'и выше', 'catalog.sort': 'Сортировка', 'catalog.default': 'По умолчанию', 'catalog.lowHigh': 'Сначала дешевле', 'catalog.highLow': 'Сначала дороже',
    'catalog.topRated': 'Лучший рейтинг', 'catalog.reset': 'Сбросить', 'catalog.reviews': 'отзывов', 'catalog.noReviews': 'Пока нет отзывов', 'catalog.outOfStock': 'Нет в наличии', 'catalog.inStock': 'в наличии', 'catalog.only': 'Остаток', 'catalog.left': '',
    'catalog.noMatch': 'По этим фильтрам книги не найдены.', 'catalog.byReviews': 'по отзывам покупателей',
  },
  kk: {
    'nav.catalog': 'Каталог', 'nav.reviews': 'Дүкен туралы пікірлер', 'nav.about': 'Біз туралы', 'nav.cart': 'Себет', 'nav.login': 'Кіру', 'nav.language': 'Тіл',
    'home.title': 'Қандай кітап іздеп жүрсіз?', 'home.description': 'Романдар, ертегілер, қиял-ғажайып және өзін-өзі дамыту кітаптары. Каталогты қарап, онлайн тапсырыс беріңіз.', 'home.signup': 'Тіркелу', 'home.browse': 'Каталогты ашу',
    'catalog.title': 'Біздің кітаптар', 'catalog.subtitle': 'Санатты таңдап, келесі кітабыңызды табыңыз', 'catalog.all': 'Барлығы',
    'catalog.priceFrom': 'Бағасы, бастап ₸', 'catalog.priceTo': 'Бағасы, дейін ₸', 'catalog.any': 'кез келген', 'catalog.rating': 'Рейтингі', 'catalog.anyRating': 'Кез келген рейтинг',
    'catalog.andUp': 'және жоғары', 'catalog.sort': 'Сұрыптау', 'catalog.default': 'Әдепкі бойынша', 'catalog.lowHigh': 'Бағасы: арзандан қымбатқа', 'catalog.highLow': 'Бағасы: қымбаттан арзанға',
    'catalog.topRated': 'Үздік рейтинг', 'catalog.reset': 'Тазарту', 'catalog.reviews': 'пікір', 'catalog.noReviews': 'Әзірге пікір жоқ', 'catalog.outOfStock': 'Қоймада жоқ', 'catalog.inStock': 'қоймада бар', 'catalog.only': 'Қалды', 'catalog.left': '',
    'catalog.noMatch': 'Бұл сүзгілер бойынша кітап табылмады.', 'catalog.byReviews': 'оқырмандардың пікірлері бойынша',
  },
};

const bookTitles: Record<string, Record<ShopLanguage, string>> = {
  'Atomic Habits': { en: 'Atomic Habits', ru: 'Атомные привычки', kk: 'Атомдық әдеттер' },
  'The Little Prince': { en: 'The Little Prince', ru: 'Маленький принц', kk: 'Кішкентай ханзада' },
  'Abai Zholy': { en: 'Abai Zholy', ru: 'Путь Абая', kk: 'Абай жолы' },
  '1984': { en: '1984', ru: '1984', kk: '1984' },
  'Harry Potter 1': { en: 'Harry Potter and the Sorcerer’s Stone', ru: 'Гарри Поттер и философский камень', kk: 'Гарри Поттер және пәлсапа тас' },
  'Harry Potter and the Sorcerer\'s Stone': { en: 'Harry Potter and the Sorcerer’s Stone', ru: 'Гарри Поттер и философский камень', kk: 'Гарри Поттер және пәлсапа тас' },
};

const authorNames: Record<string, Record<ShopLanguage, string>> = {
  'James Clear': { en: 'James Clear', ru: 'Джеймс Клир', kk: 'Джеймс Клир' },
  'Antoine de Saint-Exupery': { en: 'Antoine de Saint-Exupéry', ru: 'Антуан де Сент-Экзюпери', kk: 'Антуан де Сент-Экзюпери' },
  'Mukhtar Auezov': { en: 'Mukhtar Auezov', ru: 'Мухтар Ауэзов', kk: 'Мұхтар Әуезов' },
  'George Orwell': { en: 'George Orwell', ru: 'Джордж Оруэлл', kk: 'Джордж Оруэлл' },
  'J. K. Rowling': { en: 'J. K. Rowling', ru: 'Дж. К. Роулинг', kk: 'Дж. К. Роулинг' },
};

const phrases: Record<'ru' | 'kk', Record<string, string>> = {
  ru: {
    'Back to shop': 'Назад в магазин', 'Reviews about our shop': 'Отзывы о магазине', 'Share your experience with our book shop.': 'Расскажите о своём опыте покупок в нашем книжном магазине.',
    'Edit your review': 'Изменить отзыв', 'Write a shop review': 'Написать отзыв о магазине', 'Tell us about your experience (optional)': 'Расскажите о своём опыте (необязательно)',
    'Thank you! Your review is published.': 'Спасибо! Ваш отзыв опубликован.', 'Sending…': 'Отправка…', 'Update review': 'Обновить отзыв', 'Publish review': 'Опубликовать отзыв',
    'Log in': 'Войти', 'to rate our shop and leave a review.': 'чтобы оценить магазин и оставить отзыв.', 'Customer reviews': 'Отзывы покупателей', 'Loading…': 'Загрузка…', 'Be the first to review our shop.': 'Оставьте первый отзыв о магазине.',
    'My orders': 'Мои заказы', 'All orders made with your account e-mail.': 'Все заказы, оформленные с электронной почты вашего аккаунта.', 'to see your orders.': 'чтобы посмотреть заказы.',
    'Reserved': 'Зарезервирован', 'Paid': 'Оплачен', 'Cancelled': 'Отменён', 'You have no orders yet.': 'У вас пока нет заказов.', 'Browse catalog': 'Открыть каталог',
    'My requests': 'Мои обращения', 'Your messages to support and the answers you received.': 'Ваши обращения в поддержку и ответы на них.', 'to see your requests.': 'чтобы посмотреть обращения.',
    'Support reply': 'Ответ поддержки', 'No reply yet. Support will answer here.': 'Пока нет ответа. Поддержка ответит здесь.', 'You have not written to support yet.': 'Вы ещё не обращались в поддержку.', 'Go to my orders': 'Перейти к заказам',
    'Open': 'Открыто', 'In progress': 'В работе', 'Closed': 'Закрыто', 'Refund': 'Возврат', 'Delivery': 'Доставка', 'Other': 'Другое',
    'Notifications': 'Уведомления', 'Books you are waiting for. When a book is back in stock, it appears at the top.': 'Книги, которых вы ждёте. Когда книга появится в наличии, она будет вверху списка.',
    'to see your notifications and waiting list.': 'чтобы посмотреть уведомления и список ожидания.', 'Back in stock': 'Снова в наличии', 'New': 'Новое', 'Was back, but sold out again': 'Появилась, но снова закончилась', 'Buy now': 'Купить', 'Waiting list': 'Список ожидания',
    'Stop waiting': 'Убрать из списка ожидания', 'You are not waiting for any book. Press “Notify me” on a sold-out book in the': 'Вы не ждёте ни одну книгу. Нажмите «Сообщить о поступлении» у отсутствующей книги в',
    'Wishlist': 'Избранное', 'Books you saved for later.': 'Книги, которые вы сохранили на потом.', 'to save books to your wishlist.': 'чтобы сохранять книги в избранное.',
    'Remove': 'Убрать', 'Your wishlist is empty. Press ♡ on a book page to save it here.': 'В избранном пока пусто. Нажмите ♡ на странице книги, чтобы сохранить её здесь.',
    'For you': 'Для вас', 'Choose the categories you like, and we will pick books for you.': 'Выберите любимые категории, и мы подберём для вас книги.', 'My favourite categories': 'Мои любимые категории', 'Saving…': 'Сохранение…', 'Save': 'Сохранить', 'Saved ✓': 'Сохранено ✓', 'Recommended for you': 'Рекомендуем вам',
    'Recommended from your favourite categories:': 'По вашим любимым категориям:', 'Based on your wishlist, orders and reviews:': 'На основе избранного, заказов и отзывов:', 'You have not chosen categories yet, so here are our best-rated books.': 'Вы ещё не выбрали категории — вот книги с лучшим рейтингом.',
    'You already have all books from these categories. Look at the top rated books in the': 'Вы уже просмотрели все книги из этих категорий. Посмотрите книги с высоким рейтингом в',
    'Profile': 'Профиль', 'Cart': 'Корзина', 'Log out': 'Выйти', 'My account': 'Мой аккаунт',
    'Your orders, saved books and notifications in one place.': 'Заказы, избранные книги и уведомления в одном месте.', 'book': 'книга', 'books': 'книг', 'in cart': 'в корзине', 'order': 'заказ', 'orders': 'заказов',
    'support request': 'обращение', 'support requests': 'обращений', 'in wishlist': 'в избранном', 'on waiting list': 'в списке ожидания', 'back in stock': 'снова в наличии',
    'About us': 'О нас', 'What you can do here': 'Что можно делать в магазине', 'Orders, delivery and payment': 'Заказы, доставка и оплата', 'Contact support': 'Связаться с поддержкой', 'The team': 'Команда',
    'Genre:': 'Жанр:', 'First published:': 'Год публикации:', 'No reviews yet': 'Пока нет отзывов', 'Out of stock': 'Нет в наличии', 'Add to cart': 'В корзину', 'Log in to save': 'Войдите, чтобы сохранить',
    'This book is sold out. Want to know when it is back?': 'Книга закончилась. Хотите узнать, когда она появится?', 'Your e-mail': 'Ваша почта', 'Notify me': 'Сообщить о поступлении',
    'Reviews': 'Отзывы', 'Write a review': 'Написать отзыв', 'What did you think of this book? (optional)': 'Что вы думаете об этой книге? (необязательно)',
    'Be the first to review this book.': 'Оставьте первый отзыв об этой книге.', 'You may also like': 'Вам также может понравиться', 'Back to catalog': 'Назад в каталог', 'by': 'автор',
    'Welcome back': 'С возвращением', 'Log in to your account.': 'Войдите в аккаунт.', 'Email': 'Электронная почта', 'Password': 'Пароль', 'Logging in…': 'Вход…', "Don't have an account?": 'Нет аккаунта?', 'Sign up': 'Зарегистрироваться',
    'Create an account': 'Создать аккаунт', 'Sign up to start ordering books.': 'Зарегистрируйтесь, чтобы заказывать книги.', 'Full name': 'Имя и фамилия', 'Creating account…': 'Создание аккаунта…', 'Already have an account?': 'Уже есть аккаунт?',
    'Your cart is empty.': 'Корзина пуста.', 'Go to catalog': 'Перейти в каталог', 'Books subtotal': 'Стоимость книг', 'Select area': 'Выберите зону доставки', 'Total including delivery': 'Итого с доставкой',
    'Customer': 'Покупатель', 'Phone': 'Телефон', 'Delivery address': 'Адрес доставки', 'Saved address': 'Сохранённый адрес', 'Enter a new address': 'Ввести новый адрес', 'City': 'Город', 'Location': 'Зона доставки',
    'Choose a delivery area': 'Выберите зону доставки', 'inside city': 'в пределах города', 'outside city': 'за пределами города', 'Full address': 'Полный адрес', 'Entrance (optional)': 'Подъезд (необязательно)', 'Apartment (optional)': 'Квартира (необязательно)', 'Intercom code (optional)': 'Код домофона (необязательно)', 'Floor (optional)': 'Этаж (необязательно)',
    'Save this address for next time': 'Сохранить адрес для следующих заказов', 'Placing order…': 'Оформление заказа…', 'Place order': 'Оформить заказ',
    'Delivery inside the city costs 1,000 ₸. Delivery outside the city costs 1,500 ₸.': 'Доставка в пределах города стоит 1 000 ₸, за город — 1 500 ₸.',
    'Payment': 'Оплата', 'Payment attempts': 'Попытки оплаты', 'Processing…': 'Обработка…', 'Thank you for your purchase!': 'Спасибо за покупку!', 'Reservation expired': 'Бронь истекла',
    'The order wasn\'t paid within 15 minutes, so the books are available again.': 'Заказ не оплатили за 15 минут, поэтому книги снова доступны.', 'Order again': 'Заказать снова', 'Hide support form': 'Скрыть форму поддержки', 'Contact support about this order': 'Написать в поддержку по этому заказу',
    'Topic': 'Тема', 'Message': 'Сообщение', 'Describe the problem (at least 10 characters, no links or rude words)': 'Опишите проблему (минимум 10 символов, без ссылок и грубых слов)', 'Send to support': 'Отправить в поддержку', 'Your requests': 'Ваши обращения', 'No reply yet.': 'Пока нет ответа.',
    'Search books': 'Поиск книг', 'Search': 'Поиск', 'Price from, ₸': 'Цена от, ₸', 'Price to, ₸': 'Цена до, ₸', 'Any rating': 'Любой рейтинг', 'Sort by': 'Сортировка', 'Default': 'По умолчанию',
    'Price: low to high': 'Сначала дешевле', 'Price: high to low': 'Сначала дороже', 'Reset': 'Сбросить', 'No books match these filters.': 'По этим фильтрам книги не найдены.',
    'Online Book Shop is a student project made at KBTU.': 'Online Book Shop — учебный проект студентов KBTU.',
    'Browse the': 'Смотрите', 'filter books by category, price and rating.': ', фильтруйте книги по категории, цене и рейтингу.',
    'Read book pages and reviews, and leave your own review after you log in.': 'Читайте о книгах и отзывы, а после входа оставляйте свои.',
    'Add books to the cart and the wishlist.': 'Добавляйте книги в корзину и избранное.',
    'Press “Notify me” on a book that is out of stock and we will tell you when it is back.': 'Нажмите «Сообщить о поступлении» у книги, которой нет в наличии, и мы сообщим, когда она появится.',
    'Rate the shop on the': 'Оцените магазин на странице', 'page.': '.',
    'After you place an order, the books are reserved for you for 15 minutes. Pay within this time, otherwise the reservation expires.': 'После оформления заказа книги резервируются на 15 минут. Оплатите заказ за это время, иначе бронь истечёт.',
    'Delivery costs 1 000 ₸ inside the city limits and 1 500 ₸ outside them.': 'Доставка стоит 1 000 ₸ в пределах города и 1 500 ₸ за его пределами.',
    'Payment in this project is simulated: no real money is taken.': 'Оплата в проекте демонстрационная: реальные деньги не списываются.',
    'Every order has its own secret link. Keep it: anyone who has the link can open the order, and nobody can guess it.': 'У каждого заказа есть секретная ссылка. Сохраните её: заказ может открыть тот, у кого есть ссылка, её нельзя подобрать.',
    'Have a problem with an order, a refund or delivery? Open your order and press': 'Возникла проблема с заказом, возвратом или доставкой? Откройте заказ и нажмите',
    'Choose a topic and describe the problem in a few clear words.': 'Выберите тему и кратко опишите проблему.',
    'Please write politely. Messages with rude words, links or meaningless text are not sent.': 'Пожалуйста, пишите вежливо. Сообщения с грубыми словами, ссылками или бессмысленным текстом не отправляются.',
    'A request can be': 'У обращения может быть статус', ' (not seen yet), ': ' (ещё не просмотрено), ', ' (support is working on it) or ': ' (поддержка работает над ним) или ', ' (solved).': ' (решено).',
    'The shop was built by the KBTU Online Shop Team: Django REST backend, Angular frontend, PostgreSQL on Render.': 'Магазин создан командой KBTU Online Shop: Django REST, Angular и PostgreSQL на Render.',
    'Cannot reach the server. Is Django running (python manage.py runserver)?': 'Не удалось связаться с сервером. Проверьте подключение к интернету.',
    'Something went wrong. Please try again.': 'Что-то пошло не так. Попробуйте ещё раз.',
    'Please log out and log in again to leave a review.': 'Выйдите и войдите снова, чтобы оставить отзыв.', 'Choose from 1 to 5 stars.': 'Выберите от 1 до 5 звёзд.',
    'Enter your e-mail and we will let you know.': 'Введите электронную почту, и мы сообщим вам.', 'Please log in to leave a shop review.': 'Войдите, чтобы оставить отзыв о магазине.',
    'Waiting since': 'В списке с', 'catalog': 'каталоге', 'Rated': 'Оценка', 'out of 5': 'из 5', 'Your rating': 'Ваша оценка',
    'to rate this book and leave a review.': 'чтобы оценить книгу и оставить отзыв.',
    'Log in with your account to use saved addresses.': 'Войдите в аккаунт, чтобы использовать сохранённые адреса.',
    'No saved addresses yet. You can choose to save the new address below.': 'Сохранённых адресов пока нет. Ниже можно сохранить новый адрес.',
    'Entrance': 'Подъезд', 'Apartment': 'Квартира', 'Intercom code': 'Код домофона', 'Floor': 'Этаж', 'In cart': 'В корзине',
    'Reserved for': 'Зарезервировано на', 'Total': 'Итого', 'Card number': 'Номер карты', 'Pay': 'Оплатить',
    'This is a simulated bank, so no real card is needed. Any 16 digits will work. A card ending in 0000 will be declined.': 'Это демонстрационный банк, настоящая карта не нужна. Подойдут любые 16 цифр. Карта, оканчивающаяся на 0000, будет отклонена.',
    'inside city limits': 'в пределах города', 'outside city limits': 'за пределами города', 'entrance': 'подъезд', 'apt.': 'кв.', 'floor': 'этаж', 'intercom': 'домофон',
    'Fiction': 'Художественная литература', 'Fantasy': 'Фэнтези', 'Novels': 'Романы', 'Children\'s Books': 'Детские книги', 'Personal Development': 'Саморазвитие', 'Fairy tale': 'Сказка', 'Dystopia': 'Антиутопия', 'Self-development': 'Саморазвитие',
    'Filter books by category': 'Фильтр книг по категории', 'Top rated books': 'Книги с высоким рейтингом', 'reviews': 'отзывов', 'left': 'осталось', 'in stock': 'в наличии',
    'Welcome,': 'Добро пожаловать,', 'Your account for': 'Ваш аккаунт для адреса', 'has been created.': 'создан.',
    'Inside': 'В пределах города', 'Outside': 'За пределами города', 'the city': 'города', 'Street, building, block': 'Улица, дом, корпус', 'KBTU · Online Shop Team · student project': 'KBTU · Команда Online Shop · учебный проект',
    'Literature': 'Литература', 'Novel': 'Роман', 'Shop reviews': 'Отзывы о магазине',
    'Online Book Shop': 'Книжный магазин Online Book Shop', 'Catalog · Online Book Shop': 'Каталог · Online Book Shop', 'Book · Online Book Shop': 'Книга · Online Book Shop',
    'Shop reviews · Online Book Shop': 'Отзывы о магазине · Online Book Shop', 'About us · Online Book Shop': 'О нас · Online Book Shop', 'Cart · Online Book Shop': 'Корзина · Online Book Shop',
    'My account · Online Book Shop': 'Аккаунт · Online Book Shop', 'For you · Online Book Shop': 'Для вас · Online Book Shop', 'My orders · Online Book Shop': 'Мои заказы · Online Book Shop',
    'My requests · Online Book Shop': 'Мои обращения · Online Book Shop', 'Wishlist · Online Book Shop': 'Избранное · Online Book Shop', 'Notifications · Online Book Shop': 'Уведомления · Online Book Shop',
    'Order · Online Book Shop': 'Заказ · Online Book Shop', 'Sign up · Online Book Shop': 'Регистрация · Online Book Shop', 'Log in · Online Book Shop': 'Вход · Online Book Shop',
    'Hello,': 'Здравствуйте,', 'stars': 'звёзд', 'Decrease': 'Уменьшить', 'Increase': 'Увеличить', 'Girl reading a book on a stack of books': 'Девушка читает книгу, сидя на стопке книг', 'No rating yet': 'Пока нет оценок',
    'Author:': 'Автор:', 'Summary': 'О книге', 'Pages:': 'Страниц:', 'Edition:': 'Издание:', 'Varies by edition': 'Зависит от издания',
    'Add to wishlist': 'В избранное', 'In wishlist': 'В избранном', 'You are on the waiting list. We will notify you when this book is back in stock.': 'Вы в списке ожидания. Мы сообщим, когда книга снова появится.',
    'Thank you! We will let': 'Спасибо! Мы сообщим на адрес', 'know when the book is back.': 'когда книга появится в наличии.',
    'Avery hardcover edition': 'Твёрдый переплёт Avery', 'Penguin Random House hardcover edition': 'Твёрдый переплёт Penguin Random House', 'Four-part epic; page count varies by edition': 'Эпопея из четырёх книг; число страниц зависит от издания', 'Signet mass-market paperback edition': 'Карманное издание в мягкой обложке Signet', 'Scholastic paperback edition (Sorcerer\'s Stone title)': 'Мягкая обложка Scholastic (издание «Философский камень»)',
    'James Clear explains how small routines can build into lasting change. The book follows a practical four-step framework—make it obvious, attractive, easy, and satisfying—to help readers build helpful habits and reduce unwanted ones. It combines research from biology, psychology, and neuroscience with everyday examples and exercises for shaping routines and the environment around them.': 'Джеймс Клир показывает, как небольшие действия складываются в устойчивые перемены. Он предлагает систему из четырёх шагов — сделать привычку заметной, привлекательной, простой и приятной — чтобы закреплять полезные привычки и ослаблять нежелательные. Научные данные из биологии, психологии и нейронауки здесь дополнены примерами и упражнениями для изменения повседневных привычек и окружающей среды.',
    'A pilot makes an emergency landing in the Sahara and meets a mysterious boy from a tiny asteroid. As the Little Prince tells the story of his travels and the people he met on other planets, the pilot learns about the prince\'s rose and his journey to Earth. Their friendship frames a fable about seeing beyond appearances, caring for others, and understanding what matters.': 'Лётчик совершает вынужденную посадку в Сахаре и встречает мальчика с крошечного астероида. Маленький принц рассказывает о путешествиях и жителях других планет, о своей розе и дороге на Землю. Их дружба превращает сказку в размышление о заботе, ответственности и умении видеть главное.',
    'This historical novel follows Abai from childhood into adulthood on the Kazakh steppe. Through his relationships with family, poets, and community leaders, the story depicts the traditions, conflicts, and social changes of nineteenth-century Kazakh society. The work is an epic published in multiple books and volumes; the total page count depends on the edition.': 'Исторический роман рассказывает о взрослении Абая в казахской степи. Через его отношения с семьёй, поэтами и общественными деятелями показаны традиции, конфликты и перемены в казахском обществе XIX века. «Абай жолы» — эпопея из нескольких книг и томов, поэтому общее число страниц зависит от издания.',
    'Winston Smith works at the Ministry of Truth, where he alters old records to match the ruling Party\'s version of events. In a society shaped by surveillance, propaganda, and fear, he begins a private diary and forms a forbidden relationship with Julia. His search for truth and personal freedom brings him into conflict with the system that controls everyday life.': 'Уинстон Смит работает в Министерстве правды и переписывает старые документы в соответствии с версией событий правящей партии. В обществе, где царят слежка, пропаганда и страх, он начинает вести дневник и вступает в запретные отношения с Джулией. Поиск правды и личной свободы приводит его к столкновению с системой, контролирующей повседневную жизнь.',
    'On his eleventh birthday, Harry Potter discovers that he is a wizard and leaves his unhappy home to study at Hogwarts. He makes friends with Ron and Hermione, learns about his parents, and encounters a mystery surrounding the Sorcerer\'s Stone. The first story follows Harry through his first year at the school as he and his friends try to uncover what is being hidden.': 'В одиннадцатый день рождения Гарри Поттер узнаёт, что он волшебник, и отправляется учиться в Хогвартс. Он знакомится с Роном и Гермионой, узнаёт о родителях и сталкивается с тайной Философского камня. Первая книга рассказывает о его учебном году и о том, как друзья пытаются раскрыть скрываемую в школе загадку.',
    'success': 'Успешно', 'failed': 'Ошибка', 'refunded': 'Возвращён',
    'Open one of your orders and press': 'Откройте один из заказов и нажмите',
    'Please describe your problem: the message is empty.': 'Опишите проблему: сообщение пустое.',
    'Support answers on the same order page. If you are logged in, all your messages and answers are in': 'Поддержка ответит на странице заказа. Если вы вошли в аккаунт, все сообщения и ответы находятся в разделе',
    'Request #': 'Обращение №', 'Order #': 'Заказ №', 'sent. Our support team will review it.': 'отправлено. Поддержка рассмотрит его.',
    'Incorrect email or password.': 'Неверная почта или пароль.', 'Book not found.': 'Книга не найдена.', 'Order not found.': 'Заказ не найден.',
    'This email is already registered.': 'Эта почта уже зарегистрирована.', 'Address is required for delivery.': 'Для доставки нужен адрес.',
    'Choose a saved address or enter a new one.': 'Выберите сохранённый адрес или введите новый.', 'This book is in stock, you can order it now.': 'Эта книга есть в наличии, её можно заказать.',
    'Saved address not found for this customer.': 'Сохранённый адрес покупателя не найден.', 'Customer not found. Create an order first.': 'Покупатель не найден. Сначала оформите заказ.',
    'The message is too short. Please write at least 10 characters so we can understand the problem.': 'Сообщение слишком короткое. Напишите не менее 10 символов, чтобы мы поняли проблему.',
    'Please describe the problem in words, not only with digits or symbols.': 'Опишите проблему словами, а не только цифрами или символами.',
    'Links are not allowed in a support request. Please remove the link and describe the problem in words.': 'В обращении нельзя отправлять ссылки. Удалите ссылку и опишите проблему словами.',
    'Please remove rude words or insults. We will gladly help if you describe the problem politely.': 'Уберите грубые слова и оскорбления. Мы поможем, если вы вежливо опишете проблему.',
    'The message looks like spam (repeated characters or words). Please write a normal description of the problem.': 'Сообщение похоже на спам (повторяются символы или слова). Опишите проблему обычным текстом.',
    'James Clear explains how small routines can build into lasting change. The book offers practical methods for creating helpful habits, changing your environment, and making progress easier to repeat.': 'Джеймс Клир объясняет, как небольшие привычки складываются в устойчивые перемены. В книге собраны практические способы формировать полезные привычки, менять окружение и закреплять прогресс.',
    'After meeting a young prince in the desert, a stranded pilot hears about the prince\'s travels between planets. Their conversations explore friendship, responsibility, and how people learn to value one another.': 'В пустыне лётчик встречает маленького принца и узнаёт о его путешествиях между планетами. Их разговоры — о дружбе, ответственности и умении ценить друг друга.',
    'Mukhtar Auezov\'s novel follows the poet and thinker Abai as he grows up on the Kazakh steppe. Through his life, the story portrays the customs, conflicts, and social changes of nineteenth-century Kazakh society.': 'Роман Мухтара Ауэзова рассказывает о взрослении поэта и мыслителя Абая в казахской степи. Через его судьбу показаны обычаи, конфликты и перемены в казахском обществе XIX века.',
    'Winston Smith lives in a state where the government monitors its citizens and rewrites the past. His quiet search for truth and personal freedom becomes a dangerous challenge to the ruling system.': 'Уинстон Смит живёт в государстве, где власти следят за гражданами и переписывают прошлое. Его попытка найти правду и сохранить свободу становится опасным вызовом режиму.',
    'On his eleventh birthday, Harry Potter learns that he is a wizard and begins life at Hogwarts. With new friends, he discovers the history of his family and a mystery connected to the school.': 'В одиннадцатый день рождения Гарри Поттер узнаёт, что он волшебник, и отправляется в Хогвартс. Вместе с новыми друзьями он открывает историю своей семьи и тайну, связанную со школой.',
  },
  kk: {
    'Back to shop': 'Дүкенге қайту', 'Reviews about our shop': 'Дүкен туралы пікірлер', 'Share your experience with our book shop.': 'Кітап дүкеніміз туралы пікіріңізбен бөлісіңіз.',
    'Edit your review': 'Пікірді өзгерту', 'Write a shop review': 'Дүкен туралы пікір жазу', 'Tell us about your experience (optional)': 'Әсеріңізбен бөлісіңіз (міндетті емес)',
    'Thank you! Your review is published.': 'Рақмет! Пікіріңіз жарияланды.', 'Sending…': 'Жіберілуде…', 'Update review': 'Пікірді жаңарту', 'Publish review': 'Пікірді жариялау',
    'Log in': 'Кіру', 'to rate our shop and leave a review.': 'дүкенге баға беріп, пікір қалдыру үшін.', 'Customer reviews': 'Сатып алушылардың пікірлері', 'Loading…': 'Жүктелуде…', 'Be the first to review our shop.': 'Дүкен туралы алғашқы пікірді қалдырыңыз.',
    'My orders': 'Менің тапсырыстарым', 'All orders made with your account e-mail.': 'Аккаунтыңыздың электрондық поштасымен жасалған барлық тапсырыс.', 'to see your orders.': 'тапсырыстарыңызды көру үшін.',
    'Reserved': 'Брондалған', 'Paid': 'Төленген', 'Cancelled': 'Бас тартылған', 'You have no orders yet.': 'Әзірге тапсырыстарыңыз жоқ.', 'Browse catalog': 'Каталогты ашу',
    'My requests': 'Менің өтініштерім', 'Your messages to support and the answers you received.': 'Қолдау қызметіне жазған хабарламаларыңыз бен жауаптар.', 'to see your requests.': 'өтініштеріңізді көру үшін.',
    'Support reply': 'Қолдау қызметінің жауабы', 'No reply yet. Support will answer here.': 'Әзірге жауап жоқ. Қолдау қызметі осында жауап береді.', 'You have not written to support yet.': 'Қолдау қызметіне әлі жазбадыңыз.', 'Go to my orders': 'Тапсырыстарыма өту',
    'Open': 'Ашық', 'In progress': 'Орындалуда', 'Closed': 'Жабық', 'Refund': 'Қайтару', 'Delivery': 'Жеткізу', 'Other': 'Басқа',
    'Notifications': 'Хабарландырулар', 'Books you are waiting for. When a book is back in stock, it appears at the top.': 'Күтіп жүрген кітаптарыңыз. Кітап қайта сатылымға шыққанда тізімнің басында көрінеді.',
    'to see your notifications and waiting list.': 'хабарландырулар мен күту тізімін көру үшін.', 'Back in stock': 'Қайта сатылымда', 'New': 'Жаңа', 'Was back, but sold out again': 'Қайта шықты, бірақ тағы таусылды', 'Buy now': 'Сатып алу', 'Waiting list': 'Күту тізімі',
    'Stop waiting': 'Күтуді тоқтату', 'You are not waiting for any book. Press “Notify me” on a sold-out book in the': 'Сіз ешбір кітапты күтіп тұрған жоқсыз. Таусылған кітапта «Хабарлау» батырмасын басыңыз:',
    'Wishlist': 'Таңдаулылар', 'Books you saved for later.': 'Кейінге сақтаған кітаптарыңыз.', 'to save books to your wishlist.': 'кітаптарды таңдаулыларға сақтау үшін.',
    'Remove': 'Өшіру', 'Your wishlist is empty. Press ♡ on a book page to save it here.': 'Таңдаулылар тізімі бос. Кітапты сақтау үшін оның бетіндегі ♡ батырмасын басыңыз.',
    'For you': 'Сізге арналған', 'Choose the categories you like, and we will pick books for you.': 'Ұнайтын санаттарды таңдаңыз, біз сізге кітаптарды ұсынамыз.', 'My favourite categories': 'Менің сүйікті санаттарым', 'Saving…': 'Сақталуда…', 'Save': 'Сақтау', 'Saved ✓': 'Сақталды ✓', 'Recommended for you': 'Сізге ұсынамыз',
    'Recommended from your favourite categories:': 'Сүйікті санаттарыңыз бойынша:', 'Based on your wishlist, orders and reviews:': 'Таңдаулыларыңыз, тапсырыстарыңыз бен пікірлеріңіз бойынша:', 'You have not chosen categories yet, so here are our best-rated books.': 'Санаттарды әлі таңдамадыңыз. Міне, рейтингі жоғары кітаптар.',
    'You already have all books from these categories. Look at the top rated books in the': 'Бұл санаттардың барлық кітабын қарап шықтыңыз. Рейтингі жоғары кітаптарды қараңыз:',
    'Profile': 'Профиль', 'Cart': 'Себет', 'Log out': 'Шығу', 'My account': 'Менің аккаунтым',
    'Your orders, saved books and notifications in one place.': 'Тапсырыстарыңыз, сақталған кітаптар мен хабарландырулар бір жерде.', 'book': 'кітап', 'books': 'кітап', 'in cart': 'себетте', 'order': 'тапсырыс', 'orders': 'тапсырыс',
    'support request': 'өтініш', 'support requests': 'өтініш', 'in wishlist': 'таңдаулыларда', 'on waiting list': 'күту тізімінде', 'back in stock': 'қайта сатылымда',
    'About us': 'Біз туралы', 'What you can do here': 'Дүкенде не істей аласыз', 'Orders, delivery and payment': 'Тапсырыс, жеткізу және төлем', 'Contact support': 'Қолдау қызметіне хабарласу', 'The team': 'Команда',
    'Genre:': 'Жанры:', 'First published:': 'Алғашқы басылым жылы:', 'No reviews yet': 'Әзірге пікір жоқ', 'Out of stock': 'Қоймада жоқ', 'Add to cart': 'Себетке қосу', 'Log in to save': 'Сақтау үшін кіріңіз',
    'This book is sold out. Want to know when it is back?': 'Бұл кітап таусылды. Қайта шыққанда білгіңіз келе ме?', 'Your e-mail': 'Электрондық поштаңыз', 'Notify me': 'Хабарлау',
    'Reviews': 'Пікірлер', 'Write a review': 'Пікір жазу', 'What did you think of this book? (optional)': 'Бұл кітап туралы ойыңыз? (міндетті емес)', 'Be the first to review this book.': 'Бұл кітап туралы алғашқы пікірді қалдырыңыз.', 'You may also like': 'Сізге ұнауы мүмкін', 'Back to catalog': 'Каталогқа қайту', 'by': 'авторы',
    'Welcome back': 'Қайта қош келдіңіз', 'Log in to your account.': 'Аккаунтыңызға кіріңіз.', 'Email': 'Электрондық пошта', 'Password': 'Құпиясөз', 'Logging in…': 'Кіру…', "Don't have an account?": 'Аккаунтыңыз жоқ па?', 'Sign up': 'Тіркелу',
    'Create an account': 'Аккаунт жасау', 'Sign up to start ordering books.': 'Кітаптарға тапсырыс беру үшін тіркеліңіз.', 'Full name': 'Аты-жөні', 'Creating account…': 'Аккаунт жасалуда…', 'Already have an account?': 'Аккаунтыңыз бар ма?',
    'Your cart is empty.': 'Себетіңіз бос.', 'Go to catalog': 'Каталогқа өту', 'Books subtotal': 'Кітаптардың құны', 'Select area': 'Жеткізу аймағын таңдаңыз', 'Total including delivery': 'Жеткізумен бірге барлығы',
    'Customer': 'Сатып алушы', 'Phone': 'Телефон', 'Delivery address': 'Жеткізу мекенжайы', 'Saved address': 'Сақталған мекенжай', 'Enter a new address': 'Жаңа мекенжай енгізу', 'City': 'Қала', 'Location': 'Жеткізу аймағы',
    'Choose a delivery area': 'Жеткізу аймағын таңдаңыз', 'inside city': 'қала ішінде', 'outside city': 'қала сыртында', 'Full address': 'Толық мекенжай', 'Entrance (optional)': 'Кіреберіс (міндетті емес)', 'Apartment (optional)': 'Пәтер (міндетті емес)', 'Intercom code (optional)': 'Домофон коды (міндетті емес)', 'Floor (optional)': 'Қабат (міндетті емес)',
    'Save this address for next time': 'Бұл мекенжайды келесі жолы үшін сақтау', 'Placing order…': 'Тапсырыс рәсімделуде…', 'Place order': 'Тапсырыс беру',
    'Delivery inside the city costs 1,000 ₸. Delivery outside the city costs 1,500 ₸.': 'Қала ішіндегі жеткізу 1 000 ₸, қала сыртында 1 500 ₸ тұрады.',
    'Payment': 'Төлем', 'Payment attempts': 'Төлем әрекеттері', 'Processing…': 'Өңделуде…', 'Thank you for your purchase!': 'Сатып алғаныңызға рақмет!', 'Reservation expired': 'Брондау мерзімі аяқталды',
    'The order wasn\'t paid within 15 minutes, so the books are available again.': 'Тапсырыс 15 минут ішінде төленбеді, кітаптар қайта сатылымға шықты.', 'Order again': 'Қайта тапсырыс беру', 'Hide support form': 'Қолдау формасын жасыру', 'Contact support about this order': 'Осы тапсырыс бойынша қолдауға жазу',
    'Topic': 'Тақырып', 'Message': 'Хабарлама', 'Describe the problem (at least 10 characters, no links or rude words)': 'Мәселені сипаттаңыз (кемінде 10 таңба, сілтеме мен дөрекі сөздерсіз)', 'Send to support': 'Қолдауға жіберу', 'Your requests': 'Сіздің өтініштеріңіз', 'No reply yet.': 'Әзірге жауап жоқ.',
    'Price from, ₸': 'Бағасы, бастап ₸', 'Price to, ₸': 'Бағасы, дейін ₸', 'Any rating': 'Кез келген рейтинг', 'Sort by': 'Сұрыптау', 'Default': 'Әдепкі бойынша', 'Price: low to high': 'Арзаннан қымбатқа', 'Price: high to low': 'Қымбаттан арзанға', 'Reset': 'Тазарту', 'No books match these filters.': 'Бұл сүзгілерге сай кітап табылмады.',
    'Online Book Shop is a student project made at KBTU.': 'Online Book Shop — KBTU студенттерінің оқу жобасы.',
    'Browse the': 'Каталогты қараңыз,', 'filter books by category, price and rating.': 'кітаптарды санаты, бағасы мен рейтингі бойынша сүзіңіз.',
    'Read book pages and reviews, and leave your own review after you log in.': 'Кітаптар мен пікірлерді оқып, кіргеннен кейін өз пікіріңізді қалдырыңыз.',
    'Add books to the cart and the wishlist.': 'Кітаптарды себетке және таңдаулыларға қосыңыз.',
    'Press “Notify me” on a book that is out of stock and we will tell you when it is back.': 'Таусылған кітаптағы «Хабарлау» батырмасын басыңыз, ол қайта сатылымға шыққанда хабарлаймыз.',
    'Rate the shop on the': 'Дүкенге бағаны мына бетте қалдырыңыз:', 'page.': '.',
    'After you place an order, the books are reserved for you for 15 minutes. Pay within this time, otherwise the reservation expires.': 'Тапсырыс берген соң кітаптар 15 минутқа брондалады. Осы уақытта төлем жасамасаңыз, бронь аяқталады.',
    'Delivery costs 1 000 ₸ inside the city limits and 1 500 ₸ outside them.': 'Жеткізу қала ішінде 1 000 ₸, қала сыртында 1 500 ₸ тұрады.',
    'Payment in this project is simulated: no real money is taken.': 'Бұл жобада төлем сынақ ретінде жасалады: ақша алынбайды.',
    'Every order has its own secret link. Keep it: anyone who has the link can open the order, and nobody can guess it.': 'Әр тапсырыстың құпия сілтемесі бар. Сақтап қойыңыз: сілтемесі бар адам тапсырысты аша алады, оны табу мүмкін емес.',
    'Have a problem with an order, a refund or delivery? Open your order and press': 'Тапсырыс, қайтару немесе жеткізу мәселесі бар ма? Тапсырысты ашып, басыңыз:',
    'Choose a topic and describe the problem in a few clear words.': 'Тақырыпты таңдап, мәселені қысқаша сипаттаңыз.',
    'Please write politely. Messages with rude words, links or meaningless text are not sent.': 'Сыпайы жазыңыз. Дөрекі сөздері, сілтемелері немесе мағынасыз мәтіні бар хабарламалар жіберілмейді.',
    'A request can be': 'Өтініштің күйі', ' (not seen yet), ': ' (әлі қаралмады), ', ' (support is working on it) or ': ' (қолдау қызметі қарап жатыр) немесе ', ' (solved).': ' (шешілді).',
    'The shop was built by the KBTU Online Shop Team: Django REST backend, Angular frontend, PostgreSQL on Render.': 'Дүкенді KBTU Online Shop командасы Django REST, Angular және Render-дегі PostgreSQL арқылы жасады.',
    'Cannot reach the server. Is Django running (python manage.py runserver)?': 'Серверге қосылмады. Интернет байланысын тексеріңіз.', 'Something went wrong. Please try again.': 'Қате шықты. Қайталап көріңіз.',
    'Please log out and log in again to leave a review.': 'Пікір қалдыру үшін аккаунттан шығып, қайта кіріңіз.', 'Choose from 1 to 5 stars.': '1 мен 5 жұлдыз аралығын таңдаңыз.',
    'Enter your e-mail and we will let you know.': 'Электрондық поштаңызды енгізіңіз, хабарлаймыз.', 'Please log in to leave a shop review.': 'Дүкен туралы пікір қалдыру үшін кіріңіз.',
    'Waiting since': 'Күту басталды:', 'catalog': 'каталогтан', 'Rated': 'Бағасы', 'out of 5': 'ішінен 5', 'Your rating': 'Сіздің бағаңыз',
    'to rate this book and leave a review.': 'кітапты бағалап, пікір қалдыру үшін.',
    'Log in with your account to use saved addresses.': 'Сақталған мекенжайларды пайдалану үшін аккаунтқа кіріңіз.',
    'No saved addresses yet. You can choose to save the new address below.': 'Сақталған мекенжай жоқ. Төменде жаңа мекенжайды сақтай аласыз.',
    'Entrance': 'Кіреберіс', 'Apartment': 'Пәтер', 'Intercom code': 'Домофон коды', 'Floor': 'Қабат', 'In cart': 'Себетте',
    'Reserved for': 'Бронь уақыты', 'Total': 'Барлығы', 'Card number': 'Карта нөмірі', 'Pay': 'Төлеу',
    'This is a simulated bank, so no real card is needed. Any 16 digits will work. A card ending in 0000 will be declined.': 'Бұл сынақ банкі, нақты карта қажет емес. Кез келген 16 сан жарайды. Соңы 0000 картасы қабылданбайды.',
    'inside city limits': 'қала ішінде', 'outside city limits': 'қала сыртында', 'entrance': 'кіреберіс', 'apt.': 'пәтер', 'floor': 'қабат', 'intercom': 'домофон',
    'Fiction': 'Көркем әдебиет', 'Fantasy': 'Фэнтези', 'Novels': 'Романдар', 'Children\'s Books': 'Балалар әдебиеті', 'Personal Development': 'Өзін-өзі дамыту', 'Fairy tale': 'Ертегі', 'Dystopia': 'Антиутопия', 'Self-development': 'Өзін-өзі дамыту',
    'Filter books by category': 'Кітаптарды санат бойынша сүзу', 'Top rated books': 'Рейтингі жоғары кітаптар', 'reviews': 'пікір', 'left': 'қалды', 'in stock': 'қоймада бар',
    'Welcome,': 'Қош келдіңіз,', 'Your account for': 'Аккаунтыңыз мына мекенжайға', 'has been created.': 'жасалды.',
    'Inside': 'Қала ішінде', 'Outside': 'Қала сыртында', 'the city': 'қала', 'Street, building, block': 'Көше, үй, корпус', 'KBTU · Online Shop Team · student project': 'KBTU · Online Shop командасы · оқу жобасы',
    'Literature': 'Әдебиет', 'Novel': 'Роман', 'Shop reviews': 'Дүкен туралы пікірлер',
    'Online Book Shop': 'Online Book Shop кітап дүкені', 'Catalog · Online Book Shop': 'Каталог · Online Book Shop', 'Book · Online Book Shop': 'Кітап · Online Book Shop',
    'Shop reviews · Online Book Shop': 'Дүкен пікірлері · Online Book Shop', 'About us · Online Book Shop': 'Біз туралы · Online Book Shop', 'Cart · Online Book Shop': 'Себет · Online Book Shop',
    'My account · Online Book Shop': 'Менің аккаунтым · Online Book Shop', 'For you · Online Book Shop': 'Сізге арналған · Online Book Shop', 'My orders · Online Book Shop': 'Менің тапсырыстарым · Online Book Shop',
    'My requests · Online Book Shop': 'Менің өтініштерім · Online Book Shop', 'Wishlist · Online Book Shop': 'Таңдаулылар · Online Book Shop', 'Notifications · Online Book Shop': 'Хабарландырулар · Online Book Shop',
    'Order · Online Book Shop': 'Тапсырыс · Online Book Shop', 'Sign up · Online Book Shop': 'Тіркелу · Online Book Shop', 'Log in · Online Book Shop': 'Кіру · Online Book Shop',
    'Hello,': 'Сәлем,', 'stars': 'жұлдыз', 'Decrease': 'Азайту', 'Increase': 'Көбейту', 'Girl reading a book on a stack of books': 'Кітаптар үстінде отырып кітап оқып отырған қыз', 'No rating yet': 'Әзірге баға жоқ',
    'Author:': 'Авторы:', 'Summary': 'Кітап туралы', 'Pages:': 'Бет саны:', 'Edition:': 'Басылымы:', 'Varies by edition': 'Басылымына байланысты',
    'Add to wishlist': 'Таңдаулыларға қосу', 'In wishlist': 'Таңдаулыларда', 'You are on the waiting list. We will notify you when this book is back in stock.': 'Сіз күту тізіміндесіз. Кітап қайта сатылымға шыққанда хабарлаймыз.',
    'Thank you! We will let': 'Рақмет! Мына мекенжайға хабарлаймыз:', 'know when the book is back.': 'кітап қайта шыққанда.',
    'Avery hardcover edition': 'Avery баспасының қатты мұқабалы басылымы', 'Penguin Random House hardcover edition': 'Penguin Random House баспасының қатты мұқабалы басылымы', 'Four-part epic; page count varies by edition': 'Төрт кітаптан тұратын эпопея; бет саны басылымға байланысты', 'Signet mass-market paperback edition': 'Signet баспасының жұмсақ мұқабалы шағын басылымы', 'Scholastic paperback edition (Sorcerer\'s Stone title)': 'Scholastic жұмсақ мұқабалы басылымы («Пәлсапа тасы» атауымен)',
    'James Clear explains how small routines can build into lasting change. The book follows a practical four-step framework—make it obvious, attractive, easy, and satisfying—to help readers build helpful habits and reduce unwanted ones. It combines research from biology, psychology, and neuroscience with everyday examples and exercises for shaping routines and the environment around them.': 'Джеймс Клир шағын әрекеттердің тұрақты өзгеріске қалай айналатынын түсіндіреді. Кітап пайдалы әдеттерді қалыптастырып, қажетсіз әдеттерді азайтуға арналған төрт қадам ұсынады: әдетті анық, тартымды, оңай және жағымды ету. Биология, психология және нейроғылым деректері күнделікті мысалдармен және жаттығулармен толықтырылған.',
    'A pilot makes an emergency landing in the Sahara and meets a mysterious boy from a tiny asteroid. As the Little Prince tells the story of his travels and the people he met on other planets, the pilot learns about the prince\'s rose and his journey to Earth. Their friendship frames a fable about seeing beyond appearances, caring for others, and understanding what matters.': 'Ұшқыш Сахараға апатты жағдайда қонып, шағын астероидтан келген жұмбақ баланы кездестіреді. Кішкентай ханзада саяхаттары мен басқа ғаламшарларда кездескен адамдар туралы айтып, раушан гүлі мен Жерге сапарын баяндайды. Олардың достығы қамқорлық, жауапкершілік және маңызды нәрсені түсіну туралы ертегіге айналады.',
    'This historical novel follows Abai from childhood into adulthood on the Kazakh steppe. Through his relationships with family, poets, and community leaders, the story depicts the traditions, conflicts, and social changes of nineteenth-century Kazakh society. The work is an epic published in multiple books and volumes; the total page count depends on the edition.': 'Тарихи роман Абайдың қазақ даласындағы балалық шағынан есейген кезеңіне дейінгі өмірін баяндайды. Отбасымен, ақындармен және ел басшыларымен қарым-қатынасы арқылы XIX ғасырдағы қазақ қоғамының дәстүрлері, қайшылықтары мен өзгерістері суреттеледі. «Абай жолы» бірнеше кітап пен томнан тұратын эпопея, сондықтан жалпы бет саны басылымға байланысты.',
    'Winston Smith works at the Ministry of Truth, where he alters old records to match the ruling Party\'s version of events. In a society shaped by surveillance, propaganda, and fear, he begins a private diary and forms a forbidden relationship with Julia. His search for truth and personal freedom brings him into conflict with the system that controls everyday life.': 'Уинстон Смит Ақиқат министрлігінде жұмыс істеп, ескі құжаттарды билеуші партияның нұсқасына сай өзгертеді. Бақылау, үгіт-насихат пен үрей жайлаған қоғамда ол күнделік жүргізіп, Джулиямен тыйым салынған қарым-қатынас бастайды. Шындық пен жеке еркіндікті іздеуі оны адамдардың күнделікті өмірін бақылайтын жүйемен қақтығыстырады.',
    'On his eleventh birthday, Harry Potter discovers that he is a wizard and leaves his unhappy home to study at Hogwarts. He makes friends with Ron and Hermione, learns about his parents, and encounters a mystery surrounding the Sorcerer\'s Stone. The first story follows Harry through his first year at the school as he and his friends try to uncover what is being hidden.': 'Он бірінші туған күнінде Гарри Поттер өзінің сиқыршы екенін біліп, Хогвартсқа оқуға кетеді. Ол Рон және Гермионамен достасып, ата-анасы туралы біліп, Пәлсапа тасына қатысты құпияға тап болады. Бірінші кітап Гарридің мектептегі алғашқы жылын және достарымен бірге жасырын сырды ашуға талпынысын баяндайды.',
    'success': 'Сәтті', 'failed': 'Қате', 'refunded': 'Қайтарылды',
    'Open one of your orders and press': 'Тапсырыстарыңыздың бірін ашып, басыңыз',
    'Please describe your problem: the message is empty.': 'Мәселені сипаттаңыз: хабарлама бос.',
    'Support answers on the same order page. If you are logged in, all your messages and answers are in': 'Қолдау қызметі тапсырыс бетінде жауап береді. Аккаунтқа кірсеңіз, барлық хабарлама мен жауап мына бөлімде:',
    'Request #': 'Өтініш №', 'Order #': 'Тапсырыс №', 'sent. Our support team will review it.': 'жіберілді. Қолдау қызметі қарайды.',
    'Incorrect email or password.': 'Электрондық пошта немесе құпиясөз қате.', 'Book not found.': 'Кітап табылмады.', 'Order not found.': 'Тапсырыс табылмады.',
    'This email is already registered.': 'Бұл электрондық пошта тіркелген.', 'Address is required for delivery.': 'Жеткізу үшін мекенжай қажет.',
    'Choose a saved address or enter a new one.': 'Сақталған мекенжайды таңдаңыз немесе жаңасын енгізіңіз.', 'This book is in stock, you can order it now.': 'Бұл кітап қоймада бар, тапсырыс бере аласыз.',
    'Saved address not found for this customer.': 'Бұл сатып алушының сақталған мекенжайы табылмады.', 'Customer not found. Create an order first.': 'Сатып алушы табылмады. Алдымен тапсырыс жасаңыз.',
    'The message is too short. Please write at least 10 characters so we can understand the problem.': 'Хабарлама тым қысқа. Мәселені түсінуіміз үшін кемінде 10 таңба жазыңыз.',
    'Please describe the problem in words, not only with digits or symbols.': 'Мәселені тек сандармен не таңбалармен емес, сөзбен сипаттаңыз.',
    'Links are not allowed in a support request. Please remove the link and describe the problem in words.': 'Өтініште сілтемеге рұқсат жоқ. Сілтемені өшіріп, мәселені сөзбен сипаттаңыз.',
    'Please remove rude words or insults. We will gladly help if you describe the problem politely.': 'Дөрекі сөздер мен қорлауды алып тастаңыз. Мәселені сыпайы сипаттасаңыз, көмектесеміз.',
    'The message looks like spam (repeated characters or words). Please write a normal description of the problem.': 'Хабарлама спамға ұқсайды (таңбалар не сөздер қайталанған). Мәселені қалыпты түрде сипаттаңыз.',
    'James Clear explains how small routines can build into lasting change. The book offers practical methods for creating helpful habits, changing your environment, and making progress easier to repeat.': 'Джеймс Клир шағын әдеттердің тұрақты өзгерістерге қалай әкелетінін түсіндіреді. Кітап пайдалы әдеттерді қалыптастыру, ортаны өзгерту және жетістікті қайталау жолдарын ұсынады.',
    'After meeting a young prince in the desert, a stranded pilot hears about the prince\'s travels between planets. Their conversations explore friendship, responsibility, and how people learn to value one another.': 'Шөлде кішкентай ханзадамен кездескен ұшқыш оның ғаламшарлар арасындағы сапарлары туралы әңгімесін тыңдайды. Олардың әңгімесі достық, жауапкершілік және бір-бірін бағалау туралы.',
    'Mukhtar Auezov\'s novel follows the poet and thinker Abai as he grows up on the Kazakh steppe. Through his life, the story portrays the customs, conflicts, and social changes of nineteenth-century Kazakh society.': 'Мұхтар Әуезовтің романы ақын әрі ойшыл Абайдың қазақ даласында өсуін баяндайды. Оның өмірі арқылы XIX ғасырдағы қазақ қоғамының салт-дәстүрі, қайшылықтары мен өзгерістері суреттеледі.',
    'Winston Smith lives in a state where the government monitors its citizens and rewrites the past. His quiet search for truth and personal freedom becomes a dangerous challenge to the ruling system.': 'Уинстон Смит үкіметі азаматтарды бақылап, өткенді қайта жазатын мемлекетте өмір сүреді. Оның шындық пен жеке еркіндікті іздеуі билікке қауіпті қарсылыққа айналады.',
    'On his eleventh birthday, Harry Potter learns that he is a wizard and begins life at Hogwarts. With new friends, he discovers the history of his family and a mystery connected to the school.': 'Он бірінші туған күнінде Гарри Поттер өзінің сиқыршы екенін біліп, Хогвартста оқи бастайды. Жаңа достарымен бірге отбасының тарихын және мектепке қатысты құпияны ашады.',
  },
};

// Переводы расширенного каталога (новые книги, категории, жанры) — в отдельном файле
Object.assign(bookTitles, CATALOG_BOOK_TITLES);
Object.assign(authorNames, CATALOG_AUTHORS);
Object.assign(phrases.ru, CATALOG_PHRASES.ru);
Object.assign(phrases.kk, CATALOG_PHRASES.kk);

@Injectable({ providedIn: 'root' })
export class LanguageService {
  private title = inject(Title);
  private readonly storageKey = 'online-book-shop-language';
  readonly current = signal<ShopLanguage>(this.readSavedLanguage());
  private routeTitle = ''; // английский заголовок текущей страницы (из app.routes.ts)

  constructor() {
    document.documentElement.lang = this.current();
  }

  /** Вызывает ShopTitleStrategy после каждого перехода: запоминаем заголовок и ставим перевод. */
  setRouteTitle(routeTitle: string): void {
    this.routeTitle = routeTitle;
    this.updateTitle();
  }

  setLanguage(value: string): void {
    if (value !== 'en' && value !== 'ru') return;
    this.current.set(value);
    localStorage.setItem(this.storageKey, value);
    document.documentElement.lang = value;
    this.updateTitle();
  }

  text(key: string): string {
    return translations[this.current()][key] ?? translations.en[key] ?? key;
  }

  tr(english: string): string {
    const whole = this.trOne(english);
    if (whole !== english || this.current() === 'en') return whole;
    // Ошибки сервера бывают из нескольких фраз подряд (например, требования к паролю):
    // если целиком строки нет в словаре — переводим каждое предложение отдельно
    const sentences = english.split(/(?<=[.!?])\s+/);
    return sentences.length > 1 ? sentences.map((s) => this.trOne(s)).join(' ') : whole;
  }

  private trOne(english: string): string {
    const lang = this.current();
    if (lang === 'en') {
      const source = Object.keys(phrases.ru).find((key) => phrases.ru[key] === english)
        ?? Object.keys(phrases.kk).find((key) => phrases.kk[key] === english);
      return source ?? english;
    }
    const source = phrases[lang][english] ? english : Object.keys(phrases.ru)
      .find((key) => phrases.ru[key] === english || phrases.kk[key] === english) ?? english;
    if (phrases[lang][source]) return phrases[lang][source];
    // Сообщения сервера с названием книги или числом внутри
    const notFound = english.match(/^Book (\S+) not found\.$/);
    if (notFound) return lang === 'ru' ? `Книга ${notFound[1]} не найдена.` : `${notFound[1]} кітабы табылмады.`;
    const onlyLeft = english.match(/^"(.+)": only (\d+) in stock\.$/);
    if (onlyLeft) {
      const name = this.bookTitle(onlyLeft[1]);
      return lang === 'ru' ? `«${name}»: в наличии только ${onlyLeft[2]} шт.` : `«${name}»: қоймада тек ${onlyLeft[2]} дана бар.`;
    }
    const soldOut = english.match(/^"(.+)" is out of stock\.$/);
    if (soldOut) {
      const name = this.bookTitle(soldOut[1]);
      return lang === 'ru' ? `«${name}» закончилась.` : `«${name}» таусылды.`;
    }
    const loginAction = english.match(/^Please log in to (.+)\.$/);
    if (loginAction) {
      const actions: Record<ShopLanguage, Record<string, string>> = {
        en: {},
        ru: { 'see your support requests': 'посмотреть обращения в поддержку', 'manage your waiting list': 'управлять списком ожидания', 'see your notifications': 'посмотреть уведомления', 'see your orders': 'посмотреть заказы', 'use your wishlist': 'использовать избранное', 'choose your favourite categories': 'выбрать любимые категории', 'see books picked for you': 'посмотреть подборку книг для вас' },
        kk: { 'see your support requests': 'қолдау өтініштерін көру', 'manage your waiting list': 'күту тізімін басқару', 'see your notifications': 'хабарландыруларды көру', 'see your orders': 'тапсырыстарды көру', 'use your wishlist': 'таңдаулыларды пайдалану', 'choose your favourite categories': 'сүйікті санаттарды таңдау', 'see books picked for you': 'сізге ұсынылған кітаптарды көру' },
      };
      return `${lang === 'ru' ? 'Войдите, чтобы' : 'Кіру қажет:'} ${actions[lang][loginAction[1]] ?? loginAction[1]}.`;
    }
    return source;
  }

  category(name: string | null): string {
    return name ? this.tr(name) : '';
  }

  bookTitle(title: string): string {
    return bookTitles[title]?.[this.current()] ?? title;
  }

  authorName(name: string): string {
    return authorNames[name]?.[this.current()] ?? name;
  }

  bookLanguageLabel(): string {
    return this.current() === 'ru' ? 'Язык издания:' : 'Book language:';
  }

  bookLanguages(languages: string[]): string {
    const russianNames: Record<string, string> = {
      English: 'Английский', Russian: 'Русский', Kazakh: 'Казахский',
    };
    return languages.map((name) => this.current() === 'ru' ? (russianNames[name] ?? name) : name).join(', ');
  }

  searchLabel(): string {
    return this.current() === 'ru' ? 'Поиск по названию или автору' : 'Search by title or author';
  }

  searchPlaceholder(): string {
    return this.current() === 'ru' ? 'Начните вводить название книги или имя автора' : 'Start typing a book title or author name';
  }

  authorSuggestionsLabel(): string {
    return this.current() === 'ru' ? 'Авторы' : 'Authors';
  }

  bookSuggestionsLabel(): string {
    return this.current() === 'ru' ? 'Книги' : 'Books';
  }

  searchNoSuggestions(): string {
    return this.current() === 'ru' ? 'Совпадений не найдено' : 'No matches found';
  }

  categoryList(names: string[]): string {
    return names.map((name) => this.category(name)).join(', ');
  }

  dateLocale(): string {
    return this.current() === 'en' ? 'en-US' : 'ru';
  }

  private readSavedLanguage(): ShopLanguage {
    const saved = localStorage.getItem(this.storageKey);
    return saved === 'ru' || saved === 'en' ? saved : 'en';
  }

  private updateTitle(): void {
    if (this.routeTitle) this.title.setTitle(this.tr(this.routeTitle));
  }
}

/**
 * Заголовок вкладки браузера. Стандартная стратегия Angular ставит английский title из
 * app.routes.ts уже после наших обработчиков, поэтому заменяем её своей: она отдаёт
 * заголовок в LanguageService, а тот показывает его на выбранном языке.
 */
@Injectable({ providedIn: 'root' })
export class ShopTitleStrategy extends TitleStrategy {
  private language = inject(LanguageService);

  override updateTitle(snapshot: RouterStateSnapshot): void {
    const routeTitle = this.buildTitle(snapshot);
    if (routeTitle) this.language.setRouteTitle(routeTitle);
  }
}
