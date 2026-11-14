# screwby.in — Production Deployment Package

This folder (`dist/`) is the self-contained, production-ready release of **screwby.in** (guywithyellowscrewdriver).
It contains only the essential static files, styles, interactive motion engine, and media assets.

---

## Folder Structure

```
dist/
├── index.html           # Homepage (Hero stage, axioms, curated builds, contact)
├── build.html           # Dynamic project inspector (routes via ?id=<project>)
├── experiments.html     # Laboratory catalog (All 10 hardware builds with filters)
├── journals.html        # Field documentation archive (All 9 field journals)
├── journal.html         # Individual journal reader & interactive photo lightbox
├── style.css            # Swiss Editorial typography & interactive styles
├── app.js               # Procedural Web Audio, Kalman/particle physics, motion engine
├── server.js            # Standalone zero-dependency Node.js HTTP server
├── package.json         # npm start script configuration
├── vercel.json          # Pre-configured headers & routing for Vercel
├── robots.txt           # SEO crawler permissions
├── sitemap.xml          # Complete XML sitemap
└── assets/              # Optimized media assets
    ├── front.webp       # Hero workbench visual
    ├── projects/        # Photos, teardown schematics & video demos for all 10 builds
    └── journals/        # High-res photo galleries for all 9 field journals
```

---

## How to Deploy

### Option 1: Vercel (Recommended)
1. Install Vercel CLI (or connect GitHub):
   ```bash
   npm i -g vercel
   ```
2. Navigate to this directory and deploy:
   ```bash
   cd dist
   vercel
   ```
*(When prompted for production deployment, run `vercel --prod`)*

---

### Option 2: Netlify
- **Drag & Drop:** Simply drag and drop the `dist/` folder into the Netlify dashboard.
- **Netlify CLI:**
  ```bash
  cd dist
  netlify deploy --prod --dir=.
  ```

---

### Option 3: Cloudflare Pages
1. Go to Cloudflare Dashboard → Workers & Pages → Create Application → Pages.
2. Direct Upload → Upload the `dist/` folder.

---

### Option 4: GitHub Pages
1. Push the contents of `dist/` to the `gh-pages` branch or configure GitHub Pages in Settings to deploy from the `/dist` folder.

---

### Option 5: Any Node / VPS / Docker / PM2
Run with zero dependencies:
```bash
cd dist
node server.js
```
Or with PM2:
```bash
pm2 start server.js --name "screwby-web"
```
