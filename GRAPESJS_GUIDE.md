# GrapesJS Visual Template Builder Guide

## Overview

Your email system now features **GrapesJS**, a professional open-source web builder framework that provides a powerful drag-and-drop interface for creating email templates.

## What is GrapesJS?

GrapesJS is an industry-standard, multi-purpose web builder that offers:
- 🎨 **Professional drag-and-drop interface**
- 📱 **Responsive design tools**
- 🎯 **Block-based composition**
- 🎨 **Advanced styling options**
- 📝 **WYSIWYG editing**
- 💾 **Export clean HTML/CSS**

## Features Included

### Newsletter Preset
The system uses the `gjs-preset-newsletter` plugin, specifically optimized for email building with:
- Email-safe table-based layouts
- Pre-configured blocks for common email elements
- Inline CSS export for email compatibility
- Mobile-responsive components

### Available Blocks

**Basic Elements:**
- **Section** - Table-based containers for layout
- **Text** - Editable text blocks with variable support ({{name}}, {{email}})
- **Button** - Call-to-action buttons with customizable links
- **Image** - Responsive images
- **Divider** - Horizontal rules for visual separation
- **Spacer** - Custom vertical spacing

### Advanced Features

1. **Layers Panel** - View and manage element hierarchy
2. **Style Manager** - Customize:
   - Typography (fonts, sizes, colors)
   - Dimensions (width, height, padding, margin)
   - Decorations (backgrounds, borders, shadows)
   - Layout (positioning, display)

3. **Asset Manager** - Manage images and media
4. **Device Preview** - Test responsive behavior

## How to Use

### Creating a Template

1. **Navigate to Templates Tab**
   - Click "Settings" → "Templates"
   - Click "Create Template" button

2. **Choose Visual Builder Mode**
   - Click the **"Visual Builder"** mode button (top right)
   - The GrapesJS editor will initialize

3. **Fill Template Details**
   - Enter **Template Name** (e.g., "Welcome Email")
   - Enter **Email Subject** (e.g., "Welcome to our service")

4. **Build Your Template**
   - Drag blocks from the **left panel** to the canvas
   - Click elements to select them
   - Use the **right panel** to customize styles
   - Double-click text to edit content

5. **Add Variables**
   - Use template variables in text: `{{name}}`, `{{email}}`, etc.
   - These will be replaced when sending emails

6. **Save Template**
   - Click **"Save Template"** button
   - Template is saved with both HTML and plain text versions

### Editing Existing Templates

1. Click **"Edit"** on any template card
2. Switch to **"Visual Builder"** mode
3. The template HTML will load automatically
4. Make changes and click **"Save Template"**

### Switching Modes

You can switch between:
- **Code Editor** - Direct HTML editing for advanced users
- **Visual Builder** - GrapesJS WYSIWYG interface

Changes made in either mode sync to the template on save.

## Tips & Best Practices

### Email Compatibility
✅ **Do:**
- Use table-based layouts (automatically handled by GrapesJS newsletter preset)
- Keep widths under 600px for email clients
- Use inline styles (automatically generated)
- Test with different email clients

❌ **Avoid:**
- Complex CSS (flexbox, grid)
- JavaScript (not supported in emails)
- External stylesheets
- Web fonts (limited support)

### Template Variables
Available variables for personalization:
- `{{name}}` - Recipient's name
- `{{email}}` - Recipient's email
- `{{company}}` - Company name
- Add more in database columns

### Performance
- Keep image sizes reasonable (< 1MB)
- Optimize images before uploading
- Use web-ready formats (JPG, PNG, GIF)

## GrapesJS Keyboard Shortcuts

- **Ctrl/Cmd + Z** - Undo
- **Ctrl/Cmd + Shift + Z** - Redo
- **Delete/Backspace** - Delete selected element
- **Ctrl/Cmd + C** - Copy element
- **Ctrl/Cmd + V** - Paste element
- **Ctrl/Cmd + S** - Save (triggers template save)

## Customization Options

### Style Manager Sectors

1. **General**
   - Element positioning (float, display, position)
   - Coordinates (top, right, bottom, left)

2. **Dimension**
   - Size controls (width, height)
   - Constraints (max-width, min-height)
   - Spacing (margin, padding)

3. **Typography**
   - Font properties (family, size, weight)
   - Text styling (color, alignment, decoration)
   - Readability (line-height, letter-spacing)

4. **Decorations**
   - Backgrounds (colors, images)
   - Borders (style, width, radius)
   - Effects (shadows)

## Troubleshooting

### Visual Builder Not Loading
- Check browser console for errors
- Ensure GrapesJS CDN scripts are accessible
- Try refreshing the page
- Clear browser cache

### Template Not Saving
- Ensure template name and subject are filled
- Check database connection
- View browser console for error messages

### Styles Not Applying
- GrapesJS generates inline styles automatically
- Check if CSS is email-safe (tables, not flexbox)
- Preview in actual email client for final test

## Technical Details

### Libraries Used
- **GrapesJS Core** - v0.21.x+ (from CDN)
- **GrapesJS Newsletter Preset** - Latest (from CDN)

### Integration
- HTML stored in `email_templates.html_body` column
- Plain text auto-generated from HTML
- Inline CSS for email compatibility
- Editor instance managed in `dashboard.js`

### Storage
Templates are saved to database with:
- Generated HTML (with inline styles)
- Plain text version (stripped HTML)
- Template name and subject
- Creation/update timestamps

## Resources

- [GrapesJS Documentation](https://grapesjs.com/docs/)
- [GrapesJS Newsletter Preset](https://github.com/artf/grapesjs-preset-newsletter)
- [Email Design Best Practices](https://www.campaignmonitor.com/resources/guides/email-design/)

## Support

For issues or questions:
1. Check this guide first
2. Review browser console for errors
3. Check database connection
4. Verify CDN scripts are loading

---

**Version:** 1.0  
**Last Updated:** February 2026  
**System:** Email Dashboard with GrapesJS Integration
