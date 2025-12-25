"""
Initialize legal documents (Privacy Policy and Terms of Service)
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.core.models_legal import LegalDocument
from datetime import datetime


def create_privacy_policy():
    """Create Privacy Policy document"""
    
    privacy_policy_content = {
        'en': """# Privacy Policy

**Effective Date:** {date}
**Version:** 1.0

## Introduction

Welcome to Sportlink. We respect your privacy and are committed to protecting your personal data. This privacy policy explains how we collect, use, and safeguard your information when you use our mobile application and services.

## Information We Collect

### Personal Information
We collect the following personal information:
- **Account Information:** Name, phone number, email address, nickname
- **Profile Information:** Age, gender, city, profile picture
- **Sports Preferences:** Favorite sports, experience levels, preferred equipment
- **Location Data:** Your location to help find nearby courts and opponents

### Usage Information
- **Booking History:** Records of court bookings and reservations
- **Tournament Participation:** Registration and participation in tournaments
- **App Usage:** How you interact with our app and services

## How We Use Your Information

We use your information for the following purposes:

### 1. Opponent Matching
We analyze your sports preferences, experience level, and location to match you with suitable opponents for games and practice sessions.

### 2. Tournament Organization
We use your profile information to organize tournaments, create brackets, and manage tournament registrations.

### 3. Personalized Offers
Based on your activity and preferences, we provide:
- Personalized discount offers
- Recommended courts and facilities
- Special promotions for your favorite sports

### 4. Service Improvement
We analyze usage patterns to improve our app features and user experience.

### 5. Communication
We send you notifications about:
- Booking confirmations
- Tournament updates
- Special offers and promotions
- Important service announcements

## Data Sharing

**We do NOT share your personal data with third parties.** Your information is used exclusively within the Sportlink platform to provide and improve our services.

### Exceptions
We may disclose your information only in the following circumstances:
- **Legal Requirements:** When required by law or legal process
- **Safety:** To protect the rights, property, or safety of Sportlink, our users, or others
- **Business Transfer:** In the event of a merger, acquisition, or sale of assets

## Data Security

We implement appropriate technical and organizational measures to protect your personal data against unauthorized access, alteration, disclosure, or destruction.

### Security Measures Include:
- Encrypted data transmission (HTTPS/TLS)
- Secure password storage (hashing)
- Regular security audits
- Access controls and authentication

## Your Rights

You have the following rights regarding your personal data:

- **Access:** Request a copy of your personal data
- **Correction:** Update or correct inaccurate information
- **Deletion:** Request deletion of your account and data
- **Opt-out:** Unsubscribe from promotional communications
- **Data Portability:** Request your data in a portable format

To exercise these rights, contact us at: support@sportlink.tm

## Data Retention

We retain your personal data for as long as your account is active or as needed to provide services. If you delete your account, we will delete or anonymize your data within 30 days, except where retention is required by law.

## Children's Privacy

Sportlink is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13.

## Changes to This Policy

We may update this privacy policy from time to time. We will notify you of any significant changes by posting the new policy in the app and updating the "Effective Date" above.

## Contact Us

If you have questions about this privacy policy, please contact us:

**Email:** support@sportlink.tm
**Phone:** +993 65 XXX XXX
**Address:** Ashgabat, Turkmenistan

---

By using Sportlink, you acknowledge that you have read and understood this Privacy Policy.
""",
        'ru': """# Политика конфиденциальности

**Дата вступления в силу:** {date}
**Версия:** 1.0

## Введение

Добро пожаловать в Sportlink. Мы уважаем вашу конфиденциальность и стремимся защитить ваши персональные данные. Эта политика конфиденциальности объясняет, как мы собираем, используем и защищаем вашу информацию при использовании нашего мобильного приложения и услуг.

## Информация, которую мы собираем

### Персональная информация
Мы собираем следующую персональную информацию:
- **Информация об аккаунте:** Имя, номер телефона, адрес электронной почты, никнейм
- **Информация профиля:** Возраст, пол, город, фотография профиля
- **Спортивные предпочтения:** Любимые виды спорта, уровень опыта, предпочитаемое оборудование
- **Данные о местоположении:** Ваше местоположение для поиска ближайших площадок и соперников

### Информация об использовании
- **История бронирований:** Записи о бронировании площадок
- **Участие в турнирах:** Регистрация и участие в турнирах
- **Использование приложения:** Как вы взаимодействуете с нашим приложением

## Как мы используем вашу информацию

Мы используем вашу информацию для следующих целей:

### 1. Подбор соперников
Мы анализируем ваши спортивные предпочтения, уровень опыта и местоположение, чтобы подобрать вам подходящих соперников для игр и тренировок.

### 2. Организация турниров
Мы используем информацию вашего профиля для организации турниров, создания сеток и управления регистрацией.

### 3. Персонализированные предложения
На основе вашей активности и предпочтений мы предоставляем:
- Персонализированные скидки
- Рекомендации площадок и объектов
- Специальные акции для ваших любимых видов спорта

### 4. Улучшение сервиса
Мы анализируем модели использования для улучшения функций приложения и пользовательского опыта.

### 5. Коммуникация
Мы отправляем вам уведомления о:
- Подтверждениях бронирований
- Обновлениях турниров
- Специальных предложениях и акциях
- Важных объявлениях о сервисе

## Передача данных

**Мы НЕ передаем ваши персональные данные третьим лицам.** Ваша информация используется исключительно в рамках платформы Sportlink для предоставления и улучшения наших услуг.

### Исключения
Мы можем раскрыть вашу информацию только в следующих случаях:
- **Юридические требования:** Когда это требуется законом или судебным процессом
- **Безопасность:** Для защиты прав, собственности или безопасности Sportlink, наших пользователей или других лиц
- **Передача бизнеса:** В случае слияния, приобретения или продажи активов

## Безопасность данных

Мы применяем соответствующие технические и организационные меры для защиты ваших персональных данных от несанкционированного доступа, изменения, раскрытия или уничтожения.

### Меры безопасности включают:
- Шифрованную передачу данных (HTTPS/TLS)
- Безопасное хранение паролей (хеширование)
- Регулярные аудиты безопасности
- Контроль доступа и аутентификация

## Ваши права

У вас есть следующие права в отношении ваших персональных данных:

- **Доступ:** Запросить копию ваших персональных данных
- **Исправление:** Обновить или исправить неточную информацию
- **Удаление:** Запросить удаление вашего аккаунта и данных
- **Отказ:** Отписаться от рекламных сообщений
- **Переносимость данных:** Запросить ваши данные в переносимом формате

Для осуществления этих прав свяжитесь с нами: support@sportlink.tm

## Хранение данных

Мы храним ваши персональные данные до тех пор, пока ваш аккаунт активен или необходим для предоставления услуг. Если вы удалите свой аккаунт, мы удалим или анонимизируем ваши данные в течение 30 дней, за исключением случаев, когда хранение требуется по закону.

## Конфиденциальность детей

Sportlink не предназначен для детей младше 13 лет. Мы сознательно не собираем персональную информацию от детей младше 13 лет.

## Изменения в этой политике

Мы можем время от времени обновлять эту политику конфиденциальности. Мы уведомим вас о любых значительных изменениях, разместив новую политику в приложении и обновив дату вступления в силу выше.

## Свяжитесь с нами

Если у вас есть вопросы об этой политике конфиденциальности, пожалуйста, свяжитесь с нами:

**Email:** support@sportlink.tm
**Телефон:** +993 65 XXX XXX
**Адрес:** Ашхабад, Туркменистан

---

Используя Sportlink, вы подтверждаете, что прочитали и поняли эту Политику конфиденциальности.
""",
        'tk': """# Gizlinlik syýasaty

**Güýje giren senesi:** {date}
**Wersiýa:** 1.0

## Giriş

Sportlink-e hoş geldiňiz. Biz siziň gizlinligiňize hormat goýýarys we şahsy maglumatlaryňyzy goramaga ygrarlydyrys. Bu gizlinlik syýasaty, mobil programmamyzy we hyzmatlarymyzy ulananyňyzda maglumatlaryňyzy nädip ýygnaýandygymyzy, ulanýandygymyzy we goraýandygymyzy düşündirýär.

## Ýygnaýan maglumatlarymyz

### Şahsy maglumatlar
Biz aşakdaky şahsy maglumatlary ýygnaýarys:
- **Hasap maglumatlary:** Ady, telefon belgisi, e-poçta salgysy, lakam
- **Profil maglumatlary:** Ýaş, jyns, şäher, profil suraty
- **Sport islegleri:** Halaýan sport görnüşleri, tejribe derejesi, saýlanan enjamlar
- **Ýerleşiş maglumatlary:** Ýakyn meýdançalary we garşydaşlary tapmak üçin ýerleşişiňiz

### Ulanyş maglumatlary
- **Bronlaş taryhy:** Meýdança bronlaşlarynyň ýazgylary
- **Ýaryşa gatnaşmak:** Ýaryşlara hasaba alynmak we gatnaşmak
- **Programmany ulanmak:** Programmamyz bilen nähili gatnaşýandygyňyz

## Maglumatlaryňyzy nädip ulanýarys

Maglumatlaryňyzy aşakdaky maksatlar üçin ulanýarys:

### 1. Garşydaş saýlamak
Sport islegleriňizi, tejribe derejeňizi we ýerleşişiňizi seljermek arkaly oýunlar we türgenleşikler üçin size laýyk garşydaşlary saýlaýarys.

### 2. Ýaryş guramaçylygy
Ýaryşlary guramak, setkalary döretmek we hasaba alynmagy dolandyrmak üçin profil maglumatlaryňyzy ulanýarys.

### 3. Şahsylaşdyrylan teklipler
Işjeňligiňize we islegleriňize esaslanyp, biz hödürleýäris:
- Şahsylaşdyrylan arzanladyşlar
- Maslahat berilýän meýdançalar we desgalar
- Halaýan sport görnüşleriňiz üçin ýörite teklipler

### 4. Hyzmaty gowulandyrmak
Programma aýratynlyklaryny we ulanyjy tejribesini gowulandyrmak üçin ulanyş nusgalaryny seljermek.

### 5. Aragatnaşyk
Size aşakdaky habarnamalary iberýäris:
- Bronlaş tassyklamalary
- Ýaryş täzelenmeleri
- Ýörite teklipler we mahabatlar
- Möhüm hyzmat bildirişleri

## Maglumatlary paýlaşmak

**Biz şahsy maglumatlaryňyzy üçünji taraplara BERMEZÝÄRIS.** Maglumatlaryňyz diňe Sportlink platformasynda hyzmatlarymyzy bermek we gowulandyrmak üçin ulanylýar.

### Kadadan çykmalar
Maglumatlaryňyzy diňe aşakdaky ýagdaýlarda açyp bileris:
- **Kanuny talaplar:** Kanun ýa-da kazyýet işi tarapyndan talap edilende
- **Howpsuzlyk:** Sportlink-iň, ulanyjylarymyzyň ýa-da beýlekileriň hukuklaryny, emlägini ýa-da howpsuzlygyny goramak üçin
- **Işiň geçirilmegi:** Birleşme, satyn almak ýa-da emläk satmak ýagdaýynda

## Maglumatlaryň howpsuzlygy

Şahsy maglumatlaryňyzy rugsatsyz giriş, üýtgetme, açmak ýa-da ýok etmekden goramak üçin degişli tehniki we guramaçylyk çärelerini ulanýarys.

### Howpsuzlyk çäreleri:
- Şifrlenen maglumat geçirme (HTTPS/TLS)
- Howpsuz parol saklamak (heşleme)
- Yzygiderli howpsuzlyk barlaglary
- Giriş gözegçiligi we tassyklamak

## Siziň hukuklaryňyz

Şahsy maglumatlaryňyz barada aşakdaky hukuklaryňyz bar:

- **Giriş:** Şahsy maglumatlaryňyzyň nusgasyny soramak
- **Düzetme:** Nädogry maglumatlary täzelemek ýa-da düzetmek
- **Öçürmek:** Hasabyňyzy we maglumatlaryňyzy öçürmegi soramak
- **Ret etmek:** Mahabat habarnamalaryndan ýazylyşdan çykmak
- **Maglumatlaryň göçürilmegi:** Maglumatlaryňyzy göçürilip bilinjek formatda soramak

Bu hukuklary amala aşyrmak üçin bize ýüz tutuň: support@sportlink.tm

## Maglumatlary saklamak

Hasabyňyz işjeň bolsa ýa-da hyzmatlary bermek üçin zerur bolsa, şahsy maglumatlaryňyzy saklaýarys. Hasabyňyzy öçürseňiz, kanun tarapyndan saklamak talap edilmedik ýagdaýynda, maglumatlaryňyzy 30 günüň içinde öçüreris ýa-da anonim ederis.

## Çagalaryň gizlinligi

Sportlink 13 ýaşdan kiçi çagalar üçin niýetlenmedi. Biz 13 ýaşdan kiçi çagalardan bilgeşleýin şahsy maglumat ýygnamaýarys.

## Bu syýasatdaky üýtgeşmeler

Bu gizlinlik syýasatyny wagtal-wagtal täzeläp bileris. Programmada täze syýasaty ýerleşdirip we ýokardaky güýje giren senesini täzeläp, islendik möhüm üýtgeşmeler barada size habar bereris.

## Bize ýüz tutuň

Bu gizlinlik syýasaty barada soraglaryňyz bar bolsa, bize ýüz tutuň:

**Email:** support@sportlink.tm
**Telefon:** +993 65 XXX XXX
**Salgy:** Aşgabat, Türkmenistan

---

Sportlink-i ulanmak bilen, bu Gizlinlik syýasatyny okandygyňyzy we düşündügiňizi tassyklaýarsyňyz.
"""
    }
    
    # Format date
    current_date = datetime.now().strftime('%B %d, %Y')
    for lang in privacy_policy_content:
        privacy_policy_content[lang] = privacy_policy_content[lang].format(date=current_date)
    
    # Check if already exists
    existing = LegalDocument.objects(document_type='privacy_policy').first()
    if existing:
        print("Privacy Policy already exists. Updating...")
        existing.title = {
            'en': 'Privacy Policy',
            'ru': 'Политика конфиденциальности',
            'tk': 'Gizlinlik syýasaty'
        }
        existing.content = privacy_policy_content
        existing.save()
        print(f"✓ Privacy Policy updated (ID: {existing.id})")
    else:
        doc = LegalDocument(
            document_type='privacy_policy',
            title={
                'en': 'Privacy Policy',
                'ru': 'Политика конфиденциальности',
                'tk': 'Gizlinlik syýasaty'
            },
            content=privacy_policy_content,
            version='1.0',
            is_active=True
        )
        doc.save()
        print(f"✓ Privacy Policy created (ID: {doc.id})")


def create_terms_of_service():
    """Create Terms of Service document"""
    
    terms_content = {
        'en': """# Terms of Service

**Effective Date:** {date}
**Version:** 1.0

## Agreement to Terms

By accessing or using the Sportlink mobile application ("App"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, please do not use our App.

## Description of Service

Sportlink is a sports facility booking and community platform that provides:
- Court and facility booking services
- Opponent matching based on skill level and preferences
- Tournament organization and registration
- Sports community features
- Personalized offers and discounts

## User Accounts

### Registration
- You must provide accurate and complete information during registration
- You are responsible for maintaining the confidentiality of your account credentials
- You must be at least 13 years old to use Sportlink
- One person may only create one account

### Account Security
- You are responsible for all activities under your account
- Notify us immediately of any unauthorized use
- We are not liable for losses due to unauthorized account use

## User Conduct

You agree NOT to:
- Violate any laws or regulations
- Impersonate another person or entity
- Harass, abuse, or harm other users
- Post false, misleading, or fraudulent content
- Attempt to gain unauthorized access to our systems
- Use automated systems (bots) without permission
- Interfere with the proper functioning of the App

## Bookings and Payments

### Court Bookings
- All bookings are subject to availability
- Booking confirmations will be sent via the App
- Cancellation policies vary by facility
- Late cancellations may incur fees

### Payments
- Prices are displayed in Turkmen Manat (TMT)
- Payment methods accepted: Cash, Card (as available)
- All sales are final unless otherwise stated
- Refunds are subject to our refund policy

## Subscriptions

### Subscription Plans
- Various subscription tiers are available
- Subscriptions provide access to premium features
- Subscription fees are non-refundable
- You can cancel your subscription at any time
- Cancellation takes effect at the end of the current billing period

### Auto-Renewal
- Subscriptions automatically renew unless cancelled
- You will be charged before each renewal period
- Renewal prices may change with 30 days notice

## Tournaments

### Registration
- Tournament registration is subject to availability
- Registration fees are non-refundable
- You must meet eligibility requirements
- Tournament rules and schedules are subject to change

### Conduct
- Players must follow tournament rules and sportsmanship guidelines
- Unsportsmanlike conduct may result in disqualification
- Disputes will be resolved by tournament organizers

## Opponent Matching

- Matching is based on skill level, preferences, and location
- We do not guarantee the accuracy of user-provided information
- Users are responsible for their own safety during matches
- Report any concerns about matched opponents to support

## Intellectual Property

### Our Content
- All content in the App is owned by Sportlink or licensed to us
- You may not copy, modify, or distribute our content without permission
- Trademarks and logos are protected

### User Content
- You retain ownership of content you post
- You grant us a license to use, display, and distribute your content
- You represent that you have rights to post your content
- We may remove content that violates these Terms

## Disclaimers

### Service Availability
- We strive for 99% uptime but do not guarantee uninterrupted service
- We may modify or discontinue features without notice
- Maintenance and updates may cause temporary disruptions

### Third-Party Facilities
- We are not responsible for the condition or safety of third-party facilities
- Facility policies and rules are set by facility owners
- Disputes with facilities should be resolved directly with them

### Health and Safety
- Sports activities carry inherent risks
- You participate at your own risk
- Consult a physician before engaging in physical activities
- We are not liable for injuries or health issues

## Limitation of Liability

TO THE MAXIMUM EXTENT PERMITTED BY LAW:
- Sportlink is provided "AS IS" without warranties
- We are not liable for indirect, incidental, or consequential damages
- Our total liability is limited to the amount you paid in the last 12 months
- Some jurisdictions do not allow these limitations

## Indemnification

You agree to indemnify and hold harmless Sportlink, its officers, directors, employees, and agents from any claims, damages, losses, or expenses arising from:
- Your use of the App
- Your violation of these Terms
- Your violation of any rights of another party

## Termination

### By You
- You may delete your account at any time
- Deletion is permanent and cannot be undone

### By Us
We may suspend or terminate your account if you:
- Violate these Terms
- Engage in fraudulent activity
- Abuse or harass other users
- Fail to pay fees owed

## Changes to Terms

We may update these Terms from time to time. We will notify you of significant changes by:
- Posting the new Terms in the App
- Sending an email notification (if applicable)
- Updating the "Effective Date" above

Continued use of the App after changes constitutes acceptance of the new Terms.

## Governing Law

These Terms are governed by the laws of Turkmenistan. Any disputes will be resolved in the courts of Ashgabat, Turkmenistan.

## Contact Us

For questions about these Terms of Service:

**Email:** support@sportlink.tm
**Phone:** +993 65 XXX XXX
**Address:** Ashgabat, Turkmenistan

---

**Last Updated:** {date}

By using Sportlink, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
""",
        'ru': """# Условия использования

**Дата вступления в силу:** {date}
**Версия:** 1.0

## Согласие с условиями

Получая доступ или используя мобильное приложение Sportlink ("Приложение"), вы соглашаетесь соблюдать эти Условия использования ("Условия"). Если вы не согласны с этими Условиями, пожалуйста, не используйте наше Приложение.

## Описание сервиса

Sportlink - это платформа для бронирования спортивных объектов и сообщества, которая предоставляет:
- Услуги бронирования площадок и объектов
- Подбор соперников на основе уровня мастерства и предпочтений
- Организацию и регистрацию на турниры
- Функции спортивного сообщества
- Персонализированные предложения и скидки

## Учетные записи пользователей

### Регистрация
- Вы должны предоставить точную и полную информацию при регистрации
- Вы несете ответственность за сохранение конфиденциальности учетных данных
- Вам должно быть не менее 13 лет для использования Sportlink
- Один человек может создать только одну учетную запись

### Безопасность аккаунта
- Вы несете ответственность за все действия в вашем аккаунте
- Немедленно сообщите нам о любом несанкционированном использовании
- Мы не несем ответственности за потери из-за несанкционированного использования аккаунта

## Поведение пользователей

Вы соглашаетесь НЕ:
- Нарушать какие-либо законы или правила
- Выдавать себя за другое лицо или организацию
- Преследовать, оскорблять или причинять вред другим пользователям
- Размещать ложный, вводящий в заблуждение или мошеннический контент
- Пытаться получить несанкционированный доступ к нашим системам
- Использовать автоматизированные системы (боты) без разрешения
- Мешать правильной работе Приложения

## Бронирования и платежи

### Бронирование площадок
- Все бронирования зависят от наличия мест
- Подтверждения бронирования будут отправлены через Приложение
- Политика отмены варьируется в зависимости от объекта
- Поздние отмены могут повлечь за собой комиссию

### Платежи
- Цены указаны в туркменских манатах (TMT)
- Принимаемые способы оплаты: Наличные, Карта (при наличии)
- Все продажи окончательны, если не указано иное
- Возвраты средств регулируются нашей политикой возврата

## Подписки

### Планы подписки
- Доступны различные уровни подписки
- Подписки предоставляют доступ к премиум-функциям
- Стоимость подписки не возвращается
- Вы можете отменить подписку в любое время
- Отмена вступает в силу в конце текущего расчетного периода

### Автоматическое продление
- Подписки автоматически продлеваются, если не отменены
- С вас будет взиматься плата перед каждым периодом продления
- Цены на продление могут измениться с уведомлением за 30 дней

## Турниры

### Регистрация
- Регистрация на турнир зависит от наличия мест
- Регистрационные взносы не возвращаются
- Вы должны соответствовать требованиям участия
- Правила и расписание турниров могут быть изменены

### Поведение
- Игроки должны следовать правилам турнира и принципам спортивного поведения
- Неспортивное поведение может привести к дисквалификации
- Споры будут разрешаться организаторами турнира

## Подбор соперников

- Подбор основан на уровне мастерства, предпочтениях и местоположении
- Мы не гарантируем точность информации, предоставленной пользователями
- Пользователи несут ответственность за свою безопасность во время матчей
- Сообщайте о любых проблемах с подобранными соперниками в службу поддержки

## Интеллектуальная собственность

### Наш контент
- Весь контент в Приложении принадлежит Sportlink или лицензирован нам
- Вы не можете копировать, изменять или распространять наш контент без разрешения
- Товарные знаки и логотипы защищены

### Пользовательский контент
- Вы сохраняете право собственности на размещаемый контент
- Вы предоставляете нам лицензию на использование, отображение и распространение вашего контента
- Вы заявляете, что имеете права на размещение своего контента
- Мы можем удалить контент, нарушающий эти Условия

## Отказ от ответственности

### Доступность сервиса
- Мы стремимся к 99% времени работы, но не гарантируем бесперебойную работу
- Мы можем изменять или прекращать функции без уведомления
- Обслуживание и обновления могут вызвать временные перерывы

### Сторонние объекты
- Мы не несем ответственности за состояние или безопасность сторонних объектов
- Политика и правила объектов устанавливаются владельцами объектов
- Споры с объектами должны решаться непосредственно с ними

### Здоровье и безопасность
- Спортивная деятельность несет в себе риски
- Вы участвуете на свой собственный риск
- Проконсультируйтесь с врачом перед физической активностью
- Мы не несем ответственности за травмы или проблемы со здоровьем

## Ограничение ответственности

В МАКСИМАЛЬНОЙ СТЕПЕНИ, РАЗРЕШЕННОЙ ЗАКОНОМ:
- Sportlink предоставляется "КАК ЕСТЬ" без гарантий
- Мы не несем ответственности за косвенные, случайные или последующие убытки
- Наша общая ответственность ограничена суммой, которую вы заплатили за последние 12 месяцев
- Некоторые юрисдикции не допускают эти ограничения

## Возмещение убытков

Вы соглашаетесь возместить и обезопасить Sportlink, его должностных лиц, директоров, сотрудников и агентов от любых претензий, убытков, потерь или расходов, возникающих из:
- Вашего использования Приложения
- Вашего нарушения этих Условий
- Вашего нарушения прав другой стороны

## Прекращение

### С вашей стороны
- Вы можете удалить свой аккаунт в любое время
- Удаление является постоянным и не может быть отменено

### С нашей стороны
Мы можем приостановить или прекратить ваш аккаунт, если вы:
- Нарушаете эти Условия
- Участвуете в мошеннической деятельности
- Оскорбляете или преследуете других пользователей
- Не оплачиваете причитающиеся сборы

## Изменения в Условиях

Мы можем время от времени обновлять эти Условия. Мы уведомим вас о значительных изменениях:
- Размещением новых Условий в Приложении
- Отправкой уведомления по электронной почте (если применимо)
- Обновлением даты вступления в силу выше

Продолжение использования Приложения после изменений означает принятие новых Условий.

## Применимое право

Эти Условия регулируются законами Туркменистана. Любые споры будут разрешаться в судах Ашхабада, Туркменистан.

## Свяжитесь с нами

По вопросам об этих Условиях использования:

**Email:** support@sportlink.tm
**Телефон:** +993 65 XXX XXX
**Адрес:** Ашхабад, Туркменистан

---

**Последнее обновление:** {date}

Используя Sportlink, вы подтверждаете, что прочитали, поняли и согласны соблюдать эти Условия использования.
""",
        'tk': """# Ulanyş şertleri

**Güýje giren senesi:** {date}
**Wersiýa:** 1.0

## Şertlere razy bolmak

Sportlink mobil programmasyna ("Programma") girmek ýa-da ulanmak bilen, bu Ulanyş şertlerine ("Şertler") eýermäge razy bolýarsyňyz. Bu Şertlere razy bolmasaňyz, Programmamyzy ulanmaň.

## Hyzmaty düşündirmek

Sportlink sport desgalaryny bronlaşmak we jemgyýet platformasydyr we hödürleýär:
- Meýdançalary we desgalary bronlaşmak hyzmatlary
- Ussatlyk derejesine we isleglere esaslanyp garşydaş saýlamak
- Ýaryş guramaçylygy we hasaba alynmak
- Sport jemgyýeti aýratynlyklary
- Şahsylaşdyrylan teklipler we arzanladyşlar

## Ulanyjy hasaplary

### Hasaba alynmak
- Hasaba alynanda takyk we doly maglumat bermeli
- Hasap maglumatlaryňyzyň gizlinligini saklamak üçin jogapkärsiňiz
- Sportlink-i ulanmak üçin azyndan 13 ýaşyňyz bolmaly
- Bir adam diňe bir hasap döredip biler

### Hasabyň howpsuzlygy
- Hasabyňyzdaky ähli hereketler üçin jogapkärsiňiz
- Rugsatsyz ulanylmagy derrew habar beriň
- Rugsatsyz hasap ulanylyşy sebäpli ýitgiler üçin jogapkär däldiris

## Ulanyjynyň hereketleri

Etmezlige razy bolýarsyňyz:
- Kanunlary ýa-da düzgünleri bozmak
- Başga bir adamy ýa-da guramany görkezmek
- Beýleki ulanyjylary yzarlamak, kemsitmek ýa-da zyýan bermek
- Ýalan, ýalňyş ýa-da galp mazmun ýerleşdirmek
- Ulgamlarymyza rugsatsyz girmäge synanyşmak
- Awtomatlaşdyrylan ulgamlary (botlar) rugsatsyz ulanmak
- Programmanyň dogry işlemegine päsgel bermek

## Bronlaşlar we tölegler

### Meýdança bronlaşlary
- Bronlaşlaryň hemmesi elýeterlilige bagly
- Bronlaş tassyklamalary Programma arkaly iberiler
- Ýatyrmak syýasaty desgalara görä üýtgeýär
- Giç ýatyrylmalar töleg gerek edip biler

### Tölegler
- Bahalar Türkmen manatynda (TMT) görkezilýär
- Kabul edilýän töleg usullary: Nagt, Kart (elýeterli bolsa)
- Satuwlaryň hemmesi gutarnykly, başgaça aýdylmasa
- Yzyna gaýtarmalar yzyna gaýtarmak syýasatymyza bagly

## Abunalar

### Abuna meýilnamalary
- Dürli abuna derejeleri elýeterlidir
- Abunalar premium aýratynlyklara giriş berýär
- Abuna tölegleri yzyna gaýtarylmaýar
- Abunaňyzy islendik wagt ýatyryp bilersiňiz
- Ýatyrma häzirki hasap döwrüniň ahyrynda güýje girýär

### Awtomatik täzelenme
- Abunalar ýatyrylmasa awtomatiki täzelenýär
- Her täzelenme döwründen öň töleg alnar
- Täzelenme bahalary 30 günlük habar bilen üýtgäp biler

## Ýaryşlar

### Hasaba alynmak
- Ýaryşa hasaba alynmak elýeterlilige bagly
- Hasaba alynmak tölegleri yzyna gaýtarylmaýar
- Gatnaşmak talaplaryna laýyk gelmeli
- Ýaryş düzgünleri we tertibi üýtgäp biler

### Hereket
- Oýunçylar ýaryş düzgünlerine we sport terbiýesi görkezmelerine eýermeli
- Sport däl hereket diskwalifikasiýa sebäp bolup biler
- Jedeller ýaryş guramaçylary tarapyndan çözüler

## Garşydaş saýlamak

- Saýlamak ussatlyk derejesine, isleglere we ýerleşişe esaslanýar
- Ulanyjylar tarapyndan berlen maglumatlaryň takyklygyna kepil bermeýäris
- Ulanyjylar duşuşyklarda öz howpsuzlygy üçin jogapkärdirler
- Saýlanan garşydaşlar barada aladalary goldaw hyzmatyna habar beriň

## Intellektual eýeçilik

### Biziň mazmunymyz
- Programmadaky ähli mazmun Sportlink-e degişlidir ýa-da bize ygtyýarnama berildi
- Rugsatsyz mazmunymyzy göçürip, üýtgedip ýa-da ýaýradyp bilmersiňiz
- Söwda bellikleri we logotiplar goralýar

### Ulanyjy mazmun
- Ýerleşdirýän mazmunyňyza eýeçilik hukugy saklaýarsyňyz
- Mazmunyňyzy ulanmak, görkezmek we ýaýratmak üçin bize ygtyýarnama berýärsiňiz
- Mazmunyňyzy ýerleşdirmäge hukugyňyzyň bardygyny aýdýarsyňyz
- Bu Şertleri bozýan mazmunlary aýryp bileris

## Jogapkärçilikden ýüz öwürmek

### Hyzmaty elýeterlilik
- 99% iş wagtyna çalyşýarys, ýöne üznüksiz hyzmaty kepillendirmeýäris
- Habar bermezden aýratynlyklary üýtgedip ýa-da bes edip bileris
- Hyzmat we täzelenme wagtlaýyn bökdençliklere sebäp bolup biler

### Üçünji tarap desgalary
- Üçünji tarap desgalarynyň ýagdaýy ýa-da howpsuzlygy üçin jogapkär däldiris
- Desgalaryň syýasaty we düzgünleri desgalaryň eýeleri tarapyndan kesgitlenýär
- Desgalar bilen jedeller gönüden-göni olar bilen çözülmeli

### Saglyk we howpsuzlyk
- Sport işjeňligi töwekgelçilikleri öz içine alýar
- Öz töwekgelçiligiňizde gatnaşýarsyňyz
- Fiziki işjeňlik bilen meşgullanmazdan öň lukmana maslahat alyň
- Şikesler ýa-da saglyk meseleleri üçin jogapkär däldiris

## Jogapkärçiligiň çäklendirilmegi

KANUN TARAPYNDAN RUGSAT BERLEN IŇŇ ÝOKARY DEREJEDE:
- Sportlink "NÄHILI BOLSA" kepilsiz hödürlenýär
- Gytaklaýyn, tötänleýin ýa-da netijeli zeper üçin jogapkär däldiris
- Umumy jogapkärçiligimiz soňky 12 aýda tölen mukdary bilen çäklendirilýär
- Käbir ýurisdiksiýalar bu çäklendirmelere rugsat bermeýär

## Öwezini dolmak

Sportlink-i, onuň işgärlerini, direktorlaryny, işgärlerini we agentlerini islendik talaplardan, zyýanlardan, ýitgilerden ýa-da çykdajylardan goramaga we howpsuz saklamaga razy bolýarsyňyz:
- Programmany ulanmagyňyz
- Bu Şertleri bozmagy

ňyz
- Başga bir tarapyň hukuklaryny bozmagy

ňyz

## Bes etmek

### Siziň tarapyňyzdan
- Hasabyňyzy islendik wagt öçürip bilersiňiz
- Öçürmek hemişelik we yzyna gaýtarylyp bilinmeýär

### Biziň tarapymyzdan
Hasabyňyzy togtatyp ýa-da bes edip bileris:
- Bu Şertleri bozýan bolsaňyz
- Galp işjeňlige gatnaşýan bolsaňyz
- Beýleki ulanyjylary kemsidýän ýa-da yzarlaýan bolsaňyz
- Tölenilmeli tölegleri tölemän bolsaňyz

## Şertlerdäki üýtgeşmeler

Bu Şertleri wagtal-wagtal täzeläp bileris. Möhüm üýtgeşmeler barada size habar bereris:
- Programmada täze Şertleri ýerleşdirmek
- E-poçta habar ibermek (bar bolsa)
- Ýokardaky güýje giren senesini täzelemek

Üýtgeşmelerden soň Programmany ulanmagy dowam etmek täze Şertleri kabul etmegi aňladýar.

## Dolandyryjy kanun

Bu Şertler Türkmenistanyň kanunlary bilen dolandyrylýar. Islendik jedeller Aşgabat, Türkmenistanyň kazyýetlerinde çözüler.

## Bize ýüz tutuň

Bu Ulanyş şertleri barada soraglar üçin:

**Email:** support@sportlink.tm
**Telefon:** +993 65 XXX XXX
**Salgy:** Aşgabat, Türkmenistan

---

**Soňky täzelenen:** {date}

Sportlink-i ulanmak bilen, bu Ulanyş şertlerini okandygyňyzy, düşündügiňizi we olara eýermäge razy bolýandygyňyzy tassyklaýarsyňyz.
"""
    }
    
    # Format date
    current_date = datetime.now().strftime('%B %d, %Y')
    for lang in terms_content:
        terms_content[lang] = terms_content[lang].format(date=current_date)
    
    # Check if already exists
    existing = LegalDocument.objects(document_type='terms_of_service').first()
    if existing:
        print("Terms of Service already exists. Updating...")
        existing.title = {
            'en': 'Terms of Service',
            'ru': 'Условия использования',
            'tk': 'Ulanyş şertleri'
        }
        existing.content = terms_content
        existing.save()
        print(f"✓ Terms of Service updated (ID: {existing.id})")
    else:
        doc = LegalDocument(
            document_type='terms_of_service',
            title={
                'en': 'Terms of Service',
                'ru': 'Условия использования',
                'tk': 'Ulanyş şertleri'
            },
            content=terms_content,
            version='1.0',
            is_active=True
        )
        doc.save()
        print(f"✓ Terms of Service created (ID: {doc.id})")


if __name__ == '__main__':
    print("Initializing legal documents...")
    print("-" * 50)
    
    create_privacy_policy()
    create_terms_of_service()
    
    print("-" * 50)
    print("✓ Legal documents initialized successfully!")
    print("\nYou can now access them via:")
    print("  - Privacy Policy: GET /api/v1/legal/privacy-policy/")
    print("  - Terms of Service: GET /api/v1/legal/terms-of-service/")

