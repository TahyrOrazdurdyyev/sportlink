class Booking {
  final String id;
  final String userId;
  final String courtId;
  final DateTime startTime;
  final DateTime endTime;
  final String status;
  final int numberOfPlayers;
  final bool findOpponents;
  final int opponentsNeeded;
  final bool equipmentNeeded;
  final Map<String, int>? equipmentDetails;
  final double? totalPrice;
  final String? paymentMethod;
  final String? paymentStatus;
  final String? notes;
  final String? cancellationReason;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? cancelledAt;
  
  // Populated fields (from backend)
  final CourtInfo? court;
  
  Booking({
    required this.id,
    required this.userId,
    required this.courtId,
    required this.startTime,
    required this.endTime,
    required this.status,
    this.numberOfPlayers = 1,
    this.findOpponents = false,
    this.opponentsNeeded = 0,
    this.equipmentNeeded = false,
    this.equipmentDetails,
    this.totalPrice,
    this.paymentMethod,
    this.paymentStatus,
    this.notes,
    this.cancellationReason,
    required this.createdAt,
    required this.updatedAt,
    this.cancelledAt,
    this.court,
  });
  
  factory Booking.fromJson(Map<String, dynamic> json) {
    // Helper to safely convert to int
    int? _toInt(dynamic value) {
      if (value == null) return null;
      if (value is int) return value;
      if (value is double) return value.toInt();
      if (value is String) return int.tryParse(value);
      return null;
    }
    
    // Helper to safely convert to bool
    bool? _toBool(dynamic value) {
      if (value == null) return null;
      if (value is bool) return value;
      if (value is num) return value != 0;
      if (value is String) return value.toLowerCase() == 'true' || value == '1';
      return null;
    }
    
    // Safely extract user ID
    String? userId;
    if (json['user'] != null) {
      if (json['user'] is String) {
        userId = json['user'] as String;
      } else if (json['user'] is Map && json['user']['id'] != null) {
        userId = json['user']['id'] as String;
      }
    }
    
    // Safely extract court ID
    String? courtId;
    if (json['court'] != null) {
      if (json['court'] is String) {
        courtId = json['court'] as String;
      } else if (json['court'] is Map && json['court']['id'] != null) {
        courtId = json['court']['id'] as String;
      }
    }
    
    return Booking(
      id: json['id'] as String,
      userId: userId ?? '',
      courtId: courtId ?? '',
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      status: json['status'] as String,
      numberOfPlayers: _toInt(json['number_of_players']) ?? 1,
      findOpponents: _toBool(json['find_opponents']) ?? false,
      opponentsNeeded: _toInt(json['opponents_needed']) ?? 0,
      equipmentNeeded: _toBool(json['equipment_needed']) ?? false,
      equipmentDetails: json['equipment_details'] != null 
          ? Map<String, int>.from(
              (json['equipment_details'] as Map).map((key, value) => 
                MapEntry(key as String, _toInt(value) ?? 0)
              )
            )
          : null,
      totalPrice: json['total_price'] != null ? double.parse(json['total_price'].toString()) : null,
      paymentMethod: json['payment_method'] as String?,
      paymentStatus: json['payment_status'] as String?,
      notes: json['notes'] as String?,
      cancellationReason: json['cancellation_reason'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      cancelledAt: json['cancelled_at'] != null ? DateTime.parse(json['cancelled_at'] as String) : null,
      court: json['court'] is Map ? CourtInfo.fromJson(json['court'] as Map<String, dynamic>) : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user': userId,
      'court': courtId,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'status': status,
      'number_of_players': numberOfPlayers,
      'find_opponents': findOpponents,
      'opponents_needed': opponentsNeeded,
      'equipment_needed': equipmentNeeded,
      'equipment_details': equipmentDetails,
      'total_price': totalPrice,
      'payment_method': paymentMethod,
      'payment_status': paymentStatus,
      'notes': notes,
      'cancellation_reason': cancellationReason,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'cancelled_at': cancelledAt?.toIso8601String(),
    };
  }
  
  String getStatusLabel() {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'confirmed':
        return 'Confirmed';
      case 'cancelled':
        return 'Cancelled';
      case 'completed':
        return 'Completed';
      default:
        return status;
    }
  }
  
  bool isPast() {
    return endTime.isBefore(DateTime.now());
  }
  
  bool isUpcoming() {
    return startTime.isAfter(DateTime.now()) && status != 'cancelled';
  }
  
  bool canCancel() {
    if (status == 'cancelled' || status == 'completed') {
      return false;
    }
    // Can cancel if more than 2 hours before start time
    final twoHoursBefore = startTime.subtract(const Duration(hours: 2));
    return DateTime.now().isBefore(twoHoursBefore);
  }
}

// Court info for booking display
class CourtInfo {
  final String id;
  final Map<String, String> nameI18n;
  final String? address;
  final List<String>? images;
  
  CourtInfo({
    required this.id,
    required this.nameI18n,
    this.address,
    this.images,
  });
  
  factory CourtInfo.fromJson(Map<String, dynamic> json) {
    return CourtInfo(
      id: json['id'] as String,
      nameI18n: Map<String, String>.from(json['name_i18n'] as Map),
      address: json['address'] as String?,
      images: json['images'] != null ? List<String>.from(json['images'] as List) : null,
    );
  }
  
  String getName(String languageCode) {
    return nameI18n[languageCode] ?? nameI18n['en'] ?? '';
  }
}

