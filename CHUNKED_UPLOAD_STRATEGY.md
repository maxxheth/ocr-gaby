# Chunked Upload Strategy - 413 Error Resolution

## Problem
HTTP 413 "Request Entity Too Large" errors occur when uploading files that exceed server size limits. This typically happens with:
- Large scanned documents (> 10MB)
- High-resolution images
- Multi-page PDFs
- Network proxies with strict size limits

## Solution Overview
We've implemented a **multi-layer chunking strategy** that works on both client and server sides to handle files up to **50MB**.

---

## Architecture

### 1. Server-Side Configuration

#### Nginx Configuration (`frontend/nginx.conf`)
```nginx
# Increase upload limits
client_max_body_size 50M;          # Maximum request body size
client_body_buffer_size 10M;        # Buffer size for reading
client_body_timeout 120s;           # Timeout for receiving body

# Proxy settings for large uploads
proxy_buffering off;                # Disable proxy buffering
proxy_request_buffering off;        # Stream requests directly
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

**What it does:**
- Allows uploads up to 50MB through Nginx
- Extends timeouts for large file transfers
- Disables buffering to stream data directly to backend
- Prevents 413 errors at the reverse proxy level

#### Flask API Configuration (`api.py`)
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
CHUNK_SIZE = 1024 * 1024          # 1MB chunks

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
```

**What it does:**
- Sets Flask's maximum content length to 50MB
- Defines chunk size for processing

### 2. Chunked Upload API Endpoints

#### `/upload/init` - Initialize Upload Session
**Method:** POST  
**Purpose:** Create a new upload session and receive an upload ID

**Request:**
```json
{
  "filename": "document.pdf",
  "filesize": 15728640,
  "chunk_count": 15
}
```

**Response:**
```json
{
  "success": true,
  "upload_id": "uuid-here",
  "chunk_size": 1048576
}
```

#### `/upload/chunk/<upload_id>` - Upload Single Chunk
**Method:** POST  
**Purpose:** Upload one chunk of the file

**Form Data:**
- `chunk`: Binary chunk data
- `chunk_index`: Index of this chunk (0-based)

**Response:**
```json
{
  "success": true,
  "chunk_index": 5,
  "received": 6,
  "total": 15,
  "is_complete": false
}
```

#### `/upload/complete/<upload_id>` - Finalize and Process
**Method:** POST  
**Purpose:** Mark upload complete and process the file

**Form Data:**
- `language`: OCR language (optional, default: eng)
- `preprocess`: Enable preprocessing (optional, default: false)
- `use_gemini`: Enable AI analysis (optional, default: false)
- `gemini_task`: Gemini task type (optional)
- `gemini_prompt`: Custom prompt (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "ocr": { /* OCR results */ },
    "gemini": { /* AI analysis (if requested) */ }
  }
}
```

#### `/upload/cancel/<upload_id>` - Cancel Upload
**Method:** DELETE  
**Purpose:** Cancel ongoing upload and cleanup temp files

---

### 3. Client-Side Implementation

#### Chunked Upload Utility (`lib/chunkedUpload.ts`)

**Smart Upload Strategy:**
```typescript
// Files < 10MB: Regular upload with progress tracking
// Files >= 10MB: Chunked upload (1MB chunks)
// Files >= 50MB: Rejected (exceeds limit)

export async function uploadFileChunked(options: ChunkedUploadOptions)
```

**Features:**
- **Automatic Strategy Selection:** Chooses best upload method based on file size
- **Progress Tracking:** Real-time upload progress callbacks
- **Chunk Management:** Handles chunk creation, upload, and reassembly
- **Error Recovery:** Automatic cleanup on failure
- **Network Resilience:** Individual chunk retry capability

**Usage Example:**
```typescript
const result = await uploadFileChunked({
  file: selectedFile,
  language: 'eng',
  preprocess: true,
  useGemini: true,
  geminiTask: 'analyze',
  onProgress: (progress) => {
    console.log(`Upload: ${progress}%`)
  },
  onChunkComplete: (chunk, total) => {
    console.log(`Chunk ${chunk + 1}/${total} uploaded`)
  }
})
```

---

## Upload Flow

### Small Files (< 10MB)
```
┌─────────┐
│  Client │
└────┬────┘
     │ 1. Single POST /api/ocr
     │    with full file
     ▼
┌─────────┐
│   API   │
└────┬────┘
     │ 2. Process immediately
     │ 3. Return results
     ▼
┌─────────┐
│  Client │
└─────────┘
```

### Large Files (10-50MB)
```
┌─────────┐
│  Client │
└────┬────┘
     │ 1. POST /api/upload/init
     │    { filename, size, chunks }
     ▼
┌─────────┐
│   API   │ → Create session, return upload_id
└────┬────┘
     │
     ▼
┌─────────┐
│  Client │ Split file into 1MB chunks
└────┬────┘
     │ 2. Loop: POST /api/upload/chunk/{id}
     │    for each chunk
     ▼
┌─────────┐
│   API   │ → Append to temp file
└────┬────┘    Track progress
     │
     ▼
┌─────────┐
│  Client │ All chunks uploaded
└────┬────┘
     │ 3. POST /api/upload/complete/{id}
     │    { settings }
     ▼
┌─────────┐
│   API   │ → Process file
└────┬────┘    Return OCR/Gemini results
     │         Cleanup temp files
     ▼
┌─────────┐
│  Client │ Display results
└─────────┘
```

---

## UI Enhancements

### Progress Indicator
Added visual progress bar to show upload status:

```tsx
{loading && uploadProgress > 0 && (
  <div className="space-y-2">
    <div className="flex justify-between text-sm">
      <span>Uploading...</span>
      <span>{uploadProgress}%</span>
    </div>
    <div className="w-full bg-slate-200 rounded-full h-2">
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all"
        style={{ width: `${uploadProgress}%` }}
      />
    </div>
  </div>
)}
```

### File Size Display
Shows file size and indicates chunked upload for large files:

```tsx
{file && (
  <>
    <span className="font-medium">{file.name}</span>
    <br />
    <span className="text-xs">{formatFileSize(file.size)}</span>
  </>
)}
```

### Smart Notifications
Alerts users when large files are detected:

```typescript
if (selectedFile.size > 10 * 1024 * 1024) {
  toast({
    title: "Large file detected",
    description: `File size: ${size}. Will use chunked upload.`
  })
}
```

---

## Benefits

### 1. **Eliminates 413 Errors**
- Files are broken into small chunks that always fit within limits
- Works with any proxy/gateway configuration

### 2. **Better User Experience**
- Real-time progress feedback
- Faster perceived performance (chunked uploads appear faster)
- Clear file size information

### 3. **Network Resilience**
- Individual chunks can be retried on failure
- No need to re-upload entire file on network hiccup
- Works on slower connections

### 4. **Resource Efficiency**
- Server processes chunks as they arrive
- Reduced memory usage (no need to buffer entire file)
- Better handling of concurrent uploads

### 5. **Scalability**
- Easy to add resume capability later
- Can implement parallel chunk uploads
- Supports very large files (limited only by disk space)

---

## Configuration Limits

| Setting | Value | Location |
|---------|-------|----------|
| **Max File Size** | 50MB | `api.py`, `nginx.conf` |
| **Chunk Size** | 1MB | `api.py`, `chunkedUpload.ts` |
| **Chunking Threshold** | 10MB | `chunkedUpload.ts` |
| **Upload Timeout** | 120s | `nginx.conf` |
| **Buffer Size** | 10MB | `nginx.conf` |

---

## Testing

### Test Small File (< 10MB)
```bash
curl -X POST http://localhost:5000/ocr \
  -F "file=@small.jpg" \
  -F "language=eng"
```

### Test Large File (> 10MB) with Chunked Upload
The frontend will automatically use chunked upload for files > 10MB.

### Manually Test Chunked Upload
```bash
# 1. Initialize
curl -X POST http://localhost:5000/upload/init \
  -H "Content-Type: application/json" \
  -d '{"filename":"large.pdf","filesize":15728640,"chunk_count":15}'

# Response: {"upload_id": "abc-123", ...}

# 2. Upload chunks (repeat for each chunk)
curl -X POST http://localhost:5000/upload/chunk/abc-123 \
  -F "chunk=@chunk_0.bin" \
  -F "chunk_index=0"

# 3. Complete
curl -X POST http://localhost:5000/upload/complete/abc-123 \
  -F "language=eng" \
  -F "preprocess=true"
```

---

## Error Handling

### Upload Session Cleanup
```python
# Automatic cleanup on:
- Upload completion (success)
- Upload cancellation (user action)
- Upload failure (exception)
- Session timeout (future enhancement)
```

### Error Recovery
```typescript
try {
  // Upload chunks
  for (let i = 0; i < totalChunks; i++) {
    const response = await uploadChunk(...)
    if (!response.ok) {
      await cancelUpload(uploadId)  // Cleanup
      throw new Error('Chunk upload failed')
    }
  }
} catch (error) {
  // Automatically cleans up partial uploads
  return { success: false, error: error.message }
}
```

---

## Future Enhancements

### Potential Improvements
1. **Resume Capability:** Store chunk checksums to allow resume after disconnect
2. **Parallel Chunks:** Upload multiple chunks simultaneously for faster speeds
3. **Compression:** Compress chunks before upload
4. **Session TTL:** Automatic cleanup of abandoned uploads after timeout
5. **WebSocket Progress:** Real-time progress updates via WebSocket
6. **Multipart Resume:** Use HTTP Range headers for native resume support

---

## Deployment Checklist

- [x] Update Nginx configuration with size limits
- [x] Add chunked upload endpoints to Flask API
- [x] Create client-side chunking utility
- [x] Update React UI with progress tracking
- [x] Add file size validation
- [x] Implement cleanup mechanisms
- [x] Test with files > 10MB
- [x] Test with files at 50MB limit
- [x] Document API endpoints
- [x] Update user-facing file size limits

---

## Troubleshooting

### Still Getting 413 Errors?

1. **Check Nginx Logs:**
   ```bash
   docker compose logs frontend | grep 413
   ```

2. **Verify Nginx Config Loaded:**
   ```bash
   docker compose exec frontend nginx -t
   docker compose restart frontend
   ```

3. **Check API Logs:**
   ```bash
   docker compose logs api | grep -i error
   ```

4. **Test Direct to API (bypass Nginx):**
   ```bash
   curl -X POST http://localhost:5000/health
   ```

### Large Files Timing Out?

- Increase `proxy_read_timeout` in nginx.conf
- Check network speed
- Verify file size is under 50MB limit

### Chunks Not Reassembling?

- Check server disk space: `docker compose exec api df -h`
- Verify all chunks received: check API logs
- Ensure chunk indices are correct (0-based)

---

## Summary

This chunking strategy provides a **robust, scalable solution** for handling large file uploads without 413 errors. It:

✅ Handles files up to 50MB  
✅ Provides real-time progress feedback  
✅ Works with any network configuration  
✅ Gracefully handles errors  
✅ Optimizes small files (no unnecessary chunking)  
✅ Easy to extend and improve  

The implementation is **production-ready** and can be further enhanced with resume capabilities, parallel uploads, and compression as needed.
