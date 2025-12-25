import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../../../core/models/subscription_plan.dart';
import '../../../core/services/subscription_service.dart';

class SubscriptionPlansScreen extends StatefulWidget {
  const SubscriptionPlansScreen({super.key});

  @override
  State<SubscriptionPlansScreen> createState() =>
      _SubscriptionPlansScreenState();
}

class _SubscriptionPlansScreenState extends State<SubscriptionPlansScreen> {
  final ApiClient _apiClient = ApiClient();
  late SubscriptionService _subscriptionService;

  List<SubscriptionPlan> _plans = [];
  bool _isLoading = true;
  bool _hasActiveSubscription = false;
  Map<String, dynamic>? _currentSubscription;
  String _selectedPeriod = 'monthly'; // or 'yearly'

  @override
  void initState() {
    super.initState();
    _subscriptionService = SubscriptionService(_apiClient.dio);
    _checkCurrentSubscription();
  }

  Future<void> _checkCurrentSubscription() async {
    setState(() => _isLoading = true);

    try {
      // Check if user has active subscription
      final response = await _apiClient.dio.get('/subscriptions/my-subscription/');
      
      if (response.data['has_subscription'] == true) {
        setState(() {
          _hasActiveSubscription = true;
          _currentSubscription = response.data['subscription'];
          _isLoading = false;
        });
      } else {
        // No active subscription, load plans
        await _loadPlans();
      }
    } catch (e) {
      // If error, assume no subscription and load plans
      await _loadPlans();
    }
  }

  Future<void> _loadPlans() async {
    setState(() => _isLoading = true);

    try {
      final loadedPlans = await _subscriptionService.getAvailablePlans();
      setState(() {
        _plans = loadedPlans..sort((a, b) => a.order.compareTo(b.order));
        _isLoading = false;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка загрузки планов: $e')),
      );
      setState(() => _isLoading = false);
    }
  }

  Future<void> _handleSubscribe(SubscriptionPlan plan) async {
    final price = _selectedPeriod == 'monthly' ? plan.monthlyPrice : plan.yearlyPrice;
    final period = _selectedPeriod == 'monthly' ? 'месяц' : 'год';
    
    // Show office payment information dialog
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.payment, color: Theme.of(context).primaryColor),
            const SizedBox(width: 12),
            const Expanded(child: Text('Оплата подписки')),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Subscription info
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      plan.getLocalizedName('ru'),
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$price ${plan.currency}/$period',
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.blue,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              
              // Payment instructions
              const Text(
                'Для оформления подписки необходимо:',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              
              _buildInstructionStep(
                '1',
                'Посетить наш офис по адресу',
              ),
              const SizedBox(height: 8),
              
              // Office address
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.location_on, color: Colors.red[700], size: 20),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'г. Ашхабад, ул. Огузхан, 15',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              
              _buildInstructionStep(
                '2',
                'Произвести оплату наличными',
              ),
              const SizedBox(height: 12),
              
              _buildInstructionStep(
                '3',
                'Получить активацию подписки',
              ),
              const SizedBox(height: 20),
              
              // Office hours and contact
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.access_time, size: 18, color: Colors.green[700]),
                        const SizedBox(width: 8),
                        const Text(
                          'Часы работы:',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    const Padding(
                      padding: EdgeInsets.only(left: 26),
                      child: Text('Пн-Пт: 9:00 - 18:00\nСб: 10:00 - 15:00'),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Icon(Icons.phone, size: 18, color: Colors.green[700]),
                        const SizedBox(width: 8),
                        const Text(
                          'Телефон:',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    const Padding(
                      padding: EdgeInsets.only(left: 26),
                      child: Text(
                        '+993 12 34-56-78',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.blue,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              
              // Note
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.info_outline, size: 18, color: Colors.orange[700]),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'При себе иметь документ, удостоверяющий личность',
                        style: TextStyle(fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Закрыть'),
          ),
            ElevatedButton.icon(
            onPressed: () async {
              Navigator.pop(context);
              // Send subscription request to backend
              await _sendSubscriptionRequest(plan);
            },
            icon: const Icon(Icons.send),
            label: const Text('Отправить заявку'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildInstructionStep(String number, String text) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: Theme.of(context).primaryColor,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              number,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Text(
              text,
              style: const TextStyle(fontSize: 14),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _sendSubscriptionRequest(SubscriptionPlan plan) async {
    try {
      // Send request to backend
      await _apiClient.dio.post(
        '/subscriptions/requests/create/',
        data: {
          'plan_id': plan.id,
          'period': _selectedPeriod,
          'user_notes': '',
        },
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Заявка отправлена! Ждем вас в офисе для оплаты.'),
            duration: Duration(seconds: 4),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_hasActiveSubscription ? 'Моя подписка' : 'Выберите подписку'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _hasActiveSubscription
              ? _buildCurrentSubscriptionView()
              : Column(
              children: [
                // Period Toggle
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(
                        value: 'monthly',
                        label: Text('Месяц'),
                      ),
                      ButtonSegment(
                        value: 'yearly',
                        label: Text('Год'),
                      ),
                    ],
                    selected: {_selectedPeriod},
                    onSelectionChanged: (Set<String> newSelection) {
                      setState(() {
                        _selectedPeriod = newSelection.first;
                      });
                    },
                  ),
                ),

                // Plans List
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _plans.length,
                    itemBuilder: (context, index) {
                      final plan = _plans[index];
                      return _buildPlanCard(plan);
                    },
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildPlanCard(SubscriptionPlan plan) {
    final originalPrice =
        _selectedPeriod == 'monthly' ? plan.monthlyPrice : plan.yearlyPrice;
    final price =
        _selectedPeriod == 'monthly' ? plan.discountedMonthlyPrice : plan.discountedYearlyPrice;
    final period = _selectedPeriod == 'monthly' ? 'месяц' : 'год';

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: plan.isPopular ? 4 : 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: plan.isPopular
            ? BorderSide(color: Theme.of(context).primaryColor, width: 2)
            : BorderSide.none,
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        plan.getLocalizedName('ru'),
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        plan.getLocalizedDescription('ru'),
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    if (plan.isPopular)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Theme.of(context).primaryColor,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text(
                          'Популярно',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    if (plan.hasDiscount)
                      Container(
                        margin: const EdgeInsets.only(top: 4),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '-${plan.discountPercentage.toInt()}%',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Price
            if (plan.hasDiscount) ...[
              // Original price (crossed out)
              Text(
                '$originalPrice ${plan.currency}/$period',
                style: TextStyle(
                  fontSize: 18,
                  decoration: TextDecoration.lineThrough,
                  color: Colors.grey[500],
                ),
              ),
              const SizedBox(height: 4),
              // Discounted price
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    '${price.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: Colors.red,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${plan.currency}/$period',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ] else ...[
              // Regular price
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    '$price',
                    style: const TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${plan.currency}/$period',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 20),

            // Features
            ...plan.features.entries
                .where((e) => e.value)
                .map((entry) => _buildFeatureItem(entry.key)),
            
            // Booking Restrictions
            if (plan.bookingLimits != null) ...[
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.info_outline, size: 18, color: Colors.blue[700]),
                        const SizedBox(width: 8),
                        const Text(
                          'Ограничения бронирования',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (plan.bookingLimits!.bookingsPerWeek != null)
                      Padding(
                        padding: const EdgeInsets.only(left: 26, bottom: 4),
                        child: Text(
                          '• ${plan.bookingLimits!.bookingsPerWeek} бронирований в неделю',
                          style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                        ),
                      ),
                    if (plan.bookingLimits!.maxDurationHours != null)
                      Padding(
                        padding: const EdgeInsets.only(left: 26, bottom: 4),
                        child: Text(
                          '• Макс. ${plan.bookingLimits!.maxDurationHours} часов за раз',
                          style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                        ),
                      ),
                    if (plan.bookingLimits!.allowedDays != null && plan.bookingLimits!.allowedDays!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(left: 26),
                        child: Text(
                          '• Дни: ${plan.bookingLimits!.getAllowedDaysText()}',
                          style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                        ),
                      ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 20),

            // Subscribe Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => _handleSubscribe(plan),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Оформить',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureItem(String featureKey) {
    final featureNames = {
      'court_booking': 'Аренда площадки',
      'opponent_matching': 'Подбор соперника',
      'weekend_booking': 'Бронирование в выходные',
      'tournament_registration': 'Регистрация на турниры',
      'equipment_rental': 'Аренда экипировки',
      'advanced_statistics': 'Расширенная статистика',
      'discount_court_booking': 'Скидка на аренду',
    };

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(
            Icons.check_circle,
            color: Colors.green[600],
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              featureNames[featureKey] ?? featureKey,
              style: const TextStyle(fontSize: 15),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentSubscriptionView() {
    if (_currentSubscription == null) {
      return const Center(child: Text('Нет данных о подписке'));
    }

    final plan = _currentSubscription!['plan'];
    final startDate = DateTime.parse(_currentSubscription!['start_date']);
    final endDate = DateTime.parse(_currentSubscription!['end_date']);
    final daysLeft = endDate.difference(DateTime.now()).inDays;
    final features = _currentSubscription!['features'] as Map<String, dynamic>? ?? {};

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Subscription Status Card
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).primaryColor,
                    Theme.of(context).primaryColor.withOpacity(0.7),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.verified, color: Colors.white, size: 32),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Активная подписка',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            Text(
                              plan['name']['en'] ?? plan['name']['ru'] ?? 'Unknown',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Осталось дней',
                            style: TextStyle(color: Colors.white70, fontSize: 14),
                          ),
                          Text(
                            '$daysLeft',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          const Text(
                            'Действует до',
                            style: TextStyle(color: Colors.white70, fontSize: 14),
                          ),
                          Text(
                            '${endDate.day}.${endDate.month}.${endDate.year}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Features Section
          Text(
            'Доступные возможности',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),

          ...features.entries.where((e) => e.value == true).map((entry) {
            final featureNames = {
              'court_booking': 'Аренда площадки',
              'opponent_matching': 'Подбор соперника',
              'weekend_booking': 'Бронирование в выходные',
              'tournament_registration': 'Регистрация на турниры',
              'equipment_rental': 'Аренда экипировки',
              'advanced_statistics': 'Расширенная статистика',
              'discount_court_booking': 'Скидка на аренду',
            };

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.check_circle, color: Colors.green),
                ),
                title: Text(
                  featureNames[entry.key] ?? entry.key,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
              ),
            );
          }).toList(),

          const SizedBox(height: 24),

          // Subscription Details
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Детали подписки',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const Divider(height: 24),
                  _buildDetailRow('Дата начала', '${startDate.day}.${startDate.month}.${startDate.year}'),
                  const SizedBox(height: 12),
                  _buildDetailRow('Дата окончания', '${endDate.day}.${endDate.month}.${endDate.year}'),
                  const SizedBox(height: 12),
                  _buildDetailRow('Статус', _currentSubscription!['status']),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.grey, fontSize: 14),
        ),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
      ],
    );
  }
}

