class Notification {
  final String id;
  final String type;
  final Map<String, String> title;
  final Map<String, String> message;
  final Map<String, dynamic>? data;
  final bool isRead;
  final bool isSent;
  final DateTime createdAt;
  final DateTime? readAt;

  Notification({
    required this.id,
    required this.type,
    required this.title,
    required this.message,
    this.data,
    required this.isRead,
    required this.isSent,
    required this.createdAt,
    this.readAt,
  });

  factory Notification.fromJson(Map<String, dynamic> json) {
    return Notification(
      id: json['id'] as String,
      type: json['type'] as String,
      title: Map<String, String>.from(json['title'] as Map),
      message: Map<String, String>.from(json['message'] as Map),
      data: json['data'] as Map<String, dynamic>?,
      isRead: json['is_read'] as bool? ?? false,
      isSent: json['is_sent'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      readAt: json['read_at'] != null ? DateTime.parse(json['read_at'] as String) : null,
    );
  }

  String getTitle(String locale) {
    return title[locale] ?? title['en'] ?? '';
  }

  String getMessage(String locale) {
    return message[locale] ?? message['en'] ?? '';
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'title': title,
      'message': message,
      'data': data,
      'is_read': isRead,
      'is_sent': isSent,
      'created_at': createdAt.toIso8601String(),
      'read_at': readAt?.toIso8601String(),
    };
  }
}

class OpponentMatch {
  final String matchId;
  final String role; // 'seeker' or 'opponent'
  final OpponentInfo opponent;
  final MatchBookingInfo booking;
  final DateTime? matchedAt;

  OpponentMatch({
    required this.matchId,
    required this.role,
    required this.opponent,
    required this.booking,
    this.matchedAt,
  });

  factory OpponentMatch.fromJson(Map<String, dynamic> json) {
    return OpponentMatch(
      matchId: json['match_id'] as String,
      role: json['role'] as String,
      opponent: OpponentInfo.fromJson(json['opponent'] as Map<String, dynamic>),
      booking: MatchBookingInfo.fromJson(json['booking'] as Map<String, dynamic>),
      matchedAt: json['matched_at'] != null 
          ? DateTime.parse(json['matched_at'] as String) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'match_id': matchId,
      'role': role,
      'opponent': opponent.toJson(),
      'booking': booking.toJson(),
      'matched_at': matchedAt?.toIso8601String(),
    };
  }
}

class OpponentInfo {
  final String id;
  final String nickname;
  final String firstName;
  final String lastName;

  OpponentInfo({
    required this.id,
    required this.nickname,
    required this.firstName,
    required this.lastName,
  });

  factory OpponentInfo.fromJson(Map<String, dynamic> json) {
    return OpponentInfo(
      id: json['id'] as String,
      nickname: json['nickname'] as String,
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
    );
  }

  String get fullName => '$firstName $lastName'.trim();

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nickname': nickname,
      'first_name': firstName,
      'last_name': lastName,
    };
  }
}

class MatchBookingInfo {
  final String id;
  final String courtId;
  final String courtName;
  final DateTime startTime;
  final DateTime endTime;
  final String status;

  MatchBookingInfo({
    required this.id,
    required this.courtId,
    required this.courtName,
    required this.startTime,
    required this.endTime,
    required this.status,
  });

  factory MatchBookingInfo.fromJson(Map<String, dynamic> json) {
    return MatchBookingInfo(
      id: json['id'] as String,
      courtId: json['court_id'] as String,
      courtName: json['court_name'] as String,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      status: json['status'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'court_id': courtId,
      'court_name': courtName,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'status': status,
    };
  }
}

