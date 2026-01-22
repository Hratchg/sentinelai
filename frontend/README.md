# SentinelAI Frontend

React dashboard for SentinelAI video surveillance system.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Lucide React** - Icons

## Features

- Video upload with drag-and-drop
- Real-time job monitoring with polling
- Video player for processed results
- Event timeline visualization
- Responsive design with dark mode
- Progress tracking (0-100%)
- Action summary statistics

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Frontend will run on http://localhost:5173

### 3. Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── Layout.tsx
│   ├── StatusBadge.tsx
│   └── ProgressBar.tsx
├── pages/           # Page components
│   ├── HomePage.tsx
│   ├── UploadPage.tsx
│   ├── JobsPage.tsx
│   └── ResultsPage.tsx
├── services/        # API services
│   └── api.ts
├── types/           # TypeScript types
│   └── index.ts
├── App.tsx          # Main app with routing
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/api/v1`.

Configure the API URL in `.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Pages

### Home Page (/)
- Welcome message and features
- Quick start guide
- Project statistics

### Upload Page (/upload)
- Drag-and-drop file upload
- File validation (format, size)
- Upload progress
- Redirects to results page on success

### Jobs Page (/jobs)
- List all jobs with status
- Real-time polling (every 2 seconds)
- Filter by status (queued, processing, completed, failed)
- Progress bars for active jobs
- Delete jobs

### Results Page (/results/:jobId)
- Video player for processed video
- Download button
- Video metadata (duration, FPS, frames)
- Action summary statistics
- Events timeline with timestamps

## Development

### Type Safety

All API responses are typed with TypeScript interfaces in `src/types/index.ts`.

### State Management

Using TanStack Query (React Query) for:
- Server state caching
- Automatic refetching
- Loading and error states
- Real-time polling

### Styling

TailwindCSS with custom theme and dark mode support.

## Troubleshooting

### CORS Errors

Make sure the backend has CORS enabled for `http://localhost:5173`.

The backend should have:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    ...
)
```

### API Connection Failed

1. Check backend is running: `http://localhost:8000/health`
2. Verify API URL in `.env`
3. Check browser console for errors

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT
