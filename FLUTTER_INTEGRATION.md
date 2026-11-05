# Flutter Integration - Subscription Features

## Интеграция функций подписок в Flutter приложение

### 1. Модели данных

Создайте файлы моделей:

```dart
// lib/models/subscription_plan.dart
class SubscriptionPlan {
  final String id;
  final Map<String, String> name;
  final Map<String, String> description;
  final double monthlyPrice;
  final double yearlyPrice;
  final String currency;
  final Map<String, bool> features;
  final bool isPopular;

  SubscriptionPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.monthlyPrice,
    required this.yearlyPrice,
    required this.currency,
    required this.features,
    required this.isPopular,
  });

  factory SubscriptionPlan.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlan(
      id: json['id'],
      name: Map<String, String>.from(json['name']),
      description: Map<String, String>.from(json['description']),
      monthlyPrice: (json['monthly_price'] as num).toDouble(),
      yearlyPrice: (json['yearly_price'] as num).toDouble(),
      currency: json['currency'] ?? 'TMT',
      features: Map<String, bool>.from(json['features']),
      isPopular: json['is_popular'] ?? false,
    );
  }
}

// lib/models/user_subscription.dart
class UserSubscription {
  final String id;
  final SubscriptionPlan plan;
  final DateTime startDate;
  final DateTime endDate;
  final String status;
  final bool isAutoRenew;
  final Map<String, bool> features;

  UserSubscription({
    required this.id,
    required this.plan,
    required this.startDate,
    required this.endDate,
    required this.status,
    required this.isAutoRenew,
    required this.features,
  });

  bool isActive() {
    final now = DateTime.now();
    return status == 'active' && now.isBefore(endDate);
  }

  bool hasFeature(String featureKey) {
    return isActive() && (features[featureKey] ?? false);
  }
}

// lib/models/opponent.dart
class Opponent {
  final String id;
  final String firstName;
  final String lastName;
  final String? avatarUrl;
  final int experienceLevel;
  final double rating;
  final String? city;
  final int compatibilityScore;
  final DateTime? lastActive;

  String get fullName => '$firstName $lastName';
}

// lib/models/user_statistics.dart
class UserStatistics {
  final int totalBookings;
  final int confirmedBookings;
  final int completedBookings;
  final double totalHours;
  final double totalSpent;
  final int tournamentsParticipated;
  final Map<String, int> activityByDayOfWeek;
  final Map<int, int> activityByHourOfDay;
  final double averageBookingsPerWeek;
  final double completionRate;

  UserStatistics({...});
}
```

---

### 2. API Сервисы

```dart
// lib/services/subscription_service.dart
class SubscriptionService {
  final ApiClient _apiClient;

  SubscriptionService(this._apiClient);

  // Получить доступные планы
  Future<List<SubscriptionPlan>> getAvailablePlans() async {
    final response = await _apiClient.get('/admin/subscriptions/plans/public/');
    return (response.data as List)
        .map((json) => SubscriptionPlan.fromJson(json))
        .toList();
  }

  // Получить текущую подписку
  Future<UserSubscription?> getMySubscription() async {
    final response = await _apiClient.get('/admin/subscriptions/my-subscription/');
    
    if (response.data['has_subscription'] == false) {
      return null;
    }
    
    return UserSubscription.fromJson(response.data['subscription']);
  }

  // Оформить подписку
  Future<Map<String, dynamic>> subscribe({
    required String planId,
    required String period, // 'monthly' or 'yearly'
    required String paymentMethod,
    String? transactionId,
  }) async {
    final response = await _apiClient.post(
      '/admin/subscriptions/subscribe/',
      data: {
        'plan_id': planId,
        'period': period,
        'payment_method': paymentMethod,
        'transaction_id': transactionId,
      },
    );
    return response.data;
  }

  // Отменить подписку
  Future<void> cancelSubscription() async {
    await _apiClient.post('/admin/subscriptions/cancel/');
  }

  // Получить доступные features
  Future<Map<String, bool>> getMyFeatures() async {
    final response = await _apiClient.get('/admin/subscriptions/my-features/');
    return Map<String, bool>.from(response.data['features']);
  }
}

// lib/services/opponent_matching_service.dart
class OpponentMatchingService {
  final ApiClient _apiClient;

  OpponentMatchingService(this._apiClient);

  // Найти соперников
  Future<List<Opponent>> findOpponents({
    int? experienceLevel,
    String? categoryId,
    String? city,
    int limit = 20,
  }) async {
    final params = {
      'limit': limit,
      if (experienceLevel != null) 'experience_level': experienceLevel,
      if (categoryId != null) 'category_id': categoryId,
      if (city != null) 'city': city,
    };

    final response = await _apiClient.get(
      '/users/find-opponents/',
      queryParameters: params,
    );

    return (response.data['results'] as List)
        .map((json) => Opponent.fromJson(json))
        .toList();
  }

  // Отправить приглашение
  Future<void> sendMatchInvitation({
    required String opponentId,
    String? courtId,
    DateTime? proposedTime,
    String? message,
  }) async {
    await _apiClient.post(
      '/users/match-invitation/',
      data: {
        'opponent_id': opponentId,
        if (courtId != null) 'court_id': courtId,
        if (proposedTime != null) 'proposed_time': proposedTime.toIso8601String(),
        if (message != null) 'message': message,
      },
    );
  }
}

// lib/services/statistics_service.dart
class StatisticsService {
  final ApiClient _apiClient;

  StatisticsService(this._apiClient);

  // Получить статистику
  Future<UserStatistics> getUserStatistics({int days = 30}) async {
    final response = await _apiClient.get(
      '/users/statistics/',
      queryParameters: {'range': days},
    );
    return UserStatistics.fromJson(response.data);
  }

  // Получить достижения
  Future<List<Achievement>> getAchievements() async {
    final response = await _apiClient.get('/users/achievements/');
    return (response.data['achievements'] as List)
        .map((json) => Achievement.fromJson(json))
        .toList();
  }

  // Получить лидерборд
  Future<Map<String, List<LeaderboardEntry>>> getLeaderboard() async {
    final response = await _apiClient.get('/users/leaderboard/');
    return {
      'by_rating': (response.data['leaderboards']['by_rating'] as List)
          .map((json) => LeaderboardEntry.fromJson(json))
          .toList(),
      'by_bookings': (response.data['leaderboards']['by_bookings'] as List)
          .map((json) => LeaderboardEntry.fromJson(json))
          .toList(),
    };
  }
}

// lib/services/booking_service.dart (добавить метод)
class BookingService {
  // ... существующий код ...

  // Проверить доступность
  Future<AvailabilityCheck> checkAvailability({
    required String courtId,
    required DateTime startTime,
    required DateTime endTime,
  }) async {
    final response = await _apiClient.get(
      '/bookings/check-availability/',
      queryParameters: {
        'court_id': courtId,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime.toIso8601String(),
      },
    );
    return AvailabilityCheck.fromJson(response.data);
  }
}
```

---

### 3. UI компоненты

#### Экран выбора подписки

```dart
// lib/screens/subscription_plans_screen.dart
class SubscriptionPlansScreen extends StatefulWidget {
  @override
  _SubscriptionPlansScreenState createState() => _SubscriptionPlansScreenState();
}

class _SubscriptionPlansScreenState extends State<SubscriptionPlansScreen> {
  final SubscriptionService _subscriptionService = SubscriptionService(ApiClient());
  List<SubscriptionPlan> plans = [];
  bool isLoading = true;
  String selectedPeriod = 'monthly'; // or 'yearly'

  @override
  void initState() {
    super.initState();
    _loadPlans();
  }

  Future<void> _loadPlans() async {
    try {
      final loadedPlans = await _subscriptionService.getAvailablePlans();
      setState(() {
        plans = loadedPlans;
        isLoading = false;
      });
    } catch (e) {
      // Handle error
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Выберите подписку')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Period Toggle
                ToggleButtons(
                  children: [
                    Padding(padding: EdgeInsets.all(16), child: Text('Месяц')),
                    Padding(padding: EdgeInsets.all(16), child: Text('Год')),
                  ],
                  isSelected: [
                    selectedPeriod == 'monthly',
                    selectedPeriod == 'yearly'
                  ],
                  onPressed: (index) {
                    setState(() {
                      selectedPeriod = index == 0 ? 'monthly' : 'yearly';
                    });
                  },
                ),
                
                // Plans List
                Expanded(
                  child: ListView.builder(
                    itemCount: plans.length,
                    itemBuilder: (context, index) {
                      final plan = plans[index];
                      return PlanCard(
                        plan: plan,
                        period: selectedPeriod,
                        onSubscribe: () => _handleSubscribe(plan),
                      );
                    },
                  ),
                ),
              ],
            ),
    );
  }

  Future<void> _handleSubscribe(SubscriptionPlan plan) async {
    // Show payment dialog
    // Process payment
    // Call API
    try {
      await _subscriptionService.subscribe(
        planId: plan.id,
        period: selectedPeriod,
        paymentMethod: 'card',
      );
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Подписка оформлена!')),
      );
      
      Navigator.pop(context);
    } catch (e) {
      // Handle error
    }
  }
}
```

#### Экран поиска соперников

```dart
// lib/screens/find_opponents_screen.dart
class FindOpponentsScreen extends StatefulWidget {
  @override
  _FindOpponentsScreenState createState() => _FindOpponentsScreenState();
}

class _FindOpponentsScreenState extends State<FindOpponentsScreen> {
  final OpponentMatchingService _matchingService = OpponentMatchingService(ApiClient());
  List<Opponent> opponents = [];
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadOpponents();
  }

  Future<void> _loadOpponents() async {
    setState(() => isLoading = true);
    
    try {
      final loadedOpponents = await _matchingService.findOpponents();
      setState(() {
        opponents = loadedOpponents;
        isLoading = false;
      });
    } on DioError catch (e) {
      if (e.response?.statusCode == 403) {
        // Feature not available - show upgrade dialog
        _showUpgradeDialog();
      }
      setState(() => isLoading = false);
    }
  }

  void _showUpgradeDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Требуется подписка'),
        content: Text('Эта функция доступна только с подпиской ProSport или выше'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => SubscriptionPlansScreen()),
              );
            },
            child: Text('Обновить'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Найти соперника')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: opponents.length,
              itemBuilder: (context, index) {
                final opponent = opponents[index];
                return OpponentCard(
                  opponent: opponent,
                  onInvite: () => _sendInvitation(opponent),
                );
              },
            ),
    );
  }

  Future<void> _sendInvitation(Opponent opponent) async {
    try {
      await _matchingService.sendMatchInvitation(
        opponentId: opponent.id,
        message: 'Давай сыграем!',
      );
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Приглашение отправлено!')),
      );
    } catch (e) {
      // Handle error
    }
  }
}
```

#### Экран статистики

```dart
// lib/screens/statistics_screen.dart
class StatisticsScreen extends StatefulWidget {
  @override
  _StatisticsScreenState createState() => _StatisticsScreenState();
}

class _StatisticsScreenState extends State<StatisticsScreen> {
  final StatisticsService _statisticsService = StatisticsService(ApiClient());
  UserStatistics? statistics;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStatistics();
  }

  Future<void> _loadStatistics() async {
    try {
      final stats = await _statisticsService.getUserStatistics(days: 30);
      setState(() {
        statistics = stats;
        isLoading = false;
      });
    } on DioError catch (e) {
      if (e.response?.statusCode == 403) {
        _showUpgradeDialog();
      }
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Моя статистика')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : statistics == null
              ? Center(child: Text('Нет данных'))
              : SingleChildScrollView(
                  child: Column(
                    children: [
                      // Summary Cards
                      Row(
                        children: [
                          StatCard(
                            title: 'Всего игр',
                            value: statistics!.totalBookings.toString(),
                            icon: Icons.sports_tennis,
                          ),
                          StatCard(
                            title: 'Часов',
                            value: statistics!.totalHours.toStringAsFixed(1),
                            icon: Icons.access_time,
                          ),
                        ],
                      ),
                      
                      // Charts
                      ActivityChart(
                        activityByDay: statistics!.activityByDayOfWeek,
                      ),
                      
                      // More stats...
                    ],
                  ),
                ),
    );
  }
}
```

---

### 4. Проверка доступа к features

```dart
// lib/utils/feature_check.dart
class FeatureGuard {
  static Future<bool> checkFeature(
    BuildContext context,
    String featureKey,
  ) async {
    final subscriptionService = SubscriptionService(ApiClient());
    
    try {
      final features = await subscriptionService.getMyFeatures();
      
      if (features[featureKey] == true) {
        return true;
      }
      
      // Feature not available - show dialog
      _showFeatureNotAvailableDialog(context, featureKey);
      return false;
    } catch (e) {
      return false;
    }
  }

  static void _showFeatureNotAvailableDialog(
    BuildContext context,
    String featureKey,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Функция недоступна'),
        content: Text('Эта функция требует подписку'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => SubscriptionPlansScreen()),
              );
            },
            child: Text('Подписаться'),
          ),
        ],
      ),
    );
  }
}

// Использование:
if (await FeatureGuard.checkFeature(context, 'opponent_matching')) {
  // Proceed with feature
  Navigator.push(context, MaterialPageRoute(
    builder: (_) => FindOpponentsScreen(),
  ));
}
```

---

### 5. Обработка ошибок 403

Добавьте в ApiClient interceptor:

```dart
// lib/core/api/api_client.dart
class ApiClient {
  final Dio _dio;

  ApiClient() : _dio = Dio() {
    _dio.interceptors.add(InterceptorsWrapper(
      onError: (error, handler) async {
        if (error.response?.statusCode == 403) {
          final data = error.response?.data;
          
          if (data['error'] == 'Feature not available' ||
              data['error'] == 'Subscription required') {
            // Show subscription dialog
            _showSubscriptionRequiredDialog(data);
            return handler.reject(error);
          }
        }
        
        return handler.next(error);
      },
    ));
  }
}
```

---

## ✅ Готово к интеграции!

Все API endpoints готовы и защищены. Осталось реализовать UI в Flutter приложении используя эти примеры.

