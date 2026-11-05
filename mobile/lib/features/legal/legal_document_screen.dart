import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:sportlink/core/network/api_client.dart';
import 'package:sportlink/core/providers/locale_provider.dart';

class LegalDocumentScreen extends ConsumerStatefulWidget {
  final String documentType; // 'privacy_policy' or 'terms_of_service'
  final String title;

  const LegalDocumentScreen({
    Key? key,
    required this.documentType,
    required this.title,
  }) : super(key: key);

  @override
  ConsumerState<LegalDocumentScreen> createState() => _LegalDocumentScreenState();
}

class _LegalDocumentScreenState extends ConsumerState<LegalDocumentScreen> {
  bool _isLoading = true;
  String _content = '';
  String _documentTitle = '';
  String _version = '';
  String _effectiveDate = '';
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadDocument();
  }

  Future<void> _loadDocument() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final locale = ref.read(localeProvider);
      
      final endpoint = widget.documentType == 'privacy_policy'
          ? '/legal/privacy-policy/'
          : '/legal/terms-of-service/';
      
      final response = await apiClient.dio.get(
        endpoint,
        queryParameters: {'lang': locale.languageCode},
      );

      if (mounted) {
        final data = response.data;
        setState(() {
          _documentTitle = data['title'][locale.languageCode] ?? data['title']['en'] ?? widget.title;
          _content = data['content'][locale.languageCode] ?? data['content']['en'] ?? '';
          _version = data['version'] ?? '1.0';
          _effectiveDate = data['effective_date'] ?? '';
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to load document: $e';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          if (_version.isNotEmpty)
            Center(
              child: Padding(
                padding: const EdgeInsets.only(right: 16),
                child: Text(
                  'v$_version',
                  style: const TextStyle(fontSize: 12, color: Colors.white70),
                ),
              ),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        Text(
                          _error!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Colors.red),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadDocument,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : Markdown(
                  data: _content,
                  selectable: true,
                  styleSheet: MarkdownStyleSheet(
                    h1: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                    h2: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                    h3: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                    p: const TextStyle(fontSize: 14, height: 1.5),
                    listBullet: const TextStyle(fontSize: 14),
                  ),
                ),
    );
  }
}

