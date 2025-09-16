<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Лучшие практики дизайна панелей Streamlit

Создание эффективных и привлекательных панелей в Streamlit требует понимания как технических возможностей фреймворка, так и принципов хорошего UX/UI дизайна. В данном обзоре рассмотрим ключевые практики и паттерны, которые помогут создать профессиональные интерфейсы.

![Title slide for responsive UI design with Streamlit and Python](https://img.youtube.com/vi/qOn1vUvA5iA/maxresdefault.jpg)

Title slide for responsive UI design with Streamlit and Python

## Основы макетирования и структуры

### Использование колонок для организации контента

Одним из наиболее важных инструментов для создания структурированного интерфейса являются колонки. Streamlit предоставляет гибкую систему колонок, которая позволяет создавать профессиональные макеты:[^1][^2]

```python
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.write("Основной контент")
with col2:
    st.metric("Продажи", "1,234")
with col3:
    st.metric("Прибыль", "5,678")
```

Для адаптивного дизайна важно учитывать различные размеры экранов. Можно использовать разные пропорции колонок в зависимости от устройства.[^3][^4]

### Контейнеры для группировки элементов

Контейнеры помогают логически группировать связанные элементы интерфейса:[^2][^5]

```python
with st.container():
    st.subheader("Аналитика продаж")
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(data)
    with col2:
        st.bar_chart(data)
```


## Навигационные паттерны

### Сайдбар навигация

Сайдбар является классическим решением для навигации в Streamlit приложениях. Лучшие практики включают:[^6][^7][^8]

- Использование `streamlit-option-menu` для создания профессиональных меню[^7][^9]
- Применение иконок для улучшения визуального восприятия[^7]
- Группировка связанных разделов[^6]

```python
from streamlit_option_menu import option_menu

with st.sidebar:
    selected = option_menu(
        menu_title="Главное меню",
        options=["Главная", "Аналитика", "Настройки"],
        icons=["house", "graph-up", "gear"],
        menu_icon="cast",
        default_index=0,
    )
```

![Example of a clean and simple Streamlit sidebar navigation menu with four items, including an emoji, running locally.](https://pplx-res.cloudinary.com/image/upload/v1758045288/pplx_project_search_images/9f9e283112ae8c2c42a01e8d6821611fb0af3fe2.png)

Example of a clean and simple Streamlit sidebar navigation menu with four items, including an emoji, running locally.

### Многостраничные приложения

Для сложных приложений рекомендуется использовать архитектуру многостраничных приложений:[^10][^11][^12]

- Использование `st.Page` и `st.navigation` для максимальной гибкости[^11][^10]
- Создание директории `pages/` для простых случаев[^10]
- Общие элементы в основном файле как "рамка" для всех страниц[^11]


## Стилизация и темизация

### Пользовательские темы

Streamlit предоставляет мощные возможности темизации через файл `config.toml`:[^13][^14][^15]

```toml
[theme]
primaryColor = '#7792E3'
backgroundColor = '#273346'
secondaryBackgroundColor = '#B9F1C0'
textColor = '#FFFFFF'
font = 'sans serif'
```


### Кастомный CSS

Для более глубокой кастомизации можно использовать CSS:[^16][^17][^18]

```python
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Применение CSS
load_css('style.css')
```

Новые версии Streamlit позволяют использовать ключи элементов как CSS-классы:[^17][^16]

```python
st.button("Красная кнопка", key="red")
# CSS: .st-key-red { background-color: red; }
```


## Адаптивный дизайн

### Отзывчивый интерфейс

Современные панели должны корректно работать на различных устройствах:[^3][^4][^19]

- Использование относительных размеров колонок
- Адаптация количества колонок в зависимости от размера экрана
- Тестирование на мобильных устройствах

```python
# Адаптивные колонки
if st.session_state.get('screen_width', 1200) < 768:
    cols = st.columns(1)  # Мобильные устройства
else:
    cols = st.columns([2, 1, 1])  # Десктоп
```


## Производительность и оптимизация

### Кэширование данных

Правильное использование кэширования критически важно для производительности:[^1][^20][^21]

```python
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')

@st.cache_resource
def init_model():
    return load_model('model.pkl')
```


### Управление состоянием

Эффективное управление состоянием предотвращает ненужные перезапуски:[^22][^23][^24]

```python
# Инициализация состояния
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Использование колбэков
def increment():
    st.session_state.counter += 1

st.button('Увеличить', on_click=increment)
```


## Визуализация данных

### Эффективное отображение метрик

Streamlit предоставляет специальные компоненты для отображения KPI:[^18]

![Example of a Python interactive dashboard design using Streamlit showing multiple data visualizations and filters for exploratory data analysis.](https://img.youtube.com/vi/7yAw1nPareM/maxresdefault.jpg)

Example of a Python interactive dashboard design using Streamlit showing multiple data visualizations and filters for exploratory data analysis.

```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Выручка", "1.2M ₽", "12%")
with col2:
    st.metric("Пользователи", "1,234", "5%")
with col3:
    st.metric("Конверсия", "3.2%", "-0.5%")
```


### Интерактивные элементы

Использование виджетов для создания интерактивности:[^1][^19]

```python
# Фильтры в сайдбаре
with st.sidebar:
    date_range = st.date_input("Период", [datetime.now() - timedelta(30), datetime.now()])
    category = st.selectbox("Категория", ['Все', 'A', 'B', 'C'])
    
# Основная панель с результатами
filtered_data = filter_data(data, date_range, category)
st.plotly_chart(create_chart(filtered_data))
```


## Специализированные компоненты

### Библиотеки компонентов

Для расширения возможностей можно использовать сторонние библиотеки:[^25][^26]

- `streamlit-shadcn-ui` - современные UI компоненты[^25]
- `streamlit-navigation-bar` - продвинутая навигация[^9]
- `streamlit-option-menu` - стилизованные меню[^7]

![Streamlit Shadcn UI dashboard demonstrating a clean and modern layout with navigation, key metrics, and sales visualization.](https://pplx-res.cloudinary.com/image/upload/v1754757118/pplx_project_search_images/ad053af9a8d3433785f0c57225b2db34cb0ffab7.png)

Streamlit Shadcn UI dashboard demonstrating a clean and modern layout with navigation, key metrics, and sales visualization.

## Доступность и соответствие стандартам

### Принципы доступности

Хотя Streamlit еще не полностью соответствует стандартам доступности, важно следовать базовым принципам:[^27][^28]

- Использование контрастных цветов[^29]
- Добавление описаний к элементам
- Логическая структура навигации
- Поддержка клавиатурного управления


### Тестирование интерфейса

Регулярное тестирование на различных устройствах и браузерах помогает выявить проблемы с отображением и взаимодействием.[^3][^19]

## Архитектурные паттерны

### Модульная структура кода

Для больших приложений важна правильная организация кода:[^1][^19]

```python
# utils/layout.py
def create_sidebar():
    with st.sidebar:
        return create_navigation()

# utils/data.py
@st.cache_data
def load_dashboard_data():
    return fetch_data()

# main.py
from utils.layout import create_sidebar
from utils.data import load_dashboard_data
```


### Управление состоянием приложения

Централизованное управление состоянием через отдельные модули:[^22]

```python
# state_management.py
class AppState:
    @staticmethod
    def initialize():
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
    
    @staticmethod
    def update_user_data(key, value):
        st.session_state.user_data[key] = value
```


## Обработка ошибок и UX

### Graceful error handling

Правильная обработка ошибок улучшает пользовательский опыт:[^19]

```python
try:
    data = load_data()
    st.success("Данные загружены успешно")
except Exception as e:
    st.error(f"Ошибка загрузки данных: {str(e)}")
    st.info("Попробуйте обновить страницу")
```


### Индикаторы загрузки

Использование спиннеров и прогресс-баров для длительных операций:[^1]

```python
with st.spinner('Загрузка данных...'):
    data = expensive_operation()

progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
    time.sleep(0.01)
```


## Заключение

Создание эффективных панелей Streamlit требует баланса между функциональностью и эстетикой. Ключевые принципы включают логическую структуру, адаптивный дизайн, оптимизацию производительности и внимание к пользовательскому опыту. Использование современных компонентов и библиотек, правильное управление состоянием и следование принципам доступности помогают создавать профессиональные приложения, которые эффективно решают бизнес-задачи.
<span style="display:none">[^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^43][^44][^45][^46][^47][^48][^49][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72]</span>

<div style="text-align: center">⁂</div>

[^1]: https://dev-kit.io/blog/python/mastering-streamlit-creating-interactive-data-dashboards-with-ease

[^2]: https://dev.to/jamesbmour/streamlit-part-6-mastering-layouts-4hci

[^3]: https://www.toolify.ai/ai-news/enhance-your-streamlit-app-with-a-responsive-ui-727346

[^4]: https://discuss.streamlit.io/t/build-responsive-apps-based-on-different-screen-features/51625

[^5]: https://docs.streamlit.io/develop/api-reference/layout

[^6]: https://evidence.dev/learn/streamlit-sidebar

[^7]: https://pythonandvba.com/blog/the-easiest-way-to-insert-a-navigation-into-your-streamlit-app/

[^8]: https://www.youtube.com/watch?v=flFy5o-2MvI

[^9]: https://pypi.org/project/streamlit-navigation-bar/3.1.1/

[^10]: https://docs.streamlit.io/develop/concepts/multipage-apps/overview

[^11]: https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation

[^12]: https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app

[^13]: https://blog.streamlit.io/introducing-theming/

[^14]: https://dev.to/buildandcodewithraman/how-to-configure-themes-in-streamlit-4bb8

[^15]: https://docs.streamlit.io/develop/concepts/configuration/theming

[^16]: https://pythonandvba.com/blog/style_your_streamlit_app_with_custom_css/

[^17]: https://www.youtube.com/watch?v=jbJpAdGlKVY

[^18]: https://dev.to/barrisam/how-to-style-streamlit-metrics-in-custom-css-4h14

[^19]: https://megainterview.com/streamlit-best-practices/

[^20]: https://blog.streamlit.io/how-to-improve-streamlit-app-loading-speed/

[^21]: https://blog.streamlit.io/six-tips-for-improving-your-streamlit-app-performance/

[^22]: https://discuss.streamlit.io/t/state-management-best-practices/24735

[^23]: https://docs.streamlit.io/develop/concepts/architecture/session-state

[^24]: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state

[^25]: https://discuss.streamlit.io/t/new-component-streamlit-shadcn-ui-using-modern-ui-components-to-build-data-app/56390

[^26]: https://github.com/streamlit/component-template

[^27]: https://discuss.streamlit.io/t/508-compliance-for-streamlit/13579

[^28]: https://github.com/streamlit/streamlit/issues/8399

[^29]: https://blog.streamlit.io/accessible-color-themes-for-streamlit-apps/

[^30]: https://dev-kit.io/blog/python/streamlit-ui-development

[^31]: https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/

[^32]: https://panel.holoviz.org/how_to/streamlit_migration/layouts.html

[^33]: https://dev-kit.io/blog/python/streamlit-real-time-design-patterns-creating-interactive-and-dynamic-data-visualizations

[^34]: https://blog.streamlit.io/best-practices-for-building-genai-apps-with-streamlit/

[^35]: https://github.com/microsoft/Streamlit_UI_Template

[^36]: https://discuss.streamlit.io/t/streamlit-best-practices/57921

[^37]: https://python-textbook.pythonhumanities.com/05_streamlit/05_02_03_layout_design.html

[^38]: https://docs.streamlit.io/develop/concepts/design

[^39]: https://blog.datatraininglab.com/building-effective-dashboards-de81c3c45aeb

[^40]: https://discuss.streamlit.io/t/complex-lay-outs/64423

[^41]: https://www.figma.com/community/file/1166786573904778097/streamlit-design-system

[^42]: https://www.tzrconsulting.co.uk/post/designing-a-business-intelligence-dashboard-using-streamlit

[^43]: https://panel.holoviz.org/explanation/comparisons/compare_streamlit.html

[^44]: https://streamlit.io

[^45]: https://www.reddit.com/r/StreamlitOfficial/comments/1j5qe12/request_best_practices_for_hosting_multiple/

[^46]: https://www.youtube.com/watch?v=1ydOnGUAJxw

[^47]: https://discuss.streamlit.io/t/responsive-ui-streamlit/36125

[^48]: https://discuss.streamlit.io/t/css-styling/35243

[^49]: https://docs.streamlit.io/develop/api-reference/navigation/st.navigation

[^50]: https://discuss.streamlit.io/t/streamlit-responsive-ui/34879

[^51]: https://discuss.streamlit.io/t/applying-custom-css-to-manually-created-containers/33428

[^52]: https://discuss.streamlit.io/t/how-to-make-sidebar-as-navigation-bar/30650

[^53]: https://pythonandvba.com/blog/build-a-website-in-only-12-minutes-using-python-streamlit/

[^54]: https://www.insightbig.com/post/creating-a-crypto-dashboard-with-custom-css-in-streamlit

[^55]: https://discuss.streamlit.io/t/navigation-sidebar/39918

[^56]: https://www.streamoku.com/post/streamlit-analytics-dashboard-gaining-insights-into-your-applications-performance-and-user-engagement

[^57]: https://www.geeksforgeeks.org/python/creating-multipage-applications-using-streamlit/

[^58]: https://discuss.streamlit.io/t/streamlit-dashboard-performance/15166

[^59]: https://stackoverflow.com/questions/79586550/how-can-i-optimize-a-streamlit-dashboard-for-large-csv-files-to-improve-load-tim

[^60]: https://towardsdatascience.com/how-to-build-an-interconnected-multi-page-streamlit-app-3114c313f88f/

[^61]: https://discuss.streamlit.io/t/seeking-advice-for-streamlit-app-state-management-and-best-practices/80025

[^62]: https://www.youtube.com/watch?v=9n4Ch2Dgex0

[^63]: https://pub.towardsai.net/unlocking-the-power-of-session-state-in-streamlit-1-2-c7acda8dda6c

[^64]: https://discuss.streamlit.io/t/streamlit-optimization/50657

[^65]: https://docs.snowflake.com/en/developer-guide/streamlit/example-multi-page

[^66]: https://www.youtube.com/watch?v=qccakpz9yRs

[^67]: https://blog.streamlit.io/prototype-your-app-in-figma/

[^68]: https://discuss.streamlit.io/t/customize-theme/39156

[^69]: https://github.com/streamlit/theming-showcase-blue

[^70]: https://www.youtube.com/watch?v=sCqXieMcwDg

[^71]: https://streamlit.io/components

[^72]: https://docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders

