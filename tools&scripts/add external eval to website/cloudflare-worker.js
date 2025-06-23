addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const CHALLENGE_URL = 'https://eval.vladsdomain.live';
const STIRLING_PDF_ORIGIN = 'https://pdf-internal.vladsdomain.live'; // Internal tunnel access

function getCookie(request, name) {
  const cookieHeader = request.headers.get('Cookie');
  if (!cookieHeader) return null;
  
  const cookies = cookieHeader.split(';');
  for (let cookie of cookies) {
    const [cookieName, cookieValue] = cookie.trim().split('=');
    if (cookieName === name) {
      return cookieValue;
    }
  }
  return null;
}

function validateAccessToken(token) {
  try {
    const payload = JSON.parse(atob(token));
    return payload.approved && (Date.now() - payload.timestamp < 24 * 60 * 60 * 1000);
  } catch (e) {
    return false;
  }
}

async function handleRequest(request) {
  const url = new URL(request.url);
  
  console.log('Request URL:', url.pathname);
  
  // Handle challenge success callback
  if (url.pathname === '/challenge/success') {
    console.log('Handling challenge success');
    const returnUrl = url.searchParams.get('return') || '/';
    
    // Create access token
    const token = btoa(JSON.stringify({
      approved: true,
      timestamp: Date.now()
    }));
    
    // Create redirect response with cookie
    const response = new Response(null, {
      status: 302,
      headers: {
        'Location': returnUrl,
        'Set-Cookie': `access_token=${token}; HttpOnly; Secure; Max-Age=86400; Path=/`
      }
    });
    
    return response;
  }
  
  // Handle logout
  if (url.pathname === '/logout') {
    const response = new Response(`
      <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h2>Logged Out</h2>
        <p>You have been logged out. <a href="/">Return to PDF Tools</a></p>
      </div>
    `, {
      headers: { 
        'Content-Type': 'text/html',
        'Set-Cookie': 'access_token=; HttpOnly; Secure; Max-Age=0; Path=/'
      }
    });
    return response;
  }
  
  // Check access for all other requests
  const accessToken = getCookie(request, 'access_token');
  console.log('Access token:', accessToken ? 'present' : 'missing');
  
  if (!accessToken || !validateAccessToken(accessToken)) {
    console.log('Redirecting to access required page');
    // User needs to complete challenge - redirect to your access required page
    const returnUrl = encodeURIComponent(request.url);
    const accessRequiredUrl = `${CHALLENGE_URL}/access-required?return=${returnUrl}`;
    
    // Redirect to your custom access required page
    return Response.redirect(accessRequiredUrl, 302);
  }
  
  console.log('User has access, proxying to Stirling PDF');
  
  // User has access - proxy to Stirling PDF
  try {
    // Create new URL pointing to Stirling PDF
    const targetUrl = new URL(url.pathname + url.search, STIRLING_PDF_ORIGIN);
    
    // Create new request with same method, headers, and body
    const modifiedRequest = new Request(targetUrl.toString(), {
      method: request.method,
      headers: request.headers,
      body: request.body
    });
    
    // Forward to Stirling PDF
    const response = await fetch(modifiedRequest);
    
    // Create new response with same body and most headers
    const modifiedResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers
    });
    
    return modifiedResponse;
    
  } catch (error) {
    console.error('Proxy error:', error);
    
    // Fallback error page
    return new Response(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Service Unavailable</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
          .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 20px; border-radius: 8px; }
        </style>
      </head>
      <body>
        <h1>Service Temporarily Unavailable</h1>
        <div class="error">
          <p>The PDF service is currently unavailable. Please try again later.</p>
          <p>Error: ${error.message}</p>
        </div>
        <p><a href="/">Try Again</a> | <a href="/logout">Logout</a></p>
      </body>
      </html>
    `, {
      status: 503,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}