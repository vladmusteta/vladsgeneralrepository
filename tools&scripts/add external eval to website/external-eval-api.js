const path = require('path');
const express = require('express');
const cookieParser = require('cookie-parser');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

const FAVORITE_COLOR = "ANSWER1";
const FAVORITE_FRUIT = "ANSWER2";
const MAX_ATTEMPTS = 2;
const TIMEOUT_MINUTES = 10;

function getUserId(req) {
  return req.ip || req.connection.remoteAddress;
}

// Store attempt info per user in memory
const userData = new Map();

// Serve the access required page
app.get('/access-required', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'access_required.html'));
});

// Serve the challenge form
app.get('/challenge', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'challenge.html'));
});

// Handle challenge completion
app.post('/challenge', (req, res) => {
  if (!req.body) {
    return res.status(400).send('Bad request');
  }

  const userId = getUserId(req);
  let data = userData.get(userId) || { attempts: 0, timeoutStart: null, approved: false };
  const answer1 = (req.body.answer1 || "").trim().toLowerCase();
  const answer2 = (req.body.answer2 || "").trim().toLowerCase();
  const returnUrl = req.body.return || 'https://pdf.vladsdomain.live/';
  // Check timeout
  if (data.timeoutStart) {
    const elapsedMinutes = (Date.now() - data.timeoutStart) / 1000 / 60;
    if (elapsedMinutes < TIMEOUT_MINUTES) {
      return res.send(`
        <div style="text-align: center; padding: 50px; font-family: Arial;">
          <h2>Timeout Active</h2>
          <p>Please wait ${Math.ceil(TIMEOUT_MINUTES - elapsedMinutes)} minutes before trying again.</p>
          <a href="/challenge?return=${encodeURIComponent(returnUrl)}">Back</a>
        </div>
      `);
    } else {
      data.attempts = 0;
      data.timeoutStart = null;
    }
  }

  if (answer1 === FAVORITE_COLOR && answer2 === FAVORITE_FRUIT) {
    data.approved = true;
    data.attempts = 0;
    data.timeoutStart = null;
    userData.set(userId, data);

    console.log('User approved - UserID:', userId);

    // Redirect to success endpoint on the protected app
    const successUrl = `https://pdf.vladsdomain.live/challenge/success?return=${encodeURIComponent(returnUrl)}`;
    return res.redirect(successUrl);

  } else {
    data.attempts++;
    if (data.attempts >= MAX_ATTEMPTS) {
      data.timeoutStart = Date.now();
      userData.set(userId, data);
      return res.send(`
        <div style="text-align: center; padding: 50px; font-family: Arial;">
          <h2>Wrong Answer</h2>
          <p>You have reached max attempts. Please wait ${TIMEOUT_MINUTES} minutes before trying again.</p>
          <a href="/challenge?return=${encodeURIComponent(returnUrl)}">Back</a>
        </div>
      `);
    } else {
      userData.set(userId, data);
      return res.send(`
        <div style="text-align: center; padding: 50px; font-family: Arial;">
          <h2>Wrong Answer</h2>
          <p>Try again. Attempts remaining: ${MAX_ATTEMPTS - data.attempts}</p>
          <a href="/challenge?return=${encodeURIComponent(returnUrl)}">Back</a>
        </div>
      `);
    }
  }
});

// API endpoint to check if user is approved (for the PDF app to call)
app.get('/api/check/:userId', (req, res) => {
  const userId = req.params.userId;
  const data = userData.get(userId) || { approved: false };
  res.json({ approved: data.approved });
});

// Keep existing endpoints for compatibility
app.get('/keys', (req, res) => {
  res.json({
    keys: [
      {
        kty: "RSA",
        kid: "dummy",
        use: "sig",
        alg: "RS256",
        n: "00",
        e: "AQAB"
      }
    ]
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Challenge Service listening on port ${PORT}`);
});