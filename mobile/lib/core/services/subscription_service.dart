import 'package:dio/dio.dart';
import '../models/subscription_plan.dart';
import '../models/user_subscription.dart';

class SubscriptionService {
  final Dio _dio;

  SubscriptionService(this._dio);

  // Получить доступные планы
  Future<List<SubscriptionPlan>> getAvailablePlans() async {
    try {
      final response = await _dio.get('/admin/subscriptions/plans/public/');
      return (response.data as List)
          .map((json) => SubscriptionPlan.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('Failed to load plans: $e');
    }
  }

  // Получить текущую подписку
  Future<UserSubscription?> getMySubscription() async {
    try {
      final response = await _dio.get('/admin/subscriptions/my-subscription/');

      if (response.data['has_subscription'] == false) {
        return null;
      }

      return UserSubscription.fromJson(response.data['subscription']);
    } catch (e) {
      throw Exception('Failed to load subscription: $e');
    }
  }

  // Оформить подписку
  Future<Map<String, dynamic>> subscribe({
    required String planId,
    required String period, // 'monthly' or 'yearly'
    required String paymentMethod,
    String? transactionId,
  }) async {
    try {
      final response = await _dio.post(
        '/admin/subscriptions/subscribe/',
        data: {
          'plan_id': planId,
          'period': period,
          'payment_method': paymentMethod,
          if (transactionId != null) 'transaction_id': transactionId,
        },
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to subscribe: $e');
    }
  }

  // Отменить подписку
  Future<void> cancelSubscription() async {
    try {
      await _dio.post('/admin/subscriptions/cancel/');
    } catch (e) {
      throw Exception('Failed to cancel subscription: $e');
    }
  }

  // Получить доступные features
  Future<Map<String, bool>> getMyFeatures() async {
    try {
      final response = await _dio.get('/admin/subscriptions/my-features/');
      return Map<String, bool>.from(response.data['features']);
    } catch (e) {
      throw Exception('Failed to load features: $e');
    }
  }

  // Проверить доступ к конкретной фиче
  Future<bool> hasFeature(String featureKey) async {
    try {
      final features = await getMyFeatures();
      return features[featureKey] ?? false;
    } catch (e) {
      // Если ошибка (например, нет подписки), считаем что фичи нет
      return false;
    }
  }

  // Получить планы, которые включают конкретную фичу
  Future<List<SubscriptionPlan>> getPlansWithFeature(String featureKey) async {
    try {
      final allPlans = await getAvailablePlans();
      return allPlans.where((plan) => plan.features[featureKey] == true).toList();
    } catch (e) {
      throw Exception('Failed to load plans with feature: $e');
    }
  }

  // Создать заявку на подписку
  Future<void> createSubscriptionRequest({
    required String planId,
    required String period,
    required double amount,
    String? notes,
  }) async {
    try {
      await _dio.post(
        '/subscriptions/requests/create/',
        data: {
          'plan': planId,
          'period': period,
          'amount': amount,
          if (notes != null) 'notes': notes,
        },
      );
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to create subscription request');
      }
      throw Exception('Failed to create subscription request: ${e.message}');
    }
  }
}

