class PasswordValidator {
  /// Validates password strength
  /// Requirements:
  /// - At least 8 characters
  /// - Contains at least one letter
  /// - Contains at least one number
  /// - Contains at least one special character
  static bool isValid(String password) {
    if (password.length < 8) return false;
    
    // Check for at least one letter
    if (!RegExp(r'[a-zA-Z]').hasMatch(password)) return false;
    
    // Check for at least one number
    if (!RegExp(r'\d').hasMatch(password)) return false;
    
    // Check for at least one special character
    if (!RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(password)) return false;
    
    return true;
  }
  
  /// Returns error message if password is invalid, null otherwise
  static String? validate(String password, String locale) {
    if (!isValid(password)) {
      switch (locale) {
        case 'ru':
          return 'Пароль должен содержать минимум 8 символов, включая буквы, цифры и символы';
        case 'tk':
          return 'Parol azyndan 8 nyşany öz içine almalydyr, şol sanda harplar, sanlar we simwollar';
        default:
          return 'Password must contain at least 8 characters, including letters, numbers and symbols';
      }
    }
    return null;
  }
}

