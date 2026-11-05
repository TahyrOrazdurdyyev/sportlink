import 'package:dio/dio.dart';
import '../models/user_statistics.dart';

class StatisticsService {
  final Dio _dio;

  StatisticsService(this._dio);

  // Получить статистику
  Future<UserStatistics> getUserStatistics({int days = 30}) async {
    try {
      final response = await _dio.get(
        '/users/statistics/',
        queryParameters: {'range': days},
      );
      return UserStatistics.fromJson(response.data);
    } catch (e) {
      if (e is DioException && e.response?.statusCode == 403) {
        throw FeatureNotAvailableException(
          'Advanced statistics requires subscription',
          'advanced_statistics',
        );
      }
      throw Exception('Failed to load statistics: $e');
    }
  }

  // Получить достижения
  Future<List<Achievement>> getAchievements() async {
    try {
      final response = await _dio.get('/users/achievements/');
      return (response.data['achievements'] as List)
          .map((json) => Achievement.fromJson(json))
          .toList();
    } catch (e) {
      if (e is DioException && e.response?.statusCode == 403) {
        throw FeatureNotAvailableException(
          'Achievements require subscription',
          'advanced_statistics',
        );
      }
      throw Exception('Failed to load achievements: $e');
    }
  }

  // Получить лидерборд
  Future<Map<String, List<LeaderboardEntry>>> getLeaderboard() async {
    try {
      final response = await _dio.get('/users/leaderboard/');
      return {
        'by_rating': (response.data['leaderboards']['by_rating'] as List)
            .map((json) => LeaderboardEntry.fromJson(json))
            .toList(),
        'by_bookings': (response.data['leaderboards']['by_bookings'] as List)
            .map((json) => LeaderboardEntry.fromJson(json))
            .toList(),
      };
    } catch (e) {
      throw Exception('Failed to load leaderboard: $e');
    }
  }
}

class LeaderboardEntry {
  final int rank;
  final String id;
  final String name;
  final double? rating;
  final int? experienceLevel;
  final int? count;

  LeaderboardEntry({
    required this.rank,
    required this.id,
    required this.name,
    this.rating,
    this.experienceLevel,
    this.count,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) {
    return LeaderboardEntry(
      rank: json['rank'],
      id: json['id'],
      name: json['name'],
      rating: (json['rating'] as num?)?.toDouble(),
      experienceLevel: json['experience_level'],
      count: json['count'],
    );
  }
}

class FeatureNotAvailableException implements Exception {
  final String message;
  final String featureKey;

  FeatureNotAvailableException(this.message, this.featureKey);

  @override
  String toString() => message;
}

