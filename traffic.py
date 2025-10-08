import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, TextBox

class TrafficVisualizer:
    def __init__(self, traffic_df):
        self.data = traffic_df
        self.data['session_start'] = pd.to_datetime(self.data['session_start'])
        self.filter_type = 'channel'
        self.start_date = traffic_df['session_start'].min()
        self.end_date = traffic_df['session_start'].max()
        
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.25 )
        
        self.create_widgets()
        self.update_plot()
        
    def create_widgets(self):
        rax = plt.axes((0.15, 0.06, 0.1, 0.1))
        self.radio = RadioButtons(rax, ['канал', 'устройство'])
        self.radio.on_clicked(self.on_filter_change)
        
        # Поля для ввода дат
        start_ax = plt.axes((0.3, 0.12, 0.08, 0.04))
        end_ax = plt.axes((0.3, 0.06, 0.08, 0.04))
        
        self.start_text = TextBox(start_ax, 'Начало', 
                                 initial=self.start_date)
        self.end_text = TextBox(end_ax, 'Конец', 
                               initial=self.end_date)   

        # Кнопка обновления
        update_ax = plt.axes((0.4, 0.06, 0.1, 0.06))
        self.update_btn = Button(update_ax, 'Применить')
        self.update_btn.on_clicked(self.update_plot)
        
    def on_filter_change(self, label):
        self.filter_type = label
        self.update_plot()
        
    def on_date_change(self, text):
        self.update_plot()
        
    def update_plot(self):
        try:
            # Получение дат из текстовых полей
            start_date = pd.to_datetime(self.start_text.text)
            end_date = pd.to_datetime(self.end_text.text)

            self.start_text.set_val(start_date.strftime('%Y-%m-%d'))
            self.end_text.set_val(end_date.strftime('%Y-%m-%d'))
            
            # Фильтрация данных по дате
            filtered_data = self.data[
                (self.data['session_start'] >= start_date) & 
                (self.data['session_start'] <= end_date)
            ]
            
            # Группировка данных в зависимости от выбранного фильтра
            if self.filter_type == 'channel':
                grouped_data = filtered_data['channel'].value_counts()
                x_label = 'Каналы'
                title = 'Посетители с каналов'
            else:
                grouped_data = filtered_data['device'].value_counts()
                x_label = 'Устройства'
                title = 'Посетители с устройств'
            
            # Очистка графика
            self.ax.clear()
            
            # Создание столбчатой диаграммы
            colors = plt.cm.Set3(np.linspace(0, 1, len(grouped_data)))
            bars = self.ax.bar(grouped_data.index, grouped_data.values, color=colors)
            
            # Настройка графика
            self.ax.set_xlabel(x_label, fontsize=12)
            self.ax.set_ylabel('Трафик клиентов', fontsize=12)
            self.ax.set_title(f'{title}\n'
                             f'({start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")})', 
                             fontsize=14, fontweight='bold')
            
            # Добавление значений на столбцы
            for bar, value in zip(bars, grouped_data.values):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{value}', ha='center', va='bottom', fontweight='bold')

            # Настройка внешнего вида
            self.ax.grid(axis='y', alpha=0.3)
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=15, ha='right')
            self.ax.tick_params(axis='x', labelsize=10)
            
            plt.draw()
            
        except Exception as e:
            print(f"Ошибка: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Ошибка: {str(e)}', 
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, color='red')
            plt.draw()
    def show(self):
        plt.show()

def start(df):
    visualizer = TrafficVisualizer(df)
    visualizer.show()
