# 🔑 How to Get Your OpenAI API Key

## Step-by-Step Instructions (5 minutes)

### 1. Go to OpenAI Platform

Open your web browser and visit:
```
https://platform.openai.com/api-keys
```

### 2. Sign In or Create Account

- **If you have an account:** Click "Log in" and enter your credentials
- **If you're new:** Click "Sign up" and create a free account
  - You can use Google/Microsoft to sign up quickly
  - No credit card required for sign-up!

### 3. Add Payment Method (Required for API usage)

- Click your profile icon (top right)
- Go to "Billing" → "Payment methods"
- Add a credit/debit card
- **Cost:** Very cheap! ~$0.002 per conversation
- **Free credits:** New accounts get $5 free credit

### 4. Create API Key

1. Go back to: https://platform.openai.com/api-keys
2. Click the green **"Create new secret key"** button
3. **Name it:** "Medical AI Agent" (or any name you want)
4. **Important:**
   - Set "Permissions" to "All" (default)
   - Leave "Project" as default
5. Click **"Create secret key"**

### 5. Copy Your Key

- A popup will show your key
- It starts with: `sk-proj-...` or `sk-...`
- **IMPORTANT:** Click "Copy" and save it somewhere safe
- You can only see it once!
- Example key format: `sk-proj-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx`

### 6. Add Key to Your Application

Now paste your key into the `.env` file:

**File location:**
```
/Users/thisalthulnith/medicalagent/backend/.env
```

**Edit line 2:**
```env
# Before:
OPENAI_API_KEY=REPLACE_WITH_YOUR_OPENAI_KEY

# After (paste your actual key):
OPENAI_API_KEY=sk-proj-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
```

**Save the file!**

---

## ✅ You're Done!

Now you can run the application:

```bash
cd /Users/thisalthulnith/medicalagent
./RUN_ME.sh
```

Or open in browser: http://localhost:3000

---

## 💰 Pricing Information

**Cost per usage:**
- Simple conversation: ~$0.001 - $0.002
- Complex medical analysis: ~$0.005 - $0.01
- Image analysis (GPT-4 Vision): ~$0.01 - $0.02

**Example monthly cost:**
- 50 conversations/month: ~$0.50
- 200 conversations/month: ~$2.00

**New users get $5 free credit!** (good for ~500-1000 conversations)

---

## 🔒 Security Tips

✅ **DO:**
- Keep your API key secret
- Don't share it with anyone
- Don't commit it to GitHub

❌ **DON'T:**
- Don't share screenshots with your key visible
- Don't paste it in public forums
- Don't email it to anyone

If you accidentally expose your key:
1. Go to https://platform.openai.com/api-keys
2. Click the trash icon next to that key
3. Create a new one

---

## 🆘 Troubleshooting

### "Invalid API Key" Error
- Make sure you copied the entire key
- Check for extra spaces before/after
- Key should start with `sk-proj-` or `sk-`

### "Insufficient Quota" Error
- Add payment method: https://platform.openai.com/account/billing
- Check your usage: https://platform.openai.com/usage
- Free credits may be expired

### "Rate Limit" Error
- You're making too many requests
- Wait a few seconds and try again
- Upgrade to paid tier for higher limits

---

## 📊 Monitor Your Usage

Check how much you're spending:
```
https://platform.openai.com/usage
```

Set spending limits:
```
https://platform.openai.com/account/limits
```

---

## 🎉 Ready to Run!

Once you've added your API key to `.env`, you can start the application!

See [HOW_TO_RUN.md](HOW_TO_RUN.md) for detailed running instructions.
