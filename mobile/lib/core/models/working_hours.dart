class WorkingHours {
  final int dayOfWeek; // 0=Monday, 6=Sunday
  final bool isWorkingDay;
  final String? startTime; // HH:MM format
  final String? endTime; // HH:MM format

  WorkingHours({
    required this.dayOfWeek,
    required this.isWorkingDay,
    this.startTime,
    this.endTime,
  });

  factory WorkingHours.fromJson(Map<String, dynamic> json) {
    return WorkingHours(
      dayOfWeek: json['day_of_week'] as int,
      isWorkingDay: json['is_working_day'] as bool? ?? true,
      startTime: json['start_time'] as String?,
      endTime: json['end_time'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'day_of_week': dayOfWeek,
      'is_working_day': isWorkingDay,
      'start_time': startTime,
      'end_time': endTime,
    };
  }

  WorkingHours copyWith({
    int? dayOfWeek,
    bool? isWorkingDay,
    String? startTime,
    String? endTime,
  }) {
    return WorkingHours(
      dayOfWeek: dayOfWeek ?? this.dayOfWeek,
      isWorkingDay: isWorkingDay ?? this.isWorkingDay,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
    );
  }
}

