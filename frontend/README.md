# Frontend Documentation

Modern React + TypeScript frontend for Naukri Job Automation Dashboard.

## Features

- **Modern UI**: Built with React, TypeScript, and Tailwind CSS
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Dashboard polls for live automation status
- **Session Management**: Visual session status with countdown timer
- **Profile Management**: Complete profile editing interface
- **Resume Upload**: Drag-and-drop resume upload with parsing
- **Job Preferences**: Visual configuration of job search settings
- **Application History**: Searchable and filterable application log
- **Security**: No password storage, session-based authentication

## Tech Stack

- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **React Router**: Navigation
- **Axios**: HTTP client
- **Lucide React**: Icons

## Installation

1. **Install Node.js Dependencies**
```bash
cd frontend
npm install
```

2. **Configure Environment**
```bash
# No additional configuration needed
# API is proxied through Vite
```

## Development

### Start Development Server
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   │   └── Layout.tsx  # Main layout with sidebar
│   ├── pages/          # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Profile.tsx
│   │   ├── Resume.tsx
│   │   ├── JobPreferences.tsx
│   │   ├── Applications.tsx
│   │   └── Settings.tsx
│   ├── services/       # API services
│   │   └── api.ts      # API client
│   ├── types/          # TypeScript types
│   │   └── index.ts    # Type definitions
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript config
├── vite.config.ts      # Vite config
├── tailwind.config.js  # Tailwind config
└── postcss.config.js   # PostCSS config
```

## Pages

### Dashboard
- Naukri connection status
- Session expiry countdown
- Automation control (start/stop)
- Statistics cards (jobs found, applications, success rate)
- Quick actions

### Profile
- Personal information (name, email, phone, location)
- Professional information (experience, CTC, company)
- Skills management
- Additional context

### Resume
- Drag-and-drop upload
- Supported formats: PDF, DOC, DOCX
- Automatic parsing
- Review and edit extracted data
- Approve and sync with profile

### Job Preferences
- Target roles selection (20+ roles)
- Experience range
- Location preferences
- Salary expectations
- Work preferences (night shift, weekend)

### Applications
- Application history table
- Search by title/company
- Filter by status
- Summary statistics

### Settings
- Security information
- Data management (cleanup)
- API configuration
- Privacy notice

## API Integration

The frontend communicates with the backend via REST API:

```typescript
import apiService from '../services/api';

// Get session status
const status = await apiService.getSessionStatus();

// Update profile
await apiService.updateProfile({ full_name: 'John Doe' });

// Upload resume
const result = await apiService.uploadResume(file);

// Start automation
await apiService.startAutomation();
```

## Styling

The project uses Tailwind CSS with custom theme configuration:

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          // ... more shades
          600: '#2563eb',
        },
      },
    },
  },
}
```

Custom utility classes are defined in `index.css`:
- `.btn`: Base button styles
- `.btn-primary`: Primary button
- `.card`: Card component
- `.input`: Input field
- `.label`: Label text

## State Management

The frontend uses React's built-in state management with hooks:

```typescript
const [profile, setProfile] = useState<Profile>({});
const [loading, setLoading] = useState(false);

useEffect(() => {
  loadData();
}, []);
```

## Responsive Design

The layout is responsive:
- **Desktop**: Fixed sidebar, main content area
- **Tablet**: Collapsible sidebar (future enhancement)
- **Mobile**: Bottom navigation (future enhancement)

## Error Handling

All API calls include error handling:

```typescript
try {
  await apiService.updateProfile(profile);
  alert('Success!');
} catch (error) {
  alert('Failed: ' + error);
}
```

## Performance

- **Code Splitting**: Automatic with Vite
- **Lazy Loading**: Future enhancement
- **Caching**: Browser caching for static assets
- **Minification**: Automatic in production build

## Accessibility

- Semantic HTML
- ARIA labels (future enhancement)
- Keyboard navigation (future enhancement)
- Screen reader support (future enhancement)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Proxy Issues
If API calls fail, ensure the backend is running on port 5000.

### Build Errors
Clear node_modules and reinstall:
```bash
rm -rf node_modules
npm install
```

### TypeScript Errors
Ensure all types are properly defined in `src/types/index.ts`.

## Future Enhancements

- WebSocket for real-time updates
- Dark mode toggle
- Advanced filtering
- Export to Excel
- Mobile app
- PWA support
