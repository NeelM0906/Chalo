#!/bin/bash

echo "Building and Running Local Wander iOS App..."
echo "==========================================="

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "Error: Xcode is not installed. Please install Xcode from the App Store."
    exit 1
fi

# Check if iOS Simulator is available
if ! xcrun simctl list devices | grep -q "iPhone"; then
    echo "Error: No iOS Simulator found. Please install iOS Simulator in Xcode."
    exit 1
fi

# Get the first available iPhone simulator
SIMULATOR=$(xcrun simctl list devices | grep "iPhone" | head -1 | sed 's/.*(\([^)]*\)).*/\1/')

if [ -z "$SIMULATOR" ]; then
    echo "Error: Could not find iPhone simulator."
    exit 1
fi

echo "Using simulator: $SIMULATOR"

# Build the project
echo "Building project..."
xcodebuild -project LocalWanderApp.xcodeproj -scheme LocalWanderApp -destination "platform=iOS Simulator,id=$SIMULATOR" build

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo "Build successful!"
echo ""
echo "To run the app:"
echo "1. Open LocalWanderApp.xcodeproj in Xcode"
echo "2. Select your target device/simulator"
echo "3. Press Cmd+R to run"
echo ""
echo "Or use: xcrun simctl install $SIMULATOR /path/to/app" 