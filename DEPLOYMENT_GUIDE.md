# 🚀 UPSC CDS Exam Portal — Deployment Guide

This project is a high-performance, offline-first web portal and CBT examination simulator. All test datasets, PDF question booklets, solutions, and scoring engines are pre-compiled and bundled.

---

## ⚡ 1. Local Server (Currently Live & Running)

The application server is actively running in the background at:
```
http://localhost:8080/index.html
```

To run manually or restart at any time:
```bash
# Option A: Dedicated Python Server (with CORS & MIME types)
python server.py

# Option B: NPM start script
npm start

# Option C: Standard Node HTTP Server
npx serve -s . -l 8080
```

---

## 🌐 2. One-Click Cloud Deployment Options

### Option A: Vercel (Recommended)
1. Push your repository to GitHub / GitLab / Bitbucket.
2. Go to [vercel.com](https://vercel.com) and import the repository.
3. The included `vercel.json` will automatically configure routing and headers.
4. Click **Deploy** — your portal is live with global CDN acceleration and HTTPS.

### Option B: Netlify
1. Go to [netlify.com](https://netlify.com) and connect your repository.
2. The included `netlify.toml` automatically configures static publishing and PDF inline viewing.
3. Click **Deploy Site**.

### Option C: GitHub Pages (Free Automatic CI/CD)
1. Push the code to GitHub.
2. The included `.github/workflows/deploy.yml` workflow will automatically trigger on push to `main`/`master`.
3. In GitHub Settings > Pages, set Source to **GitHub Actions**.
4. Your site will be published at `https://<username>.github.io/<repo-name>/`.

### Option D: Docker / Cloud Run / VPS
A production-ready `Dockerfile` (Nginx Alpine) is included:
```bash
# Build the Docker image
docker build -t upsc-cds-portal .

# Run the container on port 80
docker run -d -p 80:80 upsc-cds-portal
```

---

## 📑 3. Bundled PDFs & Assets Verification

Every question paper, companion answer key, and OMR sheet referenced on the portal is compiled and verified:

| PDF Document | Status | Size | Purpose |
|---|---|---|---|
| `UPSC_CDS_English_All_Questions_Paper.pdf` | ✅ Ready | ~220 KB | English Complete Archive Booklet (960 Qs) |
| `UPSC_CDS_Math_All_Questions_Paper.pdf` | ✅ Ready | ~195 KB | Mathematics Complete Archive Booklet (800 Qs) |
| `UPSC_CDS_GS_All_Questions_Paper.pdf` | ✅ Ready | ~215 KB | GS Complete Archive Booklet (960 Qs) |
| `UPSC_CDS_GS_All_Questions_Answer_Key.pdf` | ✅ Ready | ~85 KB | GS Companion Solutions & Key (960 Qs) |
| `UPSC_CDS_Official_OMR_Sheet.pdf` | ✅ Ready | ~42 KB | Machine-Gradable Bubble Sheet (120 Items) |
| `UPSC_CDS_Paper_I_English_Real_Test_Paper.pdf` | ✅ Ready | ~75 KB | 120-Q Mock Test Booklet |
| `UPSC_CDS_Paper_II_General_Knowledge_Real_Test_Paper.pdf`| ✅ Ready | ~80 KB | 120-Q GS Mock Test Booklet |
| `UPSC_CDS_Paper_III_Elementary_Mathematics_Real_Test_Paper.pdf` | ✅ Ready | ~70 KB | 100-Q Math Mock Test Booklet |
| `UPSC_CDS_Official_Answer_Keys_and_Solutions.pdf` | ✅ Ready | ~60 KB | Master Solutions & Keys (Papers I–III) |

To recompile all PDFs at any time:
```bash
npm run build:pdfs
```
