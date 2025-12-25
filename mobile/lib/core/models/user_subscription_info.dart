class UserSubscriptionInfo {
  final String id;
  final String planId;
  final String planName;
  final List<String> planFeatures;
  final DateTime? startDate;
  final DateTime? endDate;
  final String status;
  final String? paymentMethod;

  UserSubscriptionInfo({
    required this.id,
    required this.planId,
    required this.planName,
    required this.planFeatures,
    this.startDate,
    this.endDate,
    required this.status,
    this.paymentMethod,
  });

  factory UserSubscriptionInfo.fromJson(Map<String, dynamic> json) {
    return UserSubscriptionInfo(
      id: json['id'] as String,
      planId: json['plan_id'] as String,
      planName: json['plan_name'] as String,
      planFeatures: json['plan_features'] != null
          ? List<String>.from(json['plan_features'] as List)
          : [],
      startDate: json['start_date'] != null
          ? DateTime.parse(json['start_date'] as String)
          : null,
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'] as String)
          : null,
      status: json['status'] as String,
      paymentMethod: json['payment_method'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'plan_id': planId,
      'plan_name': planName,
      'plan_features': planFeatures,
      'start_date': startDate?.toIso8601String(),
      'end_date': endDate?.toIso8601String(),
      'status': status,
      'payment_method': paymentMethod,
    };
  }

  bool get isActive => status == 'active' && (endDate?.isAfter(DateTime.now()) ?? false);
  
  int get daysRemaining {
    if (endDate == null) return 0;
    final diff = endDate!.difference(DateTime.now());
    return diff.inDays > 0 ? diff.inDays : 0;
  }
}

