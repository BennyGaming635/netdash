# NetDash UI Overview

This document describes the user interface and visual design of NetDash.

## Color Scheme

The dashboard uses a modern dark theme inspired by UniFi:

- **Background**: Deep slate (`#0f172a`)
- **Cards**: Dark slate (`#1e293b`)
- **Primary**: Sky blue (`#0ea5e9`)
- **Success/Online**: Green (`#10b981`)
- **Warning**: Amber (`#f59e0b`)
- **Danger/Offline**: Red (`#ef4444`)
- **Text**: Light slate (`#f8fafc`)

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  NetDash  🟢 Connected    [ Devices ] [ Topology ] ...      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Connected Devices                                           │
│  3 of 3 devices online                                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 🔀 Main      │  │ 📡 Access    │  │ 🔌 Switch 1  │     │
│  │    Router    │  │    Point 1   │  │              │     │
│  │ 🟢 online    │  │ 🟢 online    │  │ 🟢 online    │     │
│  │              │  │              │  │              │     │
│  │ IP: 192...   │  │ IP: 192...   │  │ IP: 192...   │     │
│  │ MAC: 00:11   │  │ MAC: AA:BB   │  │ MAC: 11:22   │     │
│  │ Uptime: 99%  │  │ Uptime: 98%  │  │ Uptime: 99%  │     │
│  │ ████████████ │  │ ███████████  │  │ ████████████ │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Views

### 1. Devices View (Default)

**Header Section:**
- Title: "Connected Devices"
- Status summary: "X of Y devices online"

**Device Cards Grid:**
- Responsive 3-column layout (desktop)
- 2-column on tablet, 1-column on mobile
- Each card shows:
  - Device icon (emoji): 🔀 router, 📡 AP, 🔌 switch
  - Device name and type
  - Status indicator (colored dot + text)
  - IP address (monospace font)
  - MAC address (monospace font)
  - Uptime percentage (bold)
  - Last seen timestamp
  - Progress bar (color-coded by uptime)

**Card Styling:**
- Dark slate background with border
- Hover effect: border changes to primary blue
- Smooth transitions
- Rounded corners
- Shadow for depth

### 2. Topology View

**Network Graph:**
- Full-width canvas (600px height)
- Dark background matching theme
- Interactive controls:
  - Drag nodes to reposition
  - Pan by dragging background
  - Zoom with scroll wheel

**Node Styling:**
- Size: 60x60 pixels
- Router: Diamond shape ◆
- Access Point: Triangle shape ▲
- Switch: Rectangle shape ▢
- Online: Green fill
- Offline: Red fill
- Labels below nodes
- Selection highlight: Blue border

**Edges (Connections):**
- Gray color matching theme
- Arrows pointing to connection direction
- Bezier curves for smooth appearance
- 3px width

**Legend:**
- Bottom center alignment
- Color-coded status indicators
- Shape reference for device types
- Clean, minimal design

**Controls:**
- "Refresh" button (top right)
- Blue primary button
- Hover state

### 3. Uptime View

**Bar Chart:**
- Chart.js powered visualization
- 400px height
- Dark theme matching dashboard
- Color-coded bars:
  - Green: 99%+ uptime
  - Yellow: 95-99% uptime
  - Red: Below 95% uptime
- Y-axis: 0-100% with grid lines
- X-axis: Device names
- Tooltips on hover showing exact percentage

**Statistics Cards:**
- 3-column grid below chart
- Each card shows:
  - Label in gray text
  - Large number in white/colored text
  - Semi-transparent dark background
- Metrics:
  - Average Uptime (white text)
  - Devices Online (green text)
  - Devices Offline (red text)

### 4. Alerts View

**Alert List:**
- Vertical stack of alert cards
- Each alert card contains:
  - Severity icon (emoji): ❌ error, ⚠️ warning, ℹ️ info
  - Colored left border (4px) matching severity
  - Severity badge (top left)
  - Timestamp (gray text)
  - Alert message (large white text)
  - Device ID if applicable
  - Dismiss button (X icon, top right)

**Alert Card Colors:**
- Error: Red border and badge, red tinted background
- Warning: Yellow border and badge, yellow tinted background
- Info: Blue border and badge, blue tinted background

**Empty State:**
- Centered message when no alerts
- "No alerts at this time"
- "All systems operational"
- Large text with icons

## Navigation

**Top Header:**
- Left side:
  - "NetDash" logo/title
  - Connection status indicator
  - Status text ("Connected" / "Disconnected")
- Right side:
  - Tab buttons for each view
  - Active tab highlighted in blue
  - Inactive tabs in gray with hover state
  - Alert count badge (red) on Alerts tab when applicable

**Responsive Behavior:**
- Desktop: Full horizontal layout
- Tablet: Adjusted grid columns
- Mobile: Stacked single column
- Navigation remains accessible on all sizes

## Animation and Transitions

- Smooth color transitions (200ms)
- Fade-in for new alerts
- Pulse effect for connection status
- Smooth chart rendering
- Graph layout animation (1.5s)
- Hover effects on interactive elements

## Typography

- **Headers**: 2xl, bold, white
- **Subheaders**: xl, semibold, white
- **Body text**: Base size, normal weight, light slate
- **Labels**: Small size, slate-400
- **Monospace**: For IP/MAC addresses
- **Font family**: System fonts for native appearance

## Accessibility

- High contrast colors
- Clear status indicators
- Keyboard navigation support
- Screen reader friendly labels
- Focus indicators on interactive elements

## Real-time Updates

Visual feedback for real-time changes:
- Status indicators update instantly
- New alerts fade in at the top
- Uptime bars animate when updated
- Topology nodes change color on status change
- No page refresh needed

## Performance

- Optimized renders with React hooks
- Memoized calculations
- Efficient WebSocket updates
- Smooth 60fps animations
- Fast initial load with Vite

---

This UI design provides a professional, modern, and intuitive interface for network monitoring that matches the UniFi aesthetic while being fully functional and user-friendly.
