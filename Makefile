# Zimmer Integration Makefile

.PHONY: smoke test verify help

# Default target
help:
	@echo "Zimmer Integration Commands:"
	@echo "  make smoke     - Run production smoke test"
	@echo "  make test      - Run integration test suite"
	@echo "  make verify    - Verify implementation"
	@echo "  make help      - Show this help"

# Production smoke test
smoke:
	@echo "🚀 Running production smoke test..."
	@echo "Required environment variables:"
	@echo "  BASE_URL - Base URL of deployed service"
	@echo "  ZIMMER_SERVICE_TOKEN - Service token for authentication"
	@echo ""
	python smoke_test.py

# Integration test suite
test:
	@echo "🧪 Running integration test suite..."
	python test_zimmer_integration.py

# Implementation verification
verify:
	@echo "✅ Verifying implementation..."
	python verify_implementation.py

# Development server (for testing)
dev:
	@echo "🔧 Starting development server..."
	@echo "Set environment variables:"
	@echo "  export ZIMMER_SERVICE_TOKEN=test-token-123"
	@echo "  export OPENAI_API_KEY=your-key"
	@echo "  export TELEGRAM_TOKEN=your-token"
	python main.py