class UserStatistics {
  final UserInfo user;
  final TimeRange timeRange;
  final BookingStats bookings;
  final TournamentStats tournaments;
  final ActivityPatterns activityPatterns;
  final PerformanceMetrics performance;
  final List<RecentActivity> recentActivity;

  UserStatistics({
    required this.user,
    required this.timeRange,
    required this.bookings,
    required this.tournaments,
    required this.activityPatterns,
    required this.performance,
    required this.recentActivity,
  });

  factory UserStatistics.fromJson(Map<String, dynamic> json) {
    return UserStatistics(
      user: UserInfo.fromJson(json['user']),
      timeRange: TimeRange.fromJson(json['time_range']),
      bookings: BookingStats.fromJson(json['bookings']),
      tournaments: TournamentStats.fromJson(json['tournaments']),
      activityPatterns: ActivityPatterns.fromJson(json['activity_patterns']),
      performance: PerformanceMetrics.fromJson(json['performance']),
      recentActivity: (json['recent_activity'] as List)
          .map((a) => RecentActivity.fromJson(a))
          .toList(),
    );
  }
}

class UserInfo {
  final String id;
  final String name;
  final int experienceLevel;
  final double rating;

  UserInfo({
    required this.id,
    required this.name,
    required this.experienceLevel,
    required this.rating,
  });

  factory UserInfo.fromJson(Map<String, dynamic> json) {
    return UserInfo(
      id: json['id'],
      name: json['name'],
      experienceLevel: json['experience_level'] ?? 1,
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class TimeRange {
  final int days;
  final DateTime startDate;

  TimeRange({
    required this.days,
    required this.startDate,
  });

  factory TimeRange.fromJson(Map<String, dynamic> json) {
    return TimeRange(
      days: json['days'],
      startDate: DateTime.parse(json['start_date']),
    );
  }
}

class BookingStats {
  final int total;
  final int confirmed;
  final int cancelled;
  final int completed;
  final double totalHours;
  final double totalSpent;

  BookingStats({
    required this.total,
    required this.confirmed,
    required this.cancelled,
    required this.completed,
    required this.totalHours,
    required this.totalSpent,
  });

  factory BookingStats.fromJson(Map<String, dynamic> json) {
    return BookingStats(
      total: json['total'],
      confirmed: json['confirmed'],
      cancelled: json['cancelled'],
      completed: json['completed'],
      totalHours: (json['total_hours'] as num).toDouble(),
      totalSpent: (json['total_spent'] as num).toDouble(),
    );
  }
}

class TournamentStats {
  final int totalParticipated;
  final List<TournamentInfo> list;

  TournamentStats({
    required this.totalParticipated,
    required this.list,
  });

  factory TournamentStats.fromJson(Map<String, dynamic> json) {
    return TournamentStats(
      totalParticipated: json['total_participated'],
      list: (json['list'] as List)
          .map((t) => TournamentInfo.fromJson(t))
          .toList(),
    );
  }
}

class TournamentInfo {
  final String id;
  final String name;
  final DateTime? startDate;
  final String status;

  TournamentInfo({
    required this.id,
    required this.name,
    this.startDate,
    required this.status,
  });

  factory TournamentInfo.fromJson(Map<String, dynamic> json) {
    return TournamentInfo(
      id: json['id'],
      name: json['name'],
      startDate:
          json['start_date'] != null ? DateTime.parse(json['start_date']) : null,
      status: json['status'],
    );
  }
}

class ActivityPatterns {
  final Map<String, int> byDayOfWeek;
  final Map<String, int> byHourOfDay;

  ActivityPatterns({
    required this.byDayOfWeek,
    required this.byHourOfDay,
  });

  factory ActivityPatterns.fromJson(Map<String, dynamic> json) {
    return ActivityPatterns(
      byDayOfWeek: Map<String, int>.from(json['by_day_of_week']),
      byHourOfDay: Map<String, int>.from(json['by_hour_of_day']),
    );
  }
}

class PerformanceMetrics {
  final double averageBookingsPerWeek;
  final double completionRate;
  final double cancellationRate;

  PerformanceMetrics({
    required this.averageBookingsPerWeek,
    required this.completionRate,
    required this.cancellationRate,
  });

  factory PerformanceMetrics.fromJson(Map<String, dynamic> json) {
    return PerformanceMetrics(
      averageBookingsPerWeek:
          (json['average_bookings_per_week'] as num).toDouble(),
      completionRate: (json['completion_rate'] as num).toDouble(),
      cancellationRate: (json['cancellation_rate'] as num).toDouble(),
    );
  }
}

class RecentActivity {
  final String id;
  final String courtName;
  final DateTime? startTime;
  final String status;
  final DateTime createdAt;

  RecentActivity({
    required this.id,
    required this.courtName,
    this.startTime,
    required this.status,
    required this.createdAt,
  });

  factory RecentActivity.fromJson(Map<String, dynamic> json) {
    return RecentActivity(
      id: json['id'],
      courtName: json['court_name'],
      startTime:
          json['start_time'] != null ? DateTime.parse(json['start_time']) : null,
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class Achievement {
  final String id;
  final String name;
  final String description;
  final String icon;
  final bool unlocked;

  Achievement({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.unlocked,
  });

  factory Achievement.fromJson(Map<String, dynamic> json) {
    return Achievement(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      icon: json['icon'],
      unlocked: json['unlocked'],
    );
  }
}

