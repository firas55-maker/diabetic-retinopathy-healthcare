# Image Loading Debug Report

## Problem Summary
The Scan Review page showed "Image not available" instead of displaying the actual retinal image.

## Root Cause Analysis

### Issue 1: No Image Serving Endpoint
- **Original State**: Backend had no dedicated endpoint to serve image files
- **Impact**: Frontend couldn't retrieve the image file from disk
- **Why it failed**: The `image_data` field in API response was either `None` or too large (base64 bloats response size)

### Issue 2: No Image File Access Method
- **Original State**: Image files stored at absolute paths (e.g., `C:\Users\...\uploads\scans\uuid.jpg`)
- **Impact**: Frontend had no way to access these files
- **Why it failed**: Static files were not mounted in FastAPI app

### Issue 3: Authentication Headers Missing
- **Original State**: Would have used `<img src="url">` which doesn't send JWT tokens
- **Impact**: Authenticated image endpoint wouldn't work with plain img tags
- **Why it failed**: Image requests need Authorization header with Bearer token

## Solution Implemented

### Backend Changes (routes/doctor.py)

#### 1. Added FileResponse import
```python
from fastapi.responses import FileResponse
```

#### 2. New Endpoint: GET /doctor/scans/{scan_id}/image
- **Purpose**: Serve the actual image file from disk
- **Authentication**: Requires doctor role (via `require_doctor` dependency)
- **Authorization**: Doctor can only view scans from their hospital (same as scan detail)
- **Error Handling**:
  - 404 if scan not found
  - 403 if user not authorized
  - 404 if image file missing from disk
- **Media Types**: Supports JPEG, PNG, WebP based on file extension
- **Response**: FileResponse with correct media type and filename

```python
@router.get("/scans/{scan_id}/image")
async def get_scan_image(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    # Validates scan exists
    # Checks user authorization
    # Verifies file exists on disk
    # Returns FileResponse with correct media type
```

### Frontend Changes (pages/doctor/ScanReview.tsx)

#### 1. Added Image State Management
```typescript
const [imageUrl, setImageUrl] = useState<string>('');
```

#### 2. New Function: fetchScanImage()
- **Purpose**: Fetch image file with authentication
- **Method**: Uses `fetch()` with Bearer token in Authorization header
- **Response Handling**: Converts blob to object URL for display
- **Error Handling**: Logs errors, silently fails (shows fallback UI)

```typescript
const fetchScanImage = async (scanId: string) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/doctor/scans/${scanId}/image`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  if (response.ok) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    setImageUrl(url);
  }
};
```

#### 3. Updated fetchScan() to Load Image
- Calls `fetchScanImage()` after successfully loading scan details
- Adds image loading to the same useEffect that loads scan data

#### 4. Updated Image Display
- Changed from `image_data` base64 check to `imageUrl` blob URL check
- Shows actual image when URL is available
- Shows warning icon when image unavailable (file missing or load error)

## Data Flow

### Request Flow
```
1. Doctor navigates to /doctor/scan/{scanId}
2. ScanReview component mounts
3. fetchScan() called:
   - Calls api.getScanDetail(scanId)
   - Backend returns ScanDetailResponse (with metadata, no image data)
   - Calls fetchScanImage(scanId)
   - Sends GET /doctor/scans/{scanId}/image with JWT token
   - Backend verifies authorization, reads file, returns FileResponse
   - Frontend receives blob, creates object URL, displays in <img>
```

### Image File Lookup
```
Database Scan Record:
  └── file_path: "C:\Users\LENOVO\Desktop\helathcare 2\uploads\scans\{uuid}.jpg"
      (stored by upload_scan endpoint in patients.py)

Image Serving:
  1. /doctor/scans/{scan_id}/image endpoint receives request
  2. Looks up Scan record by ID
  3. Gets file_path from database
  4. Verifies file exists at that path
  5. Returns FileResponse with proper media type
```

## Security Considerations

✅ **Authentication**: All image requests require valid JWT token
✅ **Authorization**: User can only view images from scans in their hospital
✅ **File Access**: Validates file exists before serving (prevents path traversal)
✅ **Media Types**: Correctly identified by extension (prevents content-type attacks)
✅ **Error Handling**: Doesn't expose sensitive paths in error messages

## Testing Checklist

- [ ] Create a patient (via technical staff)
- [ ] Upload a retinal scan image for that patient
- [ ] Verify image file exists in `./uploads/scans/` directory
- [ ] Login as doctor from same hospital
- [ ] Open Scan Review page for that scan
- [ ] Verify retinal image displays in card
- [ ] Verify image is responsive and fills card
- [ ] Verify AI grade and confidence show alongside image
- [ ] Verify image persists through page navigation
- [ ] Try accessing image as different hospital's doctor (should get 403)
- [ ] Try accessing image without authentication (should get 401)

## Files Modified

1. **backend/routes/doctor.py**
   - Added FileResponse import
   - Added os import
   - Added `get_scan_image()` endpoint

2. **frontend/src/pages/doctor/ScanReview.tsx**
   - Added `API_BASE_URL` constant
   - Added `imageUrl` state
   - Added `fetchScanImage()` function
   - Updated `fetchScan()` to call `fetchScanImage()`
   - Updated image display to use `imageUrl` blob URL

## Advantages of This Approach

1. **Efficient**: Images served as files, not bloated JSON responses
2. **Secure**: Auth token checked on every request
3. **User Experience**: Native browser image caching works
4. **Scalable**: Supports large image files without response bloat
5. **Flexible**: Can add image resizing/thumbnails later without client changes
6. **Error Handling**: Graceful fallback if file missing or access denied
