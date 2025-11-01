# OCR Gaby - React Interface Specification

## Overview
A modern, clean web interface for OCR document processing with AI analysis capabilities. The app should have a professional look with gradient backgrounds, card-based layouts, and smooth interactions.

## Technology Stack
- React 19 with TypeScript
- Tailwind CSS for styling
- ShadCN UI components (Button, Card, Select, Switch, Tabs, Toast)
- Axios for API calls
- Lucide React for icons

## Layout Structure

### Main Container
- Full viewport height with gradient background: `from-slate-50 to-slate-100`
- Dark mode support: `dark:from-slate-900 dark:to-slate-800`
- Max width container (7xl) with padding
- Responsive grid layout

### Header Section
- Large title: "OCR Gaby" (4xl, bold)
- Subtitle: "Extract text from images with OCR and AI-powered analysis"
- 8 margin bottom spacing

### Main Content Grid
Three-column layout (responsive):
- Left column (1/3): Upload & Settings panels
- Right column (2/3): Results panel

## Components

### 1. Upload Panel (White Card)
**Location:** Top of left column

**Elements:**
- Card header with Upload icon and title "Upload Document"
- Dashed border drop zone for file upload
  - FileText icon (large, centered)
  - Display filename when file selected, or "Click to select file"
  - Supported formats note: "JPG, PNG, PDF up to 10MB"
- Hidden file input (click label to trigger)
- Large primary button: "Process Document" with Sparkles icon
  - Disabled when no file selected or processing
  - Shows "Processing..." with spinning Loader2 icon when active
  - Blue background with hover state

### 2. Settings Panel (White Card)
**Location:** Below upload panel

**Settings:**

a) **Language Select**
- Label: "Language"
- Dropdown with options:
  - English (eng)
  - Spanish (spa)
  - French (fra)
  - German (deu)

b) **Image Preprocessing Toggle**
- Label: "Image Preprocessing"
- Switch component (boolean)

c) **AI Analysis Toggle**
- Label: "AI Analysis (Gemini)"
- Switch component (boolean)

d) **AI Task Select** (conditional - only shown when Gemini enabled)
- Label: "AI Task"
- Dropdown with options:
  - Analyze
  - Summarize
  - Extract Data
  - Structure
  - Translate
  - Validate
  - Format

e) **Custom Prompt Textarea** (conditional - only shown when Gemini enabled)
- Label: "Custom Prompt (Optional)"
- Placeholder: "e.g., Extract all dates and amounts..."
- 3 rows
- Optional field for custom instructions

### 3. Results Panel (White Card - Full Height)
**Location:** Right side, spans 2/3 width

**Header:**
- Title: "Results"
- Description: "Extracted text and AI analysis"

**Empty State:**
- Large FileText icon (slate-300/slate-700)
- Message: "No results yet. Upload and process a document to get started."
- Centered, 96 height

**With Results:**
Use Tabs component with two tabs:
- "OCR Text" (default)
- "AI Analysis" (disabled if no Gemini results)

#### OCR Text Tab Content:

**Stats Grid (4 columns):**
- Confidence % (slate background, rounded)
- Word Count
- Character Count
- Language (uppercase)

**Extracted Text Section:**
- Label: "Extracted Text" or similar
- Light slate background box with border
- Monospace font for text
- Pre-wrap whitespace handling
- Copy to Clipboard button (outline style)

#### AI Analysis Tab Content (when available):

**Analysis Header:**
- Gradient background (purple-50 to blue-50)
- Sparkles icon with purple color
- "AI Analysis - {task name}"

**Analysis Text:**
- Light slate background box with border
- Sans-serif font (not monospace)
- Pre-wrap whitespace
- Purple-themed styling
- Copy Analysis button (outline style)

## State Management

### Component State:
```typescript
const [file, setFile] = useState<File | null>(null)
const [loading, setLoading] = useState(false)
const [ocrResult, setOcrResult] = useState<OCRResult | null>(null)
const [geminiResult, setGeminiResult] = useState<GeminiResult | null>(null)

// Settings
const [language, setLanguage] = useState('eng')
const [preprocess, setPreprocess] = useState(false)
const [useGemini, setUseGemini] = useState(false)
const [geminiTask, setGeminiTask] = useState('analyze')
const [customPrompt, setCustomPrompt] = useState('')
```

### Interfaces:
```typescript
interface OCRResult {
  text: string
  confidence: number
  word_count: number
  character_count: number
  language: string
}

interface GeminiResult {
  success: boolean
  response: string
  task: string
}
```

## API Integration

### Base URL
```typescript
const API_BASE_URL = '/api'
```

### File Upload Handler
- Validate file exists
- Clear previous results and errors
- Store file in state

### Process Handler

**FormData Construction:**
- Append file
- Append language
- Append preprocess (as string)
- If Gemini enabled: append gemini_task and optional gemini_prompt

**API Calls:**

1. **With Gemini:**
   - POST to `/api/ocr/gemini`
   - multipart/form-data
   - On success: set ocrResult and geminiResult
   - Show toast: "Document processed with AI analysis"

2. **Without Gemini:**
   - POST to `/api/ocr`
   - multipart/form-data
   - On success: set ocrResult only
   - Show toast: "Text extracted from document"

**Error Handling:**
- Catch errors and show toast with error message
- Use destructive variant for error toasts

**Loading State:**
- Set loading true at start
- Set loading false in finally block
- Disable button and show spinner during processing

## Toast Notifications

Use shadcn toast system with:
- Success toasts (green) for successful operations
- Destructive toasts (red) for errors
- Toast component rendered at app root: `<Toaster />`

## Styling Guidelines

### Colors:
- Primary: Blue (blue-600, blue-700 hover)
- Success: Default toast styling
- Error: Destructive variant
- OCR section: Slate grays
- AI section: Purple/blue gradients
- Backgrounds: White cards on gradient slate background

### Typography:
- Headers: Bold, larger sizes (2xl, 4xl)
- Labels: Medium weight, small size
- Body text: Regular weight
- Monospace: For extracted OCR text
- Sans-serif: For AI analysis

### Spacing:
- Consistent gap-4, gap-6 for grids
- p-4, p-6 for card padding
- mb-4, mb-6, mb-8 for vertical spacing
- space-y-2, space-y-4 for stacked elements

### Interactive Elements:
- Hover states on clickable elements
- Disabled states with reduced opacity
- Smooth transitions
- Visual feedback on interactions

## Responsive Behavior
- Mobile: Single column layout
- Tablet: Maintain some side-by-side
- Desktop: Full 1/3 - 2/3 split
- Use lg: breakpoint for major layout shifts

## Accessibility
- Proper labels for all form inputs
- IDs linking labels to inputs
- Disabled states on buttons
- Alt text for icons (screen reader friendly)
- Keyboard navigation support

## User Flow

1. User lands on page → sees empty state
2. User clicks upload area → file picker opens
3. User selects image → filename displays
4. User optionally adjusts settings
5. User clicks "Process Document" → button shows loading
6. API processes → results display
7. User can view OCR and/or AI analysis in tabs
8. User can copy results to clipboard
9. User can upload another file → results clear and process repeats

## Error States
- No file selected → show toast notification
- API error → show toast with error message
- Network error → show generic error message
- Invalid file type → backend validates, shows error

## Success States
- OCR complete → show stats + extracted text
- Gemini complete → enable AI Analysis tab with results
- Both complete → user can switch between tabs

## Final Notes
- Clean, professional interface
- Fast, responsive interactions
- Clear visual hierarchy
- Progressive disclosure (Gemini options only when enabled)
- Intuitive workflow
- Mobile-friendly responsive design
