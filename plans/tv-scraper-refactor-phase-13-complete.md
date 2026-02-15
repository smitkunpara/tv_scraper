## Phase 13 Complete: Streaming Refactor + Realtime Feature

Refactored the entire streaming package into `tv_scraper/streaming/` with renamed methods, standardized response envelopes, and a new persistent realtime price streaming API.

**Files created/changed:**
- tv_scraper/streaming/__init__.py (updated exports)
- tv_scraper/streaming/stream_handler.py
- tv_scraper/streaming/streamer.py
- tv_scraper/streaming/price.py
- tv_scraper/streaming/utils.py
- tests_new/unit/test_streaming.py
- docs_new/streaming/index.md
- docs_new/streaming/streamer.md
- docs_new/streaming/realtime-price.md

**Functions created/changed:**
- StreamHandler: generate_session, prepend_header, construct_message, create_message, send_message, _initialize, _initialize_sessions
- Streamer: get_candles (renamed from stream), stream (alias), stream_realtime_price (new), _add_symbol_to_sessions, _add_indicators, _serialize_ohlc, _extract_indicator_from_stream, get_data, _export, _success_response, _error_response
- RealTimeData: get_ohlcv, get_latest_trade_info, _add_symbol_to_sessions, _get_data
- Utils: validate_symbols, fetch_tradingview_indicators, fetch_indicator_metadata, prepare_indicator_metadata

**Tests created/changed:**
- TestStreamHandler: 8 tests (session format, header, message construction, initialization)
- TestStreamer: 9 tests (get_candles success/ohlc/indicators/timeframe/export/alias, stream_realtime_price, heartbeat, error response)
- TestRealTimeData: 3 tests (ohlcv generator, trade info generator, heartbeat)
- TestStreamingUtils: 5 tests (validate valid/invalid, fetch metadata, prepare metadata, search indicators)
- Total: 25 tests, 238 total suite

**Review Status:** APPROVED

**Git Commit Message:**
feat: add Streaming module with realtime price API
