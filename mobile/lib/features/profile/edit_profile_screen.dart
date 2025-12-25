import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sportlink/features/auth/data/repositories/auth_repository.dart';
import 'package:sportlink/features/auth/data/models/user_model.dart';
import 'package:sportlink/core/models/category.dart';
import 'package:sportlink/core/models/favorite_sport.dart';
import 'package:sportlink/core/services/category_service.dart';
import 'package:sportlink/core/services/user_service.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:io';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _cityController = TextEditingController();
  final _ageController = TextEditingController();
  
  final CategoryService _categoryService = CategoryService();
  final UserService _userService = UserService();
  final ImagePicker _imagePicker = ImagePicker();
  
  bool _isLoading = true;
  bool _isSaving = false;
  bool _isUploadingAvatar = false;
  UserModel? _currentUser;
  List<Category> _allCategories = [];
  
  String? _selectedGender;
  List<FavoriteSport> _selectedSports = [];
  File? _selectedAvatarFile;
  String? _currentAvatarUrl;
  
  final List<String> _genderOptions = ['male', 'female', 'other'];
  final Map<String, String> _genderLabels = {
    'male': 'Male',
    'female': 'Female',
    'other': 'Other',
  };

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      // Load user data
      final authRepo = ref.read(authRepositoryProvider);
      final user = await authRepo.getCurrentUser();
      
      // Load categories
      final categories = await _categoryService.getCategories();
      
      if (user != null && mounted) {
        setState(() {
          _currentUser = user;
          _firstNameController.text = user.firstName ?? '';
          _lastNameController.text = user.lastName ?? '';
          _emailController.text = user.email ?? '';
          _cityController.text = user.city ?? '';
          _ageController.text = user.age?.toString() ?? '';
          _selectedGender = user.gender;
          _selectedSports = List.from(user.favoriteSports);
          _currentAvatarUrl = user.avatarUrl;
          _allCategories = categories;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      final updateData = {
        'first_name': _firstNameController.text,
        'last_name': _lastNameController.text,
        'email': _emailController.text.isNotEmpty ? _emailController.text : null,
        'city': _cityController.text.isNotEmpty ? _cityController.text : null,
        'age': _ageController.text.isNotEmpty ? int.parse(_ageController.text) : null,
        'gender': _selectedGender,
        'favorite_sports': _selectedSports.map((sport) => sport.toJson()).toList(),
      };
      
      await _userService.updateProfile(updateData);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully!')),
        );
        Navigator.pop(context, true); // Return true to indicate profile was updated
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  void _addFavoriteSport() {
    showDialog(
      context: context,
      builder: (context) => _SportSelectionDialog(
        categories: _allCategories,
        selectedSports: _selectedSports,
        onSportSelected: (categoryId) {
          setState(() {
            _selectedSports.add(FavoriteSport(
              categoryId: categoryId,
              experienceLevel: 1,
            ));
          });
          Navigator.pop(context);
        },
      ),
    );
  }

  void _removeFavoriteSport(int index) {
    setState(() {
      _selectedSports.removeAt(index);
    });
  }

  void _updateExperienceLevel(int index, int level) {
    setState(() {
      _selectedSports[index] = _selectedSports[index].copyWith(
        experienceLevel: level,
      );
    });
  }

  String _getCategoryName(String categoryId) {
    final category = _allCategories.firstWhere(
      (cat) => cat.id == categoryId,
      orElse: () => Category(
        id: categoryId,
        nameI18n: {'en': 'Unknown'},
        icon: '',
      ),
    );
    return category.nameI18n['en'] ?? 'Unknown';
  }

  Future<void> _pickAndUploadAvatar() async {
    // Show options: Camera or Gallery
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.photo_camera),
              title: const Text('Take Photo'),
              onTap: () {
                Navigator.pop(context);
                _selectAvatar(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Choose from Gallery'),
              onTap: () {
                Navigator.pop(context);
                _selectAvatar(ImageSource.gallery);
              },
            ),
            if (_currentAvatarUrl != null)
              ListTile(
                leading: const Icon(Icons.delete, color: Colors.red),
                title: const Text('Remove Photo', style: TextStyle(color: Colors.red)),
                onTap: () {
                  Navigator.pop(context);
                  _deleteAvatar();
                },
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _selectAvatar(ImageSource source) async {
    try {
      // Request permissions
      if (source == ImageSource.camera) {
        final status = await Permission.camera.request();
        if (!status.isGranted) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Camera permission is required')),
            );
          }
          return;
        }
      } else {
        final status = await Permission.photos.request();
        if (!status.isGranted) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Gallery permission is required')),
            );
          }
          return;
        }
      }

      // Pick image
      final XFile? pickedFile = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (pickedFile == null) return;

      setState(() {
        _selectedAvatarFile = File(pickedFile.path);
        _isUploadingAvatar = true;
      });

      // Upload to server
      final avatarUrl = await _userService.uploadAvatar(_selectedAvatarFile!);

      if (mounted) {
        setState(() {
          _currentAvatarUrl = avatarUrl;
          _isUploadingAvatar = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Avatar uploaded successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isUploadingAvatar = false;
          _selectedAvatarFile = null;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error uploading avatar: $e')),
        );
      }
    }
  }

  Future<void> _deleteAvatar() async {
    try {
      setState(() => _isUploadingAvatar = true);

      await _userService.deleteAvatar();

      if (mounted) {
        setState(() {
          _currentAvatarUrl = null;
          _selectedAvatarFile = null;
          _isUploadingAvatar = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Avatar deleted successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isUploadingAvatar = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting avatar: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _cityController.dispose();
    _ageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Profile'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Profile Avatar
                    Center(
                      child: Stack(
                        children: [
                          _isUploadingAvatar
                              ? Container(
                                  width: 120,
                                  height: 120,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: Colors.grey[300],
                                  ),
                                  child: const Center(
                                    child: CircularProgressIndicator(),
                                  ),
                                )
                              : CircleAvatar(
                                  radius: 60,
                                  backgroundColor: Colors.grey[300],
                                  backgroundImage: _selectedAvatarFile != null
                                      ? FileImage(_selectedAvatarFile!)
                                      : (_currentAvatarUrl != null
                                          ? NetworkImage(_currentAvatarUrl!)
                                          : null) as ImageProvider?,
                                  child: (_selectedAvatarFile == null && _currentAvatarUrl == null)
                                      ? const Icon(Icons.person, size: 60, color: Colors.grey)
                                      : null,
                                ),
                          if (!_isUploadingAvatar)
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: CircleAvatar(
                                backgroundColor: Theme.of(context).primaryColor,
                                radius: 20,
                                child: IconButton(
                                  icon: const Icon(Icons.camera_alt, size: 20, color: Colors.white),
                                  onPressed: _pickAndUploadAvatar,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),
                    
                    // Basic Info Section
                    Text(
                      'Basic Information',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 16),
                    
                    // First Name
                    TextFormField(
                      controller: _firstNameController,
                      decoration: const InputDecoration(
                        labelText: 'First Name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your first name';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // Last Name
                    TextFormField(
                      controller: _lastNameController,
                      decoration: const InputDecoration(
                        labelText: 'Last Name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your last name';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // Email
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.email),
                      ),
                      validator: (value) {
                        if (value != null && value.isNotEmpty) {
                          if (!value.contains('@')) {
                            return 'Please enter a valid email';
                          }
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // City
                    TextFormField(
                      controller: _cityController,
                      decoration: const InputDecoration(
                        labelText: 'City',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.location_city),
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    // Age
                    TextFormField(
                      controller: _ageController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Age',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.cake),
                      ),
                      validator: (value) {
                        if (value != null && value.isNotEmpty) {
                          final age = int.tryParse(value);
                          if (age == null || age < 1 || age > 120) {
                            return 'Please enter a valid age';
                          }
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // Gender
                    DropdownButtonFormField<String>(
                      value: _selectedGender,
                      decoration: const InputDecoration(
                        labelText: 'Gender',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.wc),
                      ),
                      items: _genderOptions.map((gender) {
                        return DropdownMenuItem(
                          value: gender,
                          child: Text(_genderLabels[gender] ?? gender),
                        );
                      }).toList(),
                      onChanged: (value) {
                        setState(() {
                          _selectedGender = value;
                        });
                      },
                    ),
                    const SizedBox(height: 32),
                    
                    // Favorite Sports Section
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Favorite Sports',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.add_circle),
                          color: Theme.of(context).primaryColor,
                          onPressed: _addFavoriteSport,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    
                    if (_selectedSports.isEmpty)
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Center(
                          child: Text(
                            'No favorite sports selected.\nTap + to add one.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.grey),
                          ),
                        ),
                      )
                    else
                      ...List.generate(_selectedSports.length, (index) {
                        final sport = _selectedSports[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      _getCategoryName(sport.categoryId),
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.delete, color: Colors.red),
                                      onPressed: () => _removeFavoriteSport(index),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text('Experience Level: ${sport.experienceLevel}/10'),
                                Slider(
                                  value: sport.experienceLevel.toDouble(),
                                  min: 1,
                                  max: 10,
                                  divisions: 9,
                                  label: sport.experienceLevel.toString(),
                                  onChanged: (value) {
                                    _updateExperienceLevel(index, value.toInt());
                                  },
                                ),
                              ],
                            ),
                          ),
                        );
                      }),
                    
                    const SizedBox(height: 32),
                    
                    // Read-only fields
                    Text(
                      'Account Information',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 16),
                    
                    // Phone (read-only)
                    TextFormField(
                      initialValue: _currentUser?.phone ?? '',
                      enabled: false,
                      decoration: const InputDecoration(
                        labelText: 'Phone',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.phone),
                        suffixIcon: Icon(Icons.lock, size: 16),
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    // Nickname (read-only)
                    TextFormField(
                      initialValue: _currentUser?.nickname ?? '',
                      enabled: false,
                      decoration: const InputDecoration(
                        labelText: 'Nickname',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.alternate_email),
                        suffixIcon: Icon(Icons.lock, size: 16),
                      ),
                    ),
                    const SizedBox(height: 32),
                    
                    // Action Buttons
                    Row(
                      children: [
                        // Cancel Button
                        Expanded(
                          child: SizedBox(
                            height: 50,
                            child: OutlinedButton(
                              onPressed: _isSaving
                                  ? null
                                  : () {
                                      Navigator.pop(context);
                                    },
                              style: OutlinedButton.styleFrom(
                                side: BorderSide(color: Theme.of(context).primaryColor),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                              ),
                              child: Text(
                                'Cancel',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Theme.of(context).primaryColor,
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        // Save Button
                        Expanded(
                          flex: 2,
                          child: SizedBox(
                            child: ElevatedButton(
                              onPressed: _isSaving ? null : _saveProfile,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Theme.of(context).primaryColor,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                minimumSize: const Size(double.infinity, 56),
                              ),
                              child: _isSaving
                                  ? const SizedBox(
                                      width: 24,
                                      height: 24,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                      ),
                                    )
                                  : const Text(
                                      'Save Changes',
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        height: 1.2,
                                      ),
                                    ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
    );
  }
}

// Sport Selection Dialog
class _SportSelectionDialog extends StatelessWidget {
  final List<Category> categories;
  final List<FavoriteSport> selectedSports;
  final Function(String) onSportSelected;

  const _SportSelectionDialog({
    required this.categories,
    required this.selectedSports,
    required this.onSportSelected,
  });

  @override
  Widget build(BuildContext context) {
    // Filter out already selected sports
    final availableCategories = categories.where((category) {
      return !selectedSports.any((sport) => sport.categoryId == category.id);
    }).toList();

    return AlertDialog(
      title: const Text('Select Sport'),
      content: SizedBox(
        width: double.maxFinite,
        child: availableCategories.isEmpty
            ? const Text('All sports have been selected.')
            : ListView.builder(
                shrinkWrap: true,
                itemCount: availableCategories.length,
                itemBuilder: (context, index) {
                  final category = availableCategories[index];
                  return ListTile(
                    title: Text(category.nameI18n['en'] ?? 'Unknown'),
                    onTap: () => onSportSelected(category.id),
                  );
                },
              ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
      ],
    );
  }
}
