# SkillTree.io Frontend

Modern React-based frontend for the SkillTree.io GitHub repository analyzer.

## 🚀 Features

- **Split-Screen Interface**: Side-by-side resume and proficiency chart display
- **Real-time Validation**: Client-side GitHub URL validation with instant feedback
- **Interactive Charts**: Plotly-powered skill proficiency visualizations
- **Export Functionality**: Download resumes as Markdown or copy to clipboard
- **Responsive Design**: Mobile-first Tailwind CSS styling
- **Loading States**: Animated status indicators during analysis
- **Preset Examples**: Quick-start demo repositories

## 📦 Tech Stack

- **Framework**: React 18.3+ with Vite 5.1+
- **Styling**: Tailwind CSS 3.4+
- **Charts**: Plotly.js (basic-dist-min) + react-plotly.js
- **Markdown**: react-markdown 9.0+
- **Icons**: lucide-react 0.344+

## 🛠️ Installation

```bash
cd frontend
npm install
```

## 🏃 Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 🏗️ Build

Create a production build:

```bash
npm run build
```

Build output will be in the `dist/` directory.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── RepoInput.jsx          # GitHub URL input with validation
│   │   ├── LoadingState.jsx       # Animated loading indicators
│   │   ├── ResumePanel.jsx        # Markdown resume display
│   │   ├── ProficiencyChart.jsx   # Plotly skill chart
│   │   └── ExportBar.jsx          # Export utilities
│   ├── styles/
│   │   └── index.css              # Global styles & Tailwind
│   ├── api.js                     # Backend API client
│   ├── App.jsx                    # Main application
│   └── main.jsx                   # Entry point
├── index.html                     # HTML template
├── vite.config.js                 # Vite configuration
├── tailwind.config.js             # Tailwind configuration
├── postcss.config.js              # PostCSS configuration
└── package.json                   # Dependencies
```

## 🧩 Components

### RepoInput
- GitHub URL validation with regex
- Real-time validation feedback
- Preset repository examples
- Loading state handling

### LoadingState
- Cycling status messages
- Animated progress indicators
- Customizable messages
- Compact mode support

### ResumePanel
- Markdown rendering with react-markdown
- Custom styled components
- Copy to clipboard
- Download as .md file
- Empty state handling

### ProficiencyChart
- Horizontal bar chart
- Color-coded by category
- Interactive tooltips
- Responsive sizing
- Export to PNG
- Statistics footer

### ExportBar
- Reusable export component
- Copy to clipboard
- File download
- Success feedback

## 🎨 Styling

The project uses Tailwind CSS with custom configurations:

- **Primary Color**: Blue (#0ea5e9)
- **Custom Components**: `.panel-container`, `.btn-primary`, `.input-field`
- **Custom Scrollbars**: Thin, styled scrollbars
- **Responsive Breakpoints**: Mobile-first approach

## 🔌 API Integration

The frontend communicates with the backend via the `/analyze` endpoint:

```javascript
import { analyzeRepo } from './api'

const data = await analyzeRepo('https://github.com/user/repo')
```

Expected response structure:
```json
{
  "resume_markdown": "# Resume content...",
  "skills": [
    {
      "name": "JavaScript",
      "proficiency": 85.5,
      "category": "Language"
    }
  ],
  "metadata": {
    "repo_name": "user/repo"
  }
}
```

## 🧪 Testing

Run frontend integration tests:

```bash
# From project root
python scripts/test_frontend_build.py
python scripts/test_frontend_integration.py
```

## 🚦 Development Workflow

1. **Start Backend**: Ensure the FastAPI backend is running on port 8000
2. **Start Frontend**: Run `npm run dev` in the frontend directory
3. **Test**: Use preset examples or enter a GitHub URL
4. **Build**: Run `npm run build` before deployment

## 📝 Environment Variables

The Vite dev server proxies `/analyze` requests to `http://localhost:8000`.

For production, configure your web server to proxy API requests appropriately.

## 🔧 Configuration

### Vite Proxy (Development)
```javascript
server: {
  proxy: {
    '/analyze': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### Build Optimization
- Manual chunks for React and Plotly vendors
- Source maps enabled
- Gzip compression ready

## 📊 Performance

- **Initial Load**: ~150KB (gzipped, excluding Plotly)
- **Plotly Vendor**: ~1.5MB (gzipped, lazy-loaded)
- **Build Time**: ~60 seconds
- **Hot Reload**: < 1 second

## 🐛 Troubleshooting

### Build Fails
- Ensure Node.js 18+ is installed
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for syntax errors in components

### Plotly Not Loading
- Verify `plotly.js-basic-dist-min` is installed
- Check browser console for import errors
- Ensure build completed successfully

### API Errors
- Verify backend is running on port 8000
- Check CORS configuration
- Inspect network tab for request details

## 📄 License

Part of the SkillTree.io project. See root LICENSE file.

## 🤝 Contributing

1. Follow the existing component structure
2. Use TypeScript-style JSDoc comments
3. Maintain Tailwind CSS conventions
4. Test with `npm run build` before committing
5. Run integration tests

## 🎯 Future Enhancements

- [ ] Dark mode support
- [ ] Multiple chart types (radar, tree)
- [ ] PDF export
- [ ] Skill comparison view
- [ ] Repository history tracking
- [ ] Custom theme configuration
