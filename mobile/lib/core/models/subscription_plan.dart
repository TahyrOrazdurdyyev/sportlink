class BookingLimits {
  final int? bookingsPerWeek;
  final double? maxDurationHours;
  final List<int>? allowedDays;

  BookingLimits({
    this.bookingsPerWeek,
    this.maxDurationHours,
    this.allowedDays,
  });

  factory BookingLimits.fromJson(Map<String, dynamic> json) {
    return BookingLimits(
      bookingsPerWeek: json['bookings_per_week'] as int?,
      maxDurationHours: (json['max_duration_hours'] as num?)?.toDouble(),
      allowedDays: (json['allowed_days'] as List?)?.map((e) => e as int).toList(),
    );
  }

  bool isDayAllowed(int dayOfWeek) {
    if (allowedDays == null || allowedDays!.isEmpty) return true;
    return allowedDays!.contains(dayOfWeek);
  }

  String getAllowedDaysText() {
    if (allowedDays == null || allowedDays!.isEmpty) return 'All days';
    if (allowedDays!.length == 7) return 'All days';
    
    final dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return allowedDays!.map((d) => dayNames[d - 1]).join(', ');
  }
}

class SubscriptionPlan {
  final String id;
  final Map<String, String> name;
  final Map<String, String> description;
  final double monthlyPrice;
  final double yearlyPrice;
  final String currency;
  final double discountPercentage;
  final double discountedMonthlyPrice;
  final double discountedYearlyPrice;
  final bool hasDiscount;
  final Map<String, bool> features;
  final BookingLimits? bookingLimits;
  final bool isPopular;
  final int order;

  SubscriptionPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.monthlyPrice,
    required this.yearlyPrice,
    required this.currency,
    required this.discountPercentage,
    required this.discountedMonthlyPrice,
    required this.discountedYearlyPrice,
    required this.hasDiscount,
    required this.features,
    this.bookingLimits,
    required this.isPopular,
    required this.order,
  });

  factory SubscriptionPlan.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlan(
      id: json['id'],
      name: Map<String, String>.from(json['name']),
      description: Map<String, String>.from(json['description']),
      monthlyPrice: (json['monthly_price'] as num).toDouble(),
      yearlyPrice: (json['yearly_price'] as num).toDouble(),
      currency: json['currency'] ?? 'TMT',
      discountPercentage: (json['discount_percentage'] as num?)?.toDouble() ?? 0.0,
      discountedMonthlyPrice: (json['discounted_monthly_price'] as num?)?.toDouble() ?? (json['monthly_price'] as num).toDouble(),
      discountedYearlyPrice: (json['discounted_yearly_price'] as num?)?.toDouble() ?? (json['yearly_price'] as num).toDouble(),
      hasDiscount: json['has_discount'] ?? false,
      features: Map<String, bool>.from(json['features']),
      bookingLimits: json['booking_limits'] != null 
          ? BookingLimits.fromJson(json['booking_limits']) 
          : null,
      isPopular: json['is_popular'] ?? false,
      order: json['order'] ?? 0,
    );
  }

  String getLocalizedName(String locale) {
    return name[locale] ?? name['en'] ?? '';
  }

  String getLocalizedDescription(String locale) {
    return description[locale] ?? description['en'] ?? '';
  }
}

