
## Этапы проекта:

### 1. [[Сбор данных]]

#### Описание
Основная задача на этом этапе — разработать парсеры для различных источников новостей, которые будут собирать данные, анализировать и сохранять их в структурированной форме для последующей обработки.

#### Источники данных:
- Telegram-каналы.
- Яндекс.Новости.
- Медуза.
- Риа Новости.
- Тинькофф Пульс.
- Отраслевые порталы (HackerNews, etc).

#### Что будет сделано:
- Реализация парсеров для автоматического сбора данных с различных новостных источников.
- Нормализация данных: обработка ссылок, извлечение сущностей (Named Entity Recognition), очистка текста от шума.
- Формирование структурированного датасета с новостями и сущностями, связанными с ними.
- Сохранение данных в базу (PostgreSQL).

#### Инструменты:
- Python (Beautiful Soup, Selenium).
- PostgreSQL для хранения данных.
- FastAPI для взаимодействия с базой данных.

---
 
### 2. [[Этап ML (машинное обучение)]]

#### Описание
На этом этапе мы исследуем и применим различные алгоритмы для анализа графов на основе новостных данных. Это включает кластеризацию, поиск синонимов, и предварительное изучение связи между новостями.

#### Алгоритмы и задачи:
- **PageRank** для оценки важности новостей или сущностей.
- **Louvain Method** для кластеризации графа и выявления сообществ.
- **[[SVD & LSA]]** для снижения размерности и выделения ключевых тем. 
- **Word2Vec/Doc2Vec** для работы с семантикой текста и синонимами.

#### Цели:
- Выявление ключевых сущностей, которые оказывают наибольшее влияние в новостном графе.
- Поиск и анализ скрытых связей между новостями.
- Работа с синонимами и разрешение случаев, когда одно событие описывается разными словами.

#### Ожидаемые результаты:
- Кластеры новостей по темам или событиям.
- Семантические связи между сущностями и новостями.
- База данных с метаинформацией о новостях (вес сущностей, связи, тематическая принадлежность).

#### Инструменты:
- NetworkX, PyTorch Geometric.
- FastAPI для интеграции ML моделей с API.

---

### 3. [[Этап DL  (глубокое обучение)]]

#### Описание
На данном этапе будет проведена реализация глубоких нейронных сетей для решения задач на графе новостей, таких как предсказание связей (link prediction), классификация узлов (node classification) и entity matching.

#### Задачи и модели:
1. **Link Prediction**:
   - Модель для предсказания потенциальных связей между новостями и сущностями.
   - Алгоритмы: GCN (Graph Convolutional Networks), GraphSAGE.

2. **Node Classification**:
   - Классификация новостей по темам и выявление фейковых новостей.
   - Модели: GCN, Graph Attention Networks (GAT).

3. **Entity Matching**:
   - Поиск новостей, относящихся к одному событию, несмотря на разную формулировку.
   - Алгоритмы: Siamese Networks, Sentence-BERT для сравнения новостей.

4. **LLM + Граф**:
   - Ответы на вопросы, используя граф новостей и LLM для интерпретации данных.
   - GPT или другие модели для генерации ответов на сложные вопросы о новостях.

#### Ожидаемые результаты:
- Предсказание новых связей между новостями и сущностями.
- Автоматическая классификация новостей по категориям.
- Модель для поиска и идентификации схожих статей.
- Интерпретация графа новостей и выдача ответов на вопросы.

#### Инструменты:
- PyTorch Geometric, StellarGraph.
- HuggingFace Transformers для работы с языковыми моделями.
- FastAPI для интеграции моделей в сервисы.

---

### 4. Описание сервиса

#### Архитектура и инфраструктура:
- **Backend:** FastAPI для взаимодействия с базой данных и моделями.
- **Frontend:** React для построения пользовательских интерфейсов.
- **База данных:** MongoDB для хранения новостей и их метаинформации.
- **Модели:** GNN для анализа новостей, языковые модели для обработки текстов.
- **Микросервисы:** Использование Docker и Kubernetes для развертывания и масштабирования.

---

### 5. Реализация сервисов
[[Идеи сервисов]]

#### Основные сервисы:

1. **Мониторинг упоминаемости сущностей**:
   - Пользователи могут отслеживать упоминания интересующих их компаний, персон или событий в новостях.
   - Уведомления через веб-приложение, Telegram-бот или email.

2. **Оценка отношения (сентимента) к событиям**:
   - Анализ тональности новостей и отслеживание динамики отношения к сущностям (компании, продукты, политики).
   - Автоматические уведомления о резком изменении сентимента.

3. **Поиск схожих новостей (Entity Matching)**:
   - Поиск статей и новостей, относящихся к одному событию, с возможностью их хронологической визуализации.

4. **Предсказание влияния новостей (Link Prediction)**:
   - Прогнозирование новых связей между новостями и сущностями на основе анализа графа.

5. **Ответы на вопросы по графу (Graph + LLM)**:
   - Пользователь вводит вопрос, система анализирует граф и использует LLM для формирования ответа.

6. **API для разработчиков**:
   - REST/GraphQL API для интеграции данных и аналитики с внешними сервисами.

---

### 6. Монетизация и бизнес-ценность 
Куда можно развивать проект
- **Финансовые компании:** Анализ новостей для прогнозирования влияния на рынки и компании.
- **PR-агентства:** Мониторинг упоминаний брендов и оценка отношения к ним в медиа.
- **Медиа:** Быстрый доступ к аналитике новостей, прогнозирование трендов.
- **Разработчики:** Интеграция API для создания собственных сервисов на основе новостного графа.

---

### TODO:
- [ ] Организация репозитория с README на GitHub.
- [ ] Ресерч по алгоритмам и решениям для DL/ML в контексте новостных графов.
- [ ] Реализация парсеров для различных новостных источников.
- [ ] Интеграция ML и DL моделей в сервисы.
- [ ] Разработка веб-приложений и ботов для взаимодействия с пользователями.