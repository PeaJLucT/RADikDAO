import pandas as pd
import product_sales as ps
import traffic as tr
import in_stock as ist
from datetime import datetime

# Загрузка данных и их передача в файл product_sales.csv для дальнейшего анализа
def product_sales_data_edit():
    try:
        sales_df = pd.read_csv('sales.csv', sep=',', encoding='utf-8')        
        products_df = pd.read_csv('products.csv', sep=',', encoding='utf-8')  
        prod_sales_df = pd.DataFrame()                                        
        prod_sales_df = sales_df[['transaction_date', 'product_id', 'payment_method', 'quantity']].merge(
            products_df[['product_id', 'category', 'price']], 
            on='product_id', 
            how='left')
        prod_sales_df['summary_price'] = prod_sales_df['price'] * prod_sales_df['quantity']
        prod_sales_df['transaction_date'] = pd.to_datetime(prod_sales_df['transaction_date'])
        prod_sales_df = prod_sales_df.sort_values('transaction_date', ascending=False)
        print('Сохраняем')
        prod_sales_df.to_csv('product-sales.csv', index=False, encoding='utf-8')
    except Exception as e:
        print(f"Ошибка загрузки файлов: {e}")
 

#Загрузка данных и их передача в файл trafficend.csv для дальнейшего анализа
def traffic_edit():
    try:
        traffic_df = pd.read_csv('traffic.csv', sep=',', encoding='utf-8')
        trafficend = pd.DataFrame()
        trafficend = traffic_df[['customer_id', 'channel', 'session_start', 'device']].copy()
        trafficend.to_csv('trafficend.csv', index=False, encoding='utf-8')
    except Exception as e:
        print(f"Ошибка загрузки файлов: {e}")
 

#Загрузка данных для остатков
def in_stock_edit():
    try:
        inventory_df = pd.read_csv('inventory.csv', sep=',', encoding='utf-8')
        products_df = pd.read_csv('products.csv', sep=',', encoding='utf-8')
        sales_df = pd.read_csv('sales.csv', sep=',', encoding='utf-8')
    
        inventory_df['last_updated'] = pd.to_datetime(inventory_df['last_updated'])
        sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'])
        
        original_df = inventory_df.merge(
            products_df[['product_id', 'product_name', 'category']], 
            on='product_id', 
            how='left'
        )
        # total_rows = len(original_df)
        # print(f"В стоке обработано - {total_rows} товаров")
        return original_df, sales_df
    except Exception as e:
        print(f"Ошибка загрузки файлов: {e}")

#Загрузка данных для возвратов
def returns_edit():
    returns = pd.read_csv('returns.csv')
    sales = pd.read_csv('sales.csv')
    returns_with_quantity = returns.merge(
        sales[['transaction_id', 'quantity', 'customer_id']],
        left_on='transaction_id',
        right_on='transaction_id',
        how='left'
        )
    # Первая таблица
    # Общее количество купленных товаров по клиентам
    customer_orders = sales.groupby('customer_id')['quantity'].sum().reset_index()
    customer_orders.columns = ['customer_id', 'orders_value']
    # Количество возвращенных товаров по клиентам
    customer_returns = returns_with_quantity.groupby('customer_id')["quantity"].sum().reset_index()
    customer_returns.columns = ['customer_id', 'returns_value']
    # Объединяем и
    customer_stats = customer_orders.merge(customer_returns, on='customer_id', how='left')
    customer_stats['returns_value'] = customer_stats['returns_value'].fillna(0)
    # Процент выкупа
    customer_stats['percent_buyout'] = (
            (customer_stats['orders_value'] - customer_stats['returns_value']) /
            customer_stats['orders_value'] * 100
    ).round(2)

    # ВТОРАЯ ТАБЛИЦА
    # Количество возвратов по товарам
    product_returns = returns_with_quantity.groupby('product_id')['quantity'].sum().reset_index()
    product_returns.columns = ['product_id', 'value_return']

    # Самая популярная причина возврата
    def get_most_common_reason(group):
        if group['reason'].empty:
            return 'No returns'
        return group['reason'].mode()[0]

    common_reasons = returns.groupby('product_id').apply(
        get_most_common_reason,
        include_groups=False
    ).reset_index()
    common_reasons.columns = ['product_id', 'common_cause']


    # Объединяем
    product_stats = product_returns.merge(common_reasons, on='product_id', how='outer')
    product_stats['value_return'] = product_stats['value_return'].fillna(0)
    product_stats['common_cause'] = product_stats['common_cause'].fillna('No returns')

    customer_stats_filename = f'customer_returns_stats.csv'
    product_stats_filename = f'product_returns_stats.csv'

    # Сохраняем таблицы
    customer_stats.to_csv(customer_stats_filename, index=False, encoding='utf-8')
    product_stats.to_csv(product_stats_filename, index=False, encoding='utf-8')

    print(f"\nКолонки после объединения:")
    print(returns_with_quantity.columns.tolist())
    print(customer_orders.columns.tolist())
    print(customer_returns.columns.tolist())
    print(customer_stats.columns.tolist())

if __name__ == "__main__":
    while True:
        
        print("\nВыберите график:")
        print("1 - График продаж товаров")
        print("2 - График прихода трафика")
        print("3 - Остатки товаров")
        print('9 - Обновление таблиц с данными для их актуализации') 
        print("0 - Выход")
        choice = input("Введите номер: ").strip()

        if choice == '1':
            prod_sales_df = pd.read_csv('product-sales.csv')
            ps.start(prod_sales_df) # открытие графика продуктов/продаж
        elif choice == '2':
            trafficend = pd.read_csv('trafficend.csv')
            tr.start(trafficend)
        elif choice == '3':
            ist.start(in_stock_edit())
        elif choice == '9':
            product_sales_data_edit() #  создание таблицы для product-sales
            traffic_edit()        #создание таблицы для трафика


        elif choice == '0':
            print("Выход из программы")
            break


