import 'package:flutter_riverpod/flutter_riverpod.dart';

final localeProvider = StateProvider<Locale>((ref) {
  return const Locale('tk', 'TM'); // Default to Turkmen
});

