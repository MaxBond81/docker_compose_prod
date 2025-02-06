from rest_framework import serializers

from logistic.models import Product, StockProduct, Stock


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе

    product = ProductSerializer

    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price', ]


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions', ]

    # настройте сериализатор для склада

    def create(self, validated_data):
        print(validated_data)
        print(self.context['request'].data)
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')
        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        for position in positions:
            StockProduct.objects.create(stock_id=stock.id, **position)

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        # мой способ:
        # for position_data in positions:
        #     StockProduct.objects.filter(stock_id=stock.id).update_or_create(
        #         stock=stock,
        #         product=position_data['product'],
        #         defaults={
        #             'quantity': position_data['quantity'],
        #             'price': position_data['price']
        #         }
        #     )

        #  способ эксперта:
        for position_data in positions:
            StockProduct.objects.update_or_create(
                stock=stock,
                product=position_data['product'],
                defaults={
                    'quantity': position_data['quantity'],
                    'price': position_data['price']
                })

        return stock
