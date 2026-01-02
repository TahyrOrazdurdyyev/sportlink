class TimeSlot {
  final String startTime; // Format: "HH:MM"
  final String endTime;   // Format: "HH:MM"

  TimeSlot({
    required this.startTime,
    required this.endTime,
  });

  factory TimeSlot.fromJson(Map<String, dynamic> json) {
    return TimeSlot(
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'start_time': startTime,
      'end_time': endTime,
    };
  }

  TimeSlot copyWith({
    String? startTime,
    String? endTime,
  }) {
    return TimeSlot(
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
    );
  }
}

class DayAvailability {
  final String day; // monday, tuesday, etc.
  final bool isAvailable;
  final List<TimeSlot> timeSlots;

  DayAvailability({
    required this.day,
    required this.isAvailable,
    this.timeSlots = const [],
  });

  factory DayAvailability.fromJson(Map<String, dynamic> json) {
    return DayAvailability(
      day: json['day'] as String,
      isAvailable: json['is_available'] as bool? ?? false,
      timeSlots: json['time_slots'] != null
          ? (json['time_slots'] as List)
              .map((slot) => TimeSlot.fromJson(slot as Map<String, dynamic>))
              .toList()
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'day': day,
      'is_available': isAvailable,
      'time_slots': timeSlots.map((slot) => slot.toJson()).toList(),
    };
  }

  DayAvailability copyWith({
    String? day,
    bool? isAvailable,
    List<TimeSlot>? timeSlots,
  }) {
    return DayAvailability(
      day: day ?? this.day,
      isAvailable: isAvailable ?? this.isAvailable,
      timeSlots: timeSlots ?? this.timeSlots,
    );
  }

  // Helper method to get localized day name
  String getLocalizedDayName(String locale) {
    final dayNames = {
      'en': {
        'monday': 'Monday',
        'tuesday': 'Tuesday',
        'wednesday': 'Wednesday',
        'thursday': 'Thursday',
        'friday': 'Friday',
        'saturday': 'Saturday',
        'sunday': 'Sunday',
      },
      'ru': {
        'monday': 'Понедельник',
        'tuesday': 'Вторник',
        'wednesday': 'Среда',
        'thursday': 'Четверг',
        'friday': 'Пятница',
        'saturday': 'Суббота',
        'sunday': 'Воскресенье',
      },
      'tk': {
        'monday': 'Duşenbe',
        'tuesday': 'Sişenbe',
        'wednesday': 'Çarşenbe',
        'thursday': 'Penşenbe',
        'friday': 'Anna',
        'saturday': 'Şenbe',
        'sunday': 'Ýekşenbe',
      },
    };

    return dayNames[locale]?[day] ?? day;
  }
}

