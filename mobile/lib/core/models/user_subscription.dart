import 'subscription_plan.dart';

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

  factory UserSubscription.fromJson(Map<String, dynamic> json) {
    return UserSubscription(
      id: json['id'],
      plan: SubscriptionPlan.fromJson(json['plan']),
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      status: json['status'],
      isAutoRenew: json['is_auto_renew'] ?? false,
      features: Map<String, bool>.from(json['features']),
    );
  }

  bool isActive() {
    final now = DateTime.now();
    return status == 'active' && now.isBefore(endDate);
  }

  bool hasFeature(String featureKey) {
    return isActive() && (features[featureKey] ?? false);
  }

  int daysRemaining() {
    if (!isActive()) return 0;
    return endDate.difference(DateTime.now()).inDays;
  }
}

