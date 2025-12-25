import 'package:dio/dio.dart';
import 'package:sportlink/core/network/api_client.dart';
import 'package:sportlink/core/models/booking.dart';

class BookingService {
  final ApiClient _apiClient = ApiClient();

  /// Get user's booking history
  Future<List<Booking>> getUserBookings({
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };
      
      if (status != null) {
        queryParams['status'] = status;
      }
      
      final response = await _apiClient.dio.get(
        '/bookings/',
        queryParameters: queryParams,
      );
      
      // Handle paginated response
      final results = response.data['results'] as List? ?? response.data as List;
      return results.map((booking) => Booking.fromJson(booking as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to get bookings');
      }
      throw Exception('Failed to get bookings: ${e.message}');
    } catch (e) {
      throw Exception('Failed to get bookings: $e');
    }
  }

  /// Get booking by ID
  Future<Booking> getBooking(String bookingId) async {
    try {
      final response = await _apiClient.dio.get('/bookings/$bookingId/');
      return Booking.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to get booking');
      }
      throw Exception('Failed to get booking: ${e.message}');
    } catch (e) {
      throw Exception('Failed to get booking: $e');
    }
  }

  /// Create a new booking
  Future<Booking> createBooking({
    required String courtId,
    required DateTime startTime,
    required DateTime endTime,
    String? notes,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/bookings/',
        data: {
          'court': courtId,
          'start_time': startTime.toIso8601String(),
          'end_time': endTime.toIso8601String(),
          'notes': notes,
        },
      );
      return Booking.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? errorData['detail'] ?? 'Failed to create booking');
      }
      throw Exception('Failed to create booking: ${e.message}');
    } catch (e) {
      throw Exception('Failed to create booking: $e');
    }
  }

  /// Cancel a booking
  Future<void> cancelBooking(String bookingId, {String? reason}) async {
    try {
      await _apiClient.dio.post(
        '/bookings/$bookingId/cancel/',
        data: {
          'reason': reason,
        },
      );
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to cancel booking');
      }
      throw Exception('Failed to cancel booking: ${e.message}');
    } catch (e) {
      throw Exception('Failed to cancel booking: $e');
    }
  }

  /// Check court availability
  Future<bool> checkAvailability({
    required String courtId,
    required DateTime startTime,
    required DateTime endTime,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/bookings/check-availability/',
        queryParameters: {
          'court_id': courtId,
          'start_time': startTime.toIso8601String(),
          'end_time': endTime.toIso8601String(),
        },
      );
      return response.data['available'] as bool? ?? false;
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to check availability');
      }
      throw Exception('Failed to check availability: ${e.message}');
    } catch (e) {
      throw Exception('Failed to check availability: $e');
    }
  }
}

