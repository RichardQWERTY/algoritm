# Проектирование моделей данных для Django-проекта

## Описание проекта
Веб-приложение для управления каталогом товаров (интернет-магазин)

## Сущности (модели)

### 1. User (Пользователь)
Встроенная модель Django `django.contrib.auth.models.User`
- id (PK)
- username
- email
- password
- first_name
- last_name
- date_joined

### 2. Category (Категория товаров)
- id (PK)
- name (CharField, max_length=200) - название категории
- slug (SlugField, unique=True) - URL-friendly название
- description (TextField, blank=True) - описание категории
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 3. Product (Товар)
- id (PK)
- name (CharField, max_length=200) - название товара
- slug (SlugField, unique=True)
- description (TextField) - описание товара
- price (DecimalField, max_digits=10, decimal_places=2) - цена
- stock (PositiveIntegerField) - количество на складе
- available (BooleanField, default=True) - доступен для заказа
- category (ForeignKey → Category) - категория товара
- image (ImageField, blank=True) - изображение товара
- created_by (ForeignKey → User) - кто добавил товар
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 4. Order (Заказ)
- id (PK)
- user (ForeignKey → User) - покупатель
- first_name (CharField, max_length=100)
- last_name (CharField, max_length=100)
- email (EmailField)
- address (CharField, max_length=250)
- postal_code (CharField, max_length=20)
- city (CharField, max_length=100)
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)
- paid (BooleanField, default=False) - оплачен ли заказ
- status (CharField, choices) - статус заказа (новый, в обработке, отправлен, доставлен)

### 5. OrderItem (Позиция заказа)
- id (PK)
- order (ForeignKey → Order) - заказ
- product (ForeignKey → Product) - товар
- price (DecimalField, max_digits=10, decimal_places=2) - цена на момент заказа
- quantity (PositiveIntegerField) - количество

### 6. Review (Отзыв)
- id (PK)
- product (ForeignKey → Product) - товар
- user (ForeignKey → User) - автор отзыва
- rating (PositiveSmallIntegerField, choices=1-5) - оценка
- comment (TextField) - текст отзыва
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 7. Cart (Корзина)
- id (PK)
- user (ForeignKey → User, null=True, blank=True) - пользователь (может быть анонимным)
- session_key (CharField, max_length=40, null=True) - для анонимных пользователей
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 8. CartItem (Позиция корзины)
- id (PK)
- cart (ForeignKey → Cart) - корзина
- product (ForeignKey → Product) - товар
- quantity (PositiveIntegerField) - количество

## Связи между моделями

### One-to-Many (ForeignKey):
1. **Category → Product** (одна категория содержит много товаров)
2. **User → Product** (один пользователь может добавить много товаров)
3. **User → Order** (один пользователь может сделать много заказов)
4. **Order → OrderItem** (один заказ содержит много позиций)
5. **Product → OrderItem** (один товар может быть в разных заказах)
6. **Product → Review** (у одного товара может быть много отзывов)
7. **User → Review** (один пользователь может оставить много отзывов)
8. **User → Cart** (у пользователя одна корзина)
9. **Cart → CartItem** (корзина содержит много позиций)
10. **Product → CartItem** (товар может быть в разных корзинах)

## ER-диаграмма (текстовое представление)

```
┌─────────────┐
│    User     │
│  (Django)   │
└──────┬──────┘
       │
       │ 1:N
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│   Product   │    │    Order    │
│             │    │             │
│ created_by  │    │    user     │
└──────┬──────┘    └──────┬──────┘
       │                  │
       │ N:1              │ 1:N
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│  Category   │    │  OrderItem  │
│             │    │             │
└─────────────┘    │   order     │
                   │   product   │
                   └─────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       ▼
┌─────────────┐
│   Review    │
│             │
│    user     │
│   product   │
└──────┬──────┘
       │ N:1
       ▼
┌─────────────┐
│   Product   │
└─────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:1
       ▼
┌─────────────┐
│    Cart     │
│             │
│    user     │
└──────┬──────┘
       │ 1:N
       ▼
┌─────────────┐
│  CartItem   │
│             │
│    cart     │
│   product   │
└──────┬──────┘
       │ N:1
       ▼
┌─────────────┐
│   Product   │
└─────────────┘
```

## Индексы и ограничения

### Уникальные ограничения:
- Category.slug - уникальный
- Product.slug - уникальный

### Составные уникальные ограничения:
- Review: уникальная пара (user, product) - один пользователь может оставить только один отзыв на товар

### Индексы для оптимизации:
- Product.category (ForeignKey автоматически создаёт индекс)
- Product.available + Product.category (для фильтрации доступных товаров)
- Order.user + Order.created_at (для истории заказов)
- Review.product (для быстрого получения отзывов)

## Валидация данных

### Product:
- price > 0
- stock >= 0
- name не пустое

### Review:
- rating от 1 до 5
- один отзыв от пользователя на товар

### OrderItem:
- quantity > 0
- price > 0

### CartItem:
- quantity > 0

## Методы моделей

### Product:
- `get_absolute_url()` - URL товара
- `get_average_rating()` - средняя оценка
- `get_reviews_count()` - количество отзывов

### Order:
- `get_total_cost()` - общая стоимость заказа

### Cart:
- `get_total_cost()` - общая стоимость корзины
- `clear()` - очистить корзину

## Примечания для реализации

1. Использовать `django.contrib.auth` для User
2. Для изображений установить `Pillow`
3. Настроить `MEDIA_ROOT` и `MEDIA_URL` для загрузки изображений
4. Использовать `django-cleanup` для автоматического удаления файлов
5. Добавить `__str__()` методы для всех моделей
6. Использовать `select_related()` и `prefetch_related()` для оптимизации запросов
