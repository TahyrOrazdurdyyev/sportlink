import 'package:flutter/material.dart';

class CourtsListScreen extends StatelessWidget {
  const CourtsListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Courts'),
      ),
      body: const Center(
        child: Text('Courts List Screen'),
      ),
    );
  }
}

