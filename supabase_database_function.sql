-- This is a template for a Supabase Database Function for secure Merge token retrieval
-- You can implement this if you prefer using database functions instead of Edge Functions

-- Create a secure schema for sensitive operations
CREATE SCHEMA IF NOT EXISTS secure_operations;

-- Create a table to store Merge API configuration
-- IMPORTANT: Set appropriate RLS policies to restrict access
CREATE TABLE IF NOT EXISTS secure_operations.merge_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key TEXT NOT NULL,
    account_token TEXT NOT NULL,
    account_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

-- Table RLS: Only allow administrators to modify the config
ALTER TABLE secure_operations.merge_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Only administrators can view merge_config" 
    ON secure_operations.merge_config FOR SELECT 
    USING (auth.uid() IN (
        SELECT user_id FROM administrators WHERE is_active = TRUE
    ));

CREATE POLICY "Only administrators can modify merge_config" 
    ON secure_operations.merge_config FOR ALL 
    USING (auth.uid() IN (
        SELECT user_id FROM administrators WHERE is_active = TRUE
    ));

-- Function to get a Merge token
-- This is the function that will be called by your Python script
CREATE OR REPLACE FUNCTION public.get_merge_token()
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER
AS $$
DECLARE
    config_record RECORD;
    result JSONB;
BEGIN
    -- Verify the user is authenticated
    IF auth.uid() IS NULL THEN
        RAISE EXCEPTION 'Authentication required';
    END IF;
    
    -- Get the most recent active token
    SELECT * INTO config_record 
    FROM secure_operations.merge_config 
    WHERE is_active = TRUE
    ORDER BY updated_at DESC
    LIMIT 1;
    
    IF config_record IS NULL THEN
        RAISE EXCEPTION 'No active Merge configuration found';
    END IF;
    
    -- Check if token is expired and needs refresh
    IF config_record.expires_at IS NOT NULL AND config_record.expires_at < NOW() THEN
        -- In a real implementation, you might make an API call to refresh the token
        -- For this template, we'll just raise an exception
        RAISE EXCEPTION 'Token expired, needs manual refresh';
    END IF;
    
    -- Return the token with an expiry time but without the API key
    result := jsonb_build_object(
        'token', config_record.account_token,
        'expires_at', config_record.expires_at
    );
    
    RETURN result;
END;
$$;

-- Grant access to the function - adjust as needed for your auth setup
GRANT EXECUTE ON FUNCTION public.get_merge_token() TO authenticated;

-- Example insert for testing (REMOVE THIS IN PRODUCTION)
-- INSERT INTO secure_operations.merge_config (api_key, account_token, expires_at)
-- VALUES ('YOUR_API_KEY', 'YOUR_ACCOUNT_TOKEN', NOW() + INTERVAL '30 days'); 