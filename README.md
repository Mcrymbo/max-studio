# Max Studio - Video Streaming Platform

A complete video streaming platform with Django GraphQL backend, Next.js frontend, Flutter mobile app, and Jellyfin media engine.

## Architecture

- **Backend**: Django with Graphene-Django (GraphQL API)
- **Media Engine**: Jellyfin (handles transcoding, thumbnails, streaming)
- **Frontend**: Next.js (React-based, SEO-friendly)
- **Mobile**: Flutter (iOS/Android)
- **Database**: PostgreSQL
- **Storage**: Local filesystem (expandable to DigitalOcean Spaces/S3)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)
- Flutter (for mobile development)

### Using Docker Compose (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd max-studio
   ```

2. **Configure Jellyfin**:
   ```bash
   # Start Jellyfin first
   docker compose up jellyfin -d
   
   # Open http://localhost:8096 and complete setup
   # Create an API key in Dashboard > API Keys
   # Note your User ID from Dashboard > Users
   ```

3. **Set environment variables**:
   ```bash
   export JELLYFIN_API_KEY="your-api-key"
   export JELLYFIN_USER_ID="your-user-id"
   ```

4. **Start all services**:
   ```bash
   docker compose up -d
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend GraphQL: http://localhost:8000/graphql/
   - Jellyfin: http://localhost:8096
   - Nginx (production): http://localhost

### Local Development

#### Backend

```bash
cd backend

# Install dependencies
pipenv install

# Set environment variables
export USE_SQLITE=true
export JELLYFIN_URL=http://127.0.0.1:8096
export JELLYFIN_API_KEY="your-key"
export JELLYFIN_USER_ID="your-user-id"
export SIGNED_URL_SECRET="your-secret"

# Run migrations
pipenv run python manage.py migrate

# Create superuser
pipenv run python manage.py createsuperuser

# Start server
pipenv run python manage.py runserver
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8000/graphql/
export NEXT_PUBLIC_BACKEND_ORIGIN=http://localhost:8000

# Start development server
npm run dev
```

#### Mobile

```bash
cd mobile

# Install dependencies
flutter pub get

# Run on device/emulator
flutter run
```

## Features

### Backend (Django + GraphQL)

- **Authentication**: JWT-based auth with registration/login
- **Video Management**: Upload videos to Jellyfin library
- **GraphQL API**: Complete CRUD operations
- **Secure Streaming**: Signed URLs for video access
- **User Features**: Watchlists, saved videos

### Frontend (Next.js)

- **Browse Videos**: Grid layout with thumbnails
- **Video Player**: HLS streaming with signed URLs
- **Authentication**: Login/register pages
- **Watchlist**: Save and manage favorite videos
- **Responsive**: Works on desktop and mobile

### Mobile (Flutter)

- **Cross-platform**: iOS and Android support
- **Video Streaming**: HLS playback with video_player
- **Offline Downloads**: Download videos for offline viewing
- **GraphQL Integration**: Full API integration
- **Native UI**: Material Design components

### Media Engine (Jellyfin)

- **Auto-transcoding**: Multiple quality levels
- **Thumbnail Generation**: Automatic preview images
- **HLS Streaming**: Adaptive bitrate streaming
- **Library Management**: Organized media collections

## API Usage

### GraphQL Queries

```graphql
# List all videos
query {
  videos {
    id
    title
    thumbnailUrl
    playbackUrl
  }
}

# Get single video
query {
  video(id: "jellyfin-item-id") {
    title
    description
    playbackUrl
  }
}

# Login
mutation {
  tokenAuth(username: "user", password: "pass") {
    token
  }
}

# Save video to watchlist
mutation {
  saveVideo(videoId: "jellyfin-item-id") {
    ok
  }
}
```

### Authentication

Include JWT token in requests:
```
Authorization: JWT your-token-here
```

## Deployment

### DigitalOcean Droplet

1. **Create Droplet**: Ubuntu 22.04, 4GB RAM minimum
2. **Install Docker**: Follow Docker installation guide
3. **Clone Repository**: `git clone <repo>`
4. **Configure Environment**: Set production environment variables
5. **Start Services**: `docker compose up -d`
6. **Setup SSL**: Use Let's Encrypt with Nginx
7. **Configure Domain**: Point domain to droplet IP

### Environment Variables

```bash
# Production settings
DEBUG=false
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
POSTGRES_DB=maxstudio
POSTGRES_USER=maxstudio
POSTGRES_PASSWORD=secure-password

# Jellyfin
JELLYFIN_URL=http://jellyfin:8096
JELLYFIN_API_KEY=your-api-key
JELLYFIN_USER_ID=your-user-id

# Security
SIGNED_URL_SECRET=your-signed-url-secret
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## Development

### Adding New Features

1. **Backend**: Add GraphQL types/mutations in `backend/*/schema.py`
2. **Frontend**: Create new pages in `frontend/src/app/`
3. **Mobile**: Add screens in `mobile/lib/screens/`
4. **Testing**: Write tests for each component

### Database Migrations

```bash
# Create migration
pipenv run python manage.py makemigrations

# Apply migration
pipenv run python manage.py migrate
```

### Building Mobile Apps

```bash
# Build APK
flutter build apk --release

# Build iOS (macOS only)
flutter build ios --release
```

## Troubleshooting

### Common Issues

1. **Jellyfin not accessible**: Check API key and user ID
2. **Video playback fails**: Verify signed URL configuration
3. **CORS errors**: Update CORS settings in Django
4. **Mobile build fails**: Ensure Flutter SDK is up to date

### Logs

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs backend
docker compose logs frontend
docker compose logs jellyfin
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

