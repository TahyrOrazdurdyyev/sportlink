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
    return Booking(
      id: json['id'] as String,
      userId: json['user'] is String ? json['user'] as String : (json['user']['id'] as String),
      courtId: json['court'] is String ? json['court'] as String : (json['court']['id'] as String),
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      status: json['status'] as String,
      numberOfPlayers: (json['number_of_players'] as int?) ?? 1,
      findOpponents: (json['find_opponents'] as bool?) ?? false,
      opponentsNeeded: (json['opponents_needed'] as int?) ?? 0,
      equipmentNeeded: (json['equipment_needed'] as bool?) ?? false,
      equipmentDetails: json['equipment_details'] != null 
          ? Map<String, int>.from(json['equipment_details'] as Map)
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

