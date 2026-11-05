# App Logo

Place your app logo here. Recommended format: PNG with transparent background.

## Recommended specifications:
- **Format**: PNG (with transparency)
- **Size**: At least 1024x1024 pixels (square image)
- **Background**: Transparent or solid color
- **File name**: `app_logo.png`

## To set the app icon:

The configuration for `flutter_launcher_icons` is already set up in `pubspec.yaml`.

1. Place your logo file as `app_logo.png` in this folder (`assets/images/app_logo.png`)

2. Run the following commands:
   ```bash
   flutter pub get
   flutter pub run flutter_launcher_icons
   ```

3. This will automatically generate all required icon sizes for:
   - Android (various densities: mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi)
   - iOS (various sizes for iPhone and iPad)

4. Rebuild your app to see the new icon

## Note:
- The icon generation tool will automatically resize your logo to all required sizes
- Make sure your logo is square (equal width and height) for best results
- The logo should be recognizable even at small sizes (app icons are often displayed very small)
