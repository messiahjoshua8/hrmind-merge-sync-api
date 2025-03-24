/**
 * This is a template for a Supabase Edge Function that manages Merge.dev tokens securely.
 * 
 * To implement this function:
 * 1. Create a new Supabase Edge Function named "get_merge_token"
 * 2. Use this template as a starting point
 * 3. Deploy it to your Supabase project
 * 
 * Security benefits:
 * - Keeps Merge API credentials on the server, not in client code
 * - Handles token exchange server-side
 * - Can implement rate limiting and audit logging
 * - Secures access through Supabase auth
 */

// Supabase Edge Function
export async function get_merge_token(req, res) {
  // Verify the request is authenticated
  const { authorization } = req.headers;
  if (!authorization) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // Get the user from the JWT token
    const token = authorization.replace('Bearer ', '');
    const { data: user, error } = await supabase.auth.getUser(token);
    
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid token' });
    }

    // Your secure token handling logic here
    // For example, you might:
    // 1. Retrieve a stored token from a secure location
    // 2. Exchange credentials for a new token if needed
    // 3. Use environment variables for sensitive values

    // IMPORTANT: Store these securely in Supabase environment variables
    const MERGE_API_KEY = process.env.MERGE_API_KEY;
    const MERGE_ACCOUNT_ID = process.env.MERGE_ACCOUNT_ID;
    
    // Example: Generate or retrieve a token
    let mergeToken;
    
    // Option 1: Return a stored token (simplest)
    mergeToken = process.env.MERGE_ACCOUNT_TOKEN;
    
    // Option 2: Exchange credentials for a new token
    // Use the Merge API to get a new token
    /* 
    const response = await fetch('https://api.merge.dev/api/ats/v1/account-token', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${MERGE_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        account_id: MERGE_ACCOUNT_ID
      })
    });
    
    const data = await response.json();
    mergeToken = data.account_token;
    */
    
    // Return the token to the client
    return res.status(200).json({ 
      token: mergeToken,
      // Don't include sensitive information in the response
      expires_at: new Date(Date.now() + 3600000).toISOString() // Example expiry 1 hour
    });
  } catch (error) {
    console.error('Error generating Merge token:', error);
    return res.status(500).json({ error: 'Failed to generate token' });
  }
} 