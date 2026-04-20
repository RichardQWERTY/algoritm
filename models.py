"""
Модели данных для Django-проекта интернет-магазина
Этот файл содержит описание всех моделей в соответствии с ER-диаграммой
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Category(models.Model):
    """Категория товаров"""
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', args=[self.slug])


class Product(models.Model):
    """Товар"""
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Цена'
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество на складе'
    )
    available = models.BooleanField(default=True, verbose_name='Доступен')
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        blank=True,
        verbose_name='Изображение'
    )
    created_by = models.ForeignKey(
        User,
        related_name='products',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Добавил'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        indexes = [
            models.Index(fields=['available', 'category']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    def get_average_rating(self):
        """Средняя оценка товара"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_reviews_count(self):
        """Количество отзывов"""
        return self.reviews.count()


class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(
        User,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Покупатель'
    )
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    address = models.CharField(max_length=250, verbose_name='Адрес')
    postal_code = models.CharField(max_length=20, verbose_name='Индекс')
    city = models.CharField(max_length=100, verbose_name='Город')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    paid = models.BooleanField(default=False, verbose_name='Оплачен')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'Заказ #{self.id}'

    def get_total_cost(self):
        """Общая стоимость заказа"""
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """Позиция заказа"""
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Цена'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.id}'

    def get_cost(self):
        """Стоимость позиции"""
        return self.price * self.quantity


class Review(models.Model):
    """Отзыв на товар"""
    product = models.ForeignKey(
        Product,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ['user', 'product']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]

    def __str__(self):
        return f'Отзыв от {self.user.username} на {self.product.name}'


class Cart(models.Model):
    """Корзина покупок"""
    user = models.OneToOneField(
        User,
        related_name='cart',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name='Ключ сессии'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username}'
        return f'Корзина (анонимная) {self.session_key}'

    def get_total_cost(self):
        """Общая стоимость корзины"""
        return sum(item.get_cost() for item in self.items.all())

    def clear(self):
        """Очистить корзину"""
        self.items.all().delete()


class CartItem(models.Model):
    """Позиция корзины"""
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        Product,
        related_name='cart_items',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_cost(self):
        """Стоимость позиции"""
        return self.product.price * self.quantity
