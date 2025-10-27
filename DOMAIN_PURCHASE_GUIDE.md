# 🌐 Domain Purchase Guide

## 🎯 **Task 2: Purchase Domain (15 minutes)**

---

## 📝 **Domain Name Suggestions**

### **Available Options (Check availability):**
1. `confidentpicks.com` ⭐ **Best choice**
2. `confident-picks.com`
3. `theconfidentpicks.com`
4. `confidentpick.com`
5. `confidentpicks.io`
6. `confidentpicks.app`

### **Naming Considerations:**
- ✅ Short and memorable
- ✅ Easy to spell
- ✅ Matches your brand
- ✅ `.com` preferred (most trusted)
- ❌ Avoid hyphens if possible
- ❌ Avoid numbers

---

## 💰 **Recommended Registrars**

### **Option 1: Namecheap (Recommended)**
**Why:** Cheap, reliable, good UI  
**Cost:** ~$12/year for `.com`  
**Link:** https://www.namecheap.com

**Steps:**
1. Go to Namecheap.com
2. Search for your domain
3. Add to cart
4. Create account
5. Purchase (use coupon code if available)
6. **IMPORTANT:** Enable "WhoisGuard" (free privacy protection)

---

### **Option 2: Google Domains**
**Why:** Simple, integrates with Google services  
**Cost:** ~$12/year for `.com`  
**Link:** https://domains.google.com

**Steps:**
1. Go to domains.google.com
2. Search for domain
3. Add to cart
4. Purchase with Google account
5. Privacy protection included free

---

### **Option 3: Cloudflare**
**Why:** Cheapest, includes free CDN  
**Cost:** ~$10/year for `.com` (at-cost pricing)  
**Link:** https://www.cloudflare.com/products/registrar/

**Steps:**
1. Create Cloudflare account
2. Add your domain
3. Transfer or register domain
4. Free privacy protection
5. Free CDN and DDoS protection

---

## ⚙️ **Initial DNS Configuration**

### **After Purchase (Do Later):**

You'll need to configure DNS when you set up hosting. For now, just:

1. ✅ Purchase the domain
2. ✅ Enable privacy protection
3. ⏸️ **Wait** - We'll configure DNS when we set up Firebase Hosting (Task 5)

### **DNS Records You'll Need Later:**

```
Type    Name    Value                           TTL
A       @       [Firebase Hosting IP]           Auto
A       www     [Firebase Hosting IP]           Auto
CNAME   www     [your-project].web.app          Auto
TXT     @       [Email verification]            Auto
```

**Don't worry about this now!** We'll do it when we set up hosting.

---

## 📧 **Email Configuration (Do Later)**

Once you have a domain, you can set up:
- Professional email: `support@confidentpicks.com`
- Email for SendGrid/AWS SES
- SPF/DKIM records for email deliverability

**We'll do this in Task 6 (Email System)**

---

## ✅ **Completion Checklist**

- [ ] Domain purchased
- [ ] Privacy protection enabled
- [ ] Domain registered to your account
- [ ] Confirmation email received
- [ ] Domain shows in your registrar dashboard

---

## 🎉 **Once Complete:**

**You now have:**
- ✅ Your own domain name
- ✅ Privacy protection
- ✅ Ready for hosting setup

**Next Step:** Move to Task 3 (NBA Data Collection)

---

**Estimated Time:** 15 minutes  
**Cost:** ~$12/year  
**Status:** Ready to purchase!

