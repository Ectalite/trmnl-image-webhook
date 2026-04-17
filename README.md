# TRMNL Image Webhook

Automatically upload images from your photo collection to your TRMNL e-ink display with proper dithering and color support.
## Example output
![beach-2bit-dither-800x480.png](example_images/beach-2bit-dither-800x480.png) 

## Features

- 📸 **Automatic Image Processing** - Scales and converts photos to e-ink format
- 🎨 **Floyd-Steinberg Dithering** - Professional halftone effect for smooth gradients
- 🖼️ **2-bit Grayscale** - 4 shades of gray for better quality than pure black & white
- ✨ **Gamma Correction** - Brightens midtones for better e-ink visibility
- 🖼️ **Frame Borders** - Optional decorative borders (line or rounded corners)
- 🎨 **Color Output Mode** - Full RGB for color e-ink displays (auto-selected for 24-bit devices)
- 🔴 **BWRY Output Mode** - 4-color palette (black/white/red/yellow) for BWRY e-ink displays (auto-selected for `og_bwry`, `waveshare_7_5_bwry`, etc.)
- 🎲 **Multiple Selection Modes** - Random, sequential, shuffle, newest, or oldest
- 🔄 **Auto-Rotation** - Respects EXIF orientation data
- 🖼️ **Flexible Layouts** - Auto, landscape, or portrait modes
- 🎯 **Orientation Filtering** - Show only landscape or portrait photos (with smart caching)
- 🎨 **Border Styles** - White, black, or blurred borders
- 📏 **Adjustable Margins** - Add spacing around images for framed picture look
- 📁 **Subfolder Support** - Organize photos in folders and subfolders
- 🏷️ **Optional Labels** - Show filename or path on images
- 🐳 **Docker Ready** - Easy deployment with docker-compose
- 💾 **State Management** - Remembers position for sequential/shuffle modes
- 🔍 **Debug Mode** - Saves processed images for inspection
- 🧪 **Dry Run** - Test without uploading
- 🔔 **Version Checking** - Notifies when updates are available

## Quick Start

### 1. Get Your Webhook URL

1. Log into [TRMNL](https://trmnl.com)
2. Go to Plugins > Webhook Image
3. Click "Add to my plugins"
4. Copy your webhook URL

### 2. Set Up Configuration

```bash
# Clone or download this repository
cd trmnl-image-webhook

# Copy example config
cp .env.example .env

# Edit with your settings
nano .env
```

Minimum required config:
```bash
WEBHOOK_URL=https://trmnl.com/api/plugin_settings/YOUR-UUID/image
IMAGES_PATH=/path/to/your/photos
```

### 3. Run with Docker

```bash
docker-compose up -d
```

That's it! Your TRMNL will start showing photos from your collection.

## Configuration

### Required Settings

| Variable | Description | Example                           |
|----------|-------------|-----------------------------------|
| `WEBHOOK_URL` | Your TRMNL webhook URL | `https://trmnl.com/api/...`       |
| `IMAGES_PATH` | Path to your photos | `./images` or `/home/user/Photos` |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVICE_MODEL` | _(none)_ | Auto-configure from TRMNL API: `og_png`, `v2`, `amazon_kindle_2024`, etc. Sets width, height, and bit depth automatically |
| `LAYOUT` | `auto` | Orientation: auto/landscape/portrait |
| `ORIENTATION_FILTER` | `any` | Filter images: any/landscape/portrait |
| `BORDER_STYLE` | `white` | Border style: white/black/blur |
| `MARGIN` | `0` | Margin in pixels (0-100) for framed look |
| `GAMMA` | `1.5` | Gamma correction (1.0-2.0, brightens midtones for e-ink) |
| `FRAME_BORDER` | `none` | Frame border: none/line/rounded (only with MARGIN > 0) |
| `FRAME_BORDER_WIDTH` | `2` | Frame border width in pixels (1-10) |
| `OUTPUT_MODE` | _(auto)_ | Output mode: `grayscale`, `color` (24-bit devices), or `bwry` (BWRY devices). Auto-selected when `DEVICE_MODEL` is set |
| `INTERVAL_MINUTES` | `60` | Minutes between uploads |
| `SELECTION_MODE` | `random` | How to pick images (see below) |
| `INCLUDE_SUBFOLDERS` | `true` | Include images from subdirectories |
| `USE_DITHERING` | `true` | Apply Floyd-Steinberg dithering |
| `IMAGE_LABEL` | `none` | Show label (none/filename/path) |
| `DRY_RUN` | `false` | Test mode - don't upload |

### Selection Modes

- **random** - Pick any image randomly
- **sequential** - Go through images A-Z, remembers position
- **shuffle** - Random order, each image once before reshuffling
- **newest** - Always show most recently modified image
- **oldest** - Show oldest image first

### Image Labels

Add text overlay to images:

- **none** - No label (default)
- **filename** - Show just the filename
- **path** - Show relative path from images directory

Example with label:
```bash
IMAGE_LABEL=path
```

### Gamma Correction

Brightens midtones for better e-ink visibility. E-ink displays tend to look darker than regular screens, so gamma correction helps.

```bash
GAMMA=1.5  # Recommended for e-ink (default)
GAMMA=1.0  # No correction (original brightness)
GAMMA=1.8  # More aggressive brightening
```

### Frame Borders

Add decorative borders around images for a framed picture look. Requires `MARGIN > 0`.

```bash
MARGIN=40              # Space around image
FRAME_BORDER=line      # Style: none/line/rounded
FRAME_BORDER_WIDTH=3   # Border thickness (1-10 pixels)
BORDER_STYLE=white     # Background: white/black
```

**Examples:**
- **Gallery style**: `MARGIN=60`, `FRAME_BORDER=line`, `BORDER_STYLE=black`
- **Modern**: `MARGIN=30`, `FRAME_BORDER=rounded`, `BORDER_STYLE=white`
- **Classic**: `MARGIN=50`, `FRAME_BORDER=line`, `FRAME_BORDER_WIDTH=5`

### Output Modes

When `DEVICE_MODEL` is set, the output mode is chosen automatically. You can override with `OUTPUT_MODE`.

**grayscale** (default) — Floyd-Steinberg dithered grayscale. Best for standard TRMNL e-ink displays.

**color** — Full RGB, no dithering. Auto-selected for 24-bit devices (tidbyt, openframe, raspberry_pi_touch_2). Produces larger files (~200-500KB).

```bash
OUTPUT_MODE=color
```

**bwry** — 4-color palette: black, white, red, yellow. Floyd-Steinberg dithered in RGB space. Auto-selected for BWRY devices (`og_bwry`, `waveshare_7_5_bwry`).

```bash
OUTPUT_MODE=bwry
```

### Image Fit Modes

Control how images are scaled to the display:

**Contain (default):**
```bash
IMAGE_FIT=contain
```
- Fits entire image on screen
- Maintains aspect ratio
- May show borders if image ratio doesn't match display
- Best for preserving full image

**Fill:**
```bash
IMAGE_FIT=fill
```
- Fills entire display
- Maintains aspect ratio
- May crop edges of image
- Best for edge-to-edge display, no borders
- Great for wallpaper-style images

**Example - Full Screen Photos:**
```bash
IMAGE_FIT=fill
MARGIN=0
BORDER_STYLE=white
```

## Image Processing

### What Happens to Your Photos

1. **Scaling** - Resized to fit display (800x480 or 1280x800)
2. **Grayscale** - Converted to grayscale
3. **Dithering** - Floyd-Steinberg dithering applied for smooth gradients
4. **1-bit Conversion** - Pure black and white (2 colors)
5. **PNG Export** - Optimized 1-bit PNG (~20-40KB)

### Why Dithering?

TRMNL displays are 1-bit (pure black and white). Dithering creates the illusion of grayscale by using patterns of black and white dots - like newspaper photos. This makes photos look much better than simple thresholding.

**With dithering:**
- Smooth gradients in sky, skin tones, etc.
- Details visible in shadows and highlights
- Professional halftone appearance

**Without dithering:**
- Harsh black/white contrast
- Loss of detail
- Posterized look

## Examples

### Basic Setup

```bash
# .env
WEBHOOK_URL=https://trmnl.com/api/plugin_settings/abc-123/image
IMAGES_PATH=/home/user/Photos
INTERVAL_MINUTES=60
SELECTION_MODE=random
INCLUDE_SUBFOLDERS=true
USE_DITHERING=true
```

### Photo Album (Sequential)

```bash
SELECTION_MODE=sequential
INTERVAL_MINUTES=120
IMAGE_LABEL=filename
```

### Slideshow (Shuffle)

```bash
SELECTION_MODE=shuffle
INTERVAL_MINUTES=30
INCLUDE_SUBFOLDERS=true
```

### Latest Photo Display

```bash
SELECTION_MODE=newest
INTERVAL_MINUTES=15
IMAGE_LABEL=path
```

### Framed Picture Gallery

```bash
MARGIN=40
BORDER_STYLE=white
FRAME_BORDER=line
FRAME_BORDER_WIDTH=3
GAMMA=1.5
```

### Classic Black Frame

```bash
MARGIN=60
BORDER_STYLE=black
FRAME_BORDER=rounded
FRAME_BORDER_WIDTH=2
```

### Color Display (Pimoroni Inky / openframe)

```bash
DEVICE_MODEL=openframe   # auto-selects OUTPUT_MODE=color
GAMMA=1.0
WEBHOOK_URL=http://192.168.1.x:5000/display
```

### BWRY Display (TRMNL OG BWRY / Waveshare)

```bash
DEVICE_MODEL=og_bwry     # auto-selects OUTPUT_MODE=bwry
GAMMA=1.2
```

## Deployment

### Docker Compose (Recommended)

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f  trmnl-image-webhook

# Stop
docker-compose down

# Restart after config changes
docker-compose restart
```

### Synology NAS

1. Enable Docker in Package Center
2. Upload project folder to your NAS
3. Edit `.env` with your settings
4. SSH into NAS:
```bash
cd /volume1/docker/trmnl-image-webhook
docker-compose up -d
```

### Raspberry Pi

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone and configure
git clone <repo-url>
cd trmnl-image-webhook
cp .env.example .env
nano .env

# Run
docker-compose up -d
```

## Debugging

### Check Logs

```bash
docker-compose logs -f
```

Look for:
```
Found X images
Converting to grayscale
Converting to 1-bit with Floyd-Steinberg dithering  
Final: 800x480 1-bit PNG, 25.3KB
✓ Successfully uploaded image.jpg
Response: 200
```

### Inspect Processed Images

Every upload saves two files to `./data/`:

- `last_original.jpg` - Original unprocessed photo
- `last_processed.png` - Final 1-bit dithered PNG sent to TRMNL

Compare these to see exactly what's being displayed.

### Dry Run Mode

Test without uploading:

```bash
DRY_RUN=true
docker-compose restart
```

### Common Issues

**No images found**

- Check `IMAGES_PATH` is correct
- Set `INCLUDE_SUBFOLDERS=true` if images are in subdirectories
- Verify image formats (PNG, JPG, JPEG, BMP, GIF supported)

**Images not displaying on TRMNL**

- Check device WiFi connection
- Verify webhook URL is correct
- Try "Force Refresh" in TRMNL plugin settings
- Check `data/last_processed.png` looks correct

**Rate limited (429 error)**

- TRMNL allows max 12 uploads per hour
- Increase `INTERVAL_MINUTES` to 60 or higher
- 
## Technical Details

### Supported Image Formats

Input: PNG, JPEG, JPG, BMP, GIF  
Output: 1-bit or 2-bit grayscale PNG (default: 2-bit)

### Bit Depth Options

**2-bit (Default - Recommended):**
- 4 shades of gray (0, 85, 170, 255)
- Smoother gradients and better photo quality
- Smaller file sizes (~5-10KB)
- Supported on TRMNL OG firmware v1.7.2+

**1-bit (Classic):**
- Pure black and white (2 colors)
- Sharper, higher contrast
- Slightly larger files (~15-30KB)
- Maximum compatibility

Both modes use Floyd-Steinberg dithering for professional halftone effects.

### File Sizes

- Input: Any size (auto-scaled)
- Output: ~15-40KB (1-bit PNG)
- Limit: 5MB (rarely reached)

### Device Models

Set `DEVICE_MODEL` to auto-configure display dimensions, bit depth, and output mode. 41 devices supported — run `python generate_examples.py` to render a sample image for every model.

Common models:

| Model | Size | Output |
|-------|------|--------|
| `og_png` | 800×480 | grayscale 1-bit |
| `og_plus` | 800×480 | grayscale 2-bit |
| `og_bwry` | 800×480 | bwry (auto) |
| `v2` | 1872×1404 | grayscale 4-bit |
| `openframe` | 800×480 | color (auto) |
| `tidbyt` | 64×32 | color (auto) |

### State Management

For `sequential` and `shuffle` modes, position is saved in `./data/state.json`:

```json
{
  "last_image": "vacation/photo.jpg",
  "current_index": 42,
  "last_upload": "2024-12-31T16:20:57"
}
```

## Performance

- **Memory**: ~50MB
- **CPU**: Minimal (only during processing)
- **Network**: ~20-40KB per upload
- **Storage**: State file <1KB

## Requirements

- Docker & Docker Compose
- Network access to TRMNL API
- Directory of images (local or mounted)

## License

MIT License - see LICENSE file

## Contributing

Issues and pull requests welcome!

## Support

For issues with:
- **This tool**: Open a GitHub issue
- **TRMNL device/service**: Contact TRMNL support
- **Docker/deployment**: Check Docker logs first

## Credits

Developed for the TRMNL community. Inspired by TRMNL's own image processing code.