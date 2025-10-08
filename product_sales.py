import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from datetime import timedelta

class SalesAnalyzer:
    def __init__(self, prod_sales_df):
        self.df = prod_sales_df
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])
        self.current_data = pd.DataFrame(self.df)
        self.current_chart_type = 'daily' 
        self.fig = None
        self.ax = None
        self.start_date = prod_sales_df['transaction_date'].min()
        self.end_date = prod_sales_df['transaction_date'].max()
        self.period_label = '(все данные)'
        self.setup_ui()

        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        
        # Создаем области для кнопок
        plt.subplots_adjust(bottom=0.35)
        # Кнопки выбора периода
        ax_week = plt.axes((0.15, 0.15, 0.12, 0.06))
        ax_month = plt.axes((0.3, 0.15, 0.12, 0.06))
        ax_quarter = plt.axes((0.45, 0.15, 0.12, 0.06))
        ax_all = plt.axes((0.6, 0.15, 0.12, 0.06))
        
        self.btn_week = Button(ax_week, '7 дней')
        self.btn_month = Button(ax_month, '30 дней')
        self.btn_quarter = Button(ax_quarter, '90 дней')
        self.btn_all = Button(ax_all, 'Все данные')

        # Кнопки типа графика
        ax_daily = plt.axes((0.15, 0.05, 0.12, 0.06))
        ax_weekly = plt.axes((0.3, 0.05, 0.12, 0.06))
        ax_monthly = plt.axes((0.45, 0.05, 0.12, 0.06))
        ax_category = plt.axes((0.6, 0.05, 0.12, 0.06))
        
        self.btn_daily = Button(ax_daily, 'По дням')
        self.btn_weekly = Button(ax_weekly, 'По неделям')
        self.btn_monthly = Button(ax_monthly, 'По месяцам')
        self.btn_category = Button(ax_category, 'По категориям')
        
        # Поля для ввода дат кастомных
        start_ax = plt.axes((0.77, 0.15, 0.08, 0.04))
        end_ax = plt.axes((0.77, 0.1, 0.08, 0.04))
        
        self.start_text = TextBox(start_ax, 'Начало', 
                                 initial=self.start_date)
        self.end_text = TextBox(end_ax, 'Конец', 
                               initial=self.end_date)
        
        # Кнопка применения дат
        apply_ax = plt.axes((0.77, 0.05, 0.08, 0.04))
        self.btn_apply = Button(apply_ax, 'Применить даты')
        self.btn_apply.on_clicked(self.apply_custom_dates)
        
        # Подключаем обработчики
        self.btn_week.on_clicked(lambda x: self.filter_data('week'))
        self.btn_month.on_clicked(lambda x: self.filter_data('month'))
        self.btn_quarter.on_clicked(lambda x: self.filter_data('quarter'))
        self.btn_all.on_clicked(lambda x: self.filter_data('all'))

        self.btn_daily.on_clicked(lambda x: self.plot_chart('daily'))
        self.btn_weekly.on_clicked(lambda x: self.plot_chart('weekly'))
        self.btn_monthly.on_clicked(lambda x: self.plot_chart('monthly'))
        self.btn_category.on_clicked(lambda x: self.plot_chart('category'))
        
        # Показываем начальный график
        self.filter_data('week')
        self.plot_chart('daily')

    def apply_custom_dates(self):
        """Применяет выбранные даты при нажатии кнопки"""
        try:
            start_date = pd.to_datetime(self.start_text.text)
            end_date = pd.to_datetime(self.end_text.text)
            if start_date > end_date:
                raise ValueError("Начальная дата не может быть больше конечной")
                
            self.current_data = self.df[
                (self.df['transaction_date'] >= start_date) & 
                (self.df['transaction_date'] <= end_date)
            ]
            self.period_label = f' ({end_date.strftime("%Y-%m-%d")} - {start_date.strftime("%Y-%m-%d")})'
            self.update_info()
            self.plot_chart(self.current_chart_type)

        except Exception as e:
            print(f"Ошибка: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Ошибка: {str(e)}', 
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, color='red')
            plt.draw()
        

    def filter_data(self, period):
        def period_filter(max_date, days):
            """Установка периода в зависимости от входных дней(неделя, месяц, сезон)
            """
            start_date = max_date - timedelta(days=days)
            self.current_data = self.df[self.df['transaction_date'] >= start_date]
            self.period_label = f' (последние {days} дней)'
            self.start_text.set_val(start_date.strftime('%Y-%m-%d'))
            self.end_text.set_val(max_date.strftime('%Y-%m-%d'))
        """Фильтрация данных по периоду"""
        max_date = pd.to_datetime(self.end_text.text)
        
        if period == 'week':
            period_filter(max_date, 7)
            
        elif period == 'month':
            period_filter(max_date, 30)

        elif period == 'quarter':
            period_filter(max_date, 90)

        else:  # all
            self.current_data = self.df
            self.period_label = ' (все данные)'
            self.start_text.set_val(self.start_date.strftime('%Y-%m-%d'))
            self.end_text.set_val(self.end_date.strftime('%Y-%m-%d'))
                
        self.update_info()
        self.plot_chart(self.current_chart_type)
        
    def plot_chart(self, chart_type):
        """Построение графика"""
        self.ax.clear()
        if self.current_data.empty:
            self.ax.text(0.5, 0.5, 'Нет данных для отображения', 
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=16)
            self.ax.set_title('Нет данных' + self.period_label, fontsize=16, fontweight='bold')
            plt.draw()
            return
            
        def period_filter_plot(period):
            if period == 'daily':
                sales_data = self.current_data.groupby(self.current_data['transaction_date'].dt.date)['summary_price'].sum()
            elif period == 'weekly':
                sales_data = self.current_data.groupby(self.current_data['transaction_date'].dt.to_period('W'))['summary_price'].sum()
            elif period == 'monthly':
                sales_data = self.current_data.groupby(self.current_data['transaction_date'].dt.to_period('M'))['summary_price'].sum()
            self.ax.bar(sales_data.index.astype(str), sales_data.values, color="#DA5FF0", alpha=0.95)
            self.ax.tick_params(axis='x', rotation=45)
        
        if chart_type == 'daily':
            title = 'Продажи по дням'
            period_filter_plot(chart_type)
            
        elif chart_type == 'weekly':
            title = 'Продажи по неделям'    
            period_filter_plot(chart_type)

        elif chart_type == 'monthly':
            title = 'Продажи по месяцам'
            period_filter_plot(chart_type)
            
        elif chart_type == 'category':
            # данные по категориям
            sales_data = self.current_data.groupby('category')['summary_price'].sum().sort_values(ascending=False)
            self.ax.bar(sales_data.index, sales_data.values, color='#96CEB4', alpha=0.95)
            title = 'Продажи по категориям'
            self.ax.tick_params(axis='x', rotation=45)
            
        self.ax.set_title(title + self.period_label, fontsize=16, fontweight='bold', pad=20)
        self.ax.set_ylabel('Сумма продаж, руб.', fontsize=12, fontweight='bold')
        self.ax.grid(axis='y', alpha=0.3)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))

        for i, bar in enumerate(self.ax.patches):
            height = bar.get_height()
            if height > 0:  
                self.ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                            f'{height:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        self.current_chart_type = chart_type
        plt.draw()

        
    def update_info(self):
        """Обновление информации о данных"""
        if not self.current_data.empty:
            total_sales = self.current_data['summary_price'].sum()
            avg_sale = self.current_data['summary_price'].mean()
            transactions = len(self.current_data)
            
            info_text = f"Транзакций: {transactions:,} | Общая сумма: {total_sales:,.0f} руб | Средний чек: {avg_sale:,.0f} руб"
            if hasattr(self, 'info_text'):
                self.info_text.remove()
            self.info_text = self.fig.text(0.5, 0.95, info_text, ha='center', fontsize=11, 
                                         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        
    def show(self):
        plt.show()

# Запуск 
def start(prod_sales_df):
    analyzer = SalesAnalyzer(prod_sales_df)
    analyzer.show()