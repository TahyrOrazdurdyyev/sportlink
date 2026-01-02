import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

/// Custom MaterialLocalizations delegate that falls back to English
/// for Material widgets when using Turkmen locale, since Flutter doesn't
/// have built-in support for Turkmen MaterialLocalizations
class TurkmenMaterialLocalizationsDelegate extends LocalizationsDelegate<MaterialLocalizations> {
  const TurkmenMaterialLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'ru', 'tk'].contains(locale.languageCode);
  }

  @override
  Future<MaterialLocalizations> load(Locale locale) async {
    // For Turkmen locale, use English MaterialLocalizations as fallback
    // since Flutter doesn't have built-in Turkmen support
    if (locale.languageCode == 'tk') {
      return await GlobalMaterialLocalizations.delegate.load(const Locale('en'));
    }
    // For other locales, use standard MaterialLocalizations
    return await GlobalMaterialLocalizations.delegate.load(locale);
  }

  @override
  bool shouldReload(TurkmenMaterialLocalizationsDelegate old) => false;
}

