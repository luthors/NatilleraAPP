# Natillera Mobile

React Native + Expo mobile application for iOS and Android.

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with API_BASE_URL

# 3. Start Expo
npx expo start

# 4. Open in device
# Scan QR code with Expo Go app
# OR press 'a' for Android emulator, 'i' for iOS simulator
```

## Structure

```
app/
├── index.jsx            # Entry point
├── (tabs)/              # Tab navigation
│   ├── _layout.jsx
│   ├── index.jsx        # Dashboard tab
│   ├── pagos.jsx        # Pagos tab
│   └── profile.jsx      # Profile tab
├── screens/             # Screen components
│   ├── Auth/
│   │   ├── LoginScreen.jsx
│   │   └── RegisterScreen.jsx
│   ├── Natilleras/
│   │   └── NatilleraDetailScreen.jsx
│   └── Common/
└── navigation/          # Navigation config
services/                # API calls
hooks/                   # Custom hooks
utils/                   # Utilities
```

## Development

```bash
# Start dev server
npx expo start

# Run on Android emulator
npx expo start --android

# Run on iOS simulator
npx expo start --ios

# Run on web
npx expo start --web

# Build for production
eas build --platform android
eas build --platform ios
```

## Configuration

Environment variables in `.env`:
- `EXPO_PUBLIC_API_BASE_URL` - Backend API URL (default: http://localhost:8000)
- `EXPO_PUBLIC_APP_NAME` - Application name

## Dependencies

- Expo - Development platform
- React Native - Mobile UI library
- React Navigation - Navigation
- Axios - HTTP client
- Zustand - State management

## Deployment

Build and submit to app stores:

```bash
# Create EAS account
eas login

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

See DEPLOYMENT.md for detailed instructions.

## Testing on Device

### Expo Go App
1. Install Expo Go from App Store / Play Store
2. Run `npx expo start`
3. Scan QR code with Expo Go

### Android Emulator
1. Install Android Studio
2. Create virtual device
3. Run `npx expo start --android`

### iOS Simulator
1. Install Xcode
2. Run `npx expo start --ios`

## Contributing

1. Create feature branch: `git checkout -b feat/feature-name`
2. Make changes
3. Commit: `git commit -m "feat: description"`
4. Push: `git push origin feat/feature-name`
5. Create Pull Request
