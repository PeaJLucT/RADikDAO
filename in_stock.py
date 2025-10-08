import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox, Slider
from datetime import datetime, timedelta

class InventoryAnalyzer:
    def __init__(self, orig_df, sales_df):
        self.original_df = orig_df
        self.sales_df = sales_df
        self.analysis_df = self.original_df.copy()
        self.fig = None
        self.ax = None
        self.scroll_position = 0
        self.visible_rows = 15
        self.total_rows = 0
        
        self.calculate_stockout_time(sales_df)
        self.setup_ui()

        self.scroll_text = self.fig.text(0.1, 0.08, '', ha='left', fontsize=11,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
        
        self.stats_text = self.fig.text(0.5, 0.08, '', ha='center', fontsize=11,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))

    def calculate_stockout_time(self, sales_df):
        """Расчет времени до истощения запасов"""
        time_to_stockout_hours = []
        urgency_levels = []
        
        for idx, row in self.original_df.iterrows():
            product_id = row['product_id']
            current_stock = row['stock_quantity']
            
            one_week_ago = datetime.now() - timedelta(days=7)
            product_sales = sales_df[
                (sales_df['product_id'] == product_id) & 
                (sales_df['transaction_date'] >= one_week_ago)
            ]
            
            if len(product_sales) == 0:
                time_to_stockout_hours.append(9999)
                urgency_levels.append('Низкий')
                continue
            
            total_sold_week = product_sales['quantity'].sum()
            hours_in_week = 7 * 24
            avg_sales_per_hour = total_sold_week / hours_in_week
            
            if avg_sales_per_hour <= 0:
                time_to_stockout_hours.append(9999)

                urgency_levels.append('Низкий')
            else:
                hours_until_stockout = current_stock / avg_sales_per_hour
                time_to_stockout_hours.append(hours_until_stockout)
                
                if hours_until_stockout <= 24:
                    urgency_levels.append('Критический')
                elif hours_until_stockout <= (24 * 7):
                    urgency_levels.append('Средний')
                else:
                    urgency_levels.append('Низкий')
        
        self.original_df['time_to_stockout_hours'] = time_to_stockout_hours
        self.original_df['urgency_level'] = urgency_levels
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.suptitle('АНАЛИЗ ОСТАТКОВ ТОВАРОВ', fontsize=16, fontweight='bold', y=0.95)
        
        plt.subplots_adjust(bottom=0.25)
        
        # Поле поиска по ID
        search_ax = plt.axes((0.2, 0.15, 0.25, 0.05))
        self.search_text = TextBox(search_ax, 'Поиск по ID:', initial='')
        self.search_text.on_submit(self.on_search_change)
        
        critical_ax = plt.axes((0.63, 0.15, 0.12, 0.05))
        self.critical_btn = Button(critical_ax, 'Критические')
        self.critical_btn.on_clicked(self.show_critical_items)
        
        all_ax = plt.axes((0.76, 0.15, 0.12, 0.05))
        self.all_btn = Button(all_ax, 'Все товары')
        self.all_btn.on_clicked(self.show_all_items)
        
        # Слайдер для скроллинга (инвертированный визуально)
        slider_ax = plt.axes([0.92, 0.25, 0.02, 0.6])
        self.slider = Slider(slider_ax, '', 0, 1, valinit=1, orientation='vertical')
        self.slider.on_changed(self.on_slider_change)
        
        # Кнопки для скроллинга (поменял местами)
        up_ax = plt.axes([0.92, 0.85, 0.02, 0.03])
        self.up_btn = Button(up_ax, '▲')
        self.up_btn.on_clicked(self.scroll_up)
        
        down_ax = plt.axes([0.92, 0.22, 0.02, 0.03])
        self.down_btn = Button(down_ax, '▼')
        self.down_btn.on_clicked(self.scroll_down)
        
        self.display_table()
    
    def get_visible_data(self):
        """Получение данных для текущей видимой области"""
        start_idx = self.scroll_position
        end_idx = min(start_idx + self.visible_rows, self.total_rows)
        return self.analysis_df.iloc[start_idx:end_idx]
    
    def display_table(self):
        """Отображение таблицы с текущей позицией скролла"""
        self.ax.clear()
        
        visible_data = self.get_visible_data()
        
        if visible_data.empty:
            self.ax.text(0.5, 0.5, 'Нет данных для отображения', 
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=14)
            plt.draw()
            return
        
        table_data = []
        headers = ['Название товара', 'Склад', 'Остаток', 'Время до истощения', 'Уровень срочности']
        
        for idx, row in visible_data.iterrows():
            time_display = self.format_time_display(row['time_to_stockout_hours'])
            
            table_data.append([
                row['product_name'],
                row['warehouse_id'],
                f"{int(row['stock_quantity'])} шт",
                time_display,
                row['urgency_level']
            ])
        
        # Создаем таблицу
        table = self.ax.table(
            cellText=table_data,
            colLabels=headers,
            cellLoc='center',
            loc='center',
            bbox=[0.02, 0.15, 0.95, 0.85]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.0)
        
        # Цветовое кодирование
        for i in range(1, len(table_data) + 1):
            urgency_level = table_data[i-1][4]

            cell = table[(i, 4)]
            
            if urgency_level == 'Критический':
                cell.set_facecolor('#FF6B6B')
            elif urgency_level == 'Средний':
                cell.set_facecolor('#FFD166')
            else:
                cell.set_facecolor('#06D6A0')
        
        self.ax.axis('off')
        
        # Информация о скроллинге и статистика
        self.scroll_text.remove()
        self.stats_text.remove()
        total_items = len(self.analysis_df)
        critical_count = len(self.analysis_df[self.analysis_df['urgency_level'] == 'Критический'])
        scroll_info = f"Позиция: {self.scroll_position + 1}-{min(self.scroll_position + self.visible_rows, total_items)} из {total_items}"
        stats_info = f"Всего товаров: {total_items} | Критических: {critical_count}"
        
        self.scroll_text = self.fig.text(0.2, 0.08, scroll_info, ha='left', fontsize=11,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
        
        self.stats_text = self.fig.text(0.5, 0.08, stats_info, ha='center', fontsize=11,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
        
        # Обновляем слайдер (инвертированно)
        max_scroll = max(0, self.total_rows - self.visible_rows)
        if max_scroll > 0:
            # Инвертируем значение для визуального эффекта
            slider_val = 1 - (self.scroll_position / max_scroll)
            self.slider.eventson = False
            self.slider.set_val(slider_val)
            self.slider.eventson = True
        
        plt.draw()
    
    def on_slider_change(self, val):
        """Обработчик изменения слайдера (инвертированный)"""
        max_scroll = max(0, self.total_rows - self.visible_rows)
        if max_scroll > 0:
            # Инвертируем значение обратно
            new_position = int((1 - val) * max_scroll)
            if new_position != self.scroll_position:
                self.scroll_position = new_position
                self.display_table()
    
    def scroll_up(self, event):
        """Прокрутка вверх"""
        if self.scroll_position > 0:
            self.scroll_position -= 1
            self.display_table()
    
    def scroll_down(self, event):
        """Прокрутка вниз"""
        max_scroll = max(0, self.total_rows - self.visible_rows)
        if self.scroll_position < max_scroll:
            self.scroll_position += 1
            self.display_table()
    
    def format_time_display(self, hours):
        """Форматирование времени в читаемый вид"""
        if pd.isna(hours) or hours == 9999:
            return "Нет продаж"
        elif hours >= 24:
            days = hours / 24
            if days > 30:
                return "> 30 дней"
            return f"{days:.1f} дн."
        else:
            return f"{hours:.1f} ч."
    
    def on_search_change(self, text):
        """Поиск товаров по ID"""
        search_term = text.strip()
        
        if not search_term:
            # Если поиск пустой, показываем все товары
            self.analysis_df = self.original_df.copy()
        else:
            try:
                search_id = int(search_term)
                self.analysis_df = self.original_df[self.original_df['product_id'] == search_id].copy()
            except ValueError:
                # Если ввели не число, ищем по названию товара
                mask = self.original_df['product_name'].str.lower().str.contains(search_term.lower(), na=False)
                self.analysis_df = self.original_df[mask].copy()
        
        self.total_rows = len(self.analysis_df)
        self.scroll_position = 0
        self.display_table()
        # print(f"Поиск: '{search_term}' - найдено {self.total_rows} товаров")
    
    def show_critical_items(self, event):
        """Показать только критические товары (отсортированные по времени)"""
        critical_df = self.original_df[self.original_df['urgency_level'] == 'Критический']
        critical_df = critical_df.sort_values('time_to_stockout_hours', ascending=True)
        self.analysis_df = critical_df.copy()
        self.total_rows = len(self.analysis_df)
        self.scroll_position = 0
        self.display_table()
        # print(f"Показаны критические товары: {self.total_rows} шт, отсортированы по срочности")
    
    def show_all_items(self, event):
        """Показать все товары"""
        self.analysis_df = self.original_df.copy()
        self.total_rows = len(self.analysis_df)
        self.scroll_position = 0
        self.display_table()

    def show(self):
        plt.show()


# Запуск приложения
def start(df):
    analyzer = InventoryAnalyzer(df[0], df[1])
    analyzer.show()
