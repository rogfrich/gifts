#!/bin/bash

# Always move to project root
cd "$(dirname "$0")/.." || { echo "Failed to move to project root"; exit 1; }

echo "Running app tests (gifts/tests.py)..."
if ! python manage.py test gifts; then
    echo "❌ App tests failed (gifts)"
    exit 1
fi
echo "✅ App tests passed!"

echo "Running utils tests (utils/test_exporter.py and utils/test_importer.py)..."
if ! python manage.py test utils; then
    echo "❌ Utils tests failed (utils)"
    exit 1
fi
echo "✅ Utils tests passed!"

echo "🎉 All tests passed successfully!"