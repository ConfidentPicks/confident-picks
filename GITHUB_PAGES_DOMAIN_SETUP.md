# 🌐 Connect confident-picks.com to GitHub Pages

## Current Status
- ✅ GitHub Repository: `https://github.com/ConfidentPicks/confident-picks`
- ✅ Latest code pushed to `master` branch
- ✅ Domain owned: `confident-picks.com`
- ⏳ Need to connect domain to GitHub Pages

---

## Step 1: Add CNAME File to Repository

I'll create a `CNAME` file with your domain name. This tells GitHub Pages what custom domain to use.

**File:** `CNAME`
**Content:** `confident-picks.com`

---

## Step 2: Configure GitHub Pages Settings

1. Go to: https://github.com/ConfidentPicks/confident-picks/settings/pages
2. Under "Source", select:
   - Branch: `master`
   - Folder: `/ (root)`
3. Click "Save"
4. Under "Custom domain", enter: `confident-picks.com`
5. Click "Save"
6. Wait for DNS check (may take a few minutes)
7. Once verified, check "Enforce HTTPS"

---

## Step 3: Configure DNS at Your Domain Registrar

You need to add DNS records at wherever you bought `confident-picks.com` (GoDaddy, Namecheap, etc.)

### **Option A: Use Apex Domain (confident-picks.com)**

Add these **A records**:
```
Type: A
Name: @
Value: 185.199.108.153

Type: A
Name: @
Value: 185.199.109.153

Type: A
Name: @
Value: 185.199.110.153

Type: A
Name: @
Value: 185.199.111.153
```

### **Option B: Use www Subdomain (www.confident-picks.com)**

Add this **CNAME record**:
```
Type: CNAME
Name: www
Value: confidentpicks.github.io
```

### **Recommended: Do BOTH**

1. Add all 4 A records (for apex domain)
2. Add CNAME record (for www subdomain)
3. This way both `confident-picks.com` AND `www.confident-picks.com` work!

---

## Step 4: Wait for DNS Propagation

- DNS changes take 15 minutes to 48 hours
- Usually works within 1-2 hours
- Check status: https://www.whatsmydns.net

---

## Step 5: Verify It Works

After DNS propagates:
1. Visit: `https://confident-picks.com`
2. Should see your app!
3. SSL certificate automatically provided by GitHub

---

## Where Did You Buy the Domain?

Let me know your registrar and I can give you specific instructions:
- **GoDaddy**
- **Namecheap**
- **Google Domains**
- **Cloudflare**
- **Other?**

---

## Current GitHub Pages URL

Your site is currently live at:
**https://confidentpicks.github.io/confident-picks/**

Test it to make sure everything works before connecting the custom domain!

---

## Next Steps

1. ✅ I'll create the CNAME file
2. ✅ I'll push it to GitHub
3. ⏳ You configure GitHub Pages settings (link above)
4. ⏳ You add DNS records at your registrar
5. ⏳ Wait for DNS propagation
6. ✅ Site live at confident-picks.com!

**Ready to proceed?** Let me know and I'll create the CNAME file!

