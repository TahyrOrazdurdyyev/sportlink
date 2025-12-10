import 'package:flutter/material.dart';

class TournamentsListScreen extends StatelessWidget {
  const TournamentsListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tournaments'),
      ),
      body: const Center(
        child: Text('Tournaments List Screen'),
      ),
    );
  }
}

