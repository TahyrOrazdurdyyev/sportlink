import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../network/api_client.dart';
import '../services/subscription_service.dart';
import '../../features/subscription/subscription_plans_screen.dart';

class FeatureGuard {
  static final ApiClient _apiClient = ApiClient();
  static late SubscriptionService _subscriptionService;

  static void initialize() {
    _subscriptionService = SubscriptionService(_apiClient.dio);
  }

  /// Check if user has access to a specific feature
  /// Returns true if access is granted, false otherwise
  /// Shows upgrade dialog if feature is not available
  static Future<bool> checkFeature(
    BuildContext context,
    String featureKey, {
    bool showDialog = true,
  }) async {
    try {
      final features = await _subscriptionService.getMyFeatures();

      if (features[featureKey] == true) {
        return true;
      }

      // Feature not available
      if (showDialog && context.mounted) {
        _showFeatureNotAvailableDialog(context, featureKey);
      }
      return false;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        // Not authenticated
        if (context.mounted) {
          Navigator.pushNamedAndRemoveUntil(
              context, '/login', (route) => false);
        }
      }
      return false;
    } catch (e) {
      debugPrint('Feature check error: $e');
      return false;
    }
  }

  /// Silent check without showing dialog
  static Future<bool> hasFeature(String featureKey) async {
    try {
      final features = await _subscriptionService.getMyFeatures();
      return features[featureKey] == true;
    } catch (e) {
      debugPrint('Feature check error: $e');
      return false;
    }
  }

  /// Get all available features for the user
  static Future<Map<String, bool>> getUserFeatures() async {
    try {
      return await _subscriptionService.getMyFeatures();
    } catch (e) {
      debugPrint('Get features error: $e');
      return {};
    }
  }

  /// Show dialog when feature is not available
  static void _showFeatureNotAvailableDialog(
    BuildContext context,
    String featureKey,
  ) {
    final featureNames = {
      'court_booking': 'Аренда площадки',
      'opponent_matching': 'Подбор соперника',
      'weekend_booking': 'Бронирование в выходные',
      'tournament_registration': 'Регистрация на турниры',
      'equipment_rental': 'Аренда экипировки',
      'advanced_statistics': 'Расширенная статистика',
      'discount_court_booking': 'Скидка на аренду',
    };

    final featureDescriptions = {
      'court_booking': 'Бронируйте спортивные площадки в любое время',
      'opponent_matching':
          'Находите партнеров соответствующего уровня для игры',
      'weekend_booking': 'Бронируйте площадки в субботу и воскресенье',
      'tournament_registration': 'Участвуйте в турнирах и соревнованиях',
      'equipment_rental': 'Арендуйте ракетки, мячи и другую экипировку',
      'advanced_statistics':
          'Просматривайте подробную статистику и достижения',
      'discount_court_booking':
          'Получайте скидки при бронировании площадок',
    };

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.lock, color: Theme.of(context).primaryColor),
            const SizedBox(width: 12),
            const Expanded(child: Text('Требуется подписка')),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              featureNames[featureKey] ?? 'Эта функция',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              featureDescriptions[featureKey] ??
                  'Эта функция требует активную подписку',
              style: TextStyle(color: Colors.grey[700]),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue[700]),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Оформите подписку для доступа к этой функции',
                      style: TextStyle(fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Отмена'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const SubscriptionPlansScreen(),
                ),
              );
            },
            icon: const Icon(Icons.star),
            label: const Text('Выбрать тариф'),
          ),
        ],
      ),
    );
  }

  /// Show subscription required message (SnackBar)
  static void showSubscriptionRequired(BuildContext context, String featureKey) {
    final featureNames = {
      'court_booking': 'Аренда площадки',
      'opponent_matching': 'Подбор соперника',
      'weekend_booking': 'Бронирование в выходные',
      'tournament_registration': 'Регистрация на турниры',
      'equipment_rental': 'Аренда экипировки',
      'advanced_statistics': 'Расширенная статистика',
      'discount_court_booking': 'Скидка на аренду',
    };

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '${featureNames[featureKey] ?? 'Эта функция'} требует подписку',
        ),
        action: SnackBarAction(
          label: 'Оформить',
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => const SubscriptionPlansScreen(),
              ),
            );
          },
        ),
      ),
    );
  }
}

/// Widget wrapper to conditionally show content based on feature access
class FeatureGate extends StatefulWidget {
  final String featureKey;
  final Widget child;
  final Widget? fallback;
  final bool showDialog;

  const FeatureGate({
    super.key,
    required this.featureKey,
    required this.child,
    this.fallback,
    this.showDialog = true,
  });

  @override
  State<FeatureGate> createState() => _FeatureGateState();
}

class _FeatureGateState extends State<FeatureGate> {
  bool? _hasAccess;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _checkAccess();
  }

  Future<void> _checkAccess() async {
    final hasAccess = await FeatureGuard.hasFeature(widget.featureKey);
    setState(() {
      _hasAccess = hasAccess;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_hasAccess == true) {
      return widget.child;
    }

    if (widget.fallback != null) {
      return widget.fallback!;
    }

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.lock_outline,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            const Text(
              'Требуется подписка',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Эта функция доступна только с активной подпиской',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const SubscriptionPlansScreen(),
                  ),
                );
              },
              icon: const Icon(Icons.star),
              label: const Text('Выбрать тариф'),
            ),
          ],
        ),
      ),
    );
  }
}

