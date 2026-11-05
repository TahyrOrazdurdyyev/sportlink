import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sportlink/core/providers/locale_provider.dart';
import 'package:sportlink/core/l10n/app_localizations.dart';
import 'package:sportlink/features/settings/change_password_screen.dart';
import 'package:sportlink/features/legal/legal_document_screen.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _locationEnabled = true;

  @override
  Widget build(BuildContext context) {
    final loc = AppLocalizations.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(loc.settingsTitle),
      ),
      body: ListView(
        children: [
          // Notifications Section
          _buildSectionHeader(loc.notificationsSection),
          SwitchListTile(
            title: Text(loc.pushNotifications),
            subtitle: Text(loc.pushNotificationsSubtitle),
            value: _notificationsEnabled,
            onChanged: (value) {
              setState(() => _notificationsEnabled = value);
            },
          ),
          const Divider(),
          
          // Location Section
          _buildSectionHeader(loc.locationSection),
          SwitchListTile(
            title: Text(loc.locationServices),
            subtitle: Text(loc.locationServicesSubtitle),
            value: _locationEnabled,
            onChanged: (value) {
              setState(() => _locationEnabled = value);
            },
          ),
          const Divider(),
          
          // Language Section
          _buildSectionHeader(loc.languageSection),
          ListTile(
            title: Text(loc.languageLabel),
            subtitle: Text(ref.read(localeProvider.notifier).getLanguageName(ref.watch(localeProvider).languageCode)),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              _showLanguagePicker();
            },
          ),
          const Divider(),
          
          // Account Section
          _buildSectionHeader(loc.accountSection),
          ListTile(
            leading: const Icon(Icons.lock),
            title: Text(loc.changePassword),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ChangePasswordScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.privacy_tip),
            title: Text(loc.privacyPolicy),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => LegalDocumentScreen(
                    documentType: 'privacy_policy',
                    title: loc.privacyPolicy,
                  ),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.description),
            title: Text(loc.termsOfService),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => LegalDocumentScreen(
                    documentType: 'terms_of_service',
                    title: loc.termsOfService,
                  ),
                ),
              );
            },
          ),
          const Divider(),
          
          // App Info
          _buildSectionHeader(loc.aboutSection),
          ListTile(
            leading: const Icon(Icons.info),
            title: Text(loc.appVersion),
            subtitle: const Text('1.0.0'),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).primaryColor,
        ),
      ),
    );
  }

  void _showLanguagePicker() {
    final currentLocale = ref.read(localeProvider);
    final loc = AppLocalizations.of(context);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(loc.selectLanguage),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('English'),
              value: 'en',
              groupValue: currentLocale.languageCode,
              onChanged: (value) {
                ref.read(localeProvider.notifier).setLocale(const Locale('en'));
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Language changed to English')),
                );
              },
            ),
            RadioListTile<String>(
              title: const Text('Русский'),
              value: 'ru',
              groupValue: currentLocale.languageCode,
              onChanged: (value) {
                ref.read(localeProvider.notifier).setLocale(const Locale('ru'));
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Язык изменен на Русский')),
                );
              },
            ),
            RadioListTile<String>(
              title: const Text('Türkmençe'),
              value: 'tk',
              groupValue: currentLocale.languageCode,
              onChanged: (value) {
                ref.read(localeProvider.notifier).setLocale(const Locale('tk'));
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Dil Türkmençä üýtgedildi')),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

