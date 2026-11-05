import 'package:flutter/material.dart';
import 'auth_screen.dart';

class OTPVerificationScreen extends StatelessWidget {
  final String phone;
  
  const OTPVerificationScreen({
    super.key,
    required this.phone,
  });

  @override
  Widget build(BuildContext context) {
    return AuthScreen(initialLogin: phone);
  }
}

