# 🔄 Automatic Sync Guide

You have several options for automatic updates, from simple to advanced:

## 🎯 Option 1: Windows Task Scheduler (Recommended - Simple)

**Best for:** Local automatic syncing on your computer

### Setup:
1. **Run the setup script:**
   ```powershell
   setup-auto-sync.bat
   ```

2. **Choose your frequency:**
   - Every hour
   - Every 6 hours  
   - Daily at 9 AM
   - Daily at 6 PM
   - Custom schedule

### What it does:
- ✅ Automatically runs `node sheet-to-firebase.js` on schedule
- ✅ Updates Firebase when you edit your Google Sheet
- ✅ Works even when your computer is asleep (if it wakes up for tasks)
- ✅ Free and built into Windows

### Manage your schedule:
- **View tasks:** Open Task Scheduler (taskschd.msc)
- **Delete task:** `schtasks /delete /tn "ConfidentPicks-Sync" /f`

---

## 🚀 Option 2: Vercel API with Cron Jobs (Advanced)

**Best for:** Cloud-based automatic syncing that works 24/7

### Setup:
1. **Deploy to Vercel:**
   ```powershell
   cd confident-picks-automation
   vercel --prod
   ```

2. **Set environment variables in Vercel:**
   - `GOOGLE_SHEETS_SPREADSHEET_ID`: Your spreadsheet ID
   - All your Firebase credentials
   - All other environment variables

3. **Cron job is already configured:**
   - Runs every 6 hours automatically
   - Syncs Google Sheets → Firebase
   - Works even when your computer is off

### What it does:
- ✅ Runs in the cloud 24/7
- ✅ Automatically syncs every 6 hours
- ✅ No need to keep your computer on
- ✅ Professional-grade reliability

---

## 💡 Option 3: Manual Trigger (Flexible)

**Best for:** When you want control over when syncs happen

### Setup:
Just run when needed:
```powershell
# Export Firebase → Google Sheets
node fixed-sync.js

# Import Google Sheets → Firebase  
node sheet-to-firebase.js

# Or use the menu
sync-both-ways.bat
```

---

## 🎯 My Recommendation

**Start with Option 1 (Windows Task Scheduler):**

1. **Simple setup** - Just run `setup-auto-sync.bat`
2. **Works locally** - No need to deploy anything
3. **Free** - Built into Windows
4. **Flexible** - Choose your own schedule

**Upgrade to Option 2 (Vercel) later if you need:**
- Cloud-based syncing (works when computer is off)
- More frequent syncing
- Professional reliability

---

## ⚙️ Configuration Options

### Windows Task Scheduler Frequencies:

| Frequency | Command | Description |
|-----------|---------|-------------|
| Every hour | `/sc hourly` | Sync every hour |
| Every 6 hours | `/sc minute /mo 360` | Sync every 6 hours |
| Daily at 9 AM | `/sc daily /st 09:00` | Sync once per day |
| Daily at 6 PM | `/sc daily /st 18:00` | Sync once per day |
| Every 30 minutes | `/sc minute /mo 30` | Sync every 30 minutes |

### Vercel Cron Schedules:

| Schedule | Description |
|----------|-------------|
| `0 */6 * * *` | Every 6 hours |
| `0 * * * *` | Every hour |
| `*/30 * * * *` | Every 30 minutes |
| `0 9 * * *` | Daily at 9 AM |
| `0 18 * * *` | Daily at 6 PM |

---

## 🔧 Troubleshooting

### Windows Task Scheduler Issues:

**Task not running:**
- Check if your computer is awake at the scheduled time
- Verify the task is enabled in Task Scheduler
- Check the task history for errors

**Permission errors:**
- Run the setup script as Administrator
- Make sure the paths are correct

### Vercel Issues:

**Cron job not running:**
- Check Vercel dashboard for function logs
- Verify environment variables are set
- Check if the function is deployed correctly

**API errors:**
- Check Firebase credentials
- Verify Google Sheets API is enabled
- Check sheet sharing permissions

---

## 📊 Monitoring Your Syncs

### Windows Task Scheduler:
- Open Task Scheduler (taskschd.msc)
- Find "ConfidentPicks-Sync" task
- Check "Last Run Time" and "Last Run Result"

### Vercel:
- Go to Vercel dashboard
- Check function logs
- Look for auto-sync function execution logs

### Manual Check:
- Edit your Google Sheet
- Wait for the next scheduled sync
- Check Firebase to see if changes appear

---

## 🎯 Best Practices

### For Google Sheets:
- **Keep ID column** - Don't change the ID values
- **Use consistent formatting** - Keep column headers the same
- **Save changes** - Make sure your edits are saved
- **Test first** - Make a small change and verify it syncs

### For Scheduling:
- **Start simple** - Begin with hourly or daily syncs
- **Monitor first** - Watch a few syncs to make sure they work
- **Adjust frequency** - Increase/decrease based on your needs
- **Have backup** - Keep manual sync option available

---

## 🚀 Quick Start

### Option 1 (Windows Task Scheduler):
```powershell
setup-auto-sync.bat
```
Choose your frequency and you're done!

### Option 2 (Vercel):
```powershell
cd confident-picks-automation
vercel --prod
```
Set environment variables in Vercel dashboard.

---

## ✨ Summary

**You now have automatic syncing options:**

1. **Windows Task Scheduler** - Simple, local, free
2. **Vercel Cron Jobs** - Cloud-based, professional
3. **Manual Triggers** - Flexible, on-demand

**Choose what works best for your workflow!**

---

👉 **Ready to set up automatic syncing?** Start with `setup-auto-sync.bat` for the simplest option!


