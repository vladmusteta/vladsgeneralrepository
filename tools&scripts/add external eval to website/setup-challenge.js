// setup-challenge.js - Interactive script that reads ALL current values from files
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let config = {};
let currentValues = {};

function readCurrentConfig() {
  console.log('📖 Reading current configuration from your files...\n');
  
  try {
    // Read current external-eval-api.js
    const apiFile = fs.readFileSync('external-eval-api.js', 'utf8');
    
    // Extract current answers using multiple patterns
    let answer1 = null, answer2 = null, maxAttempts = null, timeoutMinutes = null;
    
    // Pattern 1: Look for ANSWERS object
    const answersMatch = apiFile.match(/const ANSWERS = \{[\s\S]*?answer1:\s*["']([^"']+)["'][\s\S]*?answer2:\s*["']([^"']+)["'][\s\S]*?\}/);
    if (answersMatch) {
      answer1 = answersMatch[1];
      answer2 = answersMatch[2];
    }
    
    // Pattern 2: Look for individual constants
    if (!answer1) {
      const colorMatch = apiFile.match(/(?:FAVORITE_COLOR|answer1).*?["']([^"']+)["']/);
      if (colorMatch) answer1 = colorMatch[1];
    }
    
    if (!answer2) {
      const fruitMatch = apiFile.match(/(?:FAVORITE_FRUIT|answer2).*?["']([^"']+)["']/);
      if (fruitMatch) answer2 = fruitMatch[1];
    }
    
    // Pattern 3: Look for comparison in if statements
    if (!answer1) {
      const ifMatch1 = apiFile.match(/answer1\s*===\s*["']([^"']+)["']/);
      if (ifMatch1) answer1 = ifMatch1[1];
    }
    
    if (!answer2) {
      const ifMatch2 = apiFile.match(/answer2\s*===\s*["']([^"']+)["']/);
      if (ifMatch2) answer2 = ifMatch2[1];
    }
    
    // Extract timeout and attempts settings
    const maxAttemptsMatch = apiFile.match(/MAX_ATTEMPTS\s*=\s*(\d+)/);
    if (maxAttemptsMatch) maxAttempts = parseInt(maxAttemptsMatch[1]);
    
    const timeoutMatch = apiFile.match(/TIMEOUT_MINUTES\s*=\s*(\d+)/);
    if (timeoutMatch) timeoutMinutes = parseInt(timeoutMatch[1]);
    
    currentValues.answer1 = answer1;
    currentValues.answer2 = answer2;
    currentValues.maxAttempts = maxAttempts;
    currentValues.timeoutMinutes = timeoutMinutes;
    
  } catch (error) {
    console.log('⚠️  Could not read external-eval-api.js:', error.message);
  }
  
  try {
    // Read current challenge.html
    const challengeFile = fs.readFileSync('views/challenge.html', 'utf8');
    
    // Extract questions from HTML
    const questionMatches = challengeFile.match(/<div class="question">([^<]+)<\/div>/g);
    
    if (questionMatches && questionMatches.length >= 2) {
      currentValues.question1 = questionMatches[0].replace(/<div class="question">([^<]+)<\/div>/, '$1');
      currentValues.question2 = questionMatches[1].replace(/<div class="question">([^<]+)<\/div>/, '$1');
    } else {
      // Try alternative patterns for questions
      const allQuestions = challengeFile.match(/What [^?]+\?/g);
      if (allQuestions && allQuestions.length >= 2) {
        currentValues.question1 = allQuestions[0];
        currentValues.question2 = allQuestions[1];
      }
    }
    
  } catch (error) {
    console.log('⚠️  Could not read views/challenge.html:', error.message);
  }
  
  // Display what was found
  console.log('✅ Current configuration detected:');
  console.log(`   Question 1: "${currentValues.question1 || 'Not found'}"`);
  console.log(`   Answer 1: "${currentValues.answer1 || 'Not found'}"`);
  console.log(`   Question 2: "${currentValues.question2 || 'Not found'}"`);
  console.log(`   Answer 2: "${currentValues.answer2 || 'Not found'}"`);
  console.log(`   Max attempts: ${currentValues.maxAttempts || 'Not found'}`);
  console.log(`   Timeout (minutes): ${currentValues.timeoutMinutes || 'Not found'}`);
  console.log();
  
  // Check if any values were not found
  const missingValues = [];
  if (!currentValues.question1) missingValues.push('question1');
  if (!currentValues.answer1) missingValues.push('answer1');
  if (!currentValues.question2) missingValues.push('question2');
  if (!currentValues.answer2) missingValues.push('answer2');
  if (!currentValues.maxAttempts) missingValues.push('maxAttempts');
  if (!currentValues.timeoutMinutes) missingValues.push('timeoutMinutes');
  
  if (missingValues.length > 0) {
    console.log(`⚠️  Could not detect: ${missingValues.join(', ')}`);
    console.log('   You can set values below.\n');
  }
}

function askQuestion(prompt, defaultValue) {
  return new Promise((resolve) => {
    const question = defaultValue !== undefined && defaultValue !== null
      ? `${prompt} (current: "${defaultValue}"): `
      : `${prompt} (no current value detected): `;
    
    rl.question(question, (answer) => {
      // If no default and no answer provided, ask again
      if ((defaultValue === undefined || defaultValue === null) && !answer.trim()) {
        console.log('Please provide a value.');
        resolve(askQuestion(prompt, defaultValue));
      } else {
        resolve(answer.trim() || defaultValue);
      }
    });
  });
}

async function setupChallenge() {
  console.log('🍅 Challenge Setup - Configure your questions, answers, and settings\n');
  
  // Read current configuration from files
  readCurrentConfig();
  
  console.log('Press Enter to keep current values, or type new ones.\n');

  // Question 1
  console.log('--- Question 1 ---');
  config.question1 = await askQuestion('What should question 1 be?', currentValues.question1);
  config.answer1 = await askQuestion('What should answer 1 be?', currentValues.answer1);
  
  // Question 2  
  console.log('\n--- Question 2 ---');
  config.question2 = await askQuestion('What should question 2 be?', currentValues.question2);
  config.answer2 = await askQuestion('What should answer 2 be?', currentValues.answer2);

  // Security settings
  console.log('\n--- Security Settings ---');
  config.maxAttempts = await askQuestion('Maximum attempts before timeout?', currentValues.maxAttempts);
  config.timeoutMinutes = await askQuestion('Timeout duration in minutes?', currentValues.timeoutMinutes);

  // Convert to numbers
  config.maxAttempts = parseInt(config.maxAttempts) || 2;
  config.timeoutMinutes = parseInt(config.timeoutMinutes) || 10;

  // Summary
  console.log('\n📋 Summary of your challenge:');
  console.log(`Question 1: "${config.question1}"`);
  console.log(`Answer 1: "${config.answer1}"`);
  console.log(`Question 2: "${config.question2}"`);
  console.log(`Answer 2: "${config.answer2}"`);
  console.log(`Max attempts: ${config.maxAttempts}`);
  console.log(`Timeout: ${config.timeoutMinutes} minutes`);

  const confirm = await askQuestion('\nDoes this look correct? (y/N)', 'n');
  
  if (confirm.toLowerCase() === 'y' || confirm.toLowerCase() === 'yes') {
    await generateFiles();
    console.log('\n✅ Challenge setup complete!');
    console.log('\nNext steps:');
    console.log('1. Build and deploy: docker build -t vladko2050/external-eval-api:latest .');
    console.log('2. Push: docker push vladko2050/external-eval-api:latest');
    console.log('3. Restart: kubectl rollout restart deployment/external-eval-api -n external-eval');
    console.log('Or just use updateDocker.sh');
  } else {
    console.log('\n❌ Setup cancelled. Run the script again to try again.');
  }
  
  rl.close();
}

async function generateFiles() {
  // Generate updated external-eval-api.js
  const apiContent = `const path = require('path');
const express = require('express');
const cookieParser = require('cookie-parser');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Challenge configuration
const ANSWERS = {
  answer1: "${config.answer1.toLowerCase()}",
  answer2: "${config.answer2.toLowerCase()}"
};

const MAX_ATTEMPTS = ${config.maxAttempts};
const TIMEOUT_MINUTES = ${config.timeoutMinutes};

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
  
  console.log('Answers received:', { answer1, answer2, userId });
  console.log('Expected answers:', ANSWERS);
  
  // Check timeout
  if (data.timeoutStart) {
    const elapsedMinutes = (Date.now() - data.timeoutStart) / 1000 / 60;
    if (elapsedMinutes < TIMEOUT_MINUTES) {
      return res.send(\`
        <div style="text-align: center; padding: 50px; font-family: Arial;">
          <h2>Timeout Active</h2>
          <p>Please wait \${Math.ceil(TIMEOUT_MINUTES - elapsedMinutes)} minutes before trying again.</p>
          <a href="/challenge?return=\${encodeURIComponent(returnUrl)}">Back</a>
        </div>
      \`);
    } else {
      data.attempts = 0;
      data.timeoutStart = null;
    }
  }
  
  // Check both answers
  if (answer1 === ANSWERS.answer1 && answer2 === ANSWERS.answer2) {
    data.approved = true;
    data.attempts = 0;
    data.timeoutStart = null;
    userData.set(userId, data);
    
    console.log('User approved - UserID:', userId);
    
    // Redirect to success endpoint on the protected app
    const successUrl = \`https://pdf.vladsdomain.live/challenge/success?return=\${encodeURIComponent(returnUrl)}\`;
    return res.redirect(successUrl);
    
  } else {
    data.attempts++;
    if (data.attempts >= MAX_ATTEMPTS) {
      data.timeoutStart = Date.now();
      userData.set(userId, data);
      return res.send(\`
        <div style="text-align: center; padding: 50px; font-family: Arial;">
          <h2>Wrong Answer</h2>
          <p>You have reached max attempts. Please wait \${TIMEOUT_MINUTES} minutes before trying again.</p>
          <a href="/challenge?return=\${encodeURIComponent(returnUrl)}">Back</a>
        </div>
      \`);
    } else {
      userData.set(userId, data);
      let wrongMessage = "Wrong answer(s). Try again.";
      if (answer1 !== ANSWERS.answer1 && answer2 !== ANSWERS.answer2) {
        wrongMessage = "Both answers are incorrect. Try again.";
      } else if (answer1 !== ANSWERS.answer1) {
        wrongMessage = "First answer is incorrect. Try again.";
      } else if (answer2 !== ANSWERS.answer2) {
        wrongMessage = "Second answer is incorrect. Try again.";
      }
      
      return res.send(\`
        <div style="text-align: center; padding: 50px; font-family: Arial;">
          <h2>\${wrongMessage}</h2>
          <p>Attempts remaining: \${MAX_ATTEMPTS - data.attempts}</p>
          <a href="/challenge?return=\${encodeURIComponent(returnUrl)}">Back</a>
        </div>
      \`);
    }
  }
});

// API endpoint to check if user is approved
app.get('/api/check/:userId', (req, res) => {
  const userId = req.params.userId;
  const data = userData.get(userId) || { approved: false };
  res.json({ approved: data.approved });
});

// Keep existing endpoints
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
  console.log(\`Challenge Service listening on port \${PORT}\`);
  console.log('Challenge configuration:');
  console.log('  Question 1: ${config.question1}');
  console.log('  Question 2: ${config.question2}');
  console.log('  Max attempts: ${config.maxAttempts}');
  console.log('  Timeout: ${config.timeoutMinutes} minutes');
});
`;

  // Generate updated challenge.html
  const challengeHtml = `<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Challenge - PDF Tools</title>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      
      html, body {
        height: 100%;
        width: 100%;
        overflow: hidden;
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
      }
      
      .fruit-bg {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://shoptextile.ro/wp-content/uploads/2024/03/IMG_9422.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
      }
      
      .content-overlay {
        background-color: rgba(255, 255, 255, 0.6);
        padding: 60px;
        border-radius: 30px;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.7);
        max-width: 500px;
        width: 90%;
      }
      
      .icon {
        font-size: 60px;
        margin-bottom: 20px;
        filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.1));
      }
      
      h1 {
        color: #ff6347;
        font-size: 28px;
        margin-bottom: 30px;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.9);
        letter-spacing: -0.5px;
      }
      
      .question {
        color: #333;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
      }
      
      input[type="text"] {
        width: 100%;
        padding: 12px 16px;
        border: 2px solid rgba(255, 99, 71, 0.3);
        border-radius: 8px;
        font-size: 16px;
        margin-bottom: 20px;
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
      }
      
      input[type="text"]:focus {
        outline: none;
        border-color: #ff6347;
        box-shadow: 0 0 10px rgba(255, 99, 71, 0.3);
        background: rgba(255, 255, 255, 1);
      }
      
      input[type="text"]::placeholder {
        color: #999;
        font-style: italic;
      }
      
      button {
        background: linear-gradient(135deg, #ff9800, #ff6347);
        color: white;
        border: none;
        padding: 16px 32px;
        font-size: 18px;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 20px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
        width: 100%;
      }
      
      button:hover {
        background: linear-gradient(135deg, #e68900, #e5533d);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 152, 0, 0.5);
      }
      
      button:active {
        transform: translateY(0);
      }
      
      .form-group {
        margin-bottom: 25px;
      }
      
      .info-text {
        color: #666;
        font-size: 14px;
        margin-top: 20px;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
      }
      
      /* Mobile adjustments */
      @media (max-width: 768px) {
        .content-overlay {
          padding: 40px 30px;
          margin: 20px;
          max-width: none;
        }
        
        h1 {
          font-size: 24px;
        }
        
        button {
          padding: 14px 28px;
          font-size: 16px;
        }
        
        .icon {
          font-size: 50px;
        }
      }
      
      @media (max-width: 480px) {
        .content-overlay {
          padding: 30px 20px;
          margin: 15px;
          border-radius: 20px;
        }
        
        h1 {
          font-size: 22px;
        }
        
        button {
          padding: 12px 24px;
          font-size: 15px;
        }
        
        .icon {
          font-size: 45px;
        }
        
        input[type="text"] {
          padding: 10px 14px;
          font-size: 15px;
        }
      }
    </style>
  </head>
  <body>
    <div class="fruit-bg">
      <div class="content-overlay">
        <div class="icon">🍅</div>
        
        <h1>Answer the questions to enter</h1>
        
        <form method="POST" action="/challenge">
          <!-- Hidden field to preserve return URL -->
          <input type="hidden" name="return" id="returnUrl" />
          
          <div class="form-group">
            <div class="question">${config.question1}</div>
            <input name="answer1" type="text" autocomplete="off" placeholder="Enter your answer" required />
          </div>
          
          <div class="form-group">
            <div class="question">${config.question2}</div>
            <input name="answer2" type="text" autocomplete="off" placeholder="Enter your answer" required />
          </div>
          
          <button type="submit">Submit Answers</button>
          
          <div class="info-text">
            You have ${config.maxAttempts} attempts. After failed attempts, wait ${config.timeoutMinutes} minutes.
          </div>
        </form>
      </div>
    </div>

    <script>
      // Get return URL from query parameter and set it in the hidden field
      const urlParams = new URLSearchParams(window.location.search);
      const returnUrl = urlParams.get('return') || 'https://pdf.vladsdomain.live/';
      document.getElementById('returnUrl').value = returnUrl;
    </script>
  </body>
</html>
`;

  // Write the files
  fs.writeFileSync('external-eval-api.js', apiContent);
  fs.writeFileSync('views/challenge.html', challengeHtml);
  
  console.log('\n📁 Files generated:');
  console.log('  ✅ external-eval-api.js updated');
  console.log('  ✅ views/challenge.html updated');
}

// Start the interactive setup
setupChallenge().catch(console.error);
