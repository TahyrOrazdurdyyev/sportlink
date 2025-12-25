import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sportlink/features/auth/data/repositories/auth_repository.dart';
import 'package:sportlink/core/l10n/app_localizations.dart';
import 'package:sportlink/core/utils/password_validator.dart';

class AuthScreen extends ConsumerStatefulWidget {
  const AuthScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends ConsumerState<AuthScreen> {
  bool isLoginMode = true;
  bool isLoading = false;
  
  // Controllers for Login
  final TextEditingController _loginController = TextEditingController();
  final TextEditingController _loginPasswordController = TextEditingController();
  
  // Controllers for Sign Up
  final TextEditingController _firstNameController = TextEditingController();
  final TextEditingController _lastNameController = TextEditingController();
  final TextEditingController _nicknameController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _signupPasswordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();
  
  String? errorMessage;
  
  // Locale state
  Locale _currentLocale = const Locale('en');

  @override
  void dispose() {
    _loginController.dispose();
    _loginPasswordController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _nicknameController.dispose();
    _phoneController.dispose();
    _signupPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    final l10n = AppLocalizations(_currentLocale);
    
    if (_loginController.text.trim().isEmpty || _loginPasswordController.text.isEmpty) {
      setState(() {
        errorMessage = l10n.allFieldsRequired;
      });
      return;
    }
    
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final authRepo = ref.read(authRepositoryProvider);
      final success = await authRepo.login(
        login: _loginController.text.trim(),
        password: _loginPasswordController.text,
      );

      if (success && mounted) {
        // Navigate to home screen
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } catch (e) {
      setState(() {
        errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  Future<void> _handleSignUp() async {
    final l10n = AppLocalizations(_currentLocale);
    
    // Validate all fields
    if (_firstNameController.text.trim().isEmpty ||
        _lastNameController.text.trim().isEmpty ||
        _nicknameController.text.trim().isEmpty ||
        _phoneController.text.trim().isEmpty ||
        _signupPasswordController.text.isEmpty ||
        _confirmPasswordController.text.isEmpty) {
      setState(() {
        errorMessage = l10n.allFieldsRequired;
      });
      return;
    }
    
    // Validate password match
    if (_signupPasswordController.text != _confirmPasswordController.text) {
      setState(() {
        errorMessage = l10n.passwordsDontMatch;
      });
      return;
    }
    
    // Validate password strength
    final passwordError = PasswordValidator.validate(
      _signupPasswordController.text,
      _currentLocale.languageCode,
    );
    if (passwordError != null) {
      setState(() {
        errorMessage = passwordError;
      });
      return;
    }
    
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final authRepo = ref.read(authRepositoryProvider);
      final success = await authRepo.register(
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        nickname: _nicknameController.text.trim(),
        phone: _phoneController.text.trim(),
        password: _signupPasswordController.text,
      );

      if (success && mounted) {
        // Navigate to home screen after successful registration
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } catch (e) {
      setState(() {
        errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations(_currentLocale);
    
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Language Selector
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    _LanguageButton(
                      label: 'EN',
                      isSelected: _currentLocale.languageCode == 'en',
                      onTap: () => setState(() => _currentLocale = const Locale('en')),
                    ),
                    const SizedBox(width: 8),
                    _LanguageButton(
                      label: 'RU',
                      isSelected: _currentLocale.languageCode == 'ru',
                      onTap: () => setState(() => _currentLocale = const Locale('ru')),
                    ),
                    const SizedBox(width: 8),
                    _LanguageButton(
                      label: 'TK',
                      isSelected: _currentLocale.languageCode == 'tk',
                      onTap: () => setState(() => _currentLocale = const Locale('tk')),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                
                // App Logo/Name
                Text(
                  l10n.appName,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).primaryColor,
                      ),
                ),
                const SizedBox(height: 48),

                // Toggle between Login and Sign Up
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () {
                          setState(() {
                            isLoginMode = true;
                            errorMessage = null;
                          });
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: isLoginMode
                              ? Theme.of(context).primaryColor
                              : Colors.grey[300],
                          foregroundColor: isLoginMode ? Colors.white : Colors.black,
                        ),
                        child: Text(l10n.login),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () {
                          setState(() {
                            isLoginMode = false;
                            errorMessage = null;
                          });
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: !isLoginMode
                              ? Theme.of(context).primaryColor
                              : Colors.grey[300],
                          foregroundColor: !isLoginMode ? Colors.white : Colors.black,
                        ),
                        child: Text(l10n.signUp),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),

                // Form
                if (isLoginMode) _buildLoginForm(l10n) else _buildSignUpForm(l10n),

                const SizedBox(height: 16),

                // Error Message
                if (errorMessage != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      errorMessage!,
                      style: TextStyle(color: Colors.red[900]),
                      textAlign: TextAlign.center,
                    ),
                  ),

                const SizedBox(height: 24),

                // Submit Button
                ElevatedButton(
                  onPressed: isLoading
                      ? null
                      : () {
                          if (isLoginMode) {
                            _handleLogin();
                          } else {
                            _handleSignUp();
                          }
                        },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Theme.of(context).primaryColor,
                    foregroundColor: Colors.white,
                  ),
                  child: isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : Text(
                          isLoginMode ? l10n.loginButton : l10n.signupButton,
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLoginForm(AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _loginController,
          decoration: InputDecoration(
            labelText: l10n.loginPlaceholder,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.person),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _loginPasswordController,
          obscureText: true,
          decoration: InputDecoration(
            labelText: l10n.password,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.lock),
          ),
        ),
      ],
    );
  }

  Widget _buildSignUpForm(AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _firstNameController,
          decoration: InputDecoration(
            labelText: l10n.firstName,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.person),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _lastNameController,
          decoration: InputDecoration(
            labelText: l10n.lastName,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.person_outline),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _nicknameController,
          decoration: InputDecoration(
            labelText: l10n.nickname,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.alternate_email),
            helperText: l10n.nicknameHelper,
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _phoneController,
          keyboardType: TextInputType.phone,
          decoration: InputDecoration(
            labelText: l10n.phone,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.phone),
            helperText: l10n.phoneHelper,
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _signupPasswordController,
          obscureText: true,
          decoration: InputDecoration(
            labelText: l10n.password,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.lock),
            helperText: l10n.passwordRequirements,
            helperMaxLines: 2,
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _confirmPasswordController,
          obscureText: true,
          decoration: InputDecoration(
            labelText: l10n.confirmPassword,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.lock_outline),
          ),
        ),
      ],
    );
  }
}

class _LanguageButton extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _LanguageButton({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? Theme.of(context).primaryColor : Colors.grey[300],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.black,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
