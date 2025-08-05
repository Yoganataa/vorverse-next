# Ultimate Hybrid Dynamic Bot Framework V3

A production-ready, highly extensible Telegram media downloader bot with precision replication of proven engines.

## 🚀 Features

### Core Capabilities
- **Hybrid Tiered Engine**: Intelligently deploys the best tool for each platform
- **Dynamic Configuration**: All settings controlled via `.env` file
- **High Concurrency**: asyncio-based task processing with semaphore control
- **Advanced Downloads**: Resume capability, multi-retry, atomic file operations
- **Multi-Database Support**: PostgreSQL, MySQL, SQLite with SQLAlchemy
- **Role-Based Access Control**: Admin commands with user management
- **Production Ready**: Docker containerization with health checks

### Supported Platforms
- **TikTok & Douyin** (via JoeanAmier/TikTokDownloader precision replication)
- **Instagram** (Posts, Reels, IGTV via instaloader)
- **YouTube** (Videos, Shorts via yt-dlp)
- **Twitter/X** (via yt-dlp)
- **Facebook** (via yt-dlp)
- **Generic** (Any yt-dlp supported platform)

## 📦 Installation

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vorverse_hybrid_framework
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Manual Installation

1. **Install Python 3.9+**
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Setup directories**
   ```bash
   mkdir -p data/cookies downloads logs
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the bot**
   ```bash
   python -m app.main
   ```

## ⚙️ Configuration

### Required Settings

```bash
# Bot credentials (from @BotFather)
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id
API_HASH=your_api_hash

# Admin users (comma-separated user IDs)
ADMIN_IDS=123456789,987654321
```

### Platform-Specific Settings

#### TikTok Configuration
All parameters from JoeanAmier/TikTokDownloader are supported:

```bash
TIKTOK_COOKIE_FILE=./data/cookies/tiktok.txt
TIKTOK_NAME_FORMAT={create}_{desc}_{id}
TIKTOK_MAX_SIZE=104857600
TIKTOK_BROWSER_INFO={"headers": {"User-Agent": "Mozilla/5.0..."}}
```

#### Instagram Configuration
```bash
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_SESSION_FILE=./data/instagram_session
```

### Database Configuration
```bash
# SQLite (default)
DATABASE_URL=sqlite:///./data/bot_database.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/dbname

# MySQL
DATABASE_URL=mysql://user:password@localhost/dbname
```

## 🎛️ Admin Commands

- `/promote` - Promote user to admin (reply to message)
- `/verify` - Verify user (reply to message)
- `/ban` - Ban user (reply to message)
- `/unban` - Unban user (reply to message)
- `/stats` - Show bot statistics
- `/stop` - Graceful shutdown
- `/reboot` - Restart bot

## 🏗️ Architecture

### Directory Structure
```
vorverse_hybrid_framework/
├── app/
│   ├── config.py              # Central configuration management
│   ├── main.py                # Main entry point & asyncio worker
│   ├── handlers/              # Message handlers
│   ├── services/              # Downloader services
│   ├── tiktok_dl_lib/         # JoeanAmier library integration
│   └── utils/                 # Utility modules
├── data/
│   ├── platforms.yml          # YT-DLP platform configs
│   ├── bot_database.db        # SQLite database
│   └── cookies/               # Cookie files
├── .env                       # Configuration
├── Dockerfile                 # Multi-stage container build
└── docker-compose.yml         # Container orchestration
```

### Service Architecture

1. **Dynamic Configuration Bridge**: Precisely replicates JoeanAmier/TikTokDownloader settings
2. **Plugin-Based Discovery**: Auto-discovers downloader services
3. **In-Memory Task Queue**: High-performance asyncio.Queue with semaphore control
4. **Advanced Download Core**: Resume capability, atomic operations, multi-retry

## 🔧 Development

### Adding New Platforms

1. Create service in `app/services/{platform}_service.py`
2. Inherit from `BaseDownloader`
3. Implement `download()` method
4. Add URL patterns to `URLParser`
5. Service auto-discovery handles registration

### Testing

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
```

## 🚀 Deployment

### Production Deployment

1. **Use multi-stage Dockerfile**
   ```bash
   docker build -t media-downloader-bot .
   ```

2. **Environment-specific configs**
   ```bash
   # Production
   LOG_LEVEL=WARNING
   MAX_CONCURRENT_DOWNLOADS=10
   
   # Development  
   LOG_LEVEL=DEBUG
   MAX_CONCURRENT_DOWNLOADS=3
   ```

3. **Resource limits**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
         cpus: '1.0'
   ```

### Monitoring

- Health checks via Docker
- Prometheus metrics (optional)
- Structured logging to files
- Database query optimization

## 📊 Performance

- **Concurrent Downloads**: Configurable semaphore control
- **Memory Efficient**: Streaming downloads with chunked processing
- **Resume Capability**: HTTP Range requests for interrupted downloads
- **Atomic Operations**: Two-stage file saving prevents corruption

## 🔒 Security

- **Role-Based Access**: Admin/verified user/user roles
- **Input Validation**: URL parsing and sanitization
- **File Size Limits**: Configurable maximum file sizes
- **Cookie Management**: Secure Netscape format cookie handling

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- 📧 Email: support@example.com
- 💬 Telegram: @support_channel
- 🐛 Issues: GitHub Issues page

---

**Note**: This framework implements precision replication of JoeanAmier/TikTokDownloader and instaloader engines. Ensure you have proper permissions and follow terms of service for all platforms.